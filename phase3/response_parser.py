"""Response Parser: Parses and validates structured LLM responses."""

from typing import Dict, Any, List, Optional, Union
import json
import re
import logging
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Recommendation:
    """Structured recommendation data."""
    rank: int
    restaurant_name: str
    match_score: float
    reasons: List[str]
    highlights: List[str]
    price_indication: str
    best_for: str


@dataclass
class RankedRestaurant:
    """Ranked restaurant data."""
    original_rank: int
    new_rank: int
    restaurant_name: str
    score_breakdown: Dict[str, float]
    overall_score: float
    ranking_reason: str


@dataclass
class DetailedExplanation:
    """Detailed explanation data."""
    rank: int
    restaurant_name: str
    why_recommended: Dict[str, str]
    suitability_for: Dict[str, Union[str, List[str]]]


class ResponseParser:
    """Parses and validates LLM responses into structured data."""
    
    def __init__(self):
        """Initialize the ResponseParser."""
        self.logger = logging.getLogger(__name__)
        self.expected_schemas = {
            "recommendation": self._get_recommendation_schema(),
            "ranking": self._get_ranking_schema(),
            "explanation": self._get_explanation_schema()
        }
    
    def parse_response(
        self, 
        response_text: str, 
        response_type: str = "recommendation"
    ) -> Dict[str, Any]:
        """
        Parse LLM response text into structured data.
        
        Args:
            response_text: Raw text response from LLM
            response_type: Type of response to parse
            
        Returns:
            Parsed and validated structured data
        """
        # Extract JSON from response
        json_data = self._extract_json(response_text)
        
        if not json_data:
            raise ValueError("No valid JSON found in response")
        
        # Validate and parse based on type
        if response_type == "recommendation":
            return self._parse_recommendation_response(json_data)
        elif response_type == "ranking":
            return self._parse_ranking_response(json_data)
        elif response_type == "explanation":
            return self._parse_explanation_response(json_data)
        else:
            raise ValueError(f"Unknown response type: {response_type}")
    
    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from text that might contain markdown or other content."""
        # Try to parse the entire text as JSON first
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass
        
        # Try to extract JSON from markdown blocks
        json_patterns = [
            r'```json\s*(.*?)\s*```',
            r'```\s*(.*?)\s*```',
            r'\{.*\}'
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match.strip())
                except json.JSONDecodeError:
                    continue
        
        return None
    
    def _parse_recommendation_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse recommendation response."""
        if "recommendations" not in data:
            raise ValueError("Missing 'recommendations' field in response")
        
        recommendations = []
        for rec_data in data["recommendations"]:
            try:
                recommendation = Recommendation(
                    rank=int(rec_data.get("rank", 0)),
                    restaurant_name=str(rec_data.get("restaurant_name", "")),
                    match_score=float(rec_data.get("match_score", 0)),
                    reasons=self._ensure_list(rec_data.get("reasons", [])),
                    highlights=self._ensure_list(rec_data.get("highlights", [])),
                    price_indication=str(rec_data.get("price_indication", "")),
                    best_for=str(rec_data.get("best_for", ""))
                )
                recommendations.append(asdict(recommendation))
            except (ValueError, TypeError) as e:
                self.logger.warning(f"Failed to parse recommendation: {e}")
                continue
        
        return {
            "recommendations": recommendations,
            "summary": data.get("summary", ""),
            "alternative_suggestions": data.get("alternative_suggestions", ""),
            "total_matches": int(data.get("total_matches", 0)),
            "parsed_at": datetime.now().isoformat()
        }
    
    def _parse_ranking_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse ranking response."""
        if "ranked_restaurants" not in data:
            raise ValueError("Missing 'ranked_restaurants' field in response")
        
        ranked_restaurants = []
        for rank_data in data["ranked_restaurants"]:
            try:
                ranked_rest = RankedRestaurant(
                    original_rank=int(rank_data.get("original_rank", 0)),
                    new_rank=int(rank_data.get("new_rank", 0)),
                    restaurant_name=str(rank_data.get("restaurant_name", "")),
                    score_breakdown=self._ensure_dict(rank_data.get("score_breakdown", {})),
                    overall_score=float(rank_data.get("overall_score", 0)),
                    ranking_reason=str(rank_data.get("ranking_reason", ""))
                )
                ranked_restaurants.append(asdict(ranked_rest))
            except (ValueError, TypeError) as e:
                self.logger.warning(f"Failed to parse ranked restaurant: {e}")
                continue
        
        return {
            "ranked_restaurants": ranked_restaurants,
            "ranking_methodology": data.get("ranking_methodology", ""),
            "parsed_at": datetime.now().isoformat()
        }
    
    def _parse_explanation_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse explanation response."""
        if "detailed_explanations" not in data:
            raise ValueError("Missing 'detailed_explanations' field in response")
        
        explanations = []
        for exp_data in data["detailed_explanations"]:
            try:
                explanation = DetailedExplanation(
                    rank=int(exp_data.get("rank", 0)),
                    restaurant_name=str(exp_data.get("restaurant_name", "")),
                    why_recommended=self._ensure_dict(exp_data.get("why_recommended", {})),
                    suitability_for=self._ensure_dict(exp_data.get("suitability_for", {}))
                )
                explanations.append(asdict(explanation))
            except (ValueError, TypeError) as e:
                self.logger.warning(f"Failed to parse explanation: {e}")
                continue
        
        return {
            "detailed_explanations": explanations,
            "parsed_at": datetime.now().isoformat()
        }
    
    def _ensure_list(self, value: Any) -> List[str]:
        """Ensure value is a list of strings."""
        if isinstance(value, list):
            return [str(item) for item in value]
        elif value is None:
            return []
        else:
            return [str(value)]
    
    def _ensure_dict(self, value: Any) -> Dict[str, Any]:
        """Ensure value is a dictionary."""
        if isinstance(value, dict):
            return value
        elif value is None:
            return {}
        else:
            return {"value": str(value)}
    
    def validate_response_structure(
        self, 
        data: Dict[str, Any], 
        response_type: str
    ) -> bool:
        """
        Validate response structure against expected schema.
        
        Args:
            data: Parsed response data
            response_type: Type of response
            
        Returns:
            True if valid, False otherwise
        """
        schema = self.expected_schemas.get(response_type)
        if not schema:
            return False
        
        return self._validate_against_schema(data, schema)
    
    def _validate_against_schema(self, data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """Basic schema validation."""
        required_fields = schema.get("required", [])
        
        for field in required_fields:
            if field not in data:
                self.logger.error(f"Missing required field: {field}")
                return False
        
        return True
    
    def _get_recommendation_schema(self) -> Dict[str, Any]:
        """Get expected schema for recommendation responses."""
        return {
            "type": "object",
            "required": ["recommendations"],
            "properties": {
                "recommendations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["rank", "restaurant_name", "match_score"],
                        "properties": {
                            "rank": {"type": "number"},
                            "restaurant_name": {"type": "string"},
                            "match_score": {"type": "number"},
                            "reasons": {"type": "array"},
                            "highlights": {"type": "array"},
                            "price_indication": {"type": "string"},
                            "best_for": {"type": "string"}
                        }
                    }
                },
                "summary": {"type": "string"},
                "alternative_suggestions": {"type": "string"},
                "total_matches": {"type": "number"}
            }
        }
    
    def _get_ranking_schema(self) -> Dict[str, Any]:
        """Get expected schema for ranking responses."""
        return {
            "type": "object",
            "required": ["ranked_restaurants"],
            "properties": {
                "ranked_restaurants": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["original_rank", "new_rank", "restaurant_name", "overall_score"],
                        "properties": {
                            "original_rank": {"type": "number"},
                            "new_rank": {"type": "number"},
                            "restaurant_name": {"type": "string"},
                            "score_breakdown": {"type": "object"},
                            "overall_score": {"type": "number"},
                            "ranking_reason": {"type": "string"}
                        }
                    }
                },
                "ranking_methodology": {"type": "string"}
            }
        }
    
    def _get_explanation_schema(self) -> Dict[str, Any]:
        """Get expected schema for explanation responses."""
        return {
            "type": "object",
            "required": ["detailed_explanations"],
            "properties": {
                "detailed_explanations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["rank", "restaurant_name"],
                        "properties": {
                            "rank": {"type": "number"},
                            "restaurant_name": {"type": "string"},
                            "why_recommended": {"type": "object"},
                            "suitability_for": {"type": "object"}
                        }
                    }
                }
            }
        }
    
    def format_for_display(self, parsed_data: Dict[str, Any], response_type: str) -> str:
        """
        Format parsed data for user display.
        
        Args:
            parsed_data: Parsed response data
            response_type: Type of response
            
        Returns:
            Formatted string for display
        """
        if response_type == "recommendation":
            return self._format_recommendations_for_display(parsed_data)
        elif response_type == "ranking":
            return self._format_ranking_for_display(parsed_data)
        elif response_type == "explanation":
            return self._format_explanation_for_display(parsed_data)
        else:
            return json.dumps(parsed_data, indent=2)
    
    def _format_recommendations_for_display(self, data: Dict[str, Any]) -> str:
        """Format recommendations for display."""
        output = []
        
        if data.get("summary"):
            output.append(f"**Summary:** {data['summary']}\n")
        
        recommendations = data.get("recommendations", [])
        for rec in recommendations:
            output.append(f"**{rec['rank']}. {rec['restaurant_name']}**")
            output.append(f"   Match Score: {rec['match_score']:.2f}")
            output.append(f"   Price: {rec['price_indication']}")
            output.append(f"   Best For: {rec['best_for']}")
            
            if rec.get("reasons"):
                output.append("   Why Recommended:")
                for reason in rec["reasons"]:
                    output.append(f"   • {reason}")
            
            if rec.get("highlights"):
                output.append("   Highlights:")
                for highlight in rec["highlights"]:
                    output.append(f"   • {highlight}")
            
            output.append("")
        
        if data.get("alternative_suggestions"):
            output.append(f"**Alternatives:** {data['alternative_suggestions']}")
        
        return "\n".join(output)
    
    def _format_ranking_for_display(self, data: Dict[str, Any]) -> str:
        """Format ranking for display."""
        output = []
        
        if data.get("ranking_methodology"):
            output.append(f"**Methodology:** {data['ranking_methodology']}\n")
        
        ranked_restaurants = data.get("ranked_restaurants", [])
        for rank in ranked_restaurants:
            output.append(f"**{rank['new_rank']}. {rank['restaurant_name']}**")
            output.append(f"   Overall Score: {rank['overall_score']:.2f}")
            output.append(f"   Moved from rank {rank['original_rank']} to {rank['new_rank']}")
            output.append(f"   Reason: {rank['ranking_reason']}")
            
            if rank.get("score_breakdown"):
                output.append("   Score Breakdown:")
                for criterion, score in rank["score_breakdown"].items():
                    output.append(f"   • {criterion}: {score:.2f}")
            
            output.append("")
        
        return "\n".join(output)
    
    def _format_explanation_for_display(self, data: Dict[str, Any]) -> str:
        """Format explanations for display."""
        output = []
        
        explanations = data.get("detailed_explanations", [])
        for exp in explanations:
            output.append(f"**{exp['rank']}. {exp['restaurant_name']}**")
            
            why_rec = exp.get("why_recommended", {})
            if why_rec:
                output.append("   Why Recommended:")
                for key, value in why_rec.items():
                    output.append(f"   • {key.title()}: {value}")
            
            suitability = exp.get("suitability_for", {})
            if suitability:
                output.append("   Suitability:")
                for key, value in suitability.items():
                    if isinstance(value, list):
                        output.append(f"   • {key.title()}: {', '.join(value)}")
                    else:
                        output.append(f"   • {key.title()}: {value}")
            
            output.append("")
        
        return "\n".join(output)
