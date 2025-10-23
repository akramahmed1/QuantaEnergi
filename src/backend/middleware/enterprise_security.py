"""
Enterprise Security Middleware
Comprehensive security middleware implementing industry-standard protocols
"""

import time
import hashlib
import secrets
import hmac
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import structlog
from ..core.config import settings

logger = structlog.get_logger()

class EnterpriseSecurityMiddleware(BaseHTTPMiddleware):
    """
    Enterprise-grade security middleware implementing comprehensive security protocols
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        
        # Security configuration
        self.security_headers = {
            "Strict-Transport-Security": f"max-age={settings.HSTS_MAX_AGE}; includeSubDomains; preload",
            "X-Content-Type-Options": settings.X_CONTENT_TYPE_OPTIONS,
            "X-Frame-Options": settings.X_FRAME_OPTIONS,
            "X-XSS-Protection": settings.X_XSS_PROTECTION,
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=(), payment=(), usb=()",
            "Cross-Origin-Embedder-Policy": "require-corp",
            "Cross-Origin-Opener-Policy": "same-origin",
            "Cross-Origin-Resource-Policy": "same-origin",
            "X-Permitted-Cross-Domain-Policies": "none",
            "Cache-Control": "no-store, no-cache, must-revalidate, proxy-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
        
        # Content Security Policy
        if settings.CSP_ENABLED:
            self.security_headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self' wss: ws: https:; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'; "
                "object-src 'none'; "
                "media-src 'self'; "
                "worker-src 'self'"
            )
        
        # Rate limiting storage
        self.rate_limit_store: Dict[str, Dict[str, Any]] = {}
        
        # Security patterns
        self.malicious_patterns = {
            'sql_injection': [
                r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|OR|AND)\b)",
                r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
                r"(\b(OR|AND)\s+'.*'\s*=\s*'.*')",
                r"(\b(OR|AND)\s+\".*\"\s*=\s*\".*\")",
                r"(\b(OR|AND)\s+1\s*=\s*1)",
                r"(--|\#|\/\*|\*\/)",
                r"(\b(WAITFOR|DELAY|BENCHMARK|SLEEP)\b)"
            ],
            'xss': [
                r"<script[^>]*>.*?</script>",
                r"javascript:",
                r"vbscript:",
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
                r"data:text/html",
                r"data:application/javascript"
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
                r"\.\.%c1%9c"
            ],
            'command_injection': [
                r"[;&|`$]",
                r"\b(cat|ls|pwd|whoami|id|uname|ps|netstat|ifconfig|curl|wget)\b",
                r"\b(cmd|command|exec|system|shell_exec|passthru|eval)\b",
                r"\b(powershell|bash|sh|cmd)\b",
                r"(\||&&|;|\$\(|\`|\$\{)"
            ],
            'ldap_injection': [
                r"[()=*!&|]",
                r"(\b(uid|cn|ou|dc|dn)\s*=\s*[^)]*\*[^)]*)",
                r"(\b(admin|root|user)\s*=\s*[^)]*\*[^)]*)"
            ]
        }
        
        # Blocked IPs and user agents
        self.blocked_ips: Dict[str, datetime] = {}
        self.blocked_user_agents = [
            'bot', 'crawler', 'spider', 'scanner', 'nikto', 'sqlmap',
            'nmap', 'masscan', 'burp', 'zap', 'wget', 'curl',
            'python-requests', 'go-http-client', 'java-http-client'
        ]
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request through security middleware"""
        start_time = time.time()
        
        try:
            # Security checks
            await self._perform_security_checks(request)
            
            # Process request
            response = await call_next(request)
            
            # Add security headers
            await self._add_security_headers(response)
            
            # Log security event
            await self._log_security_event(request, response, start_time)
            
            return response
            
        except HTTPException as e:
            # Log security violation
            await self._log_security_violation(request, e)
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail},
                headers=self.security_headers
            )
        except Exception as e:
            logger.error("Security middleware error", error=str(e))
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error"},
                headers=self.security_headers
            )
    
    async def _perform_security_checks(self, request: Request):
        """Perform comprehensive security checks"""
        
        # 1. IP blocking check
        await self._check_ip_blocking(request)
        
        # 2. User agent check
        await self._check_user_agent(request)
        
        # 3. Rate limiting check
        await self._check_rate_limiting(request)
        
        # 4. Input validation check
        await self._check_malicious_input(request)
        
        # 5. HTTPS enforcement
        await self._check_https_enforcement(request)
        
        # 6. Request size check
        await self._check_request_size(request)
        
        # 7. CORS check
        await self._check_cors(request)
    
    async def _check_ip_blocking(self, request: Request):
        """Check if IP is blocked"""
        client_ip = self._get_client_ip(request)
        current_time = datetime.now()
        
        # Check if IP is in blocked list
        if client_ip in self.blocked_ips:
            block_time = self.blocked_ips[client_ip]
            if current_time - block_time < timedelta(hours=1):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="IP address is temporarily blocked"
                )
            else:
                # Remove expired block
                del self.blocked_ips[client_ip]
        
        # Check for private IPs in production
        if settings.COMPLIANCE_MODE == "strict" and self._is_private_ip(client_ip):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Private IP addresses not allowed"
            )
    
    async def _check_user_agent(self, request: Request):
        """Check for suspicious user agents"""
        user_agent = request.headers.get("user-agent", "").lower()
        
        for blocked_ua in self.blocked_user_agents:
            if blocked_ua in user_agent:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Suspicious user agent detected"
                )
        
        # Check for missing user agent
        if not user_agent or user_agent in ["", "-"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User agent header is required"
            )
    
    async def _check_rate_limiting(self, request: Request):
        """Check rate limiting"""
        if not settings.RATE_LIMIT_ENABLED:
            return
        
        client_ip = self._get_client_ip(request)
        current_time = time.time()
        
        # Initialize rate limit data for IP
        if client_ip not in self.rate_limit_store:
            self.rate_limit_store[client_ip] = {
                'requests': [],
                'last_cleanup': current_time
            }
        
        ip_data = self.rate_limit_store[client_ip]
        
        # Clean old requests
        window_start = current_time - 60  # 1 minute window
        ip_data['requests'] = [req_time for req_time in ip_data['requests'] if req_time > window_start]
        
        # Check rate limit
        if len(ip_data['requests']) >= settings.RATE_LIMIT_REQUESTS_PER_MINUTE:
            # Block IP for 1 hour
            self.blocked_ips[client_ip] = datetime.now()
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        # Add current request
        ip_data['requests'].append(current_time)
        
        # Cleanup old data periodically
        if current_time - ip_data['last_cleanup'] > 300:  # 5 minutes
            self._cleanup_rate_limit_data()
            ip_data['last_cleanup'] = current_time
    
    async def _check_malicious_input(self, request: Request):
        """Check for malicious input patterns"""
        import re
        
        # Check URL path
        path = str(request.url.path)
        for pattern_type, patterns in self.malicious_patterns.items():
            for pattern in patterns:
                if re.search(pattern, path, re.IGNORECASE):
                    await self._log_security_violation(request, HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Malicious pattern detected: {pattern_type}"
                    ))
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Malicious input detected"
                    )
        
        # Check query parameters
        for param_name, param_value in request.query_params.items():
            if isinstance(param_value, str):
                for pattern_type, patterns in self.malicious_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, param_value, re.IGNORECASE):
                            await self._log_security_violation(request, HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Malicious query parameter: {param_name}"
                            ))
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Malicious query parameter detected"
                            )
    
    async def _check_https_enforcement(self, request: Request):
        """Enforce HTTPS in production"""
        if settings.TLS_ENABLED and settings.COMPLIANCE_MODE == "strict":
            if request.url.scheme != "https":
                raise HTTPException(
                    status_code=status.HTTP_426_UPGRADE_REQUIRED,
                    detail="HTTPS required"
                )
    
    async def _check_request_size(self, request: Request):
        """Check request size limits"""
        content_length = request.headers.get("content-length")
        if content_length:
            size = int(content_length)
            max_size = 10 * 1024 * 1024  # 10MB
            
            if size > max_size:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="Request too large"
                )
    
    async def _check_cors(self, request: Request):
        """Check CORS policy"""
        origin = request.headers.get("origin")
        if origin and origin not in settings.CORS_ORIGINS:
            if settings.COMPLIANCE_MODE == "strict":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="CORS policy violation"
                )
    
    async def _add_security_headers(self, response: Response):
        """Add comprehensive security headers"""
        for header, value in self.security_headers.items():
            response.headers[header] = value
        
        # Add custom security headers
        response.headers["X-Security-Policy"] = "quantaenergi-enterprise"
        response.headers["X-Request-ID"] = secrets.token_urlsafe(16)
    
    async def _log_security_event(self, request: Request, response: Response, start_time: float):
        """Log security event"""
        if settings.AUDIT_LOGGING_ENABLED:
            event = {
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": response.headers.get("X-Request-ID"),
                "method": request.method,
                "path": str(request.url.path),
                "query_params": str(request.query_params),
                "client_ip": self._get_client_ip(request),
                "user_agent": request.headers.get("user-agent"),
                "status_code": response.status_code,
                "response_time": time.time() - start_time,
                "content_length": response.headers.get("content-length"),
                "referer": request.headers.get("referer"),
                "origin": request.headers.get("origin")
            }
            
            logger.info("Security event", **event)
    
    async def _log_security_violation(self, request: Request, exception: HTTPException):
        """Log security violation"""
        violation = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "security_violation",
            "method": request.method,
            "path": str(request.url.path),
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent"),
            "violation_type": exception.detail,
            "status_code": exception.status_code,
            "headers": dict(request.headers),
            "severity": "high" if exception.status_code >= 400 else "medium"
        }
        
        logger.warning("Security violation detected", **violation)
        
        # In production, this would send to SIEM system
        if settings.COMPLIANCE_MODE == "strict":
            await self._send_to_siem(violation)
    
    async def _send_to_siem(self, violation: Dict[str, Any]):
        """Send security violation to SIEM system"""
        # This would integrate with SIEM systems like Splunk, ELK, etc.
        logger.critical("SIEM alert", violation=violation)
    
    def _get_client_ip(self, request: Request) -> str:
        """Get real client IP address"""
        # Check for forwarded headers
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _is_private_ip(self, ip: str) -> bool:
        """Check if IP is private"""
        import ipaddress
        try:
            ip_obj = ipaddress.ip_address(ip)
            return ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local
        except ValueError:
            return True
    
    def _cleanup_rate_limit_data(self):
        """Cleanup old rate limit data"""
        current_time = time.time()
        cutoff_time = current_time - 3600  # 1 hour
        
        for ip in list(self.rate_limit_store.keys()):
            ip_data = self.rate_limit_store[ip]
            ip_data['requests'] = [req_time for req_time in ip_data['requests'] if req_time > cutoff_time]
            
            # Remove IP if no recent requests
            if not ip_data['requests']:
                del self.rate_limit_store[ip]

# Global security middleware instance
enterprise_security = EnterpriseSecurityMiddleware
