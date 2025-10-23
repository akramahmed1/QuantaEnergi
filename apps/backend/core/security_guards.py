"""
OWASP AI Security Guards
Comprehensive authentication and authorization for AI endpoints
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import structlog

from .jwt_auth import auth_manager

logger = structlog.get_logger()

# Security scheme
security = HTTPBearer()

class OWASPSecurityGuard:
    """OWASP AI Security Guard for comprehensive endpoint protection"""
    
    def __init__(self):
        self.rate_limits = {}  # Simple in-memory rate limiting
        self.blocked_ips = set()  # Blocked IP addresses
        self.suspicious_patterns = [
            r'<script', r'javascript:', r'vbscript:', r'onload=',
            r'onerror=', r'eval\(', r'exec\(', r'import\s+',
            r'__import__', r'getattr', r'setattr', r'delattr',
            r'subprocess', r'os\.system', r'popen', r'shell=True'
        ]
    
    def validate_jwt_token(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
        """
        Validate JWT token with enhanced security checks
        
        Args:
            credentials: HTTP Authorization credentials
            
        Returns:
            Validated user information
            
        Raises:
            HTTPException: If token is invalid or user lacks permissions
        """
        try:
            if not credentials or not credentials.credentials:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing authentication token"
                )
            
            # Validate token format
            token = credentials.credentials
            if not self._validate_token_format(token):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token format"
                )
            
            # Verify token with auth manager
            payload = auth_manager.verify_token(token)
            
            # Additional security checks
            if not self._validate_user_permissions(payload):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions for AI operations"
                )
            
            # Check if user is active
            if not payload.get("is_active", True):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User account is deactivated"
                )
            
            # Log successful authentication
            logger.info("JWT authentication successful", 
                       user_id=payload.get("user_id"),
                       role=payload.get("role"))
            
            return payload
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"JWT validation error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )
    
    def _validate_token_format(self, token: str) -> bool:
        """Validate JWT token format"""
        if not token or not isinstance(token, str):
            return False
        
        # Check for suspicious patterns in token
        for pattern in self.suspicious_patterns:
            if re.search(pattern, token, re.IGNORECASE):
                logger.warning("Suspicious pattern detected in token", pattern=pattern)
                return False
        
        # Basic JWT format check (3 parts separated by dots)
        parts = token.split('.')
        if len(parts) != 3:
            return False
        
        return True
    
    def _validate_user_permissions(self, payload: Dict[str, Any]) -> bool:
        """Validate user has permissions for AI operations"""
        user_role = payload.get("role", "")
        allowed_roles = ["admin", "trader", "analyst", "compliance_officer"]
        
        return user_role in allowed_roles
    
    def check_rate_limit(self, request: Request, user_id: str) -> bool:
        """
        Check rate limiting for AI endpoints
        
        Args:
            request: FastAPI request object
            user_id: User identifier
            
        Returns:
            True if request is allowed, False if rate limited
        """
        current_time = datetime.now()
        client_ip = self._get_client_ip(request)
        
        # Check if IP is blocked
        if client_ip in self.blocked_ips:
            logger.warning("Blocked IP attempted access", ip=client_ip)
            return False
        
        # Simple rate limiting (requests per minute)
        rate_key = f"{user_id}:{client_ip}"
        
        if rate_key not in self.rate_limits:
            self.rate_limits[rate_key] = {
                "count": 1,
                "window_start": current_time
            }
            return True
        
        rate_data = self.rate_limits[rate_key]
        
        # Reset window if minute has passed
        if current_time - rate_data["window_start"] > timedelta(minutes=1):
            rate_data["count"] = 1
            rate_data["window_start"] = current_time
            return True
        
        # Check if rate limit exceeded
        max_requests = 60  # 60 requests per minute
        if rate_data["count"] >= max_requests:
            logger.warning("Rate limit exceeded", user_id=user_id, ip=client_ip)
            return False
        
        rate_data["count"] += 1
        return True
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request"""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct connection IP
        return request.client.host if request.client else "unknown"
    
    def validate_ai_input(self, input_data: Any, max_length: int = 1000) -> Any:
        """
        Validate AI input data to prevent injection attacks
        
        Args:
            input_data: Input data to validate
            max_length: Maximum length for string inputs
            
        Returns:
            Validated input data
            
        Raises:
            HTTPException: If input contains malicious patterns
        """
        if isinstance(input_data, str):
            # Check length
            if len(input_data) > max_length:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Input too long - maximum {max_length} characters"
                )
            
            # Check for suspicious patterns
            for pattern in self.suspicious_patterns:
                if re.search(pattern, input_data, re.IGNORECASE):
                    logger.warning("Suspicious pattern detected in input", 
                                 pattern=pattern, input=input_data[:100])
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid input pattern detected"
                    )
            
            return input_data
        
        elif isinstance(input_data, dict):
            # Recursively validate dictionary
            validated_dict = {}
            for key, value in input_data.items():
                validated_key = self.validate_ai_input(key, 100)
                validated_value = self.validate_ai_input(value, max_length)
                validated_dict[validated_key] = validated_value
            return validated_dict
        
        elif isinstance(input_data, list):
            # Validate list elements
            validated_list = []
            for item in input_data:
                validated_item = self.validate_ai_input(item, max_length)
                validated_list.append(validated_item)
            return validated_list
        
        return input_data


# Global security guard instance
security_guard = OWASPSecurityGuard()

# Dependency functions for FastAPI
async def get_authenticated_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get authenticated user with comprehensive security validation"""
    return security_guard.validate_jwt_token(credentials)

async def get_ai_authenticated_user(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get authenticated user specifically for AI endpoints with rate limiting"""
    user_data = security_guard.validate_jwt_token(credentials)
    
    # Check rate limiting
    if not security_guard.check_rate_limit(request, user_data.get("user_id")):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded for AI operations"
        )
    
    return user_data

def require_ai_permissions(user_data: Dict[str, Any] = Depends(get_ai_authenticated_user)) -> Dict[str, Any]:
    """Require specific AI permissions"""
    user_role = user_data.get("role", "")
    
    # AI-specific roles
    ai_roles = ["admin", "analyst", "trader"]
    if user_role not in ai_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions for AI operations"
        )
    
    return user_data

def validate_ai_input_data(max_length: int = 1000):
    """Decorator for AI input validation"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Find input data in kwargs
            for key, value in kwargs.items():
                if key in ['request', 'data', 'input_data', 'payload']:
                    kwargs[key] = security_guard.validate_ai_input(value, max_length)
            return await func(*args, **kwargs)
        return wrapper
    return decorator
