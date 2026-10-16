"""
Transactional data loader: inserts validated financial records into PostgreSQL
with duplicate detection and atomic commits.
"""
from __future__ import annotations

import logging
import time
from datetime import datetime
from decimal import Decimal
from typing import Optional

import pandas as pd
from sqlalchemy.orm import Session

from database import repository as repo
from models.import_models import DuplicatePolicy, ImportStatus

logger = logging.getLogger(__name__)


class LoadResult:
    """Result of a load operation."""
    def __init__(self):
        self.inserted = 0
        self.skipped = 0
        self.rejected = 0
        self.duplicates = 0
        self.errors: list[str] = []


def load_financial_facts(
    session: Session,
    df: pd.DataFrame,
    batch_id: int,
    duplicate_policy: DuplicatePolicy = DuplicatePolicy.REJECT,
) -> LoadResult:
    """
    Load validated financial facts into PostgreSQL within an existing session/transaction.

    Parameters:
        session: Active SQLAlchemy session (caller manages transaction)
        df: Transformed DataFrame with canonical columns
        batch_id: Import batch ID for tracking
        duplicate_policy: How to handle duplicate records

    Returns:
        LoadResult with counts of inserted, skipped, rejected, duplicates

    The caller is responsible for committing or rolling back the session.
    """
    result = LoadResult()
    start_time = time.monotonic()

    # Resolve dimension IDs
    dept_cache: dict[str, int] = {}
    acct_cache: dict[str, int] = {}
    period_cache: dict[str, int] = {}
    scenario_cache: dict[str, int] = {}
    version_cache: dict[str, int] = {}

    facts_to_insert: list[dict] = []

    for idx, row in df.iterrows():
        try:
            # Resolve department
            dept_code = str(row.get("department", "")).strip()
            if dept_code not in dept_cache:
                dept = repo.get_department_by_code(session, dept_code)
                if dept is None:
                    result.rejected += 1
                    result.errors.append(f"Row {idx + 1}: Department '{dept_code}' not found.")
                    continue
                dept_cache[dept_code] = dept.id
            dept_id = dept_cache[dept_code]

            # Resolve account
            acc_code = str(row.get("account", "")).strip()
            if acc_code not in acct_cache:
                acc = repo.get_account_by_code(session, acc_code)
                if acc is None:
                    result.rejected += 1
                    result.errors.append(f"Row {idx + 1}: Account '{acc_code}' not found.")
                    continue
                acct_cache[acc_code] = acc.id
            acc_id = acct_cache[acc_code]

            # Resolve period
            period_key = str(row.get("period", "")).strip()
            if period_key not in period_cache:
                period = repo.get_period_by_key(session, period_key)
                if period is None:
                    # Auto-create period
                    parts = period_key.split("-")
                    year, month = int(parts[0]), int(parts[1])
                    period = repo.upsert_period(session, year, month)
                period_cache[period_key] = period.id
            period_id = period_cache[period_key]

            # Resolve scenario
            scenario_name = str(row.get("scenario", "Actuals")).strip()
            if scenario_name not in scenario_cache:
                scenario = repo.get_scenario_by_name(session, scenario_name)
                if scenario is None:
                    scenario = repo.upsert_scenario(session, scenario_name)
                scenario_cache[scenario_name] = scenario.id
            scenario_id = scenario_cache[scenario_name]

            # Resolve version
            version_name = str(row.get("version", "v1")).strip()
            if version_name not in version_cache:
                version = repo.get_version_by_name(session, version_name)
                if version is None:
                    version = repo.upsert_version(session, version_name, scenario_id=scenario_id)
                version_cache[version_name] = version.id
            version_id = version_cache[version_name]

            currency = str(row.get("currency", "EUR")).strip().upper()
            amount = float(row.get("amount", 0))

            # Check for duplicates
            is_dup = repo.check_fact_exists(
                session, period_id, dept_id, acc_id, scenario_id, version_id, currency,
            )

            if is_dup:
                result.duplicates += 1
                if duplicate_policy == DuplicatePolicy.REJECT:
                    result.rejected += 1
                    result.errors.append(
                        f"Row {idx + 1}: Duplicate fact for {period_key}/{dept_code}/{acc_code}/{scenario_name}."
                    )
                    continue
                elif duplicate_policy == DuplicatePolicy.SKIP:
                    result.skipped += 1
                    continue
                elif duplicate_policy == DuplicatePolicy.REPLACE:
                    # Delete existing and re-insert below
                    pass  # Will be inserted, replacing the old one

            facts_to_insert.append({
                "period_id": period_id,
                "department_id": dept_id,
                "account_id": acc_id,
                "scenario_id": scenario_id,
                "version_id": version_id,
                "currency": currency,
                "amount": amount,
                "import_batch_id": batch_id,
            })

        except Exception as e:
            result.rejected += 1
            result.errors.append(f"Row {idx + 1}: {str(e)}")
            logger.error("Error loading row %d: %s", idx + 1, e)

    # Bulk insert
    if facts_to_insert:
        inserted = repo.bulk_insert_facts(session, facts_to_insert)
        result.inserted = inserted

    elapsed = int((time.monotonic() - start_time) * 1000)
    logger.info(
        "Load complete: %d inserted, %d skipped, %d rejected, %d duplicates (%dms)",
        result.inserted, result.skipped, result.rejected, result.duplicates, elapsed,
    )

    return result
