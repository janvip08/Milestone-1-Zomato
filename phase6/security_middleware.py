"""Security & Reliability Middleware: Rate limiting, input sanitization, and security features."""

from typing import Dict, Any, List, Optional, Callable, Union
import re
import time
import hashlib
import secrets
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import threading
from collections import defaultdict, deque
import json
import ipaddress
from functools import wraps


class SecurityLevel(Enum):
    """Security levels for different operations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatType(Enum):
    """Types of security threats."""
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    MALICIOUS_INPUT = "malicious_input"
    INVALID_AUTH = "invalid_auth"
    SUSPICIOUS_PATTERN = "suspicious_pattern"


@dataclass
class SecurityEvent:
    """Security event for monitoring."""
    event_id: str
    timestamp: datetime
    threat_type: ThreatType
    severity: SecurityLevel
    source_ip: str
    user_id: Optional[str]
    request_path: str
    details: Dict[str, Any]
    blocked: bool
    message: str


class InputSanitizer:
    """Input sanitization and validation."""
    
    def __init__(self):
        """Initialize input sanitizer."""
        # Malicious patterns
        self.sql_injection_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
            r"(\b(OR|AND)\s+['\"][^'\"]*['\"]\s*=\s*['\"][^'\"]*['\"])",
            r"(--|#|\/\*|\*\/)",
            r"(\b(LOAD_FILE|INTO\s+OUTFILE)\b)",
            r"(\b(INFORMATION_SCHEMA|SYS|MASTER|MSDB)\b)"
        ]
        
        self.xss_patterns = [
            r"(<script[^>]*>.*?</script>)",
            r"(javascript:)",
            r"(on\w+\s*=)",
            r"(<iframe[^>]*>)",
            r"(<object[^>]*>)",
            r"(<embed[^>]*>)",
            r"(<link[^>]*>)",
            r"(<meta[^>]*>)",
            r"(<style[^>]*>.*?</style>)",
            r"(<\s*\/?\w+[^>]*>)"
        ]
        
        self.suspicious_patterns = [
            r"(\b(admin|root|superuser)\b)",
            r"(\b(password|passwd|pwd)\b)",
            r"(\b(login|signin|auth)\b)",
            r"(\b(union|select|insert|update|delete|drop)\b)",
            r"(\b(exec|system|shell|cmd)\b)",
            r"(\b(eval|base64|encode|decode)\b)",
            r"(\b(cookie|session|token)\b)",
            r"(\b(http|https|ftp)\s*://)",
            r"(\b(file://|data:)\s*)"
        ]
        
        # Compile patterns for performance
        self.compiled_patterns = {
            'sql_injection': [re.compile(pattern, re.IGNORECASE) for pattern in self.sql_injection_patterns],
            'xss': [re.compile(pattern, re.IGNORECASE) for pattern in self.xss_patterns],
            'suspicious': [re.compile(pattern, re.IGNORECASE) for pattern in self.suspicious_patterns]
        }
    
    def sanitize_text(self, text: str, max_length: int = 1000) -> str:
        """
        Sanitize text input.
        
        Args:
            text: Input text
            max_length: Maximum allowed length
            
        Returns:
            Sanitized text
        """
        if not isinstance(text, str):
            text = str(text)
        
        # Length limit
        if len(text) > max_length:
            text = text[:max_length]
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', '\x00', '\n', '\r', '\t']
        for char in dangerous_chars:
            text = text.replace(char, '')
        
        return text.strip()
    
    def sanitize_html(self, html: str, allowed_tags: Optional[List[str]] = None) -> str:
        """
        Sanitize HTML input.
        
        Args:
            html: HTML input
            allowed_tags: List of allowed HTML tags
            
        Returns:
            Sanitized HTML
        """
        if not isinstance(html, str):
            html = str(html)
        
        # Remove all HTML tags if no allowed tags specified
        if not allowed_tags:
            return re.sub(r'<[^>]+>', '', html)
        
        # Allow specific tags (basic implementation)
        allowed_pattern = '|'.join(allowed_tags)
        pattern = f'</?(?!{allowed_pattern})\\w+[^>]*>'
        return re.sub(pattern, '', html, flags=re.IGNORECASE)
    
    def validate_email(self, email: str) -> bool:
        """
        Validate email format.
        
        Args:
            email: Email address
            
        Returns:
            True if valid
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def validate_phone(self, phone: str) -> bool:
        """
        Validate phone number format.
        
        Args:
            phone: Phone number
            
        Returns:
            True if valid
        """
        # Remove common formatting characters
        clean_phone = re.sub(r'[\s\-\(\)\+]', '', phone)
        
        # Check if it's all digits and reasonable length
        return clean_phone.isdigit() and 10 <= len(clean_phone) <= 15
    
    def validate_numeric_range(self, value: Union[str, int, float], min_val: float, max_val: float) -> bool:
        """
        Validate numeric value is within range.
        
        Args:
            value: Numeric value
            min_val: Minimum value
            max_val: Maximum value
            
        Returns:
            True if valid
        """
        try:
            num_value = float(value)
            return min_val <= num_value <= max_val
        except (ValueError, TypeError):
            return False
    
    def detect_threats(self, input_data: str, input_type: str = "text") -> List[ThreatType]:
        """
        Detect security threats in input.
        
        Args:
            input_data: Input data to analyze
            input_type: Type of input (text, html, etc.)
            
        Returns:
            List of detected threats
        """
        threats = []
        
        if not isinstance(input_data, str):
            input_data = str(input_data)
        
        # Check for SQL injection
        for pattern in self.compiled_patterns['sql_injection']:
            if pattern.search(input_data):
                threats.append(ThreatType.SQL_INJECTION)
                break
        
        # Check for XSS (only for HTML-like inputs)
        if input_type in ["html", "content"] or "<" in input_data:
            for pattern in self.compiled_patterns['xss']:
                if pattern.search(input_data):
                    threats.append(ThreatType.XSS)
                    break
        
        # Check for suspicious patterns
        for pattern in self.compiled_patterns['suspicious']:
            if pattern.search(input_data):
                threats.append(ThreatType.SUSPICIOUS_PATTERN)
                break
        
        return threats
    
    def sanitize_preferences(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize user preferences.
        
        Args:
            preferences: User preferences dictionary
            
        Returns:
            Sanitized preferences
        """
        sanitized = {}
        
        for key, value in preferences.items():
            if key in ["location", "cuisine", "occasion"]:
                # Text fields
                sanitized[key] = self.sanitize_text(str(value), max_length=100)
            elif key in ["min_rating", "max_cost_for_two"]:
                # Numeric fields
                try:
                    sanitized[key] = float(value)
                except (ValueError, TypeError):
                    sanitized[key] = None
            elif key == "additional_requirements":
                # Longer text field
                sanitized[key] = self.sanitize_text(str(value), max_length=500)
            else:
                # Other fields
                sanitized[key] = self.sanitize_text(str(value), max_length=200)
        
        return sanitized


class RateLimiter:
    """Rate limiting with multiple strategies."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize rate limiter.
        
        Args:
            config: Rate limiting configuration
        """
        self.config = config or self._get_default_config()
        self.storage = defaultdict(deque)  # In-memory storage
        self.lock = threading.RLock()
        
        # Rate limits
        self.rate_limits = {
            "global": {
                "requests": 1000,  # requests per window
                "window": 60        # seconds
            },
            "per_ip": {
                "requests": 100,
                "window": 60
            },
            "per_user": {
                "requests": 50,
                "window": 60
            },
            "expensive_operations": {
                "requests": 10,
                "window": 60
            }
        }
        
        # Override with config
        if "rate_limits" in self.config:
            self.rate_limits.update(self.config["rate_limits"])
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "storage_backend": "memory",  # memory, redis, etc.
            "cleanup_interval": 300,  # seconds
            "block_duration": 300,     # seconds
            "max_storage_size": 10000
        }
    
    def _get_key(self, identifier: str, limit_type: str) -> str:
        """Get storage key for rate limiting."""
        return f"{limit_type}:{identifier}"
    
    def _cleanup_expired(self, limit_type: str, identifier: str, window: int) -> None:
        """Clean up expired entries."""
        key = self._get_key(identifier, limit_type)
        current_time = time.time()
        
        with self.lock:
            timestamps = self.storage[key]
            # Remove entries outside the window
            while timestamps and timestamps[0] < current_time - window:
                timestamps.popleft()
    
    def is_allowed(
        self,
        identifier: str,
        limit_type: str = "per_ip",
        operation: Optional[str] = None
    ) -> tuple[bool, Dict[str, Any]]:
        """
        Check if request is allowed based on rate limits.
        
        Args:
            identifier: Unique identifier (IP, user ID, etc.)
            limit_type: Type of rate limit
            operation: Specific operation type
            
        Returns:
            Tuple of (allowed, info)
        """
        if limit_type not in self.rate_limits:
            return True, {"message": "No rate limit configured"}
        
        rate_config = self.rate_limits[limit_type]
        max_requests = rate_config["requests"]
        window = rate_config["window"]
        
        # Clean up expired entries
        self._cleanup_expired(limit_type, identifier, window)
        
        with self.lock:
            key = self._get_key(identifier, limit_type)
            timestamps = self.storage[key]
            
            current_count = len(timestamps)
            
            if current_count >= max_requests:
                return False, {
                    "message": f"Rate limit exceeded: {current_count}/{max_requests}",
                    "limit_type": limit_type,
                    "window": window,
                    "retry_after": int(timestamps[0] + window - time.time())
                }
            
            # Add current request
            timestamps.append(time.time())
            
            return True, {
                "message": "Request allowed",
                "remaining": max_requests - current_count - 1,
                "limit_type": limit_type,
                "window": window
            }
    
    def get_rate_limit_info(self, identifier: str, limit_type: str = "per_ip") -> Dict[str, Any]:
        """
        Get rate limit information.
        
        Args:
            identifier: Unique identifier
            limit_type: Type of rate limit
            
        Returns:
            Rate limit information
        """
        if limit_type not in self.rate_limits:
            return {"message": "No rate limit configured"}
        
        rate_config = self.rate_limits[limit_type]
        max_requests = rate_config["requests"]
        window = rate_config["window"]
        
        self._cleanup_expired(limit_type, identifier, window)
        
        with self.lock:
            key = self._get_key(identifier, limit_type)
            timestamps = self.storage[key]
            
            current_count = len(timestamps)
            oldest_request = timestamps[0] if timestamps else None
            
            return {
                "limit": max_requests,
                "window": window,
                "current": current_count,
                "remaining": max(0, max_requests - current_count),
                "reset_time": oldest_request + window if oldest_request else None,
                "retry_after": max(0, int(oldest_request + window - time.time())) if oldest_request else 0
            }


class SecurityMiddleware:
    """Security middleware for API protection."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize security middleware.
        
        Args:
            config: Security configuration
        """
        self.config = config or self._get_default_config()
        self.sanitizer = InputSanitizer()
        self.rate_limiter = RateLimiter(self.config.get("rate_limiting", {}))
        self.security_events = deque(maxlen=1000)
        self.blocked_ips = set()
        self.blocked_users = set()
        
        # Security settings
        self.max_request_size = self.config.get("max_request_size", 1024 * 1024)  # 1MB
        self.enable_csrf_protection = self.config.get("csrf_protection", True)
        self.enable_ip_whitelist = self.config.get("ip_whitelist", False)
        self.ip_whitelist = set(self.config.get("allowed_ips", []))
        
        # CSRF tokens
        self.csrf_tokens = {}
        self.csrf_token_timeout = 3600  # 1 hour
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default security configuration."""
        return {
            "max_request_size": 1024 * 1024,  # 1MB
            "csrf_protection": True,
            "ip_whitelist": False,
            "allowed_ips": [],
            "rate_limiting": {
                "rate_limits": {
                    "global": {"requests": 1000, "window": 60},
                    "per_ip": {"requests": 100, "window": 60},
                    "per_user": {"requests": 50, "window": 60}
                }
            },
            "input_validation": {
                "max_text_length": 1000,
                "max_html_length": 5000,
                "allowed_html_tags": ["p", "br", "strong", "em", "ul", "ol", "li"]
            }
        }
    
    def generate_csrf_token(self, user_id: Optional[str] = None) -> str:
        """
        Generate CSRF token.
        
        Args:
            user_id: User identifier
            
        Returns:
            CSRF token
        """
        token = secrets.token_urlsafe(32)
        
        if user_id:
            self.csrf_tokens[user_id] = {
                "token": token,
                "timestamp": time.time()
            }
        else:
            # Session-based token
            session_id = secrets.token_hex(16)
            self.csrf_tokens[session_id] = {
                "token": token,
                "timestamp": time.time()
            }
            return f"{session_id}:{token}"
        
        return token
    
    def validate_csrf_token(self, token: str, user_id: Optional[str] = None) -> bool:
        """
        Validate CSRF token.
        
        Args:
            token: CSRF token to validate
            user_id: User identifier
            
        Returns:
            True if valid
        """
        if not self.enable_csrf_protection:
            return True
        
        if not token:
            return False
        
        # Handle session-based tokens
        if user_id is None and ":" in token:
            session_id, actual_token = token.split(":", 1)
            if session_id in self.csrf_tokens:
                token_data = self.csrf_tokens[session_id]
                if token_data["token"] == actual_token:
                    # Check timeout
                    if time.time() - token_data["timestamp"] < self.csrf_token_timeout:
                        return True
                # Remove expired/invalid token
                del self.csrf_tokens[session_id]
            return False
        
        # Handle user-based tokens
        if user_id and user_id in self.csrf_tokens:
            token_data = self.csrf_tokens[user_id]
            if token_data["token"] == token:
                # Check timeout
                if time.time() - token_data["timestamp"] < self.csrf_token_timeout:
                    return True
            # Remove expired/invalid token
            del self.csrf_tokens[user_id]
        
        return False
    
    def validate_ip_address(self, ip: str) -> bool:
        """
        Validate IP address.
        
        Args:
            ip: IP address string
            
        Returns:
            True if valid and allowed
        """
        try:
            # Validate IP format
            ip_obj = ipaddress.ip_address(ip)
            
            # Check whitelist if enabled
            if self.enable_ip_whitelist:
                return str(ip_obj) in self.ip_whitelist
            
            # Check blocked IPs
            return str(ip_obj) not in self.blocked_ips
            
        except ValueError:
            return False
    
    def validate_request_size(self, request_data: Union[str, Dict, bytes]) -> bool:
        """
        Validate request size.
        
        Args:
            request_data: Request data
            
        Returns:
            True if within limits
        """
        if isinstance(request_data, str):
            size = len(request_data.encode('utf-8'))
        elif isinstance(request_data, dict):
            size = len(json.dumps(request_data).encode('utf-8'))
        elif isinstance(request_data, bytes):
            size = len(request_data)
        else:
            size = len(str(request_data).encode('utf-8'))
        
        return size <= self.max_request_size
    
    def check_rate_limits(
        self,
        ip: str,
        user_id: Optional[str] = None,
        operation: Optional[str] = None
    ) -> tuple[bool, List[SecurityEvent]]:
        """
        Check rate limits.
        
        Args:
            ip: Client IP address
            user_id: User identifier
            operation: Operation type
            
        Returns:
            Tuple of (allowed, security events)
        """
        events = []
        
        # Check global rate limit
        allowed, info = self.rate_limiter.is_allowed("global", "global", operation)
        if not allowed:
            events.append(SecurityEvent(
                event_id=f"rate_limit_global_{int(time.time())}",
                timestamp=datetime.now(),
                threat_type=ThreatType.RATE_LIMIT_EXCEEDED,
                severity=SecurityLevel.HIGH,
                source_ip=ip,
                user_id=user_id,
                request_path=operation or "unknown",
                details=info,
                blocked=True,
                message="Global rate limit exceeded"
            ))
        
        # Check IP rate limit
        allowed_ip, info_ip = self.rate_limiter.is_allowed(ip, "per_ip", operation)
        if not allowed_ip:
            events.append(SecurityEvent(
                event_id=f"rate_limit_ip_{int(time.time())}",
                timestamp=datetime.now(),
                threat_type=ThreatType.RATE_LIMIT_EXCEEDED,
                severity=SecurityLevel.MEDIUM,
                source_ip=ip,
                user_id=user_id,
                request_path=operation or "unknown",
                details=info_ip,
                blocked=True,
                message="IP rate limit exceeded"
            ))
        
        # Check user rate limit
        if user_id:
            allowed_user, info_user = self.rate_limiter.is_allowed(user_id, "per_user", operation)
            if not allowed_user:
                events.append(SecurityEvent(
                    event_id=f"rate_limit_user_{int(time.time())}",
                    timestamp=datetime.now(),
                    threat_type=ThreatType.RATE_LIMIT_EXCEEDED,
                    severity=SecurityLevel.MEDIUM,
                    source_ip=ip,
                    user_id=user_id,
                    request_path=operation or "unknown",
                    details=info_user,
                    blocked=True,
                    message="User rate limit exceeded"
                ))
        
        # Check expensive operations
        if operation in ["recommend", "llm_generate", "batch_process"]:
            allowed_expensive, info_expensive = self.rate_limiter.is_allowed(
                f"{ip}:{user_id or 'anonymous'}", "expensive_operations", operation
            )
            if not allowed_expensive:
                events.append(SecurityEvent(
                    event_id=f"rate_limit_expensive_{int(time.time())}",
                    timestamp=datetime.now(),
                    threat_type=ThreatType.RATE_LIMIT_EXCEEDED,
                    severity=SecurityLevel.HIGH,
                    source_ip=ip,
                    user_id=user_id,
                    request_path=operation,
                    details=info_expensive,
                    blocked=True,
                    message="Expensive operation rate limit exceeded"
                ))
        
        # Store events
        for event in events:
            self.security_events.append(event)
        
        return len(events) == 0, events
    
    def validate_input(
        self,
        input_data: Dict[str, Any],
        input_type: str = "preferences"
    ) -> tuple[bool, List[SecurityEvent]]:
        """
        Validate and sanitize input data.
        
        Args:
            input_data: Input data to validate
            input_type: Type of input
            
        Returns:
            Tuple of (valid, security events)
        """
        events = []
        
        # Check request size
        if not self.validate_request_size(input_data):
            events.append(SecurityEvent(
                event_id=f"request_size_{int(time.time())}",
                timestamp=datetime.now(),
                threat_type=ThreatType.MALICIOUS_INPUT,
                severity=SecurityLevel.MEDIUM,
                source_ip="unknown",
                user_id=None,
                request_path=input_type,
                details={"size": len(str(input_data))},
                blocked=True,
                message="Request size exceeded"
            ))
        
        # Detect threats in input
        input_string = json.dumps(input_data) if isinstance(input_data, dict) else str(input_data)
        threats = self.sanitizer.detect_threats(input_string, input_type)
        
        for threat in threats:
            severity = SecurityLevel.HIGH if threat in [ThreatType.SQL_INJECTION, ThreatType.XSS] else SecurityLevel.MEDIUM
            
            events.append(SecurityEvent(
                event_id=f"threat_{threat.value}_{int(time.time())}",
                timestamp=datetime.now(),
                threat_type=threat,
                severity=severity,
                source_ip="unknown",
                user_id=None,
                request_path=input_type,
                details={"threat_type": threat.value},
                blocked=severity == SecurityLevel.HIGH,
                message=f"Threat detected: {threat.value}"
            ))
        
        # Store events
        for event in events:
            self.security_events.append(event)
        
        return len(events) == 0, events
    
    def sanitize_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize input data.
        
        Args:
            input_data: Input data to sanitize
            
        Returns:
            Sanitized input data
        """
        if isinstance(input_data, dict):
            return self.sanitizer.sanitize_preferences(input_data)
        elif isinstance(input_data, str):
            return self.sanitizer.sanitize_text(input_data)
        else:
            return input_data
    
    def get_security_headers(self) -> Dict[str, str]:
        """
        Get security headers for HTTP responses.
        
        Returns:
            Security headers
        """
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
    
    def get_security_events(
        self,
        hours_back: int = 24,
        severity: Optional[SecurityLevel] = None,
        threat_type: Optional[ThreatType] = None
    ) -> List[SecurityEvent]:
        """
        Get security events with filtering.
        
        Args:
            hours_back: Filter by time period
            severity: Filter by severity
            threat_type: Filter by threat type
            
        Returns:
            List of security events
        """
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        filtered_events = [
            event for event in self.security_events
            if event.timestamp >= cutoff_time
        ]
        
        if severity:
            filtered_events = [event for event in filtered_events if event.severity == severity]
        
        if threat_type:
            filtered_events = [event for event in filtered_events if event.threat_type == threat_type]
        
        return sorted(filtered_events, key=lambda x: x.timestamp, reverse=True)
    
    def block_ip(self, ip: str, reason: str = "Manual block") -> bool:
        """
        Block an IP address.
        
        Args:
            ip: IP address to block
            reason: Reason for blocking
            
        Returns:
            True if blocked
        """
        try:
            ip_obj = ipaddress.ip_address(ip)
            self.blocked_ips.add(str(ip_obj))
            
            # Log security event
            event = SecurityEvent(
                event_id=f"block_ip_{int(time.time())}",
                timestamp=datetime.now(),
                threat_type=ThreatType.SUSPICIOUS_PATTERN,
                severity=SecurityLevel.HIGH,
                source_ip=ip,
                user_id=None,
                request_path="manual_block",
                details={"reason": reason},
                blocked=True,
                message=f"IP blocked: {reason}"
            )
            self.security_events.append(event)
            
            return True
        except ValueError:
            return False
    
    def unblock_ip(self, ip: str) -> bool:
        """
        Unblock an IP address.
        
        Args:
            ip: IP address to unblock
            
        Returns:
            True if unblocked
        """
        try:
            ip_obj = ipaddress.ip_address(ip)
            self.blocked_ips.discard(str(ip_obj))
            return True
        except ValueError:
            return False


# Decorators for security
def require_csrf_token(func):
    """Decorator to require CSRF token."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # This would be implemented in the actual FastAPI middleware
        return func(*args, **kwargs)
    return wrapper


def rate_limit(limit_type: str = "per_ip"):
    """Decorator for rate limiting."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # This would be implemented in the actual FastAPI middleware
            return func(*args, **kwargs)
        return wrapper
    return decorator


def sanitize_input(input_type: str = "preferences"):
    """Decorator for input sanitization."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # This would be implemented in the actual FastAPI middleware
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Global security middleware instance
security_middleware = SecurityMiddleware()
