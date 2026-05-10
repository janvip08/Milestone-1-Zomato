"""Main entry point and examples for Phase 5 Evaluation, Feedback, and Tuning."""

import os
import sys
import argparse
import logging
from datetime import datetime
from typing import Dict, Any, List

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phase5.evaluation_harness import EvaluationHarness
from phase5.prompt_tuning import PromptTuningModule
from phase5.feedback_collection import FeedbackCollectionLayer
from phase5.test_scenarios import TestScenarios
from phase5.metrics import EvaluationMetrics
from phase5.report_generator import EvaluationReportGenerator, ReportFormat
from phase5.hallucination_detector import HallucinationDetector, RankingConsistencyTracker
from phase5.improvement_backlog import ImprovementBacklog, Priority, Category


def setup_logging(level: str = "INFO"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def example_comprehensive_evaluation():
    """Example of running comprehensive evaluation."""
    print("=" * 60)
    print("PHASE 5 COMPREHENSIVE EVALUATION EXAMPLE")
    print("=" * 60)
    
    # Mock recommendation engine for demonstration
    class MockRecommendationEngine:
        def generate_recommendations_complete(self, preferences, response_type="recommendation", max_recommendations=5):
            # Simulate recommendation generation
            return {
                "recommendations": [
                    {
                        "rank": 1,
                        "restaurant_name": "Test Restaurant 1",
                        "match_score": 0.85,
                        "reasons": ["Good rating", "Within budget"],
                        "highlights": ["Nice ambiance", "Good service"],
                        "price_indication": "Moderate",
                        "best_for": "Casual dining"
                    },
                    {
                        "rank": 2,
                        "restaurant_name": "Test Restaurant 2",
                        "match_score": 0.78,
                        "reasons": ["Authentic cuisine", "Good value"],
                        "highlights": ["Traditional recipes", "Family friendly"],
                        "price_indication": "Budget-friendly",
                        "best_for": "Family meal"
                    }
                ],
                "summary": "Found 2 good restaurants matching your preferences",
                "total_matches": 2,
                "pipeline_metadata": {
                    "total_candidates": 5,
                    "candidates_used": 2,
                    "response_time_ms": 850,
                    "groq_model": "llama3-8b-8192"
                }
            }
    
    # Initialize components
    engine = MockRecommendationEngine()
    metrics_calculator = EvaluationMetrics()
    
    # Create evaluation harness
    eval_harness = EvaluationHarness(engine, metrics_calculator)
    
    # Run comprehensive evaluation
    print("Running comprehensive evaluation...")
    summary = eval_harness.run_comprehensive_evaluation()
    
    # Display results
    print(f"\nEvaluation Results:")
    print(f"Total Tests: {summary.total_tests}")
    print(f"Passed: {summary.passed_tests}")
    print(f"Failed: {summary.failed_tests}")
    print(f"Success Rate: {summary.passed_tests/summary.total_tests*100:.1f}%")
    
    print(f"\nAverage Metrics:")
    for metric, value in summary.average_metrics.items():
        print(f"  {metric}: {value:.3f}")
    
    print(f"\nCommon Issues:")
    for issue in summary.common_issues:
        print(f"  - {issue}")
    
    print(f"\nRecommendations:")
    for rec in summary.recommendations:
        print(f"  - {rec}")


def example_prompt_tuning():
    """Example of prompt tuning."""
    print("\n" + "=" * 60)
    print("PROMPT TUNING EXAMPLE")
    print("=" * 60)
    
    # Mock components for demonstration
    class MockPromptBuilder:
        def __init__(self):
            self.templates = {
                "recommendation": "Generate recommendations for {preferences} with candidates {candidates}"
            }
    
    class MockFilterEngine:
        pass
    
    class MockRanker:
        pass
    
    # Initialize components
    prompt_builder = MockPromptBuilder()
    filter_engine = MockFilterEngine()
    ranker = MockRanker()
    
    # Create prompt tuning module
    tuning_module = PromptTuningModule(prompt_builder, filter_engine, ranker)
    
    # Create prompt variants
    print("Creating prompt variants...")
    variants = tuning_module.create_prompt_variants("recommendation", num_variants=3)
    
    print(f"Created {len(variants)} variants:")
    for variant in variants:
        print(f"  - {variant.variant_id}: {variant.description}")
    
    # Test variants (mock)
    print("\nTesting variants...")
    test_scenarios = [
        {"id": "test1", "preferences": {"location": "Downtown", "cuisine": "Italian"}},
        {"id": "test2", "preferences": {"location": "Koramangala", "budget": 1000}}
    ]
    
    # Mock baseline metrics
    baseline_metrics = {"relevance_score": 0.75, "response_time_ms": 1000}
    
    results = tuning_module.test_prompt_variants("recommendation", test_scenarios, baseline_metrics)
    
    print(f"Test results for {len(results)} variants:")
    for result in results:
        print(f"  - {result.variant_id}: Avg relevance = {result.average_metrics.get('relevance_score', 0):.3f}")
    
    # Select best variant
    best_variant = tuning_module.select_best_variant("recommendation")
    if best_variant:
        print(f"\nBest variant: {best_variant.variant_id}")
        print(f"Performance: {best_variant.performance_metrics}")


def example_feedback_collection():
    """Example of feedback collection."""
    print("\n" + "=" * 60)
    print("FEEDBACK COLLECTION EXAMPLE")
    print("=" * 60)
    
    # Create feedback collection layer
    feedback_layer = FeedbackCollectionLayer()
    
    # Collect different types of feedback
    print("Collecting sample feedback...")
    
    # Rating feedback
    rating_id = feedback_layer.collect_rating_feedback(
        recommendation_id="rec_001",
        restaurant_name="Test Restaurant",
        rating=4,
        user_preferences={"location": "Downtown", "cuisine": "Italian"}
    )
    print(f"Collected rating feedback: {rating_id}")
    
    # Like/dislike feedback
    like_id = feedback_layer.collect_like_dislike_feedback(
        recommendation_id="rec_002",
        restaurant_name="Another Restaurant",
        like_dislike=True,
        user_preferences={"location": "Bellandur", "budget": 1000}
    )
    print(f"Collected like/dislike feedback: {like_id}")
    
    # Detailed feedback
    detailed_id = feedback_layer.collect_detailed_feedback(
        recommendation_id="rec_003",
        restaurant_name="Third Restaurant",
        detailed_feedback="Great food but service was slow. Ambiance is nice for families.",
        rating=3,
        user_preferences={"location": "Indiranagar", "occasion": "family_dining"}
    )
    print(f"Collected detailed feedback: {detailed_id}")
    
    # Get feedback summary
    summary = feedback_layer.get_feedback_summary(days_back=30)
    
    print(f"\nFeedback Summary:")
    print(f"Total Feedback: {summary.total_feedback}")
    print(f"Average Rating: {summary.average_rating:.2f}")
    print(f"Satisfaction Rate: {summary.satisfaction_rate:.2f}")
    print(f"Like/Dislike: {summary.like_dislike_ratio['like']} likes, {summary.like_dislike_ratio['dislike']} dislikes")
    
    if summary.common_issues:
        print(f"Common Issues: {', '.join(summary.common_issues)}")


def example_hallucination_detection():
    """Example of hallucination detection."""
    print("\n" + "=" * 60)
    print("HALLUCINATION DETECTION EXAMPLE")
    print("=" * 60)
    
    # Create hallucination detector
    detector = HallucinationDetector()
    
    # Load sample restaurant database
    sample_restaurants = [
        {"name": "Real Restaurant 1", "cuisine": "Italian", "location": "Downtown"},
        {"name": "Real Restaurant 2", "cuisine": "Indian", "location": "Bellandur"},
        {"name": "Real Restaurant 3", "cuisine": "Chinese", "location": "Koramangala"}
    ]
    detector.load_restaurant_database(sample_restaurants)
    
    # Test recommendations with potential hallucinations
    test_recommendations = [
        {
            "rank": 1,
            "restaurant_name": "Test Restaurant",  # Fake
            "match_score": 1.5,  # Unrealistic
            "reasons": ["Good food", "Nice place"],  # Generic
            "rating": 6.0,  # Unrealistic
            "cuisine": "Exotic Cuisine",  # Unknown
            "location": "Unknown Area"  # Unknown
        },
        {
            "rank": 2,
            "restaurant_name": "Real Restaurant 1",  # Real
            "match_score": 0.85,
            "reasons": ["Authentic Italian cuisine", "Great ambiance"],
            "rating": 4.2,
            "cuisine": "Italian",
            "location": "Downtown"
        }
    ]
    
    user_preferences = {"location": "Downtown", "cuisine": "Italian"}
    
    # Detect hallucinations
    print("Detecting hallucinations...")
    hallucination_reports = detector.detect_hallucinations(test_recommendations, user_preferences)
    
    print(f"Found {len(hallucination_reports)} hallucination issues:")
    for report in hallucination_reports:
        print(f"  - {report.hallucination_type}: {report.description} (Severity: {report.severity})")
    
    # Check ranking consistency
    consistency_tracker = RankingConsistencyTracker()
    consistency_reports = consistency_tracker.check_ranking_consistency(test_recommendations)
    
    print(f"\nFound {len(consistency_reports)} consistency issues:")
    for report in consistency_reports:
        print(f"  - {report.inconsistency_type}: {report.description} (Severity: {report.severity})")


def example_improvement_backlog():
    """Example of improvement backlog management."""
    print("\n" + "=" * 60)
    print("IMPROVEMENT BACKLOG EXAMPLE")
    print("=" * 60)
    
    # Create improvement backlog
    backlog = ImprovementBacklog()
    
    # Add improvement items
    print("Adding improvement items...")
    
    item1_id = backlog.add_item(
        title="Improve response time performance",
        description="Optimize LLM model selection and implement caching to reduce response times",
        category=Category.PERFORMANCE,
        priority=Priority.HIGH,
        estimated_effort=16,
        tags=["performance", "optimization", "llm"],
        acceptance_criteria=[
            "Average response time < 1000ms",
            "95th percentile response time < 1500ms",
            "No degradation in recommendation quality"
        ]
    )
    print(f"Added item: {item1_id}")
    
    item2_id = backlog.add_item(
        title="Enhance explanation quality",
        description="Improve prompt templates to generate more specific and helpful explanations",
        category=Category.QUALITY,
        priority=Priority.MEDIUM,
        estimated_effort=12,
        tags=["quality", "prompts", "explanations"],
        acceptance_criteria=[
            "Explanation quality score > 0.8",
            "No generic explanations",
            "Specific details included"
        ]
    )
    print(f"Added item: {item2_id}")
    
    item3_id = backlog.add_item(
        title="Implement hallucination detection",
        description="Add comprehensive hallucination detection and filtering system",
        category=Category.SAFETY,
        priority=Priority.CRITICAL,
        estimated_effort=20,
        tags=["safety", "hallucination", "detection"],
        dependencies=[item1_id],  # Depends on performance improvement
        acceptance_criteria=[
            "Zero critical hallucinations",
            "Detection accuracy > 95%",
            "No false positives"
        ]
    )
    print(f"Added item: {item3_id}")
    
    # Get backlog summary
    summary = backlog.get_backlog_summary()
    
    print(f"\nBacklog Summary:")
    print(f"Total Items: {summary['total_items']}")
    print(f"Completion Rate: {summary['completion_rate']:.2%}")
    print(f"Total Estimated Effort: {summary['total_estimated_effort']} hours")
    
    print(f"\nBy Status:")
    for status, count in summary['by_status'].items():
        print(f"  {status}: {count}")
    
    print(f"\nBy Priority:")
    for priority, count in summary['by_priority'].items():
        print(f"  {priority}: {count}")
    
    # Generate improvement plan
    plan = backlog.generate_improvement_plan(days_ahead=30)
    
    print(f"\n30-Day Improvement Plan:")
    print(f"Total Items: {plan['total_items']}")
    print(f"Estimated Effort: {plan['estimated_effort']} hours")
    
    for item in plan['items']:
        can_start_text = "✅" if item['can_start'] else "❌"
        print(f"  {can_start_text} {item['title']} ({item['priority']})")


def example_report_generation():
    """Example of report generation."""
    print("\n" + "=" * 60)
    print("REPORT GENERATION EXAMPLE")
    print("=" * 60)
    
    # Create mock data for report
    from phase5.evaluation_harness import EvaluationSummary
    from phase5.feedback_collection import FeedbackSummary
    
    # Mock evaluation summary
    eval_summary = EvaluationSummary(
        total_tests=20,
        passed_tests=17,
        failed_tests=3,
        average_metrics={
            "relevance_score": 0.82,
            "response_time_ms": 950,
            "explanation_quality": 0.75,
            "ranking_consistency": 0.88
        },
        common_issues=["Generic explanations", "Slow response times"],
        recommendations=["Improve prompt templates", "Optimize performance"]
    )
    
    # Mock feedback summary
    feedback_summary = FeedbackSummary(
        total_feedback=45,
        average_rating=4.1,
        rating_distribution={1: 2, 2: 3, 3: 8, 4: 15, 5: 17},
        like_dislike_ratio={"like": 35, "dislike": 10},
        common_issues=["price concerns", "service quality"],
        satisfaction_rate=0.78,
        feedback_by_source={"web_ui": 30, "api": 10, "cli": 5},
        feedback_by_type={"rating": 35, "like_dislike": 10},
        time_period="Last 30 days"
    )
    
    # Create report generator
    report_generator = EvaluationReportGenerator()
    
    # Generate report
    print("Generating evaluation report...")
    report = report_generator.generate_report(
        evaluation_summary=eval_summary,
        detailed_results=[],
        feedback_summary=feedback_summary,
        report_type="detailed"
    )
    
    print(f"Report generated: {report.report_id}")
    print(f"Generated at: {report.timestamp}")
    
    # Format as different types
    print("\n--- JSON Format (first 200 chars) ---")
    json_report = report_generator.format_report(report, ReportFormat.JSON)
    print(json_report[:200] + "...")
    
    print("\n--- Markdown Format ---")
    md_report = report_generator.format_report(report, ReportFormat.MARKDOWN)
    print(md_report[:500] + "...")
    
    # Save report
    report_generator.save_report(report, "phase5/sample_report.json", ReportFormat.JSON)
    report_generator.save_report(report, "phase5/sample_report.md", ReportFormat.MARKDOWN)
    print("\nReports saved to phase5/sample_report.json and phase5/sample_report.md")


def main():
    """Main function to run Phase 5 examples."""
    parser = argparse.ArgumentParser(
        description="Phase 5 Evaluation, Feedback, and Tuning Examples",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m phase5.main evaluation     # Run comprehensive evaluation
  python -m phase5.main tuning          # Run prompt tuning
  python -m phase5.main feedback         # Run feedback collection
  python -m phase5.main hallucination    # Run hallucination detection
  python -m phase5.main backlog         # Run improvement backlog
  python -m phase5.main report          # Generate reports
  python -m phase5.main all             # Run all examples
        """
    )
    
    parser.add_argument(
        "command",
        choices=["evaluation", "tuning", "feedback", "hallucination", "backlog", "report", "all"],
        help="Example to run"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    
    print("PHASE 5 EVALUATION, FEEDBACK, AND TUNING EXAMPLES")
    print("=" * 60)
    
    # Run requested example
    if args.command == "evaluation":
        example_comprehensive_evaluation()
    elif args.command == "tuning":
        example_prompt_tuning()
    elif args.command == "feedback":
        example_feedback_collection()
    elif args.command == "hallucination":
        example_hallucination_detection()
    elif args.command == "backlog":
        example_improvement_backlog()
    elif args.command == "report":
        example_report_generation()
    elif args.command == "all":
        example_comprehensive_evaluation()
        example_prompt_tuning()
        example_feedback_collection()
        example_hallucination_detection()
        example_improvement_backlog()
        example_report_generation()
    
    print("\n" + "=" * 60)
    print("PHASE 5 EXAMPLES COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
