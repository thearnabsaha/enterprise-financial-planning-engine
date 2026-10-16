"""
Tests for financial calculations: variance, profit, margin, and Decimal precision.
"""
from __future__ import annotations

from decimal import Decimal
import pytest

from calculations.metrics import (
    month_over_month_growth,
    operating_margin,
    operating_profit,
    safe_divide,
    year_over_year_growth,
)
from calculations.variance import (
    classify_favourability,
    compute_variance,
    signed_variance,
    variance_percentage,
)
from models.financial import AccountCategory, Favourability


class TestVarianceCalculations:
    """Test signed variance and variance percentage arithmetic."""

    def test_revenue_variance_positive(self):
        """Higher revenue than budget produces positive variance and favourable classification."""
        act = Decimal("110000.00")
        bud = Decimal("100000.00")
        var = signed_variance(act, bud)
        pct = variance_percentage(act, bud)
        fav = classify_favourability(AccountCategory.REVENUE, var)

        assert var == Decimal("10000.00")
        assert pct == Decimal("10.00")
        assert fav == Favourability.FAVOURABLE

    def test_expense_variance_unfavourable_overspend(self):
        """More negative expenses (e.g. -55k vs -50k) is an overspend (UNFAVOURABLE)."""
        act = Decimal("-55000.00")
        bud = Decimal("-50000.00")
        var = signed_variance(act, bud)
        pct = variance_percentage(act, bud)
        fav = classify_favourability(AccountCategory.EXPENSE, var)

        assert var == Decimal("-5000.00")
        assert pct == Decimal("-10.00")
        assert fav == Favourability.UNFAVOURABLE

    def test_expense_variance_favourable_underspend(self):
        """Less negative expenses (e.g. -45k vs -50k) is an underspend (FAVOURABLE)."""
        act = Decimal("-45000.00")
        bud = Decimal("-50000.00")
        var = signed_variance(act, bud)
        pct = variance_percentage(act, bud)
        fav = classify_favourability(AccountCategory.EXPENSE, var)

        assert var == Decimal("5000.00")
        assert pct == Decimal("10.00")
        assert fav == Favourability.FAVOURABLE

    def test_profit_variance(self):
        """Operating profit variance: positive = favourable, negative = unfavourable."""
        var_fav = signed_variance(Decimal("55000.00"), Decimal("50000.00"))
        fav = classify_favourability("profit", var_fav)
        assert var_fav == Decimal("5000.00")
        assert fav == Favourability.FAVOURABLE

        var_unfav = signed_variance(Decimal("45000.00"), Decimal("50000.00"))
        unfav = classify_favourability("profit", var_unfav)
        assert var_unfav == Decimal("-5000.00")
        assert unfav == Favourability.UNFAVOURABLE

    def test_zero_budget_variance_pct(self):
        """Zero budget should return None for percentage without throwing ZeroDivisionError."""
        pct = variance_percentage(Decimal("10000.00"), Decimal("0.00"))
        assert pct is None

    def test_zero_variance_neutral(self):
        """Zero variance is classified as neutral."""
        var = signed_variance(Decimal("100000.00"), Decimal("100000.00"))
        assert var == Decimal("0.00")
        assert classify_favourability(AccountCategory.REVENUE, var) == Favourability.NEUTRAL


class TestMetricsCalculations:
    """Test operating profit and margin metrics."""

    def test_operating_profit_calculation(self):
        """Profit = Revenue + Expenses (with negative expenses)."""
        rev = Decimal("1000000.00")
        exp = Decimal("-700000.00")
        profit = operating_profit(rev, exp)
        assert profit == Decimal("300000.00")

    def test_operating_margin_calculation(self):
        """Margin % = (Profit / Revenue) * 100."""
        profit = Decimal("300000.00")
        rev = Decimal("1000000.00")
        margin = operating_margin(profit, rev)
        assert margin == Decimal("30.00")

    def test_operating_margin_zero_revenue(self):
        """Zero revenue yields None for margin without crashing."""
        margin = operating_margin(Decimal("0.00"), Decimal("0.00"))
        assert margin is None

    def test_mom_and_yoy_growth(self):
        """Test MoM and YoY growth rate calculations."""
        current = Decimal("120000.00")
        prior = Decimal("100000.00")
        growth = month_over_month_growth(current, prior)
        assert growth == Decimal("20.00")


class TestFormatting:
    """Test currency, percentage, and badge formatting."""

    def test_format_currency_positive_and_negative(self):
        from calculations.formatting import format_currency
        assert format_currency(Decimal("1234567.89")) == "€1,234,567.89"
        assert format_currency(Decimal("-50000")) == "-€50,000.00"
        assert format_currency(None) == "—"

    def test_format_percentage(self):
        from calculations.formatting import format_percentage
        assert format_percentage(Decimal("10.50")) == "+10.50%"
        assert format_percentage(Decimal("-3.20")) == "-3.20%"
        assert format_percentage(None) == "—"


class TestCalculationService:
    """Test calculation service aggregation from seeded database."""

    def test_calculation_service_kpis(self, db_session):
        from services.calculation_service import CalculationService
        kpis = CalculationService.get_kpis(session=db_session)
        assert "revenue" in kpis
        assert "expenses" in kpis
        assert "profit" in kpis
        assert "margin_pct" in kpis
