"""
Reports & Exports — Multi-format reporting suite (CSV and formatted Excel workbooks).
"""
from __future__ import annotations

import streamlit as st

from components.data_tables import render_financial_table
from components.filters import render_sidebar_filters
from components.navigation import render_footer, render_header
from components.styles import apply_theme
from services.calculation_service import CalculationService
from services.export_service import ExportService
from services.forecast_service import ForecastService

apply_theme()
filters = render_sidebar_filters()

render_header(
    title="Financial Reports & Export Suite",
    subtitle="Northstar Digital Services GmbH • Executive Workbooks & Analytical Extracts",
    period_label=f"{filters.start_period} to {filters.end_period}",
    scenario_label=f"{filters.scenario} vs {filters.compare_scenario}",
)

report_type = st.selectbox(
    "Select Report Type:",
    [
        "Department Performance Summary",
        "Account Variance Breakdown",
        "Monthly Trend & Profitability",
        "Complete Multi-Sheet Executive Financial Book (Excel)",
    ],
)

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

trend_df = CalculationService.get_monthly_trend(
    department_codes=filters.department_codes,
    scenario_name=filters.scenario,
    compare_scenario=filters.compare_scenario,
)

# Render Preview & Download buttons
if report_type == "Department Performance Summary":
    st.subheader("Report Preview: Department Performance")
    render_financial_table(dept_df, height=300)

    col1, col2 = st.columns(2)
    with col1:
        csv_bytes = ExportService.dataframe_to_csv(dept_df)
        st.download_button("📥 Download CSV", data=csv_bytes, file_name="department_performance.csv", mime="text/csv")
    with col2:
        xlsx_bytes = ExportService.generate_excel_report(
            {"Department Summary": dept_df},
            report_title="Department Performance Summary",
            filters={"Period": f"{filters.start_period} to {filters.end_period}", "Scenario": filters.scenario},
        )
        st.download_button("📥 Download Formatted Excel (XLSX)", data=xlsx_bytes, file_name="department_performance.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

elif report_type == "Account Variance Breakdown":
    st.subheader("Report Preview: Account Variance Breakdown")
    render_financial_table(acct_df, height=350)

    col1, col2 = st.columns(2)
    with col1:
        csv_bytes = ExportService.dataframe_to_csv(acct_df)
        st.download_button("📥 Download CSV", data=csv_bytes, file_name="account_variances.csv", mime="text/csv")
    with col2:
        xlsx_bytes = ExportService.generate_excel_report(
            {"Account Breakdown": acct_df},
            report_title="Account Variance Breakdown",
            filters={"Period": f"{filters.start_period} to {filters.end_period}", "Scenario": filters.scenario},
        )
        st.download_button("📥 Download Formatted Excel (XLSX)", data=xlsx_bytes, file_name="account_variances.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

elif report_type == "Monthly Trend & Profitability":
    st.subheader("Report Preview: Monthly Trend & Profitability")
    render_financial_table(trend_df, height=350)

    col1, col2 = st.columns(2)
    with col1:
        csv_bytes = ExportService.dataframe_to_csv(trend_df)
        st.download_button("📥 Download CSV", data=csv_bytes, file_name="monthly_trends.csv", mime="text/csv")
    with col2:
        xlsx_bytes = ExportService.generate_excel_report(
            {"Monthly Trends": trend_df},
            report_title="Monthly Financial Trends",
            filters={"Scenario": filters.scenario},
        )
        st.download_button("📥 Download Formatted Excel (XLSX)", data=xlsx_bytes, file_name="monthly_trends.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

else:
    st.subheader("Complete Multi-Sheet Executive Financial Book")
    st.markdown("""
    Generates an executive-ready Excel workbook with:
    * **Sheet 1**: Department Performance Summary
    * **Sheet 2**: Account Variance Breakdown
    * **Sheet 3**: Monthly Financial Trends
    * **Sheet 4**: Multi-Scenario Forecast Trajectories
    * **Sheet 5**: Audit Metadata & Applied Filter Configuration
    """)

    multi_df = ForecastService.get_multi_scenario_comparison(account_code="REV")
    sheets = {
        "Departments": dept_df,
        "Accounts": acct_df,
        "Monthly Trends": trend_df,
        "Scenario Forecasts": multi_df,
    }

    excel_book_bytes = ExportService.generate_excel_report(
        sheets=sheets,
        report_title="Northstar Digital Services — Executive Financial Book",
        filters={
            "Period Range": f"{filters.start_period} to {filters.end_period}",
            "Active Scenario": filters.scenario,
            "Comparison Scenario": filters.compare_scenario,
            "Departments": ", ".join(filters.department_codes) if filters.department_codes else "All",
        },
    )

    st.download_button(
        "📥 Download Complete Financial Workbook (Excel XLSX)",
        data=excel_book_bytes,
        file_name="Northstar_Executive_Financial_Book.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary",
    )

render_footer()
