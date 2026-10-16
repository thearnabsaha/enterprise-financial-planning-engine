"""
CLI script to initialise and seed the database.
Usage:
    python scripts/seed_database.py [--sample-dir data/sample] [--database-url URL]
"""
from __future__ import annotations

import argparse
import logging
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.seed import seed_database

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("seed_database")


def main():
    parser = argparse.ArgumentParser(description="Seed Northstar financial planning database.")
    parser.add_argument("--sample-dir", default="data/sample", help="Path to sample data CSVs")
    parser.add_argument("--database-url", default=None, help="Database connection URL override")
    args = parser.parse_args()

    logger.info("Starting database seeding...")
    result = seed_database(database_url=args.database_url, sample_dir=args.sample_dir)
    logger.info("Database seeding finished successfully: %s", result)


if __name__ == "__main__":
    main()
