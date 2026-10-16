"""
CLI script for generating synthetic data.
Usage: python scripts/generate_data.py [--seed 42] [--output data/sample]
"""
import argparse
import logging
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_generator.generator import DataGenerator


def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic financial data for Northstar Digital Services GmbH"
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for reproducible generation (default: 42)",
    )
    parser.add_argument(
        "--output", type=str, default="data/sample",
        help="Output directory (default: data/sample)",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    print(f"\n{'='*60}")
    print("  Northstar Digital Services GmbH")
    print("  Synthetic Financial Data Generator")
    print(f"{'='*60}")
    print(f"  Seed:   {args.seed}")
    print(f"  Output: {args.output}")
    print(f"{'='*60}\n")

    generator = DataGenerator(seed=args.seed)
    files = generator.generate_all(output_dir=args.output)

    print(f"\n✅ Generated {len(files)} files:")
    for name, path in files.items():
        size = os.path.getsize(path)
        print(f"   {name:30s} {size:>10,} bytes")

    print(f"\nAll files written to: {args.output}")
    print("Use --seed to reproduce the exact same dataset.\n")


if __name__ == "__main__":
    main()
