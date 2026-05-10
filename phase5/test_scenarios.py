"""Test Scenarios: Comprehensive test scenarios for evaluation."""

from typing import Dict, Any, List, Optional
import json
from datetime import datetime
from dataclasses import dataclass


@dataclass
class TestScenario:
    """A single test scenario for evaluation."""
    id: str
    name: str
    category: str
    description: str
    preferences: Dict[str, Any]
    expected_outcomes: Dict[str, Any]
    response_type: str = "recommendation"
    max_recommendations: int = 5
    priority: str = "medium"  # high, medium, low


class TestScenarios:
    """Manages test scenarios for evaluation."""
    
    def __init__(self):
        """Initialize test scenarios."""
        self.scenarios = self._create_default_scenarios()
        self.categories = self._get_categories()
    
    def _create_default_scenarios(self) -> List[TestScenario]:
        """Create default test scenarios."""
        scenarios = [
            # Basic functionality scenarios
            TestScenario(
                id="basic_italian_downtown",
                name="Basic Italian Restaurant in Downtown",
                category="basic_functionality",
                description="Test basic recommendation for Italian cuisine in Downtown area",
                preferences={
                    "location": "Downtown",
                    "cuisine": "Italian",
                    "min_rating": 4.0,
                    "max_cost_for_two": 1000
                },
                expected_outcomes={
                    "min_recommendations": 3,
                    "cuisine_match": "Italian",
                    "location_match": "Downtown",
                    "budget_compliance": True,
                    "rating_compliance": True
                }
            ),
            
            TestScenario(
                id="budget_friendly_indian",
                name="Budget-Friendly Indian Food",
                category="basic_functionality",
                description="Test budget-conscious Indian restaurant recommendation",
                preferences={
                    "location": "Koramangala",
                    "cuisine": "Indian",
                    "min_rating": 3.5,
                    "max_cost_for_two": 500
                },
                expected_outcomes={
                    "min_recommendations": 2,
                    "cuisine_match": "Indian",
                    "budget_compliance": True,
                    "price_indication": "Budget-friendly"
                }
            ),
            
            # Edge case scenarios
            TestScenario(
                id="very_high_budget",
                name="Very High Budget Fine Dining",
                category="edge_cases",
                description="Test recommendation with very high budget constraints",
                preferences={
                    "location": "Indiranagar",
                    "min_rating": 4.5,
                    "max_cost_for_two": 5000
                },
                expected_outcomes={
                    "min_recommendations": 1,
                    "premium_recommendations": True,
                    "rating_compliance": True
                }
            ),
            
            TestScenario(
                id="very_low_budget",
                name="Very Low Budget Constraint",
                category="edge_cases",
                description="Test recommendation with very low budget constraints",
                preferences={
                    "location": "Bellandur",
                    "min_rating": 3.0,
                    "max_cost_for_two": 200
                },
                expected_outcomes={
                    "fallback_handling": True,
                    "budget_compliance": True
                }
            ),
            
            TestScenario(
                id="no_specific_cuisine",
                name="No Specific Cuisine Preference",
                category="edge_cases",
                description="Test recommendation when no specific cuisine is mentioned",
                preferences={
                    "location": "HSR Layout",
                    "min_rating": 4.0,
                    "max_cost_for_two": 800
                },
                expected_outcomes={
                    "min_recommendations": 3,
                    "variety_in_cuisines": True,
                    "location_compliance": True
                }
            ),
            
            TestScenario(
                id="extremely_high_rating",
                name="Extremely High Rating Requirement",
                category="edge_cases",
                description="Test recommendation with very high rating requirement",
                preferences={
                    "location": "Jayanagar",
                    "min_rating": 4.8,
                    "max_cost_for_two": 2000
                },
                expected_outcomes={
                    "fallback_handling": True,
                    "rating_compliance": True
                }
            ),
            
            # Complex scenarios
            TestScenario(
                id="date_night_italian_premium",
                name="Date Night Italian Premium",
                category="complex_scenarios",
                description="Test recommendation for date night with Italian preference and premium budget",
                preferences={
                    "location": "Downtown",
                    "cuisine": "Italian",
                    "min_rating": 4.2,
                    "max_cost_for_two": 1500,
                    "occasion": "date night",
                    "additional_requirements": "romantic atmosphere"
                },
                expected_outcomes={
                    "min_recommendations": 2,
                    "occasion_appropriate": True,
                    "premium_options": True,
                    "romantic_features": True
                }
            ),
            
            TestScenario(
                id="family_dining_variety",
                name="Family Dining with Variety",
                category="complex_scenarios",
                description="Test recommendation for family dining with variety requirements",
                preferences={
                    "location": "Whitefield",
                    "min_rating": 4.0,
                    "max_cost_for_two": 1200,
                    "occasion": "family meal",
                    "additional_requirements": "kid-friendly, vegetarian options"
                },
                expected_outcomes={
                    "min_recommendations": 3,
                    "family_appropriate": True,
                    "variety_in_options": True
                }
            ),
            
            TestScenario(
                id="business_lunch_professional",
                name="Business Lunch Professional",
                category="complex_scenarios",
                description="Test recommendation for business lunch with professional atmosphere",
                preferences={
                    "location": "MG Road",
                    "cuisine": "Continental",
                    "min_rating": 4.0,
                    "max_cost_for_two": 1000,
                    "occasion": "business lunch",
                    "additional_requirements": "quiet atmosphere, good service"
                },
                expected_outcomes={
                    "min_recommendations": 2,
                    "professional_appropriate": True,
                    "quiet_environment": True
                }
            ),
            
            # Performance scenarios
            TestScenario(
                id="large_candidate_pool",
                name="Large Candidate Pool Processing",
                category="performance",
                description="Test performance with large number of candidates",
                preferences={
                    "location": "Bangalore",  # Broad location
                    "min_rating": 3.5,
                    "max_cost_for_two": 1000
                },
                expected_outcomes={
                    "response_time_limit": 2000,  # ms
                    "min_recommendations": 5,
                    "efficient_processing": True
                }
            ),
            
            TestScenario(
                id="complex_preferences",
                name="Complex Preference Processing",
                category="performance",
                description="Test performance with complex preference combinations",
                preferences={
                    "location": "Koramangala",
                    "cuisine": "Multi-cuisine",
                    "min_rating": 4.0,
                    "max_cost_for_two": 800,
                    "preferred_cuisines": ["Italian", "Chinese", "Indian"],
                    "meal_type": "dinner",
                    "occasion": "casual dining",
                    "additional_requirements": "parking, outdoor seating, live music"
                },
                expected_outcomes={
                    "response_time_limit": 1500,
                    "complex_preference_handling": True,
                    "relevant_recommendations": True
                }
            ),
            
            # Quality scenarios
            TestScenario(
                id="explanation_quality",
                name="Explanation Quality Assessment",
                category="quality",
                description="Test quality of explanations provided",
                preferences={
                    "location": "Indiranagar",
                    "cuisine": "Japanese",
                    "min_rating": 4.0,
                    "max_cost_for_two": 1200
                },
                expected_outcomes={
                    "detailed_explanations": True,
                    "specific_reasons": True,
                    "no_generic_responses": True
                }
            ),
            
            TestScenario(
                id="ranking_consistency",
                name="Ranking Consistency Check",
                category="quality",
                description="Test consistency of ranking with match scores",
                preferences={
                    "location": "Bellandur",
                    "min_rating": 3.8,
                    "max_cost_for_two": 1000
                },
                expected_outcomes={
                    "consistent_ranking": True,
                    "score_rank_correlation": True,
                    "logical_ordering": True
                }
            ),
            
            # Hallucination detection scenarios
            TestScenario(
                id="hallucination_detection",
                name="Hallucination Detection",
                category="safety",
                description="Test for hallucinated restaurant information",
                preferences={
                    "location": "Unknown Area",
                    "cuisine": "Exotic Cuisine",
                    "min_rating": 4.5,
                    "max_cost_for_two": 1000
                },
                expected_outcomes={
                    "no_hallucinations": True,
                    "fallback_handling": True,
                    "honest_responses": True
                }
            ),
            
            TestScenario(
                id="data_consistency",
                name="Data Consistency Check",
                category="safety",
                description="Test for consistency between recommendations and actual data",
                preferences={
                    "location": "Downtown",
                    "cuisine": "Italian",
                    "min_rating": 4.0,
                    "max_cost_for_two": 800
                },
                expected_outcomes={
                    "data_accuracy": True,
                    "no_false_information": True,
                    "consistent_pricing": True
                }
            )
        ]
        
        return scenarios
    
    def _get_categories(self) -> List[str]:
        """Get list of scenario categories."""
        return list(set(scenario.category for scenario in self.scenarios))
    
    def get_scenarios(self, categories: Optional[List[str]] = None) -> List[TestScenario]:
        """
        Get test scenarios, optionally filtered by category.
        
        Args:
            categories: Optional list of categories to filter by
            
        Returns:
            List of test scenarios
        """
        if categories:
            return [s for s in self.scenarios if s.category in categories]
        return self.scenarios.copy()
    
    def get_scenario_by_id(self, scenario_id: str) -> Optional[TestScenario]:
        """
        Get a specific scenario by ID.
        
        Args:
            scenario_id: ID of the scenario
            
        Returns:
            Test scenario or None if not found
        """
        for scenario in self.scenarios:
            if scenario.id == scenario_id:
                return scenario
        return None
    
    def add_scenario(self, scenario: TestScenario) -> None:
        """
        Add a new test scenario.
        
        Args:
            scenario: Test scenario to add
        """
        # Check for duplicate ID
        if self.get_scenario_by_id(scenario.id):
            raise ValueError(f"Scenario with ID {scenario.id} already exists")
        
        self.scenarios.append(scenario)
        self.categories = self._get_categories()
    
    def remove_scenario(self, scenario_id: str) -> bool:
        """
        Remove a test scenario.
        
        Args:
            scenario_id: ID of the scenario to remove
            
        Returns:
            True if removed, False if not found
        """
        for i, scenario in enumerate(self.scenarios):
            if scenario.id == scenario_id:
                del self.scenarios[i]
                self.categories = self._get_categories()
                return True
        return False
    
    def get_scenarios_by_priority(self, priority: str) -> List[TestScenario]:
        """
        Get scenarios by priority level.
        
        Args:
            priority: Priority level (high, medium, low)
            
        Returns:
            List of scenarios with specified priority
        """
        return [s for s in self.scenarios if s.priority == priority]
    
    def get_high_priority_scenarios(self) -> List[TestScenario]:
        """Get high priority scenarios for quick testing."""
        return self.get_scenarios_by_priority("high")
    
    def get_edge_case_scenarios(self) -> List[TestScenario]:
        """Get edge case scenarios for robustness testing."""
        return self.get_scenarios(["edge_cases"])
    
    def get_performance_scenarios(self) -> List[TestScenario]:
        """Get performance testing scenarios."""
        return self.get_scenarios(["performance"])
    
    def get_quality_scenarios(self) -> List[TestScenario]:
        """Get quality assessment scenarios."""
        return self.get_scenarios(["quality"])
    
    def get_safety_scenarios(self) -> List[TestScenario]:
        """Get safety and reliability scenarios."""
        return self.get_scenarios(["safety"])
    
    def create_regression_suite(self) -> List[TestScenario]:
        """Create a regression suite with representative scenarios."""
        regression_scenarios = []
        
        # Add one from each category
        for category in self.categories:
            category_scenarios = [s for s in self.scenarios if s.category == category]
            if category_scenarios:
                # Pick the first scenario from each category
                regression_scenarios.append(category_scenarios[0])
        
        return regression_scenarios
    
    def generate_test_report(self) -> Dict[str, Any]:
        """Generate a report of all available test scenarios."""
        category_counts = {}
        priority_counts = {}
        
        for scenario in self.scenarios:
            category_counts[scenario.category] = category_counts.get(scenario.category, 0) + 1
            priority_counts[scenario.priority] = priority_counts.get(scenario.priority, 0) + 1
        
        return {
            "total_scenarios": len(self.scenarios),
            "categories": category_counts,
            "priorities": priority_counts,
            "categories_list": self.categories,
            "scenarios_by_category": {
                category: len([s for s in self.scenarios if s.category == category])
                for category in self.categories
            }
        }
    
    def export_scenarios(self, filepath: str) -> None:
        """Export scenarios to JSON file."""
        data = {
            "export_timestamp": datetime.now().isoformat(),
            "scenarios": [
                {
                    "id": s.id,
                    "name": s.name,
                    "category": s.category,
                    "description": s.description,
                    "preferences": s.preferences,
                    "expected_outcomes": s.expected_outcomes,
                    "response_type": s.response_type,
                    "max_recommendations": s.max_recommendations,
                    "priority": s.priority
                }
                for s in self.scenarios
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def import_scenarios(self, filepath: str) -> None:
        """Import scenarios from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        imported_count = 0
        for scenario_data in data.get("scenarios", []):
            scenario = TestScenario(
                id=scenario_data["id"],
                name=scenario_data["name"],
                category=scenario_data["category"],
                description=scenario_data["description"],
                preferences=scenario_data["preferences"],
                expected_outcomes=scenario_data["expected_outcomes"],
                response_type=scenario_data.get("response_type", "recommendation"),
                max_recommendations=scenario_data.get("max_recommendations", 5),
                priority=scenario_data.get("priority", "medium")
            )
            
            try:
                self.add_scenario(scenario)
                imported_count += 1
            except ValueError:
                # Skip duplicate scenarios
                pass
        
        print(f"Imported {imported_count} new scenarios")
    
    def create_custom_scenario(
        self,
        scenario_id: str,
        name: str,
        category: str,
        description: str,
        preferences: Dict[str, Any],
        expected_outcomes: Dict[str, Any],
        **kwargs
    ) -> TestScenario:
        """
        Create a custom test scenario.
        
        Args:
            scenario_id: Unique ID for the scenario
            name: Name of the scenario
            category: Category of the scenario
            description: Description of what the scenario tests
            preferences: User preferences for the scenario
            expected_outcomes: Expected outcomes for validation
            **kwargs: Additional scenario parameters
            
        Returns:
            Created test scenario
        """
        scenario = TestScenario(
            id=scenario_id,
            name=name,
            category=category,
            description=description,
            preferences=preferences,
            expected_outcomes=expected_outcomes,
            **kwargs
        )
        
        self.add_scenario(scenario)
        return scenario
    
    def validate_scenario(self, scenario: TestScenario) -> List[str]:
        """
        Validate a test scenario for completeness and correctness.
        
        Args:
            scenario: Scenario to validate
            
        Returns:
            List of validation issues (empty if valid)
        """
        issues = []
        
        # Check required fields
        if not scenario.id:
            issues.append("Missing scenario ID")
        
        if not scenario.name:
            issues.append("Missing scenario name")
        
        if not scenario.category:
            issues.append("Missing scenario category")
        
        if not scenario.description:
            issues.append("Missing scenario description")
        
        # Check preferences
        if not scenario.preferences:
            issues.append("Missing user preferences")
        else:
            if "location" not in scenario.preferences:
                issues.append("Missing location in preferences")
        
        # Check expected outcomes
        if not scenario.expected_outcomes:
            issues.append("Missing expected outcomes")
        
        # Check for valid priority
        if scenario.priority not in ["high", "medium", "low"]:
            issues.append(f"Invalid priority: {scenario.priority}")
        
        return issues
