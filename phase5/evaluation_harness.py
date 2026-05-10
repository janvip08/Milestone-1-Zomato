"""Evaluation Harness: Comprehensive testing framework for recommendation quality."""

from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime
from dataclasses import dataclass
import json

from .test_scenarios import TestScenarios
from .metrics import EvaluationMetrics
from .feedback_collection import FeedbackCollectionLayer


@dataclass
class EvaluationResult:
    """Result of a single evaluation test."""
    test_id: str
    scenario_name: str
    input_preferences: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    metrics: Dict[str, float]
    issues: List[str]
    timestamp: datetime


@dataclass
class EvaluationSummary:
    """Summary of evaluation results."""
    total_tests: int
    passed_tests: int
    failed_tests: int
    average_metrics: Dict[str, float]
    common_issues: List[str]
    recommendations: List[str]


class EvaluationHarness:
    """Main evaluation framework for testing recommendation quality."""
    
    def __init__(self, recommendation_engine, metrics_calculator=None):
        """
        Initialize the evaluation harness.
        
        Args:
            recommendation_engine: The recommendation system to test
            metrics_calculator: Optional custom metrics calculator
        """
        self.logger = logging.getLogger(__name__)
        self.recommendation_engine = recommendation_engine
        self.metrics_calculator = metrics_calculator or EvaluationMetrics()
        self.test_scenarios = TestScenarios()
        self.feedback_layer = FeedbackCollectionLayer()
        
        # Evaluation history
        self.evaluation_history: List[EvaluationResult] = []
        self.current_session_results: List[EvaluationResult] = []
        
        self.logger.info("Evaluation harness initialized")
    
    def run_comprehensive_evaluation(
        self,
        test_categories: Optional[List[str]] = None,
        include_user_feedback: bool = False
    ) -> EvaluationSummary:
        """
        Run comprehensive evaluation of the recommendation system.
        
        Args:
            test_categories: Specific test categories to run
            include_user_feedback: Whether to include user feedback in evaluation
            
        Returns:
            Summary of evaluation results
        """
        self.logger.info("Starting comprehensive evaluation")
        self.current_session_results = []
        
        # Get test scenarios
        scenarios = self.test_scenarios.get_scenarios(categories=test_categories)
        
        total_tests = len(scenarios)
        passed_tests = 0
        failed_tests = 0
        
        all_metrics = []
        all_issues = []
        
        for scenario in scenarios:
            try:
                result = self._run_single_test(scenario)
                self.current_session_results.append(result)
                
                # Count passed/failed based on metrics
                if self._test_passed(result):
                    passed_tests += 1
                else:
                    failed_tests += 1
                
                # Collect metrics and issues
                all_metrics.append(result.metrics)
                all_issues.extend(result.issues)
                
            except Exception as e:
                self.logger.error(f"Test {scenario['id']} failed: {e}")
                failed_tests += 1
                all_issues.append(f"Test {scenario['id']} crashed: {str(e)}")
        
        # Calculate summary
        summary = self._calculate_summary(
            total_tests, passed_tests, failed_tests, all_metrics, all_issues
        )
        
        # Include user feedback if requested
        if include_user_feedback:
            feedback_summary = self._collect_user_feedback_summary()
            summary.user_feedback = feedback_summary
        
        # Save to history
        self.evaluation_history.extend(self.current_session_results)
        
        self.logger.info(f"Evaluation completed: {passed_tests}/{total_tests} passed")
        return summary
    
    def _run_single_test(self, scenario: Dict[str, Any]) -> EvaluationResult:
        """Run a single test scenario."""
        test_id = scenario["id"]
        scenario_name = scenario["name"]
        input_preferences = scenario["preferences"]
        expected_outcomes = scenario.get("expected_outcomes", {})
        
        self.logger.info(f"Running test: {test_id} - {scenario_name}")
        
        # Generate recommendations
        try:
            recommendations = self.recommendation_engine.generate_recommendations_complete(
                input_preferences,
                response_type=scenario.get("response_type", "recommendation"),
                max_recommendations=scenario.get("max_recommendations", 5)
            )
        except Exception as e:
            raise Exception(f"Recommendation generation failed: {e}")
        
        # Calculate metrics
        metrics = self.metrics_calculator.calculate_metrics(
            recommendations, input_preferences, expected_outcomes
        )
        
        # Detect issues
        issues = self._detect_issues(recommendations, input_preferences, scenario)
        
        return EvaluationResult(
            test_id=test_id,
            scenario_name=scenario_name,
            input_preferences=input_preferences,
            recommendations=recommendations.get("recommendations", []),
            metrics=metrics,
            issues=issues,
            timestamp=datetime.now()
        )
    
    def _test_passed(self, result: EvaluationResult) -> bool:
        """Determine if a test passed based on metrics."""
        # Define passing criteria
        passing_criteria = {
            "relevance_score": 0.7,
            "response_time_ms": 2000,
            "explanation_quality": 0.6,
            "ranking_consistency": 0.8
        }
        
        for metric, threshold in passing_criteria.items():
            if metric in result.metrics:
                if metric == "response_time_ms":
                    if result.metrics[metric] > threshold:
                        return False
                else:
                    if result.metrics[metric] < threshold:
                        return False
        
        # Test passes if no critical issues
        critical_issues = [issue for issue in result.issues if "critical" in issue.lower()]
        return len(critical_issues) == 0
    
    def _detect_issues(
        self,
        recommendations: Dict[str, Any],
        preferences: Dict[str, Any],
        scenario: Dict[str, Any]
    ) -> List[str]:
        """Detect issues in recommendations."""
        issues = []
        rec_list = recommendations.get("recommendations", [])
        
        # Check for empty recommendations
        if not rec_list:
            issues.append("CRITICAL: No recommendations generated")
            return issues
        
        # Check for duplicate recommendations
        restaurant_names = [rec.get("restaurant_name", "") for rec in rec_list]
        if len(set(restaurant_names)) != len(restaurant_names):
            issues.append("Duplicate restaurant recommendations")
        
        # Check for hallucinations
        for rec in rec_list:
            if self._is_hallucination(rec, preferences):
                issues.append(f"Potential hallucination in {rec.get('restaurant_name', 'unknown')}")
        
        # Check ranking consistency
        if not self._check_ranking_consistency(rec_list):
            issues.append("Inconsistent ranking detected")
        
        # Check explanation quality
        for rec in rec_list:
            reasons = rec.get("reasons", [])
            if not reasons or len(reasons) == 0:
                issues.append(f"No explanations provided for {rec.get('restaurant_name', 'unknown')}")
            elif any(len(reason.strip()) < 10 for reason in reasons):
                issues.append(f"Poor quality explanations for {rec.get('restaurant_name', 'unknown')}")
        
        # Check budget compliance
        max_budget = preferences.get("max_cost_for_two")
        if max_budget:
            for rec in rec_list:
                # This would need actual cost data from restaurant
                pass  # Placeholder for cost checking
        
        # Check rating compliance
        min_rating = preferences.get("min_rating")
        if min_rating:
            for rec in rec_list:
                # This would need actual rating data
                pass  # Placeholder for rating checking
        
        return issues
    
    def _is_hallucination(self, recommendation: Dict[str, Any], preferences: Dict[str, Any]) -> bool:
        """Check if recommendation contains hallucinated information."""
        # Basic hallucination detection
        restaurant_name = recommendation.get("restaurant_name", "")
        
        # Check for obviously fake restaurant names
        fake_patterns = ["Test Restaurant", "Sample Place", "Demo Eatery", "Fake Food"]
        if any(pattern in restaurant_name for pattern in fake_patterns):
            return True
        
        # Check for unrealistic match scores
        match_score = recommendation.get("match_score", 0)
        if match_score > 1.0 or match_score < 0:
            return True
        
        # Check for nonsensical explanations
        reasons = recommendation.get("reasons", [])
        for reason in reasons:
            if "test" in reason.lower() or "sample" in reason.lower():
                return True
        
        return False
    
    def _check_ranking_consistency(self, recommendations: List[Dict[str, Any]]) -> bool:
        """Check if rankings are consistent with scores."""
        if len(recommendations) < 2:
            return True
        
        # Check if match scores are in descending order
        scores = [rec.get("match_score", 0) for rec in recommendations]
        return all(scores[i] >= scores[i+1] for i in range(len(scores)-1))
    
    def _calculate_summary(
        self,
        total_tests: int,
        passed_tests: int,
        failed_tests: int,
        all_metrics: List[Dict[str, float]],
        all_issues: List[str]
    ) -> EvaluationSummary:
        """Calculate evaluation summary."""
        # Calculate average metrics
        avg_metrics = {}
        if all_metrics:
            metric_keys = set()
            for metrics in all_metrics:
                metric_keys.update(metrics.keys())
            
            for key in metric_keys:
                values = [m.get(key, 0) for m in all_metrics if key in m]
                if values:
                    avg_metrics[key] = sum(values) / len(values)
        
        # Find common issues
        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        common_issues = sorted(
            [(issue, count) for issue, count in issue_counts.items() if count > 1],
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Generate recommendations
        recommendations = self._generate_recommendations(avg_metrics, common_issues)
        
        return EvaluationSummary(
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            average_metrics=avg_metrics,
            common_issues=[issue for issue, count in common_issues],
            recommendations=recommendations
        )
    
    def _generate_recommendations(
        self,
        metrics: Dict[str, float],
        issues: List[Tuple[str, int]]
    ) -> List[str]:
        """Generate improvement recommendations based on evaluation results."""
        recommendations = []
        
        # Relevance recommendations
        relevance = metrics.get("relevance_score", 0)
        if relevance < 0.7:
            recommendations.append("Improve prompt templates for better relevance matching")
            recommendations.append("Enhance candidate filtering logic")
        
        # Response time recommendations
        response_time = metrics.get("response_time_ms", 0)
        if response_time > 1500:
            recommendations.append("Optimize LLM model selection for faster response")
            recommendations.append("Implement response caching")
        
        # Explanation quality recommendations
        explanation_quality = metrics.get("explanation_quality", 0)
        if explanation_quality < 0.6:
            recommendations.append("Refine prompt templates for better explanations")
            recommendations.append("Add few-shot examples for improved output quality")
        
        # Issue-based recommendations
        issue_texts = [issue for issue, count in issues]
        if any("hallucination" in issue.lower() for issue in issue_texts):
            recommendations.append("Add hallucination detection and filtering")
            recommendations.append("Improve prompt constraints and validation")
        
        if any("ranking" in issue.lower() for issue in issue_texts):
            recommendations.append("Fix ranking consistency logic")
            recommendations.append("Add score validation and normalization")
        
        if any("explanation" in issue.lower() for issue in issue_texts):
            recommendations.append("Enhance explanation generation prompts")
            recommendations.append("Add explanation quality validation")
        
        return recommendations
    
    def _collect_user_feedback_summary(self) -> Dict[str, Any]:
        """Collect summary of user feedback."""
        feedback_data = self.feedback_layer.get_feedback_summary()
        return {
            "total_feedback": feedback_data.get("total_count", 0),
            "average_rating": feedback_data.get("average_rating", 0),
            "common_complaints": feedback_data.get("common_issues", []),
            "satisfaction_rate": feedback_data.get("satisfaction_rate", 0)
        }
    
    def run_regression_test(self, baseline_results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Run regression test against baseline results.
        
        Args:
            baseline_results: Previous evaluation results to compare against
            
        Returns:
            Regression test results
        """
        self.logger.info("Running regression test")
        
        # Get current results for same scenarios
        current_results = []
        for baseline in baseline_results:
            scenario = self.test_scenarios.get_scenario_by_id(baseline.test_id)
            if scenario:
                try:
                    current = self._run_single_test(scenario)
                    current_results.append(current)
                except Exception as e:
                    self.logger.error(f"Regression test for {baseline.test_id} failed: {e}")
        
        # Compare results
        regressions = []
        improvements = []
        
        for baseline, current in zip(baseline_results, current_results):
            comparison = self._compare_results(baseline, current)
            if comparison["status"] == "regression":
                regressions.append(comparison)
            elif comparison["status"] == "improvement":
                improvements.append(comparison)
        
        return {
            "total_comparisons": len(baseline_results),
            "regressions": regressions,
            "improvements": improvements,
            "unchanged": len(baseline_results) - len(regressions) - len(improvements)
        }
    
    def _compare_results(self, baseline: EvaluationResult, current: EvaluationResult) -> Dict[str, Any]:
        """Compare baseline and current results."""
        baseline_passed = self._test_passed(baseline)
        current_passed = self._test_passed(current)
        
        if baseline_passed and not current_passed:
            return {
                "status": "regression",
                "test_id": baseline.test_id,
                "reason": "Test passed in baseline but failed now"
            }
        elif not baseline_passed and current_passed:
            return {
                "status": "improvement", 
                "test_id": baseline.test_id,
                "reason": "Test failed in baseline but passes now"
            }
        
        # Compare key metrics
        metric_regressions = []
        for metric in ["relevance_score", "response_time_ms", "explanation_quality"]:
            if metric in baseline.metrics and metric in current.metrics:
                baseline_val = baseline.metrics[metric]
                current_val = current.metrics[metric]
                
                if metric == "response_time_ms":
                    if current_val > baseline_val * 1.2:  # 20% slower
                        metric_regressions.append(metric)
                else:
                    if current_val < baseline_val * 0.9:  # 10% worse
                        metric_regressions.append(metric)
        
        if metric_regressions:
            return {
                "status": "regression",
                "test_id": baseline.test_id,
                "reason": f"Metric regressions in: {', '.join(metric_regressions)}"
            }
        
        return {
            "status": "unchanged",
            "test_id": baseline.test_id,
            "reason": "No significant changes"
        }
    
    def get_evaluation_history(self) -> List[Dict[str, Any]]:
        """Get evaluation history."""
        return [
            {
                "test_id": result.test_id,
                "scenario_name": result.scenario_name,
                "timestamp": result.timestamp.isoformat(),
                "passed": self._test_passed(result),
                "metrics": result.metrics,
                "issues": result.issues
            }
            for result in self.evaluation_history
        ]
    
    def export_results(self, filepath: str) -> None:
        """Export evaluation results to file."""
        results_data = {
            "evaluation_history": self.get_evaluation_history(),
            "current_session": [
                {
                    "test_id": result.test_id,
                    "scenario_name": result.scenario_name,
                    "input_preferences": result.input_preferences,
                    "recommendations": result.recommendations,
                    "metrics": result.metrics,
                    "issues": result.issues,
                    "timestamp": result.timestamp.isoformat()
                }
                for result in self.current_session_results
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        self.logger.info(f"Evaluation results exported to {filepath}")
    
    def load_baseline(self, filepath: str) -> List[EvaluationResult]:
        """Load baseline results from file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        baseline_results = []
        for result_data in data.get("evaluation_history", []):
            # Convert back to EvaluationResult objects
            result = EvaluationResult(
                test_id=result_data["test_id"],
                scenario_name=result_data["scenario_name"],
                input_preferences=result_data.get("input_preferences", {}),
                recommendations=result_data.get("recommendations", []),
                metrics=result_data.get("metrics", {}),
                issues=result_data.get("issues", []),
                timestamp=datetime.fromisoformat(result_data["timestamp"])
            )
            baseline_results.append(result)
        
        self.logger.info(f"Loaded {len(baseline_results)} baseline results")
        return baseline_results
