"""Error and Fallback Handler: Comprehensive error handling and graceful degradation."""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import traceback


class ErrorHandler:
    """Handles errors in the recommendation system with appropriate responses."""
    
    def __init__(self):
        """Initialize the error handler."""
        self.logger = logging.getLogger(__name__)
        
        # Error type mappings
        self.error_mappings = {
            "ConnectionError": {
                "status_code": 503,
                "message": "Unable to connect to AI service. Please try again later.",
                "user_friendly": "Our AI service is temporarily unavailable. Please try again in a few moments."
            },
            "TimeoutError": {
                "status_code": 408,
                "message": "Request timed out. Please try again.",
                "user_friendly": "The request took too long to process. Please try again with simpler preferences."
            },
            "ValidationError": {
                "status_code": 400,
                "message": "Invalid input parameters.",
                "user_friendly": "Please check your preferences and try again."
            },
            "APIKeyError": {
                "status_code": 401,
                "message": "Invalid API key or authentication failed.",
                "user_friendly": "Service configuration error. Please contact support."
            },
            "RateLimitError": {
                "status_code": 429,
                "message": "Too many requests. Please try again later.",
                "user_friendly": "Too many requests at once. Please wait a moment and try again."
            },
            "DataError": {
                "status_code": 500,
                "message": "Data processing error.",
                "user_friendly": "We encountered an issue processing restaurant data. Please try again."
            },
            "LLMError": {
                "status_code": 502,
                "message": "AI model error.",
                "user_friendly": "Our AI model encountered an issue. Please try again."
            }
        }
    
    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle an error and return appropriate response.
        
        Args:
            error: The exception that occurred
            context: Additional context about the error
            
        Returns:
            Error response dictionary
        """
        error_name = error.__class__.__name__
        error_message = str(error)
        
        # Log the error
        self.logger.error(f"Error occurred: {error_name}: {error_message}")
        self.logger.debug(f"Context: {context}")
        self.logger.debug(f"Traceback: {traceback.format_exc()}")
        
        # Get error mapping
        error_info = self.error_mappings.get(error_name, self._get_default_error())
        
        # Create error response
        response = {
            "error": error_name,
            "message": error_info["message"],
            "user_friendly": error_info["user_friendly"],
            "status_code": error_info["status_code"],
            "timestamp": datetime.now().isoformat(),
            "context": context or {}
        }
        
        # Add specific error details if available
        if hasattr(error, 'details'):
            response["details"] = error.details
        
        return response
    
    def _get_default_error(self) -> Dict[str, Any]:
        """Get default error information."""
        return {
            "status_code": 500,
            "message": "An unexpected error occurred.",
            "user_friendly": "Something went wrong. Please try again or contact support if the issue persists."
        }
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Log error details for debugging."""
        self.logger.error(f"Error: {type(error).__name__}: {error}")
        if context:
            self.logger.error(f"Context: {context}")
        self.logger.debug(f"Full traceback: {traceback.format_exc()}")


class FallbackHandler:
    """Provides fallback responses when the main system fails."""
    
    def __init__(self):
        """Initialize the fallback handler."""
        self.logger = logging.getLogger(__name__)
        
        # Fallback recommendations by location
        self.fallback_recommendations = {
            "downtown": [
                {
                    "name": "City Bistro",
                    "cuisine": "Continental",
                    "rating": 4.2,
                    "price_range": "Moderate",
                    "reason": "Popular downtown spot with consistent quality"
                },
                {
                    "name": "The Garden Restaurant",
                    "cuisine": "Italian",
                    "rating": 4.0,
                    "price_range": "Moderate",
                    "reason": "Known for fresh ingredients and pleasant ambiance"
                }
            ],
            "koramangala": [
                {
                    "name": "Spice Junction",
                    "cuisine": "Indian",
                    "rating": 4.3,
                    "price_range": "Budget-friendly",
                    "reason": "Local favorite for authentic Indian cuisine"
                },
                {
                    "name": "Pasta Paradise",
                    "cuisine": "Italian",
                    "rating": 4.1,
                    "price_range": "Moderate",
                    "reason": "Great value Italian food in a casual setting"
                }
            ],
            "indiranagar": [
                {
                    "name": "Brew & Bite",
                    "cuisine": "Continental",
                    "rating": 4.4,
                    "price_range": "Premium",
                    "reason": "Trendy spot with craft beer and good food"
                },
                {
                    "name": "Sakura Sushi",
                    "cuisine": "Japanese",
                    "rating": 4.5,
                    "price_range": "Premium",
                    "reason": "Best sushi in the area with fresh ingredients"
                }
            ]
        }
        
        # Generic fallback recommendations
        self.generic_fallbacks = [
            {
                "name": "Local Favorite",
                "cuisine": "Multi-cuisine",
                "rating": 4.0,
                "price_range": "Moderate",
                "reason": "Well-regarded local restaurant with diverse menu"
            },
            {
                "name": "The Classic",
                "cuisine": "Continental",
                "rating": 3.9,
                "price_range": "Budget-friendly",
                "reason": "Reliable choice with good value for money"
            }
        ]
    
    def handle_no_matches(self, preferences) -> Dict[str, Any]:
        """
        Handle case when no restaurants match user preferences.
        
        Args:
            preferences: User preferences that didn't match
            
        Returns:
            Fallback response with suggestions
        """
        location = preferences.location.lower() if preferences.location else ""
        cuisine = preferences.cuisine.lower() if preferences.cuisine else ""
        
        # Get location-specific recommendations
        recommendations = []
        
        # Try location-specific first
        for loc_key, recs in self.fallback_recommendations.items():
            if loc_key in location:
                recommendations = recs
                break
        
        # If no location match, use generic
        if not recommendations:
            recommendations = self.generic_fallbacks
        
        # Create fallback response
        response = {
            "recommendations": self._format_fallback_recommendations(recommendations),
            "summary": self._create_no_match_summary(preferences),
            "total_matches": 0,
            "fallback_used": True,
            "suggestions": self._get_suggestions(preferences)
        }
        
        return response
    
    def handle_llm_failure(self, preferences: Dict[str, Any], candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Handle LLM failure with rule-based recommendations.
        
        Args:
            preferences: User preferences
            candidates: Filtered restaurant candidates
            
        Returns:
            Rule-based recommendations
        """
        # Simple rule-based ranking
        ranked_candidates = sorted(
            candidates,
            key=lambda x: (
                float(x.get("rating", 0)) * 0.4 +
                (1 - min(float(x.get("cost_for_two", 2000)) / 2000, 1)) * 0.3 +
                (1 if preferences.get("cuisine", "").lower() in x.get("cuisine", "").lower() else 0) * 0.3
            ),
            reverse=True
        )[:5]
        
        # Format recommendations
        recommendations = []
        for i, candidate in enumerate(ranked_candidates, 1):
            rec = {
                "rank": i,
                "restaurant_name": candidate.get("name", "Unknown"),
                "match_score": 0.8 - (i * 0.1),  # Decreasing scores
                "reasons": [
                    f"Good rating ({candidate.get('rating', 'N/A')})",
                    f"Matches your location ({candidate.get('location', 'N/A')})",
                    "Popular choice"
                ],
                "highlights": [f"Cuisine: {candidate.get('cuisine', 'Various')}"],
                "price_indication": self._get_price_indication(candidate.get("cost_for_two", 0)),
                "best_for": "General dining"
            }
            recommendations.append(rec)
        
        return {
            "recommendations": recommendations,
            "summary": "Recommendations generated using our backup system (AI temporarily unavailable)",
            "total_matches": len(candidates),
            "fallback_used": True,
            "fallback_reason": "LLM service unavailable"
        }
    
    def _format_fallback_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format fallback recommendations to match expected structure."""
        formatted = []
        
        for i, rec in enumerate(recommendations, 1):
            formatted_rec = {
                "rank": i,
                "restaurant_name": rec["name"],
                "match_score": 0.75,  # Default fallback score
                "reasons": [rec["reason"]],
                "highlights": [f"Cuisine: {rec['cuisine']}", f"Rating: {rec['rating']}/5"],
                "price_indication": rec["price_range"],
                "best_for": "General dining"
            }
            formatted.append(formatted_rec)
        
        return formatted
    
    def _create_no_match_summary(self, preferences) -> str:
        """Create summary for no-match scenarios."""
        location = preferences.location if preferences.location else "your area"
        cuisine = preferences.cuisine if preferences.cuisine else "your preferred cuisine"
        
        summary = f"No exact matches found for {cuisine} restaurants in {location}. "
        summary += "Here are some popular alternatives that you might enjoy:"
        
        return summary
    
    def _get_suggestions(self, preferences) -> List[str]:
        """Get suggestions for improving search results."""
        suggestions = []
        
        if preferences.min_rating and preferences.min_rating > 4.0:
            suggestions.append("Try lowering the minimum rating requirement")
        
        # Note: UserPreferences doesn't have max_cost_for_two, so we skip this check
        # if preferences.max_cost_for_two and preferences.max_cost_for_two < 500:
        #     suggestions.append("Consider increasing your budget range")
        
        if preferences.cuisine:
            suggestions.append("Try browsing without a specific cuisine filter")
        
        suggestions.append("Check if the location name is spelled correctly")
        suggestions.append("Try a broader location search")
        
        return suggestions
    
    def _get_price_indication(self, cost: int) -> str:
        """Get price indication from cost."""
        if cost <= 500:
            return "Budget-friendly"
        elif cost <= 1000:
            return "Moderate"
        elif cost <= 1500:
            return "Premium"
        else:
            return "Fine Dining"


class GracefulDegradation:
    """Manages graceful degradation of the system."""
    
    def __init__(self):
        """Initialize graceful degradation manager."""
        self.error_handler = ErrorHandler()
        self.fallback_handler = FallbackHandler()
        self.logger = logging.getLogger(__name__)
    
    def handle_request_failure(self, error: Exception, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle complete request failure with appropriate fallback.
        
        Args:
            error: The error that occurred
            preferences: User preferences
            
        Returns:
            Appropriate fallback response
        """
        # Log the error
        self.error_handler.log_error(error, preferences)
        
        # Determine fallback strategy based on error type
        error_name = error.__class__.__name__
        
        if error_name in ["ConnectionError", "TimeoutError", "APIKeyError"]:
            # LLM service issues - use rule-based fallback
            return self.fallback_handler.handle_no_matches(preferences)
        elif error_name in ["ValidationError", "DataError"]:
            # Input/data issues - provide helpful suggestions
            return self.fallback_handler.handle_no_matches(preferences)
        else:
            # Unknown errors - use generic fallback
            return self.fallback_handler.handle_no_matches(preferences)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status for monitoring."""
        return {
            "status": "operational",
            "fallback_mode": False,
            "last_error": None,
            "timestamp": datetime.now().isoformat()
        }
