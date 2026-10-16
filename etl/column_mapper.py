"""
Column mapper: auto-detects common financial column names and maps them
to the canonical schema. Supports manual override.
"""
from __future__ import annotations

import logging
from typing import Optional

from models.import_models import ColumnMapping

logger = logging.getLogger(__name__)

# Canonical target fields in the financial fact schema
CANONICAL_FIELDS = {
    "date": "Reporting date (YYYY-MM-DD)",
    "period": "Period key (YYYY-MM)",
    "department": "Department code",
    "account": "Account code",
    "scenario": "Scenario name",
    "version": "Version name",
    "currency": "Currency code (ISO 4217)",
    "amount": "Financial amount",
}

# Known aliases for automatic mapping
COLUMN_ALIASES: dict[str, list[str]] = {
    "date": ["date", "transaction_date", "posting_date", "report_date", "entry_date"],
    "period": ["period", "month", "period_key", "fiscal_period", "reporting_period"],
    "department": [
        "department", "dept", "department_code", "dept_code",
        "team", "cost_centre", "cost_center", "business_unit",
    ],
    "account": [
        "account", "account_code", "acct", "gl_account",
        "account_number", "chart_of_accounts",
    ],
    "scenario": ["scenario", "version_type", "data_type", "plan_type", "scenario_name"],
    "version": ["version", "ver", "version_name", "revision"],
    "currency": ["currency", "ccy", "currency_code", "curr"],
    "amount": ["amount", "value", "balance", "total", "net_amount", "gross_amount"],
}


def auto_map_columns(source_columns: list[str]) -> list[ColumnMapping]:
    """
    Automatically map source column names to canonical fields.

    Uses case-insensitive matching against known aliases.
    Returns a list of ColumnMapping objects with confidence scores.
    Unmapped columns are not included.
    """
    mappings = []
    mapped_targets = set()

    for source_col in source_columns:
        normalised = source_col.strip().lower().replace(" ", "_").replace("-", "_")

        for target, aliases in COLUMN_ALIASES.items():
            if target in mapped_targets:
                continue

            if normalised in aliases:
                confidence = 1.0 if normalised == target else 0.9
                mappings.append(ColumnMapping(
                    source_column=source_col,
                    target_field=target,
                    confidence=confidence,
                    is_auto_mapped=True,
                ))
                mapped_targets.add(target)
                break
        else:
            # Try partial matching for lower confidence
            for target, aliases in COLUMN_ALIASES.items():
                if target in mapped_targets:
                    continue
                for alias in aliases:
                    if alias in normalised or normalised in alias:
                        mappings.append(ColumnMapping(
                            source_column=source_col,
                            target_field=target,
                            confidence=0.6,
                            is_auto_mapped=True,
                        ))
                        mapped_targets.add(target)
                        break
                else:
                    continue
                break

    return mappings


def apply_column_mapping(
    df_columns: list[str],
    mappings: list[ColumnMapping],
) -> dict[str, str]:
    """
    Build a rename dict from column mappings.
    Returns: {source_column_name: target_field_name}
    """
    rename_map = {}
    for mapping in mappings:
        if mapping.source_column in df_columns:
            rename_map[mapping.source_column] = mapping.target_field
    return rename_map


def get_unmapped_required_fields(mappings: list[ColumnMapping]) -> list[str]:
    """
    Check which required canonical fields are missing from the mappings.
    Required fields: date or period, department, account, amount.
    """
    mapped_targets = {m.target_field for m in mappings}
    required = {"department", "account", "amount"}

    # Need at least one of date or period
    has_date_or_period = "date" in mapped_targets or "period" in mapped_targets

    missing = []
    if not has_date_or_period:
        missing.append("date or period")

    for field in required:
        if field not in mapped_targets:
            missing.append(field)

    return missing


def get_ambiguous_mappings(mappings: list[ColumnMapping]) -> list[ColumnMapping]:
    """Return mappings with low confidence that need user review."""
    return [m for m in mappings if m.confidence < 0.8]
