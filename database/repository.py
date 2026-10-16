"""
Data access repository — CRUD operations for all database entities.
Uses parameterised queries through SQLAlchemy ORM (no raw string concatenation).
"""
from __future__ import annotations

import logging
from decimal import Decimal
from typing import Optional

from sqlalchemy import func, and_, text
from sqlalchemy.orm import Session

from database.schema import (
    AccountTable,
    ApplicationSettingTable,
    AuditEventTable,
    DepartmentTable,
    FinancialFactTable,
    ForecastAssumptionTable,
    ImportBatchTable,
    ImportFileTable,
    PeriodTable,
    ScenarioTable,
    ValidationErrorTable,
    VersionTable,
)

logger = logging.getLogger(__name__)


# ─── Departments ─────────────────────────────────────────────────────────────


def get_all_departments(session: Session) -> list[DepartmentTable]:
    """Get all active departments."""
    return session.query(DepartmentTable).filter(DepartmentTable.is_active.is_(True)).order_by(DepartmentTable.name).all()


def get_department_by_code(session: Session, code: str) -> Optional[DepartmentTable]:
    """Get a department by its code."""
    return session.query(DepartmentTable).filter(DepartmentTable.code == code).first()


def upsert_department(session: Session, code: str, name: str, parent_code: Optional[str] = None) -> DepartmentTable:
    """Insert or update a department."""
    dept = get_department_by_code(session, code)
    if dept is None:
        dept = DepartmentTable(code=code, name=name, parent_code=parent_code)
        session.add(dept)
    else:
        dept.name = name
        dept.parent_code = parent_code
    session.flush()
    return dept


# ─── Accounts ────────────────────────────────────────────────────────────────


def get_all_accounts(session: Session) -> list[AccountTable]:
    """Get all active accounts."""
    return session.query(AccountTable).filter(AccountTable.is_active.is_(True)).order_by(AccountTable.name).all()


def get_account_by_code(session: Session, code: str) -> Optional[AccountTable]:
    """Get an account by its code."""
    return session.query(AccountTable).filter(AccountTable.code == code).first()


def upsert_account(
    session: Session,
    code: str,
    name: str,
    category: str,
    sign_convention: int,
    parent_code: Optional[str] = None,
) -> AccountTable:
    """Insert or update an account."""
    acc = get_account_by_code(session, code)
    if acc is None:
        acc = AccountTable(
            code=code, name=name, category=category,
            sign_convention=sign_convention, parent_code=parent_code,
        )
        session.add(acc)
    else:
        acc.name = name
        acc.category = category
        acc.sign_convention = sign_convention
        acc.parent_code = parent_code
    session.flush()
    return acc


# ─── Periods ─────────────────────────────────────────────────────────────────


def get_all_periods(session: Session) -> list[PeriodTable]:
    """Get all periods ordered chronologically."""
    return session.query(PeriodTable).order_by(PeriodTable.year, PeriodTable.month).all()


def get_period_by_key(session: Session, period_key: str) -> Optional[PeriodTable]:
    """Get a period by its key (e.g., '2024-01')."""
    return session.query(PeriodTable).filter(PeriodTable.period_key == period_key).first()


def upsert_period(session: Session, year: int, month: int) -> PeriodTable:
    """Insert or update a period."""
    import math
    period_key = f"{year:04d}-{month:02d}"
    quarter = math.ceil(month / 3)
    period = get_period_by_key(session, period_key)
    if period is None:
        period = PeriodTable(year=year, month=month, period_key=period_key, quarter=quarter)
        session.add(period)
    session.flush()
    return period


# ─── Scenarios ───────────────────────────────────────────────────────────────


def get_all_scenarios(session: Session) -> list[ScenarioTable]:
    """Get all scenarios."""
    return session.query(ScenarioTable).order_by(ScenarioTable.name).all()


def get_scenario_by_name(session: Session, name: str) -> Optional[ScenarioTable]:
    """Get a scenario by name."""
    return session.query(ScenarioTable).filter(ScenarioTable.name == name).first()


def upsert_scenario(session: Session, name: str, description: Optional[str] = None) -> ScenarioTable:
    """Insert or update a scenario."""
    scenario = get_scenario_by_name(session, name)
    if scenario is None:
        scenario = ScenarioTable(name=name, description=description)
        session.add(scenario)
    else:
        if description is not None:
            scenario.description = description
    session.flush()
    return scenario


# ─── Versions ────────────────────────────────────────────────────────────────


def get_all_versions(session: Session) -> list[VersionTable]:
    """Get all versions."""
    return session.query(VersionTable).order_by(VersionTable.name).all()


def get_version_by_name(session: Session, name: str) -> Optional[VersionTable]:
    """Get a version by name."""
    return session.query(VersionTable).filter(VersionTable.name == name).first()


def upsert_version(
    session: Session, name: str, scenario_id: Optional[int] = None, description: Optional[str] = None,
) -> VersionTable:
    """Insert or update a version."""
    version = get_version_by_name(session, name)
    if version is None:
        version = VersionTable(name=name, scenario_id=scenario_id, description=description)
        session.add(version)
    else:
        if scenario_id is not None:
            version.scenario_id = scenario_id
        if description is not None:
            version.description = description
    session.flush()
    return version


# ─── Financial Facts ─────────────────────────────────────────────────────────


def get_financial_facts(
    session: Session,
    period_ids: Optional[list[int]] = None,
    department_ids: Optional[list[int]] = None,
    account_ids: Optional[list[int]] = None,
    scenario_ids: Optional[list[int]] = None,
    version_ids: Optional[list[int]] = None,
    currency: Optional[str] = None,
    scenario_name: Optional[str] = None,
    start_period: Optional[str] = None,
    end_period: Optional[str] = None,
    account_id: Optional[int] = None,
) -> list[FinancialFactTable]:
    """Query financial facts with optional filters."""
    query = session.query(FinancialFactTable)

    if scenario_name:
        scn = get_scenario_by_name(session, scenario_name)
        if scn:
            query = query.filter(FinancialFactTable.scenario_id == scn.id)
        else:
            return []

    if account_id:
        query = query.filter(FinancialFactTable.account_id == account_id)

    if start_period or end_period:
        p_query = session.query(PeriodTable.id)
        if start_period:
            p_query = p_query.filter(PeriodTable.period_key >= start_period)
        if end_period:
            p_query = p_query.filter(PeriodTable.period_key <= end_period)
        p_ids = [r[0] for r in p_query.all()]
        query = query.filter(FinancialFactTable.period_id.in_(p_ids))
    elif period_ids:
        query = query.filter(FinancialFactTable.period_id.in_(period_ids))

    if department_ids:
        query = query.filter(FinancialFactTable.department_id.in_(department_ids))
    if account_ids:
        query = query.filter(FinancialFactTable.account_id.in_(account_ids))
    if scenario_ids:
        query = query.filter(FinancialFactTable.scenario_id.in_(scenario_ids))
    if version_ids:
        query = query.filter(FinancialFactTable.version_id.in_(version_ids))
    if currency:
        query = query.filter(FinancialFactTable.currency == currency)

    return query.all()


def check_fact_exists(
    session: Session,
    period_id: int,
    department_id: int,
    account_id: int,
    scenario_id: int,
    version_id: int,
    currency: str,
) -> bool:
    """Check if a financial fact already exists at the given grain."""
    return session.query(
        session.query(FinancialFactTable).filter(
            FinancialFactTable.period_id == period_id,
            FinancialFactTable.department_id == department_id,
            FinancialFactTable.account_id == account_id,
            FinancialFactTable.scenario_id == scenario_id,
            FinancialFactTable.version_id == version_id,
            FinancialFactTable.currency == currency,
        ).exists()
    ).scalar()


def insert_financial_fact(session: Session, **kwargs) -> FinancialFactTable:
    """Insert a single financial fact."""
    fact = FinancialFactTable(**kwargs)
    session.add(fact)
    session.flush()
    return fact


def bulk_insert_facts(session: Session, facts: list[dict]) -> int:
    """Bulk insert financial facts. Returns the count inserted."""
    if not facts:
        return 0
    session.bulk_insert_mappings(FinancialFactTable, facts)
    session.flush()
    return len(facts)


def delete_facts_by_batch(session: Session, batch_id: int) -> int:
    """Delete all financial facts for a given import batch."""
    count = session.query(FinancialFactTable).filter(
        FinancialFactTable.import_batch_id == batch_id
    ).delete()
    session.flush()
    return count


def get_aggregated_amounts(
    session: Session,
    scenario_id: int,
    version_id: int,
    period_ids: Optional[list[int]] = None,
    department_ids: Optional[list[int]] = None,
    group_by_account: bool = False,
    group_by_department: bool = False,
    group_by_period: bool = False,
):
    """Get aggregated financial amounts with flexible grouping."""
    columns = [func.sum(FinancialFactTable.amount).label("total_amount")]
    group_cols = []

    if group_by_account:
        columns.insert(0, FinancialFactTable.account_id)
        group_cols.append(FinancialFactTable.account_id)
    if group_by_department:
        columns.insert(0, FinancialFactTable.department_id)
        group_cols.append(FinancialFactTable.department_id)
    if group_by_period:
        columns.insert(0, FinancialFactTable.period_id)
        group_cols.append(FinancialFactTable.period_id)

    query = session.query(*columns).filter(
        FinancialFactTable.scenario_id == scenario_id,
        FinancialFactTable.version_id == version_id,
    )

    if period_ids:
        query = query.filter(FinancialFactTable.period_id.in_(period_ids))
    if department_ids:
        query = query.filter(FinancialFactTable.department_id.in_(department_ids))

    if group_cols:
        query = query.group_by(*group_cols)

    return query.all()


# ─── Import Batches ──────────────────────────────────────────────────────────


def create_import_batch(session: Session) -> ImportBatchTable:
    """Create a new import batch."""
    batch = ImportBatchTable()
    session.add(batch)
    session.flush()
    return batch


def get_import_batch(session: Session, batch_id: int) -> Optional[ImportBatchTable]:
    """Get an import batch by ID."""
    return session.query(ImportBatchTable).filter(ImportBatchTable.id == batch_id).first()


def get_all_import_batches(session: Session, limit: int = 50) -> list[ImportBatchTable]:
    """Get recent import batches."""
    return (
        session.query(ImportBatchTable)
        .order_by(ImportBatchTable.started_at.desc())
        .limit(limit)
        .all()
    )


def update_import_batch(session: Session, batch_id: int, **kwargs) -> None:
    """Update import batch fields."""
    session.query(ImportBatchTable).filter(ImportBatchTable.id == batch_id).update(kwargs)
    session.flush()


# ─── Import Files ────────────────────────────────────────────────────────────


def create_import_file(session: Session, **kwargs) -> ImportFileTable:
    """Record a file within an import batch."""
    file_record = ImportFileTable(**kwargs)
    session.add(file_record)
    session.flush()
    return file_record


# ─── Validation Errors ───────────────────────────────────────────────────────


def create_validation_error(session: Session, **kwargs) -> ValidationErrorTable:
    """Record a validation error."""
    error = ValidationErrorTable(**kwargs)
    session.add(error)
    session.flush()
    return error


def bulk_insert_validation_errors(session: Session, errors: list[dict]) -> int:
    """Bulk insert validation errors."""
    if not errors:
        return 0
    session.bulk_insert_mappings(ValidationErrorTable, errors)
    session.flush()
    return len(errors)


def get_validation_errors_for_batch(session: Session, batch_id: int) -> list[ValidationErrorTable]:
    """Get all validation errors for a batch."""
    return (
        session.query(ValidationErrorTable)
        .filter(ValidationErrorTable.batch_id == batch_id)
        .order_by(ValidationErrorTable.row_number)
        .all()
    )


# ─── Forecast Assumptions ───────────────────────────────────────────────────


def get_forecast_assumptions(
    session: Session, scenario_id: int, version_id: Optional[int] = None,
) -> list[ForecastAssumptionTable]:
    """Get all forecast assumptions for a scenario (and optional version)."""
    query = session.query(ForecastAssumptionTable).filter(
        ForecastAssumptionTable.scenario_id == scenario_id
    )
    if version_id is not None:
        query = query.filter(ForecastAssumptionTable.version_id == version_id)
    return query.all()


def upsert_forecast_assumption(session: Session, **kwargs) -> ForecastAssumptionTable:
    """Insert or update a forecast assumption."""
    existing = (
        session.query(ForecastAssumptionTable)
        .filter(
            ForecastAssumptionTable.scenario_id == kwargs.get("scenario_id"),
            ForecastAssumptionTable.version_id == kwargs.get("version_id"),
            ForecastAssumptionTable.assumption_key == kwargs.get("assumption_key"),
            ForecastAssumptionTable.department_id == kwargs.get("department_id"),
            ForecastAssumptionTable.account_id == kwargs.get("account_id"),
        )
        .first()
    )
    if existing is None:
        assumption = ForecastAssumptionTable(**kwargs)
        session.add(assumption)
        session.flush()
        return assumption
    else:
        for key, value in kwargs.items():
            if hasattr(existing, key):
                setattr(existing, key, value)
        session.flush()
        return existing


# ─── Audit Events ────────────────────────────────────────────────────────────


def create_audit_event(
    session: Session,
    event_type: str,
    event_description: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    metadata_json: Optional[str] = None,
) -> AuditEventTable:
    """Record an audit event."""
    event = AuditEventTable(
        event_type=event_type,
        event_description=event_description,
        entity_type=entity_type,
        entity_id=entity_id,
        metadata_json=metadata_json,
    )
    session.add(event)
    session.flush()
    return event


def log_audit_event(
    session: Session,
    event_type: str,
    event_description: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> AuditEventTable:
    """Convenience helper to record an audit event with dict metadata."""
    import json
    metadata_json = json.dumps(metadata) if metadata else None
    return create_audit_event(
        session=session,
        event_type=event_type,
        event_description=event_description,
        entity_type=entity_type,
        entity_id=entity_id,
        metadata_json=metadata_json,
    )


def get_recent_audit_events(session: Session, limit: int = 100) -> list[AuditEventTable]:
    """Get recent audit events."""
    return (
        session.query(AuditEventTable)
        .order_by(AuditEventTable.created_at.desc())
        .limit(limit)
        .all()
    )


# ─── Application Settings ───────────────────────────────────────────────────


def get_setting(session: Session, key: str) -> Optional[str]:
    """Get an application setting value."""
    setting = session.query(ApplicationSettingTable).filter(
        ApplicationSettingTable.key == key
    ).first()
    return setting.value if setting else None


def set_setting(session: Session, key: str, value: str, description: Optional[str] = None) -> None:
    """Set an application setting."""
    setting = session.query(ApplicationSettingTable).filter(
        ApplicationSettingTable.key == key
    ).first()
    if setting is None:
        setting = ApplicationSettingTable(key=key, value=value, description=description)
        session.add(setting)
    else:
        setting.value = value
        if description is not None:
            setting.description = description
    session.flush()


# ─── Statistics ──────────────────────────────────────────────────────────────


def get_data_statistics(session: Session) -> dict:
    """Get data volume statistics for the admin page."""
    return {
        "departments": session.query(func.count(DepartmentTable.id)).scalar() or 0,
        "accounts": session.query(func.count(AccountTable.id)).scalar() or 0,
        "periods": session.query(func.count(PeriodTable.id)).scalar() or 0,
        "scenarios": session.query(func.count(ScenarioTable.id)).scalar() or 0,
        "versions": session.query(func.count(VersionTable.id)).scalar() or 0,
        "financial_facts": session.query(func.count(FinancialFactTable.id)).scalar() or 0,
        "import_batches": session.query(func.count(ImportBatchTable.id)).scalar() or 0,
        "audit_events": session.query(func.count(AuditEventTable.id)).scalar() or 0,
    }


# Alias for convenience
get_table_counts = get_data_statistics
