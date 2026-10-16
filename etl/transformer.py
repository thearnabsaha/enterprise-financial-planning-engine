"""
Data transformer: normalises types, dates, amounts, and dimension references
after validation passes.
"""
from __future__ import annotations

import logging
from decimal import Decimal, ROUND_HALF_UP

import pandas as pd

logger = logging.getLogger(__name__)

TWO_DP = Decimal("0.01")


def transform_dataframe(
    df: pd.DataFrame,
    column_mapping: Optional[dict[str, str]] = None,
    default_scenario: str = "Actuals",
    default_version: str = "v1",
    default_currency: str = "EUR",
) -> pd.DataFrame:
    """
    Transform a validated DataFrame into the canonical format.

    Steps:
      1. Rename columns using the mapping
      2. Normalise period from date if needed
      3. Clean and normalise text fields
      4. Convert amounts to Decimal-safe floats
      5. Fill defaults for optional columns

    Parameters:
        df: Raw DataFrame (after validation)
        column_mapping: {source_col: target_field} (optional)
        default_scenario: Default scenario if not in data
        default_version: Default version if not in data
        default_currency: Default currency if not in data

    Returns:
        Transformed DataFrame with canonical columns
    """
    # Step 1: Rename columns
    if column_mapping:
        result = df.rename(columns=column_mapping).copy()
    else:
        result = df.copy()

    # Step 2: Extract period from date if period not present
    if "period" not in result.columns and "date" in result.columns:
        result["period"] = result["date"].apply(_extract_period_from_date)

    # Step 3: Clean text fields
    text_columns = ["department", "account", "scenario", "version", "currency"]
    for col in text_columns:
        if col in result.columns:
            result[col] = result[col].astype(str).str.strip()

    # Step 4: Convert amounts
    if "amount" in result.columns:
        result["amount"] = result["amount"].apply(_safe_decimal_convert)

    # Step 5: Fill defaults
    if "scenario" not in result.columns:
        result["scenario"] = default_scenario
    else:
        result["scenario"] = result["scenario"].replace("", default_scenario)

    if "version" not in result.columns:
        result["version"] = default_version
    else:
        result["version"] = result["version"].replace("", default_version)

    if "currency" not in result.columns:
        result["currency"] = default_currency
    else:
        result["currency"] = result["currency"].replace("", default_currency)
        result["currency"] = result["currency"].str.upper()

    # Select canonical columns
    canonical = ["period", "department", "account", "scenario", "version", "currency", "amount"]
    available = [c for c in canonical if c in result.columns]
    result = result[available]

    # Drop rows with NaN amounts
    if "amount" in result.columns:
        result = result.dropna(subset=["amount"])

    return result.reset_index(drop=True)


def _extract_period_from_date(date_str: str) -> str:
    """Extract YYYY-MM period from a date string."""
    try:
        s = str(date_str).strip()
        if len(s) >= 7:
            return s[:7]
        return s
    except Exception:
        return str(date_str)


def _safe_decimal_convert(value) -> float | None:
    """Safely convert a value to float for DataFrame storage."""
    try:
        s = str(value).strip().replace(",", "")
        if not s:
            return None
        d = Decimal(s).quantize(TWO_DP, rounding=ROUND_HALF_UP)
        return float(d)
    except Exception:
        return None
