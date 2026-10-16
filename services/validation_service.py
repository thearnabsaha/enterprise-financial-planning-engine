"""
Validation service: orchestrates data quality checks, rule enforcement,
and error reporting for financial datasets.
"""
from __future__ import annotations

import logging
from typing import Optional

import pandas as pd
from sqlalchemy.orm import Session

from database import repository as repo
from database.connection import get_session
from etl.validator import validate_dataframe
from models.import_models import ValidationSeverity, ValidationSummary

logger = logging.getLogger(__name__)


class ValidationService:
    """Service for running data quality rules against financial DataFrames."""

    @staticmethod
    def get_known_dimensions(session: Optional[Session] = None) -> tuple[set[str], set[str], set[str]]:
        """Retrieve active departments, accounts, and scenarios for validation."""
        def _fetch(s: Session):
            depts = {d.code for d in repo.get_all_departments(s)}
            accounts = {a.code for a in repo.get_all_accounts(s)}
            scenarios = {sc.name for sc in repo.get_all_scenarios(s)}
            return depts, accounts, scenarios

        if session is not None:
            return _fetch(session)
        with get_session() as s:
            return _fetch(s)

    @classmethod
    def validate(
        cls,
        df: pd.DataFrame,
        file_id: Optional[int] = None,
        batch_id: Optional[int] = None,
        session: Optional[Session] = None,
    ) -> ValidationSummary:
        """
        Validate a DataFrame against current dimension records in the database.
        """
        depts, accounts, scenarios = cls.get_known_dimensions(session)
        return validate_dataframe(
            df=df,
            known_departments=depts,
            known_accounts=accounts,
            known_scenarios=scenarios,
            file_id=file_id,
            batch_id=batch_id,
        )

    @staticmethod
    def errors_to_dataframe(summary: ValidationSummary) -> pd.DataFrame:
        """Convert validation errors list into a presentable DataFrame for the UI."""
        if not summary.errors:
            return pd.DataFrame(columns=["Row", "Column", "Severity", "Code", "Message", "Raw Value"])

        rows = []
        for err in summary.errors:
            rows.append({
                "Row": err.row_number,
                "Column": err.column_name or "N/A",
                "Severity": err.severity.value.upper(),
                "Code": err.error_code,
                "Message": err.message,
                "Raw Value": err.raw_value or "",
            })
        return pd.DataFrame(rows)
