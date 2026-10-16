"""
Financial metrics: revenue, profit, margin, month-over-month, year-over-year.

All calculations use Decimal for monetary precision.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

ZERO = Decimal("0")
HUNDRED = Decimal("100")
TWO_DP = Decimal("0.01")


def operating_profit(revenue: Decimal, expenses: Decimal) -> Decimal:
    """
    Operating Profit = Revenue + Expenses.
    (Expenses are stored as negative values.)

    >>> operating_profit(Decimal("100000"), Decimal("-60000"))
    Decimal('40000.00')
    """
    return (Decimal(str(revenue)) + Decimal(str(expenses))).quantize(TWO_DP, rounding=ROUND_HALF_UP)


def operating_margin(revenue: Decimal, profit: Decimal) -> Optional[Decimal]:
    """
    Operating Margin = (Operating Profit / Revenue) × 100.
    Returns None if revenue is zero.

    >>> operating_margin(Decimal("100000"), Decimal("40000"))
    Decimal('40.00')
    """
    rev = Decimal(str(revenue))
    if rev == ZERO:
        return None
    return (Decimal(str(profit)) / rev * HUNDRED).quantize(TWO_DP, rounding=ROUND_HALF_UP)


def month_over_month_change(current: Decimal, previous: Decimal) -> Optional[Decimal]:
    """
    Month-over-month change as a percentage.
    Returns None if previous period is zero.

    >>> month_over_month_change(Decimal("110000"), Decimal("100000"))
    Decimal('10.00')
    """
    prev = Decimal(str(previous))
    if prev == ZERO:
        return None
    curr = Decimal(str(current))
    return ((curr - prev) / abs(prev) * HUNDRED).quantize(TWO_DP, rounding=ROUND_HALF_UP)


def year_over_year_change(current: Decimal, prior_year: Decimal) -> Optional[Decimal]:
    """
    Year-over-year change as a percentage.
    Returns None if prior year value is zero.

    >>> year_over_year_change(Decimal("120000"), Decimal("100000"))
    Decimal('20.00')
    """
    prior = Decimal(str(prior_year))
    if prior == ZERO:
        return None
    curr = Decimal(str(current))
    return ((curr - prior) / abs(prior) * HUNDRED).quantize(TWO_DP, rounding=ROUND_HALF_UP)


def expense_ratio(expenses: Decimal, revenue: Decimal) -> Optional[Decimal]:
    """
    Expense ratio = |Expenses| / Revenue × 100.
    Returns None if revenue is zero.

    >>> expense_ratio(Decimal("-60000"), Decimal("100000"))
    Decimal('60.00')
    """
    rev = Decimal(str(revenue))
    if rev == ZERO:
        return None
    exp = abs(Decimal(str(expenses)))
    return (exp / rev * HUNDRED).quantize(TWO_DP, rounding=ROUND_HALF_UP)


def safe_divide(numerator: Decimal, denominator: Decimal, scale: int = 2) -> Optional[Decimal]:
    """
    Safe division with configurable scale. Returns None on zero denominator.

    >>> safe_divide(Decimal("10"), Decimal("3"), 4)
    Decimal('3.3333')
    """
    denom = Decimal(str(denominator))
    if denom == ZERO:
        return None
    quantizer = Decimal(10) ** -scale
    return (Decimal(str(numerator)) / denom).quantize(quantizer, rounding=ROUND_HALF_UP)
