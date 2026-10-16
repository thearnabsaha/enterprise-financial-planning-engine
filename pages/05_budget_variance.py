"""
Budget & Variance Analysis — Detailed variance breakdown and favourability classification.
"""
from __future__ import annotations

import streamlit as st

from components.charts import chart_department_breakdown, chart_waterfall_variance
from components.data_tables import render_financial_table
from components.filters import render_sidebar_filters
from components.navigation import render_footer, render_header
from components.styles import apply_theme
from services.calculation_service import CalculationService

apply_theme()
filters = render_sidebar_filters()

render_header(
    title="Budget & Variance Analysis",
    subtitle="Northstar Digital Services GmbH • Signed Variance & Favourability Accounting",
    period_label=f"{filters.start_period} to {filters.end_period}",
    scenario_label=f"{filters.scenario} vs {filters.compare_scenario}",
)

# 1. Calculation service queries
kpis = CalculationService.get_kpis(
    start_period=filters.start_period,
    end_period=filters.end_period,
    department_codes=filters.department_codes,
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

dept_df = CalculationService.get_department_variance_summary(
    start_period=filters.start_period,
    end_period=filters.end_period,
    scenario_name=filters.scenario,
    compare_scenario=filters.compare_scenario,
)

# 2. Executive Variance Callout
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Net Variance", f"€ {float(kpis.get('profit_variance', 0)):+,.2f}")
with col2:
    st.metric("Revenue Variance", f"€ {float(kpis.get('revenue_variance', 0)):+,.2f}")
with col3:
    st.metric("Operating Expense Variance", f"€ {float(kpis.get('expenses_variance', 0)):+,.2f}")

st.markdown("""
<div class="info-callout">
<strong>Financial Sign Convention:</strong>
Revenue is represented as a positive amount (+), while Operating Expenses are represented as negative amounts (-).
For revenue, a positive variance represents higher income (<strong>FAVOURABLE</strong>).
For expenses, actual costs that are <em>more negative</em> than budget represent overspending (<strong>UNFAVOURABLE</strong>).
</div>
""", unsafe_allow_html=True)

# 3. Waterfall Bridge
st.subheader("Profit Bridge: Walk from Budget to Actual (€)")
bud_p = float(kpis.get("profit_budget", 0))
act_p = float(kpis.get("profit", 0))
fig_waterfall = chart_waterfall_variance(bud_p, act_p, dept_df)
st.plotly_chart(fig_waterfall, use_container_width=True)

# 4. Top Contributors
col_fav, col_unfav = st.columns(2)
with col_fav:
    st.subheader("Top Favourable Drivers")
    fav_df = acct_df[acct_df["Favourability"] == "FAVOURABLE"].sort_values("Variance (€)", ascending=False).head(5)
    render_financial_table(fav_df, height=200)

with col_unfav:
    st.subheader("Top Unfavourable Drivers")
    unfav_df = acct_df[acct_df["Favourability"] == "UNFAVOURABLE"].sort_values("Variance (€)", ascending=True).head(5)
    render_financial_table(unfav_df, height=200)

# 5. Full Account Detail Table
st.subheader("Account Variance Detail Table")
render_financial_table(acct_df, height=350)

render_footer()
