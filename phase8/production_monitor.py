"""
Phase 8: Production Monitoring System
Advanced monitoring and analytics for Streamlit Cloud deployments
"""

import os
import sys
import time
import requests
import json
import logging
import psutil
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MetricPoint:
    """Single metric data point"""
    timestamp: datetime
    metric_name: str
    value: float
    unit: str
    tags: Dict[str, str]

@dataclass
class HealthStatus:
    """Health check status"""
    status: str
    timestamp: datetime
    response_time: float
    error_message: Optional[str] = None
    details: Dict[str, Any] = None

class ProductionMonitor:
    """Advanced production monitoring system"""
    
    def __init__(self):
        self.streamlit_url = os.getenv('STREAMLIT_URL', 'http://localhost:8501')
        self.api_url = os.getenv('API_BASE_URL', 'http://localhost:8000')
        self.metrics_store: List[MetricPoint] = []
        self.health_history: List[HealthStatus] = []
        self.alert_thresholds = {
            'response_time_warning': 2.0,  # seconds
            'response_time_critical': 5.0,  # seconds
            'error_rate_warning': 5.0,  # percentage
            'error_rate_critical': 10.0,  # percentage
            'cpu_usage_warning': 80.0,  # percentage
            'memory_usage_warning': 85.0,  # percentage
            'disk_usage_warning': 90.0  # percentage
        }
        
    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system performance metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Network stats (simplified)
            network = psutil.net_io_counters()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu_usage_percent': cpu_percent,
                'memory_usage_percent': memory_percent,
                'disk_usage_percent': disk_percent,
                'network_bytes_sent': network.bytes_sent,
                'network_bytes_recv': network.bytes_recv,
                'load_average': os.getloadavg()[0] if hasattr(os, 'getloadavg') else 0
            }
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {str(e)}")
            return {}
    
    def check_streamlit_health(self) -> HealthStatus:
        """Check Streamlit application health"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.streamlit_url}/_stcore/health", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return HealthStatus(
                    status="healthy",
                    timestamp=datetime.now(),
                    response_time=response_time,
                    details=response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                )
            else:
                return HealthStatus(
                    status="unhealthy",
                    timestamp=datetime.now(),
                    response_time=response_time,
                    error_message=f"HTTP {response.status_code}"
                )
                
        except Exception as e:
            return HealthStatus(
                status="error",
                timestamp=datetime.now(),
                response_time=0.0,
                error_message=str(e)
            )
    
    def check_api_health(self) -> HealthStatus:
        """Check API health"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.api_url}/health", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return HealthStatus(
                    status="healthy",
                    timestamp=datetime.now(),
                    response_time=response_time,
                    details=response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                )
            else:
                return HealthStatus(
                    status="unhealthy",
                    timestamp=datetime.now(),
                    response_time=response_time,
                    error_message=f"HTTP {response.status_code}"
                )
                
        except Exception as e:
            return HealthStatus(
                status="error",
                timestamp=datetime.now(),
                response_time=0.0,
                error_message=str(e)
            )
    
    def check_integration_health(self) -> Dict[str, Any]:
        """Check frontend-backend integration health"""
        try:
            # Test API connectivity from frontend perspective
            test_payload = {
                "location": "Bangalore",
                "budget": 2000,
                "cuisine": "Italian"
            }
            
            start_time = time.time()
            response = requests.post(
                f"{self.api_url}/recommend",
                json=test_payload,
                timeout=30
            )
            response_time = time.time() - start_time
            
            return {
                'timestamp': datetime.now().isoformat(),
                'integration_test': {
                    'status_code': response.status_code,
                    'response_time': response_time,
                    'success': response.status_code == 200,
                    'has_recommendations': len(response.json().get("recommendations", [])) > 0 if response.status_code == 200 else False
                }
            }
            
        except Exception as e:
            return {
                'timestamp': datetime.now().isoformat(),
                'integration_test': {
                    'status': 'error',
                    'error': str(e)
                }
            }
    
    def calculate_performance_metrics(self, metrics_history: List[MetricPoint]) -> Dict[str, Any]:
        """Calculate performance metrics from history"""
        if not metrics_history:
            return {}
        
        # Filter metrics by time window (last hour)
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_metrics = [m for m in metrics_history if m.timestamp > one_hour_ago]
        
        if not recent_metrics:
            return {}
        
        # Calculate percentiles
        response_times = [m.value for m in recent_metrics if m.metric_name == 'response_time']
        if response_times:
            response_times.sort()
            p50 = response_times[len(response_times)//2] if len(response_times) > 1 else 0
            p95 = response_times[int(len(response_times)*0.95)] if len(response_times) > 1 else 0
            p99 = response_times[int(len(response_times)*0.99)] if len(response_times) > 1 else 0
            avg_response_time = sum(response_times) / len(response_times)
        else:
            p50 = p95 = p99 = avg_response_time = 0
        
        # Calculate error rate
        total_requests = len(recent_metrics)
        error_requests = len([m for m in recent_metrics if m.metric_name == 'error_rate'])
        error_rate = (error_requests / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'time_window': '1_hour',
            'total_requests': total_requests,
            'response_time_p50': p50,
            'response_time_p95': p95,
            'response_time_p99': p99,
            'average_response_time': avg_response_time,
            'error_rate_percent': error_rate,
            'uptime_percent': 100.0 - error_rate
        }
    
    def check_alert_conditions(self, metrics: Dict[str, Any], health_status: Dict[str, HealthStatus]) -> List[Dict[str, Any]]:
        """Check for alert conditions"""
        alerts = []
        
        # Response time alerts
        if 'response_time_p95' in metrics:
            if metrics['response_time_p95'] > self.alert_thresholds['response_time_critical']:
                alerts.append({
                    'type': 'critical',
                    'metric': 'response_time',
                    'value': metrics['response_time_p95'],
                    'threshold': self.alert_thresholds['response_time_critical'],
                    'message': 'Critical response time detected',
                    'timestamp': datetime.now().isoformat()
                })
            elif metrics['response_time_p95'] > self.alert_thresholds['response_time_warning']:
                alerts.append({
                    'type': 'warning',
                    'metric': 'response_time',
                    'value': metrics['response_time_p95'],
                    'threshold': self.alert_thresholds['response_time_warning'],
                    'message': 'High response time detected',
                    'timestamp': datetime.now().isoformat()
                })
        
        # Error rate alerts
        if 'error_rate_percent' in metrics:
            if metrics['error_rate_percent'] > self.alert_thresholds['error_rate_critical']:
                alerts.append({
                    'type': 'critical',
                    'metric': 'error_rate',
                    'value': metrics['error_rate_percent'],
                    'threshold': self.alert_thresholds['error_rate_critical'],
                    'message': 'Critical error rate detected',
                    'timestamp': datetime.now().isoformat()
                })
            elif metrics['error_rate_percent'] > self.alert_thresholds['error_rate_warning']:
                alerts.append({
                    'type': 'warning',
                    'metric': 'error_rate',
                    'value': metrics['error_rate_percent'],
                    'threshold': self.alert_thresholds['error_rate_warning'],
                    'message': 'High error rate detected',
                    'timestamp': datetime.now().isoformat()
                })
        
        # System resource alerts
        system_metrics = self.collect_system_metrics()
        if system_metrics.get('cpu_usage_percent', 0) > self.alert_thresholds['cpu_usage_warning']:
            alerts.append({
                'type': 'warning',
                'metric': 'cpu_usage',
                'value': system_metrics['cpu_usage_percent'],
                'threshold': self.alert_thresholds['cpu_usage_warning'],
                'message': 'High CPU usage detected',
                'timestamp': datetime.now().isoformat()
            })
        
        if system_metrics.get('memory_usage_percent', 0) > self.alert_thresholds['memory_usage_warning']:
            alerts.append({
                'type': 'warning',
                'metric': 'memory_usage',
                'value': system_metrics['memory_usage_percent'],
                'threshold': self.alert_thresholds['memory_usage_warning'],
                'message': 'High memory usage detected',
                'timestamp': datetime.now().isoformat()
            })
        
        # Health status alerts
        for service, status in health_status.items():
            if status.status != 'healthy':
                alerts.append({
                    'type': 'critical',
                    'metric': 'service_health',
                    'service': service,
                    'status': status.status,
                    'message': f'{service} service is {status.status}',
                    'timestamp': status.timestamp.isoformat()
                })
        
        return alerts
    
    def generate_monitoring_dashboard(self) -> Dict[str, Any]:
        """Generate comprehensive monitoring dashboard data"""
        # Collect all metrics
        system_metrics = self.collect_system_metrics()
        streamlit_health = self.check_streamlit_health()
        api_health = self.check_api_health()
        integration_health = self.check_integration_health()
        performance_metrics = self.calculate_performance_metrics(self.metrics_store)
        alerts = self.check_alert_conditions(performance_metrics, {'streamlit': streamlit_health, 'api': api_health})
        
        return {
            'timestamp': datetime.now().isoformat(),
            'system_metrics': system_metrics,
            'health_status': {
                'streamlit': streamlit_health.__dict__ if hasattr(streamlit_health, '__dict__') else {},
                'api': api_health.__dict__ if hasattr(api_health, '__dict__') else {},
                'integration': integration_health
            },
            'performance_metrics': performance_metrics,
            'alerts': alerts,
            'summary': {
                'overall_status': 'healthy' if all(h.status == 'healthy' for h in [streamlit_health, api_health]) else 'degraded',
                'total_alerts': len(alerts),
                'critical_alerts': len([a for a in alerts if a.get('type') == 'critical']),
                'warning_alerts': len([a for a in alerts if a.get('type') == 'warning'])
            }
        }

def main():
    """Main entry point for production monitoring"""
    monitor = ProductionMonitor()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "monitor":
            dashboard = monitor.generate_monitoring_dashboard()
            print(json.dumps(dashboard, indent=2))
            
        elif command == "health-check":
            streamlit_health = monitor.check_streamlit_health()
            api_health = monitor.check_api_health()
            integration_health = monitor.check_integration_health()
            
            health_report = {
                'timestamp': datetime.now().isoformat(),
                'streamlit_health': streamlit_health.__dict__ if hasattr(streamlit_health, '__dict__') else {},
                'api_health': api_health.__dict__ if hasattr(api_health, '__dict__') else {},
                'integration_health': integration_health,
                'overall_status': 'healthy' if streamlit_health.status == 'healthy' and api_health.status == 'healthy' else 'unhealthy'
            }
            
            print(json.dumps(health_report, indent=2))
            
        elif command == "metrics":
            metrics = monitor.calculate_performance_metrics(monitor.metrics_store)
            print(json.dumps(metrics, indent=2))
            
        elif command == "alerts":
            system_metrics = monitor.collect_system_metrics()
            streamlit_health = monitor.check_streamlit_health()
            api_health = monitor.check_api_health()
            performance_metrics = monitor.calculate_performance_metrics(monitor.metrics_store)
            alerts = monitor.check_alert_conditions(performance_metrics, {'streamlit': streamlit_health, 'api': api_health})
            
            alert_report = {
                'timestamp': datetime.now().isoformat(),
                'system_metrics': system_metrics,
                'alerts': alerts
            }
            
            print(json.dumps(alert_report, indent=2))
            
        else:
            print("❌ Unknown command")
            print("Available commands: monitor, health-check, metrics, alerts")
    else:
        print("🔍 Phase 8: Production Monitoring System")
        print("Commands: monitor, health-check, metrics, alerts")
        print("Example: python phase8/production_monitor.py monitor")

if __name__ == "__main__":
    main()
