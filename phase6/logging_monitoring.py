"""Logging and Monitoring Stack: Comprehensive logging, monitoring, and error tracking."""

from typing import Dict, Any, List, Optional, Union
import logging
import sys
import json
import time
import traceback
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import threading
from collections import defaultdict, deque
import statistics


class LogLevel(Enum):
    """Log levels for the system."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class MetricType(Enum):
    """Types of metrics to track."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class LogEntry:
    """Structured log entry."""
    timestamp: datetime
    level: LogLevel
    message: str
    module: str
    function: str
    line_number: int
    user_id: Optional[str]
    session_id: Optional[str]
    request_id: Optional[str]
    extra_data: Dict[str, Any]
    exception: Optional[str]


@dataclass
class Metric:
    """Metric data point."""
    name: str
    metric_type: MetricType
    value: Union[int, float]
    labels: Dict[str, str]
    timestamp: datetime
    unit: Optional[str] = None


@dataclass
class Alert:
    """Alert definition."""
    alert_id: str
    name: str
    severity: str
    condition: str
    threshold: float
    current_value: float
    timestamp: datetime
    message: str
    labels: Dict[str, str]


class LoggingManager:
    """Advanced logging manager with structured logging."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the logging manager.
        
        Args:
            config: Logging configuration
        """
        self.config = config or self._get_default_config()
        self.logger = self._setup_logger()
        self.log_storage = deque(maxlen=self.config.get("max_log_entries", 10000))
        self.log_file = None
        
        # Setup file logging if configured
        if self.config.get("log_to_file", True):
            self._setup_file_logging()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default logging configuration."""
        return {
            "level": "INFO",
            "format": "json",
            "log_to_file": True,
            "log_file_path": "logs/application.log",
            "max_log_entries": 10000,
            "include_traceback": True,
            "structured_logging": True
        }
    
    def _setup_logger(self) -> logging.Logger:
        """Setup the main logger."""
        logger = logging.getLogger("restaurant_recommendation")
        logger.setLevel(getattr(logging, self.config["level"]))
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, self.config["level"]))
        
        # Formatter
        if self.config["structured_logging"]:
            formatter = self._get_structured_formatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def _get_structured_formatter(self) -> logging.Formatter:
        """Get structured JSON formatter."""
        class StructuredFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                    "level": record.levelname,
                    "message": record.getMessage(),
                    "module": record.module,
                    "function": record.funcName,
                    "line_number": record.lineno,
                    "thread": record.thread,
                    "process": record.process
                }
                
                # Add extra fields if present
                if hasattr(record, 'user_id'):
                    log_entry["user_id"] = record.user_id
                if hasattr(record, 'session_id'):
                    log_entry["session_id"] = record.session_id
                if hasattr(record, 'request_id'):
                    log_entry["request_id"] = record.request_id
                if hasattr(record, 'extra_data'):
                    log_entry["extra_data"] = record.extra_data
                
                # Add exception if present
                if record.exc_info:
                    log_entry["exception"] = self.formatException(record.exc_info)
                
                return json.dumps(log_entry)
        
        return StructuredFormatter()
    
    def _setup_file_logging(self) -> None:
        """Setup file logging."""
        log_path = Path(self.config["log_file_path"])
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(getattr(logging, self.config["level"]))
        
        if self.config["structured_logging"]:
            formatter = self._get_structured_formatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        self.log_file = log_path
    
    def log(
        self,
        level: LogLevel,
        message: str,
        module: str = "unknown",
        function: str = "unknown",
        line_number: int = 0,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None,
        exception: Optional[Exception] = None
    ) -> None:
        """
        Log a message with structured data.
        
        Args:
            level: Log level
            message: Log message
            module: Module name
            function: Function name
            line_number: Line number
            user_id: User identifier
            session_id: Session identifier
            request_id: Request identifier
            extra_data: Additional data
            exception: Exception to log
        """
        log_entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            message=message,
            module=module,
            function=function,
            line_number=line_number,
            user_id=user_id,
            session_id=session_id,
            request_id=request_id,
            extra_data=extra_data or {},
            exception=str(exception) if exception else None
        )
        
        # Store in memory
        self.log_storage.append(log_entry)
        
        # Log to logger
        log_method = getattr(self.logger, level.value.lower())
        
        # Add extra fields to record
        extra = {}
        if user_id:
            extra['user_id'] = user_id
        if session_id:
            extra['session_id'] = session_id
        if request_id:
            extra['request_id'] = request_id
        if extra_data:
            extra['extra_data'] = extra_data
        
        if exception:
            log_method(message, exc_info=True, extra=extra)
        else:
            log_method(message, extra=extra)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self.log(LogLevel.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self.log(LogLevel.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self.log(LogLevel.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self.log(LogLevel.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        self.log(LogLevel.CRITICAL, message, **kwargs)
    
    def get_logs(
        self,
        level: Optional[LogLevel] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[LogEntry]:
        """
        Get logs with filtering.
        
        Args:
            level: Filter by log level
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Maximum number of logs to return
            
        Returns:
            List of log entries
        """
        filtered_logs = list(self.log_storage)
        
        # Apply filters
        if level:
            filtered_logs = [log for log in filtered_logs if log.level == level]
        
        if start_time:
            filtered_logs = [log for log in filtered_logs if log.timestamp >= start_time]
        
        if end_time:
            filtered_logs = [log for log in filtered_logs if log.timestamp <= end_time]
        
        # Sort by timestamp (newest first) and limit
        filtered_logs.sort(key=lambda x: x.timestamp, reverse=True)
        return filtered_logs[:limit]
    
    def get_error_summary(self, hours_back: int = 24) -> Dict[str, Any]:
        """Get error summary for the last N hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        error_logs = [
            log for log in self.log_storage
            if log.level in [LogLevel.ERROR, LogLevel.CRITICAL] and log.timestamp >= cutoff_time
        ]
        
        if not error_logs:
            return {
                "total_errors": 0,
                "error_rate": 0.0,
                "most_common_errors": [],
                "errors_by_hour": {}
            }
        
        # Count errors by message
        error_counts = defaultdict(int)
        for log in error_logs:
            error_counts[log.message] += 1
        
        # Errors by hour
        errors_by_hour = defaultdict(int)
        for log in error_logs:
            hour_key = log.timestamp.strftime("%Y-%m-%d %H:00")
            errors_by_hour[hour_key] += 1
        
        # Calculate error rate
        total_logs = len([log for log in self.log_storage if log.timestamp >= cutoff_time])
        error_rate = len(error_logs) / total_logs if total_logs > 0 else 0
        
        return {
            "total_errors": len(error_logs),
            "error_rate": error_rate,
            "most_common_errors": sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            "errors_by_hour": dict(errors_by_hour)
        }


class MonitoringSystem:
    """System for collecting and managing metrics and alerts."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the monitoring system.
        
        Args:
            config: Monitoring configuration
        """
        self.config = config or self._get_default_config()
        self.metrics_storage = deque(maxlen=self.config.get("max_metrics", 10000))
        self.alerts_storage = deque(maxlen=self.config.get("max_alerts", 1000))
        self.counters = defaultdict(int)
        self.gauges = defaultdict(float)
        self.histograms = defaultdict(list)
        self.timers = defaultdict(list)
        
        # Alert rules
        self.alert_rules = self._setup_default_alert_rules()
        
        # Background thread for alert checking
        self.alert_thread = threading.Thread(target=self._alert_monitor, daemon=True)
        self.alert_thread.start()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default monitoring configuration."""
        return {
            "max_metrics": 10000,
            "max_alerts": 1000,
            "alert_check_interval": 60,  # seconds
            "metric_retention_hours": 24
        }
    
    def _setup_default_alert_rules(self) -> List[Dict[str, Any]]:
        """Setup default alert rules."""
        return [
            {
                "name": "High Error Rate",
                "metric": "error_rate",
                "condition": "greater_than",
                "threshold": 0.05,  # 5%
                "severity": "warning"
            },
            {
                "name": "High Response Time",
                "metric": "response_time_p95",
                "condition": "greater_than",
                "threshold": 2000,  # ms
                "severity": "warning"
            },
            {
                "name": "Low Success Rate",
                "metric": "success_rate",
                "condition": "less_than",
                "threshold": 0.95,  # 95%
                "severity": "critical"
            },
            {
                "name": "High Memory Usage",
                "metric": "memory_usage",
                "condition": "greater_than",
                "threshold": 0.8,  # 80%
                "severity": "warning"
            }
        ]
    
    def increment_counter(
        self,
        name: str,
        value: int = 1,
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Increment a counter metric.
        
        Args:
            name: Metric name
            value: Value to increment by
            labels: Metric labels
        """
        self.counters[name] += value
        
        metric = Metric(
            name=name,
            metric_type=MetricType.COUNTER,
            value=self.counters[name],
            labels=labels or {},
            timestamp=datetime.now(),
            unit="count"
        )
        
        self.metrics_storage.append(metric)
    
    def set_gauge(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Set a gauge metric.
        
        Args:
            name: Metric name
            value: Value to set
            labels: Metric labels
        """
        self.gauges[name] = value
        
        metric = Metric(
            name=name,
            metric_type=MetricType.GAUGE,
            value=value,
            labels=labels or {},
            timestamp=datetime.now(),
            unit="value"
        )
        
        self.metrics_storage.append(metric)
    
    def record_histogram(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Record a histogram metric.
        
        Args:
            name: Metric name
            value: Value to record
            labels: Metric labels
        """
        self.histograms[name].append(value)
        
        # Keep only recent values (last 1000)
        if len(self.histograms[name]) > 1000:
            self.histograms[name] = self.histograms[name][-1000:]
        
        metric = Metric(
            name=name,
            metric_type=MetricType.HISTOGRAM,
            value=value,
            labels=labels or {},
            timestamp=datetime.now(),
            unit="value"
        )
        
        self.metrics_storage.append(metric)
    
    def record_timer(
        self,
        name: str,
        duration: float,
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Record a timer metric.
        
        Args:
            name: Metric name
            duration: Duration in seconds
            labels: Metric labels
        """
        self.timers[name].append(duration)
        
        # Keep only recent values (last 1000)
        if len(self.timers[name]) > 1000:
            self.timers[name] = self.timers[name][-1000:]
        
        metric = Metric(
            name=name,
            metric_type=MetricType.TIMER,
            value=duration,
            labels=labels or {},
            timestamp=datetime.now(),
            unit="seconds"
        )
        
        self.metrics_storage.append(metric)
    
    def get_metric_stats(
        self,
        name: str,
        metric_type: Optional[MetricType] = None
    ) -> Dict[str, Any]:
        """
        Get statistics for a metric.
        
        Args:
            name: Metric name
            metric_type: Type of metric
            
        Returns:
            Metric statistics
        """
        if metric_type == MetricType.COUNTER:
            return {"value": self.counters.get(name, 0)}
        
        elif metric_type == MetricType.GAUGE:
            return {"value": self.gauges.get(name, 0)}
        
        elif metric_type == MetricType.HISTOGRAM:
            values = self.histograms.get(name, [])
            if not values:
                return {"count": 0}
            
            return {
                "count": len(values),
                "sum": sum(values),
                "min": min(values),
                "max": max(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "p50": statistics.quantiles(values, n=100)[49] if len(values) >= 100 else statistics.median(values),
                "p95": statistics.quantiles(values, n=100)[94] if len(values) >= 100 else max(values),
                "p99": statistics.quantiles(values, n=100)[98] if len(values) >= 100 else max(values)
            }
        
        elif metric_type == MetricType.TIMER:
            values = self.timers.get(name, [])
            if not values:
                return {"count": 0}
            
            return {
                "count": len(values),
                "sum": sum(values),
                "min": min(values),
                "max": max(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "p50": statistics.quantiles(values, n=100)[49] if len(values) >= 100 else statistics.median(values),
                "p95": statistics.quantiles(values, n=100)[94] if len(values) >= 100 else max(values),
                "p99": statistics.quantiles(values, n=100)[98] if len(values) >= 100 else max(values)
            }
        
        return {}
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all current metrics."""
        metrics = {}
        
        # Counters
        for name, value in self.counters.items():
            metrics[name] = {"type": "counter", "value": value}
        
        # Gauges
        for name, value in self.gauges.items():
            metrics[name] = {"type": "gauge", "value": value}
        
        # Histograms
        for name in self.histograms.keys():
            metrics[name] = self.get_metric_stats(name, MetricType.HISTOGRAM)
        
        # Timers
        for name in self.timers.keys():
            metrics[name] = self.get_metric_stats(name, MetricType.TIMER)
        
        return metrics
    
    def check_alerts(self) -> List[Alert]:
        """Check all alert rules and return triggered alerts."""
        alerts = []
        
        for rule in self.alert_rules:
            metric_name = rule["metric"]
            condition = rule["condition"]
            threshold = rule["threshold"]
            
            # Get current metric value
            metric_stats = self.get_metric_stats(metric_name)
            if not metric_stats:
                continue
            
            current_value = metric_stats.get("value", metric_stats.get("mean", 0))
            
            # Check condition
            triggered = False
            if condition == "greater_than" and current_value > threshold:
                triggered = True
            elif condition == "less_than" and current_value < threshold:
                triggered = True
            elif condition == "equals" and current_value == threshold:
                triggered = True
            
            if triggered:
                alert = Alert(
                    alert_id=f"alert_{int(time.time())}_{len(alerts)}",
                    name=rule["name"],
                    severity=rule["severity"],
                    condition=condition,
                    threshold=threshold,
                    current_value=current_value,
                    timestamp=datetime.now(),
                    message=f"{rule['name']}: {metric_name} is {current_value:.2f} (threshold: {threshold})",
                    labels={"metric": metric_name, "condition": condition}
                )
                
                alerts.append(alert)
                self.alerts_storage.append(alert)
        
        return alerts
    
    def _alert_monitor(self) -> None:
        """Background thread for monitoring alerts."""
        while True:
            try:
                alerts = self.check_alerts()
                if alerts:
                    # Log alerts
                    for alert in alerts:
                        print(f"ALERT: {alert.message}")
                
                time.sleep(self.config["alert_check_interval"])
            except Exception as e:
                print(f"Alert monitoring error: {e}")
                time.sleep(self.config["alert_check_interval"])
    
    def get_alerts(
        self,
        severity: Optional[str] = None,
        hours_back: int = 24
    ) -> List[Alert]:
        """
        Get alerts with filtering.
        
        Args:
            severity: Filter by severity
            hours_back: Filter by time period
            
        Returns:
            List of alerts
        """
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        filtered_alerts = [
            alert for alert in self.alerts_storage
            if alert.timestamp >= cutoff_time
        ]
        
        if severity:
            filtered_alerts = [alert for alert in filtered_alerts if alert.severity == severity]
        
        return sorted(filtered_alerts, key=lambda x: x.timestamp, reverse=True)
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status."""
        # Get recent metrics
        recent_metrics = {}
        
        # Success rate
        total_requests = self.counters.get("total_requests", 0)
        successful_requests = self.counters.get("successful_requests", 0)
        success_rate = successful_requests / total_requests if total_requests > 0 else 1.0
        recent_metrics["success_rate"] = success_rate
        
        # Error rate
        error_requests = self.counters.get("error_requests", 0)
        error_rate = error_requests / total_requests if total_requests > 0 else 0.0
        recent_metrics["error_rate"] = error_rate
        
        # Response time
        if self.timers.get("response_time"):
            response_time_stats = self.get_metric_stats("response_time", MetricType.TIMER)
            recent_metrics["response_time_p95"] = response_time_stats.get("p95", 0)
        
        # Recent alerts
        recent_alerts = self.get_alerts(hours_back=1)
        
        # Determine health status
        health_status = "healthy"
        issues = []
        
        if error_rate > 0.05:  # 5%
            health_status = "degraded"
            issues.append(f"High error rate: {error_rate:.2%}")
        
        if recent_metrics.get("response_time_p95", 0) > 2000:  # 2 seconds
            health_status = "degraded"
            issues.append(f"High response time: {recent_metrics['response_time_p95']:.0f}ms")
        
        if success_rate < 0.95:  # 95%
            health_status = "unhealthy"
            issues.append(f"Low success rate: {success_rate:.2%}")
        
        critical_alerts = [alert for alert in recent_alerts if alert.severity == "critical"]
        if critical_alerts:
            health_status = "unhealthy"
            issues.append(f"{len(critical_alerts)} critical alerts")
        
        return {
            "status": health_status,
            "timestamp": datetime.now().isoformat(),
            "metrics": recent_metrics,
            "recent_alerts": len(recent_alerts),
            "issues": issues
        }


# Global instances
logging_manager = LoggingManager()
monitoring_system = MonitoringSystem()
