"""
Security Middleware for OWASP Compliance
QuantaEnergi Production Readiness
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
import re
import html
import json
import time
import hashlib
import secrets
from datetime import datetime, timedelta
import logging
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityMiddleware:
    """Comprehensive security middleware for OWASP compliance"""
    
    def __init__(self):
        self.blocked_ips: Dict[str, datetime] = {}
        self.suspicious_requests: Dict[str, List[Dict[str, Any]]] = {}
        self.csrf_tokens: Dict[str, str] = {}
        
        # Security configurations
        self.config = {
            'max_request_size': 10 * 1024 * 1024,  # 10MB
            'max_headers_size': 8192,  # 8KB
            'max_query_params': 100,
            'max_post_params': 1000,
            'block_duration_minutes': 60,
            'max_suspicious_requests': 10,
            'csrf_token_expiry_hours': 24,
        }
        
        # OWASP Top 10 patterns
        self.malicious_patterns = {
            'sql_injection': [
                r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
                r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
                r"(\b(OR|AND)\s+'.*'\s*=\s*'.*')",
                r"(\b(OR|AND)\s+\".*\"\s*=\s*\".*\")",
                r"(\b(OR|AND)\s+1\s*=\s*1)",
                r"(\b(OR|AND)\s+true)",
                r"(\b(OR|AND)\s+false)",
                r"(--|\#|\/\*|\*\/)",
                r"(\b(WAITFOR|DELAY)\b)",
                r"(\b(BENCHMARK|SLEEP)\b)",
            ],
            'xss': [
                r"<script[^>]*>.*?</script>",
                r"javascript:",
                r"on\w+\s*=",
                r"<iframe[^>]*>",
                r"<object[^>]*>",
                r"<embed[^>]*>",
                r"<link[^>]*>",
                r"<meta[^>]*>",
                r"<style[^>]*>",
                r"expression\s*\(",
                r"url\s*\(",
                r"@import",
                r"vbscript:",
                r"data:text/html",
                r"data:application/javascript",
            ],
            'path_traversal': [
                r"\.\./",
                r"\.\.\\",
                r"%2e%2e%2f",
                r"%2e%2e%5c",
                r"\.\.%2f",
                r"\.\.%5c",
                r"\.\.%252f",
                r"\.\.%255c",
                r"\.\.%c0%af",
                r"\.\.%c1%9c",
            ],
            'command_injection': [
                r"[;&|`$]",
                r"\b(cat|ls|pwd|whoami|id|uname|ps|netstat|ifconfig)\b",
                r"\b(cmd|command|exec|system|shell_exec|passthru)\b",
                r"\b(powershell|bash|sh|cmd|powershell)\b",
                r"(\||&&|;|\$\(|\`|\$\{)",
            ],
            'ldap_injection': [
                r"[()=*!&|]",
                r"\b(uid|cn|sn|givenName|mail|objectClass)\b",
                r"(\*|\()",
            ],
            'nosql_injection': [
                r"\$where",
                r"\$ne",
                r"\$gt",
                r"\$lt",
                r"\$regex",
                r"\$exists",
                r"\$in",
                r"\$nin",
                r"\$or",
                r"\$and",
                r"\$not",
                r"\$nor",
            ]
        }
        
        # Suspicious user agents
        self.suspicious_user_agents = [
            'sqlmap', 'nikto', 'nmap', 'masscan', 'zap', 'burp',
            'w3af', 'acunetix', 'nessus', 'openvas', 'skipfish',
            'wget', 'curl', 'python-requests', 'scrapy', 'bot',
            'crawler', 'spider', 'scanner', 'exploit', 'hack'
        ]
    
    def get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        return request.client.host if request.client else 'unknown'
    
    def is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is blocked"""
        if ip in self.blocked_ips:
            if datetime.now() < self.blocked_ips[ip]:
                return True
            else:
                del self.blocked_ips[ip]
        return False
    
    def block_ip(self, ip: str, duration_minutes: int = None):
        """Block IP address"""
        duration = duration_minutes or self.config['block_duration_minutes']
        self.blocked_ips[ip] = datetime.now() + timedelta(minutes=duration)
        logger.warning(f"IP {ip} blocked for {duration} minutes")
    
    def detect_malicious_patterns(self, text: str) -> List[str]:
        """Detect malicious patterns in text"""
        detected = []
        text_lower = text.lower()
        
        for category, patterns in self.malicious_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    detected.append(f"{category}: {pattern}")
        
        return detected
    
    def is_suspicious_user_agent(self, user_agent: str) -> bool:
        """Check if user agent is suspicious"""
        user_agent_lower = user_agent.lower()
        return any(suspicious in user_agent_lower for suspicious in self.suspicious_user_agents)
    
    def validate_request_size(self, request: Request) -> bool:
        """Validate request size"""
        content_length = request.headers.get('content-length')
        if content_length:
            try:
                size = int(content_length)
                return size <= self.config['max_request_size']
            except ValueError:
                return False
        return True
    
    def validate_headers(self, request: Request) -> List[str]:
        """Validate request headers"""
        issues = []
        
        # Check header count
        if len(request.headers) > 50:
            issues.append("Too many headers")
        
        # Check for suspicious headers
        suspicious_headers = ['x-forwarded-host', 'x-originating-ip', 'x-remote-ip']
        for header in suspicious_headers:
            if header in request.headers:
                issues.append(f"Suspicious header: {header}")
        
        # Check header values for malicious patterns
        for name, value in request.headers.items():
            if len(value) > self.config['max_headers_size']:
                issues.append(f"Header {name} too large")
            
            malicious = self.detect_malicious_patterns(value)
            if malicious:
                issues.extend([f"Malicious pattern in {name}: {m}" for m in malicious])
        
        return issues
    
    def validate_query_params(self, request: Request) -> List[str]:
        """Validate query parameters"""
        issues = []
        
        # Check parameter count
        if len(request.query_params) > self.config['max_query_params']:
            issues.append("Too many query parameters")
        
        # Check parameter values
        for name, value in request.query_params.items():
            if len(value) > 1000:  # Max parameter value length
                issues.append(f"Query parameter {name} too large")
            
            malicious = self.detect_malicious_patterns(value)
            if malicious:
                issues.extend([f"Malicious pattern in query param {name}: {m}" for m in malicious])
        
        return issues
    
    def sanitize_input(self, text: str) -> str:
        """Sanitize input text"""
        if not text:
            return text
        
        # HTML encode
        text = html.escape(text)
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Remove control characters
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        return text
    
    def generate_csrf_token(self, session_id: str) -> str:
        """Generate CSRF token"""
        token = secrets.token_urlsafe(32)
        self.csrf_tokens[session_id] = token
        return token
    
    def validate_csrf_token(self, session_id: str, token: str) -> bool:
        """Validate CSRF token"""
        if session_id not in self.csrf_tokens:
            return False
        
        stored_token = self.csrf_tokens[session_id]
        if stored_token != token:
            return False
        
        # Check token expiry
        # In production, store expiry time with token
        return True
    
    def add_security_headers(self, response: JSONResponse) -> JSONResponse:
        """Add security headers to response"""
        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
            'X-Permitted-Cross-Domain-Policies': 'none',
            'Cross-Origin-Embedder-Policy': 'require-corp',
            'Cross-Origin-Opener-Policy': 'same-origin',
            'Cross-Origin-Resource-Policy': 'same-origin',
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security event"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'details': details
        }
        logger.warning(f"Security event: {json.dumps(log_entry)}")
    
    def track_suspicious_request(self, ip: str, details: Dict[str, Any]):
        """Track suspicious requests"""
        if ip not in self.suspicious_requests:
            self.suspicious_requests[ip] = []
        
        self.suspicious_requests[ip].append({
            'timestamp': datetime.now(),
            'details': details
        })
        
        # Keep only recent requests
        cutoff = datetime.now() - timedelta(hours=1)
        self.suspicious_requests[ip] = [
            req for req in self.suspicious_requests[ip]
            if req['timestamp'] > cutoff
        ]
        
        # Block IP if too many suspicious requests
        if len(self.suspicious_requests[ip]) >= self.config['max_suspicious_requests']:
            self.block_ip(ip)
            self.log_security_event('ip_blocked', {
                'ip': ip,
                'reason': 'too_many_suspicious_requests',
                'count': len(self.suspicious_requests[ip])
            })

# Initialize security middleware
security_middleware = SecurityMiddleware()

async def security_middleware_func(request: Request, call_next):
    """FastAPI security middleware function"""
    client_ip = security_middleware.get_client_ip(request)
    
    # Check if IP is blocked
    if security_middleware.is_ip_blocked(client_ip):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                'error': 'Access denied',
                'message': 'IP address is blocked',
                'timestamp': datetime.now().isoformat()
            }
        )
    
    # Validate request size
    if not security_middleware.validate_request_size(request):
        security_middleware.track_suspicious_request(client_ip, {
            'reason': 'request_too_large',
            'path': request.url.path
        })
        return JSONResponse(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            content={
                'error': 'Request too large',
                'message': 'Request size exceeds maximum allowed',
                'timestamp': datetime.now().isoformat()
            }
        )
    
    # Validate headers
    header_issues = security_middleware.validate_headers(request)
    if header_issues:
        security_middleware.track_suspicious_request(client_ip, {
            'reason': 'suspicious_headers',
            'issues': header_issues,
            'path': request.url.path
        })
        security_middleware.log_security_event('suspicious_headers', {
            'ip': client_ip,
            'issues': header_issues,
            'path': request.url.path
        })
    
    # Validate query parameters
    query_issues = security_middleware.validate_query_params(request)
    if query_issues:
        security_middleware.track_suspicious_request(client_ip, {
            'reason': 'suspicious_query_params',
            'issues': query_issues,
            'path': request.url.path
        })
        security_middleware.log_security_event('suspicious_query_params', {
            'ip': client_ip,
            'issues': query_issues,
            'path': request.url.path
        })
    
    # Check user agent
    user_agent = request.headers.get('user-agent', '')
    if security_middleware.is_suspicious_user_agent(user_agent):
        security_middleware.track_suspicious_request(client_ip, {
            'reason': 'suspicious_user_agent',
            'user_agent': user_agent,
            'path': request.url.path
        })
        security_middleware.log_security_event('suspicious_user_agent', {
            'ip': client_ip,
            'user_agent': user_agent,
            'path': request.url.path
        })
    
    # Process request
    try:
        response = await call_next(request)
        
        # Add security headers
        if isinstance(response, JSONResponse):
            response = security_middleware.add_security_headers(response)
        
        return response
        
    except Exception as e:
        # Log security-relevant errors
        security_middleware.log_security_event('request_error', {
            'ip': client_ip,
            'path': request.url.path,
            'error': str(e)
        })
        raise

def require_csrf_token(func):
    """Decorator to require CSRF token"""
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        # Skip CSRF for GET requests
        if request.method == 'GET':
            return await func(request, *args, **kwargs)
        
        # Get session ID from headers or cookies
        session_id = request.headers.get('X-Session-ID') or request.cookies.get('session_id')
        csrf_token = request.headers.get('X-CSRF-Token')
        
        if not session_id or not csrf_token:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    'error': 'CSRF token required',
                    'message': 'Missing CSRF token or session ID',
                    'timestamp': datetime.now().isoformat()
                }
            )
        
        if not security_middleware.validate_csrf_token(session_id, csrf_token):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    'error': 'Invalid CSRF token',
                    'message': 'CSRF token validation failed',
                    'timestamp': datetime.now().isoformat()
                }
            )
        
        return await func(request, *args, **kwargs)
    
    return wrapper

def sanitize_input(func):
    """Decorator to sanitize input parameters"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Sanitize string arguments
        for key, value in kwargs.items():
            if isinstance(value, str):
                kwargs[key] = security_middleware.sanitize_input(value)
        
        return await func(*args, **kwargs)
    
    return wrapper

# Security endpoints for monitoring
async def get_security_stats():
    """Get security statistics"""
    return {
        'blocked_ips': len(security_middleware.blocked_ips),
        'suspicious_requests': len(security_middleware.suspicious_requests),
        'active_csrf_tokens': len(security_middleware.csrf_tokens),
        'config': security_middleware.config
    }

async def unblock_ip(ip: str):
    """Unblock IP address (admin endpoint)"""
    if ip in security_middleware.blocked_ips:
        del security_middleware.blocked_ips[ip]
        return {"message": f"IP {ip} unblocked"}
    return {"message": f"IP {ip} was not blocked"}

async def get_blocked_ips():
    """Get list of blocked IPs"""
    return {
        'blocked_ips': [
            {
                'ip': ip,
                'blocked_until': blocked_until.isoformat()
            }
            for ip, blocked_until in security_middleware.blocked_ips.items()
        ]
    }
