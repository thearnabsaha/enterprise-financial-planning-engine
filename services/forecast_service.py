"""
Forecasting service: implements baseline trend projection, assumption-driven compounding,
scenario comparison, and assumption parameter persistence.
"""
from __future__ import annotations

import logging
from decimal import Decimal
from typing import Optional

import pandas as pd
from sqlalchemy.orm import Session

from calculations.forecasting import (
    assumption_driven_forecast,
    baseline_linear_forecast,
    calculate_scenario_forecast as calc_scenario_fc,
)
from database import repository as repo
from database.connection import get_session
from models.scenario import ForecastAssumption, ForecastMethod, ForecastResult

logger = logging.getLogger(__name__)

TWO_DP = Decimal("0.01")


class ForecastService:
    """Service for calculating and managing financial forecasts and scenarios."""

    @classmethod
    def get_forecast_assumptions(
        cls,
        scenario_name: str = "Forecast v1",
        session: Optional[Session] = None,
    ) -> list[dict]:
        """Retrieve assumptions for a given scenario."""
        def _fetch(s: Session) -> list[dict]:
            scn = repo.get_scenario_by_name(s, scenario_name)
            if not scn:
                return []
            assumptions = repo.get_forecast_assumptions(s, scn.id)
            depts = {d.id: d.name for d in repo.get_all_departments(s)}
            accounts = {a.id: a.name for a in repo.get_all_accounts(s)}

            return [
                {
                    "id": a.id,
                    "assumption_key": a.assumption_key,
                    "value": float(a.assumption_value),
                    "department": depts.get(a.department_id, "All Departments"),
                    "account": accounts.get(a.account_id, "All Accounts"),
                    "description": a.description or "",
                }
                for a in assumptions
            ]

        if session is not None:
            return _fetch(session)
        with get_session() as s:
            return _fetch(s)

    @classmethod
    def update_assumption(
        cls,
        scenario_name: str,
        assumption_key: str,
        value: float,
        session: Optional[Session] = None,
    ) -> bool:
        """Update or create a scenario assumption value."""
        def _update(s: Session) -> bool:
            scn = repo.get_scenario_by_name(s, scenario_name)
            if not scn:
                return False
            vers = repo.get_all_versions(s)
            ver_id = vers[0].id if vers else 1

            repo.upsert_forecast_assumption(
                session=s,
                scenario_id=scn.id,
                version_id=ver_id,
                assumption_key=assumption_key,
                assumption_value=Decimal(str(value)),
            )
            return True

        if session is not None:
            return _update(session)
        with get_session() as s:
            return _update(s)

    @classmethod
    def generate_baseline_forecast(
        cls,
        account_code: str = "REV",
        periods_ahead: int = 12,
        session: Optional[Session] = None,
    ) -> list[ForecastResult]:
        """Generate baseline linear trend forecast from historical actuals."""
        def _gen(s: Session) -> list[ForecastResult]:
            acc = repo.get_account_by_code(s, account_code)
            if not acc:
                return []

            actuals = repo.get_financial_facts(session=s, scenario_name="Actuals", account_id=acc.id)
            periods = {p.id: p.period_key for p in repo.get_all_periods(s)}

            # Group historicals by period
            hist_by_period: dict[str, Decimal] = {}
            for f in actuals:
                pkey = periods.get(f.period_id, "")
                if pkey:
                    hist_by_period[pkey] = hist_by_period.get(pkey, Decimal("0")) + f.amount

            sorted_keys = sorted(hist_by_period.keys())
            history = [hist_by_period[k] for k in sorted_keys]

            if not history:
                return []

            projected = baseline_linear_forecast(history, periods_ahead)

            # Determine next period keys
            last_key = sorted_keys[-1]
            last_year, last_month = int(last_key[:4]), int(last_key[5:7])

            results = []
            for i, amt in enumerate(projected):
                m = last_month + i + 1
                y = last_year + (m - 1) // 12
                actual_m = ((m - 1) % 12) + 1
                pkey = f"{y:04d}-{actual_m:02d}"

                results.append(ForecastResult(
                    period_key=pkey,
                    department="Company",
                    account=acc.name,
                    amount=amt,
                    method=ForecastMethod.BASELINE,
                    base_amount=history[-1],
                    scenario_name="Baseline Extrapolation",
                ))
            return results

        if session is not None:
            return _gen(session)
        with get_session() as s:
            return _gen(s)

    @classmethod
    def get_multi_scenario_comparison(
        cls,
        account_code: Optional[str] = "REV",
        session: Optional[Session] = None,
    ) -> pd.DataFrame:
        """
        Produce side-by-side comparison across all scenarios for an account or total profit.
        """
        def _compare(s: Session) -> pd.DataFrame:
            periods = {p.id: p.period_key for p in repo.get_all_periods(s)}
            accounts = {a.id: a for a in repo.get_all_accounts(s)}
            scenarios = repo.get_all_scenarios(s)

            target_acc = repo.get_account_by_code(s, account_code) if account_code else None

            data: dict[str, dict[str, Decimal]] = {}  # period -> {scenario -> amount}

            for scn in scenarios:
                facts = repo.get_financial_facts(
                    session=s,
                    scenario_name=scn.name,
                    account_id=target_acc.id if target_acc else None,
                )
                for f in facts:
                    pkey = periods.get(f.period_id, "")
                    if not pkey:
                        continue
                    if pkey not in data:
                        data[pkey] = {}

                    acc = accounts.get(f.account_id)
                    amt = f.amount if acc and acc.category == "revenue" else f.amount
                    data[pkey][scn.name] = data[pkey].get(scn.name, Decimal("0")) + amt

            rows = []
            for pkey in sorted(data.keys()):
                row = {"Period": pkey}
                for scn in scenarios:
                    val = data[pkey].get(scn.name)
                    row[scn.name] = float(val) if val is not None else None
                rows.append(row)

            return pd.DataFrame(rows)

        if session is not None:
            return _compare(session)
        with get_session() as s:
            return _compare(s)
