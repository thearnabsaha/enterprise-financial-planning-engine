"""
Tests for financial forecasting methods: baseline extrapolation,
assumption compounding, and multi-scenario calculation.
"""
from __future__ import annotations

from decimal import Decimal
import pytest

from calculations.forecasting import (
    assumption_driven_forecast,
    baseline_forecast,
    calculate_forecast_operating_profit,
    scenario_forecast,
)


class TestForecastingMethods:
    """Test the three core forecasting calculation methods."""

    def test_baseline_linear_trend(self):
        """Baseline linear trend extrapolates steady increments."""
        history = [Decimal("100.00"), Decimal("110.00"), Decimal("120.00")]
        projected = baseline_forecast(history, periods_ahead=2)

        assert len(projected) == 2
        assert projected[0] == Decimal("130.00")
        assert projected[1] == Decimal("140.00")

    def test_baseline_forecast_insufficient_history(self):
        """Returns empty list if fewer than 2 data points provided."""
        assert baseline_forecast([Decimal("100.00")], 3) == []

    def test_assumption_driven_revenue(self):
        """Compounding revenue with positive growth rate."""
        base = Decimal("100000.00")
        rate = Decimal("0.05")  # +5%
        projected = assumption_driven_forecast(base, rate, periods=3, is_expense=False)

        assert len(projected) == 3
        assert projected[0] == Decimal("105000.00")
        assert projected[1] == Decimal("110250.00")
        assert projected[2] == Decimal("115762.50")

    def test_assumption_driven_expenses(self):
        """Compounding negative expenses with growth rate preserves negative sign convention."""
        base = Decimal("-50000.00")
        rate = Decimal("0.10")  # +10% cost inflation
        projected = assumption_driven_forecast(base, rate, periods=2, is_expense=True)

        assert len(projected) == 2
        assert projected[0] == Decimal("-55000.00")
        assert projected[1] == Decimal("-60500.00")

    def test_scenario_forecast_multi_account(self):
        """Scenario forecast applies distinct growth rates per account."""
        bases = {"REV": Decimal("100000.00"), "SAL": Decimal("-50000.00")}
        assumptions = {"REV": Decimal("0.10"), "SAL": Decimal("0.05")}
        cats = {"REV": "revenue", "SAL": "expense"}

        res = scenario_forecast(bases, assumptions, cats, periods=1)
        assert res["REV"][0] == Decimal("110000.00")
        assert res["SAL"][0] == Decimal("-52500.00")

    def test_forecast_operating_profit(self):
        """Operating profit bridges forecasted revenue and expenses."""
        rev = [Decimal("105000.00"), Decimal("110000.00")]
        exp = [Decimal("-63000.00"), Decimal("-66000.00")]
        profits = calculate_forecast_operating_profit(rev, exp)

        assert profits == [Decimal("42000.00"), Decimal("44000.00")]
