"""Improvement Backlog Management: Manages and tracks improvement items."""

from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import uuid


class Priority(Enum):
    """Priority levels for improvement items."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Status(Enum):
    """Status of improvement items."""
    BACKLOG = "backlog"
    IN_PROGRESS = "in_progress"
    TESTING = "testing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Category(Enum):
    """Categories for improvement items."""
    PERFORMANCE = "performance"
    QUALITY = "quality"
    RELIABILITY = "reliability"
    USER_EXPERIENCE = "user_experience"
    SAFETY = "safety"
    INFRASTRUCTURE = "infrastructure"


@dataclass
class ImprovementItem:
    """An improvement item in the backlog."""
    item_id: str
    title: str
    description: str
    category: Category
    priority: Priority
    status: Status
    created_at: datetime
    updated_at: datetime
    due_date: Optional[datetime]
    assigned_to: Optional[str]
    estimated_effort: Optional[int]  # in hours
    actual_effort: Optional[int]
    tags: List[str]
    dependencies: List[str]  # item_ids
    acceptance_criteria: List[str]
    implementation_notes: Optional[str]
    test_results: Optional[Dict[str, Any]]
    metadata: Dict[str, Any]


class ImprovementBacklog:
    """Manages the improvement backlog for the recommendation system."""
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the improvement backlog.
        
        Args:
            storage_path: Optional path to store backlog data
        """
        self.logger = logging.getLogger(__name__)
        self.storage_path = storage_path or "data/improvement_backlog.json"
        
        # In-memory storage
        self.items: Dict[str, ImprovementItem] = {}
        
        # Configuration
        self.config = {
            "auto_prioritization": True,
            "dependency_validation": True,
            "effort_tracking": True,
            "reminder_days": 7
        }
        
        # Load existing backlog
        self._load_backlog()
        
        self.logger.info("Improvement backlog initialized")
    
    def add_item(
        self,
        title: str,
        description: str,
        category: Category,
        priority: Priority = Priority.MEDIUM,
        due_date: Optional[datetime] = None,
        assigned_to: Optional[str] = None,
        estimated_effort: Optional[int] = None,
        tags: Optional[List[str]] = None,
        dependencies: Optional[List[str]] = None,
        acceptance_criteria: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a new improvement item to the backlog.
        
        Args:
            title: Title of the improvement item
            description: Detailed description
            category: Category of the improvement
            priority: Priority level
            due_date: Optional due date
            assigned_to: Optional assignee
            estimated_effort: Estimated effort in hours
            tags: Optional tags
            dependencies: Optional dependencies
            acceptance_criteria: Optional acceptance criteria
            metadata: Optional metadata
            
        Returns:
            Item ID of the created item
        """
        # Validate dependencies
        if dependencies and self.config["dependency_validation"]:
            for dep_id in dependencies:
                if dep_id not in self.items:
                    raise ValueError(f"Dependency {dep_id} not found in backlog")
        
        item_id = f"imp_{uuid.uuid4().hex[:8]}"
        
        item = ImprovementItem(
            item_id=item_id,
            title=title,
            description=description,
            category=category,
            priority=priority,
            status=Status.BACKLOG,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            due_date=due_date,
            assigned_to=assigned_to,
            estimated_effort=estimated_effort,
            actual_effort=None,
            tags=tags or [],
            dependencies=dependencies or [],
            acceptance_criteria=acceptance_criteria or [],
            implementation_notes=None,
            test_results=None,
            metadata=metadata or {}
        )
        
        self.items[item_id] = item
        self._save_backlog()
        
        self.logger.info(f"Added improvement item: {item_id} - {title}")
        return item_id
    
    def update_item(
        self,
        item_id: str,
        **updates
    ) -> bool:
        """
        Update an existing improvement item.
        
        Args:
            item_id: ID of the item to update
            **updates: Fields to update
            
        Returns:
            True if updated, False if not found
        """
        if item_id not in self.items:
            return False
        
        item = self.items[item_id]
        
        # Update fields
        for field, value in updates.items():
            if hasattr(item, field):
                setattr(item, field, value)
        
        item.updated_at = datetime.now()
        self._save_backlog()
        
        self.logger.info(f"Updated improvement item: {item_id}")
        return True
    
    def get_item(self, item_id: str) -> Optional[ImprovementItem]:
        """Get an improvement item by ID."""
        return self.items.get(item_id)
    
    def get_items_by_status(self, status: Status) -> List[ImprovementItem]:
        """Get items by status."""
        return [item for item in self.items.values() if item.status == status]
    
    def get_items_by_priority(self, priority: Priority) -> List[ImprovementItem]:
        """Get items by priority."""
        return [item for item in self.items.values() if item.priority == priority]
    
    def get_items_by_category(self, category: Category) -> List[ImprovementItem]:
        """Get items by category."""
        return [item for item in self.items.values() if item.category == category]
    
    def get_items_by_assignee(self, assignee: str) -> List[ImprovementItem]:
        """Get items assigned to a specific person."""
        return [item for item in self.items.values() if item.assigned_to == assignee]
    
    def get_overdue_items(self) -> List[ImprovementItem]:
        """Get overdue items."""
        now = datetime.now()
        return [
            item for item in self.items.values()
            if item.due_date and item.due_date < now and item.status not in [Status.COMPLETED, Status.CANCELLED]
        ]
    
    def get_upcoming_items(self, days_ahead: int = 7) -> List[ImprovementItem]:
        """Get items due in the next few days."""
        now = datetime.now()
        future_date = now + timedelta(days=days_ahead)
        
        return [
            item for item in self.items.values()
            if item.due_date and now <= item.due_date <= future_date and item.status not in [Status.COMPLETED, Status.CANCELLED]
        ]
    
    def get_dependencies(self, item_id: str) -> List[ImprovementItem]:
        """Get dependencies for an item."""
        item = self.get_item(item_id)
        if not item:
            return []
        
        return [self.items[dep_id] for dep_id in item.dependencies if dep_id in self.items]
    
    def get_dependents(self, item_id: str) -> List[ImprovementItem]:
        """Get items that depend on this item."""
        return [
            item for item in self.items.values()
            if item_id in item.dependencies
        ]
    
    def can_start_item(self, item_id: str) -> Tuple[bool, List[str]]:
        """
        Check if an item can be started (all dependencies completed).
        
        Args:
            item_id: ID of the item to check
            
        Returns:
            Tuple of (can_start, blocking_dependencies)
        """
        dependencies = self.get_dependencies(item_id)
        
        blocking_deps = []
        for dep in dependencies:
            if dep.status != Status.COMPLETED:
                blocking_deps.append(dep.item_id)
        
        return len(blocking_deps) == 0, blocking_deps
    
    def start_item(self, item_id: str, assignee: Optional[str] = None) -> bool:
        """Start working on an item."""
        item = self.get_item(item_id)
        if not item:
            return False
        
        if item.status != Status.BACKLOG:
            return False
        
        can_start, blocking_deps = self.can_start_item(item_id)
        if not can_start:
            self.logger.warning(f"Cannot start {item_id}: blocked by dependencies {blocking_deps}")
            return False
        
        updates = {"status": Status.IN_PROGRESS}
        if assignee:
            updates["assigned_to"] = assignee
        
        return self.update_item(item_id, **updates)
    
    def complete_item(self, item_id: str, actual_effort: Optional[int] = None, test_results: Optional[Dict[str, Any]] = None) -> bool:
        """Mark an item as completed."""
        item = self.get_item(item_id)
        if not item:
            return False
        
        updates = {
            "status": Status.COMPLETED,
            "actual_effort": actual_effort,
            "test_results": test_results
        }
        
        return self.update_item(item_id, **updates)
    
    def cancel_item(self, item_id: str, reason: Optional[str] = None) -> bool:
        """Cancel an improvement item."""
        item = self.get_item(item_id)
        if not item:
            return False
        
        updates = {"status": Status.CANCELLED}
        if reason:
            updates["metadata"] = item.metadata.copy()
            updates["metadata"]["cancellation_reason"] = reason
        
        return self.update_item(item_id, **updates)
    
    def get_backlog_summary(self) -> Dict[str, Any]:
        """Get a summary of the backlog."""
        total_items = len(self.items)
        
        # Count by status
        status_counts = {}
        for status in Status:
            status_counts[status.value] = len(self.get_items_by_status(status))
        
        # Count by priority
        priority_counts = {}
        for priority in Priority:
            priority_counts[priority.value] = len(self.get_items_by_priority(priority))
        
        # Count by category
        category_counts = {}
        for category in Category:
            category_counts[category.value] = len(self.get_items_by_category(category))
        
        # Overdue items
        overdue_count = len(self.get_overdue_items())
        
        # Upcoming items
        upcoming_count = len(self.get_upcoming_items())
        
        # Total estimated effort
        total_estimated = sum(item.estimated_effort for item in self.items.values() if item.estimated_effort)
        
        # Total actual effort
        total_actual = sum(item.actual_effort for item in self.items.values() if item.actual_effort)
        
        return {
            "total_items": total_items,
            "by_status": status_counts,
            "by_priority": priority_counts,
            "by_category": category_counts,
            "overdue_items": overdue_count,
            "upcoming_items": upcoming_count,
            "total_estimated_effort": total_estimated,
            "total_actual_effort": total_actual,
            "completion_rate": status_counts.get("completed", 0) / total_items if total_items > 0 else 0
        }
    
    def get_workload_summary(self, assignee: Optional[str] = None) -> Dict[str, Any]:
        """Get workload summary for an assignee or all assignees."""
        items = self.get_items_by_assignee(assignee) if assignee else self.items.values()
        
        # Count by status
        status_counts = {}
        for status in Status:
            status_counts[status.value] = len([item for item in items if item.status == status])
        
        # Total effort
        estimated_effort = sum(item.estimated_effort for item in items if item.estimated_effort and item.status != Status.COMPLETED)
        actual_effort = sum(item.actual_effort for item in items if item.actual_effort)
        
        # Overdue items
        overdue_items = [item for item in items if item in self.get_overdue_items()]
        
        return {
            "assignee": assignee or "all",
            "total_items": len(items),
            "by_status": status_counts,
            "estimated_effort_remaining": estimated_effort,
            "actual_effort_completed": actual_effort,
            "overdue_items": len(overdue_items),
            "overdue_item_ids": [item.item_id for item in overdue_items]
        }
    
    def prioritize_backlog(self) -> List[str]:
        """Auto-prioritize backlog items based on various factors."""
        if not self.config["auto_prioritization"]:
            return []
        
        prioritized_items = []
        
        for item in self.items.values():
            if item.status != Status.BACKLOG:
                continue
            
            # Calculate priority score
            score = 0
            
            # Base priority score
            priority_scores = {
                Priority.CRITICAL: 100,
                Priority.HIGH: 75,
                Priority.MEDIUM: 50,
                Priority.LOW: 25
            }
            score += priority_scores.get(item.priority, 0)
            
            # Urgency based on due date
            if item.due_date:
                days_until_due = (item.due_date - datetime.now()).days
                if days_until_due < 0:
                    score += 50  # Overdue
                elif days_until_due <= 7:
                    score += 30  # Due soon
                elif days_until_due <= 30:
                    score += 15  # Due this month
            
            # Effort consideration (prefer smaller items)
            if item.estimated_effort:
                if item.estimated_effort <= 4:
                    score += 10  # Quick win
                elif item.estimated_effort <= 8:
                    score += 5   # Medium effort
            
            # Dependencies (prefer items with fewer dependencies)
            dependency_count = len(item.dependencies)
            if dependency_count == 0:
                score += 20  # No dependencies
            elif dependency_count <= 2:
                score += 10  # Few dependencies
            
            prioritized_items.append((item.item_id, score))
        
        # Sort by score (descending)
        prioritized_items.sort(key=lambda x: x[1], reverse=True)
        
        # Update item priorities based on scores
        updated_items = []
        for item_id, score in prioritized_items:
            item = self.items[item_id]
            
            # Map score to priority
            if score >= 80:
                new_priority = Priority.CRITICAL
            elif score >= 60:
                new_priority = Priority.HIGH
            elif score >= 40:
                new_priority = Priority.MEDIUM
            else:
                new_priority = Priority.LOW
            
            if new_priority != item.priority:
                self.update_item(item_id, priority=new_priority)
                updated_items.append(item_id)
        
        return updated_items
    
    def generate_improvement_plan(self, days_ahead: int = 30) -> Dict[str, Any]:
        """Generate an improvement plan for the next few weeks."""
        now = datetime.now()
        future_date = now + timedelta(days=days_ahead)
        
        # Get items that should be worked on
        candidate_items = []
        
        for item in self.items.values():
            if item.status in [Status.BACKLOG, Status.IN_PROGRESS]:
                # Include if due soon or high priority
                if (item.due_date and item.due_date <= future_date) or item.priority in [Priority.CRITICAL, Priority.HIGH]:
                    candidate_items.append(item)
        
        # Sort by priority and due date
        candidate_items.sort(key=lambda x: (
            0 if x.priority == Priority.CRITICAL else
            1 if x.priority == Priority.HIGH else
            2 if x.priority == Priority.MEDIUM else 3,
            x.due_date or future_date
        ))
        
        # Generate plan
        plan = {
            "period": f"Next {days_ahead} days",
            "total_items": len(candidate_items),
            "estimated_effort": sum(item.estimated_effort for item in candidate_items if item.estimated_effort),
            "items": []
        }
        
        for item in candidate_items[:10]:  # Limit to top 10 items
            can_start, blocking_deps = self.can_start_item(item.item_id)
            
            plan["items"].append({
                "item_id": item.item_id,
                "title": item.title,
                "priority": item.priority.value,
                "category": item.category.value,
                "estimated_effort": item.estimated_effort,
                "due_date": item.due_date.isoformat() if item.due_date else None,
                "can_start": can_start,
                "blocking_dependencies": blocking_deps,
                "status": item.status.value
            })
        
        return plan
    
    def export_backlog(self, filepath: str) -> None:
        """Export backlog to JSON file."""
        data = {
            "export_timestamp": datetime.now().isoformat(),
            "items": [
                {
                    "item_id": item.item_id,
                    "title": item.title,
                    "description": item.description,
                    "category": item.category.value,
                    "priority": item.priority.value,
                    "status": item.status.value,
                    "created_at": item.created_at.isoformat(),
                    "updated_at": item.updated_at.isoformat(),
                    "due_date": item.due_date.isoformat() if item.due_date else None,
                    "assigned_to": item.assigned_to,
                    "estimated_effort": item.estimated_effort,
                    "actual_effort": item.actual_effort,
                    "tags": item.tags,
                    "dependencies": item.dependencies,
                    "acceptance_criteria": item.acceptance_criteria,
                    "implementation_notes": item.implementation_notes,
                    "test_results": item.test_results,
                    "metadata": item.metadata
                }
                for item in self.items.values()
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        self.logger.info(f"Backlog exported to {filepath}")
    
    def import_backlog(self, filepath: str) -> int:
        """Import backlog from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        imported_count = 0
        
        for item_data in data.get("items", []):
            try:
                item = ImprovementItem(
                    item_id=item_data["item_id"],
                    title=item_data["title"],
                    description=item_data["description"],
                    category=Category(item_data["category"]),
                    priority=Priority(item_data["priority"]),
                    status=Status(item_data["status"]),
                    created_at=datetime.fromisoformat(item_data["created_at"]),
                    updated_at=datetime.fromisoformat(item_data["updated_at"]),
                    due_date=datetime.fromisoformat(item_data["due_date"]) if item_data.get("due_date") else None,
                    assigned_to=item_data.get("assigned_to"),
                    estimated_effort=item_data.get("estimated_effort"),
                    actual_effort=item_data.get("actual_effort"),
                    tags=item_data.get("tags", []),
                    dependencies=item_data.get("dependencies", []),
                    acceptance_criteria=item_data.get("acceptance_criteria", []),
                    implementation_notes=item_data.get("implementation_notes"),
                    test_results=item_data.get("test_results"),
                    metadata=item_data.get("metadata", {})
                )
                
                self.items[item.item_id] = item
                imported_count += 1
                
            except Exception as e:
                self.logger.error(f"Failed to import item {item_data.get('item_id', 'unknown')}: {e}")
        
        self.logger.info(f"Imported {imported_count} backlog items")
        return imported_count
    
    def _load_backlog(self) -> None:
        """Load backlog from storage."""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                
                for item_data in data.get("items", []):
                    item = ImprovementItem(
                        item_id=item_data["item_id"],
                        title=item_data["title"],
                        description=item_data["description"],
                        category=Category(item_data["category"]),
                        priority=Priority(item_data["priority"]),
                        status=Status(item_data["status"]),
                        created_at=datetime.fromisoformat(item_data["created_at"]),
                        updated_at=datetime.fromisoformat(item_data["updated_at"]),
                        due_date=datetime.fromisoformat(item_data["due_date"]) if item_data.get("due_date") else None,
                        assigned_to=item_data.get("assigned_to"),
                        estimated_effort=item_data.get("estimated_effort"),
                        actual_effort=item_data.get("actual_effort"),
                        tags=item_data.get("tags", []),
                        dependencies=item_data.get("dependencies", []),
                        acceptance_criteria=item_data.get("acceptance_criteria", []),
                        implementation_notes=item_data.get("implementation_notes"),
                        test_results=item_data.get("test_results"),
                        metadata=item_data.get("metadata", {})
                    )
                    self.items[item.item_id] = item
                
                self.logger.info(f"Loaded {len(self.items)} backlog items")
        except Exception as e:
            self.logger.warning(f"Failed to load backlog: {e}")
    
    def _save_backlog(self) -> None:
        """Save backlog to storage."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            data = {
                "last_updated": datetime.now().isoformat(),
                "items": [
                    {
                        "item_id": item.item_id,
                        "title": item.title,
                        "description": item.description,
                        "category": item.category.value,
                        "priority": item.priority.value,
                        "status": item.status.value,
                        "created_at": item.created_at.isoformat(),
                        "updated_at": item.updated_at.isoformat(),
                        "due_date": item.due_date.isoformat() if item.due_date else None,
                        "assigned_to": item.assigned_to,
                        "estimated_effort": item.estimated_effort,
                        "actual_effort": item.actual_effort,
                        "tags": item.tags,
                        "dependencies": item.dependencies,
                        "acceptance_criteria": item.acceptance_criteria,
                        "implementation_notes": item.implementation_notes,
                        "test_results": item.test_results,
                        "metadata": item.metadata
                    }
                    for item in self.items.values()
                ]
            }
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save backlog: {e}")


# Import os for file operations
import os
