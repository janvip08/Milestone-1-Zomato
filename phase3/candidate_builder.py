"""Candidate Builder: Formats filtered restaurant data for LLM context."""

from typing import List, Dict, Any, Optional
import json


class CandidateBuilder:
    """Builds structured context from filtered restaurant candidates for LLM processing."""
    
    def __init__(self, max_candidates: int = 10):
        """
        Initialize the CandidateBuilder.
        
        Args:
            max_candidates: Maximum number of candidates to include in context
        """
        self.max_candidates = max_candidates
    
    def build_context(
        self, 
        candidates: List[Dict[str, Any]], 
        user_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build structured context from candidates and user preferences.
        
        Args:
            candidates: List of restaurant dictionaries from Phase 2 filtering
            user_preferences: User preference dictionary
            
        Returns:
            Structured context dictionary for LLM prompting
        """
        # Limit candidates to max_candidates
        limited_candidates = candidates[:self.max_candidates]
        
        # Format each candidate with key information
        formatted_candidates = []
        for i, candidate in enumerate(limited_candidates, 1):
            formatted_candidate = {
                "rank": i,
                "name": candidate.get("name", "Unknown"),
                "cuisine": self._format_cuisine(candidate.get("cuisine", "")),
                "rating": self._format_rating(candidate.get("rating", 0)),
                "cost_for_two": self._format_cost(candidate.get("cost_for_two", 0)),
                "location": candidate.get("location", "Unknown"),
                "highlights": self._extract_highlights(candidate)
            }
            formatted_candidates.append(formatted_candidate)
        
        # Build complete context
        context = {
            "user_preferences": self._summarize_preferences(user_preferences),
            "candidates": formatted_candidates,
            "total_candidates": len(limited_candidates),
            "context_summary": self._create_summary(
                user_preferences, len(limited_candidates)
            )
        }
        
        return context
    
    def _format_cuisine(self, cuisine: str) -> str:
        """Format cuisine string for better readability."""
        if not cuisine:
            return "Various"
        return cuisine.title()
    
    def _format_rating(self, rating: Any) -> str:
        """Format rating for display."""
        try:
            rating_float = float(rating)
            return f"{rating_float:.1f}/5.0"
        except (ValueError, TypeError):
            return "Not rated"
    
    def _format_cost(self, cost: Any) -> str:
        """Format cost for display."""
        try:
            cost_int = int(cost)
            if cost_int == 0:
                return "Price not available"
            return f"₹{cost_int} for two"
        except (ValueError, TypeError):
            return "Price not available"
    
    def _extract_highlights(self, candidate: Dict[str, Any]) -> List[str]:
        """Extract key highlights from candidate data."""
        highlights = []
        
        # Add rating highlight if good
        try:
            rating = float(candidate.get("rating", 0))
            if rating >= 4.5:
                highlights.append("Excellent rating")
            elif rating >= 4.0:
                highlights.append("Good rating")
        except (ValueError, TypeError):
            pass
        
        # Add cost highlight
        try:
            cost = int(candidate.get("cost_for_two", 0))
            if cost > 0 and cost <= 500:
                highlights.append("Budget-friendly")
            elif cost > 0 and cost <= 1000:
                highlights.append("Moderate pricing")
            elif cost > 1000:
                highlights.append("Premium dining")
        except (ValueError, TypeError):
            pass
        
        # Add other features if available
        if candidate.get("delivery"):
            highlights.append("Delivery available")
        if candidate.get("takeaway"):
            highlights.append("Takeaway available")
        
        return highlights
    
    def _summarize_preferences(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Create a clean summary of user preferences."""
        summary = {}
        
        # Key preference fields
        key_fields = [
            "location", "cuisine", "min_rating", "max_cost_for_two", 
            "preferred_cuisines", "budget_category", "meal_type"
        ]
        
        for field in key_fields:
            if field in preferences and preferences[field] is not None:
                summary[field] = preferences[field]
        
        return summary
    
    def _create_summary(self, preferences: Dict[str, Any], candidate_count: int) -> str:
        """Create a human-readable summary of the context."""
        location = preferences.get("location", "your area")
        cuisine = preferences.get("cuisine", "various cuisines")
        
        summary = f"Found {candidate_count} restaurants in {location} serving {cuisine}"
        
        if preferences.get("min_rating"):
            summary += f" with rating ≥ {preferences['min_rating']}"
        
        if preferences.get("max_cost_for_two"):
            summary += f" and cost ≤ ₹{preferences['max_cost_for_two']} for two"
        
        summary += ". Please rank these options and provide recommendations."
        
        return summary
    
    def to_json_string(self, context: Dict[str, Any]) -> str:
        """Convert context to JSON string for LLM prompt."""
        return json.dumps(context, indent=2, ensure_ascii=False)
    
    def validate_candidates(self, candidates: List[Dict[str, Any]]) -> bool:
        """Validate that candidates have required fields."""
        if not candidates:
            return False
        
        required_fields = ["name", "cuisine", "rating", "cost_for_two", "location"]
        
        for candidate in candidates:
            missing_fields = [
                field for field in required_fields 
                if not candidate.get(field)
            ]
            if missing_fields:
                print(f"Warning: Candidate missing fields: {missing_fields}")
                return False
        
        return True
