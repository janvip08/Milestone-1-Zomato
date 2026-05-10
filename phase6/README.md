# Phase 6: Production Readiness and Observability

Phase 6 implements comprehensive production readiness, monitoring, security, and deployment capabilities to make the restaurant recommendation system stable, secure, and monitorable.

## Overview

Phase 6 provides the essential production infrastructure components:

- **Logging & Monitoring Stack**: Comprehensive logging, metrics collection, and alerting
- **Caching Layer**: Multi-backend caching for performance optimization
- **Security & Reliability Middleware**: Rate limiting, input sanitization, and security features
- **Deployment Pipeline**: CI/CD configuration and environment management
- **Monitoring Dashboard**: Real-time monitoring and visualization
- **Incident Runbook**: Procedures for incident handling and system recovery

## Architecture

### Core Components

#### 1. Logging & Monitoring Stack (`logging_monitoring.py`)

**Features:**
- Structured logging with JSON format
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Metrics collection (counters, gauges, histograms, timers)
- Real-time alerting with configurable thresholds
- Log storage and retrieval
- Performance tracking

**Usage:**
```python
from phase6.logging_monitoring import logging_manager, monitoring_system

# Log events
logging_manager.info("User request received", 
                    user_id="user123", 
                    request_id="req_456")

# Record metrics
monitoring_system.increment_counter("total_requests")
monitoring_system.record_histogram("response_time", 0.85)

# Get system health
health = monitoring_system.get_system_health()
```

#### 2. Caching Layer (`caching_layer.py`)

**Features:**
- Multiple cache backends (Memory, Redis, SQLite)
- LRU eviction policies
- TTL (Time To Live) support
- Cache statistics and monitoring
- Decorators for easy caching
- Automatic cleanup of expired entries

**Cache Backends:**
- **Memory Cache**: Fast in-memory caching with LRU eviction
- **Redis Cache**: Distributed caching for production environments
- **SQLite Cache**: Persistent caching with SQLite backend

**Usage:**
```python
from phase6.caching_layer import cache_manager, cache_recommendations

# Basic caching
cache_manager.set("user:123:preferences", preferences, ttl=3600)
result = cache_manager.get("user:123:preferences")

# Decorator for recommendations
@cache_recommendations(ttl=1800)
def get_recommendations(preferences):
    # Your recommendation logic
    return recommendations
```

#### 3. Security & Reliability Middleware (`security_middleware.py`)

**Features:**
- Input sanitization and validation
- SQL injection and XSS detection
- Rate limiting with multiple strategies
- IP blocking and whitelisting
- CSRF protection
- Security event logging
- Request size validation

**Security Features:**
- **Input Sanitization**: Removes malicious content and validates inputs
- **Rate Limiting**: Prevents abuse with configurable limits
- **Threat Detection**: Identifies SQL injection, XSS, and other threats
- **IP Management**: Block/allow specific IP addresses

**Usage:**
```python
from phase6.security_middleware import security_middleware

# Sanitize input
sanitized_input = security_middleware.sanitize_input(user_input)

# Check rate limits
allowed, info = security_middleware.rate_limiter.is_allowed("192.168.1.1", "per_ip")

# Validate IP
is_valid = security_middleware.validate_ip_address(client_ip)
```

#### 4. Deployment Pipeline (`deployment_pipeline.py`)

**Features:**
- Multi-environment support (Development, Staging, Production)
- Environment configuration management
- Deployment automation
- Health checks and smoke tests
- Rollback capabilities
- Git integration
- Environment validation

**Environments:**
- **Development**: Debug enabled, local services
- **Staging**: Production-like configuration for testing
- **Production**: Optimized for production deployment
- **Testing**: Isolated testing environment

**Usage:**
```python
from phase6.deployment_pipeline import deployment_pipeline, Environment

# Create deployment config
config = deployment_pipeline.create_deployment_config(
    environment=Environment.PRODUCTION,
    version="v1.2.3"
)

# Execute deployment
result = deployment_pipeline.execute_deployment(config)

# Validate environment
is_valid, errors = deployment_pipeline.validate_environment(Environment.PRODUCTION)
```

#### 5. Monitoring Dashboard (`monitoring_dashboard.py`)

**Features:**
- Real-time dashboard widgets
- Multiple dashboard types (Overview, Performance, Security)
- Configurable widget layouts
- Auto-refresh capabilities
- Data export functionality
- Custom widget creation

**Dashboard Types:**
- **Overview**: System health, key metrics, recent alerts
- **Performance**: Response times, throughput, cache performance
- **Security**: Security events, threat analysis, rate limits

**Usage:**
```python
from phase6.monitoring_dashboard import monitoring_dashboard, DashboardType

# Start dashboard
monitoring_dashboard.start_dashboard()

# Get dashboard data
overview_data = monitoring_dashboard.get_dashboard_data(DashboardType.OVERVIEW)

# Create custom widget
monitoring_dashboard.create_custom_widget(
    widget_id="custom_metric",
    title="Custom Metric",
    widget_type="metric",
    data_source="custom_data_source",
    position={"x": 0, "y": 0, "width": 4, "height": 2}
)
```

#### 6. Incident Runbook (`incident_runbook.py`)

**Features:**
- Incident creation and management
- Predefined recovery procedures
- Automated recovery actions
- Incident tracking and reporting
- MTTR (Mean Time To Resolution) calculation
- Custom procedure creation

**Recovery Procedures:**
- **High Error Rate**: Automatic service restart and cache clearing
- **Slow Response Time**: Resource optimization and cache cleanup
- **Service Unavailable**: Service restart and health verification
- **Security Breach**: IP blocking and security hardening
- **Cache Failure**: Cache cleanup and backend restart

**Usage:**
```python
from phase6.incident_runbook import incident_runbook, recovery_procedures

# Create incident
incident_id = incident_runbook.create_incident(
    title="High Error Rate",
    description="Error rate exceeded threshold",
    severity=incident_runbook.IncidentSeverity.HIGH,
    affected_services=["API Server"]
)

# Execute recovery procedure
result = incident_runbook.execute_recovery_procedure(incident_id, "high_error_rate")

# Check system health
health_status = recovery_procedures.check_system_health()
```

## Installation and Setup

### Dependencies

```bash
pip install psutil requests redis sqlite3
```

### Environment Configuration

Create environment-specific `.env` files:

```bash
# Development (.env.development)
ENVIRONMENT=development
LOG_LEVEL=DEBUG
CACHE_BACKEND=memory
RATE_LIMITING_ENABLED=false

# Production (.env.production)
ENVIRONMENT=production
LOG_LEVEL=WARNING
CACHE_BACKEND=redis
REDIS_HOST=localhost
REDIS_PORT=6379
RATE_LIMITING_ENABLED=true
```

### Quick Start

```python
from phase6 import (
    logging_manager, monitoring_system,
    cache_manager, security_middleware,
    deployment_pipeline, monitoring_dashboard,
    incident_runbook
)

# Initialize all components
monitoring_dashboard.start_dashboard()

# Use in your application
logging_manager.info("Application started")
cache_manager.set("key", "value")
security_middleware.validate_ip_address(client_ip)
```

## Usage Examples

### 1. Basic Monitoring Setup

```python
from phase6.logging_monitoring import logging_manager, monitoring_system

# Setup logging
logging_manager.info("Service starting", module="main")

# Track metrics
monitoring_system.increment_counter("requests")
monitoring_system.record_histogram("response_time", 0.85)

# Check system health
health = monitoring_system.get_system_health()
```

### 2. Caching Implementation

```python
from phase6.caching_layer import cache_manager, cache_recommendations

# Cache recommendations
@cache_recommendations(ttl=1800)  # 30 minutes
def get_recommendations(preferences):
    # Expensive recommendation logic
    return recommendations

# Manual caching
cache_manager.set("user:123:data", user_data, ttl=3600)
cached_data = cache_manager.get("user:123:data")
```

### 3. Security Implementation

```python
from phase6.security_middleware import security_middleware

# Sanitize user input
sanitized_prefs = security_middleware.sanitize_input(user_preferences)

# Rate limiting
allowed, info = security_middleware.rate_limiter.is_allowed(client_ip, "per_ip")
if not allowed:
    return {"error": "Rate limit exceeded"}, 429

# Validate request
if not security_middleware.validate_request_size(request_data):
    return {"error": "Request too large"}, 413
```

### 4. Deployment Management

```python
from phase6.deployment_pipeline import deployment_pipeline, Environment

# Deploy to staging
config = deployment_pipeline.create_deployment_config(
    environment=Environment.STAGING,
    version="v1.2.3"
)

result = deployment_pipeline.execute_deployment(config)
if result.status == DeploymentStatus.SUCCESS:
    print("Deployment successful!")
```

### 5. Monitoring Dashboard

```python
from phase6.monitoring_dashboard import monitoring_dashboard, DashboardType

# Start dashboard
monitoring_dashboard.start_dashboard()

# Get overview data
overview = monitoring_dashboard.get_dashboard_data(DashboardType.OVERVIEW)
print(f"System status: {overview['widgets'][0]['data']['status']}")
```

### 6. Incident Management

```python
from phase6.incident_runbook import incident_runbook

# Create incident for high error rate
incident_id = incident_runbook.create_incident(
    title="High Error Rate Detected",
    description="Error rate exceeded 5% threshold",
    severity=incident_runbook.IncidentSeverity.HIGH,
    affected_services=["API Server"],
    impact="Users experiencing failed recommendations"
)

# Execute automatic recovery
result = incident_runbook.execute_recovery_procedure(incident_id)
```

## Configuration

### Logging Configuration

```python
logging_config = {
    "level": "INFO",
    "format": "json",
    "log_to_file": True,
    "log_file_path": "logs/application.log",
    "max_log_entries": 10000,
    "structured_logging": True
}
```

### Caching Configuration

```python
cache_config = {
    "default_backend": "memory",
    "backends": {
        "memory": {
            "type": "memory",
            "max_size": 1000,
            "default_ttl": 3600
        },
        "redis": {
            "type": "redis",
            "host": "localhost",
            "port": 6379,
            "default_ttl": 3600
        }
    }
}
```

### Security Configuration

```python
security_config = {
    "max_request_size": 1024 * 1024,  # 1MB
    "csrf_protection": True,
    "rate_limiting": {
        "per_ip": {"requests": 100, "window": 60},
        "per_user": {"requests": 50, "window": 60}
    }
}
```

### Monitoring Configuration

```python
monitoring_config = {
    "refresh_interval": 5,  # seconds
    "alert_thresholds": {
        "error_rate": 0.05,      # 5%
        "response_time_p95": 2000, # 2 seconds
        "success_rate": 0.95      # 95%
    }
}
```

## Running Examples

### Command Line Interface

```bash
# Run individual examples
python -m phase6.main logging       # Logging and monitoring
python -m phase6.main caching        # Caching layer
python -m phase6.main security       # Security middleware
python -m phase6.main deployment     # Deployment pipeline
python -m phase6.main dashboard      # Monitoring dashboard
python -m phase6.main incidents      # Incident runbook
python -m phase6.main production     # Production monitoring

# Run all examples
python -m phase6.main all
```

### Production Deployment

```bash
# Set environment
export ENVIRONMENT=production

# Start monitoring
python -m phase6.main production &

# Deploy application
python -m phase6.deployment_pipeline deploy production
```

## Monitoring and Alerting

### Key Metrics

- **Performance**: Response time, throughput, error rate
- **System**: CPU, memory, disk usage
- **Application**: Active users, cache hit rate, LLM calls
- **Security**: Threat detection, rate limits, blocked IPs

### Alert Thresholds

- **Error Rate**: > 5% triggers alert
- **Response Time**: P95 > 2 seconds triggers alert
- **Success Rate**: < 95% triggers alert
- **Memory Usage**: > 80% triggers alert
- **Cache Hit Rate**: < 70% triggers alert

### Dashboard Widgets

- **System Health**: Overall system status
- **Request Metrics**: Total requests, success rate, error rate
- **Response Times**: Current, P50, P95, P99 times
- **Cache Performance**: Hit rate, size, backend status
- **Security Events**: Recent threats and blocks
- **Incidents**: Active and resolved incidents

## Security Features

### Input Validation

- SQL injection detection
- XSS attack prevention
- Input sanitization
- Request size limits
- Malicious pattern detection

### Rate Limiting

- Per-IP rate limiting
- Per-user rate limiting
- Global rate limiting
- Expensive operation throttling
- Configurable windows and limits

### Threat Protection

- IP blocking and whitelisting
- CSRF token protection
- Security event logging
- Automated threat response
- Security headers

## Deployment Strategies

### Environment Management

- **Development**: Debug mode, local services
- **Staging**: Production-like testing
- **Production**: Optimized configuration
- **Testing**: Isolated environment

### CI/CD Pipeline

1. **Pre-deploy**: Tests, security scans, validation
2. **Deploy**: Build, deploy services, health checks
3. **Post-deploy**: Smoke tests, monitoring updates

### Rollback Procedures

- Automatic rollback on failure
- Manual rollback commands
- Version management
- Health verification

## Incident Response

### Incident Types

- **Critical**: Service outage, security breach
- **High**: High error rate, performance degradation
- **Medium**: Feature failures, cache issues
- **Low**: Minor issues, warnings

### Recovery Procedures

- **Automated**: Service restart, cache clearing
- **Manual**: Investigation, configuration changes
- **Escalation**: Alert notifications, team involvement

### MTTR Tracking

- Incident creation and resolution
- Time to detection and recovery
- Root cause analysis
- Improvement recommendations

## Best Practices

### Logging

- Use structured logging with consistent format
- Include relevant context (user_id, request_id)
- Log at appropriate levels
- Monitor error rates and patterns

### Caching

- Cache frequently accessed data
- Set appropriate TTL values
- Monitor cache hit rates
- Clean up expired entries

### Security

- Validate all user inputs
- Implement rate limiting
- Monitor for threats
- Keep security patches updated

### Monitoring

- Track key performance metrics
- Set appropriate alert thresholds
- Use dashboards for visibility
- Monitor system resources

### Deployment

- Test in staging first
- Use automated deployments
- Implement rollback procedures
- Monitor after deployment

## Troubleshooting

### Common Issues

1. **High Error Rate**
   - Check system health
   - Review recent deployments
   - Restart services
   - Clear cache

2. **Slow Response Time**
   - Check system resources
   - Monitor database performance
   - Clear expired cache
   - Check LLM provider status

3. **Security Incidents**
   - Block malicious IPs
   - Review security events
   - Update security rules
   - Rotate API keys if needed

4. **Cache Issues**
   - Check cache backend status
   - Clear corrupted entries
   - Restart cache service
   - Monitor cache performance

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable detailed logging
from phase6.logging_monitoring import logging_manager
logging_manager.debug("Debug information", extra_data={"debug": True})
```

## Integration with Other Phases

### Phase 4 Integration

- **API Monitoring**: Track API performance and errors
- **Security**: Protect API endpoints
- **Caching**: Cache API responses
- **Logging**: Log API requests and responses

### Phase 5 Integration

- **Evaluation Monitoring**: Track evaluation metrics
- **Feedback Collection**: Monitor feedback rates
- **Quality Metrics**: Track recommendation quality
- **Alerting**: Alert on quality degradation

## Future Enhancements

1. **Advanced Monitoring**
   - Distributed tracing
   - Custom metrics
   - Advanced alerting
   - ML-based anomaly detection

2. **Enhanced Security**
   - Advanced threat detection
   - Behavioral analysis
   - Automated response
   - Security orchestration

3. **Deployment Automation**
   - GitOps integration
   - Canary deployments
   - Blue-green deployments
   - Auto-scaling

4. **Performance Optimization**
   - Advanced caching strategies
   - Database optimization
   - CDN integration
   - Load balancing

## Contributing

When contributing to Phase 6:

1. Follow existing code patterns and structure
2. Add comprehensive tests for new features
3. Update documentation and examples
4. Ensure backward compatibility
5. Add proper error handling and logging
6. Consider security implications
7. Test with different environments

## License

This phase is part of the restaurant recommendation system project.
