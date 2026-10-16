"""
Pydantic models for forecast scenarios and assumptions.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ForecastMethod(str, Enum):
    """Available forecasting methods."""
    BASELINE = "baseline"
    ASSUMPTION_DRIVEN = "assumption_driven"
    SCENARIO = "scenario"


class ForecastAssumption(BaseModel):
    """A single forecast assumption (e.g., revenue growth rate)."""
    id: Optional[int] = None
    scenario_id: int
    version_id: int
    assumption_key: str = Field(min_length=1, max_length=100)
    assumption_value: Decimal = Field(decimal_places=4)
    department_id: Optional[int] = None  # None = applies to all departments
    account_id: Optional[int] = None     # None = applies to all accounts
    start_period_id: Optional[int] = None
    end_period_id: Optional[int] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ScenarioDefinition(BaseModel):
    """A complete scenario definition with its assumptions."""
    scenario_id: int
    scenario_name: str
    version_id: int
    version_name: str
    method: ForecastMethod
    description: Optional[str] = None
    assumptions: list[ForecastAssumption] = []
    is_locked: bool = False


class ForecastResult(BaseModel):
    """Result of a forecast calculation for a single cell."""
    period_key: str
    department: str
    account: str
    amount: Decimal
    method: ForecastMethod
    base_amount: Optional[Decimal] = None
    growth_rate: Optional[Decimal] = None
    scenario_name: str = ""


class ScenarioComparison(BaseModel):
    """Side-by-side scenario comparison for a metric."""
    period_key: str
    metric_name: str
    values: dict[str, Decimal] = {}  # scenario_name -> value
    differences: dict[str, Decimal] = {}  # scenario_name -> diff vs baseline


# Predefined assumption keys
ASSUMPTION_KEYS = {
    "revenue_growth_rate": "Revenue growth rate (decimal, e.g. 0.05 = 5%)",
    "salary_growth_rate": "Salary and benefits growth rate",
    "cloud_cost_growth_rate": "Cloud infrastructure cost growth rate",
    "marketing_budget_adjustment": "Marketing budget adjustment factor",
    "rent_escalation_rate": "Rent and facilities annual escalation",
    "travel_adjustment": "Travel and entertainment adjustment factor",
    "software_cost_growth": "Software subscriptions growth rate",
    "professional_services_adjustment": "Professional services adjustment factor",
    "depreciation_rate": "Depreciation rate adjustment",
    "other_expense_growth": "Other operating expenses growth rate",
}
