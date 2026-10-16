"""
Tests for financial exports: CSV byte streams and formatted multi-sheet Excel workbooks.
"""
from __future__ import annotations

import io
import openpyxl
import pandas as pd
import pytest

from services.export_service import ExportService


class TestExportService:
    """Test CSV and Excel report exports."""

    def test_dataframe_to_csv(self):
        """Export DataFrame to UTF-8 CSV bytes."""
        df = pd.DataFrame([{"dept": "ENG", "amount": 1000.0}])
        csv_bytes = ExportService.dataframe_to_csv(df)

        assert isinstance(csv_bytes, bytes)
        assert b"dept,amount" in csv_bytes
        assert b"ENG,1000.0" in csv_bytes

    def test_multi_sheet_excel_report(self):
        """Generate multi-sheet styled Excel workbook with metadata sheet."""
        df1 = pd.DataFrame([{"Department": "Engineering", "Revenue (€)": 150000.0}])
        df2 = pd.DataFrame([{"Account": "Salaries", "Actual Expenses (€)": -75000.0}])

        sheets = {
            "Departments": df1,
            "Accounts": df2,
        }

        excel_bytes = ExportService.generate_excel_report(
            sheets=sheets,
            report_title="Test Financial Report",
            filters={"Period": "2024-01 to 2024-12", "Scenario": "Actuals"},
        )

        assert isinstance(excel_bytes, bytes)
        assert len(excel_bytes) > 1000

        # Load back with openpyxl to verify sheets
        wb = openpyxl.load_workbook(io.BytesIO(excel_bytes))
        sheet_names = wb.sheetnames

        assert "Departments" in sheet_names
        assert "Accounts" in sheet_names
        assert "Report Info" in sheet_names
