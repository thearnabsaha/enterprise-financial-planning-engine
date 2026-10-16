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

with get_session() as session:
    all_accounts = repo.get_all_accounts(session)
    all_periods = repo.get_all_periods(session)
    all_depts = repo.get_all_departments(session)
    all_scenarios = repo.get_all_scenarios(session)

    acct_map = {a.id: f"{a.code} - {a.name}" for a in all_accounts}
    period_map = {p.id: p.period_key for p in all_periods}
    dept_map = {d.code: d.id for d in all_depts}
    period_keys = [p.period_key for p in all_periods]
    scenario_names = [sc.name for sc in all_scenarios]
    dept_codes = [d.code for d in all_depts]

tab_pivot, tab_cube = st.tabs(["📊 Financial Matrix Pivot", "🧊 TinyOlap Cell Inspector"])

with tab_pivot:
    st.subheader("Financial Matrix (Accounts × Periods)")

    dept_options = ["COMPANY"] + [c for c in dept_codes if c != "COMPANY"]
    selected_dept = st.selectbox(
        "Department Filter:",
        options=dept_options,
        format_func=lambda c: f"{c} - Consolidated" if c == "COMPANY" else c,
    )

    dept_id = None
    if selected_dept != "COMPANY" and selected_dept in dept_map:
        dept_id = [dept_map[selected_dept]]

    with get_session() as session:
        facts = repo.get_financial_facts(
            session=session,
            scenario_name=filters.scenario,
            start_period=filters.start_period,
            end_period=filters.end_period,
            department_ids=dept_id,
        )

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
        q_dept = st.selectbox("Department", ["COMPANY"] + [c for c in dept_codes if c != "COMPANY"])
    with c_col3:
        q_period = st.selectbox("Period", period_keys)
    with c_col4:
        scenario_idx = scenario_names.index(filters.scenario) if filters.scenario in scenario_names else 0
        q_scenario = st.selectbox("Scenario", scenario_names, index=scenario_idx)

    adapter = get_olap_adapter()
    cell_val = adapter.get_cell(q_acc, q_dept, q_period, q_scenario)

    st.markdown("#### Query Result:")
    if q_acc == "Operating Margin":
        st.success(f"**Cube Cell Value:** `{cell_val:.2f}%`")
    else:
        st.success(f"**Cube Cell Value:** `€ {cell_val:,.2f}`")

render_footer()
