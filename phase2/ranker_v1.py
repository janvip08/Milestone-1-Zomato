"""Baseline deterministic ranker for Phase 2."""

from __future__ import annotations

from typing import Any, Dict, List

from phase2.preference_parser import UserPreferences


class RankerV1:
    """Compute simple deterministic score and return Top-N rows."""

    def rank(self, rows: List[Dict[str, Any]], prefs: UserPreferences) -> List[Dict[str, Any]]:
        scored_rows: List[Dict[str, Any]] = []
        for row in rows:
            score = self._score_row(row, prefs)
            item = dict(row)
            item["score"] = round(score, 4)
            scored_rows.append(item)

        scored_rows.sort(
            key=lambda r: (
                -r["score"],
                -(self._to_float(r.get("rating")) or 0.0),
                self._to_float(r.get("cost_for_two")) or float("inf"),
                str(r.get("name", "")),
            )
        )
        return scored_rows[: prefs.top_n]

    def _score_row(self, row: Dict[str, Any], prefs: UserPreferences) -> float:
        rating = self._to_float(row.get("rating")) or 0.0
        cost = self._to_float(row.get("cost_for_two"))
        cuisines = str(row.get("cuisines", "")).lower()
        location = str(row.get("location", "")).lower()

        score = rating * 2.0

        if prefs.cuisine and prefs.cuisine in cuisines:
            score += 1.5
        if prefs.location and prefs.location == location:
            score += 1.0

        if prefs.budget and cost is not None:
            if prefs.budget == "low" and cost <= 800:
                score += 1.0
            elif prefs.budget == "medium" and 801 <= cost <= 1800:
                score += 1.0
            elif prefs.budget == "high" and cost > 1800:
                score += 1.0

        return score

    @staticmethod
    def _to_float(value: Any) -> float | None:
        if value is None or value == "":
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

