"""Basic tests for Phase 1 data pipeline."""

from phase1.preprocessor import Preprocessor
from phase1.schema_mapper import SchemaMapper


def test_schema_mapper_maps_alias_fields() -> None:
    mapper = SchemaMapper()
    mapped = mapper.map_record(
        {
            "restaurant_name": "A",
            "city": "Bengaluru",
            "cuisine": "Italian",
            "cost": "500",
            "aggregate_rating": "4.1/5",
        }
    )
    assert mapped["name"] == "A"
    assert mapped["location"] == "Bengaluru"
    assert mapped["cuisines"] == "Italian"


def test_preprocessor_normalizes_and_drops_missing_name() -> None:
    preprocessor = Preprocessor()
    cleaned, summary = preprocessor.process(
        [
            {
                "name": "Test Place",
                "location": "BLR",
                "cuisines": "North Indian, Chinese",
                "cost_for_two": "Rs. 800",
                "rating": "4.4/5",
            },
            {
                "name": "",
                "location": "Delhi",
                "cuisines": "Italian",
                "cost_for_two": "600",
                "rating": "4.0",
            },
        ]
    )
    assert len(cleaned) == 1
    assert cleaned[0]["location"] == "bangalore"
    assert summary["dropped_missing_required"] == 1

