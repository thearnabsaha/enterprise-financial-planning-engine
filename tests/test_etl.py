"""
Tests for ETL pipeline: file parser, column mapper, validator, and transformer.
"""
from __future__ import annotations

import io
from decimal import Decimal
import pandas as pd
import pytest

from etl.column_mapper import apply_column_mapping, auto_map_columns
from etl.file_parser import parse_file
from etl.transformer import transform_dataframe
from etl.validator import validate_dataframe


class TestETLPipeline:
    """Test ETL components."""

    def test_file_parser_csv(self):
        """Parse CSV bytes and extract preview and headers."""
        csv_content = b"dept,acct,period,amt\nENG,REV,2024-01,1000\nSALES,SAL,2024-01,-500\n"
        df, preview = parse_file(csv_content, "test.csv")

        assert len(df) == 2
        assert preview.row_count == 2
        assert preview.file_type == "csv"
        assert "dept" in preview.detected_columns
        assert len(preview.preview_rows) == 2

    def test_auto_column_mapper_aliases(self):
        """Auto column mapper identifies common enterprise financial headers."""
        columns = ["Cost Center", "GL Account", "Booking Date", "Total Amount"]
        mappings = auto_map_columns(columns)
        mapping_dict = {m.source_column: m.target_field for m in mappings}

        assert mapping_dict.get("Cost Center") == "department"
        assert mapping_dict.get("GL Account") == "account"
        assert mapping_dict.get("Booking Date") == "date"
        assert mapping_dict.get("Total Amount") == "amount"

    def test_validator_detects_unknown_department(self):
        """Validation flags records with invalid departments."""
        df = pd.DataFrame([{
            "department": "INVALID_DEPT",
            "account": "REV",
            "period": "2024-01",
            "amount": "1000",
        }])

        summary = validate_dataframe(
            df=df,
            known_departments={"ENG", "SALES", "MKT"},
            known_accounts={"REV"},
            known_scenarios={"Actuals"},
        )

        assert summary.invalid_rows == 1
        assert any("department" in e.message.lower() for e in summary.errors)

    def test_transformer_normalisation(self):
        """Transformer converts dates to periods and strings to canonical types."""
        df = pd.DataFrame([{
            "department": "ENG  ",
            "account": "REV",
            "date": "2024-03-15",
            "amount": "1,500.50",
        }])

        transformed = transform_dataframe(df)

        assert transformed.iloc[0]["department"] == "ENG"
        assert transformed.iloc[0]["period"] == "2024-03"
        assert float(transformed.iloc[0]["amount"]) == 1500.50
