"""
Forecasting calculation methods.

Three methods:
  1. Baseline:          Linear trend extrapolation from historical actuals
  2. Assumption-driven: Previous period × (1 + growth_rate)
  3. Scenario:          Combination of multiple assumption-driven rates per dept/account
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

ZERO = Decimal("0")
ONE = Decimal("1")
TWO_DP = Decimal("0.01")


def baseline_forecast(
    historical_values: list[Decimal],
    periods_ahead: int = 1,
) -> list[Decimal]:
    """
    Baseline forecast using simple linear trend.

    Fits a least-squares line to the historical values indexed 0..n-1,
    then extrapolates for the next `periods_ahead` periods.

    Returns an empty list if fewer than 2 historical values.

    >>> baseline_forecast([Decimal("100"), Decimal("110"), Decimal("120")], 2)
    [Decimal('130.00'), Decimal('140.00')]
    """
    n = len(historical_values)
    if n < 2:
        return []

    # Convert to float for regression, then back to Decimal
    values = [float(v) for v in historical_values]
    x_mean = (n - 1) / 2.0
    y_mean = sum(values) / n

    # Least-squares slope
    numerator = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
    denominator = sum((i - x_mean) ** 2 for i in range(n))

    if denominator == 0:
        # All x values identical — flat forecast
        slope = 0.0
    else:
        slope = numerator / denominator

    intercept = y_mean - slope * x_mean

    forecasts = []
    for j in range(periods_ahead):
        x_next = n + j
        predicted = intercept + slope * x_next
        forecasts.append(Decimal(str(predicted)).quantize(TWO_DP, rounding=ROUND_HALF_UP))

    return forecasts


def assumption_driven_forecast(
    base_amount: Decimal,
    growth_rate: Decimal,
    periods: int = 1,
    is_expense: bool = False,
) -> list[Decimal]:
    """
    Assumption-driven forecast: each period applies the growth rate to the previous.

    For expenses (negative amounts), the growth rate is applied to the magnitude,
    and the sign is preserved.

    Formula:
      Forecast[t] = Forecast[t-1] × (1 + growth_rate)

    For expenses:
      Forecast[t] = -( |Forecast[t-1]| × (1 + growth_rate) )

    >>> assumption_driven_forecast(Decimal("100000"), Decimal("0.05"), 3)
    [Decimal('105000.00'), Decimal('110250.00'), Decimal('115762.50')]
    """
    base = Decimal(str(base_amount))
    rate = Decimal(str(growth_rate))

    if is_expense:
        # Work with magnitude, preserve sign
        magnitude = abs(base)
        sign = Decimal("-1") if base < ZERO else ONE
        results = []
        current = magnitude
        for _ in range(periods):
            current = (current * (ONE + rate)).quantize(TWO_DP, rounding=ROUND_HALF_UP)
            results.append((sign * current).quantize(TWO_DP, rounding=ROUND_HALF_UP))
        return results
    else:
        results = []
        current = base
        for _ in range(periods):
            current = (current * (ONE + rate)).quantize(TWO_DP, rounding=ROUND_HALF_UP)
            results.append(current)
        return results


def scenario_forecast(
    base_amounts: dict[str, Decimal],
    assumptions: dict[str, Decimal],
    account_categories: dict[str, str],
    periods: int = 1,
) -> dict[str, list[Decimal]]:
    """
    Scenario-based forecast applying different growth rates to different accounts.

    Parameters:
      base_amounts:       account_code -> base amount (last known value)
      assumptions:        account_code or category -> growth rate
      account_categories: account_code -> 'revenue' or 'expense'
      periods:            number of periods to forecast

    Returns:
      account_code -> list of forecasted amounts

    >>> result = scenario_forecast(
    ...     {"REV": Decimal("100000"), "SAL": Decimal("-50000")},
    ...     {"REV": Decimal("0.10"), "SAL": Decimal("0.03")},
    ...     {"REV": "revenue", "SAL": "expense"},
    ...     periods=2,
    ... )
    >>> result["REV"]
    [Decimal('110000.00'), Decimal('121000.00')]
    """
    results = {}
    for account_code, base in base_amounts.items():
        # Look for account-specific rate first, then category-level rate
        rate = assumptions.get(account_code)
        if rate is None:
            cat = account_categories.get(account_code, "")
            rate = assumptions.get(cat, ZERO)

        is_expense = account_categories.get(account_code) == "expense"
        results[account_code] = assumption_driven_forecast(
            base_amount=base,
            growth_rate=rate,
            periods=periods,
            is_expense=is_expense,
        )
    return results


def calculate_forecast_operating_profit(
    forecast_revenue: list[Decimal],
    forecast_expenses: list[Decimal],
) -> list[Decimal]:
    """
    Calculate operating profit for each forecast period.

    >>> calculate_forecast_operating_profit(
    ...     [Decimal("105000"), Decimal("110000")],
    ...     [Decimal("-63000"), Decimal("-66000")],
    ... )
    [Decimal('42000.00'), Decimal('44000.00')]
    """
    results = []
    for rev, exp in zip(forecast_revenue, forecast_expenses):
        profit = (Decimal(str(rev)) + Decimal(str(exp))).quantize(TWO_DP, rounding=ROUND_HALF_UP)
        results.append(profit)
    return results
