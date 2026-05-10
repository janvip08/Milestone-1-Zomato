"""Schema mapping utilities for Phase 1."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List


@dataclass(frozen=True)
class CanonicalRestaurant:
    """Canonical fields used by downstream phases."""

    name: str
    location: str
    cuisines: str
    cost_for_two: float | None
    rating: float | None


class SchemaMapper:
    """Map raw records with varying keys into canonical schema."""

    KEY_ALIASES: Dict[str, List[str]] = {
        "name": ["restaurant_name", "name", "title"],
        "location": ["location", "city", "locality"],
        "cuisines": ["cuisines", "cuisine", "food_type"],
        "cost_for_two": ["cost_for_two", "average_cost_for_two", "cost", "price"],
        "rating": ["rating", "aggregate_rating", "user_rating"],
    }

    def map_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Convert one raw record into canonical dict fields."""
        mapped: Dict[str, Any] = {}
        for canonical_key, aliases in self.KEY_ALIASES.items():
            mapped[canonical_key] = self._first_present(record, aliases)
        return mapped

    def map_records(self, records: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert many records into canonical dict fields."""
        return [self.map_record(record) for record in records]

    @staticmethod
    def _first_present(record: Dict[str, Any], keys: Iterable[str]) -> Any:
        for key in keys:
            if key in record:
                return record[key]
        return None

