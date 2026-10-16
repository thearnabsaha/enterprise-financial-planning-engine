"""
Financial patterns for synthetic data generation.

Defines base revenue, expense profiles per department, seasonal patterns,
growth trends, and deliberate demonstration events for Northstar Digital Services GmbH.
"""
from __future__ import annotations

from decimal import Decimal


# ─── Base Monthly Revenue by Department (EUR, monthly) ────────────────────────

BASE_MONTHLY_REVENUE: dict[str, Decimal] = {
    "ENG": Decimal("320000"),    # Engineering: product-related revenue
    "SALES": Decimal("480000"),  # Sales: direct customer revenue
    "MKT": Decimal("85000"),     # Marketing: campaign-attributed revenue
    "OPS": Decimal("120000"),    # Operations: service revenue
    "FIN": Decimal("45000"),     # Finance: minimal direct revenue
}

# ─── Base Monthly Expenses by Department × Account (EUR, monthly, positive magnitudes) ─

BASE_EXPENSES: dict[str, dict[str, Decimal]] = {
    "ENG": {
        "SAL": Decimal("180000"),
        "CLOUD": Decimal("45000"),
        "SW": Decimal("12000"),
        "MKT_EXP": Decimal("0"),
        "RENT": Decimal("15000"),
        "TRAVEL": Decimal("5000"),
        "PROF": Decimal("8000"),
        "DEPR": Decimal("6000"),
        "TRAIN": Decimal("4000"),
        "INSUR": Decimal("2500"),
        "OTHER": Decimal("3000"),
    },
    "SALES": {
        "SAL": Decimal("220000"),
        "CLOUD": Decimal("5000"),
        "SW": Decimal("8000"),
        "MKT_EXP": Decimal("15000"),
        "RENT": Decimal("12000"),
        "TRAVEL": Decimal("18000"),
        "PROF": Decimal("12000"),
        "DEPR": Decimal("3000"),
        "TRAIN": Decimal("6000"),
        "INSUR": Decimal("3000"),
        "OTHER": Decimal("4000"),
    },
    "MKT": {
        "SAL": Decimal("95000"),
        "CLOUD": Decimal("3000"),
        "SW": Decimal("15000"),
        "MKT_EXP": Decimal("55000"),
        "RENT": Decimal("8000"),
        "TRAVEL": Decimal("8000"),
        "PROF": Decimal("10000"),
        "DEPR": Decimal("2000"),
        "TRAIN": Decimal("3000"),
        "INSUR": Decimal("1500"),
        "OTHER": Decimal("2500"),
    },
    "OPS": {
        "SAL": Decimal("110000"),
        "CLOUD": Decimal("25000"),
        "SW": Decimal("6000"),
        "MKT_EXP": Decimal("0"),
        "RENT": Decimal("20000"),
        "TRAVEL": Decimal("3000"),
        "PROF": Decimal("5000"),
        "DEPR": Decimal("8000"),
        "TRAIN": Decimal("2000"),
        "INSUR": Decimal("4000"),
        "OTHER": Decimal("5000"),
    },
    "FIN": {
        "SAL": Decimal("85000"),
        "CLOUD": Decimal("2000"),
        "SW": Decimal("5000"),
        "MKT_EXP": Decimal("0"),
        "RENT": Decimal("6000"),
        "TRAVEL": Decimal("3000"),
        "PROF": Decimal("15000"),
        "DEPR": Decimal("1500"),
        "TRAIN": Decimal("2500"),
        "INSUR": Decimal("2000"),
        "OTHER": Decimal("2000"),
    },
}

# ─── Seasonal Multipliers (monthly index 0-11 → Jan-Dec) ────────────────────

REVENUE_SEASONALITY: list[float] = [
    0.85,   # Jan — post-holiday slowdown
    0.90,   # Feb
    0.95,   # Mar — Q1 close
    1.00,   # Apr
    1.02,   # May
    1.05,   # Jun — Q2 close, mid-year push
    0.92,   # Jul — summer slowdown
    0.88,   # Aug — vacation month
    1.00,   # Sep — back to business
    1.08,   # Oct
    1.10,   # Nov — pre-year-end push
    1.15,   # Dec — Q4 close, year-end deals
]

EXPENSE_SEASONALITY: list[float] = [
    0.95,   # Jan — budget reset
    0.97,   # Feb
    1.00,   # Mar
    1.00,   # Apr
    1.00,   # May
    1.02,   # Jun — mid-year spending
    0.95,   # Jul
    0.90,   # Aug — reduced activity
    1.00,   # Sep
    1.05,   # Oct — Q4 push
    1.08,   # Nov
    1.10,   # Dec — year-end spending
]

# ─── Year-over-Year Growth Rates ─────────────────────────────────────────────

ANNUAL_REVENUE_GROWTH: dict[int, float] = {
    2024: 0.00,   # Base year
    2025: 0.08,   # 8% growth
    2026: 0.12,   # 12% growth (acceleration)
}

ANNUAL_EXPENSE_GROWTH: dict[int, float] = {
    2024: 0.00,
    2025: 0.05,   # 5% expense growth
    2026: 0.06,   # 6% expense growth
}

# ─── Deliberate Demonstration Events ────────────────────────────────────────

DEMO_EVENTS: list[dict] = [
    {
        "description": "Engineering cloud costs spike Q3 2025",
        "department": "ENG",
        "account": "CLOUD",
        "period_range": ("2025-07", "2025-09"),
        "multiplier": 1.40,  # +40% increase
        "scenarios": ["Actuals"],
    },
    {
        "description": "Sales revenue exceeds budget Q4 2024",
        "department": "SALES",
        "account": "REV",
        "period_range": ("2024-10", "2024-12"),
        "multiplier": 1.15,  # +15% above baseline
        "scenarios": ["Actuals"],
    },
    {
        "description": "Marketing exceeds budget in 2025",
        "department": "MKT",
        "account": "MKT_EXP",
        "period_range": ("2025-01", "2025-12"),
        "multiplier": 1.20,  # 20% overspend
        "scenarios": ["Actuals"],
    },
    {
        "description": "Revenue dip Q1 2026",
        "department": "SALES",
        "account": "REV",
        "period_range": ("2026-01", "2026-03"),
        "multiplier": 0.92,  # -8% below forecast
        "scenarios": ["Actuals"],
    },
    {
        "description": "Strong revenue Q2 2025 for Engineering",
        "department": "ENG",
        "account": "REV",
        "period_range": ("2025-04", "2025-06"),
        "multiplier": 1.12,  # +12% above baseline
        "scenarios": ["Actuals"],
    },
]

# ─── Budget Deviation Noise ──────────────────────────────────────────────────

# Standard deviation for random noise applied to actuals vs budget (as a fraction)
ACTUALS_NOISE_STD = 0.03  # ±3% random variation on actuals

# Budget tends to be slightly optimistic on revenue, slightly low on expenses
BUDGET_REVENUE_BIAS = 1.02   # Budget assumes 2% more revenue
BUDGET_EXPENSE_BIAS = 0.97   # Budget assumes 3% less expense

# ─── Forecast Assumptions for Generated Scenarios ────────────────────────────

FORECAST_ASSUMPTIONS: dict[str, dict[str, float]] = {
    "Forecast v1": {
        "revenue_growth_rate": 0.06,
        "salary_growth_rate": 0.04,
        "cloud_cost_growth_rate": 0.08,
        "marketing_budget_adjustment": 0.02,
        "rent_escalation_rate": 0.03,
        "travel_adjustment": 0.01,
        "software_cost_growth": 0.05,
        "professional_services_adjustment": 0.02,
        "depreciation_rate": 0.01,
        "other_expense_growth": 0.02,
    },
    "Optimistic Scenario": {
        "revenue_growth_rate": 0.15,
        "salary_growth_rate": 0.05,
        "cloud_cost_growth_rate": 0.06,
        "marketing_budget_adjustment": 0.08,
        "rent_escalation_rate": 0.03,
        "travel_adjustment": 0.05,
        "software_cost_growth": 0.04,
        "professional_services_adjustment": 0.03,
        "depreciation_rate": 0.01,
        "other_expense_growth": 0.02,
    },
    "Conservative Scenario": {
        "revenue_growth_rate": 0.02,
        "salary_growth_rate": 0.03,
        "cloud_cost_growth_rate": 0.10,
        "marketing_budget_adjustment": -0.05,
        "rent_escalation_rate": 0.03,
        "travel_adjustment": -0.10,
        "software_cost_growth": 0.03,
        "professional_services_adjustment": 0.00,
        "depreciation_rate": 0.01,
        "other_expense_growth": 0.01,
    },
}
