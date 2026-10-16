"""
Calculation service: aggregates facts from the database and computes
financial KPIs, variances, margins, waterfall data, and trend analysis.
"""
from __future__ import annotations

import logging
from decimal import Decimal
from typing import Optional

import pandas as pd
from sqlalchemy.orm import Session

from calculations.formatting import format_currency, format_percent, format_variance_badge
from calculations.metrics import operating_margin, operating_profit
from calculations.variance import classify_favourability, signed_variance, variance_pct
from database import repository as repo
from database.connection import get_session
from models.financial import Favourability, FinancialKPIs

logger = logging.getLogger(__name__)

TWO_DP = Decimal("0.01")


class CalculationService:
    """Computes financial analytics, variances, and presentation metrics."""

    @classmethod
    def get_kpis(
        cls,
        start_period: Optional[str] = None,
        end_period: Optional[str] = None,
        department_codes: Optional[list[str]] = None,
        scenario_name: str = "Actuals",
        compare_scenario: str = "Original Budget",
        session: Optional[Session] = None,
    ) -> dict:
        """
        Compute high-level executive KPIs for a selected scope.
        """
        def _compute(s: Session) -> dict:
            # Resolve department IDs
            dept_ids = None
            if department_codes:
                all_depts = repo.get_all_departments(s)
                code_to_id = {d.code: d.id for d in all_depts}
                dept_ids = [code_to_id[c] for c in department_codes if c in code_to_id]

            # Fetch active and comparison facts
            actual_facts = repo.get_financial_facts(
                session=s,
                scenario_name=scenario_name,
                start_period=start_period,
                end_period=end_period,
                department_ids=dept_ids,
            )
            budget_facts = repo.get_financial_facts(
                session=s,
                scenario_name=compare_scenario,
                start_period=start_period,
                end_period=end_period,
                department_ids=dept_ids,
            )

            accounts = {a.id: a for a in repo.get_all_accounts(s)}

            # Aggregate actuals
            act_rev = Decimal("0")
            act_exp = Decimal("0")
            for f in actual_facts:
                acc = accounts.get(f.account_id)
                if acc:
                    if acc.category == "revenue":
                        act_rev += f.amount
                    else:
                        act_exp += f.amount

            # Aggregate budget
            bud_rev = Decimal("0")
            bud_exp = Decimal("0")
            for f in budget_facts:
                acc = accounts.get(f.account_id)
                if acc:
                    if acc.category == "revenue":
                        bud_rev += f.amount
                    else:
                        bud_exp += f.amount

            act_profit = operating_profit(act_rev, act_exp)
            bud_profit = operating_profit(bud_rev, bud_exp)

            act_margin = operating_margin(act_profit, act_rev)
            bud_margin = operating_margin(bud_profit, bud_rev)

            rev_var = signed_variance(act_rev, bud_rev)
            rev_var_pct = variance_pct(act_rev, bud_rev)

            exp_var = signed_variance(act_exp, bud_exp)
            exp_var_pct = variance_pct(act_exp, bud_exp)

            profit_var = signed_variance(act_profit, bud_profit)
            profit_var_pct = variance_pct(act_profit, bud_profit)

            return {
                "revenue": act_rev,
                "revenue_budget": bud_rev,
                "revenue_variance": rev_var,
                "revenue_variance_pct": rev_var_pct,
                "revenue_favourability": classify_favourability("revenue", rev_var),
                "expenses": act_exp,
                "expenses_budget": bud_exp,
                "expenses_variance": exp_var,
                "expenses_variance_pct": exp_var_pct,
                "expenses_favourability": classify_favourability("expense", exp_var),
                "profit": act_profit,
                "profit_budget": bud_profit,
                "profit_variance": profit_var,
                "profit_variance_pct": profit_var_pct,
                "profit_favourability": classify_favourability("profit", profit_var),
                "margin_pct": act_margin,
                "margin_budget_pct": bud_margin,
            }

        if session is not None:
            return _compute(session)
        with get_session() as s:
            return _compute(s)

    @classmethod
    def get_monthly_trend(
        cls,
        department_codes: Optional[list[str]] = None,
        scenario_name: str = "Actuals",
        compare_scenario: Optional[str] = "Original Budget",
        session: Optional[Session] = None,
    ) -> pd.DataFrame:
        """
        Get monthly revenue, expense, and profit time series for active and compare scenarios.
        """
        def _fetch(s: Session) -> pd.DataFrame:
            dept_ids = None
            if department_codes:
                all_depts = repo.get_all_departments(s)
                code_to_id = {d.code: d.id for d in all_depts}
                dept_ids = [code_to_id[c] for c in department_codes if c in code_to_id]

            periods = {p.id: p.period_key for p in repo.get_all_periods(s)}
            accounts = {a.id: a for a in repo.get_all_accounts(s)}

            scenarios_to_load = [scenario_name]
            if compare_scenario and compare_scenario != scenario_name:
                scenarios_to_load.append(compare_scenario)

            rows = []
            for scn in scenarios_to_load:
                facts = repo.get_financial_facts(session=s, scenario_name=scn, department_ids=dept_ids)
                monthly_data: dict[str, dict[str, Decimal]] = {}

                for f in facts:
                    pkey = periods.get(f.period_id, "")
                    if pkey not in monthly_data:
                        monthly_data[pkey] = {"revenue": Decimal("0"), "expenses": Decimal("0")}
                    acc = accounts.get(f.account_id)
                    if acc:
                        if acc.category == "revenue":
                            monthly_data[pkey]["revenue"] += f.amount
                        else:
                            monthly_data[pkey]["expenses"] += f.amount

                for pkey, vals in sorted(monthly_data.items()):
                    profit = vals["revenue"] + vals["expenses"]
                    margin = (profit / vals["revenue"] * 100) if vals["revenue"] > 0 else Decimal("0")
                    rows.append({
                        "period": pkey,
                        "scenario": scn,
                        "revenue": float(vals["revenue"]),
                        "expenses": float(vals["expenses"]),
                        "profit": float(profit),
                        "margin_pct": float(margin.quantize(TWO_DP)),
                    })

            return pd.DataFrame(rows)

        if session is not None:
            return _fetch(session)
        with get_session() as s:
            return _fetch(s)

    @classmethod
    def get_account_variance_summary(
        cls,
        start_period: Optional[str] = None,
        end_period: Optional[str] = None,
        department_codes: Optional[list[str]] = None,
        scenario_name: str = "Actuals",
        compare_scenario: str = "Original Budget",
        session: Optional[Session] = None,
    ) -> pd.DataFrame:
        """
        Account-level variance table with signed variance, %, and favourability.
        """
        def _fetch(s: Session) -> pd.DataFrame:
            dept_ids = None
            if department_codes:
                all_depts = repo.get_all_departments(s)
                code_to_id = {d.code: d.id for d in all_depts}
                dept_ids = [code_to_id[c] for c in department_codes if c in code_to_id]

            accounts = {a.id: a for a in repo.get_all_accounts(s)}
            act_facts = repo.get_financial_facts(session=s, scenario_name=scenario_name, start_period=start_period, end_period=end_period, department_ids=dept_ids)
            bud_facts = repo.get_financial_facts(session=s, scenario_name=compare_scenario, start_period=start_period, end_period=end_period, department_ids=dept_ids)

            act_by_acc: dict[int, Decimal] = {}
            bud_by_acc: dict[int, Decimal] = {}

            for f in act_facts:
                act_by_acc[f.account_id] = act_by_acc.get(f.account_id, Decimal("0")) + f.amount
            for f in bud_facts:
                bud_by_acc[f.account_id] = bud_by_acc.get(f.account_id, Decimal("0")) + f.amount

            all_acc_ids = set(act_by_acc.keys()) | set(bud_by_acc.keys())
            rows = []
            for acc_id in sorted(all_acc_ids):
                acc = accounts.get(acc_id)
                if not acc:
                    continue
                act_val = act_by_acc.get(acc_id, Decimal("0"))
                bud_val = bud_by_acc.get(acc_id, Decimal("0"))
                var_amt = signed_variance(act_val, bud_val)
                var_p = variance_pct(act_val, bud_val)
                fav = classify_favourability(acc.category, var_amt)

                rows.append({
                    "Account Code": acc.code,
                    "Account Name": acc.name,
                    "Category": acc.category.title(),
                    "Actual (€)": float(act_val),
                    "Budget (€)": float(bud_val),
                    "Variance (€)": float(var_amt),
                    "Variance (%)": float(var_p) if var_p is not None else 0.0,
                    "Favourability": fav.value.upper(),
                })

            return pd.DataFrame(rows)

        if session is not None:
            return _fetch(session)
        with get_session() as s:
            return _fetch(s)

    @classmethod
    def get_department_variance_summary(
        cls,
        start_period: Optional[str] = None,
        end_period: Optional[str] = None,
        scenario_name: str = "Actuals",
        compare_scenario: str = "Original Budget",
        session: Optional[Session] = None,
    ) -> pd.DataFrame:
        """
        Department-level summary of Revenue, Expense, Operating Profit, and Variance.
        """
        def _fetch(s: Session) -> pd.DataFrame:
            depts = {d.id: d for d in repo.get_all_departments(s)}
            accounts = {a.id: a for a in repo.get_all_accounts(s)}

            act_facts = repo.get_financial_facts(session=s, scenario_name=scenario_name, start_period=start_period, end_period=end_period)
            bud_facts = repo.get_financial_facts(session=s, scenario_name=compare_scenario, start_period=start_period, end_period=end_period)

            dept_data: dict[int, dict[str, Decimal]] = {}
            for d_id in depts:
                dept_data[d_id] = {
                    "act_rev": Decimal("0"),
                    "act_exp": Decimal("0"),
                    "bud_rev": Decimal("0"),
                    "bud_exp": Decimal("0"),
                }

            for f in act_facts:
                if f.department_id not in dept_data:
                    continue
                acc = accounts.get(f.account_id)
                if acc:
                    if acc.category == "revenue":
                        dept_data[f.department_id]["act_rev"] += f.amount
                    else:
                        dept_data[f.department_id]["act_exp"] += f.amount

            for f in bud_facts:
                if f.department_id not in dept_data:
                    continue
                acc = accounts.get(f.account_id)
                if acc:
                    if acc.category == "revenue":
                        dept_data[f.department_id]["bud_rev"] += f.amount
                    else:
                        dept_data[f.department_id]["bud_exp"] += f.amount

            rows = []
            for d_id, vals in dept_data.items():
                dept = depts[d_id]
                act_p = vals["act_rev"] + vals["act_exp"]
                bud_p = vals["bud_rev"] + vals["bud_exp"]
                p_var = signed_variance(act_p, bud_p)
                p_var_pct = variance_pct(act_p, bud_p)

                rows.append({
                    "Department": dept.name,
                    "Code": dept.code,
                    "Actual Revenue (€)": float(vals["act_rev"]),
                    "Actual Expenses (€)": float(vals["act_exp"]),
                    "Actual Profit (€)": float(act_p),
                    "Budget Profit (€)": float(bud_p),
                    "Profit Variance (€)": float(p_var),
                    "Variance (%)": float(p_var_pct) if p_var_pct is not None else 0.0,
                    "Favourability": classify_favourability("profit", p_var).value.upper(),
                })

            return pd.DataFrame(rows)

        if session is not None:
            return _fetch(session)
        with get_session() as s:
            return _fetch(s)
