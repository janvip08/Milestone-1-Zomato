"""Evaluation Report Generator: Generates comprehensive evaluation reports."""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json
from enum import Enum

from .evaluation_harness import EvaluationResult, EvaluationSummary
from .feedback_collection import FeedbackSummary
from .hallucination_detector import HallucinationReport, RankingConsistencyReport
from .metrics import EvaluationMetrics


class ReportFormat(Enum):
    """Report output formats."""
    JSON = "json"
    HTML = "html"
    PDF = "pdf"
    MARKDOWN = "markdown"


@dataclass
class EvaluationReport:
    """Complete evaluation report."""
    report_id: str
    timestamp: datetime
    evaluation_summary: EvaluationSummary
    feedback_summary: Optional[FeedbackSummary]
    hallucination_reports: List[HallucinationReport]
    consistency_reports: List[RankingConsistencyReport]
    detailed_results: List[EvaluationResult]
    recommendations: List[str]
    next_steps: List[str]
    metadata: Dict[str, Any]


class EvaluationReportGenerator:
    """Generates comprehensive evaluation reports."""
    
    def __init__(self):
        """Initialize the report generator."""
        self.logger = logging.getLogger(__name__)
        self.metrics_calculator = EvaluationMetrics()
        
        # Report templates
        self.report_templates = {
            "executive": self._get_executive_template(),
            "technical": self._get_technical_template(),
            "detailed": self._get_detailed_template()
        }
        
        self.logger.info("Evaluation report generator initialized")
    
    def generate_report(
        self,
        evaluation_summary: EvaluationSummary,
        detailed_results: List[EvaluationResult],
        feedback_summary: Optional[FeedbackSummary] = None,
        hallucination_reports: Optional[List[HallucinationReport]] = None,
        consistency_reports: Optional[List[RankingConsistencyReport]] = None,
        report_type: str = "detailed",
        format: ReportFormat = ReportFormat.JSON
    ) -> EvaluationReport:
        """
        Generate a comprehensive evaluation report.
        
        Args:
            evaluation_summary: Summary of evaluation results
            detailed_results: Detailed evaluation results
            feedback_summary: Optional user feedback summary
            hallucination_reports: Optional hallucination detection reports
            consistency_reports: Optional ranking consistency reports
            report_type: Type of report to generate
            format: Output format
            
        Returns:
            Generated evaluation report
        """
        self.logger.info(f"Generating {report_type} evaluation report")
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            evaluation_summary, detailed_results, feedback_summary
        )
        
        # Generate next steps
        next_steps = self._generate_next_steps(
            evaluation_summary, hallucination_reports, consistency_reports
        )
        
        # Create report
        report = EvaluationReport(
            report_id=self._generate_report_id(),
            timestamp=datetime.now(),
            evaluation_summary=evaluation_summary,
            feedback_summary=feedback_summary,
            hallucination_reports=hallucination_reports or [],
            consistency_reports=consistency_reports or [],
            detailed_results=detailed_results,
            recommendations=recommendations,
            next_steps=next_steps,
            metadata={
                "report_type": report_type,
                "format": format.value,
                "generator_version": "1.0"
            }
        )
        
        self.logger.info(f"Report generated: {report.report_id}")
        return report
    
    def _generate_recommendations(
        self,
        evaluation_summary: EvaluationSummary,
        detailed_results: List[EvaluationResult],
        feedback_summary: Optional[FeedbackSummary]
    ) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        # Performance-based recommendations
        avg_response_time = evaluation_summary.average_metrics.get("response_time_ms", 0)
        if avg_response_time > 1500:
            recommendations.append("Optimize LLM model selection for faster response times")
            recommendations.append("Implement response caching for repeated queries")
        
        avg_relevance = evaluation_summary.average_metrics.get("relevance_score", 0)
        if avg_relevance < 0.7:
            recommendations.append("Improve prompt templates for better relevance matching")
            recommendations.append("Enhance candidate filtering logic")
        
        avg_explanation = evaluation_summary.average_metrics.get("explanation_quality", 0)
        if avg_explanation < 0.6:
            recommendations.append("Refine prompt templates for better explanations")
            recommendations.append("Add few-shot examples for improved output quality")
        
        # Issue-based recommendations
        common_issues = evaluation_summary.common_issues
        if any("hallucination" in issue.lower() for issue in common_issues):
            recommendations.append("Add hallucination detection and filtering")
            recommendations.append("Improve prompt constraints and validation")
        
        if any("ranking" in issue.lower() for issue in common_issues):
            recommendations.append("Fix ranking consistency logic")
            recommendations.append("Add score validation and normalization")
        
        # Feedback-based recommendations
        if feedback_summary:
            if feedback_summary.average_rating < 3.5:
                recommendations.append("Address user satisfaction issues")
                recommendations.append("Review recommendation quality criteria")
            
            if feedback_summary.satisfaction_rate < 0.7:
                recommendations.append("Improve overall user experience")
                recommendations.append("Add more personalized recommendations")
        
        # Success rate recommendations
        if evaluation_summary.failed_tests > evaluation_summary.passed_tests:
            recommendations.append("Address critical system failures")
            recommendations.append("Implement better error handling")
        
        return recommendations
    
    def _generate_next_steps(
        self,
        evaluation_summary: EvaluationSummary,
        hallucination_reports: Optional[List[HallucinationReport]],
        consistency_reports: Optional[List[RankingConsistencyReport]]
    ) -> List[str]:
        """Generate next steps for improvement."""
        next_steps = []
        
        # Immediate next steps based on critical issues
        critical_issues = [
            issue for issue in evaluation_summary.common_issues
            if "critical" in issue.lower()
        ]
        
        if critical_issues:
            next_steps.append("Address critical issues immediately")
            next_steps.append("Implement hotfixes for system stability")
        
        # Hallucination-related next steps
        if hallucination_reports:
            high_severity = [r for r in hallucination_reports if r.severity in ["high", "critical"]]
            if high_severity:
                next_steps.append("Review and strengthen hallucination detection")
                next_steps.append("Update prompt templates with better constraints")
        
        # Consistency-related next steps
        if consistency_reports:
            next_steps.append("Fix ranking consistency issues")
            next_steps.append("Implement score validation logic")
        
        # Performance next steps
        avg_response_time = evaluation_summary.average_metrics.get("response_time_ms", 0)
        if avg_response_time > 1000:
            next_steps.append("Optimize system performance")
            next_steps.append("Consider model optimization or caching")
        
        # Quality next steps
        avg_relevance = evaluation_summary.average_metrics.get("relevance_score", 0)
        if avg_relevance < 0.8:
            next_steps.append("Run prompt optimization experiments")
            next_steps.append("Collect more user feedback for quality improvement")
        
        # Long-term next steps
        next_steps.append("Schedule regular evaluation cycles")
        next_steps.append("Implement continuous monitoring system")
        next_steps.append("Build automated regression testing")
        
        return next_steps
    
    def format_report(self, report: EvaluationReport, format: ReportFormat = ReportFormat.JSON) -> str:
        """Format report in specified format."""
        if format == ReportFormat.JSON:
            return self._format_json_report(report)
        elif format == ReportFormat.HTML:
            return self._format_html_report(report)
        elif format == ReportFormat.MARKDOWN:
            return self._format_markdown_report(report)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _format_json_report(self, report: EvaluationReport) -> str:
        """Format report as JSON."""
        # Convert dataclasses to dictionaries
        report_dict = asdict(report)
        
        # Convert datetime objects to strings
        report_dict["timestamp"] = report.timestamp.isoformat()
        
        for result in report_dict["detailed_results"]:
            result["timestamp"] = result["timestamp"].isoformat()
        
        for hal_report in report_dict["hallucination_reports"]:
            hal_report["timestamp"] = hal_report["timestamp"].isoformat()
        
        for cons_report in report_dict["consistency_reports"]:
            cons_report["timestamp"] = cons_report["timestamp"].isoformat()
        
        return json.dumps(report_dict, indent=2, default=str)
    
    def _format_html_report(self, report: EvaluationReport) -> str:
        """Format report as HTML."""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Evaluation Report - {report.report_id}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; }}
        .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: #e8f4fd; border-radius: 3px; }}
        .recommendation {{ background-color: #fff3cd; padding: 10px; margin: 5px 0; border-radius: 3px; }}
        .issue {{ background-color: #f8d7da; padding: 10px; margin: 5px 0; border-radius: 3px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Evaluation Report</h1>
        <p><strong>Report ID:</strong> {report.report_id}</p>
        <p><strong>Generated:</strong> {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Report Type:</strong> {report.metadata.get('report_type', 'unknown')}</p>
    </div>
    
    <div class="section">
        <h2>Executive Summary</h2>
        <div class="metric">
            <strong>Total Tests:</strong> {report.evaluation_summary.total_tests}
        </div>
        <div class="metric">
            <strong>Passed:</strong> {report.evaluation_summary.passed_tests}
        </div>
        <div class="metric">
            <strong>Failed:</strong> {report.evaluation_summary.failed_tests}
        </div>
        <div class="metric">
            <strong>Success Rate:</strong> {report.evaluation_summary.passed_tests / report.evaluation_summary.total_tests * 100:.1f}%
        </div>
    </div>
    
    <div class="section">
        <h2>Performance Metrics</h2>
        <table>
            <tr><th>Metric</th><th>Average</th><th>Status</th></tr>
"""
        
        # Add metrics table
        for metric, value in report.evaluation_summary.average_metrics.items():
            status = "Good" if value >= 0.8 else "Needs Improvement" if value >= 0.6 else "Poor"
            html += f"            <tr><td>{metric}</td><td>{value:.3f}</td><td>{status}</td></tr>\n"
        
        html += """
        </table>
    </div>
    
    <div class="section">
        <h2>Common Issues</h2>
"""
        
        for issue in report.evaluation_summary.common_issues:
            html += f'        <div class="issue">{issue}</div>\n'
        
        html += """
    </div>
    
    <div class="section">
        <h2>Recommendations</h2>
"""
        
        for rec in report.recommendations:
            html += f'        <div class="recommendation">{rec}</div>\n'
        
        html += """
    </div>
    
    <div class="section">
        <h2>Next Steps</h2>
        <ul>
"""
        
        for step in report.next_steps:
            html += f'            <li>{step}</li>\n'
        
        html += """
        </ul>
    </div>
    
</body>
</html>
"""
        
        return html
    
    def _format_markdown_report(self, report: EvaluationReport) -> str:
        """Format report as Markdown."""
        md = f"""# Evaluation Report

**Report ID:** {report.report_id}  
**Generated:** {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}  
**Report Type:** {report.metadata.get('report_type', 'unknown')}

## Executive Summary

| Metric | Value |
|--------|-------|
| Total Tests | {report.evaluation_summary.total_tests} |
| Passed | {report.evaluation_summary.passed_tests} |
| Failed | {report.evaluation_summary.failed_tests} |
| Success Rate | {report.evaluation_summary.passed_tests / report.evaluation_summary.total_tests * 100:.1f}% |

## Performance Metrics

| Metric | Average | Status |
|--------|---------|--------|
"""
        
        for metric, value in report.evaluation_summary.average_metrics.items():
            status = "✅ Good" if value >= 0.8 else "⚠️ Needs Improvement" if value >= 0.6 else "❌ Poor"
            md += f"| {metric} | {value:.3f} | {status} |\n"
        
        md += "\n## Common Issues\n\n"
        for issue in report.evaluation_summary.common_issues:
            md += f"- ❌ {issue}\n"
        
        md += "\n## Recommendations\n\n"
        for rec in report.recommendations:
            md += f"- 💡 {rec}\n"
        
        md += "\n## Next Steps\n\n"
        for step in report.next_steps:
            md += f"- 📋 {step}\n"
        
        return md
    
    def _generate_report_id(self) -> str:
        """Generate unique report ID."""
        import uuid
        return f"eval_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    def _get_executive_template(self) -> str:
        """Get executive summary template."""
        return """
# Executive Summary

## Key Metrics
- Overall Success Rate: {success_rate}%
- Average Response Time: {response_time}ms
- User Satisfaction: {satisfaction_rate}

## Critical Issues
{critical_issues}

## Immediate Actions
{immediate_actions}
"""
    
    def _get_technical_template(self) -> str:
        """Get technical report template."""
        return """
# Technical Evaluation Report

## System Performance
{performance_metrics}

## Test Results
{test_results}

## Issues and Fixes
{issues_and_fixes}
"""
    
    def _get_detailed_template(self) -> str:
        """Get detailed report template."""
        return """
# Detailed Evaluation Report

## Overview
{overview}

## Test Scenarios
{test_scenarios}

## Detailed Results
{detailed_results}

## Analysis
{analysis}

## Recommendations
{recommendations}
"""
    
    def save_report(self, report: EvaluationReport, filepath: str, format: ReportFormat = ReportFormat.JSON) -> None:
        """Save report to file."""
        content = self.format_report(report, format)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.logger.info(f"Report saved to {filepath}")
    
    def generate_trend_report(
        self,
        historical_reports: List[EvaluationReport],
        days_back: int = 30
    ) -> Dict[str, Any]:
        """Generate trend analysis report."""
        if len(historical_reports) < 2:
            return {"message": "Insufficient data for trend analysis"}
        
        # Filter by time period
        cutoff_date = datetime.now() - timedelta(days=days_back)
        recent_reports = [
            report for report in historical_reports
            if report.timestamp >= cutoff_date
        ]
        
        if len(recent_reports) < 2:
            return {"message": "Insufficient recent data for trend analysis"}
        
        # Calculate trends
        trends = {}
        
        # Success rate trend
        success_rates = [
            report.evaluation_summary.passed_tests / report.evaluation_summary.total_tests
            for report in recent_reports
        ]
        trends["success_rate_trend"] = self._calculate_trend(success_rates)
        
        # Response time trend
        response_times = [
            report.evaluation_summary.average_metrics.get("response_time_ms", 0)
            for report in recent_reports
        ]
        trends["response_time_trend"] = self._calculate_trend(response_times)
        
        # Relevance score trend
        relevance_scores = [
            report.evaluation_summary.average_metrics.get("relevance_score", 0)
            for report in recent_reports
        ]
        trends["relevance_score_trend"] = self._calculate_trend(relevance_scores)
        
        return {
            "trend_period": f"Last {days_back} days",
            "reports_analyzed": len(recent_reports),
            "trends": trends,
            "overall_direction": self._get_overall_trend_direction(trends)
        }
    
    def _calculate_trend(self, values: List[float]) -> Dict[str, Any]:
        """Calculate trend for a series of values."""
        if len(values) < 2:
            return {"direction": "stable", "change": 0}
        
        # Simple linear trend calculation
        x_values = list(range(len(values)))
        n = len(values)
        
        sum_x = sum(x_values)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(x_values, values))
        sum_x2 = sum(x * x for x in x_values)
        
        # Calculate slope
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        # Determine direction
        if slope > 0.01:
            direction = "improving"
        elif slope < -0.01:
            direction = "declining"
        else:
            direction = "stable"
        
        return {
            "direction": direction,
            "slope": slope,
            "change": values[-1] - values[0] if len(values) > 1 else 0
        }
    
    def _get_overall_trend_direction(self, trends: Dict[str, Any]) -> str:
        """Get overall trend direction from multiple trends."""
        directions = [trend.get("direction", "stable") for trend in trends.values()]
        
        improving_count = directions.count("improving")
        declining_count = directions.count("declining")
        stable_count = directions.count("stable")
        
        if improving_count > declining_count and improving_count > stable_count:
            return "improving"
        elif declining_count > improving_count and declining_count > stable_count:
            return "declining"
        else:
            return "stable"
