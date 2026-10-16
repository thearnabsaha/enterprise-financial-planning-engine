"""
Executive Overview Dashboard — Northstar Digital Services GmbH
"""
from __future__ import annotations

import streamlit as st

from components.charts import (
    chart_department_breakdown,
    chart_expense_donut,
    chart_monthly_profit_trend,
    chart_revenue_vs_budget,
    chart_scenario_comparison,
    chart_waterfall_variance,
)
from components.data_tables import render_financial_table
from components.filters import render_sidebar_filters
from components.kpi_cards import render_kpi_row
from components.navigation import render_footer, render_header
from components.styles import apply_theme
from services.calculation_service import CalculationService
from services.forecast_service import ForecastService

apply_theme()

filters = render_sidebar_filters()

period_label = f"{filters.start_period} to {filters.end_period}"
scenario_label = f"{filters.scenario} vs {filters.compare_scenario}"

render_header(
    title="Executive Overview Dashboard",
    subtitle="Northstar Digital Services GmbH • Financial Summary & Performance Metrics",
    period_label=period_label,
    scenario_label=scenario_label,
)

# 1. Fetch Executive KPIs
kpis = CalculationService.get_kpis(
    start_period=filters.start_period,
    end_period=filters.end_period,
    department_codes=filters.department_codes,
    scenario_name=filters.scenario,
    compare_scenario=filters.compare_scenario,
)

# 2. Render Executive KPI Grid (4 primary + 2 secondary ratio cards)
render_kpi_row(kpis)

st.html("<div style='margin-top: 24px;'></div>")

# 3. Interactive Analytical Perspectives (Tabs)
tab_trends, tab_structure, tab_variance = st.tabs([
    "📈 Revenue & Profit Trends",
    "🏢 Cost Structure & Departments",
    "🌉 Profit Walk & Scenario Trajectories",
])

with tab_trends:
    st.caption("Monthly performance trajectory against budget targets and operating profit margin walk.")
    trend_df = CalculationService.get_monthly_trend(
        department_codes=filters.department_codes,
        scenario_name=filters.scenario,
        compare_scenario=filters.compare_scenario,
    )
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        fig_rev = chart_revenue_vs_budget(trend_df)
        st.plotly_chart(fig_rev, use_container_width=True)
    with col_t2:
        fig_profit = chart_monthly_profit_trend(trend_df)
        st.plotly_chart(fig_profit, use_container_width=True)

with tab_structure:
    st.caption("Departmental profitability and operating expense composition breakdown.")
    dept_df = CalculationService.get_department_variance_summary(
        start_period=filters.start_period,
        end_period=filters.end_period,
        scenario_name=filters.scenario,
        compare_scenario=filters.compare_scenario,
    )
    acct_df = CalculationService.get_account_variance_summary(
        start_period=filters.start_period,
        end_period=filters.end_period,
        department_codes=filters.department_codes,
        scenario_name=filters.scenario,
        compare_scenario=filters.compare_scenario,
    )
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        fig_dept = chart_department_breakdown(dept_df)
        st.plotly_chart(fig_dept, use_container_width=True)
    with col_s2:
        fig_donut = chart_expense_donut(acct_df)
        st.plotly_chart(fig_donut, use_container_width=True)

with tab_variance:
    st.caption("Departmental variance bridge walk (Budget to Actual) and forward-looking scenario trajectories.")
    dept_df = CalculationService.get_department_variance_summary(
        start_period=filters.start_period,
        end_period=filters.end_period,
        scenario_name=filters.scenario,
        compare_scenario=filters.compare_scenario,
    )
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        bud_p = float(kpis.get("profit_budget", 0))
        act_p = float(kpis.get("profit", 0))
        fig_waterfall = chart_waterfall_variance(bud_p, act_p, dept_df)
        st.plotly_chart(fig_waterfall, use_container_width=True)
    with col_v2:
        multi_df = ForecastService.get_multi_scenario_comparison(account_code="REV")
        fig_multi = chart_scenario_comparison(multi_df)
        st.plotly_chart(fig_multi, use_container_width=True)

# 4. Department Performance Summary Table
st.html("<div style='margin-top: 20px;'></div>")
st.subheader("Department Performance Summary")
dept_df = CalculationService.get_department_variance_summary(
    start_period=filters.start_period,
    end_period=filters.end_period,
    scenario_name=filters.scenario,
    compare_scenario=filters.compare_scenario,
)
render_financial_table(dept_df, height=280)

render_footer()
