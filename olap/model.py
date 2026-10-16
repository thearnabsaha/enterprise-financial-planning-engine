"""
TinyOlap multidimensional model definition for Northstar Digital Services GmbH.
Defines Dimensions, Consolidations, Cubes, and Rules (TM1/OLAP architecture).
"""
from __future__ import annotations

import logging
from typing import Optional

from tinyolap.database import Database

from data_generator.dimensions import (
    ACCOUNTS,
    DEPARTMENTS,
    LEAF_ACCOUNTS,
    LEAF_DEPARTMENTS,
    PERIOD_END_YEAR,
    PERIOD_MONTHS,
    PERIOD_START_YEAR,
    SCENARIOS,
)
from olap.rules import register_rules

logger = logging.getLogger(__name__)


def create_olap_database(db_name: str = "northstar_financial") -> Database:
    """
    Create and configure the TinyOlap Database with 4 dimensions and the Financials cube.
    """
    db = Database(db_name, in_memory=True)

    # 1. Account Dimension
    acc_dim = db.add_dimension("Account")
    acc_dim.edit()

    # Root elements & consolidations
    acc_dim.add("REV", None, 1.0, "Revenue")
    acc_dim.add("TOTAL_OPEX", None, 1.0, "Total Operating Expenses")

    # Expense leaves roll up into TOTAL_OPEX
    for acc in ACCOUNTS:
        if acc.parent_code == "TOTAL_OPEX":
            acc_dim.add(acc.code, "TOTAL_OPEX", 1.0, acc.name)

    # Calculated rule elements
    acc_dim.add("Operating Profit", None, 1.0, "Rule-calculated Operating Profit")
    acc_dim.add("Operating Margin", None, 1.0, "Rule-calculated Operating Margin %")

    acc_dim.commit()

    # 2. Department Dimension
    dept_dim = db.add_dimension("Department")
    dept_dim.edit()
    dept_dim.add("COMPANY", None, 1.0, "Northstar Digital Services GmbH (Consolidated)")
    for dept in LEAF_DEPARTMENTS:
        dept_dim.add(dept.code, "COMPANY", 1.0, dept.name)
    dept_dim.commit()

    # 3. Period Dimension
    period_dim = db.add_dimension("Period")
    period_dim.edit()
    for year in range(PERIOD_START_YEAR, PERIOD_END_YEAR + 1):
        for month in PERIOD_MONTHS:
            period_dim.add(f"{year:04d}-{month:02d}", None, 1.0)
    period_dim.commit()

    # 4. Scenario Dimension
    scenario_dim = db.add_dimension("Scenario")
    scenario_dim.edit()
    for scn in SCENARIOS:
        scenario_dim.add(scn.name, None, 1.0, scn.description)
    scenario_dim.commit()

    # 5. Create Financials Cube
    cube = db.add_cube("Financials", [acc_dim, dept_dim, period_dim, scenario_dim])

    # 6. Register Rules
    register_rules(cube)

    logger.info("TinyOlap multidimensional model initialized successfully.")
    return db
