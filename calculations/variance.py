"""
Financial variance calculations with proper sign convention and favourability.

Sign convention:
  Revenue:             positive (+)
  Operating Expenses:  negative (-)
  Operating Profit:    Revenue + Expenses
  Signed Variance:     Actual - Budget
  Variance %:          (Actual - Budget) / |Budget| × 100

Favourability:
  Revenue:   positive variance = FAVOURABLE
  Expense:   variance closer to zero = FAVOURABLE (less negative actual = underspend)
             variance more negative = UNFAVOURABLE (more negative actual = overspend)
  Profit:    positive variance = FAVOURABLE
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import Optional

from models.financial import AccountCategory, Favourability, VarianceResult


ZERO = Decimal("0")
HUNDRED = Decimal("100")
TWO_DP = Decimal("0.01")
FOUR_DP = Decimal("0.0001")


def signed_variance(actual: Decimal, budget: Decimal) -> Decimal:
    """
    Calculate signed variance: Actual - Budget.

    >>> signed_variance(Decimal("110000"), Decimal("100000"))
    Decimal('10000')
    >>> signed_variance(Decimal("-55000"), Decimal("-50000"))
    Decimal('-5000')
    """
    return (Decimal(str(actual)) - Decimal(str(budget))).quantize(TWO_DP, rounding=ROUND_HALF_UP)


def variance_percentage(
    actual: Decimal, budget: Decimal
) -> Optional[Decimal]:
    """
    Calculate variance percentage: (Actual - Budget) / |Budget| × 100.
    Returns None if budget is zero (avoids division by zero).

    >>> variance_percentage(Decimal("110000"), Decimal("100000"))
    Decimal('10.00')
    """
    actual_d = Decimal(str(actual))
    budget_d = Decimal(str(budget))
    abs_budget = abs(budget_d)

    if abs_budget == ZERO:
        return None

    try:
        pct = ((actual_d - budget_d) / abs_budget * HUNDRED).quantize(TWO_DP, rounding=ROUND_HALF_UP)
        return pct
    except (InvalidOperation, ZeroDivisionError):
        return None


# Alias for convenience
variance_pct = variance_percentage


def classify_favourability(
    category: AccountCategory,
    variance: Decimal,
) -> Favourability:
    """
    Classify a variance as favourable, unfavourable, or neutral.

    Rules:
      Revenue: positive variance = favourable (earned more than planned)
      Expense: positive variance = favourable (spent less than planned, i.e., less negative actual)
               negative variance = unfavourable (spent more than planned)
      Profit:  treated like revenue — positive variance = favourable

    Note on expense sign convention:
      Budget = -50,000, Actual = -55,000 → Variance = -5,000 → UNFAVOURABLE
      Budget = -50,000, Actual = -45,000 → Variance = +5,000 → FAVOURABLE

    >>> classify_favourability(AccountCategory.REVENUE, Decimal("10000"))
    <Favourability.FAVOURABLE: 'favourable'>
    >>> classify_favourability(AccountCategory.EXPENSE, Decimal("-5000"))
    <Favourability.UNFAVOURABLE: 'unfavourable'>
    """
    variance_d = Decimal(str(variance))

    if variance_d == ZERO:
        return Favourability.NEUTRAL

    if category == AccountCategory.REVENUE:
        return Favourability.FAVOURABLE if variance_d > ZERO else Favourability.UNFAVOURABLE
    elif category == AccountCategory.EXPENSE:
        # For expenses (stored as negative):
        # Actual less negative than budget → positive variance → FAVOURABLE (underspend)
        # Actual more negative than budget → negative variance → UNFAVOURABLE (overspend)
        return Favourability.FAVOURABLE if variance_d > ZERO else Favourability.UNFAVOURABLE
    else:
        # Profit or other — same as revenue
        return Favourability.FAVOURABLE if variance_d > ZERO else Favourability.UNFAVOURABLE


def compute_variance(
    actual: Decimal,
    budget: Decimal,
    category: AccountCategory,
) -> VarianceResult:
    """
    Compute a complete variance result including signed variance,
    percentage, and favourability.

    >>> result = compute_variance(Decimal("110000"), Decimal("100000"), AccountCategory.REVENUE)
    >>> result.signed_variance
    Decimal('10000.00')
    >>> result.favourability
    <Favourability.FAVOURABLE: 'favourable'>
    """
    actual_d = Decimal(str(actual))
    budget_d = Decimal(str(budget))
    var = signed_variance(actual_d, budget_d)
    pct = variance_percentage(actual_d, budget_d)
    fav = classify_favourability(category, var)

    return VarianceResult(
        actual=actual_d.quantize(TWO_DP),
        budget=budget_d.quantize(TWO_DP),
        signed_variance=var,
        variance_percentage=pct,
        favourability=fav,
        account_category=category,
    )
