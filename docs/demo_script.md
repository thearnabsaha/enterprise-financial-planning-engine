# Demonstration Walkthrough & Portfolio Presentation Script

**Project:** Enterprise Financial Planning & Forecasting Engine  
**Fictional Enterprise:** Northstar Digital Services GmbH  
**Presenter:** Arnab Saha  

---

## Overview

This demonstration script outlines an executive walkthrough of the system, highlighting engineering rigor, multidimensional OLAP modeling, precision accounting, and data governance.

---

## 5-Minute Demonstration Walkthrough

### Act 1: Executive KPI Dashboard & Profit Bridge (Page 01)
1. **Open Page 01**: Show the Executive Overview Dashboard.
2. **Point out the 6 Executive KPIs**: Total Revenue, Operating Expenses, Operating Profit, Operating Margin %, Budget Variance, Revenue Attainment.
3. **Highlight the Profit Waterfall Bridge**: Explain how the bridge walks from Budget Profit (€1.4M) through department-level variances to reach Actual Profit (€1.6M).
4. **Demonstrate Filter Agility**: Change the Active Scenario from "Actuals" to "Forecast v1" or filter by "Engineering" and "Sales". Show how all 6 Plotly charts and KPI cards instantly re-aggregate in real-time.

### Act 2: Multidimensional Cube & OLAP Inspector (Page 04)
1. **Open Page 04**: Switch to the **Financial Explorer**.
2. **Matrix Pivot**: Display the 36-month monthly financial matrix across accounts.
3. **Direct Cube Cell Query**:
   - Query `REV` at `COMPANY` consolidation for `2024-01` under `Actuals`.
   - Explain how `COMPANY` rolls up leaf departments (`ENG`, `SALES`, `MKT`, `OPS`, `FIN`) in memory.
   - Query `Operating Profit` and `Operating Margin` to demonstrate the `@rule` calculation engine evaluating on-the-fly.

### Act 3: Budget & Variance Analysis with Sign Conventions (Page 05)
1. **Open Page 05**: Show the Budget & Variance Analysis view.
2. **Explain the Sign Convention Standard**:
   - Walk through why revenue is positive ($+$) and expenses are negative ($-$).
   - Point to the cloud infrastructure overspend in Q3 2025: Actual was $-€55\text{k}$ vs Budget $-€50\text{k}$. The signed variance is $-€5\text{k}$, correctly flagged with an **UNFAVOURABLE** red badge.
   - Show how underspending (e.g. Travel and Entertainment) produces a positive signed variance, correctly flagged with a **FAVOURABLE** green badge.

### Act 4: Scenario Modeling & Sensitivity Projections (Page 06)
1. **Open Page 06**: Show Forecasting & Scenarios.
2. **Baseline Extrapolation**: Fit a linear trend to historical actuals and project 12 months ahead.
3. **Driver Tuning**: Adjust the revenue growth driver from 8% to 12% and cloud inflation to 15%, and show the immediate impact on projected operating margin trajectories.

### Act 5: Data Ingestion & Transactional ETL (Page 02 & 08)
1. **Open Page 02**: Go to Upload & Import.
2. **Load Sample Data**: Pick `invalid_test_data.csv`.
3. **Show Automated Validation**: Show how the validation engine catches unmapped department codes, invalid dates, and malformed currency values, protecting the relational store from corruption.
4. **Explain Duplicate Policy**: Demonstrate the difference between `REJECT`, `SKIP`, and `REPLACE` duplicate handling.
5. **Open Page 08**: Show the immutable audit trail and batch lineage log.

### Act 6: Formatted Multi-Sheet Excel Export (Page 07)
1. **Open Page 07**: Go to Reports & Exports.
2. **Download Complete Executive Book**: Download the `.xlsx` file and open it.
3. **Highlight Polish**: Point out the styled dark headers, auto-fitted columns, native currency number formatting (`€#,##0.00`), percentage formatting (`0.00%`), and the dedicated metadata audit tab.

---

*End of Demonstration.*
