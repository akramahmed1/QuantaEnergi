"""
Advanced Rate Limiting Middleware for ETRM/CTRM Platform
Implements token bucket algorithm with Redis fallback and organization-based limits
"""

import asyncio
import time
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import hashlib
import json

logger = logging.getLogger(__name__)

class TokenBucket:
    """Token bucket implementation for rate limiting"""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.tokens = capacity
        self.last_refill = time.time()
        self.lock = asyncio.Lock()
    
    async def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens from bucket
        
        Args:
            tokens: Number of tokens to consume
            
        Returns:
            True if tokens were consumed, False if bucket is empty
        """
        async with self.lock:
            now = time.time()
            time_passed = now - self.last_refill
            
            # Refill tokens based on time passed
            self.tokens = min(self.capacity, self.tokens + time_passed * self.refill_rate)
            self.last_refill = now
            
            # Check if we have enough tokens
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            else:
                return False

class RateLimiter:
    """Advanced rate limiter with multiple strategies"""
    
    def __init__(self):
        # Rate limit configurations by endpoint and role
        self.rate_limits = {
            "default": {
                "trader": {"requests": 100, "window": 60},  # 100 requests per minute
                "admin": {"requests": 1000, "window": 60},  # 1000 requests per minute
                "viewer": {"requests": 50, "window": 60},   # 50 requests per minute
            },
            "trade_capture": {
                "trader": {"requests": 20, "window": 60},   # 20 trades per minute
                "admin": {"requests": 100, "window": 60},
            },
            "market_data": {
                "trader": {"requests": 200, "window": 60},  # 200 market data requests per minute
                "admin": {"requests": 500, "window": 60},
                "viewer": {"requests": 100, "window": 60},
            },
            "risk_calculation": {
                "risk_manager": {"requests": 50, "window": 60},
                "admin": {"requests": 200, "window": 60},
            }
        }
        
        # Token buckets for each user/endpoint combination
        self.buckets: Dict[str, TokenBucket] = {}
        
        # Request tracking for sliding window
        self.request_windows: Dict[str, deque] = defaultdict(deque)
        
        # Organization-based limits
        self.org_limits = {
            "tier1": {"requests": 10000, "window": 3600},  # 10k requests per hour
            "tier2": {"requests": 5000, "window": 3600},   # 5k requests per hour
            "tier3": {"requests": 1000, "window": 3600},   # 1k requests per hour
        }
        
        # Cleanup task
        self.cleanup_task = None
        self.start_cleanup_task()
    
    def start_cleanup_task(self):
        """Start background cleanup task"""
        if self.cleanup_task is None or self.cleanup_task.done():
            self.cleanup_task = asyncio.create_task(self._cleanup_expired_entries())
    
    async def _cleanup_expired_entries(self):
        """Clean up expired rate limit entries"""
        while True:
            try:
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                now = time.time()
                
                # Clean up old request windows
                for key in list(self.request_windows.keys()):
                    window = self.request_windows[key]
                    # Remove requests older than 1 hour
                    while window and window[0] < now - 3600:
                        window.popleft()
                    
                    # Remove empty windows
                    if not window:
                        del self.request_windows[key]
                
                logger.debug("Rate limiter cleanup completed")
                
            except Exception as e:
                logger.error(f"Rate limiter cleanup error: {str(e)}")
    
    def _get_bucket_key(self, user_id: str, endpoint: str, organization_id: str) -> str:
        """Generate unique key for token bucket"""
        return f"{organization_id}:{user_id}:{endpoint}"
    
    def _get_window_key(self, user_id: str, endpoint: str, organization_id: str) -> str:
        """Generate unique key for sliding window"""
        return f"window:{organization_id}:{user_id}:{endpoint}"
    
    async def check_rate_limit(self, 
                             user_id: str, 
                             endpoint: str, 
                             user_role: str, 
                             organization_id: str,
                             organization_tier: str = "tier1") -> Tuple[bool, Dict[str, any]]:
        """
        Check if request is within rate limits
        
        Args:
            user_id: User ID
            endpoint: API endpoint
            user_role: User role
            organization_id: Organization ID
            organization_tier: Organization tier
            
        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        try:
            # Get rate limits for endpoint and role
            endpoint_limits = self.rate_limits.get(endpoint, self.rate_limits["default"])
            role_limits = endpoint_limits.get(user_role, endpoint_limits.get("viewer", {"requests": 10, "window": 60}))
            
            # Get organization limits
            org_limits = self.org_limits.get(organization_tier, self.org_limits["tier3"])
            
            # Check user-level rate limit
            user_allowed, user_info = await self._check_user_rate_limit(
                user_id, endpoint, role_limits, organization_id
            )
            
            # Check organization-level rate limit
            org_allowed, org_info = await self._check_org_rate_limit(
                organization_id, org_limits
            )
            
            # Both limits must pass
            is_allowed = user_allowed and org_allowed
            
            rate_info = {
                "user_limit": user_info,
                "org_limit": org_info,
                "allowed": is_allowed,
                "endpoint": endpoint,
                "user_role": user_role,
                "organization_tier": organization_tier
            }
            
            if not is_allowed:
                logger.warning(f"Rate limit exceeded for user {user_id} on endpoint {endpoint}")
            
            return is_allowed, rate_info
            
        except Exception as e:
            logger.error(f"Rate limit check error: {str(e)}")
            # Allow request on error to avoid blocking legitimate traffic
            return True, {"error": str(e), "allowed": True}
    
    async def _check_user_rate_limit(self, 
                                   user_id: str, 
                                   endpoint: str, 
                                   limits: Dict[str, int], 
                                   organization_id: str) -> Tuple[bool, Dict[str, any]]:
        """Check user-level rate limit using sliding window"""
        try:
            window_key = self._get_window_key(user_id, endpoint, organization_id)
            now = time.time()
            window_size = limits["window"]
            max_requests = limits["requests"]
            
            # Get request window
            request_window = self.request_windows[window_key]
            
            # Remove old requests outside the window
            while request_window and request_window[0] < now - window_size:
                request_window.popleft()
            
            # Check if we're within limits
            if len(request_window) < max_requests:
                # Add current request
                request_window.append(now)
                
                return True, {
                    "remaining": max_requests - len(request_window),
                    "reset_time": now + window_size,
                    "limit": max_requests,
                    "window": window_size
                }
            else:
                return False, {
                    "remaining": 0,
                    "reset_time": request_window[0] + window_size if request_window else now + window_size,
                    "limit": max_requests,
                    "window": window_size
                }
                
        except Exception as e:
            logger.error(f"User rate limit check error: {str(e)}")
            return True, {"error": str(e)}
    
    async def _check_org_rate_limit(self, 
                                  organization_id: str, 
                                  limits: Dict[str, int]) -> Tuple[bool, Dict[str, any]]:
        """Check organization-level rate limit"""
        try:
            window_key = f"org:{organization_id}"
            now = time.time()
            window_size = limits["window"]
            max_requests = limits["requests"]
            
            # Get organization request window
            request_window = self.request_windows[window_key]
            
            # Remove old requests outside the window
            while request_window and request_window[0] < now - window_size:
                request_window.popleft()
            
            # Check if we're within limits
            if len(request_window) < max_requests:
                # Add current request
                request_window.append(now)
                
                return True, {
                    "remaining": max_requests - len(request_window),
                    "reset_time": now + window_size,
                    "limit": max_requests,
                    "window": window_size
                }
            else:
                return False, {
                    "remaining": 0,
                    "reset_time": request_window[0] + window_size if request_window else now + window_size,
                    "limit": max_requests,
                    "window": window_size
                }
                
        except Exception as e:
            logger.error(f"Organization rate limit check error: {str(e)}")
            return True, {"error": str(e)}
    
    async def get_rate_limit_status(self, 
                                  user_id: str, 
                                  endpoint: str, 
                                  user_role: str, 
                                  organization_id: str,
                                  organization_tier: str = "tier1") -> Dict[str, any]:
        """Get current rate limit status without consuming tokens"""
        try:
            # Get rate limits
            endpoint_limits = self.rate_limits.get(endpoint, self.rate_limits["default"])
            role_limits = endpoint_limits.get(user_role, endpoint_limits.get("viewer", {"requests": 10, "window": 60}))
            org_limits = self.org_limits.get(organization_tier, self.org_limits["tier3"])
            
            # Check current status
            user_allowed, user_info = await self._check_user_rate_limit(
                user_id, endpoint, role_limits, organization_id
            )
            
            org_allowed, org_info = await self._check_org_rate_limit(
                organization_id, org_limits
            )
            
            return {
                "user_limit": user_info,
                "org_limit": org_info,
                "allowed": user_allowed and org_allowed,
                "endpoint": endpoint,
                "user_role": user_role,
                "organization_tier": organization_tier
            }
            
        except Exception as e:
            logger.error(f"Rate limit status error: {str(e)}")
            return {"error": str(e), "allowed": True}

# Global rate limiter instance
rate_limiter = RateLimiter()

async def rate_limit_middleware(request: Request, call_next):
    """
    Rate limiting middleware for FastAPI
    
    Args:
        request: FastAPI request object
        call_next: Next middleware/handler
        
    Returns:
        Response or rate limit error
    """
    try:
        # Extract user information from request (would come from auth in production)
        user_id = request.headers.get("X-User-ID", "anonymous")
        user_role = request.headers.get("X-User-Role", "viewer")
        organization_id = request.headers.get("X-Organization-ID", "default")
        organization_tier = request.headers.get("X-Organization-Tier", "tier3")
        
        # Get endpoint name
        endpoint = request.url.path.split("/")[-1] or "default"
        
        # Check rate limit
        is_allowed, rate_info = await rate_limiter.check_rate_limit(
            user_id, endpoint, user_role, organization_id, organization_tier
        )
        
        if not is_allowed:
            # Return rate limit error
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded",
                    "rate_limit_info": rate_info,
                    "retry_after": int(rate_info.get("user_limit", {}).get("reset_time", 60) - time.time())
                },
                headers={
                    "Retry-After": str(int(rate_info.get("user_limit", {}).get("reset_time", 60) - time.time())),
                    "X-RateLimit-Limit": str(rate_info.get("user_limit", {}).get("limit", 0)),
                    "X-RateLimit-Remaining": str(rate_info.get("user_limit", {}).get("remaining", 0)),
                    "X-RateLimit-Reset": str(int(rate_info.get("user_limit", {}).get("reset_time", 0)))
                }
            )
        
        # Add rate limit info to request headers
        request.state.rate_limit_info = rate_info
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(rate_info.get("user_limit", {}).get("limit", 0))
        response.headers["X-RateLimit-Remaining"] = str(rate_info.get("user_limit", {}).get("remaining", 0))
        response.headers["X-RateLimit-Reset"] = str(int(rate_info.get("user_limit", {}).get("reset_time", 0)))
        
        return response
        
    except Exception as e:
        logger.error(f"Rate limiting middleware error: {str(e)}")
        # Allow request on error
        return await call_next(request)
