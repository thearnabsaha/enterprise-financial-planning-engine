"""
Upload & Import — 8-step transactional ETL pipeline with duplicate handling.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import streamlit as st

from components.data_tables import render_financial_table
from components.navigation import render_footer, render_header
from components.styles import apply_theme
from models.import_models import DuplicatePolicy, ImportStatus
from services.import_service import ImportService
from services.validation_service import ValidationService

apply_theme()

render_header(
    title="Data Ingestion & Import Pipeline",
    subtitle="Northstar Digital Services GmbH • Transactional ETL & Duplicate Control",
)

st.markdown("""
Upload financial files (CSV or Excel). The engine executes an 8-step pipeline:
Inspection $\\to$ Column Mapping $\\to$ Domain Validation $\\to$ Type Transformation $\\to$ Atomic Database Ingestion.
""")

# Option: Upload or pick sample file
upload_tab, sample_tab = st.tabs(["📁 Upload Your File", "🧪 Load Sample / Test Fixtures"])

file_to_process = None
filename = ""
file_bytes = None

with upload_tab:
    uploaded = st.file_uploader("Select financial file (CSV or XLSX)", type=["csv", "xlsx", "xls"])
    if uploaded is not None:
        file_to_process = uploaded
        filename = uploaded.name
        file_bytes = uploaded.getvalue()

with sample_tab:
    sample_dir = Path("data/sample")
    if sample_dir.exists():
        sample_files = list(sample_dir.glob("*.csv"))
        selected_sample = st.selectbox("Choose sample file:", [f.name for f in sample_files])
        if st.button("Load Selected Sample File"):
            sample_path = sample_dir / selected_sample
            filename = selected_sample
            with open(sample_path, "rb") as f:
                file_bytes = f.read()
            file_to_process = sample_path

if file_bytes is not None:
    st.markdown("---")
    st.subheader(f"Step 1 & 2: File Inspection — `{filename}`")

    # Inspect file
    parsed = ImportService.inspect_file(file_bytes, filename)
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.metric("Total Rows", f"{parsed.total_rows:,}")
    with col_m2:
        st.metric("Columns", len(parsed.columns))
    with col_m3:
        st.metric("File Size", f"{parsed.file_size_bytes / 1024:.1f} KB")
    with col_m4:
        st.metric("Detected Format", parsed.file_type.upper())

    # Raw preview
    with st.expander("Preview Raw Data (First 15 Rows)", expanded=False):
        st.dataframe(parsed.preview_df, use_container_width=True)

    # Step 3: Column Mapping
    st.subheader("Step 3: Column Mapping")
    auto_mappings = ImportService.get_auto_mapping(parsed.columns)

    st.markdown("Verify or adjust target field mappings:")
    target_fields = ["department", "account", "period", "date", "scenario", "version", "currency", "amount", "ignore"]

    col_map_inputs = {}
    cols = st.columns(min(len(parsed.columns), 4))
    for idx, col_name in enumerate(parsed.columns):
        col_container = cols[idx % 4]
        default_target = auto_mappings.get(col_name, "ignore")
        target_idx = target_fields.index(default_target) if default_target in target_fields else 0
        col_map_inputs[col_name] = col_container.selectbox(
            f"Col: {col_name}",
            options=target_fields,
            index=target_idx,
            key=f"col_map_{col_name}",
        )

    # Step 4 & 5: Validation
    st.subheader("Step 4 & 5: Validation & Quality Pre-Check")
    # Read full dataframe for validation
    df_raw = pd.read_csv(pd.io.common.BytesIO(file_bytes), dtype=str) if filename.endswith(".csv") else pd.read_excel(pd.io.common.BytesIO(file_bytes), dtype=str)

    # Apply mapping
    active_mapping = {src: tgt for src, tgt in col_map_inputs.items() if tgt != "ignore"}
    mapped_df = df_raw.rename(columns=active_mapping)

    validation_summary = ValidationService.validate(mapped_df)

    v_col1, v_col2, v_col3, v_col4 = st.columns(4)
    with v_col1:
        st.metric("Valid Rows", f"{validation_summary.valid_rows:,}")
    with v_col2:
        st.metric("Invalid Rows", f"{validation_summary.invalid_rows:,}")
    with v_col3:
        st.metric("Warnings", f"{validation_summary.warning_count:,}")
    with v_col4:
        st.metric("Duplicates", f"{validation_summary.duplicate_count:,}")

    if validation_summary.errors:
        st.warning(f"Found {len(validation_summary.errors)} validation messages:")
        err_df = ValidationService.errors_to_dataframe(validation_summary)
        render_financial_table(err_df, title="Validation Issue Details", height=220)

    # Step 6 & 7: Duplicate Policy & Ingestion Execution
    st.subheader("Step 6 & 7: Duplicate Handling & Atomic Commit")

    dup_policy_str = st.radio(
        "Duplicate Grain Policy:",
        options=["Reject (Fail on any duplicate grain)", "Skip (Ignore duplicate rows)", "Replace (Update existing facts)"],
        index=0,
    )

    policy_map = {
        "Reject (Fail on any duplicate grain)": DuplicatePolicy.REJECT,
        "Skip (Ignore duplicate rows)": DuplicatePolicy.SKIP,
        "Replace (Update existing facts)": DuplicatePolicy.REPLACE,
    }
    selected_policy = policy_map[dup_policy_str]

    if st.button("🚀 Execute Transactional Ingestion", type="primary"):
        with st.spinner("Executing atomic transaction and updating multidimensional cube..."):
            import_result = ImportService.execute_import(
                df=df_raw,
                filename=filename,
                column_mapping=active_mapping,
                duplicate_policy=selected_policy,
                file_size_bytes=len(file_bytes),
            )

        if import_result.status == ImportStatus.COMPLETED:
            st.success(f"🎉 Successfully ingested {import_result.accepted_rows:,} financial facts into database in {import_result.duration_ms} ms!")
            # Invalidate OLAP cache so fresh facts are loaded
            from olap.cache import invalidate_olap_cache
            invalidate_olap_cache()
        else:
            st.error(f"❌ Ingestion failed. {import_result.rejected_rows} rows rejected.")
            for err in import_result.errors[:10]:
                st.error(err)

render_footer()
