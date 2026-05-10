"""CLI entry point for Phase 1 pipeline."""

from __future__ import annotations

import argparse
from pathlib import Path

from phase1.pipeline import Phase1Pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Phase 1 data ingestion and preprocessing pipeline.")
    parser.add_argument(
        "--input-file",
        default="phase1/data/sample_restaurants.json",
        help="Local dataset path (.json or .csv).",
    )
    parser.add_argument(
        "--output-dir",
        default="phase1/output",
        help="Directory where processed outputs are stored.",
    )
    args = parser.parse_args()

    pipeline = Phase1Pipeline()
    cleaned, summary = pipeline.run_with_local_file(args.input_file, args.output_dir)

    print(f"Phase 1 pipeline completed. Cleaned rows: {len(cleaned)}")
    print(f"Quality summary saved in: {Path(args.output_dir).resolve()}")
    print(summary)


if __name__ == "__main__":
    main()

