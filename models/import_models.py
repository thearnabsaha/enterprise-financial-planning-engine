"""
Pydantic models for the import workflow: batches, files, validation results.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ImportStatus(str, Enum):
    """Import batch processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class DuplicatePolicy(str, Enum):
    """How to handle duplicate financial facts during import."""
    REJECT = "reject"
    SKIP = "skip"
    REPLACE = "replace"


class ValidationSeverity(str, Enum):
    """Severity classification for validation messages."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ImportBatch(BaseModel):
    """An import batch tracking record."""
    id: Optional[int] = None
    batch_uuid: Optional[UUID] = None
    status: ImportStatus = ImportStatus.PENDING
    total_rows: int = 0
    accepted_rows: int = 0
    rejected_rows: int = 0
    duplicate_rows: int = 0
    processing_duration_ms: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ImportFile(BaseModel):
    """Metadata for a file within an import batch."""
    id: Optional[int] = None
    batch_id: Optional[int] = None
    filename: str
    file_type: str
    file_size_bytes: Optional[int] = None
    worksheet_name: Optional[str] = None
    row_count: Optional[int] = None

    model_config = {"from_attributes": True}


class ValidationError(BaseModel):
    """A single validation issue found during import processing."""
    id: Optional[int] = None
    batch_id: Optional[int] = None
    file_id: Optional[int] = None
    row_number: Optional[int] = None
    column_name: Optional[str] = None
    error_type: ValidationSeverity = ValidationSeverity.ERROR
    error_code: str
    message: str
    raw_value: Optional[str] = None

    model_config = {"from_attributes": True}


class ColumnMapping(BaseModel):
    """Mapping from a source file column to the canonical schema."""
    source_column: str
    target_field: str
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    is_auto_mapped: bool = True

    model_config = {"from_attributes": True}


class FilePreview(BaseModel):
    """Preview information for an uploaded file."""
    filename: str
    file_type: str
    file_size_bytes: int
    detected_columns: list[str] = []
    worksheet_names: list[str] = []
    row_count: int = 0
    preview_rows: list[dict] = []
    column_mappings: list[ColumnMapping] = []


class ValidationSummary(BaseModel):
    """Aggregated validation results for display."""
    total_rows: int = 0
    valid_rows: int = 0
    invalid_rows: int = 0
    duplicate_rows: int = 0
    warning_count: int = 0
    info_count: int = 0
    errors: list[ValidationError] = []
    missing_values_by_column: dict[str, int] = {}


class ImportResult(BaseModel):
    """Final result of an import operation."""
    batch_id: int
    batch_uuid: UUID
    status: ImportStatus
    total_rows: int
    accepted_rows: int
    rejected_rows: int
    duplicate_rows: int
    duration_ms: int
    errors: list[ValidationError] = []
    warnings: list[ValidationError] = []
