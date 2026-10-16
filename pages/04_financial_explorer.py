"""
Financial Explorer — Multidimensional drill-down & OLAP cube cell querying.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from components.data_tables import render_financial_table
from components.filters import render_sidebar_filters
from components.navigation import render_footer, render_header
from components.styles import apply_theme
from database import repository as repo
from database.connection import get_session
from olap.cache import get_olap_adapter

apply_theme()
filters = render_sidebar_filters()

render_header(
    title="Financial Explorer & OLAP Cube Inspector",
    subtitle="Northstar Digital Services GmbH • Dynamic Drill-Down & Multidimensional Querying",
    period_label=f"{filters.start_period} to {filters.end_period}",
    scenario_label=filters.scenario,
)

tab_pivot, tab_cube = st.tabs(["📊 Financial Matrix Pivot", "🧊 TinyOlap Cell Inspector"])

with tab_pivot:
    st.subheader("Financial Matrix (Accounts × Periods)")

    with get_session() as s:
        accounts = repo.get_all_accounts(s)
        periods = repo.get_all_periods(s)
        depts = repo.get_all_departments(s)

        selected_dept = st.selectbox(
            "Department Filter:",
            options=["COMPANY"] + [d.code for d in depts if d.code != "COMPANY"],
            format_func=lambda c: f"{c} - Consolidated" if c == "COMPANY" else c,
        )

        dept_id = None
        if selected_dept != "COMPANY":
            d_obj = repo.get_department_by_code(s, selected_dept)
            if d_obj:
                dept_id = [d_obj.id]

        facts = repo.get_financial_facts(
            session=s,
            scenario_name=filters.scenario,
            start_period=filters.start_period,
            end_period=filters.end_period,
            department_ids=dept_id,
        )

        acct_map = {a.id: f"{a.code} - {a.name}" for a in accounts}
        period_map = {p.id: p.period_key for p in periods}

        pivot_data = []
        for f in facts:
            pivot_data.append({
                "Account": acct_map.get(f.account_id, "Unknown"),
                "Period": period_map.get(f.period_id, "Unknown"),
                "Amount": float(f.amount),
            })

        if pivot_data:
            df_pivot = pd.DataFrame(pivot_data)
            pivoted = df_pivot.pivot_table(index="Account", columns="Period", values="Amount", aggfunc="sum").fillna(0)
            st.dataframe(pivoted.style.format("€ {:,.2f}"), use_container_width=True)
        else:
            st.info("No records found for the selected scope.")

with tab_cube:
    st.subheader("Direct TinyOlap Cube Cell Query")
    st.markdown("Query the in-memory multidimensional cube directly across any intersection:")

    c_col1, c_col2, c_col3, c_col4 = st.columns(4)
    with c_col1:
        q_acc = st.selectbox("Account (Leaf, Consolidation, or Rule)", ["REV", "TOTAL_OPEX", "Operating Profit", "Operating Margin", "SAL", "CLOUD", "SW", "MKT_EXP"])
    with c_col2:
        q_dept = st.selectbox("Department", ["COMPANY", "ENG", "SALES", "MKT", "OPS", "FIN"])
    with c_col3:
        q_period = st.selectbox("Period", [p.period_key for p in periods])
    with c_col4:
        q_scenario = st.selectbox("Scenario", [s.name for s in repo.get_all_scenarios(s)])

    adapter = get_olap_adapter()
    cell_val = adapter.get_cell(q_acc, q_dept, q_period, q_scenario)

    st.markdown("#### Query Result:")
    if q_acc == "Operating Margin":
        st.success(f"**Cube Cell Value:** `{cell_val:.2f}%`")
    else:
        st.success(f"**Cube Cell Value:** `€ {cell_val:,.2f}`")

render_footer()
