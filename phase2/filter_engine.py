"""Filtering engine for Phase 2."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List

from phase2.preference_parser import UserPreferences


class FilterEngine:
    """Apply deterministic preference-based filtering."""

    def filter(self, rows: Iterable[Dict[str, Any]], prefs: UserPreferences) -> List[Dict[str, Any]]:
        filtered = list(rows)

        if prefs.location:
            filtered = [row for row in filtered if self._matches_location(row, prefs.location)]

        if prefs.cuisine:
            filtered = [row for row in filtered if self._matches_cuisine(row, prefs.cuisine)]

        if prefs.min_rating is not None:
            filtered = [row for row in filtered if self._get_float(row.get("rating")) is not None and self._get_float(row.get("rating")) >= prefs.min_rating]

        if prefs.budget:
            filtered = [row for row in filtered if self._matches_budget(row, prefs.budget)]

        return filtered

    @staticmethod
    def _matches_location(row: Dict[str, Any], location: str) -> bool:
        return str(row.get("location", "")).strip().lower() == location

    @staticmethod
    def _matches_cuisine(row: Dict[str, Any], cuisine: str) -> bool:
        cuisines = str(row.get("cuisines", "")).strip().lower()
        return cuisine in cuisines

    def _matches_budget(self, row: Dict[str, Any], budget: str) -> bool:
        cost = self._get_float(row.get("cost_for_two"))
        if cost is None:
            return False

        # Simple default budget bands for baseline ranking.
        if budget == "low":
            return cost <= 800
        if budget == "medium":
            return 801 <= cost <= 1800
        return cost > 1800

    @staticmethod
    def _get_float(value: Any) -> float | None:
        if value is None or value == "":
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

