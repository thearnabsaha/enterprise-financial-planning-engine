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

# 2. Render KPI Row
render_kpi_row(kpis)

st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)

# 3. Monthly Trends & Profit Trajectory
trend_df = CalculationService.get_monthly_trend(
    department_codes=filters.department_codes,
    scenario_name=filters.scenario,
    compare_scenario=filters.compare_scenario,
)

col_chart1, col_chart2 = st.columns(2)
with col_chart1:
    fig_rev = chart_revenue_vs_budget(trend_df)
    st.plotly_chart(fig_rev, use_container_width=True)

with col_chart2:
    fig_profit = chart_monthly_profit_trend(trend_df)
    st.plotly_chart(fig_profit, use_container_width=True)

# 4. Department & Account Breakdown
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

col_chart3, col_chart4 = st.columns(2)
with col_chart3:
    fig_dept = chart_department_breakdown(dept_df)
    st.plotly_chart(fig_dept, use_container_width=True)

with col_chart4:
    fig_donut = chart_expense_donut(acct_df)
    st.plotly_chart(fig_donut, use_container_width=True)

# 5. Profit Variance Waterfall Bridge & Multi-Scenario Trajectory
col_chart5, col_chart6 = st.columns(2)
with col_chart5:
    bud_p = float(kpis.get("profit_budget", 0))
    act_p = float(kpis.get("profit", 0))
    fig_waterfall = chart_waterfall_variance(bud_p, act_p, dept_df)
    st.plotly_chart(fig_waterfall, use_container_width=True)

with col_chart6:
    multi_df = ForecastService.get_multi_scenario_comparison(account_code="REV")
    fig_multi = chart_scenario_comparison(multi_df)
    st.plotly_chart(fig_multi, use_container_width=True)

# 6. Summary Table
st.markdown("### Department Performance Summary")
render_financial_table(dept_df, height=280)

render_footer()
