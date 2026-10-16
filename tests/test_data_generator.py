"""
Tests for synthetic data generator determinism, schema adherence, and demonstration fixtures.
"""
from __future__ import annotations

from decimal import Decimal
import pandas as pd
import pytest

from data_generator.generator import DataGenerator


class TestDataGenerator:
    """Test deterministic data generation."""

    def test_same_seed_produces_identical_output(self):
        """Identical seeds must produce identical dataframes and totals."""
        gen1 = DataGenerator(seed=42)
        gen2 = DataGenerator(seed=42)

        actuals1 = gen1.generate_actuals()
        actuals2 = gen2.generate_actuals()

        pd.testing.assert_frame_equal(actuals1, actuals2)

    def test_revenue_positive_and_expenses_negative(self):
        """Financial sign conventions must hold across generated actuals."""
        gen = DataGenerator(seed=42)
        actuals = gen.generate_actuals()

        rev_rows = actuals[actuals["account"] == "REV"]
        assert (rev_rows["amount"].astype(float) > 0).all()

        exp_rows = actuals[actuals["account"].isin(["SAL", "CLOUD", "SW", "MKT_EXP"])]
        assert (exp_rows["amount"].astype(float) < 0).all()

    def test_invalid_fixtures_contain_errors(self):
        """Invalid test fixture must contain intentional anomalies for testing."""
        gen = DataGenerator(seed=42)
        invalid_df = gen.generate_invalid_test_data()

        assert not invalid_df.empty
        # Should contain missing or invalid departments
        assert len(invalid_df) > 5
