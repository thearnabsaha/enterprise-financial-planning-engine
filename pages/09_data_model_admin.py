"""
Data Model & Administration — Multidimensional hierarchies, DB status, and cube maintenance.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from components.navigation import render_footer, render_header
from components.styles import apply_theme
from database import repository as repo
from database.connection import check_connection, get_session
from database.seed import seed_database
from olap.cache import get_olap_adapter, invalidate_olap_cache

apply_theme()

render_header(
    title="Data Model & System Administration",
    subtitle="Northstar Digital Services GmbH • Dimension Hierarchies, Table Volumes & OLAP Cube Health",
)

# 1. System Health & Connectivity
st.subheader("System Infrastructure & Connectivity")
conn_info = check_connection()
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Database Status", conn_info.get("status", "Unknown").upper())
with c2:
    st.metric("Database Dialect", conn_info.get("dialect", "Unknown").upper())
with c3:
    adapter = get_olap_adapter()
    st.metric("TinyOlap Cube Status", f"ONLINE ({adapter.fact_count:,} facts)")

# 2. Table Volume Statistics
st.subheader("Database Table Volume Statistics")
with get_session() as s:
    stats = repo.get_table_counts(s)

st.dataframe(pd.DataFrame(list(stats.items()), columns=["Table Entity", "Row Count"]), hide_index=True)

# 3. Dimension Hierarchies
tab_dept, tab_acct, tab_scen = st.tabs(["🏢 Department Hierarchy", "📑 Chart of Accounts Hierarchy", "🎯 Scenarios & Versions"])

with tab_dept:
    st.markdown("""
    **Northstar Department Hierarchy (TM1 Dimension 'Department'):**
    * `COMPANY` (Consolidated Parent — Weight 1.0)
        * `ENG` — Engineering (Leaf — Weight 1.0)
        * `SALES` — Sales (Leaf — Weight 1.0)
        * `MKT` — Marketing (Leaf — Weight 1.0)
        * `OPS` — Operations (Leaf — Weight 1.0)
        * `FIN` — Finance (Leaf — Weight 1.0)
    """)

with tab_acct:
    st.markdown("""
    **Northstar Chart of Accounts Hierarchy (TM1 Dimension 'Account'):**
    * `REV` — Revenue (Positive +)
    * `TOTAL_OPEX` — Total Operating Expenses (Consolidation — Negative -)
        * `SAL` — Salaries and Benefits (Leaf)
        * `CLOUD` — Cloud Infrastructure (Leaf)
        * `SW` — Software Subscriptions (Leaf)
        * `MKT_EXP` — Marketing Expenses (Leaf)
        * `RENT` — Rent and Facilities (Leaf)
        * `TRAVEL` — Travel and Entertainment (Leaf)
        * `PROF` — Professional Services (Leaf)
        * `DEPR` — Depreciation (Leaf)
        * `INSUR` — Insurance (Leaf)
        * `TRAIN` — Training and Development (Leaf)
        * `OTHER` — Other Operating Expenses (Leaf)
    * **Calculated Rules:**
        * `Operating Profit` = Revenue + Total Operating Expenses
        * `Operating Margin` = (Operating Profit / Revenue) × 100
    """)

with tab_scen:
    with get_session() as s:
        scenarios = repo.get_all_scenarios(s)
        versions = repo.get_all_versions(s)
    st.markdown("**Registered Scenarios:**")
    st.dataframe(pd.DataFrame([{"Name": sc.name, "Description": sc.description} for sc in scenarios]), hide_index=True)

# 4. Maintenance & Demo Data Regeneration
st.subheader("Administrative Actions")
col_a1, col_a2 = st.columns(2)
with col_a1:
    if st.button("🔄 Invalidate & Refresh TinyOlap Cache"):
        invalidate_olap_cache()
        get_olap_adapter(force_refresh=True)
        st.success("TinyOlap multidimensional cache refreshed successfully!")

with col_a2:
    if st.button("⚠️ Reset & Re-Seed Database with Demo Data"):
        with st.spinner("Re-seeding database from generated fixtures..."):
            res = seed_database()
            invalidate_olap_cache()
            st.success(f"Database re-seeded successfully with {res.get('facts', 0):,} facts!")

render_footer()
