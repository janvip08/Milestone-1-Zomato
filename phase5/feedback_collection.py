"""Feedback Collection Layer: Collects and manages user feedback for recommendations."""

from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json
from enum import Enum


class FeedbackType(Enum):
    """Types of feedback."""
    RATING = "rating"
    LIKE_DISLIKE = "like_dislike"
    DETAILED = "detailed"
    CORRECTION = "correction"


class FeedbackSource(Enum):
    """Sources of feedback."""
    WEB_UI = "web_ui"
    CLI = "cli"
    API = "api"
    SURVEY = "survey"


@dataclass
class UserFeedback:
    """Individual user feedback entry."""
    feedback_id: str
    user_id: Optional[str]
    session_id: str
    recommendation_id: str
    restaurant_name: str
    feedback_type: FeedbackType
    feedback_source: FeedbackSource
    rating: Optional[int]  # 1-5 scale
    like_dislike: Optional[bool]
    detailed_feedback: Optional[str]
    correction_data: Optional[Dict[str, Any]]
    user_preferences: Dict[str, Any]
    timestamp: datetime
    context: Dict[str, Any]


@dataclass
class FeedbackSummary:
    """Summary of feedback data."""
    total_feedback: int
    average_rating: float
    rating_distribution: Dict[int, int]
    like_dislike_ratio: Dict[str, int]
    common_issues: List[str]
    satisfaction_rate: float
    feedback_by_source: Dict[str, int]
    feedback_by_type: Dict[str, int]
    time_period: str


class FeedbackCollectionLayer:
    """Layer for collecting and managing user feedback."""
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the feedback collection layer.
        
        Args:
            storage_path: Optional path to store feedback data
        """
        self.logger = logging.getLogger(__name__)
        self.storage_path = storage_path or "data/feedback.json"
        
        # In-memory storage
        self.feedback_entries: List[UserFeedback] = []
        
        # Feedback processing configuration
        self.config = {
            "max_feedback_per_user": 100,
            "feedback_retention_days": 365,
            "auto_analyze_threshold": 50,
            "min_rating_for_analysis": 3
        }
        
        # Load existing feedback
        self._load_feedback()
        
        self.logger.info("Feedback collection layer initialized")
    
    def collect_rating_feedback(
        self,
        recommendation_id: str,
        restaurant_name: str,
        rating: int,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        user_preferences: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Collect rating feedback (1-5 scale).
        
        Args:
            recommendation_id: ID of the recommendation
            restaurant_name: Name of the restaurant
            rating: Rating from 1-5
            user_id: Optional user identifier
            session_id: Optional session identifier
            user_preferences: User preferences used
            context: Additional context
            
        Returns:
            Feedback ID
        """
        if not (1 <= rating <= 5):
            raise ValueError("Rating must be between 1 and 5")
        
        feedback = UserFeedback(
            feedback_id=self._generate_feedback_id(),
            user_id=user_id,
            session_id=session_id or self._generate_session_id(),
            recommendation_id=recommendation_id,
            restaurant_name=restaurant_name,
            feedback_type=FeedbackType.RATING,
            feedback_source=FeedbackSource.WEB_UI,  # Default
            rating=rating,
            like_dislike=None,
            detailed_feedback=None,
            correction_data=None,
            user_preferences=user_preferences or {},
            timestamp=datetime.now(),
            context=context or {}
        )
        
        self._add_feedback(feedback)
        return feedback.feedback_id
    
    def collect_like_dislike_feedback(
        self,
        recommendation_id: str,
        restaurant_name: str,
        like_dislike: bool,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        user_preferences: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Collect like/dislike feedback.
        
        Args:
            recommendation_id: ID of the recommendation
            restaurant_name: Name of the restaurant
            like_dislike: True for like, False for dislike
            user_id: Optional user identifier
            session_id: Optional session identifier
            user_preferences: User preferences used
            context: Additional context
            
        Returns:
            Feedback ID
        """
        feedback = UserFeedback(
            feedback_id=self._generate_feedback_id(),
            user_id=user_id,
            session_id=session_id or self._generate_session_id(),
            recommendation_id=recommendation_id,
            restaurant_name=restaurant_name,
            feedback_type=FeedbackType.LIKE_DISLIKE,
            feedback_source=FeedbackSource.WEB_UI,  # Default
            rating=None,
            like_dislike=like_dislike,
            detailed_feedback=None,
            correction_data=None,
            user_preferences=user_preferences or {},
            timestamp=datetime.now(),
            context=context or {}
        )
        
        self._add_feedback(feedback)
        return feedback.feedback_id
    
    def collect_detailed_feedback(
        self,
        recommendation_id: str,
        restaurant_name: str,
        detailed_feedback: str,
        rating: Optional[int] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        user_preferences: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Collect detailed text feedback.
        
        Args:
            recommendation_id: ID of the recommendation
            restaurant_name: Name of the restaurant
            detailed_feedback: Detailed feedback text
            rating: Optional rating (1-5)
            user_id: Optional user identifier
            session_id: Optional session identifier
            user_preferences: User preferences used
            context: Additional context
            
        Returns:
            Feedback ID
        """
        if rating and not (1 <= rating <= 5):
            raise ValueError("Rating must be between 1 and 5")
        
        feedback = UserFeedback(
            feedback_id=self._generate_feedback_id(),
            user_id=user_id,
            session_id=session_id or self._generate_session_id(),
            recommendation_id=recommendation_id,
            restaurant_name=restaurant_name,
            feedback_type=FeedbackType.DETAILED,
            feedback_source=FeedbackSource.WEB_UI,  # Default
            rating=rating,
            like_dislike=None,
            detailed_feedback=detailed_feedback,
            correction_data=None,
            user_preferences=user_preferences or {},
            timestamp=datetime.now(),
            context=context or {}
        )
        
        self._add_feedback(feedback)
        return feedback.feedback_id
    
    def collect_correction_feedback(
        self,
        recommendation_id: str,
        restaurant_name: str,
        correction_data: Dict[str, Any],
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        user_preferences: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Collect correction feedback (user correcting system errors).
        
        Args:
            recommendation_id: ID of the recommendation
            restaurant_name: Name of the restaurant
            correction_data: Correction information
            user_id: Optional user identifier
            session_id: Optional session identifier
            user_preferences: User preferences used
            context: Additional context
            
        Returns:
            Feedback ID
        """
        feedback = UserFeedback(
            feedback_id=self._generate_feedback_id(),
            user_id=user_id,
            session_id=session_id or self._generate_session_id(),
            recommendation_id=recommendation_id,
            restaurant_name=restaurant_name,
            feedback_type=FeedbackType.CORRECTION,
            feedback_source=FeedbackSource.WEB_UI,  # Default
            rating=None,
            like_dislike=None,
            detailed_feedback=None,
            correction_data=correction_data,
            user_preferences=user_preferences or {},
            timestamp=datetime.now(),
            context=context or {}
        )
        
        self._add_feedback(feedback)
        return feedback.feedback_id
    
    def _add_feedback(self, feedback: UserFeedback) -> None:
        """Add feedback to storage."""
        # Check user feedback limits
        if feedback.user_id:
            user_feedback_count = sum(
                1 for f in self.feedback_entries
                if f.user_id == feedback.user_id
            )
            if user_feedback_count >= self.config["max_feedback_per_user"]:
                self.logger.warning(f"User {feedback.user_id} exceeded feedback limit")
                return
        
        self.feedback_entries.append(feedback)
        
        # Save to storage
        self._save_feedback()
        
        # Auto-analyze if threshold reached
        if len(self.feedback_entries) % self.config["auto_analyze_threshold"] == 0:
            self._auto_analyze_feedback()
        
        self.logger.info(f"Collected feedback: {feedback.feedback_id}")
    
    def get_feedback_summary(
        self,
        days_back: int = 30,
        restaurant_name: Optional[str] = None
    ) -> FeedbackSummary:
        """
        Get summary of feedback data.
        
        Args:
            days_back: Number of days to look back
            restaurant_name: Optional restaurant filter
            
        Returns:
            Feedback summary
        """
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        # Filter feedback
        filtered_feedback = [
            f for f in self.feedback_entries
            if f.timestamp >= cutoff_date and
            (not restaurant_name or f.restaurant_name == restaurant_name)
        ]
        
        if not filtered_feedback:
            return FeedbackSummary(
                total_feedback=0,
                average_rating=0.0,
                rating_distribution={},
                like_dislike_ratio={"like": 0, "dislike": 0},
                common_issues=[],
                satisfaction_rate=0.0,
                feedback_by_source={},
                feedback_by_type={},
                time_period=f"Last {days_back} days"
            )
        
        # Calculate metrics
        total_feedback = len(filtered_feedback)
        
        # Rating metrics
        ratings = [f.rating for f in filtered_feedback if f.rating is not None]
        average_rating = sum(ratings) / len(ratings) if ratings else 0.0
        
        rating_distribution = {}
        for rating in range(1, 6):
            rating_distribution[rating] = sum(1 for r in ratings if r == rating)
        
        # Like/dislike metrics
        like_dislike_feedback = [
            f for f in filtered_feedback
            if f.like_dislike is not None
        ]
        likes = sum(1 for f in like_dislike_feedback if f.like_dislike)
        dislikes = len(like_dislike_feedback) - likes
        
        # Satisfaction rate (ratings >= 4 + likes)
        satisfied = sum(1 for r in ratings if r >= 4) + likes
        satisfaction_rate = satisfied / total_feedback if total_feedback > 0 else 0.0
        
        # Common issues from detailed feedback
        common_issues = self._extract_common_issues(filtered_feedback)
        
        # Feedback by source
        feedback_by_source = {}
        for feedback in filtered_feedback:
            source = feedback.feedback_source.value
            feedback_by_source[source] = feedback_by_source.get(source, 0) + 1
        
        # Feedback by type
        feedback_by_type = {}
        for feedback in filtered_feedback:
            ftype = feedback.feedback_type.value
            feedback_by_type[ftype] = feedback_by_type.get(ftype, 0) + 1
        
        return FeedbackSummary(
            total_feedback=total_feedback,
            average_rating=average_rating,
            rating_distribution=rating_distribution,
            like_dislike_ratio={"like": likes, "dislike": dislikes},
            common_issues=common_issues,
            satisfaction_rate=satisfaction_rate,
            feedback_by_source=feedback_by_source,
            feedback_by_type=feedback_by_type,
            time_period=f"Last {days_back} days"
        )
    
    def _extract_common_issues(self, feedback_list: List[UserFeedback]) -> List[str]:
        """Extract common issues from detailed feedback."""
        issues = []
        
        # Analyze detailed feedback
        detailed_feedback = [
            f.detailed_feedback for f in feedback_list
            if f.detailed_feedback
        ]
        
        # Common issue patterns
        issue_patterns = {
            "price": ["expensive", "price", "cost", "budget"],
            "quality": ["quality", "taste", "food", "service"],
            "location": ["location", "distance", "far"],
            "recommendation": ["recommend", "suggestion", "wrong"],
            "explanation": ["explanation", "reason", "why"]
        }
        
        for feedback_text in detailed_feedback:
            feedback_lower = feedback_text.lower()
            for issue_type, keywords in issue_patterns.items():
                if any(keyword in feedback_lower for keyword in keywords):
                    issues.append(issue_type)
        
        # Count and return top issues
        issue_counts = {}
        for issue in issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        return [
            issue for issue, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
    
    def get_restaurant_feedback(self, restaurant_name: str) -> Dict[str, Any]:
        """Get feedback specific to a restaurant."""
        restaurant_feedback = [
            f for f in self.feedback_entries
            if f.restaurant_name == restaurant_name
        ]
        
        if not restaurant_feedback:
            return {"restaurant": restaurant_name, "feedback_count": 0}
        
        # Calculate metrics
        ratings = [f.rating for f in restaurant_feedback if f.rating is not None]
        average_rating = sum(ratings) / len(ratings) if ratings else 0.0
        
        like_dislike_feedback = [
            f for f in restaurant_feedback
            if f.like_dislike is not None
        ]
        likes = sum(1 for f in like_dislike_feedback if f.like_dislike)
        dislikes = len(like_dislike_feedback) - likes
        
        return {
            "restaurant": restaurant_name,
            "feedback_count": len(restaurant_feedback),
            "average_rating": average_rating,
            "rating_count": len(ratings),
            "likes": likes,
            "dislikes": dislikes,
            "detailed_feedback": [
                f.detailed_feedback for f in restaurant_feedback
                if f.detailed_feedback
            ]
        }
    
    def get_user_feedback_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get feedback history for a specific user."""
        user_feedback = [
            f for f in self.feedback_entries
            if f.user_id == user_id
        ]
        
        return [
            {
                "feedback_id": f.feedback_id,
                "restaurant_name": f.restaurant_name,
                "feedback_type": f.feedback_type.value,
                "rating": f.rating,
                "like_dislike": f.like_dislike,
                "detailed_feedback": f.detailed_feedback,
                "timestamp": f.timestamp.isoformat()
            }
            for f in sorted(user_feedback, key=lambda x: x.timestamp, reverse=True)
        ]
    
    def analyze_feedback_trends(self) -> Dict[str, Any]:
        """Analyze trends in feedback over time."""
        if len(self.feedback_entries) < 10:
            return {"message": "Insufficient data for trend analysis"}
        
        # Group by week
        weekly_data = {}
        for feedback in self.feedback_entries:
            week_key = feedback.timestamp.strftime("%Y-W%U")
            if week_key not in weekly_data:
                weekly_data[week_key] = {"ratings": [], "likes": 0, "dislikes": 0}
            
            if feedback.rating:
                weekly_data[week_key]["ratings"].append(feedback.rating)
            if feedback.like_dislike is not None:
                if feedback.like_dislike:
                    weekly_data[week_key]["likes"] += 1
                else:
                    weekly_data[week_key]["dislikes"] += 1
        
        # Calculate weekly averages
        trend_data = {}
        for week, data in weekly_data.items():
            avg_rating = sum(data["ratings"]) / len(data["ratings"]) if data["ratings"] else 0
            total_feedback = len(data["ratings"]) + data["likes"] + data["dislikes"]
            
            trend_data[week] = {
                "average_rating": avg_rating,
                "total_feedback": total_feedback,
                "satisfaction_rate": (sum(1 for r in data["ratings"] if r >= 4) + data["likes"]) / total_feedback if total_feedback > 0 else 0
            }
        
        return {
            "weekly_trends": trend_data,
            "overall_trend": self._calculate_trend_direction(trend_data)
        }
    
    def _calculate_trend_direction(self, trend_data: Dict[str, Dict[str, float]]) -> str:
        """Calculate overall trend direction."""
        if len(trend_data) < 2:
            return "insufficient_data"
        
        weeks = sorted(trend_data.keys())
        recent_avg = sum(trend_data[weeks[-1]]["average_rating"] for _ in range(3)) / min(3, len(weeks))
        older_avg = sum(trend_data[weeks[0]]["average_rating"] for _ in range(3)) / min(3, len(weeks))
        
        if recent_avg > older_avg + 0.1:
            return "improving"
        elif recent_avg < older_avg - 0.1:
            return "declining"
        else:
            return "stable"
    
    def _auto_analyze_feedback(self) -> None:
        """Automatically analyze feedback and log insights."""
        summary = self.get_feedback_summary(days_back=7)
        
        if summary.total_feedback > 0:
            self.logger.info(f"Auto-analysis: {summary.total_feedback} feedback entries")
            self.logger.info(f"Average rating: {summary.average_rating:.2f}")
            self.logger.info(f"Satisfaction rate: {summary.satisfaction_rate:.2f}")
            
            if summary.common_issues:
                self.logger.info(f"Common issues: {', '.join(summary.common_issues)}")
    
    def _generate_feedback_id(self) -> str:
        """Generate unique feedback ID."""
        import uuid
        return f"fb_{uuid.uuid4().hex[:8]}"
    
    def _generate_session_id(self) -> str:
        """Generate session ID."""
        import uuid
        return f"session_{uuid.uuid4().hex[:8]}"
    
    def _load_feedback(self) -> None:
        """Load feedback from storage."""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                
                for feedback_data in data.get("feedback", []):
                    feedback = UserFeedback(
                        feedback_id=feedback_data["feedback_id"],
                        user_id=feedback_data.get("user_id"),
                        session_id=feedback_data["session_id"],
                        recommendation_id=feedback_data["recommendation_id"],
                        restaurant_name=feedback_data["restaurant_name"],
                        feedback_type=FeedbackType(feedback_data["feedback_type"]),
                        feedback_source=FeedbackSource(feedback_data["feedback_source"]),
                        rating=feedback_data.get("rating"),
                        like_dislike=feedback_data.get("like_dislike"),
                        detailed_feedback=feedback_data.get("detailed_feedback"),
                        correction_data=feedback_data.get("correction_data"),
                        user_preferences=feedback_data.get("user_preferences", {}),
                        timestamp=datetime.fromisoformat(feedback_data["timestamp"]),
                        context=feedback_data.get("context", {})
                    )
                    self.feedback_entries.append(feedback)
                
                self.logger.info(f"Loaded {len(self.feedback_entries)} feedback entries")
        except Exception as e:
            self.logger.warning(f"Failed to load feedback: {e}")
    
    def _save_feedback(self) -> None:
        """Save feedback to storage."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            data = {
                "feedback": [
                    {
                        "feedback_id": f.feedback_id,
                        "user_id": f.user_id,
                        "session_id": f.session_id,
                        "recommendation_id": f.recommendation_id,
                        "restaurant_name": f.restaurant_name,
                        "feedback_type": f.feedback_type.value,
                        "feedback_source": f.feedback_source.value,
                        "rating": f.rating,
                        "like_dislike": f.like_dislike,
                        "detailed_feedback": f.detailed_feedback,
                        "correction_data": f.correction_data,
                        "user_preferences": f.user_preferences,
                        "timestamp": f.timestamp.isoformat(),
                        "context": f.context
                    }
                    for f in self.feedback_entries
                ]
            }
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save feedback: {e}")
    
    def cleanup_old_feedback(self) -> None:
        """Clean up old feedback beyond retention period."""
        cutoff_date = datetime.now() - timedelta(days=self.config["feedback_retention_days"])
        
        old_feedback = [
            f for f in self.feedback_entries
            if f.timestamp < cutoff_date
        ]
        
        if old_feedback:
            self.feedback_entries = [
                f for f in self.feedback_entries
                if f.timestamp >= cutoff_date
            ]
            
            self._save_feedback()
            self.logger.info(f"Cleaned up {len(old_feedback)} old feedback entries")
    
    def export_feedback_data(self, filepath: str, days_back: int = 30) -> None:
        """Export feedback data to file."""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "time_period": f"Last {days_back} days",
            "feedback": [
                asdict(f) for f in self.feedback_entries
                if f.timestamp >= cutoff_date
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        self.logger.info(f"Exported feedback data to {filepath}")


# Import os for file operations
import os
