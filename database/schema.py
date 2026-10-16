"""
SQLAlchemy ORM table definitions for the Enterprise Financial Planning Engine.

Tables:
  - departments: Department dimension
  - accounts: Account dimension with category and sign convention
  - periods: Financial periods (year-month)
  - scenarios: Scenario dimension (Actuals, Budget, Forecast, etc.)
  - versions: Version dimension linked to scenarios
  - financial_facts: Core fact table at canonical grain
  - forecast_assumptions: User-defined forecast parameters
  - import_batches: Import batch tracking
  - import_files: Files within import batches
  - validation_errors: Validation issues per import
  - audit_events: Application audit trail
  - application_settings: Key-value configuration store
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


class DepartmentTable(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    parent_code = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    financial_facts = relationship("FinancialFactTable", back_populates="department")
    forecast_assumptions = relationship("ForecastAssumptionTable", back_populates="department")


class AccountTable(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)
    parent_code = Column(String(50), nullable=True)
    sign_convention = Column(SmallInteger, nullable=False)  # +1 revenue, -1 expense
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("category IN ('revenue', 'expense')", name="ck_accounts_category"),
        CheckConstraint("sign_convention IN (1, -1)", name="ck_accounts_sign"),
    )

    # Relationships
    financial_facts = relationship("FinancialFactTable", back_populates="account")
    forecast_assumptions = relationship("ForecastAssumptionTable", back_populates="account")


class PeriodTable(Base):
    __tablename__ = "periods"

    id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    period_key = Column(String(7), unique=True, nullable=False)  # '2024-01'
    quarter = Column(Integer, nullable=False)
    is_closed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("month BETWEEN 1 AND 12", name="ck_periods_month"),
        CheckConstraint("quarter BETWEEN 1 AND 4", name="ck_periods_quarter"),
    )

    # Relationships
    financial_facts = relationship("FinancialFactTable", back_populates="period")


class ScenarioTable(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    is_locked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    versions = relationship("VersionTable", back_populates="scenario")
    financial_facts = relationship("FinancialFactTable", back_populates="scenario")
    forecast_assumptions = relationship("ForecastAssumptionTable", back_populates="scenario")


class VersionTable(Base):
    __tablename__ = "versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    scenario = relationship("ScenarioTable", back_populates="versions")
    financial_facts = relationship("FinancialFactTable", back_populates="version")
    forecast_assumptions = relationship("ForecastAssumptionTable", back_populates="version")


class ImportBatchTable(Base):
    __tablename__ = "import_batches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    status = Column(String(20), nullable=False, default="pending")
    total_rows = Column(Integer, default=0)
    accepted_rows = Column(Integer, default=0)
    rejected_rows = Column(Integer, default=0)
    duplicate_rows = Column(Integer, default=0)
    processing_duration_ms = Column(Integer, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'processing', 'completed', 'failed', 'rolled_back')",
            name="ck_import_batches_status",
        ),
    )

    # Relationships
    files = relationship("ImportFileTable", back_populates="batch")
    validation_errors = relationship("ValidationErrorTable", back_populates="batch")
    financial_facts = relationship("FinancialFactTable", back_populates="import_batch")


class ImportFileTable(Base):
    __tablename__ = "import_files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(Integer, ForeignKey("import_batches.id"), nullable=False)
    filename = Column(String(500), nullable=False)
    file_type = Column(String(10), nullable=False)
    file_size_bytes = Column(BigInteger, nullable=True)
    worksheet_name = Column(String(200), nullable=True)
    row_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    batch = relationship("ImportBatchTable", back_populates="files")
    validation_errors = relationship("ValidationErrorTable", back_populates="file")


class FinancialFactTable(Base):
    __tablename__ = "financial_facts"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    period_id = Column(Integer, ForeignKey("periods.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=False)
    version_id = Column(Integer, ForeignKey("versions.id"), nullable=False)
    currency = Column(String(3), nullable=False, default="EUR")
    amount = Column(Numeric(18, 2), nullable=False)  # Decimal-safe
    import_batch_id = Column(Integer, ForeignKey("import_batches.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "period_id",
            "department_id",
            "account_id",
            "scenario_id",
            "version_id",
            "currency",
            name="uq_financial_facts_grain",
        ),
        Index("idx_facts_period", "period_id"),
        Index("idx_facts_department", "department_id"),
        Index("idx_facts_account", "account_id"),
        Index("idx_facts_scenario", "scenario_id"),
        Index("idx_facts_composite", "period_id", "department_id", "scenario_id"),
    )

    # Relationships
    period = relationship("PeriodTable", back_populates="financial_facts")
    department = relationship("DepartmentTable", back_populates="financial_facts")
    account = relationship("AccountTable", back_populates="financial_facts")
    scenario = relationship("ScenarioTable", back_populates="financial_facts")
    version = relationship("VersionTable", back_populates="financial_facts")
    import_batch = relationship("ImportBatchTable", back_populates="financial_facts")


class ForecastAssumptionTable(Base):
    __tablename__ = "forecast_assumptions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=False)
    version_id = Column(Integer, ForeignKey("versions.id"), nullable=False)
    assumption_key = Column(String(100), nullable=False)
    assumption_value = Column(Numeric(10, 4), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    start_period_id = Column(Integer, ForeignKey("periods.id"), nullable=True)
    end_period_id = Column(Integer, ForeignKey("periods.id"), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    scenario = relationship("ScenarioTable", back_populates="forecast_assumptions")
    version = relationship("VersionTable", back_populates="forecast_assumptions")
    department = relationship("DepartmentTable", back_populates="forecast_assumptions")
    account = relationship("AccountTable", back_populates="forecast_assumptions")


class ValidationErrorTable(Base):
    __tablename__ = "validation_errors"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    batch_id = Column(Integer, ForeignKey("import_batches.id"), nullable=False)
    file_id = Column(Integer, ForeignKey("import_files.id"), nullable=True)
    row_number = Column(Integer, nullable=True)
    column_name = Column(String(100), nullable=True)
    error_type = Column(String(20), nullable=False)  # 'error', 'warning', 'info'
    error_code = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    raw_value = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_validation_batch", "batch_id"),
    )

    # Relationships
    batch = relationship("ImportBatchTable", back_populates="validation_errors")
    file = relationship("ImportFileTable", back_populates="validation_errors")


class AuditEventTable(Base):
    __tablename__ = "audit_events"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    event_type = Column(String(50), nullable=False)
    event_description = Column(Text, nullable=False)
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(String(100), nullable=True)
    metadata_json = Column(Text, nullable=True)  # JSON string for portability
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_audit_type", "event_type"),
        Index("idx_audit_created", "created_at"),
    )


class ApplicationSettingTable(Base):
    __tablename__ = "application_settings"

    key = Column(String(100), primary_key=True)
    value = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
