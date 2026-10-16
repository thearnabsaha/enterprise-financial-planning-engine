"""
Settings & Documentation — System configuration, financial glossaries, and TM1 concept mapping.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from components.navigation import render_footer, render_header
from components.styles import apply_theme
from models.config import get_settings

apply_theme()

render_header(
    title="Settings & Technical Documentation",
    subtitle="Northstar Digital Services GmbH • Architecture Reference, Sign Conventions & TM1 Guide",
)

tab_docs, tab_tm1, tab_cfg = st.tabs([
    "📖 Architecture & Financial Rules",
    "🏢 IBM Planning Analytics (TM1) Comparison",
    "⚙️ Configuration Parameters",
])

with tab_docs:
    st.subheader("System Architecture & Accounting Methodology")
    st.markdown("""
    #### 1. Precision Decimal Arithmetic
    All financial metrics are stored and computed using Python's `decimal.Decimal` with explicit `ROUND_HALF_UP` rounding.
    This eliminates binary floating-point rounding errors inherent to standard IEEE 754 floats.

    #### 2. Financial Sign Convention Standard
    * **Revenue** is positive ($+$).
    * **Operating Expenses** are negative ($-$).
    * **Operating Profit** = $\\text{Revenue} + \\text{Operating Expenses}$
    * **Operating Margin %** = $(\\text{Operating Profit} / \\text{Revenue}) \\times 100$

    #### 3. Favourability Classification
    * **Revenue & Profit**:
        * $\\text{Actual} > \\text{Budget} \\implies \\mathbf{FAVOURABLE}$ (Green)
        * $\\text{Actual} < \\text{Budget} \\implies \\mathbf{UNFAVOURABLE}$ (Red)
    * **Operating Expenses**:
        * $\\text{Actual} > \\text{Budget}$ (less negative, less spent) $\\implies \\mathbf{FAVOURABLE}$ (Green)
        * $\\text{Actual} < \\text{Budget}$ (more negative, more spent) $\\implies \\mathbf{UNFAVOURABLE}$ (Red)
    """)

with tab_tm1:
    st.subheader("Concept Mapping: IBM TM1 vs Northstar Engine")
    tm1_mapping = [
        {"IBM TM1 / Planning Analytics": "Multidimensional Cube", "Northstar Python Engine": "TinyOlap 4D In-Memory Cube", "Notes": "Account × Department × Period × Scenario"},
        {"IBM TM1 / Planning Analytics": "N-Level & C-Level Elements", "Northstar Python Engine": "Leaf Members & Consolidation Weights", "Notes": "Hierarchical rollups (COMPANY -> ENG/SALES)"},
        {"IBM TM1 / Planning Analytics": "TM1 Rules (.rux)", "Northstar Python Engine": "TinyOlap @rule decorated functions", "Notes": "Dynamic calculation of Operating Profit & Margin"},
        {"IBM TM1 / Planning Analytics": "TurboIntegrator (TI) Processes", "Northstar Python Engine": "8-Step Python ETL Pipeline", "Notes": "File parsing, validation, mapping, atomic loading"},
        {"IBM TM1 / Planning Analytics": "Feeders", "Northstar Python Engine": "Sparse storage optimization", "Notes": "Rule evaluation engine avoids over-calculation"},
        {"IBM TM1 / Planning Analytics": "PAW / TM1 Web Dashboards", "Northstar Python Engine": "Streamlit Interactive Web Application", "Notes": "Custom enterprise CSS, Plotly charts, Excel export"},
        {"IBM TM1 / Planning Analytics": "Transaction Logging", "Northstar Python Engine": "Relational Audit Trail (PostgreSQL/SQLite)", "Notes": "Immutable event logging across all actions"},
    ]
    st.dataframe(pd.DataFrame(tm1_mapping), use_container_width=True, hide_index=True)

with tab_cfg:
    st.subheader("Runtime Configuration Parameters")
    cfg = get_settings()
    cfg_data = [
        {"Key": "app_version", "Value": cfg.app_version, "Description": "Application build version"},
        {"Key": "app_env", "Value": cfg.app_env, "Description": "Execution environment (development/production)"},
        {"Key": "default_currency", "Value": cfg.default_currency, "Description": "Base presentation currency"},
        {"Key": "max_upload_size_mb", "Value": f"{cfg.max_upload_size_mb} MB", "Description": "Maximum upload file size limit"},
        {"Key": "data_seed", "Value": str(cfg.data_seed), "Description": "Random seed for reproducible synthetic generation"},
        {"Key": "database_engine", "Value": "SQLAlchemy 2.0 (PostgreSQL/SQLite)", "Description": "Relational persistence driver"},
    ]
    st.dataframe(pd.DataFrame(cfg_data), use_container_width=True, hide_index=True)

render_footer()
