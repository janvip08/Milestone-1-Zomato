"""Data cleaning and normalization for Phase 1."""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Tuple


class Preprocessor:
    """Normalize location, cuisine, cost, and rating fields."""

    CITY_ALIASES = {
        "bengaluru": "bangalore",
        "blr": "bangalore",
        "new delhi": "delhi",
        "ncr": "delhi",
    }

    def process(self, records: Iterable[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
        """Return cleaned records and a minimal quality summary."""
        source_records = list(records)
        cleaned: List[Dict[str, Any]] = []
        missing_required = 0
        dropped_invalid = 0

        for record in source_records:
            normalized = self._normalize_record(record)
            if not normalized["name"] or not normalized["location"] or not normalized["cuisines"]:
                missing_required += 1
                continue

            rating = normalized["rating"]
            if rating is not None and (rating < 0 or rating > 5):
                dropped_invalid += 1
                continue

            cleaned.append(normalized)

        summary = {
            "input_count": len(source_records),
            "cleaned_count": len(cleaned),
            "dropped_missing_required": missing_required,
            "dropped_invalid_rating": dropped_invalid,
        }
        return cleaned, summary

    def _normalize_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "name": self._normalize_text(record.get("name")),
            "location": self._normalize_location(record.get("location")),
            "cuisines": self._normalize_cuisines(record.get("cuisines")),
            "cost_for_two": self._parse_cost(record.get("cost_for_two")),
            "rating": self._parse_rating(record.get("rating")),
        }

    @staticmethod
    def _normalize_text(value: Any) -> str:
        if value is None:
            return ""
        return str(value).strip()

    def _normalize_location(self, value: Any) -> str:
        text = self._normalize_text(value).lower()
        return self.CITY_ALIASES.get(text, text)

    @staticmethod
    def _normalize_cuisines(value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, list):
            items = [str(item).strip().lower() for item in value if str(item).strip()]
            return ", ".join(items)
        parts = [p.strip().lower() for p in str(value).split(",") if p.strip()]
        return ", ".join(parts)

    @staticmethod
    def _parse_cost(value: Any) -> float | None:
        if value is None:
            return None
        text = str(value)
        digits = re.findall(r"\d+(?:\.\d+)?", text.replace(",", ""))
        if not digits:
            return None
        return float(digits[0])

    @staticmethod
    def _parse_rating(value: Any) -> float | None:
        if value is None:
            return None
        text = str(value).strip().lower()
        if text in {"new", "-", "na", "n/a", ""}:
            return None
        match = re.search(r"\d+(?:\.\d+)?", text)
        if not match:
            return None
        return float(match.group(0))

