"""
Import History & Audit Trail — Lineage, batch execution tracking, and audit log.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from components.navigation import render_footer, render_header
from components.styles import apply_theme
from database import repository as repo
from database.connection import get_session
from services.audit_service import AuditService

apply_theme()

render_header(
    title="Import History & Audit Governance",
    subtitle="Northstar Digital Services GmbH • Batch Lineage, Anomaly Logs & System Event Trail",
)

tab_batches, tab_audit = st.tabs(["📦 Import Batches History", "🛡️ Immutable Audit Trail"])

with tab_batches:
    st.subheader("Import Batches Executed")
    with get_session() as s:
        batches = repo.get_all_import_batches(s, limit=50)

    if batches:
        b_rows = []
        for b in batches:
            b_rows.append({
                "Batch ID": b.id,
                "Status": b.status.upper(),
                "Total Rows": b.total_rows,
                "Accepted": b.accepted_rows,
                "Rejected": b.rejected_rows,
                "Duplicates": b.duplicate_rows,
                "Duration (ms)": b.processing_duration_ms or 0,
                "Started At": b.started_at.strftime("%Y-%m-%d %H:%M:%S") if b.started_at else "",
            })
        st.dataframe(pd.DataFrame(b_rows), use_container_width=True, hide_index=True)

        selected_batch_id = st.selectbox("Drill-down into Batch ID:", [b.id for b in batches])
        with get_session() as s:
            errors = repo.get_validation_errors_for_batch(s, selected_batch_id)
            if errors:
                st.warning(f"Batch #{selected_batch_id} recorded {len(errors)} validation items:")
                err_rows = [{
                    "Row": e.row_number,
                    "Column": e.column_name,
                    "Type": e.error_type.upper(),
                    "Code": e.error_code,
                    "Message": e.message,
                } for e in errors]
                st.dataframe(pd.DataFrame(err_rows), use_container_width=True, hide_index=True)
            else:
                st.success(f"Batch #{selected_batch_id} completed with zero validation errors.")
    else:
        st.info("No import batches recorded yet.")

with tab_audit:
    st.subheader("System Audit Log")
    events = AuditService.get_recent_events(limit=100)
    if events:
        st.dataframe(pd.DataFrame(events), use_container_width=True, hide_index=True)
    else:
        st.info("No audit events recorded yet.")

render_footer()
