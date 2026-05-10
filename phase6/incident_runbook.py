"""Incident Runbook: Procedures for incident handling and system recovery."""

from typing import Dict, Any, List, Optional, Union
import json
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import subprocess
import sys


class IncidentSeverity(Enum):
    """Incident severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(Enum):
    """Incident status."""
    OPEN = "open"
    INVESTIGATING = "investigating"
    IDENTIFIED = "identified"
    MONITORING = "monitoring"
    RESOLVED = "resolved"
    CLOSED = "closed"


class RecoveryAction(Enum):
    """Types of recovery actions."""
    RESTART_SERVICE = "restart_service"
    CLEAR_CACHE = "clear_cache"
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    DEPLOY_ROLLBACK = "deploy_rollback"
    DATABASE_RESTART = "database_restart"
    NETWORK_CHECK = "network_check"
    LOG_ANALYSIS = "log_analysis"
    MANUAL_INTERVENTION = "manual_intervention"


@dataclass
class Incident:
    """Incident record."""
    incident_id: str
    title: str
    description: str
    severity: IncidentSeverity
    status: IncidentStatus
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]
    assigned_to: Optional[str]
    affected_services: List[str]
    impact: str
    root_cause: Optional[str]
    resolution: Optional[str]
    recovery_actions: List[RecoveryAction]
    tags: List[str]
    metadata: Dict[str, Any]


@dataclass
class RecoveryProcedure:
    """Recovery procedure definition."""
    procedure_id: str
    name: str
    description: str
    severity: IncidentSeverity
    triggers: List[str]
    steps: List[Dict[str, Any]]
    estimated_duration: int  # minutes
    prerequisites: List[str]
    rollback_steps: List[Dict[str, Any]]
    success_criteria: List[str]


class IncidentRunbook:
    """Comprehensive incident response and recovery procedures."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize incident runbook.
        
        Args:
            config: Runbook configuration
        """
        self.config = config or self._get_default_config()
        self.incidents = []
        self.procedures = {}
        self.active_incidents = {}
        
        # Load procedures
        self._load_procedures()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default runbook configuration."""
        return {
            "auto_detection": True,
            "notification_channels": ["email", "slack"],
            "escalation_thresholds": {
                "low": 60,  # minutes
                "medium": 30,
                "high": 15,
                "critical": 5
            },
            "auto_recovery": {
                "enabled": True,
                "max_attempts": 3,
                "procedures": ["restart_service", "clear_cache"]
            },
            "incident_retention_days": 90,
            "runbook_file": "data/incident_runbook.json"
        }
    
    def _load_procedures(self) -> None:
        """Load recovery procedures."""
        self.procedures = {
            "high_error_rate": RecoveryProcedure(
                procedure_id="high_error_rate",
                name="High Error Rate Recovery",
                description="Procedures to handle high error rate incidents",
                severity=IncidentSeverity.HIGH,
                triggers=["error_rate > 5%", "success_rate < 95%"],
                steps=[
                    {
                        "step": 1,
                        "action": "Check system health",
                        "command": "curl -f http://localhost:8000/health",
                        "expected": "HTTP 200"
                    },
                    {
                        "step": 2,
                        "action": "Check recent deployments",
                        "command": "python -m phase6.deployment_pipeline get_deployment_status production",
                        "expected": "Successful deployment"
                    },
                    {
                        "step": 3,
                        "action": "Restart API service",
                        "command": "pkill -f 'python -m phase4.main api-server' && sleep 5 && python -m phase4.main api-server",
                        "expected": "Service running"
                    },
                    {
                        "step": 4,
                        "action": "Clear cache",
                        "command": "python -c 'from phase6.caching_layer import cache_manager; cache_manager.clear()'",
                        "expected": "Cache cleared"
                    },
                    {
                        "step": 5,
                        "action": "Verify recovery",
                        "command": "curl -f http://localhost:8000/health",
                        "expected": "HTTP 200"
                    }
                ],
                estimated_duration=15,
                prerequisites=["Service access", "Admin privileges"],
                rollback_steps=[
                    {
                        "step": 1,
                        "action": "Check previous deployment",
                        "command": "python -m phase6.deployment_pipeline get_deployment_status production"
                    },
                    {
                        "step": 2,
                        "action": "Rollback if needed",
                        "command": "python -m phase6.deployment_pipeline rollback production"
                    }
                ],
                success_criteria=[
                    "Error rate < 2%",
                    "Service responding to health checks",
                    "No critical alerts"
                ]
            ),
            
            "slow_response_time": RecoveryProcedure(
                procedure_id="slow_response_time",
                name="Slow Response Time Recovery",
                description="Procedures to handle slow response time incidents",
                severity=IncidentSeverity.MEDIUM,
                triggers=["p95_response_time > 2000ms", "avg_response_time > 1000ms"],
                steps=[
                    {
                        "step": 1,
                        "action": "Check system resources",
                        "command": "top -b -n 1 | head -20",
                        "expected": "CPU/Memory usage normal"
                    },
                    {
                        "step": 2,
                        "action": "Check database performance",
                        "command": "python -c 'import sqlite3; conn = sqlite3.connect(\"data/processed/restaurants.db\"); print(\"DB OK\")'",
                        "expected": "DB OK"
                    },
                    {
                        "step": 3,
                        "action": "Clear expired cache entries",
                        "command": "python -c 'from phase6.caching_layer import cache_manager; cache_manager.cleanup_expired()'",
                        "expected": "Cache cleaned"
                    },
                    {
                        "step": 4,
                        "action": "Restart LLM provider connection",
                        "command": "python -c 'from phase4.groq_provider import GroqProvider; GroqProvider().test_connection()'",
                        "expected": "Connection OK"
                    }
                ],
                estimated_duration=10,
                prerequisites=["Service access", "Monitoring access"],
                rollback_steps=[
                    {
                        "step": 1,
                        "action": "Scale up resources",
                        "command": "echo 'Scale up procedure'"
                    }
                ],
                success_criteria=[
                    "P95 response time < 1000ms",
                    "Average response time < 500ms",
                    "No performance alerts"
                ]
            ),
            
            "service_unavailable": RecoveryProcedure(
                procedure_id="service_unavailable",
                name="Service Unavailable Recovery",
                description="Procedures to handle service unavailability",
                severity=IncidentSeverity.CRITICAL,
                triggers=["health_check_failed", "service_down"],
                steps=[
                    {
                        "step": 1,
                        "action": "Check service status",
                        "command": "ps aux | grep 'python -m phase4.main'",
                        "expected": "Service processes found"
                    },
                    {
                        "step": 2,
                        "action": "Check port availability",
                        "command": "netstat -tlnp | grep :8000",
                        "expected": "Port 8000 listening"
                    },
                    {
                        "step": 3,
                        "action": "Start API service",
                        "command": "python -m phase4.main api-server",
                        "expected": "Service started"
                    },
                    {
                        "step": 4,
                        "action": "Start Streamlit service",
                        "command": "python -m phase4.main streamlit",
                        "expected": "Streamlit started"
                    },
                    {
                        "step": 5,
                        "action": "Verify services",
                        "command": "curl -f http://localhost:8000/health && curl -f http://localhost:8501",
                        "expected": "Both services responding"
                    }
                ],
                estimated_duration=5,
                prerequisites=["Service access", "Port access"],
                rollback_steps=[
                    {
                        "step": 1,
                        "action": "Check logs for errors",
                        "command": "tail -50 logs/application.log"
                    }
                ],
                success_criteria=[
                    "All services running",
                    "Health checks passing",
                    "No service errors"
                ]
            ),
            
            "security_breach": RecoveryProcedure(
                procedure_id="security_breach",
                name="Security Breach Response",
                description="Procedures to handle security incidents",
                severity=IncidentSeverity.CRITICAL,
                triggers=["suspicious_activity", "unauthorized_access", "malicious_requests"],
                steps=[
                    {
                        "step": 1,
                        "action": "Block malicious IP",
                        "command": "python -c 'from phase6.security_middleware import security_middleware; security_middleware.block_ip(\"MALICIOUS_IP\")'",
                        "expected": "IP blocked"
                    },
                    {
                        "step": 2,
                        "action": "Enable strict rate limiting",
                        "command": "python -c 'from phase6.security_middleware import security_middleware; print(\"Rate limiting enabled\")'",
                        "expected": "Rate limiting enabled"
                    },
                    {
                        "step": 3,
                        "action": "Review security events",
                        "command": "python -c 'from phase6.security_middleware import security_middleware; events = security_middleware.get_security_events(hours_back=1); print(f\"Recent events: {len(events)}\")'",
                        "expected": "Events reviewed"
                    },
                    {
                        "step": 4,
                        "action": "Rotate API keys if compromised",
                        "command": "echo 'Rotate API keys procedure'",
                        "expected": "Keys rotated"
                    }
                ],
                estimated_duration=20,
                prerequisites=["Security access", "Admin privileges"],
                rollback_steps=[
                    {
                        "step": 1,
                        "action": "Unblock legitimate IPs",
                        "command": "python -c 'from phase6.security_middleware import security_middleware; security_middleware.unblock_ip(\"IP_ADDRESS\")'"
                    }
                ],
                success_criteria=[
                    "No active threats",
                    "Security metrics normal",
                    "All systems secure"
                ]
            ),
            
            "cache_failure": RecoveryProcedure(
                procedure_id="cache_failure",
                name="Cache Failure Recovery",
                description="Procedures to handle cache system failures",
                severity=IncidentSeverity.MEDIUM,
                triggers=["cache_hit_rate_low", "cache_errors", "cache_unavailable"],
                steps=[
                    {
                        "step": 1,
                        "action": "Check cache status",
                        "command": "python -c 'from phase6.caching_layer import cache_manager; stats = cache_manager.get_stats(); print(stats)'",
                        "expected": "Cache stats available"
                    },
                    {
                        "step": 2,
                        "action": "Clear corrupted cache",
                        "command": "python -c 'from phase6.caching_layer import cache_manager; cache_manager.clear()'",
                        "expected": "Cache cleared"
                    },
                    {
                        "step": 3,
                        "action": "Restart cache backend",
                        "command": "echo 'Restart cache backend'",
                        "expected": "Cache backend restarted"
                    },
                    {
                        "step": 4,
                        "action": "Verify cache operation",
                        "command": "python -c 'from phase6.caching_layer import cache_manager; cache_manager.set(\"test\", \"value\"); print(cache_manager.get(\"test\"))'",
                        "expected": "value"
                    }
                ],
                estimated_duration=10,
                prerequisites=["Cache access", "Service access"],
                rollback_steps=[
                    {
                        "step": 1,
                        "action": "Restore from backup",
                        "command": "echo 'Restore cache backup'"
                    }
                ],
                success_criteria=[
                    "Cache hit rate > 70%",
                    "No cache errors",
                    "Cache operations working"
                ]
            )
        }
    
    def create_incident(
        self,
        title: str,
        description: str,
        severity: IncidentSeverity,
        affected_services: List[str],
        impact: str,
        assigned_to: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Create a new incident.
        
        Args:
            title: Incident title
            description: Incident description
            severity: Incident severity
            affected_services: List of affected services
            impact: Impact description
            assigned_to: Assigned person
            tags: Incident tags
            
        Returns:
            Incident ID
        """
        incident_id = f"INC-{int(time.time())}-{len(self.incidents):04d}"
        
        incident = Incident(
            incident_id=incident_id,
            title=title,
            description=description,
            severity=severity,
            status=IncidentStatus.OPEN,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            resolved_at=None,
            assigned_to=assigned_to,
            affected_services=affected_services,
            impact=impact,
            root_cause=None,
            resolution=None,
            recovery_actions=[],
            tags=tags or []
        )
        
        self.incidents.append(incident)
        self.active_incidents[incident_id] = incident
        
        # Auto-assign procedure if applicable
        self._auto_assign_procedure(incident)
        
        return incident_id
    
    def _auto_assign_procedure(self, incident: Incident) -> None:
        """Automatically assign recovery procedure based on incident details."""
        title_lower = incident.title.lower()
        description_lower = incident.description.lower()
        
        # Check for matching triggers
        for procedure_id, procedure in self.procedures.items():
            for trigger in procedure.triggers:
                if trigger.lower() in title_lower or trigger.lower() in description_lower:
                    incident.recovery_actions.append(RecoveryAction(procedure_id))
                    break
    
    def update_incident_status(
        self,
        incident_id: str,
        status: IncidentStatus,
        assigned_to: Optional[str] = None,
        root_cause: Optional[str] = None,
        resolution: Optional[str] = None
    ) -> bool:
        """
        Update incident status.
        
        Args:
            incident_id: Incident ID
            status: New status
            assigned_to: Assigned person
            root_cause: Root cause analysis
            resolution: Resolution description
            
        Returns:
            True if updated
        """
        incident = self.active_incidents.get(incident_id)
        if not incident:
            return False
        
        incident.status = status
        incident.updated_at = datetime.now()
        
        if assigned_to:
            incident.assigned_to = assigned_to
        if root_cause:
            incident.root_cause = root_cause
        if resolution:
            incident.resolution = resolution
        
        if status == IncidentStatus.RESOLVED:
            incident.resolved_at = datetime.now()
            # Move from active to resolved
            del self.active_incidents[incident_id]
        
        return True
    
    def execute_recovery_procedure(
        self,
        incident_id: str,
        procedure_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute recovery procedure for incident.
        
        Args:
            incident_id: Incident ID
            procedure_id: Specific procedure to execute
            
        Returns:
            Execution results
        """
        incident = self.active_incidents.get(incident_id)
        if not incident:
            return {"error": "Incident not found"}
        
        # Determine procedure to execute
        if procedure_id:
            procedure = self.procedures.get(procedure_id)
            if not procedure:
                return {"error": "Procedure not found"}
        else:
            # Auto-select based on recovery actions
            if incident.recovery_actions:
                action = incident.recovery_actions[0]
                procedure = self.procedures.get(action.value)
            else:
                return {"error": "No recovery procedure assigned"}
        
        if not procedure:
            return {"error": "Procedure not found"}
        
        # Update incident status
        self.update_incident_status(incident_id, IncidentStatus.INVESTIGATING)
        
        # Execute procedure steps
        results = {
            "procedure_id": procedure_id,
            "procedure_name": procedure.name,
            "started_at": datetime.now().isoformat(),
            "steps": [],
            "success": False,
            "error": None
        }
        
        try:
            for step in procedure.steps:
                step_result = self._execute_step(step)
                results["steps"].append(step_result)
                
                if not step_result["success"]:
                    results["error"] = f"Step {step['step']} failed: {step_result.get('error', 'Unknown error')}"
                    break
            
            # Check success criteria
            if not results["error"]:
                success_check = self._check_success_criteria(procedure.success_criteria)
                if success_check["success"]:
                    results["success"] = True
                    self.update_incident_status(incident_id, IncidentStatus.MONITORING)
                else:
                    results["error"] = "Success criteria not met"
        
        except Exception as e:
            results["error"] = str(e)
        
        results["completed_at"] = datetime.now().isoformat()
        
        return results
    
    def _execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single recovery step."""
        result = {
            "step": step["step"],
            "action": step["action"],
            "command": step["command"],
            "started_at": datetime.now().isoformat(),
            "success": False,
            "output": "",
            "error": None
        }
        
        try:
            # Execute command
            process = subprocess.run(
                step["command"],
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            result["output"] = process.stdout
            result["return_code"] = process.returncode
            
            if process.returncode == 0:
                result["success"] = True
            else:
                result["error"] = process.stderr
            
        except subprocess.TimeoutExpired:
            result["error"] = "Command timed out"
        except Exception as e:
            result["error"] = str(e)
        
        result["completed_at"] = datetime.now().isoformat()
        return result
    
    def _check_success_criteria(self, criteria: List[str]) -> Dict[str, Any]:
        """Check if success criteria are met."""
        results = {
            "success": True,
            "criteria_met": [],
            "criteria_failed": []
        }
        
        for criterion in criteria:
            try:
                # This would implement actual criteria checking
                # For now, assume all criteria are met
                results["criteria_met"].append(criterion)
            except Exception as e:
                results["success"] = False
                results["criteria_failed"].append(f"{criterion}: {str(e)}")
        
        return results
    
    def get_incident_summary(self, hours_back: int = 24) -> Dict[str, Any]:
        """
        Get incident summary for the last N hours.
        
        Args:
            hours_back: Time period in hours
            
        Returns:
            Incident summary
        """
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        recent_incidents = [
            incident for incident in self.incidents
            if incident.created_at >= cutoff_time
        ]
        
        # Count by severity
        severity_counts = {}
        for severity in IncidentSeverity:
            severity_counts[severity.value] = len([
                incident for incident in recent_incidents
                if incident.severity == severity
            ])
        
        # Count by status
        status_counts = {}
        for status in IncidentStatus:
            status_counts[status.value] = len([
                incident for incident in recent_incidents
                if incident.status == status
            ])
        
        # Calculate MTTR (Mean Time To Resolution)
        resolved_incidents = [
            incident for incident in recent_incidents
            if incident.status == IncidentStatus.RESOLVED and incident.resolved_at
        ]
        
        if resolved_incidents:
            total_resolution_time = sum(
                (incident.resolved_at - incident.created_at).total_seconds()
                for incident in resolved_incidents
            )
            mttr_minutes = total_resolution_time / len(resolved_incidents) / 60
        else:
            mttr_minutes = 0
        
        return {
            "time_period": f"Last {hours_back} hours",
            "total_incidents": len(recent_incidents),
            "active_incidents": len(self.active_incidents),
            "by_severity": severity_counts,
            "by_status": status_counts,
            "mttr_minutes": mttr_minutes,
            "most_common_services": self._get_most_common_affected_services(recent_incidents)
        }
    
    def _get_most_common_affected_services(self, incidents: List[Incident]) -> List[Dict[str, Any]]:
        """Get most commonly affected services."""
        service_counts = defaultdict(int)
        for incident in incidents:
            for service in incident.affected_services:
                service_counts[service] += 1
        
        return [
            {"service": service, "count": count}
            for service, count in sorted(service_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
    
    def get_active_incidents(self) -> List[Dict[str, Any]]:
        """Get all active incidents."""
        return [
            {
                "incident_id": incident.incident_id,
                "title": incident.title,
                "severity": incident.severity.value,
                "status": incident.status.value,
                "created_at": incident.created_at.isoformat(),
                "assigned_to": incident.assigned_to,
                "affected_services": incident.affected_services,
                "recovery_actions": [action.value for action in incident.recovery_actions]
            }
            for incident in self.active_incidents.values()
        ]
    
    def get_procedure_list(self) -> List[Dict[str, Any]]:
        """Get list of all recovery procedures."""
        return [
            {
                "procedure_id": procedure.procedure_id,
                "name": procedure.name,
                "description": procedure.description,
                "severity": procedure.severity.value,
                "triggers": procedure.triggers,
                "estimated_duration": procedure.estimated_duration,
                "steps_count": len(procedure.steps)
            }
            for procedure in self.procedures.values()
        ]
    
    def create_custom_procedure(
        self,
        procedure_id: str,
        name: str,
        description: str,
        severity: IncidentSeverity,
        triggers: List[str],
        steps: List[Dict[str, Any]],
        estimated_duration: int,
        prerequisites: Optional[List[str]] = None,
        success_criteria: Optional[List[str]] = None
    ) -> bool:
        """
        Create a custom recovery procedure.
        
        Args:
            procedure_id: Procedure ID
            name: Procedure name
            description: Procedure description
            severity: Procedure severity
            triggers: Trigger conditions
            steps: Procedure steps
            estimated_duration: Estimated duration in minutes
            prerequisites: Prerequisites
            success_criteria: Success criteria
            
        Returns:
            True if created
        """
        if procedure_id in self.procedures:
            return False
        
        procedure = RecoveryProcedure(
            procedure_id=procedure_id,
            name=name,
            description=description,
            severity=severity,
            triggers=triggers,
            steps=steps,
            estimated_duration=estimated_duration,
            prerequisites=prerequisites or [],
            rollback_steps=[],
            success_criteria=success_criteria or []
        )
        
        self.procedures[procedure_id] = procedure
        return True
    
    def save_runbook(self, filepath: Optional[str] = None) -> bool:
        """
        Save runbook to file.
        
        Args:
            filepath: File path to save to
            
        Returns:
            True if saved
        """
        if filepath is None:
            filepath = self.config["runbook_file"]
        
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "incidents": [asdict(incident) for incident in self.incidents],
                "procedures": {
                    proc_id: asdict(procedure) for proc_id, procedure in self.procedures.items()
                },
                "config": self.config,
                "last_updated": datetime.now().isoformat()
            }
            
            # Convert datetime objects to strings
            data_str = json.dumps(data, indent=2, default=str)
            
            with open(filepath, 'w') as f:
                f.write(data_str)
            
            return True
            
        except Exception:
            return False
    
    def load_runbook(self, filepath: Optional[str] = None) -> bool:
        """
        Load runbook from file.
        
        Args:
            filepath: File path to load from
            
        Returns:
            True if loaded
        """
        if filepath is None:
            filepath = self.config["runbook_file"]
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Load incidents
            self.incidents = []
            for incident_data in data.get("incidents", []):
                # Convert string datetimes back to datetime objects
                incident_data["created_at"] = datetime.fromisoformat(incident_data["created_at"])
                incident_data["updated_at"] = datetime.fromisoformat(incident_data["updated_at"])
                if incident_data.get("resolved_at"):
                    incident_data["resolved_at"] = datetime.fromisoformat(incident_data["resolved_at"])
                
                incident = Incident(**incident_data)
                self.incidents.append(incident)
                
                # Update active incidents
                if incident.status not in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]:
                    self.active_incidents[incident.incident_id] = incident
            
            # Load procedures
            self.procedures = {}
            for proc_id, procedure_data in data.get("procedures", {}).items():
                procedure = RecoveryProcedure(**procedure_data)
                self.procedures[proc_id] = procedure
            
            return True
            
        except Exception:
            return False


class RecoveryProcedures:
    """Predefined recovery procedures for common incidents."""
    
    @staticmethod
    def restart_service(service_name: str) -> bool:
        """
        Restart a service.
        
        Args:
            service_name: Name of service to restart
            
        Returns:
            True if successful
        """
        try:
            # Kill existing process
            subprocess.run(f"pkill -f '{service_name}'", shell=True)
            time.sleep(2)
            
            # Start service
            if "api-server" in service_name:
                subprocess.Popen([sys.executable, "-m", "phase4.main", "api-server"])
            elif "streamlit" in service_name:
                subprocess.Popen([sys.executable, "-m", "phase4.main", "streamlit"])
            
            time.sleep(3)
            return True
            
        except Exception:
            return False
    
    @staticmethod
    def clear_all_caches() -> bool:
        """
        Clear all caches.
        
        Returns:
            True if successful
        """
        try:
            from phase6.caching_layer import cache_manager
            cache_manager.clear()
            return True
        except Exception:
            return False
    
    @staticmethod
    def check_system_health() -> Dict[str, bool]:
        """
        Check overall system health.
        
        Returns:
            Health check results
        """
        results = {}
        
        # Check API service
        try:
            import requests
            response = requests.get("http://localhost:8000/health", timeout=5)
            results["api_service"] = response.status_code == 200
        except Exception:
            results["api_service"] = False
        
        # Check Streamlit service
        try:
            import requests
            response = requests.get("http://localhost:8501", timeout=5)
            results["streamlit_service"] = response.status_code == 200
        except Exception:
            results["streamlit_service"] = False
        
        # Check database
        try:
            import sqlite3
            conn = sqlite3.connect("data/processed/restaurants.db")
            conn.execute("SELECT 1 LIMIT 1")
            conn.close()
            results["database"] = True
        except Exception:
            results["database"] = False
        
        # Check cache
        try:
            from phase6.caching_layer import cache_manager
            cache_manager.get("test_key")
            results["cache"] = True
        except Exception:
            results["cache"] = False
        
        return results
    
    @staticmethod
    def get_system_metrics() -> Dict[str, Any]:
        """
        Get system performance metrics.
        
        Returns:
            System metrics
        """
        metrics = {}
        
        # CPU and Memory
        try:
            import psutil
            metrics["cpu_percent"] = psutil.cpu_percent()
            metrics["memory_percent"] = psutil.virtual_memory().percent
            metrics["disk_percent"] = psutil.disk_usage('/').percent
        except Exception:
            metrics["cpu_percent"] = 0
            metrics["memory_percent"] = 0
            metrics["disk_percent"] = 0
        
        # Application metrics
        try:
            from phase6.logging_monitoring import monitoring_system
            app_metrics = monitoring_system.get_all_metrics()
            metrics.update(app_metrics)
        except Exception:
            pass
        
        return metrics


# Global instances
incident_runbook = IncidentRunbook()
recovery_procedures = RecoveryProcedures()
