"""
TinyOlap calculation rules for Northstar Digital Services GmbH.
Defines dynamic calculations for Operating Profit, Operating Margin, etc.
"""
from __future__ import annotations

import logging
from tinyolap.cell import Cell
from tinyolap.decorators import rule

logger = logging.getLogger(__name__)


@rule("Financials", ["Operating Profit"])
def rule_operating_profit(c: Cell) -> float:
    """
    Operating Profit = Revenue + Total Operating Expenses
    (Total Operating Expenses is negative, so Revenue + Expenses = Profit)
    """
    dept = c.member("Department")
    period = c.member("Period")
    scenario = c.member("Scenario")
    rev = c.cube["REV", dept, period, scenario] or 0.0
    opex = c.cube["TOTAL_OPEX", dept, period, scenario] or 0.0
    return float(rev + opex)


@rule("Financials", ["Operating Margin"])
def rule_operating_margin(c: Cell) -> float:
    """
    Operating Margin % = (Operating Profit / Revenue) * 100
    """
    dept = c.member("Department")
    period = c.member("Period")
    scenario = c.member("Scenario")
    rev = c.cube["REV", dept, period, scenario] or 0.0
    profit = c.cube["Operating Profit", dept, period, scenario] or 0.0
    if rev and rev != 0:
        return float((profit / rev) * 100.0)
    return 0.0


def register_rules(cube) -> None:
    """Register all defined financial rules onto the TinyOlap cube."""
    cube.register_rule(rule_operating_profit)
    cube.register_rule(rule_operating_margin)
    logger.info("Registered rules on cube '%s'", cube.name)
