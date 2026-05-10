"""Tests for Phase 2 preference parsing, filtering, and ranking."""

from phase2.filter_engine import FilterEngine
from phase2.preference_parser import PreferenceParser
from phase2.ranker_v1 import RankerV1


def test_preference_parser_normalizes_and_validates() -> None:
    parser = PreferenceParser()
    prefs = parser.parse(
        {
            "location": " Bangalore ",
            "budget": "MEDIUM",
            "cuisine": " North Indian ",
            "min_rating": 4.0,
            "top_n": 3,
        }
    )
    assert prefs.location == "bangalore"
    assert prefs.budget == "medium"
    assert prefs.cuisine == "north indian"
    assert prefs.top_n == 3


def test_filter_engine_applies_constraints() -> None:
    rows = [
        {"name": "A", "location": "bangalore", "cuisines": "north indian", "cost_for_two": "1200", "rating": "4.2"},
        {"name": "B", "location": "delhi", "cuisines": "north indian", "cost_for_two": "1200", "rating": "4.5"},
        {"name": "C", "location": "bangalore", "cuisines": "chinese", "cost_for_two": "700", "rating": "4.3"},
    ]
    prefs = PreferenceParser().parse(
        {"location": "bangalore", "budget": "medium", "cuisine": "north indian", "min_rating": 4.0}
    )
    filtered = FilterEngine().filter(rows, prefs)
    assert len(filtered) == 1
    assert filtered[0]["name"] == "A"


def test_ranker_returns_top_n_sorted() -> None:
    rows = [
        {"name": "A", "location": "bangalore", "cuisines": "north indian", "cost_for_two": "1200", "rating": "4.1"},
        {"name": "B", "location": "bangalore", "cuisines": "north indian", "cost_for_two": "1300", "rating": "4.6"},
        {"name": "C", "location": "bangalore", "cuisines": "north indian", "cost_for_two": "1100", "rating": "3.8"},
    ]
    prefs = PreferenceParser().parse(
        {"location": "bangalore", "budget": "medium", "cuisine": "north indian", "min_rating": 3.0, "top_n": 2}
    )
    ranked = RankerV1().rank(rows, prefs)
    assert len(ranked) == 2
    assert ranked[0]["name"] == "B"

