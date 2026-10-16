"""
Data adapter between relational database (PostgreSQL/SQLite) and TinyOlap multidimensional cube.
Hydrates cube cells from financial facts and provides query abstractions.
"""
from __future__ import annotations

import logging
import time
from typing import Optional

from sqlalchemy.orm import Session
from tinyolap.cube import Cube
from tinyolap.database import Database

from database import repository as repo
from database.connection import get_session
from olap.model import create_olap_database

logger = logging.getLogger(__name__)


class OlapAdapter:
    """Synchronises relational database facts with the in-memory TinyOlap cube."""

    def __init__(self, db: Optional[Database] = None):
        self.db = db or create_olap_database()
        self.cube: Cube = self.db.cubes["Financials"]
        self.last_sync_time: Optional[float] = None
        self.fact_count: int = 0

    def sync_from_database(self, session: Optional[Session] = None) -> int:
        """
        Load all financial facts from the relational database into the cube.
        Returns the number of cells populated.
        """
        start = time.monotonic()

        def _sync(s: Session) -> int:
            depts = {d.id: d.code for d in repo.get_all_departments(s)}
            accounts = {a.id: a.code for a in repo.get_all_accounts(s)}
            periods = {p.id: p.period_key for p in repo.get_all_periods(s)}
            scenarios = {sc.id: sc.name for sc in repo.get_all_scenarios(s)}

            facts = repo.get_financial_facts(session=s)
            loaded = 0

            for f in facts:
                acc_code = accounts.get(f.account_id)
                dept_code = depts.get(f.department_id)
                period_key = periods.get(f.period_id)
                scenario_name = scenarios.get(f.scenario_id)

                if acc_code and dept_code and period_key and scenario_name:
                    try:
                        self.cube[acc_code, dept_code, period_key, scenario_name] = float(f.amount)
                        loaded += 1
                    except Exception as e:
                        logger.debug("Could not populate cell (%s, %s, %s, %s): %s", acc_code, dept_code, period_key, scenario_name, e)

            self.fact_count = loaded
            self.last_sync_time = time.time()
            duration_ms = int((time.monotonic() - start) * 1000)
            logger.info("Synchronised %d facts to TinyOlap cube in %d ms", loaded, duration_ms)
            return loaded

        if session is not None:
            return _sync(session)
        with get_session() as s:
            return _sync(s)

    def get_cell(self, account: str, department: str, period: str, scenario: str) -> float:
        """Query a single cell value from the cube (leaf, consolidation, or rule)."""
        try:
            val = self.cube[account, department, period, scenario]
            return float(val) if val is not None else 0.0
        except Exception as e:
            logger.error("Error reading cell (%s, %s, %s, %s): %s", account, department, period, scenario, e)
            return 0.0
