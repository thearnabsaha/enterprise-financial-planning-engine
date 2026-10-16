"""
Tests for TinyOlap multidimensional model, consolidations, dynamic rules, and adapter sync.
"""
from __future__ import annotations

import pytest

from olap.adapter import OlapAdapter
from olap.model import create_olap_database


class TestTinyOlapModel:
    """Test multidimensional OLAP modeling with TinyOlap."""

    def test_olap_database_and_cube_creation(self):
        """Model initializes dimensions and Financials cube."""
        db = create_olap_database("test_olap_suite")
        assert "Financials" in db.cubes
        cube = db.cubes["Financials"]
        assert cube.dimensions_count == 4

    def test_department_consolidation(self):
        """Consolidated department COMPANY aggregates leaf departments."""
        db = create_olap_database("test_dept_consol")
        cube = db.cubes["Financials"]

        cube["REV", "ENG", "2024-01", "Actuals"] = 100000.0
        cube["REV", "SALES", "2024-01", "Actuals"] = 150000.0

        company_rev = cube["REV", "COMPANY", "2024-01", "Actuals"]
        assert company_rev == 250000.0

    def test_rule_operating_profit_calculation(self):
        """Rule dynamically computes Operating Profit = Revenue + Expenses."""
        db = create_olap_database("test_rules_profit")
        cube = db.cubes["Financials"]

        cube["REV", "ENG", "2024-01", "Actuals"] = 200000.0
        cube["SAL", "ENG", "2024-01", "Actuals"] = -120000.0
        cube["CLOUD", "ENG", "2024-01", "Actuals"] = -30000.0

        # TOTAL_OPEX rolls up SAL (-120k) and CLOUD (-30k) -> -150k
        tot_opex = cube["TOTAL_OPEX", "ENG", "2024-01", "Actuals"]
        assert tot_opex == -150000.0

        # Operating Profit rule evaluates: 200k + (-150k) = 50k
        profit = cube["Operating Profit", "ENG", "2024-01", "Actuals"]
        assert profit == 50000.0

        # Operating Margin rule evaluates: (50k / 200k) * 100 = 25%
        margin = cube["Operating Margin", "ENG", "2024-01", "Actuals"]
        assert margin == 25.0

    def test_olap_adapter_query(self):
        """OlapAdapter abstracts cell queries gracefully."""
        adapter = OlapAdapter()
        adapter.cube["REV", "ENG", "2024-01", "Actuals"] = 88000.0
        val = adapter.get_cell("REV", "ENG", "2024-01", "Actuals")
        assert val == 88000.0
