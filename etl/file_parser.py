"""
File parser for CSV and Excel files.
Handles reading, preview extraction, and metadata detection.
"""
from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import Optional, BinaryIO

import pandas as pd

from models.import_models import FilePreview

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}
MAX_PREVIEW_ROWS = 20


def parse_file(
    file_content: bytes,
    filename: str,
    worksheet_name: Optional[str] = None,
    max_rows: int = 100_000,
) -> tuple[pd.DataFrame, FilePreview]:
    """
    Parse an uploaded file and return the full DataFrame plus preview metadata.

    Parameters:
        file_content: Raw file bytes
        filename: Original filename
        worksheet_name: Sheet name for Excel files
        max_rows: Maximum rows to read (safety limit)

    Returns:
        (DataFrame of all rows, FilePreview metadata)

    Raises:
        ValueError: If file type is unsupported or parsing fails
    """
    ext = Path(filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{ext}'. Supported: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    file_size = len(file_content)
    buffer = io.BytesIO(file_content)

    try:
        if ext == ".csv":
            df = _parse_csv(buffer, max_rows)
            worksheets = []
        elif ext in (".xlsx", ".xls"):
            df, worksheets = _parse_excel(buffer, worksheet_name, max_rows)
        else:
            raise ValueError(f"Unsupported extension: {ext}")
    except pd.errors.EmptyDataError:
        raise ValueError(f"File '{filename}' is empty or contains no data.")
    except Exception as e:
        raise ValueError(f"Failed to parse '{filename}': {str(e)}")

    # Build preview
    preview = FilePreview(
        filename=filename,
        file_type=ext.lstrip("."),
        file_size_bytes=file_size,
        detected_columns=list(df.columns),
        worksheet_names=worksheets,
        row_count=len(df),
        preview_rows=df.head(MAX_PREVIEW_ROWS).to_dict(orient="records"),
    )

    return df, preview


def detect_worksheets(file_content: bytes, filename: str) -> list[str]:
    """Detect worksheet names in an Excel file."""
    ext = Path(filename).suffix.lower()
    if ext not in (".xlsx", ".xls"):
        return []

    try:
        buffer = io.BytesIO(file_content)
        xl = pd.ExcelFile(buffer, engine="openpyxl" if ext == ".xlsx" else None)
        return xl.sheet_names
    except Exception as e:
        logger.warning("Failed to detect worksheets in %s: %s", filename, e)
        return []


def _parse_csv(buffer: io.BytesIO, max_rows: int) -> pd.DataFrame:
    """Parse a CSV file."""
    # Try to detect encoding and delimiter
    df = pd.read_csv(
        buffer,
        nrows=max_rows,
        dtype=str,  # Read everything as strings for validation
        keep_default_na=False,
    )
    return df


def _parse_excel(
    buffer: io.BytesIO,
    worksheet_name: Optional[str],
    max_rows: int,
) -> tuple[pd.DataFrame, list[str]]:
    """Parse an Excel file, optionally selecting a specific worksheet."""
    xl = pd.ExcelFile(buffer, engine="openpyxl")
    worksheets = xl.sheet_names

    if worksheet_name:
        if worksheet_name not in worksheets:
            raise ValueError(
                f"Worksheet '{worksheet_name}' not found. Available: {', '.join(worksheets)}"
            )
        sheet = worksheet_name
    else:
        sheet = worksheets[0]  # Default to first sheet

    df = pd.read_excel(
        xl,
        sheet_name=sheet,
        nrows=max_rows,
        dtype=str,
        keep_default_na=False,
    )
    return df, worksheets
