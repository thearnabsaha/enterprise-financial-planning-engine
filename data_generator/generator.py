"""
Synthetic financial data generator for Northstar Digital Services GmbH.

Generates deterministic, seed-controlled financial datasets:
  - departments.csv
  - accounts.csv
  - actuals.csv
  - budgets.csv
  - forecasts.csv
  - scenario_assumptions.csv
  - invalid_test_data.csv

Usage:
    from data_generator.generator import DataGenerator
    gen = DataGenerator(seed=42)
    gen.generate_all("data/sample")
"""
from __future__ import annotations

import csv
import logging
import os
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from data_generator.dimensions import (
    ACCOUNTS,
    CURRENCIES,
    DEPARTMENTS,
    LEAF_ACCOUNTS,
    LEAF_DEPARTMENTS,
    PERIOD_END_YEAR,
    PERIOD_MONTHS,
    PERIOD_START_YEAR,
    REVENUE_ACCOUNTS,
    EXPENSE_ACCOUNTS,
    SCENARIOS,
    VERSIONS,
)
from data_generator.financial_patterns import (
    ACTUALS_NOISE_STD,
    ANNUAL_EXPENSE_GROWTH,
    ANNUAL_REVENUE_GROWTH,
    BASE_EXPENSES,
    BASE_MONTHLY_REVENUE,
    BUDGET_EXPENSE_BIAS,
    BUDGET_REVENUE_BIAS,
    DEMO_EVENTS,
    EXPENSE_SEASONALITY,
    FORECAST_ASSUMPTIONS,
    REVENUE_SEASONALITY,
)

logger = logging.getLogger(__name__)

TWO_DP = Decimal("0.01")


class DataGenerator:
    """
    Deterministic synthetic data generator.

    Uses a fixed random seed so that the same seed always produces
    the same dataset.
    """

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self._periods = self._generate_periods()

    def _generate_periods(self) -> list[dict]:
        """Generate all period records."""
        periods = []
        for year in range(PERIOD_START_YEAR, PERIOD_END_YEAR + 1):
            for month in PERIOD_MONTHS:
                import math
                periods.append({
                    "year": year,
                    "month": month,
                    "period_key": f"{year:04d}-{month:02d}",
                    "quarter": math.ceil(month / 3),
                })
        return periods

    def _is_in_range(self, period_key: str, start: str, end: str) -> bool:
        """Check if a period_key falls within a range."""
        return start <= period_key <= end

    def _apply_demo_events(
        self, dept_code: str, account_code: str, period_key: str,
        scenario_name: str, base_value: Decimal,
    ) -> Decimal:
        """Apply demonstration event multipliers if applicable."""
        for event in DEMO_EVENTS:
            if (
                event["department"] == dept_code
                and event["account"] == account_code
                and scenario_name in event["scenarios"]
                and self._is_in_range(period_key, *event["period_range"])
            ):
                multiplier = Decimal(str(event["multiplier"]))
                return (base_value * multiplier).quantize(TWO_DP, rounding=ROUND_HALF_UP)
        return base_value

    def generate_departments_csv(self) -> pd.DataFrame:
        """Generate departments.csv."""
        rows = []
        for dept in DEPARTMENTS:
            rows.append({
                "department_code": dept.code,
                "department_name": dept.name,
                "parent_code": dept.parent_code or "",
            })
        return pd.DataFrame(rows)

    def generate_accounts_csv(self) -> pd.DataFrame:
        """Generate accounts.csv."""
        rows = []
        for acc in ACCOUNTS:
            rows.append({
                "account_code": acc.code,
                "account_name": acc.name,
                "category": acc.category,
                "sign_convention": acc.sign_convention,
                "parent_code": acc.parent_code or "",
            })
        return pd.DataFrame(rows)

    def generate_actuals(self) -> pd.DataFrame:
        """
        Generate actuals data with seasonal patterns, growth trends,
        random noise, and demo events applied.
        """
        rows = []
        for period in self._periods:
            year = period["year"]
            month = period["month"]
            period_key = period["period_key"]
            month_idx = month - 1

            for dept in LEAF_DEPARTMENTS:
                dept_code = dept.code

                # Revenue
                base_rev = BASE_MONTHLY_REVENUE.get(dept_code, Decimal("0"))
                if base_rev > 0:
                    # Apply annual growth
                    growth = Decimal(str(1 + ANNUAL_REVENUE_GROWTH.get(year, 0)))
                    # Apply for each year above base
                    for y in range(PERIOD_START_YEAR + 1, year + 1):
                        growth_y = Decimal(str(1 + ANNUAL_REVENUE_GROWTH.get(y, 0)))
                        base_rev = (base_rev * growth_y).quantize(TWO_DP)

                    # Apply seasonality
                    seasonal = Decimal(str(REVENUE_SEASONALITY[month_idx]))
                    amount = (base_rev * seasonal).quantize(TWO_DP)

                    # Apply random noise
                    noise = Decimal(str(1 + self.rng.normal(0, ACTUALS_NOISE_STD)))
                    amount = (amount * noise).quantize(TWO_DP)

                    # Apply demo events
                    amount = self._apply_demo_events(dept_code, "REV", period_key, "Actuals", amount)

                    rows.append({
                        "date": f"{year:04d}-{month:02d}-01",
                        "period": period_key,
                        "department": dept_code,
                        "account": "REV",
                        "scenario": "Actuals",
                        "version": "v1",
                        "currency": "EUR",
                        "amount": float(amount),
                    })

                # Expenses
                dept_expenses = BASE_EXPENSES.get(dept_code, {})
                for acc in EXPENSE_ACCOUNTS:
                    base_exp = dept_expenses.get(acc.code, Decimal("0"))
                    if base_exp <= 0:
                        continue

                    # Apply annual growth
                    for y in range(PERIOD_START_YEAR + 1, year + 1):
                        growth_y = Decimal(str(1 + ANNUAL_EXPENSE_GROWTH.get(y, 0)))
                        base_exp = (base_exp * growth_y).quantize(TWO_DP)

                    # Apply seasonality
                    seasonal = Decimal(str(EXPENSE_SEASONALITY[month_idx]))
                    magnitude = (base_exp * seasonal).quantize(TWO_DP)

                    # Apply random noise
                    noise = Decimal(str(1 + self.rng.normal(0, ACTUALS_NOISE_STD)))
                    magnitude = (magnitude * noise).quantize(TWO_DP)

                    # Apply demo events (to magnitude)
                    magnitude = self._apply_demo_events(
                        dept_code, acc.code, period_key, "Actuals", magnitude
                    )

                    # Store as negative (expense convention)
                    amount = -magnitude

                    rows.append({
                        "date": f"{year:04d}-{month:02d}-01",
                        "period": period_key,
                        "department": dept_code,
                        "account": acc.code,
                        "scenario": "Actuals",
                        "version": "v1",
                        "currency": "EUR",
                        "amount": float(amount),
                    })

        return pd.DataFrame(rows)

    def generate_budgets(self) -> pd.DataFrame:
        """
        Generate budget data.
        Budget = baseline with slight bias (optimistic on revenue, conservative on expenses).
        """
        rows = []
        for period in self._periods:
            year = period["year"]
            month = period["month"]
            period_key = period["period_key"]
            month_idx = month - 1

            for dept in LEAF_DEPARTMENTS:
                dept_code = dept.code

                # Revenue budget
                base_rev = BASE_MONTHLY_REVENUE.get(dept_code, Decimal("0"))
                if base_rev > 0:
                    for y in range(PERIOD_START_YEAR + 1, year + 1):
                        growth_y = Decimal(str(1 + ANNUAL_REVENUE_GROWTH.get(y, 0)))
                        base_rev = (base_rev * growth_y).quantize(TWO_DP)

                    seasonal = Decimal(str(REVENUE_SEASONALITY[month_idx]))
                    amount = (base_rev * seasonal * Decimal(str(BUDGET_REVENUE_BIAS))).quantize(TWO_DP)

                    # Original Budget
                    rows.append({
                        "date": f"{year:04d}-{month:02d}-01",
                        "period": period_key,
                        "department": dept_code,
                        "account": "REV",
                        "scenario": "Original Budget",
                        "version": "v1-budget",
                        "currency": "EUR",
                        "amount": float(amount),
                    })

                    # Revised Budget (from July 2025, 3% lower than original)
                    if period_key >= "2025-07":
                        revised = (amount * Decimal("0.97")).quantize(TWO_DP)
                        rows.append({
                            "date": f"{year:04d}-{month:02d}-01",
                            "period": period_key,
                            "department": dept_code,
                            "account": "REV",
                            "scenario": "Revised Budget",
                            "version": "v2-budget",
                            "currency": "EUR",
                            "amount": float(revised),
                        })

                # Expense budgets
                dept_expenses = BASE_EXPENSES.get(dept_code, {})
                for acc in EXPENSE_ACCOUNTS:
                    base_exp = dept_expenses.get(acc.code, Decimal("0"))
                    if base_exp <= 0:
                        continue

                    for y in range(PERIOD_START_YEAR + 1, year + 1):
                        growth_y = Decimal(str(1 + ANNUAL_EXPENSE_GROWTH.get(y, 0)))
                        base_exp = (base_exp * growth_y).quantize(TWO_DP)

                    seasonal = Decimal(str(EXPENSE_SEASONALITY[month_idx]))
                    magnitude = (base_exp * seasonal * Decimal(str(BUDGET_EXPENSE_BIAS))).quantize(TWO_DP)
                    amount = -magnitude

                    rows.append({
                        "date": f"{year:04d}-{month:02d}-01",
                        "period": period_key,
                        "department": dept_code,
                        "account": acc.code,
                        "scenario": "Original Budget",
                        "version": "v1-budget",
                        "currency": "EUR",
                        "amount": float(amount),
                    })

                    if period_key >= "2025-07":
                        revised_mag = (magnitude * Decimal("1.02")).quantize(TWO_DP)
                        rows.append({
                            "date": f"{year:04d}-{month:02d}-01",
                            "period": period_key,
                            "department": dept_code,
                            "account": acc.code,
                            "scenario": "Revised Budget",
                            "version": "v2-budget",
                            "currency": "EUR",
                            "amount": float(-revised_mag),
                        })

        return pd.DataFrame(rows)

    def generate_forecasts(self) -> pd.DataFrame:
        """
        Generate forecast data for Forecast v1, Optimistic, and Conservative scenarios.
        Uses assumption-driven growth from the latest actuals baseline.
        """
        rows = []
        # Use last actual period as base (simplification: use 2025-12 values from budget baseline)

        for scenario_name, assumptions in FORECAST_ASSUMPTIONS.items():
            version_name = {
                "Forecast v1": "v1-forecast",
                "Optimistic Scenario": "v1-optimistic",
                "Conservative Scenario": "v1-conservative",
            }[scenario_name]

            for period in self._periods:
                year = period["year"]
                month = period["month"]
                period_key = period["period_key"]
                month_idx = month - 1

                for dept in LEAF_DEPARTMENTS:
                    dept_code = dept.code

                    # Revenue forecast
                    base_rev = BASE_MONTHLY_REVENUE.get(dept_code, Decimal("0"))
                    if base_rev > 0:
                        for y in range(PERIOD_START_YEAR + 1, year + 1):
                            base_growth = ANNUAL_REVENUE_GROWTH.get(y, 0)
                            forecast_adj = assumptions.get("revenue_growth_rate", 0)
                            combined = Decimal(str(1 + base_growth * 0.5 + forecast_adj * 0.5))
                            base_rev = (base_rev * combined).quantize(TWO_DP)

                        seasonal = Decimal(str(REVENUE_SEASONALITY[month_idx]))
                        amount = (base_rev * seasonal).quantize(TWO_DP)

                        rows.append({
                            "date": f"{year:04d}-{month:02d}-01",
                            "period": period_key,
                            "department": dept_code,
                            "account": "REV",
                            "scenario": scenario_name,
                            "version": version_name,
                            "currency": "EUR",
                            "amount": float(amount),
                        })

                    # Expense forecasts
                    dept_expenses = BASE_EXPENSES.get(dept_code, {})
                    # Map account codes to assumption keys
                    account_to_assumption = {
                        "SAL": "salary_growth_rate",
                        "CLOUD": "cloud_cost_growth_rate",
                        "SW": "software_cost_growth",
                        "MKT_EXP": "marketing_budget_adjustment",
                        "RENT": "rent_escalation_rate",
                        "TRAVEL": "travel_adjustment",
                        "PROF": "professional_services_adjustment",
                        "DEPR": "depreciation_rate",
                        "TRAIN": "other_expense_growth",
                        "INSUR": "other_expense_growth",
                        "OTHER": "other_expense_growth",
                    }

                    for acc in EXPENSE_ACCOUNTS:
                        base_exp = dept_expenses.get(acc.code, Decimal("0"))
                        if base_exp <= 0:
                            continue

                        assumption_key = account_to_assumption.get(acc.code, "other_expense_growth")
                        growth_rate = assumptions.get(assumption_key, 0)

                        for y in range(PERIOD_START_YEAR + 1, year + 1):
                            base_growth = ANNUAL_EXPENSE_GROWTH.get(y, 0)
                            combined = Decimal(str(1 + base_growth * 0.5 + growth_rate * 0.5))
                            base_exp = (base_exp * combined).quantize(TWO_DP)

                        seasonal = Decimal(str(EXPENSE_SEASONALITY[month_idx]))
                        magnitude = (base_exp * seasonal).quantize(TWO_DP)
                        amount = -magnitude

                        rows.append({
                            "date": f"{year:04d}-{month:02d}-01",
                            "period": period_key,
                            "department": dept_code,
                            "account": acc.code,
                            "scenario": scenario_name,
                            "version": version_name,
                            "currency": "EUR",
                            "amount": float(amount),
                        })

        return pd.DataFrame(rows)

    def generate_scenario_assumptions(self) -> pd.DataFrame:
        """Generate scenario_assumptions.csv from the forecast assumption definitions."""
        rows = []
        for scenario_name, assumptions in FORECAST_ASSUMPTIONS.items():
            for key, value in assumptions.items():
                rows.append({
                    "scenario": scenario_name,
                    "assumption_key": key,
                    "assumption_value": value,
                    "department": "",
                    "account": "",
                    "description": f"{key.replace('_', ' ').title()} for {scenario_name}",
                })
        return pd.DataFrame(rows)

    def generate_invalid_test_data(self) -> pd.DataFrame:
        """
        Generate invalid_test_data.csv with deliberate data quality issues.
        Each row has a specific issue for testing the validation engine.
        """
        rows = [
            # Duplicate records
            {"date": "2024-01-01", "period": "2024-01", "department": "ENG", "account": "REV",
             "scenario": "Actuals", "version": "v1", "currency": "EUR", "amount": "320000",
             "_error_type": "duplicate"},
            {"date": "2024-01-01", "period": "2024-01", "department": "ENG", "account": "REV",
             "scenario": "Actuals", "version": "v1", "currency": "EUR", "amount": "320000",
             "_error_type": "duplicate"},
            # Missing account code
            {"date": "2024-02-01", "period": "2024-02", "department": "SALES", "account": "",
             "scenario": "Actuals", "version": "v1", "currency": "EUR", "amount": "450000",
             "_error_type": "missing_account"},
            # Invalid department
            {"date": "2024-03-01", "period": "2024-03", "department": "INVALID_DEPT", "account": "REV",
             "scenario": "Actuals", "version": "v1", "currency": "EUR", "amount": "100000",
             "_error_type": "invalid_department"},
            # Invalid date
            {"date": "not-a-date", "period": "2024-04", "department": "ENG", "account": "SAL",
             "scenario": "Actuals", "version": "v1", "currency": "EUR", "amount": "-180000",
             "_error_type": "invalid_date"},
            # Missing amount
            {"date": "2024-05-01", "period": "2024-05", "department": "MKT", "account": "MKT_EXP",
             "scenario": "Actuals", "version": "v1", "currency": "EUR", "amount": "",
             "_error_type": "missing_amount"},
            # Malformed number
            {"date": "2024-06-01", "period": "2024-06", "department": "OPS", "account": "RENT",
             "scenario": "Actuals", "version": "v1", "currency": "EUR", "amount": "abc123",
             "_error_type": "malformed_amount"},
            # Unsupported currency
            {"date": "2024-07-01", "period": "2024-07", "department": "FIN", "account": "PROF",
             "scenario": "Actuals", "version": "v1", "currency": "XYZ", "amount": "-15000",
             "_error_type": "unsupported_currency"},
            # Missing required column scenario
            {"date": "2024-08-01", "period": "2024-08", "department": "ENG", "account": "CLOUD",
             "scenario": "", "version": "v1", "currency": "EUR", "amount": "-45000",
             "_error_type": "missing_scenario"},
            # Unknown account code
            {"date": "2024-09-01", "period": "2024-09", "department": "SALES", "account": "FAKE_ACC",
             "scenario": "Actuals", "version": "v1", "currency": "EUR", "amount": "500000",
             "_error_type": "unknown_account"},
            # Invalid period format
            {"date": "2024-10-01", "period": "Oct-2024", "department": "ENG", "account": "SW",
             "scenario": "Actuals", "version": "v1", "currency": "EUR", "amount": "-12000",
             "_error_type": "invalid_period_format"},
        ]
        return pd.DataFrame(rows)

    def generate_all(self, output_dir: str = "data/sample") -> dict[str, str]:
        """
        Generate all CSV files and write to the output directory.

        Returns a dict of filename -> filepath.
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        files = {}

        # Departments
        df = self.generate_departments_csv()
        path = output_path / "departments.csv"
        df.to_csv(path, index=False)
        files["departments.csv"] = str(path)
        logger.info("Generated %s (%d rows)", path, len(df))

        # Accounts
        df = self.generate_accounts_csv()
        path = output_path / "accounts.csv"
        df.to_csv(path, index=False)
        files["accounts.csv"] = str(path)
        logger.info("Generated %s (%d rows)", path, len(df))

        # Actuals
        df = self.generate_actuals()
        path = output_path / "actuals.csv"
        df.to_csv(path, index=False)
        files["actuals.csv"] = str(path)
        logger.info("Generated %s (%d rows)", path, len(df))

        # Budgets
        df = self.generate_budgets()
        path = output_path / "budgets.csv"
        df.to_csv(path, index=False)
        files["budgets.csv"] = str(path)
        logger.info("Generated %s (%d rows)", path, len(df))

        # Forecasts
        df = self.generate_forecasts()
        path = output_path / "forecasts.csv"
        df.to_csv(path, index=False)
        files["forecasts.csv"] = str(path)
        logger.info("Generated %s (%d rows)", path, len(df))

        # Scenario Assumptions
        df = self.generate_scenario_assumptions()
        path = output_path / "scenario_assumptions.csv"
        df.to_csv(path, index=False)
        files["scenario_assumptions.csv"] = str(path)
        logger.info("Generated %s (%d rows)", path, len(df))

        # Invalid test data
        df = self.generate_invalid_test_data()
        path = output_path / "invalid_test_data.csv"
        df.to_csv(path, index=False)
        files["invalid_test_data.csv"] = str(path)
        logger.info("Generated %s (%d rows)", path, len(df))

        logger.info("All files generated in %s", output_dir)
        return files
