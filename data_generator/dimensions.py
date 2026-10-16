"""
Dimension definitions for Northstar Digital Services GmbH.
Departments, accounts, periods, scenarios, and versions.
"""
from __future__ import annotations

from typing import NamedTuple


class DepartmentDef(NamedTuple):
    code: str
    name: str
    parent_code: str | None = None


class AccountDef(NamedTuple):
    code: str
    name: str
    category: str  # 'revenue' or 'expense'
    sign_convention: int  # +1 or -1
    parent_code: str | None = None


class ScenarioDef(NamedTuple):
    name: str
    description: str


class VersionDef(NamedTuple):
    name: str
    scenario_name: str
    description: str


# ─── Departments ─────────────────────────────────────────────────────────────

DEPARTMENTS: list[DepartmentDef] = [
    DepartmentDef("COMPANY", "Northstar Digital Services GmbH", None),
    DepartmentDef("ENG", "Engineering", "COMPANY"),
    DepartmentDef("SALES", "Sales", "COMPANY"),
    DepartmentDef("MKT", "Marketing", "COMPANY"),
    DepartmentDef("OPS", "Operations", "COMPANY"),
    DepartmentDef("FIN", "Finance", "COMPANY"),
]

# Leaf departments (excluding consolidation parent)
LEAF_DEPARTMENTS = [d for d in DEPARTMENTS if d.parent_code is not None]

# ─── Accounts ────────────────────────────────────────────────────────────────

ACCOUNTS: list[AccountDef] = [
    # Revenue
    AccountDef("REV", "Revenue", "revenue", 1, None),
    # Expenses (12 accounts)
    AccountDef("TOTAL_OPEX", "Total Operating Expenses", "expense", -1, None),
    AccountDef("SAL", "Salaries and Benefits", "expense", -1, "TOTAL_OPEX"),
    AccountDef("CLOUD", "Cloud Infrastructure", "expense", -1, "TOTAL_OPEX"),
    AccountDef("SW", "Software Subscriptions", "expense", -1, "TOTAL_OPEX"),
    AccountDef("MKT_EXP", "Marketing Expenses", "expense", -1, "TOTAL_OPEX"),
    AccountDef("RENT", "Rent and Facilities", "expense", -1, "TOTAL_OPEX"),
    AccountDef("TRAVEL", "Travel and Entertainment", "expense", -1, "TOTAL_OPEX"),
    AccountDef("PROF", "Professional Services", "expense", -1, "TOTAL_OPEX"),
    AccountDef("DEPR", "Depreciation", "expense", -1, "TOTAL_OPEX"),
    AccountDef("TRAIN", "Training and Development", "expense", -1, "TOTAL_OPEX"),
    AccountDef("INSUR", "Insurance", "expense", -1, "TOTAL_OPEX"),
    AccountDef("OTHER", "Other Operating Expenses", "expense", -1, "TOTAL_OPEX"),
]

# Leaf accounts (excluding consolidation parents)
LEAF_ACCOUNTS = [a for a in ACCOUNTS if a.code not in ("TOTAL_OPEX",)]

REVENUE_ACCOUNTS = [a for a in LEAF_ACCOUNTS if a.category == "revenue"]
EXPENSE_ACCOUNTS = [a for a in LEAF_ACCOUNTS if a.category == "expense"]

# ─── Scenarios ───────────────────────────────────────────────────────────────

SCENARIOS: list[ScenarioDef] = [
    ScenarioDef("Actuals", "Actual financial results as recorded"),
    ScenarioDef("Original Budget", "Board-approved annual budget"),
    ScenarioDef("Revised Budget", "Mid-year budget revision effective July 2025"),
    ScenarioDef("Forecast v1", "Latest management forecast"),
    ScenarioDef("Optimistic Scenario", "Best-case growth scenario"),
    ScenarioDef("Conservative Scenario", "Cautious growth scenario"),
]

# ─── Versions ────────────────────────────────────────────────────────────────

VERSIONS: list[VersionDef] = [
    VersionDef("v1", "Actuals", "Primary version"),
    VersionDef("v1-budget", "Original Budget", "Original board-approved budget"),
    VersionDef("v2-budget", "Revised Budget", "Mid-year revised budget"),
    VersionDef("v1-forecast", "Forecast v1", "Initial management forecast"),
    VersionDef("v1-optimistic", "Optimistic Scenario", "Best-case version"),
    VersionDef("v1-conservative", "Conservative Scenario", "Cautious version"),
]

# ─── Periods ─────────────────────────────────────────────────────────────────

PERIOD_START_YEAR = 2024
PERIOD_END_YEAR = 2026
PERIOD_MONTHS = list(range(1, 13))

CURRENCIES = ["EUR"]
