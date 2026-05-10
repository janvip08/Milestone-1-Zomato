"""Preference parser for Phase 2."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class UserPreferences:
    """Canonical user preference model."""

    location: str | None = None
    budget: str | None = None
    cuisine: str | None = None
    min_rating: float | None = None
    additional_constraints: str | None = None
    top_n: int = 5


class PreferenceParser:
    """Validate and normalize user input preferences."""

    BUDGET_VALUES = {"low", "medium", "high"}

    def parse(self, payload: Dict[str, Any]) -> UserPreferences:
        location = self._normalize_optional_text(payload.get("location"))
        budget = self._normalize_optional_text(payload.get("budget"))
        cuisine = self._normalize_optional_text(payload.get("cuisine"))
        additional_constraints = self._normalize_optional_text(payload.get("additional_constraints"))

        if budget is not None and budget not in self.BUDGET_VALUES:
            raise ValueError("budget must be one of: low, medium, high")

        min_rating_raw = payload.get("min_rating")
        min_rating = None
        if min_rating_raw is not None and min_rating_raw != "":
            min_rating = float(min_rating_raw)
            if min_rating < 0 or min_rating > 5:
                raise ValueError("min_rating must be between 0 and 5")

        top_n = int(payload.get("top_n", 5))
        if top_n < 1:
            raise ValueError("top_n must be >= 1")

        if not location and not budget and not cuisine and min_rating is None:
            raise ValueError("At least one preference should be provided.")

        return UserPreferences(
            location=location,
            budget=budget,
            cuisine=cuisine,
            min_rating=min_rating,
            additional_constraints=additional_constraints,
            top_n=top_n,
        )

    @staticmethod
    def _normalize_optional_text(value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip().lower()
        return text or None

