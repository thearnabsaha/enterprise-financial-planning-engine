"""
Forecasting & Scenarios — Three forecast methods and driver sensitivity simulation.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from components.charts import chart_scenario_comparison
from components.data_tables import render_financial_table
from components.filters import render_sidebar_filters
from components.navigation import render_footer, render_header
from components.styles import apply_theme
from services.forecast_service import ForecastService

apply_theme()
filters = render_sidebar_filters()

render_header(
    title="Forecasting & Scenario Modeling",
    subtitle="Northstar Digital Services GmbH • Driver-Based Sensitivity & Trajectory Projections",
    period_label=f"{filters.start_period} to {filters.end_period}",
    scenario_label=filters.scenario,
)

tab_multi, tab_baseline, tab_drivers = st.tabs([
    "📈 Multi-Scenario Comparison",
    "📐 Baseline Trend Extrapolation",
    "⚙️ Assumption Driver Sensitivity",
])

with tab_multi:
    st.subheader("Scenario Trajectories Comparison")
    target_metric = st.selectbox("Select Account for Trajectory Comparison:", ["REV", "CLOUD", "SAL", "SW", "MKT_EXP"])
    multi_df = ForecastService.get_multi_scenario_comparison(account_code=target_metric)

    if not multi_df.empty:
        fig_multi = chart_scenario_comparison(multi_df)
        st.plotly_chart(fig_multi, use_container_width=True)
        render_financial_table(multi_df, title="Monthly Trajectory Data (€)", height=300)

with tab_baseline:
    st.subheader("Method 1: Baseline Linear Extrapolation")
    st.markdown("Extrapolates future revenue and expenses using linear regression over historical actuals:")

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        extrap_acc = st.selectbox("Extrapolate Account:", ["REV", "CLOUD", "SAL", "TOTAL_OPEX"])
    with col_b2:
        extrap_periods = st.slider("Periods Ahead to Project:", min_value=3, max_value=24, value=12)

    if st.button("Generate Baseline Projection"):
        results = ForecastService.generate_baseline_forecast(account_code=extrap_acc, periods_ahead=extrap_periods)
        if results:
            res_df = pd.DataFrame([{
                "Period": r.period_key,
                "Account": r.account,
                "Projected Amount (€)": float(r.amount),
                "Method": r.method.value.upper(),
            } for r in results])
            render_financial_table(res_df, title="Projected Periods", height=300)

with tab_drivers:
    st.subheader("Method 2 & 3: Assumption Driver Sensitivity")
    st.markdown("Inspect and tune operational growth rate assumptions for scenario modeling:")

    assumptions = ForecastService.get_forecast_assumptions("Forecast v1")
    if assumptions:
        as_df = pd.DataFrame(assumptions)
        st.dataframe(as_df, use_container_width=True, hide_index=True)

        st.markdown("#### Adjust Driver Assumptions:")
        adj_col1, adj_col2, adj_col3 = st.columns(3)
        with adj_col1:
            new_rev_rate = st.number_input("Revenue Growth Rate (e.g. 0.08 = 8%):", value=0.08, step=0.01)
        with adj_col2:
            new_cloud_rate = st.number_input("Cloud Cost Growth Rate (e.g. 0.12 = 12%):", value=0.12, step=0.01)
        with adj_col3:
            new_salary_rate = st.number_input("Salary Inflation Rate (e.g. 0.04 = 4%):", value=0.04, step=0.01)

        if st.button("Update Scenario Assumptions"):
            ForecastService.update_assumption("Forecast v1", "revenue_growth_rate", new_rev_rate)
            ForecastService.update_assumption("Forecast v1", "cloud_cost_growth_rate", new_cloud_rate)
            ForecastService.update_assumption("Forecast v1", "salary_growth_rate", new_salary_rate)
            st.success("Updated scenario drivers successfully!")

render_footer()
