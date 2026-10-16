"""
Database seeding module for Northstar Digital Services GmbH.
Loads initial dimensions, scenarios, versions, and sample financial data.
"""
from __future__ import annotations

import csv
import logging
from decimal import Decimal
from pathlib import Path
from typing import Optional

import pandas as pd
from sqlalchemy.orm import Session

from database import connection
from database import repository as repo
from data_generator.dimensions import (
    ACCOUNTS,
    DEPARTMENTS,
    PERIOD_END_YEAR,
    PERIOD_MONTHS,
    PERIOD_START_YEAR,
    SCENARIOS,
    VERSIONS,
)
from models.config import get_settings
from models.import_models import DuplicatePolicy

logger = logging.getLogger(__name__)


def seed_dimensions(session: Session) -> dict[str, int]:
    """Seed all dimensions and reference data."""
    counts = {"departments": 0, "accounts": 0, "periods": 0, "scenarios": 0, "versions": 0}

    # 1. Departments
    for dept in DEPARTMENTS:
        repo.upsert_department(session, dept.code, dept.name, dept.parent_code)
        counts["departments"] += 1

    # 2. Accounts
    for acc in ACCOUNTS:
        repo.upsert_account(
            session,
            code=acc.code,
            name=acc.name,
            category=acc.category,
            sign_convention=acc.sign_convention,
            parent_code=acc.parent_code,
        )
        counts["accounts"] += 1

    # 3. Periods
    for year in range(PERIOD_START_YEAR, PERIOD_END_YEAR + 1):
        for month in PERIOD_MONTHS:
            repo.upsert_period(session, year, month)
            counts["periods"] += 1

    # 4. Scenarios
    for scn in SCENARIOS:
        repo.upsert_scenario(session, scn.name, scn.description)
        counts["scenarios"] += 1

    # 5. Versions
    for ver in VERSIONS:
        scn_record = repo.get_scenario_by_name(session, ver.scenario_name)
        scn_id = scn_record.id if scn_record else None
        repo.upsert_version(session, ver.name, scenario_id=scn_id, description=ver.description)
        counts["versions"] += 1

    session.flush()
    logger.info("Dimensions seeded: %s", counts)
    return counts


def seed_sample_data(
    session: Session,
    sample_dir: Optional[str] = None,
    duplicate_policy: DuplicatePolicy = DuplicatePolicy.SKIP,
) -> dict[str, int]:
    """
    Seed financial facts and forecast assumptions from CSV files in sample_dir.
    """
    from etl.loader import load_financial_facts
    from etl.transformer import transform_dataframe

    settings = get_settings()
    data_dir = Path(sample_dir or settings.sample_data_dir)

    if not data_dir.exists():
        logger.warning("Sample data directory %s does not exist.", data_dir)
        return {"facts": 0, "assumptions": 0}

    # Create an import batch for tracking the seed
    batch = repo.create_import_batch(session)
    batch.status = "processing"
    session.flush()

    total_facts = 0

    fact_files = [
        ("actuals.csv", "Actuals"),
        ("budgets.csv", "Original Budget"),
        ("forecasts.csv", "Forecast v1"),
    ]

    for filename, default_scenario in fact_files:
        file_path = data_dir / filename
        if not file_path.exists():
            continue

        try:
            df = pd.read_csv(file_path, dtype=str)
            if "scenario" not in df.columns:
                df["scenario"] = default_scenario

            transformed = transform_dataframe(df)
            load_res = load_financial_facts(
                session=session,
                df=transformed,
                batch_id=batch.id,
                duplicate_policy=duplicate_policy,
            )
            total_facts += load_res.inserted
            repo.create_import_file(
                session=session,
                batch_id=batch.id,
                filename=filename,
                file_type="csv",
                file_size_bytes=file_path.stat().st_size,
                row_count=len(df),
            )
        except Exception as e:
            logger.error("Error loading %s: %s", filename, e)

    # Seed scenario assumptions if available
    assumptions_file = data_dir / "scenario_assumptions.csv"
    assumptions_count = 0
    if assumptions_file.exists():
        try:
            assumptions_df = pd.read_csv(assumptions_file)
            for _, row in assumptions_df.iterrows():
                scn_name = str(row.get("scenario_name", "Forecast v1")).strip()
                scn = repo.get_scenario_by_name(session, scn_name)
                if not scn:
                    continue

                ver_name = str(row.get("version_name", "v1")).strip()
                ver = repo.get_version_by_name(session, ver_name)
                if not ver:
                    # fallback to first version
                    ver = repo.get_all_versions(session)[0] if repo.get_all_versions(session) else None
                ver_id = ver.id if ver else 1

                dept_id = None
                if pd.notna(row.get("department")) and str(row.get("department")).strip():
                    d = repo.get_department_by_code(session, str(row.get("department")).strip())
                    if d:
                        dept_id = d.id

                acct_id = None
                if pd.notna(row.get("account")) and str(row.get("account")).strip():
                    a = repo.get_account_by_code(session, str(row.get("account")).strip())
                    if a:
                        acct_id = a.id

                val = Decimal(str(row.get("assumption_value", "0.0000")))
                repo.upsert_forecast_assumption(
                    session=session,
                    scenario_id=scn.id,
                    version_id=ver_id,
                    assumption_key=str(row.get("assumption_key", "")).strip(),
                    assumption_value=val,
                    department_id=dept_id,
                    account_id=acct_id,
                    description=str(row.get("description", "")) if pd.notna(row.get("description")) else None,
                )
                assumptions_count += 1
        except Exception as e:
            logger.error("Error loading scenario assumptions: %s", e)

    repo.update_import_batch(
        session=session,
        batch_id=batch.id,
        status="completed",
        total_rows=total_facts,
        accepted_rows=total_facts,
        rejected_rows=0,
        duplicate_rows=0,
        processing_duration_ms=100,
    )

    repo.log_audit_event(
        session=session,
        event_type="DATABASE_SEEDED",
        event_description=f"Seeded database with {total_facts} facts and {assumptions_count} assumptions",
        entity_type="SYSTEM",
        entity_id="SEED",
    )

    return {"facts": total_facts, "assumptions": assumptions_count}


def seed_database(database_url: Optional[str] = None, sample_dir: Optional[str] = None) -> dict:
    """Full database seeding: init tables + seed dimensions + seed sample data."""
    connection.init_database(database_url)
    with connection.get_session() as session:
        dim_counts = seed_dimensions(session)
        data_counts = seed_sample_data(session, sample_dir)
        return {**dim_counts, **data_counts}
