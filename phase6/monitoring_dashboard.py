"""Monitoring Dashboard: Real-time monitoring and visualization dashboard."""

from typing import Dict, Any, List, Optional, Union
import json
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from collections import defaultdict, deque
import statistics

# Import our monitoring components
from .logging_monitoring import logging_manager, monitoring_system, LogLevel, MetricType
from .security_middleware import security_middleware, SecurityLevel, ThreatType
from .caching_layer import cache_manager


class DashboardType(Enum):
    """Types of monitoring dashboards."""
    OVERVIEW = "overview"
    PERFORMANCE = "performance"
    SECURITY = "security"
    LOGS = "logs"
    CACHE = "cache"
    SYSTEM = "system"


@dataclass
class DashboardWidget:
    """Dashboard widget configuration."""
    widget_id: str
    title: str
    type: str  # metric, chart, alert, log
    position: Dict[str, int]  # x, y, width, height
    data_source: str
    refresh_interval: int  # seconds
    config: Dict[str, Any]


class MonitoringDashboard:
    """Real-time monitoring dashboard."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize monitoring dashboard.
        
        Args:
            config: Dashboard configuration
        """
        self.config = config or self._get_default_config()
        self.widgets = {}
        self.dashboard_data = {}
        self.refresh_thread = None
        self.running = False
        
        # Initialize default widgets
        self._setup_default_widgets()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default dashboard configuration."""
        return {
            "refresh_interval": 5,  # seconds
            "max_data_points": 100,
            "alert_thresholds": {
                "error_rate": 0.05,  # 5%
                "response_time_p95": 2000,  # ms
                "success_rate": 0.95,  # 95%
                "memory_usage": 0.8,  # 80%
                "cache_hit_rate": 0.7  # 70%
            },
            "widget_layout": {
                "overview": [
                    {"widget_id": "system_health", "x": 0, "y": 0, "width": 4, "height": 2},
                    {"widget_id": "request_metrics", "x": 4, "y": 0, "width": 4, "height": 2},
                    {"widget_id": "error_rate", "x": 8, "y": 0, "width": 4, "height": 2},
                    {"widget_id": "recent_alerts", "x": 0, "y": 2, "width": 6, "height": 3},
                    {"widget_id": "response_times", "x": 6, "y": 2, "width": 6, "height": 3}
                ],
                "performance": [
                    {"widget_id": "response_time_chart", "x": 0, "y": 0, "width": 6, "height": 4},
                    {"widget_id": "throughput_chart", "x": 6, "y": 0, "width": 6, "height": 4},
                    {"widget_id": "cache_performance", "x": 0, "y": 4, "width": 6, "height": 3},
                    {"widget_id": "llm_metrics", "x": 6, "y": 4, "width": 6, "height": 3}
                ],
                "security": [
                    {"widget_id": "security_events", "x": 0, "y": 0, "width": 6, "height": 4},
                    {"widget_id": "threat_types", "x": 6, "y": 0, "width": 6, "height": 4},
                    {"widget_id": "blocked_ips", "x": 0, "y": 4, "width": 6, "height": 3},
                    {"widget_id": "rate_limits", "x": 6, "y": 4, "width": 6, "height": 3}
                ]
            }
        }
    
    def _setup_default_widgets(self) -> None:
        """Setup default dashboard widgets."""
        # Overview dashboard widgets
        self.widgets["system_health"] = DashboardWidget(
            widget_id="system_health",
            title="System Health",
            type="status",
            position={"x": 0, "y": 0, "width": 4, "height": 2},
            data_source="system_health",
            refresh_interval=10,
            config={"show_details": True}
        )
        
        self.widgets["request_metrics"] = DashboardWidget(
            widget_id="request_metrics",
            title="Request Metrics",
            type="metric",
            position={"x": 4, "y": 0, "width": 4, "height": 2},
            data_source="request_metrics",
            refresh_interval=5,
            config={"metrics": ["total_requests", "success_rate", "error_rate"]}
        )
        
        self.widgets["error_rate"] = DashboardWidget(
            widget_id="error_rate",
            title="Error Rate",
            type="gauge",
            position={"x": 8, "y": 0, "width": 4, "height": 2},
            data_source="error_rate",
            refresh_interval=5,
            config={"max_value": 0.1, "threshold": 0.05}
        )
        
        self.widgets["recent_alerts"] = DashboardWidget(
            widget_id="recent_alerts",
            title="Recent Alerts",
            type="alert",
            position={"x": 0, "y": 2, "width": 6, "height": 3},
            data_source="alerts",
            refresh_interval=10,
            config={"max_alerts": 10, "show_severity": True}
        )
        
        self.widgets["response_times"] = DashboardWidget(
            widget_id="response_times",
            title="Response Times",
            type="chart",
            position={"x": 6, "y": 2, "width": 6, "height": 3},
            data_source="response_times",
            refresh_interval=5,
            config={"chart_type": "line", "time_range": "1h"}
        )
        
        # Performance dashboard widgets
        self.widgets["response_time_chart"] = DashboardWidget(
            widget_id="response_time_chart",
            title="Response Time Trends",
            type="chart",
            position={"x": 0, "y": 0, "width": 6, "height": 4},
            data_source="response_times",
            refresh_interval=5,
            config={"chart_type": "line", "time_range": "24h", "show_p95": True}
        )
        
        self.widgets["throughput_chart"] = DashboardWidget(
            widget_id="throughput_chart",
            title="Request Throughput",
            type="chart",
            position={"x": 6, "y": 0, "width": 6, "height": 4},
            data_source="throughput",
            refresh_interval=5,
            config={"chart_type": "bar", "time_range": "24h"}
        )
        
        self.widgets["cache_performance"] = DashboardWidget(
            widget_id="cache_performance",
            title="Cache Performance",
            type="metric",
            position={"x": 0, "y": 4, "width": 6, "height": 3},
            data_source="cache_stats",
            refresh_interval=10,
            config={"metrics": ["hit_rate", "size", "total_size_bytes"]}
        )
        
        self.widgets["llm_metrics"] = DashboardWidget(
            widget_id="llm_metrics",
            title="LLM Performance",
            type="metric",
            position={"x": 6, "y": 4, "width": 6, "height": 3},
            data_source="llm_metrics",
            refresh_interval=10,
            config={"metrics": ["total_calls", "avg_response_time", "error_rate"]}
        )
        
        # Security dashboard widgets
        self.widgets["security_events"] = DashboardWidget(
            widget_id="security_events",
            title="Security Events",
            type="chart",
            position={"x": 0, "y": 0, "width": 6, "height": 4},
            data_source="security_events",
            refresh_interval=10,
            config={"chart_type": "timeline", "time_range": "24h"}
        )
        
        self.widgets["threat_types"] = DashboardWidget(
            widget_id="threat_types",
            title="Threat Types",
            type="chart",
            position={"x": 6, "y": 0, "width": 6, "height": 4},
            data_source="threat_types",
            refresh_interval=10,
            config={"chart_type": "pie", "show_percentages": True}
        )
        
        self.widgets["blocked_ips"] = DashboardWidget(
            widget_id="blocked_ips",
            title="Blocked IPs",
            type="table",
            position={"x": 0, "y": 4, "width": 6, "height": 3},
            data_source="blocked_ips",
            refresh_interval=30,
            config={"max_rows": 10, "show_reason": True}
        )
        
        self.widgets["rate_limits"] = DashboardWidget(
            widget_id="rate_limits",
            title="Rate Limit Status",
            type="metric",
            position={"x": 6, "y": 4, "width": 6, "height": 3},
            data_source="rate_limits",
            refresh_interval=5,
            config={"show_limits": True, "show_remaining": True}
        )
    
    def start_dashboard(self) -> None:
        """Start the dashboard refresh thread."""
        if self.running:
            return
        
        self.running = True
        self.refresh_thread = threading.Thread(target=self._refresh_loop, daemon=True)
        self.refresh_thread.start()
    
    def stop_dashboard(self) -> None:
        """Stop the dashboard refresh thread."""
        self.running = False
        if self.refresh_thread:
            self.refresh_thread.join()
    
    def _refresh_loop(self) -> None:
        """Background thread to refresh dashboard data."""
        while self.running:
            try:
                self.refresh_all_widgets()
                time.sleep(self.config["refresh_interval"])
            except Exception as e:
                print(f"Dashboard refresh error: {e}")
                time.sleep(self.config["refresh_interval"])
    
    def refresh_all_widgets(self) -> None:
        """Refresh all dashboard widgets."""
        for widget in self.widgets.values():
            try:
                data = self.get_widget_data(widget)
                self.dashboard_data[widget.widget_id] = {
                    "data": data,
                    "last_updated": datetime.now().isoformat(),
                    "widget": widget
                }
            except Exception as e:
                print(f"Error refreshing widget {widget.widget_id}: {e}")
    
    def get_widget_data(self, widget: DashboardWidget) -> Dict[str, Any]:
        """
        Get data for a specific widget.
        
        Args:
            widget: Widget to get data for
            
        Returns:
            Widget data
        """
        data_source = widget.data_source
        
        if data_source == "system_health":
            return self._get_system_health_data()
        elif data_source == "request_metrics":
            return self._get_request_metrics_data()
        elif data_source == "error_rate":
            return self._get_error_rate_data()
        elif data_source == "alerts":
            return self._get_alerts_data()
        elif data_source == "response_times":
            return self._get_response_times_data()
        elif data_source == "throughput":
            return self._get_throughput_data()
        elif data_source == "cache_stats":
            return self._get_cache_stats_data()
        elif data_source == "llm_metrics":
            return self._get_llm_metrics_data()
        elif data_source == "security_events":
            return self._get_security_events_data()
        elif data_source == "threat_types":
            return self._get_threat_types_data()
        elif data_source == "blocked_ips":
            return self._get_blocked_ips_data()
        elif data_source == "rate_limits":
            return self._get_rate_limits_data()
        else:
            return {"error": f"Unknown data source: {data_source}"}
    
    def _get_system_health_data(self) -> Dict[str, Any]:
        """Get system health data."""
        health = monitoring_system.get_system_health()
        
        return {
            "status": health["status"],
            "timestamp": health["timestamp"],
            "metrics": health["metrics"],
            "issues": health["issues"],
            "overall_score": self._calculate_health_score(health)
        }
    
    def _calculate_health_score(self, health: Dict[str, Any]) -> float:
        """Calculate overall health score."""
        score = 100.0
        
        # Deduct points for issues
        for issue in health["issues"]:
            if "error rate" in issue.lower():
                score -= 20
            elif "response time" in issue.lower():
                score -= 15
            elif "success rate" in issue.lower():
                score -= 25
            elif "critical alerts" in issue.lower():
                score -= 30
        
        # Deduct points for poor metrics
        metrics = health["metrics"]
        if metrics.get("error_rate", 0) > 0.05:
            score -= 20
        if metrics.get("success_rate", 1.0) < 0.95:
            score -= 25
        if metrics.get("response_time_p95", 0) > 2000:
            score -= 15
        
        return max(0, score)
    
    def _get_request_metrics_data(self) -> Dict[str, Any]:
        """Get request metrics data."""
        metrics = monitoring_system.get_all_metrics()
        
        return {
            "total_requests": metrics.get("total_requests", {}).get("value", 0),
            "successful_requests": metrics.get("successful_requests", {}).get("value", 0),
            "error_requests": metrics.get("error_requests", {}).get("value", 0),
            "success_rate": self._calculate_success_rate(metrics),
            "error_rate": self._calculate_error_rate(metrics),
            "avg_response_time": metrics.get("response_time", {}).get("mean", 0)
        }
    
    def _calculate_success_rate(self, metrics: Dict[str, Any]) -> float:
        """Calculate success rate."""
        total = metrics.get("total_requests", {}).get("value", 0)
        successful = metrics.get("successful_requests", {}).get("value", 0)
        return successful / total if total > 0 else 1.0
    
    def _calculate_error_rate(self, metrics: Dict[str, Any]) -> float:
        """Calculate error rate."""
        total = metrics.get("total_requests", {}).get("value", 0)
        errors = metrics.get("error_requests", {}).get("value", 0)
        return errors / total if total > 0 else 0.0
    
    def _get_error_rate_data(self) -> Dict[str, Any]:
        """Get error rate data."""
        metrics = monitoring_system.get_all_metrics()
        error_rate = self._calculate_error_rate(metrics)
        
        return {
            "current": error_rate,
            "threshold": self.config["alert_thresholds"]["error_rate"],
            "status": "critical" if error_rate > self.config["alert_thresholds"]["error_rate"] else "normal",
            "trend": "stable"  # Would calculate trend from historical data
        }
    
    def _get_alerts_data(self) -> Dict[str, Any]:
        """Get recent alerts data."""
        alerts = monitoring_system.get_alerts(hours_back=1)
        
        return {
            "total": len(alerts),
            "critical": len([a for a in alerts if a.severity == "critical"]),
            "warning": len([a for a in alerts if a.severity == "warning"]),
            "recent": [
                {
                    "name": alert.name,
                    "severity": alert.severity,
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat()
                }
                for alert in alerts[:10]
            ]
        }
    
    def _get_response_times_data(self) -> Dict[str, Any]:
        """Get response times data."""
        metrics = monitoring_system.get_all_metrics()
        response_time_stats = metrics.get("response_time", {})
        
        return {
            "current": response_time_stats.get("mean", 0),
            "p50": response_time_stats.get("p50", 0),
            "p95": response_time_stats.get("p95", 0),
            "p99": response_time_stats.get("p99", 0),
            "threshold": self.config["alert_thresholds"]["response_time_p95"],
            "unit": "ms"
        }
    
    def _get_throughput_data(self) -> Dict[str, Any]:
        """Get throughput data."""
        metrics = monitoring_system.get_all_metrics()
        
        return {
            "requests_per_minute": self._calculate_rpm(metrics),
            "requests_per_hour": self._calculate_rph(metrics),
            "peak_rpm": metrics.get("peak_rpm", {}).get("value", 0)
        }
    
    def _calculate_rpm(self, metrics: Dict[str, Any]) -> float:
        """Calculate requests per minute."""
        # This would be calculated from time-series data
        total = metrics.get("total_requests", {}).get("value", 0)
        return total / 60 if total > 0 else 0
    
    def _calculate_rph(self, metrics: Dict[str, Any]) -> float:
        """Calculate requests per hour."""
        total = metrics.get("total_requests", {}).get("value", 0)
        return total / 3600 if total > 0 else 0
    
    def _get_cache_stats_data(self) -> Dict[str, Any]:
        """Get cache statistics data."""
        cache_stats = cache_manager.get_stats()
        
        # Calculate overall stats
        total_hits = sum(stats.get("hits", 0) for stats in cache_stats.values())
        total_requests = sum(stats.get("hits", 0) + stats.get("misses", 0) for stats in cache_stats.values())
        overall_hit_rate = total_hits / total_requests if total_requests > 0 else 0
        
        return {
            "overall_hit_rate": overall_hit_rate,
            "threshold": self.config["alert_thresholds"]["cache_hit_rate"],
            "backends": cache_stats,
            "total_size": sum(stats.get("total_size_bytes", 0) for stats in cache_stats.values())
        }
    
    def _get_llm_metrics_data(self) -> Dict[str, Any]:
        """Get LLM performance metrics."""
        metrics = monitoring_system.get_all_metrics()
        
        return {
            "total_calls": metrics.get("llm_calls", {}).get("value", 0),
            "avg_response_time": metrics.get("llm_response_time", {}).get("mean", 0),
            "error_rate": self._calculate_llm_error_rate(metrics),
            "tokens_used": metrics.get("llm_tokens", {}).get("value", 0)
        }
    
    def _calculate_llm_error_rate(self, metrics: Dict[str, Any]) -> float:
        """Calculate LLM error rate."""
        total = metrics.get("llm_calls", {}).get("value", 0)
        errors = metrics.get("llm_errors", {}).get("value", 0)
        return errors / total if total > 0 else 0.0
    
    def _get_security_events_data(self) -> Dict[str, Any]:
        """Get security events data."""
        events = security_middleware.get_security_events(hours_back=24)
        
        # Group by hour
        events_by_hour = defaultdict(int)
        for event in events:
            hour_key = event.timestamp.strftime("%Y-%m-%d %H:00")
            events_by_hour[hour_key] += 1
        
        return {
            "timeline": dict(events_by_hour),
            "total": len(events),
            "blocked": len([e for e in events if e.blocked])
        }
    
    def _get_threat_types_data(self) -> Dict[str, Any]:
        """Get threat types distribution."""
        events = security_middleware.get_security_events(hours_back=24)
        
        threat_counts = defaultdict(int)
        for event in events:
            threat_counts[event.threat_type.value] += 1
        
        return {
            "distribution": dict(threat_counts),
            "total": len(events)
        }
    
    def _get_blocked_ips_data(self) -> Dict[str, Any]:
        """Get blocked IPs data."""
        blocked_ips = security_middleware.blocked_ips
        
        return {
            "total": len(blocked_ips),
            "ips": list(blocked_ips)[:10]  # Show top 10
        }
    
    def _get_rate_limits_data(self) -> Dict[str, Any]:
        """Get rate limiting data."""
        # This would get actual rate limiting data
        return {
            "global_limit": {"used": 100, "limit": 1000, "remaining": 900},
            "per_ip_limit": {"used": 50, "limit": 100, "remaining": 50},
            "per_user_limit": {"used": 25, "limit": 50, "remaining": 25}
        }
    
    def get_dashboard_data(self, dashboard_type: DashboardType) -> Dict[str, Any]:
        """
        Get complete dashboard data.
        
        Args:
            dashboard_type: Type of dashboard
            
        Returns:
            Dashboard data
        """
        layout = self.config["widget_layout"].get(dashboard_type.value, [])
        
        dashboard_data = {
            "type": dashboard_type.value,
            "title": f"{dashboard_type.value.title()} Dashboard",
            "last_updated": datetime.now().isoformat(),
            "widgets": []
        }
        
        for widget_config in layout:
            widget_id = widget_config["widget_id"]
            if widget_id in self.dashboard_data:
                widget_data = self.dashboard_data[widget_id]
                dashboard_data["widgets"].append({
                    "id": widget_id,
                    "title": widget_data["widget"].title,
                    "type": widget_data["widget"].type,
                    "position": widget_config,
                    "data": widget_data["data"],
                    "last_updated": widget_data["last_updated"]
                })
        
        return dashboard_data
    
    def export_dashboard_data(self, format: str = "json") -> str:
        """
        Export dashboard data.
        
        Args:
            format: Export format (json, csv)
            
        Returns:
            Exported data
        """
        if format == "json":
            return json.dumps(self.dashboard_data, indent=2, default=str)
        else:
            # CSV export would be implemented here
            return "CSV export not implemented"
    
    def create_custom_widget(
        self,
        widget_id: str,
        title: str,
        widget_type: str,
        data_source: str,
        position: Dict[str, int],
        config: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Create a custom widget.
        
        Args:
            widget_id: Widget ID
            title: Widget title
            widget_type: Widget type
            data_source: Data source
            position: Widget position
            config: Widget configuration
        """
        widget = DashboardWidget(
            widget_id=widget_id,
            title=title,
            type=widget_type,
            position=position,
            data_source=data_source,
            refresh_interval=self.config["refresh_interval"],
            config=config or {}
        )
        
        self.widgets[widget_id] = widget
    
    def remove_widget(self, widget_id: str) -> bool:
        """
        Remove a widget.
        
        Args:
            widget_id: Widget ID to remove
            
        Returns:
            True if removed
        """
        if widget_id in self.widgets:
            del self.widgets[widget_id]
            if widget_id in self.dashboard_data:
                del self.dashboard_data[widget_id]
            return True
        return False
    
    def get_widget_list(self) -> List[Dict[str, Any]]:
        """Get list of all widgets."""
        return [
            {
                "id": widget.widget_id,
                "title": widget.title,
                "type": widget.type,
                "data_source": widget.data_source,
                "position": widget.position,
                "refresh_interval": widget.refresh_interval
            }
            for widget in self.widgets.values()
        ]


# Global dashboard instance
monitoring_dashboard = MonitoringDashboard()
