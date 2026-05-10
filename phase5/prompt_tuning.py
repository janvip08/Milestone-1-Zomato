"""Prompt/Ranking Tuning Module: Optimizes prompts and ranking logic."""

from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime
from dataclasses import dataclass
import json
import re

from ..phase3.prompt_builder import PromptBuilder
from ..phase2.filter_engine import FilterEngine
from ..phase2.ranker_v1 import RankerV1


@dataclass
class PromptVariant:
    """A variant of a prompt template for testing."""
    variant_id: str
    template_name: str
    template_content: str
    description: str
    created_at: datetime
    performance_metrics: Dict[str, float]


@dataclass
class TuningResult:
    """Result of a tuning experiment."""
    experiment_id: str
    variant_id: str
    test_results: List[Dict[str, Any]]
    average_metrics: Dict[str, float]
    improvement_over_baseline: Dict[str, float]
    timestamp: datetime


class PromptTuningModule:
    """Module for tuning and optimizing prompt templates and ranking logic."""
    
    def __init__(self, prompt_builder: PromptBuilder, filter_engine: FilterEngine, ranker: RankerV1):
        """
        Initialize the prompt tuning module.
        
        Args:
            prompt_builder: The prompt builder to tune
            filter_engine: The filter engine to optimize
            ranker: The ranking engine to tune
        """
        self.logger = logging.getLogger(__name__)
        self.prompt_builder = prompt_builder
        self.filter_engine = filter_engine
        self.ranker = ranker
        
        # Prompt variants storage
        self.prompt_variants: Dict[str, PromptVariant] = {}
        self.tuning_history: List[TuningResult] = []
        
        # Tuning configuration
        self.tuning_config = {
            "max_variants_per_template": 10,
            "min_test_samples": 5,
            "improvement_threshold": 0.05,  # 5% improvement
            "test_scenarios": []
        }
        
        self.logger.info("Prompt tuning module initialized")
    
    def create_prompt_variants(self, template_name: str, num_variants: int = 3) -> List[PromptVariant]:
        """
        Create multiple variants of a prompt template for testing.
        
        Args:
            template_name: Name of the template to create variants for
            num_variants: Number of variants to create
            
        Returns:
            List of created prompt variants
        """
        self.logger.info(f"Creating {num_variants} variants for template: {template_name}")
        
        # Get original template
        original_template = self.prompt_builder.templates.get(template_name)
        if not original_template:
            raise ValueError(f"Template {template_name} not found")
        
        variants = []
        
        for i in range(num_variants):
            variant = self._create_variant(template_name, original_template, i)
            self.prompt_variants[variant.variant_id] = variant
            variants.append(variant)
        
        self.logger.info(f"Created {len(variants)} prompt variants")
        return variants
    
    def _create_variant(self, template_name: str, original_template: str, variant_index: int) -> PromptVariant:
        """Create a single variant of a prompt template."""
        variant_id = f"{template_name}_variant_{variant_index + 1}"
        
        # Different variation strategies
        strategies = [
            self._add_few_shot_examples,
            self._modify_system_prompt,
            self._adjust_output_format,
            self._enhance_context_description,
            self._add_constraints
        ]
        
        strategy = strategies[variant_index % len(strategies)]
        variant_content = strategy(original_template)
        
        return PromptVariant(
            variant_id=variant_id,
            template_name=template_name,
            template_content=variant_content,
            description=f"Variant using {strategy.__name__} strategy",
            created_at=datetime.now(),
            performance_metrics={}
        )
    
    def _add_few_shot_examples(self, template: str) -> str:
        """Add few-shot examples to the template."""
        examples = """
## Examples:
Example 1:
User Preferences: {"location": "Downtown", "cuisine": "Italian", "budget": 1000}
Optimal Recommendation: {"restaurant": "Bella Italia", "reasons": ["Perfect Italian match", "Within budget", "High rating"]}

Example 2:
User Preferences: {"location": "Koramangala", "cuisine": "Indian", "budget": 800}
Optimal Recommendation: {"restaurant": "Spice Garden", "reasons": ["Authentic Indian", "Great value", "Family friendly"]}

"""
        
        # Insert examples before the main content
        if "## Task:" in template:
            return template.replace("## Task:", examples + "## Task:")
        else:
            return examples + template
    
    def _modify_system_prompt(self, template: str) -> str:
        """Modify the system prompt for better performance."""
        enhanced_system = """You are an expert restaurant recommendation system with deep knowledge of:
- Local cuisine specialties and restaurant quality
- User preference matching and personalization
- Budget-conscious recommendations
- Dining occasion optimization

Your recommendations should be:
- Highly relevant to user preferences
- Honest and accurate
- Well-explained with specific reasons
- Considerate of budget constraints

"""
        
        return enhanced_system + template
    
    def _adjust_output_format(self, template: str) -> str:
        """Adjust the output format for better structure."""
        enhanced_format = """
## Output Format Requirements:
- Return valid JSON only
- Include specific, actionable reasons
- Provide accurate match scores (0.0-1.0)
- Ensure ranking consistency with scores
- Avoid generic explanations

"""
        
        return template + enhanced_format
    
    def _enhance_context_description(self, template: str) -> str:
        """Enhance the context description in the template."""
        enhanced_context = """
## Enhanced Context Analysis:
Please analyze:
1. How well each restaurant matches ALL user preferences
2. Value proposition (quality vs price)
3. Unique selling points
4. Suitability for specific occasions
5. Potential drawbacks or considerations

"""
        
        return enhanced_context + template
    
    def _add_constraints(self, template: str) -> str:
        """Add specific constraints to the template."""
        constraints = """
## Important Constraints:
- Do NOT recommend restaurants outside the specified budget
- Do NOT recommend restaurants below the minimum rating
- Do NOT make up information about restaurants
- Do NOT use generic or template responses
- Do NOT recommend the same restaurant multiple times

"""
        
        return template + constraints
    
    def test_prompt_variants(
        self,
        template_name: str,
        test_scenarios: List[Dict[str, Any]],
        baseline_metrics: Optional[Dict[str, float]] = None
    ) -> List[TuningResult]:
        """
        Test prompt variants against test scenarios.
        
        Args:
            template_name: Name of the template being tested
            test_scenarios: List of test scenarios to evaluate
            baseline_metrics: Baseline metrics for comparison
            
        Returns:
            List of tuning results
        """
        self.logger.info(f"Testing variants for template: {template_name}")
        
        results = []
        
        # Get all variants for this template
        variants = [
            variant for variant in self.prompt_variants.values()
            if variant.template_name == template_name
        ]
        
        for variant in variants:
            self.logger.info(f"Testing variant: {variant.variant_id}")
            
            # Temporarily replace template
            original_template = self.prompt_builder.templates[template_name]
            self.prompt_builder.templates[template_name] = variant.template_content
            
            try:
                # Test variant
                test_results = []
                for scenario in test_scenarios:
                    result = self._test_single_scenario(scenario)
                    test_results.append(result)
                
                # Calculate metrics
                avg_metrics = self._calculate_average_metrics(test_results)
                
                # Compare with baseline
                improvement = {}
                if baseline_metrics:
                    for metric, baseline_val in baseline_metrics.items():
                        current_val = avg_metrics.get(metric, 0)
                        if metric == "response_time_ms":
                            improvement[metric] = (baseline_val - current_val) / baseline_val
                        else:
                            improvement[metric] = (current_val - baseline_val) / baseline_val
                
                # Create tuning result
                tuning_result = TuningResult(
                    experiment_id=f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    variant_id=variant.variant_id,
                    test_results=test_results,
                    average_metrics=avg_metrics,
                    improvement_over_baseline=improvement,
                    timestamp=datetime.now()
                )
                
                results.append(tuning_result)
                variant.performance_metrics = avg_metrics
                
            finally:
                # Restore original template
                self.prompt_builder.templates[template_name] = original_template
        
        self.tuning_history.extend(results)
        self.logger.info(f"Completed testing {len(results)} variants")
        return results
    
    def _test_single_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single scenario with current prompt configuration."""
        # This would integrate with the actual recommendation engine
        # For now, return mock results
        return {
            "scenario_id": scenario.get("id", "unknown"),
            "relevance_score": 0.8 + (hash(scenario.get("id", "")) % 10) / 50,
            "response_time_ms": 800 + (hash(scenario.get("id", "")) % 200),
            "explanation_quality": 0.7 + (hash(scenario.get("id", "")) % 15) / 50,
            "ranking_consistency": 0.85 + (hash(scenario.get("id", "")) % 10) / 100
        }
    
    def _calculate_average_metrics(self, test_results: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate average metrics from test results."""
        if not test_results:
            return {}
        
        metrics = {}
        metric_keys = set()
        
        # Collect all metric keys
        for result in test_results:
            metric_keys.update(result.keys())
        
        # Calculate averages
        for key in metric_keys:
            if key != "scenario_id":  # Skip scenario ID
                values = [result.get(key, 0) for result in test_results if key in result]
                if values:
                    metrics[key] = sum(values) / len(values)
        
        return metrics
    
    def select_best_variant(self, template_name: str) -> Optional[PromptVariant]:
        """
        Select the best performing variant for a template.
        
        Args:
            template_name: Name of the template
            
        Returns:
            Best performing variant or None
        """
        variants = [
            variant for variant in self.prompt_variants.values()
            if variant.template_name == template_name and variant.performance_metrics
        ]
        
        if not variants:
            return None
        
        # Select based on primary metric (relevance_score)
        best_variant = max(
            variants,
            key=lambda v: v.performance_metrics.get("relevance_score", 0)
        )
        
        self.logger.info(f"Best variant for {template_name}: {best_variant.variant_id}")
        return best_variant
    
    def apply_best_variant(self, template_name: str) -> bool:
        """
        Apply the best performing variant to the prompt builder.
        
        Args:
            template_name: Name of the template
            
        Returns:
            True if variant was applied, False otherwise
        """
        best_variant = self.select_best_variant(template_name)
        if not best_variant:
            return False
        
        self.prompt_builder.templates[template_name] = best_variant.template_content
        self.logger.info(f"Applied best variant {best_variant.variant_id} to {template_name}")
        return True
    
    def optimize_filtering_logic(self, test_scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Optimize the filtering logic based on test results.
        
        Args:
            test_scenarios: Test scenarios to evaluate against
            
        Returns:
            Optimization results
        """
        self.logger.info("Optimizing filtering logic")
        
        # Test current filtering logic
        current_results = []
        for scenario in test_scenarios:
            preferences = scenario["preferences"]
            candidates = scenario.get("candidates", [])
            
            # Apply current filtering
            filtered = self.filter_engine.filter_restaurants(candidates, preferences)
            
            current_results.append({
                "scenario_id": scenario.get("id"),
                "candidates_before": len(candidates),
                "candidates_after": len(filtered),
                "filter_rate": 1 - (len(filtered) / len(candidates)) if candidates else 0
            })
        
        # Analyze results
        avg_filter_rate = sum(r["filter_rate"] for r in current_results) / len(current_results)
        
        # Generate optimization suggestions
        suggestions = []
        if avg_filter_rate > 0.8:
            suggestions.append("Filtering is too aggressive - consider relaxing constraints")
        elif avg_filter_rate < 0.3:
            suggestions.append("Filtering is too lenient - consider tightening constraints")
        
        return {
            "current_performance": {
                "average_filter_rate": avg_filter_rate,
                "results": current_results
            },
            "optimization_suggestions": suggestions
        }
    
    def optimize_ranking_logic(self, test_scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Optimize the ranking logic based on test results.
        
        Args:
            test_scenarios: Test scenarios to evaluate against
            
        Returns:
            Optimization results
        """
        self.logger.info("Optimizing ranking logic")
        
        # Test different ranking weights
        weight_combinations = [
            {"rating": 0.5, "cost": 0.3, "cuisine": 0.2},
            {"rating": 0.4, "cost": 0.4, "cuisine": 0.2},
            {"rating": 0.3, "cost": 0.5, "cuisine": 0.2},
            {"rating": 0.6, "cost": 0.2, "cuisine": 0.2}
        ]
        
        results = {}
        
        for weights in weight_combinations:
            weight_key = str(weights)
            results[weight_key] = []
            
            for scenario in test_scenarios:
                preferences = scenario["preferences"]
                candidates = scenario.get("candidates", [])
                
                # Apply ranking with current weights
                ranked = self.ranker_v1.rank_restaurants(candidates, preferences)
                
                # Calculate ranking quality (mock for now)
                quality = 0.7 + (hash(str(weights)) % 20) / 100
                
                results[weight_key].append(quality)
        
        # Find best weights
        best_weights = None
        best_avg_quality = 0
        
        for weights, qualities in results.items():
            avg_quality = sum(qualities) / len(qualities)
            if avg_quality > best_avg_quality:
                best_avg_quality = avg_quality
                best_weights = weights
        
        return {
            "best_weights": best_weights,
            "best_quality": best_avg_quality,
            "all_results": results
        }
    
    def generate_tuning_report(self) -> Dict[str, Any]:
        """Generate a comprehensive tuning report."""
        return {
            "summary": {
                "total_variants_created": len(self.prompt_variants),
                "total_experiments_run": len(self.tuning_history),
                "templates_tested": list(set(v.template_name for v in self.prompt_variants.values()))
            },
            "best_variants": {
                template: self.select_best_variant(template).variant_id
                for template in set(v.template_name for v in self.prompt_variants.values())
                if self.select_best_variant(template)
            },
            "recent_experiments": [
                {
                    "experiment_id": exp.experiment_id,
                    "variant_id": exp.variant_id,
                    "timestamp": exp.timestamp.isoformat(),
                    "avg_relevance": exp.average_metrics.get("relevance_score", 0),
                    "improvement": exp.improvement_over_baseline.get("relevance_score", 0)
                }
                for exp in self.tuning_history[-10:]  # Last 10 experiments
            ],
            "recommendations": self._generate_tuning_recommendations()
        }
    
    def _generate_tuning_recommendations(self) -> List[str]:
        """Generate recommendations based on tuning results."""
        recommendations = []
        
        if not self.tuning_history:
            recommendations.append("Run tuning experiments to generate recommendations")
            return recommendations
        
        # Analyze recent experiments
        recent_experiments = self.tuning_history[-10:]
        
        # Check for successful improvements
        successful_experiments = [
            exp for exp in recent_experiments
            if any(imp > 0.05 for imp in exp.improvement_over_baseline.values())
        ]
        
        if len(successful_experiments) == 0:
            recommendations.append("Consider more aggressive prompt variations")
            recommendations.append("Review test scenarios for better coverage")
        else:
            recommendations.append(f"Apply successful variants from {len(successful_experiments)} experiments")
        
        # Check for consistent issues
        avg_response_time = sum(
            exp.average_metrics.get("response_time_ms", 0)
            for exp in recent_experiments
        ) / len(recent_experiments)
        
        if avg_response_time > 1500:
            recommendations.append("Optimize prompts for faster response times")
        
        return recommendations
    
    def export_tuning_data(self, filepath: str) -> None:
        """Export tuning data to file."""
        data = {
            "prompt_variants": {
                variant_id: {
                    "template_name": variant.template_name,
                    "template_content": variant.template_content,
                    "description": variant.description,
                    "created_at": variant.created_at.isoformat(),
                    "performance_metrics": variant.performance_metrics
                }
                for variant_id, variant in self.prompt_variants.items()
            },
            "tuning_history": [
                {
                    "experiment_id": exp.experiment_id,
                    "variant_id": exp.variant_id,
                    "test_results": exp.test_results,
                    "average_metrics": exp.average_metrics,
                    "improvement_over_baseline": exp.improvement_over_baseline,
                    "timestamp": exp.timestamp.isoformat()
                }
                for exp in self.tuning_history
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        self.logger.info(f"Tuning data exported to {filepath}")
    
    def load_tuning_data(self, filepath: str) -> None:
        """Load tuning data from file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Load variants
        for variant_id, variant_data in data.get("prompt_variants", {}).items():
            variant = PromptVariant(
                variant_id=variant_id,
                template_name=variant_data["template_name"],
                template_content=variant_data["template_content"],
                description=variant_data["description"],
                created_at=datetime.fromisoformat(variant_data["created_at"]),
                performance_metrics=variant_data["performance_metrics"]
            )
            self.prompt_variants[variant_id] = variant
        
        # Load history
        for exp_data in data.get("tuning_history", []):
            exp = TuningResult(
                experiment_id=exp_data["experiment_id"],
                variant_id=exp_data["variant_id"],
                test_results=exp_data["test_results"],
                average_metrics=exp_data["average_metrics"],
                improvement_over_baseline=exp_data["improvement_over_baseline"],
                timestamp=datetime.fromisoformat(exp_data["timestamp"])
            )
            self.tuning_history.append(exp)
        
        self.logger.info(f"Tuning data loaded from {filepath}")
