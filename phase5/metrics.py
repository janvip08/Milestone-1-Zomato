"""Evaluation Metrics: Calculate metrics for recommendation quality assessment."""

from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime
import math
from collections import defaultdict


class EvaluationMetrics:
    """Calculates various metrics for evaluating recommendation quality."""
    
    def __init__(self):
        """Initialize the evaluation metrics calculator."""
        self.logger = logging.getLogger(__name__)
        
        # Metric weights for overall score
        self.metric_weights = {
            "relevance_score": 0.3,
            "response_time_ms": 0.2,
            "explanation_quality": 0.25,
            "ranking_consistency": 0.15,
            "hallucination_penalty": 0.1
        }
        
        self.logger.info("Evaluation metrics calculator initialized")
    
    def calculate_metrics(
        self,
        recommendations: Dict[str, Any],
        user_preferences: Dict[str, Any],
        expected_outcomes: Optional[Dict[str, Any]] = None
    ) -> Dict[str, float]:
        """
        Calculate comprehensive metrics for recommendation evaluation.
        
        Args:
            recommendations: Recommendation response from the system
            user_preferences: User preferences used for the recommendation
            expected_outcomes: Expected outcomes for validation
            
        Returns:
            Dictionary of calculated metrics
        """
        metrics = {}
        
        # Extract recommendation list
        rec_list = recommendations.get("recommendations", [])
        
        # Calculate individual metrics
        metrics["relevance_score"] = self._calculate_relevance_score(
            rec_list, user_preferences
        )
        
        metrics["response_time_ms"] = self._extract_response_time(recommendations)
        
        metrics["explanation_quality"] = self._calculate_explanation_quality(rec_list)
        
        metrics["ranking_consistency"] = self._calculate_ranking_consistency(rec_list)
        
        metrics["hallucination_penalty"] = self._calculate_hallucination_penalty(rec_list)
        
        metrics["budget_compliance"] = self._calculate_budget_compliance(
            rec_list, user_preferences
        )
        
        metrics["rating_compliance"] = self._calculate_rating_compliance(
            rec_list, user_preferences
        )
        
        metrics["location_compliance"] = self._calculate_location_compliance(
            rec_list, user_preferences
        )
        
        metrics["cuisine_compliance"] = self._calculate_cuisine_compliance(
            rec_list, user_preferences
        )
        
        metrics["variety_score"] = self._calculate_variety_score(rec_list)
        
        metrics["overall_score"] = self._calculate_overall_score(metrics)
        
        # Validate against expected outcomes if provided
        if expected_outcomes:
            validation_metrics = self._validate_against_expected(
                rec_list, user_preferences, expected_outcomes
            )
            metrics.update(validation_metrics)
        
        return metrics
    
    def _calculate_relevance_score(
        self,
        recommendations: List[Dict[str, Any]],
        user_preferences: Dict[str, Any]
    ) -> float:
        """Calculate relevance score based on preference matching."""
        if not recommendations:
            return 0.0
        
        total_score = 0.0
        
        for rec in recommendations:
            rec_score = 0.0
            weight_sum = 0.0
            
            # Location relevance (weight: 0.3)
            if "location" in user_preferences:
                location_weight = 0.3
                location_match = self._check_location_match(rec, user_preferences["location"])
                rec_score += location_match * location_weight
                weight_sum += location_weight
            
            # Cuisine relevance (weight: 0.25)
            if user_preferences.get("cuisine"):
                cuisine_weight = 0.25
                cuisine_match = self._check_cuisine_match(rec, user_preferences["cuisine"])
                rec_score += cuisine_match * cuisine_weight
                weight_sum += cuisine_weight
            
            # Budget relevance (weight: 0.2)
            if user_preferences.get("max_cost_for_two"):
                budget_weight = 0.2
                budget_match = self._check_budget_match(rec, user_preferences["max_cost_for_two"])
                rec_score += budget_match * budget_weight
                weight_sum += budget_weight
            
            # Rating relevance (weight: 0.15)
            if user_preferences.get("min_rating"):
                rating_weight = 0.15
                rating_match = self._check_rating_match(rec, user_preferences["min_rating"])
                rec_score += rating_match * rating_weight
                weight_sum += rating_weight
            
            # Occasion relevance (weight: 0.1)
            if user_preferences.get("occasion"):
                occasion_weight = 0.1
                occasion_match = self._check_occasion_match(rec, user_preferences["occasion"])
                rec_score += occasion_match * occasion_weight
                weight_sum += occasion_weight
            
            # Normalize score
            if weight_sum > 0:
                rec_score = rec_score / weight_sum
            else:
                rec_score = 0.5  # Default score if no preferences to match
            
            total_score += rec_score
        
        return total_score / len(recommendations)
    
    def _check_location_match(self, recommendation: Dict[str, Any], preferred_location: str) -> float:
        """Check if recommendation matches preferred location."""
        rec_location = recommendation.get("location", "")
        preferred_lower = preferred_location.lower()
        rec_lower = rec_location.lower()
        
        if preferred_lower in rec_lower or rec_lower in preferred_lower:
            return 1.0
        elif any(word in rec_lower for word in preferred_lower.split()):
            return 0.7
        else:
            return 0.0
    
    def _check_cuisine_match(self, recommendation: Dict[str, Any], preferred_cuisine: str) -> float:
        """Check if recommendation matches preferred cuisine."""
        rec_cuisine = recommendation.get("cuisine", "")
        preferred_lower = preferred_cuisine.lower()
        rec_lower = rec_cuisine.lower()
        
        if preferred_lower == rec_lower:
            return 1.0
        elif preferred_lower in rec_lower or rec_lower in preferred_lower:
            return 0.8
        else:
            return 0.0
    
    def _check_budget_match(self, recommendation: Dict[str, Any], max_budget: int) -> float:
        """Check if recommendation matches budget constraint."""
        rec_cost = recommendation.get("cost_for_two", 0)
        
        if rec_cost <= max_budget:
            # Better score for significantly under budget
            if rec_cost <= max_budget * 0.8:
                return 1.0
            else:
                return 0.8
        else:
            # Penalty for over budget
            over_budget_ratio = rec_cost / max_budget
            if over_budget_ratio <= 1.2:
                return 0.3
            else:
                return 0.0
    
    def _check_rating_match(self, recommendation: Dict[str, Any], min_rating: float) -> float:
        """Check if recommendation meets minimum rating requirement."""
        rec_rating = recommendation.get("rating", 0)
        
        if rec_rating >= min_rating:
            # Bonus for significantly exceeding minimum
            if rec_rating >= min_rating + 0.5:
                return 1.0
            else:
                return 0.8
        else:
            # Penalty for below minimum
            rating_diff = min_rating - rec_rating
            if rating_diff <= 0.2:
                return 0.3
            else:
                return 0.0
    
    def _check_occasion_match(self, recommendation: Dict[str, Any], occasion: str) -> float:
        """Check if recommendation is suitable for the occasion."""
        best_for = recommendation.get("best_for", "")
        highlights = recommendation.get("highlights", [])
        
        occasion_lower = occasion.lower()
        best_for_lower = best_for.lower()
        
        # Check best_for field
        if occasion_lower in best_for_lower:
            return 1.0
        
        # Check highlights
        for highlight in highlights:
            if occasion_lower in highlight.lower():
                return 0.8
        
        # Check reasons
        reasons = recommendation.get("reasons", [])
        for reason in reasons:
            if occasion_lower in reason.lower():
                return 0.6
        
        return 0.3  # Default low score
    
    def _extract_response_time(self, recommendations: Dict[str, Any]) -> float:
        """Extract response time from recommendation metadata."""
        metadata = recommendations.get("pipeline_metadata", {})
        return float(metadata.get("response_time_ms", 0))
    
    def _calculate_explanation_quality(self, recommendations: List[Dict[str, Any]]) -> float:
        """Calculate quality of explanations provided."""
        if not recommendations:
            return 0.0
        
        total_quality = 0.0
        
        for rec in recommendations:
            quality_score = 0.0
            
            # Check for reasons
            reasons = rec.get("reasons", [])
            if not reasons:
                quality_score += 0.0
            else:
                # Length and specificity
                avg_reason_length = sum(len(reason.split()) for reason in reasons) / len(reasons)
                if avg_reason_length >= 8:
                    quality_score += 0.4
                elif avg_reason_length >= 5:
                    quality_score += 0.2
                
                # Avoid generic terms
                generic_terms = ["good", "nice", "great", "excellent", "amazing"]
                non_generic_count = sum(
                    1 for reason in reasons
                    if not any(term in reason.lower() for term in generic_terms)
                )
                if non_generic_count == len(reasons):
                    quality_score += 0.3
                elif non_generic_count >= len(reasons) / 2:
                    quality_score += 0.15
                
                # Specific details
                specific_details = sum(
                    1 for reason in reasons
                    if any(detail in reason.lower() for detail in ["price", "rating", "location", "cuisine", "ambiance"])
                )
                if specific_details > 0:
                    quality_score += 0.3
            
            total_quality += min(quality_score, 1.0)
        
        return total_quality / len(recommendations)
    
    def _calculate_ranking_consistency(self, recommendations: List[Dict[str, Any]]) -> float:
        """Calculate consistency of ranking with match scores."""
        if len(recommendations) < 2:
            return 1.0  # Perfect consistency for single recommendation
        
        # Check if match scores are in descending order
        scores = [rec.get("match_score", 0) for rec in recommendations]
        
        consistency_score = 1.0
        for i in range(len(scores) - 1):
            if scores[i] < scores[i + 1]:
                consistency_score -= 0.2  # Penalty for each inversion
        
        # Check if ranking positions make sense
        for i, rec in enumerate(recommendations):
            expected_rank = rec.get("rank", i + 1)
            if expected_rank != i + 1:
                consistency_score -= 0.1
        
        return max(consistency_score, 0.0)
    
    def _calculate_hallucination_penalty(self, recommendations: List[Dict[str, Any]]) -> float:
        """Calculate penalty for hallucinated information."""
        if not recommendations:
            return 0.0
        
        penalty = 0.0
        
        for rec in recommendations:
            # Check for obviously fake restaurant names
            restaurant_name = rec.get("restaurant_name", "")
            fake_patterns = ["test", "sample", "demo", "fake", "example", "placeholder"]
            
            if any(pattern in restaurant_name.lower() for pattern in fake_patterns):
                penalty += 0.5
            
            # Check for unrealistic match scores
            match_score = rec.get("match_score", 0)
            if match_score > 1.0 or match_score < 0:
                penalty += 0.3
            
            # Check for nonsensical explanations
            reasons = rec.get("reasons", [])
            for reason in reasons:
                if any(pattern in reason.lower() for pattern in fake_patterns):
                    penalty += 0.2
            
            # Check for inconsistent information
            price_indication = rec.get("price_indication", "")
            if price_indication and "unknown" in price_indication.lower():
                penalty += 0.1
        
        return min(penalty / len(recommendations), 1.0)
    
    def _calculate_budget_compliance(
        self,
        recommendations: List[Dict[str, Any]],
        user_preferences: Dict[str, Any]
    ) -> float:
        """Calculate budget compliance rate."""
        max_budget = user_preferences.get("max_cost_for_two")
        if not max_budget:
            return 1.0  # No budget constraint
        
        if not recommendations:
            return 1.0
        
        compliant_count = 0
        for rec in recommendations:
            cost = rec.get("cost_for_two", 0)
            if cost <= max_budget:
                compliant_count += 1
        
        return compliant_count / len(recommendations)
    
    def _calculate_rating_compliance(
        self,
        recommendations: List[Dict[str, Any]],
        user_preferences: Dict[str, Any]
    ) -> float:
        """Calculate rating compliance rate."""
        min_rating = user_preferences.get("min_rating")
        if not min_rating:
            return 1.0  # No rating constraint
        
        if not recommendations:
            return 1.0
        
        compliant_count = 0
        for rec in recommendations:
            rating = rec.get("rating", 0)
            if rating >= min_rating:
                compliant_count += 1
        
        return compliant_count / len(recommendations)
    
    def _calculate_location_compliance(
        self,
        recommendations: List[Dict[str, Any]],
        user_preferences: Dict[str, Any]
    ) -> float:
        """Calculate location compliance rate."""
        preferred_location = user_preferences.get("location")
        if not preferred_location:
            return 1.0  # No location constraint
        
        if not recommendations:
            return 1.0
        
        compliant_count = 0
        for rec in recommendations:
            location = rec.get("location", "")
            if self._check_location_match(rec, preferred_location) > 0.5:
                compliant_count += 1
        
        return compliant_count / len(recommendations)
    
    def _calculate_cuisine_compliance(
        self,
        recommendations: List[Dict[str, Any]],
        user_preferences: Dict[str, Any]
    ) -> float:
        """Calculate cuisine compliance rate."""
        preferred_cuisine = user_preferences.get("cuisine")
        if not preferred_cuisine:
            return 1.0  # No cuisine constraint
        
        if not recommendations:
            return 1.0
        
        compliant_count = 0
        for rec in recommendations:
            cuisine = rec.get("cuisine", "")
            if self._check_cuisine_match(rec, preferred_cuisine) > 0.5:
                compliant_count += 1
        
        return compliant_count / len(recommendations)
    
    def _calculate_variety_score(self, recommendations: List[Dict[str, Any]]) -> float:
        """Calculate variety in recommendations."""
        if len(recommendations) < 2:
            return 1.0
        
        # Cuisine variety
        cuisines = [rec.get("cuisine", "") for rec in recommendations]
        unique_cuisines = len(set(cuisines))
        cuisine_variety = unique_cuisines / len(cuisines)
        
        # Price range variety
        price_indications = [rec.get("price_indication", "") for rec in recommendations]
        unique_prices = len(set(price_indications))
        price_variety = unique_prices / len(price_indications) if price_indications else 1.0
        
        # Overall variety
        return (cuisine_variety + price_variety) / 2
    
    def _calculate_overall_score(self, metrics: Dict[str, float]) -> float:
        """Calculate overall quality score."""
        total_score = 0.0
        total_weight = 0.0
        
        for metric, weight in self.metric_weights.items():
            if metric in metrics:
                if metric == "response_time_ms":
                    # Lower response time is better
                    value = max(0, 1 - (metrics[metric] / 2000))  # Normalize to 0-1
                elif metric == "hallucination_penalty":
                    # Lower penalty is better
                    value = 1 - metrics[metric]
                else:
                    # Higher score is better
                    value = metrics[metric]
                
                total_score += value * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _validate_against_expected(
        self,
        recommendations: List[Dict[str, Any]],
        user_preferences: Dict[str, Any],
        expected_outcomes: Dict[str, Any]
    ) -> Dict[str, float]:
        """Validate recommendations against expected outcomes."""
        validation_metrics = {}
        
        # Minimum recommendations check
        min_recs = expected_outcomes.get("min_recommendations", 0)
        validation_metrics["min_recommendations_met"] = 1.0 if len(recommendations) >= min_recs else 0.0
        
        # Cuisine match check
        expected_cuisine = expected_outcomes.get("cuisine_match")
        if expected_cuisine and recommendations:
            matches = sum(
                1 for rec in recommendations
                if rec.get("cuisine", "").lower() == expected_cuisine.lower()
            )
            validation_metrics["cuisine_match_met"] = matches / len(recommendations)
        
        # Location match check
        expected_location = expected_outcomes.get("location_match")
        if expected_location and recommendations:
            matches = sum(
                1 for rec in recommendations
                if self._check_location_match(rec, expected_location) > 0.5
            )
            validation_metrics["location_match_met"] = matches / len(recommendations)
        
        # Budget compliance check
        if expected_outcomes.get("budget_compliance"):
            validation_metrics["budget_compliance_met"] = self._calculate_budget_compliance(
                recommendations, user_preferences
            )
        
        # Rating compliance check
        if expected_outcomes.get("rating_compliance"):
            validation_metrics["rating_compliance_met"] = self._calculate_rating_compliance(
                recommendations, user_preferences
            )
        
        # Fallback handling check
        if expected_outcomes.get("fallback_handling"):
            # Check if fallback was used appropriately
            fallback_used = any(
                rec.get("restaurant_name", "").lower() in ["fallback", "default", "alternative"]
                for rec in recommendations
            )
            validation_metrics["fallback_handled"] = 1.0 if fallback_used else 0.0
        
        return validation_metrics
    
    def calculate_batch_metrics(
        self,
        batch_results: List[Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Calculate metrics for a batch of evaluation results.
        
        Args:
            batch_results: List of (recommendations, preferences, expected_outcomes) tuples
            
        Returns:
            Batch-level metrics
        """
        if not batch_results:
            return {}
        
        all_metrics = []
        for recommendations, preferences, expected_outcomes in batch_results:
            metrics = self.calculate_metrics(recommendations, preferences, expected_outcomes)
            all_metrics.append(metrics)
        
        # Calculate averages
        batch_metrics = {}
        metric_keys = set()
        for metrics in all_metrics:
            metric_keys.update(metrics.keys())
        
        for key in metric_keys:
            values = [m.get(key, 0) for m in all_metrics if key in m]
            if values:
                batch_metrics[f"avg_{key}"] = sum(values) / len(values)
                batch_metrics[f"min_{key}"] = min(values)
                batch_metrics[f"max_{key}"] = max(values)
        
        # Calculate success rates
        success_thresholds = {
            "relevance_score": 0.7,
            "explanation_quality": 0.6,
            "ranking_consistency": 0.8,
            "overall_score": 0.7
        }
        
        for metric, threshold in success_thresholds.items():
            if f"avg_{metric}" in batch_metrics:
                success_count = sum(
                    1 for m in all_metrics
                    if m.get(metric, 0) >= threshold
                )
                batch_metrics[f"{metric}_success_rate"] = success_count / len(all_metrics)
        
        return batch_metrics
    
    def get_metric_descriptions(self) -> Dict[str, str]:
        """Get descriptions of all calculated metrics."""
        return {
            "relevance_score": "How well recommendations match user preferences (0-1)",
            "response_time_ms": "Time taken to generate recommendations (milliseconds)",
            "explanation_quality": "Quality and specificity of explanations (0-1)",
            "ranking_consistency": "Consistency between rankings and scores (0-1)",
            "hallucination_penalty": "Penalty for hallucinated information (0-1, lower is better)",
            "budget_compliance": "Rate of recommendations within budget (0-1)",
            "rating_compliance": "Rate of recommendations meeting minimum rating (0-1)",
            "location_compliance": "Rate of recommendations in preferred location (0-1)",
            "cuisine_compliance": "Rate of recommendations matching preferred cuisine (0-1)",
            "variety_score": "Variety in cuisine and price ranges (0-1)",
            "overall_score": "Weighted overall quality score (0-1)"
        }
