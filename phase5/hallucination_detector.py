"""Hallucination Detection: Detect and track hallucinations in LLM responses."""

from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime
from dataclasses import dataclass
import re
from collections import defaultdict


@dataclass
class HallucinationReport:
    """Report of detected hallucinations."""
    recommendation_id: str
    timestamp: datetime
    hallucination_type: str
    severity: str  # low, medium, high, critical
    description: str
    evidence: List[str]
    confidence: float
    context: Dict[str, Any]


@dataclass
class RankingConsistencyReport:
    """Report of ranking consistency issues."""
    recommendation_id: str
    timestamp: datetime
    inconsistency_type: str
    severity: str
    description: str
    affected_rankings: List[int]
    confidence: float


class HallucinationDetector:
    """Detects hallucinations in LLM-generated recommendations."""
    
    def __init__(self):
        """Initialize the hallucination detector."""
        self.logger = logging.getLogger(__name__)
        
        # Known restaurant database (would be loaded from actual data)
        self.known_restaurants = set()
        self.known_cuisines = set()
        self.known_locations = set()
        
        # Hallucination patterns
        self.fake_patterns = [
            r"test\s+restaurant",
            r"sample\s+place",
            r"demo\s+eatery",
            r"fake\s+food",
            r"example\s+dining",
            r"placeholder\s+restaurant"
        ]
        
        # Unrealistic score patterns
        self.unrealistic_scores = {
            "match_score": (0.0, 1.0),
            "rating": (0.0, 5.0)
        }
        
        # Generic explanation patterns
        self.generic_patterns = [
            r"good\s+food",
            r"nice\s+place",
            r"great\s+service",
            r"excellent\s+choice",
            r"amazing\s+experience"
        ]
        
        self.logger.info("Hallucination detector initialized")
    
    def load_restaurant_database(self, restaurants: List[Dict[str, Any]]) -> None:
        """Load known restaurant database for validation."""
        for restaurant in restaurants:
            self.known_restaurants.add(restaurant.get("name", "").lower())
            self.known_cuisines.add(restaurant.get("cuisine", "").lower())
            self.known_locations.add(restaurant.get("location", "").lower())
        
        self.logger.info(f"Loaded {len(self.known_restaurants)} known restaurants")
    
    def detect_hallucinations(
        self,
        recommendations: List[Dict[str, Any]],
        user_preferences: Dict[str, Any]
    ) -> List[HallucinationReport]:
        """
        Detect hallucinations in recommendations.
        
        Args:
            recommendations: List of recommendation dictionaries
            user_preferences: User preferences used
            
        Returns:
            List of hallucination reports
        """
        reports = []
        
        for i, rec in enumerate(recommendations):
            rec_reports = self._analyze_single_recommendation(rec, user_preferences)
            reports.extend(rec_reports)
        
        return reports
    
    def _analyze_single_recommendation(
        self,
        recommendation: Dict[str, Any],
        user_preferences: Dict[str, Any]
    ) -> List[HallucinationReport]:
        """Analyze a single recommendation for hallucinations."""
        reports = []
        
        # Check restaurant name hallucination
        restaurant_report = self._check_restaurant_hallucination(recommendation)
        if restaurant_report:
            reports.append(restaurant_report)
        
        # Check score hallucination
        score_report = self._check_score_hallucination(recommendation)
        if score_report:
            reports.append(score_report)
        
        # Check explanation hallucination
        explanation_reports = self._check_explanation_hallucination(recommendation)
        reports.extend(explanation_reports)
        
        # Check attribute hallucination
        attribute_reports = self._check_attribute_hallucination(recommendation)
        reports.extend(attribute_reports)
        
        # Check context hallucination
        context_report = self._check_context_hallucination(recommendation, user_preferences)
        if context_report:
            reports.append(context_report)
        
        return reports
    
    def _check_restaurant_hallucination(self, recommendation: Dict[str, Any]) -> Optional[HallucinationReport]:
        """Check for restaurant name hallucination."""
        restaurant_name = recommendation.get("restaurant_name", "")
        
        if not restaurant_name:
            return None
        
        # Check for fake patterns
        for pattern in self.fake_patterns:
            if re.search(pattern, restaurant_name, re.IGNORECASE):
                return HallucinationReport(
                    recommendation_id=recommendation.get("rank", "unknown"),
                    timestamp=datetime.now(),
                    hallucination_type="fake_restaurant_name",
                    severity="high",
                    description=f"Restaurant name contains fake pattern: {pattern}",
                    evidence=[restaurant_name],
                    confidence=0.9,
                    context={"pattern": pattern}
                )
        
        # Check if restaurant is in known database
        if self.known_restaurants and restaurant_name.lower() not in self.known_restaurants:
            # Check if it's obviously fake
            if any(word in restaurant_name.lower() for word in ["test", "sample", "demo", "fake"]):
                return HallucinationReport(
                    recommendation_id=recommendation.get("rank", "unknown"),
                    timestamp=datetime.now(),
                    hallucination_type="unknown_restaurant",
                    severity="medium",
                    description="Restaurant name not found in database and contains suspicious words",
                    evidence=[restaurant_name],
                    confidence=0.7,
                    context={"known_count": len(self.known_restaurants)}
                )
        
        return None
    
    def _check_score_hallucination(self, recommendation: Dict[str, Any]) -> Optional[HallucinationReport]:
        """Check for unrealistic scores."""
        reports = []
        
        # Check match score
        match_score = recommendation.get("match_score")
        if match_score is not None:
            min_score, max_score = self.unrealistic_scores["match_score"]
            if not (min_score <= match_score <= max_score):
                severity = "critical" if match_score > 1.5 or match_score < -0.5 else "high"
                reports.append(HallucinationReport(
                    recommendation_id=recommendation.get("rank", "unknown"),
                    timestamp=datetime.now(),
                    hallucination_type="unrealistic_match_score",
                    severity=severity,
                    description=f"Match score {match_score} outside valid range [{min_score}, {max_score}]",
                    evidence=[f"match_score: {match_score}"],
                    confidence=0.95,
                    context={"score": match_score, "valid_range": (min_score, max_score)}
                ))
        
        # Check rating
        rating = recommendation.get("rating")
        if rating is not None:
            min_rating, max_rating = self.unrealistic_scores["rating"]
            if not (min_rating <= rating <= max_rating):
                severity = "critical" if rating > 6.0 or rating < 0 else "high"
                reports.append(HallucinationReport(
                    recommendation_id=recommendation.get("rank", "unknown"),
                    timestamp=datetime.now(),
                    hallucination_type="unrealistic_rating",
                    severity=severity,
                    description=f"Rating {rating} outside valid range [{min_rating}, {max_rating}]",
                    evidence=[f"rating: {rating}"],
                    confidence=0.95,
                    context={"rating": rating, "valid_range": (min_rating, max_rating)}
                ))
        
        return reports[0] if reports else None
    
    def _check_explanation_hallucination(self, recommendation: Dict[str, Any]) -> List[HallucinationReport]:
        """Check for explanation hallucination."""
        reports = []
        
        reasons = recommendation.get("reasons", [])
        highlights = recommendation.get("highlights", [])
        
        all_explanations = reasons + highlights
        
        for explanation in all_explanations:
            # Check for generic patterns
            for pattern in self.generic_patterns:
                if re.search(pattern, explanation, re.IGNORECASE):
                    reports.append(HallucinationReport(
                        recommendation_id=recommendation.get("rank", "unknown"),
                        timestamp=datetime.now(),
                        hallucination_type="generic_explanation",
                        severity="low",
                        description=f"Generic explanation pattern detected: {pattern}",
                        evidence=[explanation],
                        confidence=0.6,
                        context={"pattern": pattern, "explanation": explanation}
                    ))
            
            # Check for test/sample content
            if any(word in explanation.lower() for word in ["test", "sample", "demo", "fake"]):
                reports.append(HallucinationReport(
                    recommendation_id=recommendation.get("rank", "unknown"),
                    timestamp=datetime.now(),
                    hallucination_type="test_content_in_explanation",
                    severity="medium",
                    description="Explanation contains test/sample content",
                    evidence=[explanation],
                    confidence=0.8,
                    context={"explanation": explanation}
                ))
        
        return reports
    
    def _check_attribute_hallucination(self, recommendation: Dict[str, Any]) -> List[HallucinationReport]:
        """Check for attribute hallucination."""
        reports = []
        
        # Check cuisine
        cuisine = recommendation.get("cuisine", "")
        if cuisine and self.known_cuisines:
            if cuisine.lower() not in self.known_cuisines:
                reports.append(HallucinationReport(
                    recommendation_id=recommendation.get("rank", "unknown"),
                    timestamp=datetime.now(),
                    hallucination_type="unknown_cuisine",
                    severity="low",
                    description=f"Cuisine '{cuisine}' not found in known database",
                    evidence=[cuisine],
                    confidence=0.5,
                    context={"cuisine": cuisine}
                ))
        
        # Check location
        location = recommendation.get("location", "")
        if location and self.known_locations:
            if location.lower() not in self.known_locations:
                reports.append(HallucinationReport(
                    recommendation_id=recommendation.get("rank", "unknown"),
                    timestamp=datetime.now(),
                    hallucination_type="unknown_location",
                    severity="low",
                    description=f"Location '{location}' not found in known database",
                    evidence=[location],
                    confidence=0.5,
                    context={"location": location}
                ))
        
        return reports
    
    def _check_context_hallucination(
        self,
        recommendation: Dict[str, Any],
        user_preferences: Dict[str, Any]
    ) -> Optional[HallucinationReport]:
        """Check for context hallucination."""
        # Check if recommendation contradicts user preferences
        contradictions = []
        
        # Budget contradiction
        max_budget = user_preferences.get("max_cost_for_two")
        rec_cost = recommendation.get("cost_for_two")
        if max_budget and rec_cost and rec_cost > max_budget * 1.5:  # 50% over budget
            contradictions.append(f"Cost {rec_cost} exceeds budget {max_budget}")
        
        # Rating contradiction
        min_rating = user_preferences.get("min_rating")
        rec_rating = recommendation.get("rating")
        if min_rating and rec_rating and rec_rating < min_rating - 0.5:  # 0.5 below minimum
            contradictions.append(f"Rating {rec_rating} below minimum {min_rating}")
        
        # Location contradiction
        preferred_location = user_preferences.get("location", "").lower()
        rec_location = recommendation.get("location", "").lower()
        if preferred_location and rec_location and preferred_location not in rec_location:
            contradictions.append(f"Location {rec_location} doesn't match preference {preferred_location}")
        
        if contradictions:
            return HallucinationReport(
                recommendation_id=recommendation.get("rank", "unknown"),
                timestamp=datetime.now(),
                hallucination_type="context_contradiction",
                severity="medium",
                description="Recommendation contradicts user preferences",
                evidence=contradictions,
                confidence=0.7,
                context={"contradictions": contradictions}
            )
        
        return None


class RankingConsistencyTracker:
    """Tracks ranking consistency issues."""
    
    def __init__(self):
        """Initialize the ranking consistency tracker."""
        self.logger = logging.getLogger(__name__)
        self.consistency_history: List[RankingConsistencyReport] = []
    
    def check_ranking_consistency(
        self,
        recommendations: List[Dict[str, Any]]
    ) -> List[RankingConsistencyReport]:
        """
        Check ranking consistency in recommendations.
        
        Args:
            recommendations: List of recommendation dictionaries
            
        Returns:
            List of consistency reports
        """
        reports = []
        
        if len(recommendations) < 2:
            return reports
        
        # Check score vs rank consistency
        score_report = self._check_score_rank_consistency(recommendations)
        if score_report:
            reports.append(score_report)
        
        # Check ranking order logic
        order_report = self._check_ranking_order_logic(recommendations)
        if order_report:
            reports.append(order_report)
        
        # Check for duplicate rankings
        duplicate_report = self._check_duplicate_rankings(recommendations)
        if duplicate_report:
            reports.append(duplicate_report)
        
        # Store in history
        self.consistency_history.extend(reports)
        
        return reports
    
    def _check_score_rank_consistency(
        self,
        recommendations: List[Dict[str, Any]]
    ) -> Optional[RankingConsistencyReport]:
        """Check if scores are consistent with rankings."""
        inconsistencies = []
        
        for i, rec in enumerate(recommendations):
            rank = rec.get("rank", i + 1)
            match_score = rec.get("match_score", 0)
            
            # Check if score makes sense for rank position
            expected_score_range = self._get_expected_score_range(rank, len(recommendations))
            
            if not (expected_score_range[0] <= match_score <= expected_score_range[1]):
                inconsistencies.append(f"Rank {rank} with score {match_score} outside expected range {expected_score_range}")
        
        if inconsistencies:
            return RankingConsistencyReport(
                recommendation_id="batch",
                timestamp=datetime.now(),
                inconsistency_type="score_rank_mismatch",
                severity="medium",
                description="Match scores don't correspond to ranking positions",
                affected_rankings=[rec.get("rank", i + 1) for i, rec in enumerate(recommendations)],
                confidence=0.8,
                context={"inconsistencies": inconsistencies}
            )
        
        return None
    
    def _get_expected_score_range(self, rank: int, total_recommendations: int) -> Tuple[float, float]:
        """Get expected score range for a given rank."""
        # Top recommendation should have highest score
        # Scores should generally decrease with rank
        if rank == 1:
            return (0.8, 1.0)
        elif rank == total_recommendations:
            return (0.0, 0.4)
        else:
            # Linear interpolation
            min_score = 0.0 + (0.4 * (total_recommendations - rank) / (total_recommendations - 1))
            max_score = 1.0 - (0.6 * (rank - 1) / (total_recommendations - 1))
            return (min_score, max_score)
    
    def _check_ranking_order_logic(
        self,
        recommendations: List[Dict[str, Any]]
    ) -> Optional[RankingConsistencyReport]:
        """Check logical consistency of ranking order."""
        scores = [rec.get("match_score", 0) for rec in recommendations]
        ranks = [rec.get("rank", i + 1) for i, rec in enumerate(recommendations)]
        
        inconsistencies = []
        
        # Check for score inversions
        for i in range(len(scores) - 1):
            if scores[i] < scores[i + 1]:
                inconsistencies.append(f"Score inversion: rank {ranks[i]} ({scores[i]}) < rank {ranks[i + 1]} ({scores[i + 1]})")
        
        # Check for equal scores with different ranks
        for i in range(len(scores) - 1):
            if abs(scores[i] - scores[i + 1]) < 0.01 and ranks[i] != ranks[i + 1]:
                inconsistencies.append(f"Equal scores with different ranks: {ranks[i]} and {ranks[i + 1]} both have score ~{scores[i]}")
        
        if inconsistencies:
            return RankingConsistencyReport(
                recommendation_id="batch",
                timestamp=datetime.now(),
                inconsistency_type="ranking_order_illogical",
                severity="medium",
                description="Ranking order doesn't follow logical score progression",
                affected_rankings=ranks,
                confidence=0.7,
                context={"inconsistencies": inconsistencies}
            )
        
        return None
    
    def _check_duplicate_rankings(
        self,
        recommendations: List[Dict[str, Any]]
    ) -> Optional[RankingConsistencyReport]:
        """Check for duplicate rankings."""
        rank_counts = defaultdict(int)
        rank_positions = defaultdict(list)
        
        for i, rec in enumerate(recommendations):
            rank = rec.get("rank", i + 1)
            rank_counts[rank] += 1
            rank_positions[rank].append(i + 1)
        
        duplicates = {rank: count for rank, count in rank_counts.items() if count > 1}
        
        if duplicates:
            return RankingConsistencyReport(
                recommendation_id="batch",
                timestamp=datetime.now(),
                inconsistency_type="duplicate_rankings",
                severity="high",
                description=f"Duplicate rankings found: {duplicates}",
                affected_rankings=list(duplicates.keys()),
                confidence=0.9,
                context={"duplicates": duplicates, "positions": dict(rank_positions)}
            )
        
        return None
    
    def get_consistency_summary(self, days_back: int = 7) -> Dict[str, Any]:
        """Get summary of consistency issues."""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        recent_reports = [
            report for report in self.consistency_history
            if report.timestamp >= cutoff_date
        ]
        
        if not recent_reports:
            return {"total_issues": 0, "message": "No consistency issues found"}
        
        # Count by type
        type_counts = defaultdict(int)
        severity_counts = defaultdict(int)
        
        for report in recent_reports:
            type_counts[report.inconsistency_type] += 1
            severity_counts[report.severity] += 1
        
        return {
            "total_issues": len(recent_reports),
            "by_type": dict(type_counts),
            "by_severity": dict(severity_counts),
            "most_common_type": max(type_counts.items(), key=lambda x: x[1])[0] if type_counts else None,
            "time_period": f"Last {days_back} days"
        }


# Import timedelta for date calculations
from datetime import timedelta
