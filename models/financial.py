"""
Pydantic domain models for financial entities.
These are used for validation, serialisation, and type safety throughout the application.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ─── Enums ───────────────────────────────────────────────────────────────────


class AccountCategory(str, Enum):
    """Account type classification."""
    REVENUE = "revenue"
    EXPENSE = "expense"


class Favourability(str, Enum):
    """Variance favourability classification."""
    FAVOURABLE = "favourable"
    UNFAVOURABLE = "unfavourable"
    NEUTRAL = "neutral"


class ScenarioType(str, Enum):
    """Predefined scenario types."""
    ACTUALS = "Actuals"
    ORIGINAL_BUDGET = "Original Budget"
    REVISED_BUDGET = "Revised Budget"
    FORECAST_V1 = "Forecast v1"
    OPTIMISTIC = "Optimistic Scenario"
    CONSERVATIVE = "Conservative Scenario"


# ─── Dimension Models ────────────────────────────────────────────────────────


class Department(BaseModel):
    """Department dimension entity."""
    id: Optional[int] = None
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=200)
    parent_code: Optional[str] = None
    is_active: bool = True

    model_config = {"from_attributes": True}


class Account(BaseModel):
    """Account dimension entity."""
    id: Optional[int] = None
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=200)
    category: AccountCategory
    parent_code: Optional[str] = None
    sign_convention: int = Field(description="+1 for revenue, -1 for expense")
    is_active: bool = True

    @field_validator("sign_convention")
    @classmethod
    def validate_sign(cls, v: int) -> int:
        if v not in (1, -1):
            raise ValueError("sign_convention must be +1 or -1")
        return v

    model_config = {"from_attributes": True}


class Period(BaseModel):
    """Financial period dimension entity."""
    id: Optional[int] = None
    year: int = Field(ge=2000, le=2100)
    month: int = Field(ge=1, le=12)
    period_key: str = Field(pattern=r"^\d{4}-\d{2}$")
    quarter: Optional[int] = None
    is_closed: bool = False

    @property
    def display_name(self) -> str:
        import calendar
        return f"{calendar.month_abbr[self.month]} {self.year}"

    model_config = {"from_attributes": True}


class Scenario(BaseModel):
    """Financial scenario entity."""
    id: Optional[int] = None
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None
    is_locked: bool = False

    model_config = {"from_attributes": True}


class Version(BaseModel):
    """Version entity within a scenario."""
    id: Optional[int] = None
    name: str = Field(min_length=1, max_length=100)
    scenario_id: Optional[int] = None
    description: Optional[str] = None

    model_config = {"from_attributes": True}


# ─── Financial Fact ──────────────────────────────────────────────────────────


class FinancialFact(BaseModel):
    """
    A single financial fact at the canonical grain:
    (period, department, account, scenario, version, currency).

    Sign convention:
      - Revenue amounts are POSITIVE
      - Expense amounts are NEGATIVE
      - Operating profit = sum of revenue + expenses
    """
    id: Optional[int] = None
    period_id: int
    department_id: int
    account_id: int
    scenario_id: int
    version_id: int
    currency: str = Field(default="EUR", max_length=3)
    amount: Decimal = Field(decimal_places=2)
    import_batch_id: Optional[int] = None

    model_config = {"from_attributes": True}


# ─── KPI / Calculation Results ───────────────────────────────────────────────


class VarianceResult(BaseModel):
    """Result of a variance calculation between actual and budget."""
    actual: Decimal
    budget: Decimal
    signed_variance: Decimal
    variance_percentage: Optional[Decimal] = None
    favourability: Favourability
    account_category: AccountCategory


class KPISummary(BaseModel):
    """Aggregated KPI values for dashboard display."""
    total_revenue: Decimal = Decimal("0")
    total_expenses: Decimal = Decimal("0")
    operating_profit: Decimal = Decimal("0")
    operating_margin: Optional[Decimal] = None
    budget_variance: Optional[Decimal] = None
    budget_variance_pct: Optional[Decimal] = None
    forecast_operating_profit: Optional[Decimal] = None
    period_label: str = ""
    scenario_label: str = ""
    data_freshness: Optional[datetime] = None


class MonthlyMetric(BaseModel):
    """Monthly financial metric for trend charts."""
    period_key: str
    period_label: str
    value: Decimal
    comparison_value: Optional[Decimal] = None
    change_amount: Optional[Decimal] = None
    change_percentage: Optional[Decimal] = None
