"""Dataset ingestion layer for Phase 1."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class DatasetLoader:
    """Load restaurant records from local files or Hugging Face."""

    def load_local(self, file_path: str) -> List[Dict[str, Any]]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Dataset file not found: {file_path}")

        if path.suffix.lower() == ".json":
            return self._load_json(path)
        if path.suffix.lower() == ".csv":
            return self._load_csv(path)
        raise ValueError("Unsupported file format. Use .csv or .json.")

    def load_huggingface(
        self,
        dataset_name: str = "ManikaSaini/zomato-restaurant-recommendation",
        split: str = "train",
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Load records from Hugging Face datasets, if dependency is available."""
        try:
            from datasets import load_dataset
        except ImportError as exc:
            raise ImportError(
                "Install `datasets` package to load from Hugging Face: pip install datasets"
            ) from exc

        ds = load_dataset(dataset_name, split=split)
        if limit is not None:
            ds = ds.select(range(min(limit, len(ds))))
        return [dict(row) for row in ds]

    @staticmethod
    def _load_json(path: Path) -> List[Dict[str, Any]]:
        content = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(content, list):
            return [dict(row) for row in content]
        if isinstance(content, dict) and "data" in content and isinstance(content["data"], list):
            return [dict(row) for row in content["data"]]
        raise ValueError("JSON format must be a list of objects or {'data': [...]} format.")

    @staticmethod
    def _load_csv(path: Path) -> List[Dict[str, Any]]:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            return [dict(row) for row in reader]

