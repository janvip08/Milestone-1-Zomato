"""Main entry point and examples for Phase 6 Production Readiness and Observability."""

import os
import sys
import argparse
import logging
import time
from datetime import datetime
from typing import Dict, Any, List

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phase6.logging_monitoring import logging_manager, monitoring_system
from phase6.caching_layer import cache_manager
from phase6.security_middleware import security_middleware
from phase6.deployment_pipeline import deployment_pipeline, Environment
from phase6.monitoring_dashboard import monitoring_dashboard
from phase6.incident_runbook import incident_runbook, recovery_procedures


def setup_logging(level: str = "INFO"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def example_logging_monitoring():
    """Example of logging and monitoring system."""
    print("=" * 60)
    print("PHASE 6 LOGGING AND MONITORING EXAMPLE")
    print("=" * 60)
    
    # Log various types of events
    print("Logging sample events...")
    
    logging_manager.info("System startup initiated", 
                        module="main", 
                        function="startup",
                        extra_data={"version": "1.0.0", "environment": "production"})
    
    logging_manager.warning("High memory usage detected",
                           module="monitoring",
                           function="check_memory",
                           extra_data={"memory_percent": 85.2, "threshold": 80})
    
    logging_manager.error("API request failed",
                         module="api",
                         function="handle_request",
                         extra_data={"endpoint": "/recommend", "status_code": 500})
    
    # Record metrics
    print("Recording metrics...")
    monitoring_system.increment_counter("total_requests", 1)
    monitoring_system.set_gauge("active_users", 42)
    monitoring_system.record_histogram("response_time", 0.85)
    monitoring_system.record_timer("api_call", 1.2)
    
    # Get system health
    print("Getting system health...")
    health = monitoring_system.get_system_health()
    print(f"System Status: {health['status']}")
    print(f"Metrics: {health['metrics']}")
    
    # Get recent logs
    print("Recent error logs:")
    error_logs = logging_manager.get_logs(level=logging_manager.log_storage[0].__class__.ERROR, limit=5)
    for log in error_logs:
        print(f"  - {log.message} ({log.timestamp})")
    
    # Get alerts
    print("Recent alerts:")
    alerts = monitoring_system.get_alerts(hours_back=1)
    for alert in alerts:
        print(f"  - {alert.name}: {alert.message}")


def example_caching_layer():
    """Example of caching layer functionality."""
    print("\n" + "=" * 60)
    print("PHASE 6 CACHING LAYER EXAMPLE")
    print("=" * 60)
    
    # Test basic caching
    print("Testing basic cache operations...")
    
    # Set some values
    cache_manager.set("test_key", "test_value", ttl=60)
    cache_manager.set("user_123", {"name": "John", "preferences": {"cuisine": "Italian"}})
    cache_manager.set("recommendation:bellandur:italian", ["Restaurant A", "Restaurant B"])
    
    # Get values
    value = cache_manager.get("test_key")
    print(f"Retrieved: {value}")
    
    user_data = cache_manager.get("user_123")
    print(f"User data: {user_data}")
    
    recommendations = cache_manager.get("recommendation:bellandur:italian")
    print(f"Recommendations: {recommendations}")
    
    # Test cache miss
    missing = cache_manager.get("non_existent_key")
    print(f"Missing key: {missing}")
    
    # Get cache statistics
    print("Cache statistics:")
    stats = cache_manager.get_stats()
    for backend, backend_stats in stats.items():
        print(f"  {backend}: {backend_stats}")
    
    # Test cache cleanup
    print("Cleaning up expired entries...")
    cleanup_results = cache_manager.cleanup_expired()
    print(f"Cleaned up {sum(cleanup_results.values())} expired entries")


def example_security_middleware():
    """Example of security middleware functionality."""
    print("\n" + "=" * 60)
    print("PHASE 6 SECURITY MIDDLEWARE EXAMPLE")
    print("=" * 60)
    
    # Test input sanitization
    print("Testing input sanitization...")
    
    malicious_inputs = [
        "'; DROP TABLE users; --",
        "<script>alert('xss')</script>",
        "admin' OR '1'='1",
        "normal input"
    ]
    
    for input_text in malicious_inputs:
        sanitized = security_middleware.sanitize_input(input_text)
        threats = security_middleware.sanitizer.detect_threats(input_text)
        print(f"Input: {input_text}")
        print(f"Sanitized: {sanitized}")
        print(f"Threats: {[t.value for t in threats]}")
        print()
    
    # Test rate limiting
    print("Testing rate limiting...")
    
    # Simulate multiple requests from same IP
    ip = "192.168.1.100"
    for i in range(5):
        allowed, info = security_middleware.rate_limiter.is_allowed(ip, "per_ip")
        print(f"Request {i+1}: {'Allowed' if allowed else 'Blocked'} - {info['message']}")
        if not allowed:
            break
    
    # Get rate limit info
    rate_info = security_middleware.rate_limiter.get_rate_limit_info(ip)
    print(f"Rate limit info: {rate_info}")
    
    # Test IP validation
    print("Testing IP validation...")
    test_ips = ["192.168.1.1", "10.0.0.1", "invalid_ip", "127.0.0.1"]
    for ip in test_ips:
        is_valid = security_middleware.validate_ip_address(ip)
        print(f"IP {ip}: {'Valid' if is_valid else 'Invalid'}")
    
    # Get security events
    print("Recent security events:")
    events = security_middleware.get_security_events(hours_back=1)
    for event in events:
        print(f"  - {event.threat_type.value}: {event.message}")


def example_deployment_pipeline():
    """Example of deployment pipeline functionality."""
    print("\n" + "=" * 60)
    print("PHASE 6 DEPLOYMENT PIPELINE EXAMPLE")
    print("=" * 60)
    
    # Test environment validation
    print("Testing environment validation...")
    
    for env in [Environment.DEVELOPMENT, Environment.STAGING, Environment.PRODUCTION]:
        is_valid, errors = deployment_pipeline.validate_environment(env)
        print(f"Environment {env.value}: {'Valid' if is_valid else 'Invalid'}")
        if errors:
            for error in errors:
                print(f"  Error: {error}")
    
    # Create deployment configuration
    print("Creating deployment configuration...")
    deployment_config = deployment_pipeline.create_deployment_config(
        environment=Environment.STAGING,
        version="v1.2.3"
    )
    
    print(f"Deployment config:")
    print(f"  Environment: {deployment_config.environment.value}")
    print(f"  Version: {deployment_config.version}")
    print(f"  Git branch: {deployment_config.git_branch}")
    print(f"  Health check URL: {deployment_config.health_check_url}")
    
    # Test environment file creation
    print("Creating environment files...")
    
    for env in [Environment.DEVELOPMENT, Environment.STAGING]:
        env_file = deployment_pipeline.environment_manager.create_env_file(env)
        print(f"Created {env.value} environment file: {env_file}")
    
    # Test deployment status
    print("Getting deployment status...")
    status = deployment_pipeline.get_deployment_status(Environment.STAGING)
    print(f"Status: {status}")


def example_monitoring_dashboard():
    """Example of monitoring dashboard functionality."""
    print("\n" + "=" * 60)
    print("PHASE 6 MONITORING DASHBOARD EXAMPLE")
    print("=" * 60)
    
    # Start dashboard
    print("Starting monitoring dashboard...")
    monitoring_dashboard.start_dashboard()
    
    # Wait for data refresh
    time.sleep(2)
    
    # Get dashboard data
    print("Getting dashboard data...")
    
    overview_data = monitoring_dashboard.get_dashboard_data(
        monitoring_dashboard.DashboardType.OVERVIEW
    )
    
    print(f"Overview Dashboard:")
    print(f"  Widgets: {len(overview_data['widgets'])}")
    print(f"  Last updated: {overview_data['last_updated']}")
    
    for widget in overview_data['widgets'][:3]:  # Show first 3 widgets
        print(f"    {widget['title']}: {widget['type']}")
    
    # Get performance dashboard
    performance_data = monitoring_dashboard.get_dashboard_data(
        monitoring_dashboard.DashboardType.PERFORMANCE
    )
    
    print(f"Performance Dashboard:")
    print(f"  Widgets: {len(performance_data['widgets'])}")
    
    # Get security dashboard
    security_data = monitoring_dashboard.get_dashboard_data(
        monitoring_dashboard.DashboardType.SECURITY
    )
    
    print(f"Security Dashboard:")
    print(f"  Widgets: {len(security_data['widgets'])}")
    
    # Get widget list
    print("Available widgets:")
    widgets = monitoring_dashboard.get_widget_list()
    for widget in widgets:
        print(f"  - {widget['id']}: {widget['title']} ({widget['type']})")
    
    # Stop dashboard
    monitoring_dashboard.stop_dashboard()


def example_incident_runbook():
    """Example of incident runbook functionality."""
    print("\n" + "=" * 60)
    print("PHASE 6 INCIDENT RUNBOOK EXAMPLE")
    print("=" * 60)
    
    # Create sample incidents
    print("Creating sample incidents...")
    
    incident1_id = incident_runbook.create_incident(
        title="High Error Rate Detected",
        description="Error rate exceeded 5% threshold",
        severity=incident_runbook.IncidentSeverity.HIGH,
        affected_services=["API Server", "Groq Provider"],
        impact="Users experiencing failed recommendations",
        tags=["performance", "api"]
    )
    
    incident2_id = incident_runbook.create_incident(
        title="Service Unavailable",
        description="API server not responding to health checks",
        severity=incident_runbook.IncidentSeverity.CRITICAL,
        affected_services=["API Server"],
        impact="Complete service outage",
        tags=["outage", "critical"]
    )
    
    print(f"Created incidents: {incident1_id}, {incident2_id}")
    
    # Get active incidents
    print("Active incidents:")
    active_incidents = incident_runbook.get_active_incidents()
    for incident in active_incidents:
        print(f"  - {incident['title']} ({incident['severity']})")
    
    # Get incident summary
    print("Incident summary:")
    summary = incident_runbook.get_incident_summary(hours_back=24)
    print(f"  Total incidents: {summary['total_incidents']}")
    print(f"  Active incidents: {summary['active_incidents']}")
    print(f"  MTTR: {summary['mttr_minutes']:.1f} minutes")
    
    # Get recovery procedures
    print("Available recovery procedures:")
    procedures = incident_runbook.get_procedure_list()
    for procedure in procedures:
        print(f"  - {procedure['name']} ({procedure['severity']})")
    
    # Execute recovery procedure (simulation)
    print("Executing recovery procedure for high error rate...")
    recovery_result = incident_runbook.execute_recovery_procedure(incident1_id, "high_error_rate")
    
    print(f"Recovery procedure result:")
    print(f"  Success: {recovery_result.get('success', False)}")
    print(f"  Steps executed: {len(recovery_result.get('steps', []))}")
    
    if recovery_result.get('steps'):
        for step in recovery_result['steps'][:3]:  # Show first 3 steps
            print(f"    Step {step['step']}: {step['action']} - {'Success' if step['success'] else 'Failed'}")
    
    # Update incident status
    print("Updating incident status...")
    incident_runbook.update_incident_status(
        incident1_id,
        incident_runbook.IncidentStatus.RESOLVED,
        root_cause="High load on Groq API",
        resolution="Implemented rate limiting and cache optimization"
    )
    
    # Test recovery procedures
    print("Testing recovery procedures...")
    
    # Test system health check
    health_results = recovery_procedures.check_system_health()
    print(f"System health check:")
    for service, healthy in health_results.items():
        print(f"  {service}: {'Healthy' if healthy else 'Unhealthy'}")
    
    # Test system metrics
    print("System metrics:")
    metrics = recovery_procedures.get_system_metrics()
    for key, value in metrics.items():
        if isinstance(value, (int, float)):
            print(f"  {key}: {value}")


def example_production_monitoring():
    """Example of complete production monitoring setup."""
    print("\n" + "=" * 60)
    print("PHASE 6 PRODUCTION MONITORING SETUP")
    print("=" * 60)
    
    # Initialize all monitoring components
    print("Initializing production monitoring...")
    
    # Start monitoring
    monitoring_dashboard.start_dashboard()
    
    # Simulate production traffic
    print("Simulating production traffic...")
    
    for i in range(10):
        # Simulate API requests
        monitoring_system.increment_counter("total_requests", 1)
        monitoring_system.record_histogram("response_time", 0.5 + (i % 3) * 0.2)
        
        # Simulate occasional errors
        if i % 7 == 0:
            monitoring_system.increment_counter("error_requests", 1)
            logging_manager.error(f"Request failed - Error code: 500",
                                module="api",
                                function="handle_request")
        
        # Simulate user activity
        if i % 3 == 0:
            monitoring_system.set_gauge("active_users", 20 + i)
        
        time.sleep(0.1)  # Small delay between requests
    
    # Get comprehensive monitoring data
    print("Collecting monitoring data...")
    
    # System health
    health = monitoring_system.get_system_health()
    print(f"System Health: {health['status']}")
    
    # Dashboard data
    dashboard_data = monitoring_dashboard.get_dashboard_data(
        monitoring_dashboard.DashboardType.OVERVIEW
    )
    
    print(f"Dashboard widgets: {len(dashboard_data['widgets'])}")
    
    # Security status
    security_events = security_middleware.get_security_events(hours_back=1)
    print(f"Security events: {len(security_events)}")
    
    # Cache performance
    cache_stats = cache_manager.get_stats()
    total_cache_size = sum(stats.get('total_size_bytes', 0) for stats in cache_stats.values())
    print(f"Cache total size: {total_cache_size} bytes")
    
    # Stop monitoring
    monitoring_dashboard.stop_dashboard()
    
    print("Production monitoring example completed")


def main():
    """Main function to run Phase 6 examples."""
    parser = argparse.ArgumentParser(
        description="Phase 6 Production Readiness and Observability Examples",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m phase6.main logging       # Run logging and monitoring
  python -m phase6.main caching        # Run caching layer
  python -m phase6.main security       # Run security middleware
  python -m phase6.main deployment     # Run deployment pipeline
  python -m phase6.main dashboard      # Run monitoring dashboard
  python -m phase6.main incidents      # Run incident runbook
  python -m phase6.main production     # Run production monitoring
  python -m phase6.main all            # Run all examples
        """
    )
    
    parser.add_argument(
        "command",
        choices=["logging", "caching", "security", "deployment", "dashboard", "incidents", "production", "all"],
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
    
    print("PHASE 6 PRODUCTION READINESS AND OBSERVABILITY EXAMPLES")
    print("=" * 60)
    
    # Run requested example
    if args.command == "logging":
        example_logging_monitoring()
    elif args.command == "caching":
        example_caching_layer()
    elif args.command == "security":
        example_security_middleware()
    elif args.command == "deployment":
        example_deployment_pipeline()
    elif args.command == "dashboard":
        example_monitoring_dashboard()
    elif args.command == "incidents":
        example_incident_runbook()
    elif args.command == "production":
        example_production_monitoring()
    elif args.command == "all":
        example_logging_monitoring()
        example_caching_layer()
        example_security_middleware()
        example_deployment_pipeline()
        example_monitoring_dashboard()
        example_incident_runbook()
        example_production_monitoring()
    
    print("\n" + "=" * 60)
    print("PHASE 6 EXAMPLES COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
