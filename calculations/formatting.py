"""
Number, currency, percentage, and date formatting utilities.
Consistent formatting across dashboards, tables, and exports.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Optional


def format_currency(
    amount: Optional[Decimal],
    currency: str = "EUR",
    show_sign: bool = True,
    compact: bool = False,
    prefix: Optional[str] = None,
) -> str:
    """
    Format a monetary amount with currency symbol.

    >>> format_currency(Decimal("1234567.89"))
    '€1,234,567.89'
    >>> format_currency(Decimal("-50000"), compact=True)
    '-€50.0K'
    >>> format_currency(None)
    '—'
    """
    if amount is None:
        return "—"

    symbols = {"EUR": "€", "USD": "$", "GBP": "£", "CHF": "CHF "}
    symbol = prefix if prefix is not None else symbols.get(currency, f"{currency} ")

    value = Decimal(str(amount))

    if compact:
        return _compact_number(value, symbol)

    sign = ""
    if show_sign and value < 0:
        sign = "-"
        value = abs(value)
    elif show_sign and value > 0:
        sign = ""  # No explicit + for positive in currency

    formatted = f"{value:,.2f}"
    return f"{sign}{symbol}{formatted}"


def format_percentage(
    value: Optional[Decimal],
    show_sign: bool = True,
) -> str:
    """
    Format a percentage value.

    >>> format_percentage(Decimal("10.50"))
    '+10.50%'
    >>> format_percentage(Decimal("-3.20"))
    '-3.20%'
    >>> format_percentage(None)
    '—'
    """
    if value is None:
        return "—"

    v = Decimal(str(value))
    sign = "+" if show_sign and v > 0 else ""
    return f"{sign}{v:.2f}%"


# Alias for convenience
format_percent = format_percentage


def format_number(
    value: Optional[Decimal],
    decimals: int = 2,
    show_sign: bool = False,
) -> str:
    """
    Format a number with thousand separators.

    >>> format_number(Decimal("1234567.89"))
    '1,234,567.89'
    """
    if value is None:
        return "—"

    v = Decimal(str(value))
    sign = "+" if show_sign and v > 0 else ""
    formatted = f"{v:,.{decimals}f}"
    return f"{sign}{formatted}"


def format_variance_badge(
    favourability: str,
    variance_pct: Optional[Decimal] = None,
) -> str:
    """
    Create a text badge for variance favourability.

    >>> format_variance_badge("favourable", Decimal("10.00"))
    '▲ +10.00% Favourable'
    >>> format_variance_badge("unfavourable", Decimal("-5.00"))
    '▼ -5.00% Unfavourable'
    """
    if favourability == "favourable":
        arrow = "▲"
        label = "Favourable"
    elif favourability == "unfavourable":
        arrow = "▼"
        label = "Unfavourable"
    else:
        arrow = "●"
        label = "On Target"

    if variance_pct is not None:
        pct_str = format_percentage(variance_pct)
        return f"{arrow} {pct_str} {label}"
    return f"{arrow} {label}"


def format_period(period_key: str) -> str:
    """
    Format a period key for display.

    >>> format_period("2024-01")
    'Jan 2024'
    """
    import calendar
    try:
        parts = period_key.split("-")
        year = int(parts[0])
        month = int(parts[1])
        return f"{calendar.month_abbr[month]} {year}"
    except (IndexError, ValueError):
        return period_key


def _compact_number(value: Decimal, prefix: str = "") -> str:
    """Format large numbers in compact notation (K, M, B)."""
    abs_val = abs(value)
    sign = "-" if value < 0 else ""

    if abs_val >= 1_000_000_000:
        compact = abs_val / 1_000_000_000
        return f"{sign}{prefix}{compact:.1f}B"
    elif abs_val >= 1_000_000:
        compact = abs_val / 1_000_000
        return f"{sign}{prefix}{compact:.1f}M"
    elif abs_val >= 1_000:
        compact = abs_val / 1_000
        return f"{sign}{prefix}{compact:.1f}K"
    else:
        return f"{sign}{prefix}{abs_val:.2f}"
