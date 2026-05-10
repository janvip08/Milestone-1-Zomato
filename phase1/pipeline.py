"""Phase 1 pipeline runner."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from phase1.dataset_loader import DatasetLoader
from phase1.preprocessor import Preprocessor
from phase1.schema_mapper import SchemaMapper


class Phase1Pipeline:
    """Orchestrates ingestion, schema mapping, preprocessing, and storage."""

    def __init__(self) -> None:
        self.loader = DatasetLoader()
        self.mapper = SchemaMapper()
        self.preprocessor = Preprocessor()

    def run_with_local_file(
        self, input_file: str, output_dir: str = "phase1/output"
    ) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
        raw_records = self.loader.load_local(input_file)
        mapped_records = self.mapper.map_records(raw_records)
        cleaned_records, quality_summary = self.preprocessor.process(mapped_records)
        self._persist_outputs(cleaned_records, quality_summary, output_dir)
        return cleaned_records, quality_summary

    def run_with_huggingface(
        self,
        dataset_name: str = "ManikaSaini/zomato-restaurant-recommendation",
        split: str = "train",
        limit: int | None = 1000,
        output_dir: str = "phase1/output",
    ) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
        raw_records = self.loader.load_huggingface(dataset_name=dataset_name, split=split, limit=limit)
        mapped_records = self.mapper.map_records(raw_records)
        cleaned_records, quality_summary = self.preprocessor.process(mapped_records)
        self._persist_outputs(cleaned_records, quality_summary, output_dir)
        return cleaned_records, quality_summary

    @staticmethod
    def _persist_outputs(
        cleaned_records: List[Dict[str, Any]],
        quality_summary: Dict[str, int],
        output_dir: str,
    ) -> None:
        target = Path(output_dir)
        target.mkdir(parents=True, exist_ok=True)

        processed_json = target / "processed_dataset.json"
        processed_csv = target / "processed_dataset.csv"
        quality_report = target / "data_quality_report.json"
        dictionary_file = target / "data_dictionary.md"

        processed_json.write_text(
            json.dumps(cleaned_records, ensure_ascii=True, indent=2),
            encoding="utf-8",
        )

        with processed_csv.open("w", encoding="utf-8", newline="") as handle:
            fieldnames = ["name", "location", "cuisines", "cost_for_two", "rating"]
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for row in cleaned_records:
                writer.writerow(row)

        quality_report.write_text(
            json.dumps(quality_summary, ensure_ascii=True, indent=2),
            encoding="utf-8",
        )

        dictionary_file.write_text(
            "\n".join(
                [
                    "## Data Dictionary (Phase 1)",
                    "",
                    "- `name`: Restaurant name (string)",
                    "- `location`: Normalized city/location (lowercase string)",
                    "- `cuisines`: Comma-separated cuisine tags (lowercase string)",
                    "- `cost_for_two`: Numeric cost estimate for two people (float, nullable)",
                    "- `rating`: Numeric rating on 0-5 scale (float, nullable)",
                ]
            ),
            encoding="utf-8",
        )

