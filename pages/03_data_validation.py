"""
Data Validation — Standalone quality inspector and validation rules catalog.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import streamlit as st

from components.data_tables import render_financial_table
from components.navigation import render_footer, render_header
from components.styles import apply_theme
from services.validation_service import ValidationService

apply_theme()

render_header(
    title="Data Validation & Quality Inspector",
    subtitle="Northstar Digital Services GmbH • Rule Catalog & Anomaly Detection",
)

st.markdown("""
Ensure financial datasets adhere to referential integrity, sign conventions, date boundaries, and currency standards.
""")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Active Validation Rules Catalog")
    rules = [
        {"Rule Code": "REQ_001", "Domain": "Structure", "Description": "Required fields: department, account, amount must be present and non-empty."},
        {"Rule Code": "DATE_002", "Domain": "Time", "Description": "Period must follow YYYY-MM (2024-01 to 2026-12) or valid ISO dates."},
        {"Rule Code": "DEPT_003", "Domain": "Master Data", "Description": "Department code must exist in active department master (ENG, SALES, MKT, OPS, FIN)."},
        {"Rule Code": "ACCT_004", "Domain": "Master Data", "Description": "Account code must exist in active chart of accounts (REV, SAL, CLOUD, SW, etc.)."},
        {"Rule Code": "CURR_005", "Domain": "Currency", "Description": "Currency must be one of EUR, USD, GBP, CHF (defaults to EUR)."},
        {"Rule Code": "GRAIN_006", "Domain": "Grain", "Description": "Grain uniqueness across (Period, Department, Account, Scenario, Version, Currency)."},
    ]
    st.dataframe(pd.DataFrame(rules), hide_index=True, use_container_width=True)

with col2:
    st.subheader("Test Data Quality Engine")
    st.markdown("Inspect known problematic datasets (e.g. deliberately invalid test fixtures):")

    invalid_path = Path("data/sample/invalid_test_data.csv")
    if invalid_path.exists():
        if st.button("Inspect `invalid_test_data.csv`"):
            df = pd.read_csv(invalid_path, dtype=str)
            summary = ValidationService.validate(df)

            st.metric("Detected Violations", len(summary.errors))
            err_df = ValidationService.errors_to_dataframe(summary)
            render_financial_table(err_df, title="Detected Anomalies", height=300)

            csv_data = err_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download Error Report (CSV)",
                data=csv_data,
                file_name="northstar_validation_errors.csv",
                mime="text/csv",
            )

render_footer()
