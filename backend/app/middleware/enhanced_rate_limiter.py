"""
Enhanced Rate Limiter with SlowAPI Integration
Provides enterprise-grade rate limiting with multiple strategies
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
import asyncio
import logging
from typing import Dict, Optional, Callable
from collections import defaultdict, deque
from datetime import datetime, timedelta
import redis
import json

logger = logging.getLogger(__name__)

# Redis connection for distributed rate limiting
try:
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
    redis_client.ping()
    REDIS_AVAILABLE = True
except:
    REDIS_AVAILABLE = False
    redis_client = None

# Create SlowAPI limiter
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379" if REDIS_AVAILABLE else "memory://",
    enabled=True
)

class EnhancedRateLimiter:
    """Enhanced rate limiter with multiple strategies and enterprise features"""
    
    def __init__(self):
        self.redis_available = REDIS_AVAILABLE
        self.redis_client = redis_client
        
        # Rate limit configurations
        self.rate_limits = {
            "default": {"requests": 100, "window": 3600},  # 100 requests per hour
            "api": {"requests": 1000, "window": 3600},     # 1k requests per hour
            "auth": {"requests": 10, "window": 300},       # 10 auth attempts per 5 minutes
            "trading": {"requests": 500, "window": 3600},  # 500 trades per hour
            "admin": {"requests": 2000, "window": 3600},   # 2k requests per hour
            "public": {"requests": 50, "window": 3600},    # 50 requests per hour
        }
        
        # User tier configurations
        self.user_tiers = {
            "basic": {"requests": 100, "window": 3600},
            "premium": {"requests": 1000, "window": 3600},
            "enterprise": {"requests": 5000, "window": 3600},
            "admin": {"requests": 10000, "window": 3600},
        }
        
        # In-memory fallback storage
        self.memory_storage = defaultdict(lambda: defaultdict(deque))
        
        # Cleanup task
        self.cleanup_task = None
        self.start_cleanup_task()
    
    def start_cleanup_task(self):
        """Start background cleanup task"""
        try:
            if self.cleanup_task is None or self.cleanup_task.done():
                self.cleanup_task = asyncio.create_task(self._cleanup_expired_entries())
        except RuntimeError:
            # No event loop running, skip cleanup task initialization
            pass
    
    async def _cleanup_expired_entries(self):
        """Clean up expired rate limit entries"""
        while True:
            try:
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                now = time.time()
                
                # Clean up memory storage
                for key in list(self.memory_storage.keys()):
                    for limit_type in list(self.memory_storage[key].keys()):
                        # Remove expired entries
                        while (self.memory_storage[key][limit_type] and 
                               self.memory_storage[key][limit_type][0] < now - 3600):
                            self.memory_storage[key][limit_type].popleft()
                        
                        # Remove empty entries
                        if not self.memory_storage[key][limit_type]:
                            del self.memory_storage[key][limit_type]
                    
                    # Remove empty keys
                    if not self.memory_storage[key]:
                        del self.memory_storage[key]
                        
            except Exception as e:
                logger.error(f"Rate limiter cleanup error: {e}")
                await asyncio.sleep(60)
    
    def get_client_identifier(self, request: Request) -> str:
        """Get unique client identifier"""
        # Try to get user ID from JWT token
        try:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                # In a real implementation, decode JWT to get user ID
                return f"user:{get_remote_address(request)}"
        except:
            pass
        
        # Fallback to IP address
        return get_remote_address(request)
    
    def get_user_tier(self, request: Request) -> str:
        """Get user tier from request"""
        # In a real implementation, get from JWT token or database
        return "basic"  # Default tier
    
    async def check_rate_limit(self, 
                              request: Request, 
                              limit_type: str = "default",
                              custom_limits: Optional[Dict] = None) -> Dict:
        """Check rate limit for request"""
        try:
            client_id = self.get_client_identifier(request)
            user_tier = self.get_user_tier(request)
            
            # Determine limits
            if custom_limits:
                limits = custom_limits
            elif limit_type in self.rate_limits:
                limits = self.rate_limits[limit_type]
            else:
                limits = self.user_tiers.get(user_tier, self.rate_limits["default"])
            
            # Check rate limit
            if self.redis_available:
                result = await self._check_redis_rate_limit(client_id, limit_type, limits)
            else:
                result = await self._check_memory_rate_limit(client_id, limit_type, limits)
            
            return result
            
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            # Allow request on error (fail open)
            return {
                "allowed": True,
                "remaining": 100,
                "reset_time": int(time.time() + 3600),
                "error": str(e)
            }
    
    async def _check_redis_rate_limit(self, 
                                    client_id: str, 
                                    limit_type: str, 
                                    limits: Dict) -> Dict:
        """Check rate limit using Redis"""
        try:
            key = f"rate_limit:{client_id}:{limit_type}"
            now = time.time()
            window_start = now - limits["window"]
            
            # Use Redis pipeline for atomic operations
            pipe = self.redis_client.pipeline()
            
            # Remove expired entries
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Count current requests
            pipe.zcard(key)
            
            # Add current request
            pipe.zadd(key, {str(now): now})
            
            # Set expiration
            pipe.expire(key, limits["window"])
            
            results = pipe.execute()
            current_requests = results[1]
            
            # Check if limit exceeded
            if current_requests >= limits["requests"]:
                # Get oldest request time for reset calculation
                oldest_requests = self.redis_client.zrange(key, 0, 0, withscores=True)
                reset_time = int(oldest_requests[0][1] + limits["window"]) if oldest_requests else int(now + limits["window"])
                
                return {
                    "allowed": False,
                    "remaining": 0,
                    "reset_time": reset_time,
                    "limit": limits["requests"],
                    "window": limits["window"]
                }
            else:
                return {
                    "allowed": True,
                    "remaining": limits["requests"] - current_requests - 1,
                    "reset_time": int(now + limits["window"]),
                    "limit": limits["requests"],
                    "window": limits["window"]
                }
                
        except Exception as e:
            logger.error(f"Redis rate limit error: {e}")
            # Fallback to memory
            return await self._check_memory_rate_limit(client_id, limit_type, limits)
    
    async def _check_memory_rate_limit(self, 
                                     client_id: str, 
                                     limit_type: str, 
                                     limits: Dict) -> Dict:
        """Check rate limit using in-memory storage"""
        try:
            now = time.time()
            window_start = now - limits["window"]
            
            # Get or create client storage
            client_storage = self.memory_storage[client_id]
            
            # Clean expired entries
            while (client_storage[limit_type] and 
                   client_storage[limit_type][0] < window_start):
                client_storage[limit_type].popleft()
            
            # Check current count
            current_requests = len(client_storage[limit_type])
            
            if current_requests >= limits["requests"]:
                # Calculate reset time
                oldest_request = client_storage[limit_type][0] if client_storage[limit_type] else now
                reset_time = int(oldest_request + limits["window"])
                
                return {
                    "allowed": False,
                    "remaining": 0,
                    "reset_time": reset_time,
                    "limit": limits["requests"],
                    "window": limits["window"]
                }
            else:
                # Add current request
                client_storage[limit_type].append(now)
                
                return {
                    "allowed": True,
                    "remaining": limits["requests"] - current_requests - 1,
                    "reset_time": int(now + limits["window"]),
                    "limit": limits["requests"],
                    "window": limits["window"]
                }
                
        except Exception as e:
            logger.error(f"Memory rate limit error: {e}")
            return {
                "allowed": True,
                "remaining": 100,
                "reset_time": int(time.time() + 3600),
                "error": str(e)
            }
    
    def get_rate_limit_headers(self, result: Dict) -> Dict[str, str]:
        """Get rate limit headers for response"""
        return {
            "X-RateLimit-Limit": str(result.get("limit", 100)),
            "X-RateLimit-Remaining": str(result.get("remaining", 100)),
            "X-RateLimit-Reset": str(result.get("reset_time", int(time.time() + 3600))),
            "X-RateLimit-Window": str(result.get("window", 3600))
        }
    
    async def middleware(self, request: Request, call_next):
        """Rate limiting middleware"""
        try:
            # Determine rate limit type based on path
            path = request.url.path
            
            if path.startswith("/api/v1/auth"):
                limit_type = "auth"
            elif path.startswith("/api/v1/trades"):
                limit_type = "trading"
            elif path.startswith("/api/v1/admin"):
                limit_type = "admin"
            elif path.startswith("/api/v1"):
                limit_type = "api"
            else:
                limit_type = "public"
            
            # Check rate limit
            result = await self.check_rate_limit(request, limit_type)
            
            if not result["allowed"]:
                headers = self.get_rate_limit_headers(result)
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "message": f"Too many requests. Limit: {result['limit']} per {result['window']} seconds",
                        "retry_after": result["reset_time"] - int(time.time())
                    },
                    headers=headers
                )
            
            # Process request
            response = await call_next(request)
            
            # Add rate limit headers to response
            headers = self.get_rate_limit_headers(result)
            for header, value in headers.items():
                response.headers[header] = value
            
            return response
            
        except Exception as e:
            logger.error(f"Rate limiting middleware error: {e}")
            # Allow request on error
            return await call_next(request)

# Global rate limiter instance
enhanced_rate_limiter = EnhancedRateLimiter()

# Rate limit decorators
def rate_limit(requests: int, window: int, per: str = "second"):
    """Rate limit decorator"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # This would be implemented in the actual endpoint
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# SlowAPI rate limit decorators
@limiter.limit("100/hour")
def api_rate_limit(request: Request):
    """API rate limit"""
    pass

@limiter.limit("10/5minutes")
def auth_rate_limit(request: Request):
    """Authentication rate limit"""
    pass

@limiter.limit("500/hour")
def trading_rate_limit(request: Request):
    """Trading rate limit"""
    pass

# Export for use in FastAPI app
__all__ = ["limiter", "enhanced_rate_limiter", "rate_limit", "api_rate_limit", "auth_rate_limit", "trading_rate_limit"]
