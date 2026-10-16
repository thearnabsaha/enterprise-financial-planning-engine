"""
Import service: orchestrates file parsing, column mapping, validation,
transformation, transactional loading, and audit trail logging.
"""
from __future__ import annotations

import logging
import time
from typing import BinaryIO, Optional, Union
from uuid import uuid4

import pandas as pd
from sqlalchemy.orm import Session

from database import repository as repo
from database.connection import get_session
from etl.column_mapper import apply_column_mapping, auto_map_columns
from etl.file_parser import parse_file
from etl.loader import LoadResult, load_financial_facts
from etl.transformer import transform_dataframe
from models.import_models import (
    DuplicatePolicy,
    ImportBatch,
    ImportResult,
    ImportStatus,
    ParsedFile,
    ValidationSummary,
)
from services.audit_service import AuditService
from services.validation_service import ValidationService

logger = logging.getLogger(__name__)


class ImportService:
    """Orchestrates end-to-end financial data import workflow."""

    @staticmethod
    def inspect_file(
        file_source: Union[bytes, str, BinaryIO, Path],
        filename: str,
        worksheet_name: Optional[str] = None,
    ):
        """Parse an uploaded file and extract preview and metadata."""
        from pathlib import Path
        if isinstance(file_source, bytes):
            content = file_source
        elif hasattr(file_source, "read"):
            content = file_source.read()
        elif isinstance(file_source, (str, Path)):
            with open(file_source, "rb") as f:
                content = f.read()
        else:
            content = bytes(file_source)
        return parse_file(content, filename, worksheet_name)

    @staticmethod
    def get_auto_mapping(columns: list[str]) -> dict[str, str]:
        """Automatically detect column mappings based on aliases."""
        mapping_list = auto_map_columns(columns)
        return {m.source_column: m.target_field for m in mapping_list}

    @classmethod
    def execute_import(
        cls,
        df: pd.DataFrame,
        filename: str,
        column_mapping: Optional[dict[str, str]] = None,
        duplicate_policy: DuplicatePolicy = DuplicatePolicy.REJECT,
        worksheet_name: Optional[str] = None,
        file_size_bytes: Optional[int] = None,
        session: Optional[Session] = None,
    ) -> ImportResult:
        """
        Execute full import pipeline:
        1. Map columns
        2. Validate records
        3. Transform to canonical schema
        4. Transactionally load into database
        5. Audit event logging
        """
        start_time = time.monotonic()
        batch_uuid = uuid4()

        # Step 1: Apply mapping
        if column_mapping:
            mapped_df = apply_column_mapping(df, column_mapping)
        else:
            auto_map = cls.get_auto_mapping(list(df.columns))
            mapped_df = apply_column_mapping(df, auto_map)

        # Step 2: Validate
        validation_summary = ValidationService.validate(mapped_df)

        # If there are blocking validation errors and rejected rows
        if validation_summary.invalid_rows > 0 and duplicate_policy == DuplicatePolicy.REJECT:
            duration_ms = int((time.monotonic() - start_time) * 1000)
            return ImportResult(
                batch_id=0,
                status=ImportStatus.FAILED,
                total_rows=len(df),
                accepted_rows=0,
                rejected_rows=validation_summary.invalid_rows,
                duplicate_rows=0,
                validation_summary=validation_summary,
                duration_ms=duration_ms,
                errors=[e.message for e in validation_summary.errors[:20]],
            )

        # Step 3: Transform
        transformed_df = transform_dataframe(mapped_df)

        def _do_load(s: Session) -> ImportResult:
            # Create batch record
            batch = repo.create_import_batch(s)
            batch.status = "processing"
            s.flush()

            # Record file metadata
            repo.create_import_file(
                session=s,
                batch_id=batch.id,
                filename=filename,
                file_type="xlsx" if filename.endswith((".xlsx", ".xls")) else "csv",
                file_size_bytes=file_size_bytes or 0,
                worksheet_name=worksheet_name,
                row_count=len(df),
            )

            # Record any validation warnings/errors in the database
            for err in validation_summary.errors:
                repo.create_validation_error(
                    session=s,
                    batch_id=batch.id,
                    row_number=err.row_number,
                    column_name=err.column_name,
                    error_type=err.severity.value,
                    error_code=err.error_code,
                    message=err.message,
                    raw_value=err.raw_value,
                )

            # Execute transactional load
            load_result: LoadResult = load_financial_facts(
                session=s,
                df=transformed_df,
                batch_id=batch.id,
                duplicate_policy=duplicate_policy,
            )

            duration_ms = int((time.monotonic() - start_time) * 1000)
            status = "completed" if load_result.rejected == 0 else "completed_with_errors"

            repo.update_import_batch(
                session=s,
                batch_id=batch.id,
                status=status,
                total_rows=len(df),
                accepted_rows=load_result.inserted,
                rejected_rows=load_result.rejected,
                duplicate_rows=load_result.duplicates,
                processing_duration_ms=duration_ms,
            )

            AuditService.log(
                event_type="IMPORT_COMPLETED",
                description=f"Imported {load_result.inserted} rows from {filename} (status: {status})",
                entity_type="IMPORT_BATCH",
                entity_id=str(batch.id),
                session=s,
            )

            return ImportResult(
                batch_id=batch.id,
                status=ImportStatus.COMPLETED if status == "completed" else ImportStatus.FAILED,
                total_rows=len(df),
                accepted_rows=load_result.inserted,
                rejected_rows=load_result.rejected,
                duplicate_rows=load_result.duplicates,
                validation_summary=validation_summary,
                duration_ms=duration_ms,
                errors=load_result.errors,
            )

        if session is not None:
            return _do_load(session)
        with get_session() as s:
            return _do_load(s)
