"""
CLI script to run database migrations or initialise tables.
Usage:
    python scripts/run_migrations.py [--init]
"""
from __future__ import annotations

import argparse
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import init_database


def main():
    parser = argparse.ArgumentParser(description="Run database migrations or table initialisation.")
    parser.add_argument("--database-url", default=None, help="Database connection URL override")
    args = parser.parse_args()

    print("Initialising database tables...")
    init_database(args.database_url)
    print("Database tables initialised successfully.")


if __name__ == "__main__":
    main()
