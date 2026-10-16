"""
CLI script to verify database connectivity, table row counts, and TinyOlap model health.
Usage:
    python scripts/health_check.py
"""
from __future__ import annotations

import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import repository as repo
from database.connection import check_connection, get_session
from olap.cache import get_olap_adapter


def main():
    print("=" * 60)
    print("  NORTHSTAR FINANCIAL ENGINE — SYSTEM HEALTH CHECK")
    print("=" * 60)

    # 1. Database Connectivity
    db_status = check_connection()
    print(f"\n[Database Status] : {db_status.get('status', 'unknown').upper()}")
    print(f"  Dialect         : {db_status.get('dialect', 'unknown')}")
    print(f"  Server Version  : {db_status.get('server_version', 'unknown')}")

    if db_status.get("status") != "connected":
        print("\nERROR: Database is disconnected. Exiting with failure.")
        sys.exit(1)

    # 2. Table Row Counts
    with get_session() as s:
        counts = repo.get_table_counts(s)
        print("\n[Table Record Counts]")
        for table, cnt in counts.items():
            print(f"  {table:<25} : {cnt:>8,}")

    # 3. TinyOlap Status
    try:
        adapter = get_olap_adapter()
        print(f"\n[TinyOlap OLAP Cube Status] : ONLINE")
        print(f"  Cube Name       : {adapter.cube.name}")
        print(f"  Fact Count      : {adapter.fact_count:,}")
        rev = adapter.get_cell("REV", "COMPANY", "2024-01", "Actuals")
        profit = adapter.get_cell("Operating Profit", "COMPANY", "2024-01", "Actuals")
        print(f"  Sample Cell     : 2024-01 Company Actuals Revenue = € {rev:,.2f}, Profit = € {profit:,.2f}")
    except Exception as e:
        print(f"\n[TinyOlap Status] : ERROR ({e})")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("  ALL SYSTEMS OPERATIONAL (HEALTH CHECK PASSED)")
    print("=" * 60)


if __name__ == "__main__":
    main()
