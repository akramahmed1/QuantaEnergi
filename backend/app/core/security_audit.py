"""
Security Audit Module for EnergyOpti-Pro
Implements OWASP Top 10 security controls, vulnerability scanning, and security best practices.
"""

import asyncio
import hashlib
import hmac
import json
import logging
import re
import secrets
import structlog
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urlparse
import aiohttp
from fastapi import HTTPException, status, Request
from .config import settings

# Configure structured logging
logger = structlog.get_logger()

class SecurityAuditor:
    """Comprehensive security auditor for OWASP compliance."""
    
    def __init__(self):
        self.vulnerability_db = self._load_vulnerability_patterns()
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }
        self.rate_limit_config = {
            "default": 100,
            "auth": 10,
            "api": 50,
            "admin": 200
        }
    
    def _load_vulnerability_patterns(self) -> Dict[str, List[str]]:
        """Load known vulnerability patterns for scanning."""
        return {
            "sql_injection": [
                r"(\b(union|select|insert|update|delete|drop|create|alter)\b)",
                r"(\b(or|and)\s+\d+\s*=\s*\d+)",
                r"(\b(exec|execute|xp_|sp_)\b)",
                r"(\b(script|javascript|vbscript|onload|onerror)\b)"
            ],
            "xss": [
                r"<script[^>]*>.*?</script>",
                r"javascript:",
                r"on\w+\s*=",
                r"<iframe[^>]*>",
                r"<object[^>]*>",
                r"<embed[^>]*>"
            ],
            "path_traversal": [
                r"\.\./",
                r"\.\.\\",
                r"\.\.%2f",
                r"\.\.%5c",
                r"\.\.%2e%2e%2f"
            ],
            "command_injection": [
                r"(\b(cmd|command|exec|system|eval|os\.|subprocess\.)\b)",
                r"(\b(rm|del|format|shutdown|reboot)\b)",
                r"(\b(&&|\|\||;|`|$\(|\))\b)"
            ],
            "ldap_injection": [
                r"(\b(uid|cn|ou|dc|dn)\s*=\s*[^)]*\*[^)]*)",
                r"(\b(admin|root|user)\s*=\s*[^)]*\*[^)]*)"
            ]
        }
    
    async def audit_request(self, request: Request) -> Dict[str, Any]:
        """Comprehensive security audit of incoming request."""
        audit_result = {
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": secrets.token_urlsafe(16),
            "ip_address": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", ""),
            "endpoint": str(request.url),
            "method": request.method,
            "vulnerabilities": [],
            "risk_score": 0,
            "recommendations": []
        }
        
        try:
            # Check for common attack patterns
            await self._check_sql_injection(request, audit_result)
            await self._check_xss(request, audit_result)
            await self._check_path_traversal(request, audit_result)
            await self._check_command_injection(request, audit_result)
            await self._check_ldap_injection(request, audit_result)
            
            # Check request headers
            self._check_security_headers(request, audit_result)
            
            # Check rate limiting
            await self._check_rate_limiting(request, audit_result)
            
            # Calculate risk score
            audit_result["risk_score"] = self._calculate_risk_score(audit_result)
            
            # Generate recommendations
            audit_result["recommendations"] = self._generate_recommendations(audit_result)
            
            # Log audit result
            if audit_result["vulnerabilities"]:
                logger.warning(f"Security audit found vulnerabilities: {audit_result['vulnerabilities']}")
            else:
                logger.info(f"Security audit passed for request {audit_result['request_id']}")
            
            return audit_result
            
        except Exception as e:
            logger.error(f"Security audit error: {e}")
            audit_result["error"] = str(e)
            return audit_result
    
    async def _check_sql_injection(self, request: Request, audit_result: Dict[str, Any]):
        """Check for SQL injection patterns in request."""
        try:
            # Check query parameters
            query_params = dict(request.query_params)
            for param_name, param_value in query_params.items():
                if self._matches_patterns(param_value, self.vulnerability_db["sql_injection"]):
                    audit_result["vulnerabilities"].append({
                        "type": "sql_injection",
                        "parameter": param_name,
                        "value": param_value,
                        "severity": "high"
                    })
            
            # Check form data if POST/PUT
            if request.method in ["POST", "PUT"]:
                try:
                    body = await request.body()
                    if body:
                        body_str = body.decode('utf-8')
                        if self._matches_patterns(body_str, self.vulnerability_db["sql_injection"]):
                            audit_result["vulnerabilities"].append({
                                "type": "sql_injection",
                                "parameter": "request_body",
                                "value": body_str[:100] + "..." if len(body_str) > 100 else body_str,
                                "severity": "high"
                            })
                except Exception:
                    pass
                    
        except Exception as e:
            logger.error(f"SQL injection check error: {e}")
    
    async def _check_xss(self, request: Request, audit_result: Dict[str, Any]):
        """Check for XSS patterns in request."""
        try:
            query_params = dict(request.query_params)
            for param_name, param_value in query_params.items():
                if self._matches_patterns(param_value, self.vulnerability_db["xss"]):
                    audit_result["vulnerabilities"].append({
                        "type": "xss",
                        "parameter": param_name,
                        "value": param_value,
                        "severity": "high"
                    })
        except Exception as e:
            logger.error(f"XSS check error: {e}")
    
    async def _check_path_traversal(self, request: Request, audit_result: Dict[str, Any]):
        """Check for path traversal attempts."""
        try:
            path = str(request.url.path)
            if self._matches_patterns(path, self.vulnerability_db["path_traversal"]):
                audit_result["vulnerabilities"].append({
                    "type": "path_traversal",
                    "parameter": "url_path",
                    "value": path,
                    "severity": "high"
                })
        except Exception as e:
            logger.error(f"Path traversal check error: {e}")
    
    async def _check_command_injection(self, request: Request, audit_result: Dict[str, Any]):
        """Check for command injection patterns."""
        try:
            query_params = dict(request.query_params)
            for param_name, param_value in query_params.items():
                if self._matches_patterns(param_value, self.vulnerability_db["command_injection"]):
                    audit_result["vulnerabilities"].append({
                        "type": "command_injection",
                        "parameter": param_name,
                        "value": param_value,
                        "severity": "critical"
                    })
        except Exception as e:
            logger.error(f"Command injection check error: {e}")
    
    async def _check_ldap_injection(self, request: Request, audit_result: Dict[str, Any]):
        """Check for LDAP injection patterns."""
        try:
            query_params = dict(request.query_params)
            for param_name, param_value in query_params.items():
                if self._matches_patterns(param_value, self.vulnerability_db["ldap_injection"]):
                    audit_result["vulnerabilities"].append({
                        "type": "ldap_injection",
                        "parameter": param_name,
                        "value": param_value,
                        "severity": "high"
                    })
        except Exception as e:
            logger.error(f"LDAP injection check error: {e}")
    
    def _check_security_headers(self, request: Request, audit_result: Dict[str, Any]):
        """Check if security headers are present and properly configured."""
        missing_headers = []
        for header_name, expected_value in self.security_headers.items():
            if header_name not in request.headers:
                missing_headers.append(header_name)
        
        if missing_headers:
            audit_result["vulnerabilities"].append({
                "type": "missing_security_headers",
                "parameter": "headers",
                "value": missing_headers,
                "severity": "medium"
            })
    
    async def _check_rate_limiting(self, request: Request, audit_result: Dict[str, Any]):
        """Check if request exceeds rate limits."""
        try:
            client_ip = self._get_client_ip(request)
            endpoint = str(request.url.path)
            
            # Determine rate limit based on endpoint
            limit = self.rate_limit_config.get("default", 100)
            if "auth" in endpoint:
                limit = self.rate_limit_config["auth"]
            elif "admin" in endpoint:
                limit = self.rate_limit_config["admin"]
            
            # Check rate limit (simplified - in production use Redis)
            if not await self._is_rate_limit_exceeded(client_ip, endpoint, limit):
                audit_result["vulnerabilities"].append({
                    "type": "rate_limit_exceeded",
                    "parameter": "request_frequency",
                    "value": f"IP: {client_ip}, Endpoint: {endpoint}",
                    "severity": "medium"
                })
                
        except Exception as e:
            logger.error(f"Rate limiting check error: {e}")
    
    def _matches_patterns(self, text: str, patterns: List[str]) -> bool:
        """Check if text matches any of the vulnerability patterns."""
        try:
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return True
            return False
        except Exception:
            return False
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request."""
        try:
            # Check for forwarded headers
            forwarded_for = request.headers.get("x-forwarded-for")
            if forwarded_for:
                return forwarded_for.split(",")[0].strip()
            
            real_ip = request.headers.get("x-real-ip")
            if real_ip:
                return real_ip
            
            return request.client.host if request.client else "unknown"
        except Exception:
            return "unknown"
    
    async def _is_rate_limit_exceeded(self, client_ip: str, endpoint: str, limit: int) -> bool:
        """Check if rate limit is exceeded (simplified implementation)."""
        # In production, implement with Redis for distributed rate limiting
        return False
    
    def _calculate_risk_score(self, audit_result: Dict[str, Any]) -> int:
        """Calculate risk score based on vulnerabilities."""
        score = 0
        severity_weights = {
            "low": 1,
            "medium": 3,
            "high": 7,
            "critical": 10
        }
        
        for vuln in audit_result["vulnerabilities"]:
            score += severity_weights.get(vuln["severity"], 1)
        
        return min(score, 100)  # Cap at 100
    
    def _generate_recommendations(self, audit_result: Dict[str, Any]) -> List[str]:
        """Generate security recommendations based on audit results."""
        recommendations = []
        
        for vuln in audit_result["vulnerabilities"]:
            if vuln["type"] == "sql_injection":
                recommendations.append("Use parameterized queries and input validation")
            elif vuln["type"] == "xss":
                recommendations.append("Implement output encoding and CSP headers")
            elif vuln["type"] == "path_traversal":
                recommendations.append("Validate and sanitize file paths")
            elif vuln["type"] == "command_injection":
                recommendations.append("Avoid shell execution, use safe APIs")
            elif vuln["type"] == "missing_security_headers":
                recommendations.append("Implement all recommended security headers")
            elif vuln["type"] == "rate_limit_exceeded":
                recommendations.append("Implement proper rate limiting")
        
        if not recommendations:
            recommendations.append("No immediate security concerns detected")
        
        return recommendations

class SecurityMiddleware:
    """FastAPI middleware for automatic security auditing."""
    
    def __init__(self, app):
        self.app = app
        self.auditor = SecurityAuditor()
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Create request object for auditing
            request = Request(scope, receive)
            
            # Perform security audit
            audit_result = await self.auditor.audit_request(request)
            
            # Block requests with critical vulnerabilities
            critical_vulns = [v for v in audit_result["vulnerabilities"] if v["severity"] == "critical"]
            if critical_vulns:
                logger.critical(f"Blocking request with critical vulnerabilities: {critical_vulns}")
                # In production, return 403 Forbidden
                # For now, log and continue
            
            # Add audit info to request state
            scope["security_audit"] = audit_result
        
        await self.app(scope, receive, send)

# Initialize security auditor
security_auditor = SecurityAuditor()
