#!/usr/bin/env python3
"""
Seed script to import drug interaction data into HealthRevo DB.

Usage examples:
  python backend/scripts/seed_drug_interactions.py --csv backend/data/drug_interactions.csv --replace
  python backend/scripts/seed_drug_interactions.py --sqlite /path/to/source.db --table interactions --replace
"""
from __future__ import annotations

import argparse
from pathlib import Path

from app.utils.data_loader import (
    load_drug_interactions_from_csv,
    load_drug_interactions_from_sqlite,
    load_drug_interactions_from_medi_co_dataset,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed drug interactions into DB")
    parser.add_argument("--csv", type=str, help="Path to CSV file")
    parser.add_argument("--sqlite", type=str, help="Path to external SQLite file")
    parser.add_argument("--table", type=str, default="drug_interactions", help="Table name in external SQLite")
    parser.add_argument("--medi_co_csv", type=str, help="Path to medi-co dataset CSV (e.g., dataset/data_final_v5.csv)")
    parser.add_argument("--medi_co_synonyms", type=str, help="Path to medi-co synonyms JSON (e.g., dataset/drugs_synonyms.json)")
    parser.add_argument("--replace", action="store_true", help="Replace existing interactions")
    args = parser.parse_args()

    if not args.csv and not args.sqlite and not (args.medi_co_csv and args.medi_co_synonyms):
        parser.error("Provide one of: --csv or --sqlite or --medi_co_csv + --medi_co_synonyms")

    if args.csv:
        count = load_drug_interactions_from_csv(args.csv, replace=args.replace)
        print(f"Imported {count} rows from CSV")
    elif args.sqlite:
        count = load_drug_interactions_from_sqlite(args.sqlite, table=args.table, replace=args.replace)
        print(f"Imported {count} rows from SQLite table {args.table}")
    else:
        count = load_drug_interactions_from_medi_co_dataset(args.medi_co_csv, args.medi_co_synonyms, replace=args.replace)
        print(f"Imported {count} rows from medi-co dataset")


if __name__ == "__main__":
    main()
