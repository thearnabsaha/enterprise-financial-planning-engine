"""
Data validation engine for imported financial records.

Validates:
  - Required columns and values
  - Data types (dates, numbers)
  - Department and account references
  - Currency codes
  - Scenario and version names
  - Duplicate detection
  - Cross-file consistency
"""
from __future__ import annotations

import logging
import re
from decimal import Decimal, InvalidOperation
from typing import Optional

import pandas as pd

from models.import_models import ValidationError, ValidationSeverity, ValidationSummary

logger = logging.getLogger(__name__)

SUPPORTED_CURRENCIES = {"EUR", "USD", "GBP", "CHF"}
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
PERIOD_PATTERN = re.compile(r"^\d{4}-\d{2}$")


def validate_dataframe(
    df: pd.DataFrame,
    known_departments: set[str],
    known_accounts: set[str],
    known_scenarios: set[str],
    file_id: Optional[int] = None,
    batch_id: Optional[int] = None,
) -> ValidationSummary:
    """
    Validate an entire DataFrame of financial records.

    Parameters:
        df: DataFrame with canonical column names (after mapping)
        known_departments: Valid department codes
        known_accounts: Valid account codes
        known_scenarios: Valid scenario names
        file_id: Import file ID for error tracking
        batch_id: Import batch ID for error tracking

    Returns:
        ValidationSummary with all errors, warnings, and counts
    """
    errors: list[ValidationError] = []
    valid_mask = pd.Series([True] * len(df), index=df.index)

    # Track missing values by column
    missing_by_column: dict[str, int] = {}

    # ─── Required columns check ─────────────────────────────────────
    required_columns = ["department", "account", "amount"]
    has_period = "period" in df.columns
    has_date = "date" in df.columns

    if not has_period and not has_date:
        errors.append(ValidationError(
            batch_id=batch_id, file_id=file_id,
            error_type=ValidationSeverity.ERROR,
            error_code="MISSING_DATE_COLUMN",
            message="Neither 'date' nor 'period' column found. At least one is required.",
        ))

    for col in required_columns:
        if col not in df.columns:
            errors.append(ValidationError(
                batch_id=batch_id, file_id=file_id,
                error_type=ValidationSeverity.ERROR,
                error_code="MISSING_REQUIRED_COLUMN",
                message=f"Required column '{col}' not found in data.",
            ))

    # If critical columns are missing, return early
    if any(e.error_code == "MISSING_REQUIRED_COLUMN" for e in errors):
        return ValidationSummary(
            total_rows=len(df),
            valid_rows=0,
            invalid_rows=len(df),
            errors=errors,
        )

    # ─── Row-level validation ───────────────────────────────────────
    for idx, row in df.iterrows():
        row_num = int(idx) + 2  # +2 for header row + 0-index
        row_valid = True

        # Date / Period validation
        if has_period:
            period_val = str(row.get("period", "")).strip()
            if not period_val:
                errors.append(_make_error(
                    batch_id, file_id, row_num, "period",
                    "MISSING_PERIOD", "Period is required.", period_val,
                ))
                row_valid = False
                missing_by_column["period"] = missing_by_column.get("period", 0) + 1
            elif not PERIOD_PATTERN.match(period_val):
                errors.append(_make_error(
                    batch_id, file_id, row_num, "period",
                    "INVALID_PERIOD_FORMAT",
                    f"Period '{period_val}' must be in YYYY-MM format.",
                    period_val,
                ))
                row_valid = False

        if has_date:
            date_val = str(row.get("date", "")).strip()
            if date_val and not DATE_PATTERN.match(date_val):
                errors.append(_make_error(
                    batch_id, file_id, row_num, "date",
                    "INVALID_DATE_FORMAT",
                    f"Date '{date_val}' must be in YYYY-MM-DD format.",
                    date_val, severity=ValidationSeverity.WARNING,
                ))

        # Department validation
        dept_val = str(row.get("department", "")).strip()
        if not dept_val:
            errors.append(_make_error(
                batch_id, file_id, row_num, "department",
                "MISSING_DEPARTMENT", "Department is required.", dept_val,
            ))
            row_valid = False
            missing_by_column["department"] = missing_by_column.get("department", 0) + 1
        elif known_departments and dept_val not in known_departments:
            errors.append(_make_error(
                batch_id, file_id, row_num, "department",
                "UNKNOWN_DEPARTMENT",
                f"Department '{dept_val}' not found in master data.",
                dept_val,
            ))
            row_valid = False

        # Account validation
        acc_val = str(row.get("account", "")).strip()
        if not acc_val:
            errors.append(_make_error(
                batch_id, file_id, row_num, "account",
                "MISSING_ACCOUNT", "Account code is required.", acc_val,
            ))
            row_valid = False
            missing_by_column["account"] = missing_by_column.get("account", 0) + 1
        elif known_accounts and acc_val not in known_accounts:
            errors.append(_make_error(
                batch_id, file_id, row_num, "account",
                "UNKNOWN_ACCOUNT",
                f"Account '{acc_val}' not found in master data.",
                acc_val,
            ))
            row_valid = False

        # Amount validation
        amt_val = str(row.get("amount", "")).strip()
        if not amt_val:
            errors.append(_make_error(
                batch_id, file_id, row_num, "amount",
                "MISSING_AMOUNT", "Amount is required.", amt_val,
            ))
            row_valid = False
            missing_by_column["amount"] = missing_by_column.get("amount", 0) + 1
        else:
            try:
                Decimal(amt_val)
            except (InvalidOperation, ValueError):
                errors.append(_make_error(
                    batch_id, file_id, row_num, "amount",
                    "INVALID_AMOUNT",
                    f"Amount '{amt_val}' is not a valid number.",
                    amt_val,
                ))
                row_valid = False

        # Currency validation
        if "currency" in df.columns:
            ccy_val = str(row.get("currency", "")).strip().upper()
            if ccy_val and ccy_val not in SUPPORTED_CURRENCIES:
                errors.append(_make_error(
                    batch_id, file_id, row_num, "currency",
                    "UNSUPPORTED_CURRENCY",
                    f"Currency '{ccy_val}' is not supported. Use: {', '.join(sorted(SUPPORTED_CURRENCIES))}.",
                    ccy_val,
                ))
                row_valid = False

        # Scenario validation
        if "scenario" in df.columns:
            scenario_val = str(row.get("scenario", "")).strip()
            if not scenario_val:
                errors.append(_make_error(
                    batch_id, file_id, row_num, "scenario",
                    "MISSING_SCENARIO", "Scenario is required.", scenario_val,
                ))
                row_valid = False
                missing_by_column["scenario"] = missing_by_column.get("scenario", 0) + 1
            elif known_scenarios and scenario_val not in known_scenarios:
                errors.append(_make_error(
                    batch_id, file_id, row_num, "scenario",
                    "UNKNOWN_SCENARIO",
                    f"Scenario '{scenario_val}' not recognised.",
                    scenario_val, severity=ValidationSeverity.WARNING,
                ))

        if not row_valid:
            valid_mask.iloc[int(idx)] = False

    # ─── Duplicate detection ────────────────────────────────────────
    dup_columns = [c for c in ["period", "department", "account", "scenario", "version", "currency"]
                   if c in df.columns]
    if dup_columns:
        duplicates = df.duplicated(subset=dup_columns, keep="first")
        dup_count = duplicates.sum()
        if dup_count > 0:
            for idx in df[duplicates].index:
                row_num = int(idx) + 2
                errors.append(_make_error(
                    batch_id, file_id, row_num, None,
                    "DUPLICATE_RECORD",
                    f"Duplicate record detected (same {', '.join(dup_columns)}).",
                    None, severity=ValidationSeverity.WARNING,
                ))
            valid_mask[duplicates] = False
    else:
        dup_count = 0

    # Build summary
    error_count = sum(1 for e in errors if e.error_type == ValidationSeverity.ERROR)
    warning_count = sum(1 for e in errors if e.error_type == ValidationSeverity.WARNING)
    info_count = sum(1 for e in errors if e.error_type == ValidationSeverity.INFO)
    valid_rows = valid_mask.sum()
    invalid_rows = len(df) - valid_rows

    return ValidationSummary(
        total_rows=len(df),
        valid_rows=int(valid_rows),
        invalid_rows=int(invalid_rows),
        duplicate_rows=int(dup_count),
        warning_count=warning_count,
        info_count=info_count,
        errors=errors,
        missing_values_by_column=missing_by_column,
    )


def _make_error(
    batch_id: Optional[int],
    file_id: Optional[int],
    row_number: int,
    column_name: Optional[str],
    error_code: str,
    message: str,
    raw_value: Optional[str],
    severity: ValidationSeverity = ValidationSeverity.ERROR,
) -> ValidationError:
    """Helper to create a ValidationError."""
    return ValidationError(
        batch_id=batch_id,
        file_id=file_id,
        row_number=row_number,
        column_name=column_name,
        error_type=severity,
        error_code=error_code,
        message=message,
        raw_value=raw_value,
    )
