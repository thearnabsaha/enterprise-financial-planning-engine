"""
Enterprise Financial Planning & Forecasting Engine
Northstar Digital Services GmbH

Entry point for the Streamlit multi-page application.
"""
from __future__ import annotations

import streamlit as st

# Configure page settings
st.set_page_config(
    page_title="Northstar Digital Services | Financial Planning Engine",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

from components.navigation import render_footer, render_header
from components.styles import apply_theme
from database.connection import check_connection, init_database
from database.seed import seed_database
from models.config import get_streamlit_settings

# Apply custom dark enterprise theme
apply_theme()

# Auto-seed database if empty on startup
status = check_connection()
if status.get("status") == "connected":
    from database.connection import get_session
    from database import repository as repo
    with get_session() as s:
        depts = repo.get_all_departments(s)
        if not depts:
            with st.spinner("Initialising and seeding demo financial model..."):
                seed_database()

# Main Landing Page Banner
render_header(
    title="Enterprise Financial Planning & Forecasting Engine",
    subtitle="Northstar Digital Services GmbH • Multidimensional Corporate Performance Management (TM1/OLAP Parity)",
)

st.markdown("""
### Welcome to Northstar Financial Planning & Analytics

This enterprise application provides a complete Corporate Performance Management (CPM) platform with:
* **Multidimensional OLAP Modeling**: Powered by an in-memory 4D cube (TinyOlap) with N-level accounts and C-level consolidations.
* **Deterministic Financial Data**: 3-year historical actuals, budgets, and forecasts with realistic seasonality and corporate events.
* **Decimal Precision Calculations**: Mathematically rigorous financial variance, favourability classification, and operating margin analytics.
* **End-to-End ETL & Data Quality**: CSV/Excel workbook ingestion, schema mapping, row-level validation, and atomic commits.
* **Advanced Scenario Forecasting**: Linear trend extrapolation, driver-based compounding, and side-by-side trajectory analysis.

---
""")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    #### 📈 Executive Dashboards
    * **01 Overview Dashboard**: Executive KPIs, revenue attainment, expense composition, and profit bridges.
    * **04 Financial Explorer**: Multidimensional drill-down across Accounts, Departments, and Periods.
    * **05 Budget & Variance**: Detailed variance analysis with signed convention and favourability badges.
    """)

with col2:
    st.markdown("""
    #### 🔮 Forecasting & Scenarios
    * **06 Forecasting & Scenarios**: Baseline trend projections and assumption-driven sensitivity simulations.
    * **07 Reports & Exports**: Generate formatted executive CSV and multi-sheet Excel reports.
    """)

with col3:
    st.markdown("""
    #### ⚙️ Data Engineering & Governance
    * **02 Upload & Import**: 8-step transactional ETL pipeline with duplicate handling policies.
    * **03 Data Validation**: Data quality error and warning inspector.
    * **08 Import History & Audit**: Immutable event logging and batch drill-downs.
    * **09 Data Model & Admin**: Cube element inspector, health checks, and demo data controls.
    """)

st.info("👈 Use the sidebar navigation on the left to explore the dashboards, forecasting tools, and ETL pipelines.")

render_footer()
