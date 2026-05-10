"""Phase 2 recommendation pipeline (non-LLM baseline)."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List

from phase2.filter_engine import FilterEngine
from phase2.preference_parser import PreferenceParser
from phase2.ranker_v1 import RankerV1


class Phase2Pipeline:
    """Orchestrates preference parsing, filtering, and baseline ranking."""

    def __init__(self) -> None:
        self.preference_parser = PreferenceParser()
        self.filter_engine = FilterEngine()
        self.ranker = RankerV1()

    def run(self, preferences: Dict[str, Any], dataset_csv_path: str) -> List[Dict[str, Any]]:
        rows = self._load_rows(dataset_csv_path)
        parsed_preferences = self.preference_parser.parse(preferences)
        filtered = self.filter_engine.filter(rows, parsed_preferences)
        return self.ranker.rank(filtered, parsed_preferences)

    @staticmethod
    def _load_rows(dataset_csv_path: str) -> List[Dict[str, Any]]:
        path = Path(dataset_csv_path)
        if not path.exists():
            raise FileNotFoundError(f"Dataset file not found: {dataset_csv_path}")
        with path.open("r", encoding="utf-8", newline="") as handle:
            return [dict(row) for row in csv.DictReader(handle)]

