"""CLI entry point for Phase 2 baseline recommendation engine."""

from __future__ import annotations

import argparse
import json

from phase2.pipeline import Phase2Pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Phase 2 baseline recommendation pipeline.")
    parser.add_argument("--dataset", default="phase1/output/processed_dataset.csv", help="Path to processed CSV data from Phase 1.")
    parser.add_argument("--location", default="bangalore")
    parser.add_argument("--budget", default="medium")
    parser.add_argument("--cuisine", default="north indian")
    parser.add_argument("--min-rating", type=float, default=3.5)
    parser.add_argument("--top-n", type=int, default=5)
    args = parser.parse_args()

    preferences = {
        "location": args.location,
        "budget": args.budget,
        "cuisine": args.cuisine,
        "min_rating": args.min_rating,
        "top_n": args.top_n,
    }

    pipeline = Phase2Pipeline()
    recommendations = pipeline.run(preferences, dataset_csv_path=args.dataset)

    print(json.dumps(recommendations, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()

