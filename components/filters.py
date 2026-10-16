"""
Reusable filter components for Streamlit views (periods, departments, scenarios).
"""
from __future__ import annotations

from typing import NamedTuple, Optional
import streamlit as st

from database import repository as repo
from database.connection import get_session


class FilterState(NamedTuple):
    start_period: Optional[str]
    end_period: Optional[str]
    department_codes: Optional[list[str]]
    scenario: str
    compare_scenario: str


def render_sidebar_filters(
    default_scenario: str = "Actuals",
    default_compare: str = "Original Budget",
) -> FilterState:
    """
    Render standard filter controls in the Streamlit sidebar.
    Returns FilterState with selected parameters.
    """
    with st.sidebar:
        st.subheader("Filter & Scope")

        # 1. Scenarios
        with get_session() as session:
            scenarios = [s.name for s in repo.get_all_scenarios(session)]
            depts = repo.get_all_departments(session)
            periods = repo.get_all_periods(session)

        scn_options = scenarios or ["Actuals", "Original Budget", "Revised Budget", "Forecast v1"]
        active_idx = scn_options.index(default_scenario) if default_scenario in scn_options else 0
        comp_idx = scn_options.index(default_compare) if default_compare in scn_options else min(1, len(scn_options) - 1)

        selected_scenario = st.selectbox("Active Scenario", scn_options, index=active_idx)
        selected_compare = st.selectbox("Comparison Scenario", scn_options, index=comp_idx)

        # 2. Period Range
        period_keys = [p.period_key for p in periods] or [f"2024-{m:02d}" for m in range(1, 13)]
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            start_period = st.selectbox("Start Period", period_keys, index=0)
        with col_p2:
            end_period = st.selectbox("End Period", period_keys, index=len(period_keys) - 1)

        # 3. Department Selection
        leaf_depts = [d for d in depts if d.code != "COMPANY"]
        dept_options = {d.code: d.name for d in leaf_depts}

        select_all_depts = st.checkbox("All Departments", value=True)
        if select_all_depts:
            selected_dept_codes = list(dept_options.keys())
        else:
            selected_dept_codes = st.multiselect(
                "Select Departments",
                options=list(dept_options.keys()),
                default=list(dept_options.keys()),
                format_func=lambda code: f"{code} - {dept_options.get(code, code)}",
            )

        st.markdown("---")
        st.caption("Northstar Digital Services GmbH • TM1 Financial Model")

    return FilterState(
        start_period=start_period,
        end_period=end_period,
        department_codes=selected_dept_codes,
        scenario=selected_scenario,
        compare_scenario=selected_compare,
    )
