"""
Rate Limiting Middleware for Production Security
QuantaEnergi Production Readiness
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Dict, Optional, Any
import time
import hashlib
import asyncio
from datetime import datetime, timedelta
import logging
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RateLimiter:
    """Advanced rate limiting service with multiple strategies"""
    
    def __init__(self):
        # In production, use Redis for distributed rate limiting
        # Fallback to in-memory store if Redis unavailable
        self.rate_limit_store: Dict[str, Dict[str, Any]] = {}
        self.redis_available = False
        self.blocked_ips: Dict[str, datetime] = {}
        
        # Rate limiting configurations
        self.configs = {
            'default': {
                'requests_per_minute': 100,
                'requests_per_hour': 1000,
                'requests_per_day': 10000,
                'burst_limit': 20,
                'window_size': 60,  # seconds
            },
            'auth': {
                'requests_per_minute': 10,
                'requests_per_hour': 50,
                'requests_per_day': 200,
                'burst_limit': 5,
                'window_size': 60,
            },
            'trading': {
                'requests_per_minute': 200,
                'requests_per_hour': 2000,
                'requests_per_day': 20000,
                'burst_limit': 50,
                'window_size': 60,
            },
            'api': {
                'requests_per_minute': 500,
                'requests_per_hour': 5000,
                'requests_per_day': 50000,
                'burst_limit': 100,
                'window_size': 60,
            }
        }
    
    def get_client_id(self, request: Request) -> str:
        """Get unique client identifier"""
        # Try to get real IP from headers (for load balancers)
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            client_ip = forwarded_for.split(',')[0].strip()
        else:
            client_ip = request.client.host if request.client else 'unknown'
        
        # Include user agent for additional uniqueness
        user_agent = request.headers.get('User-Agent', 'unknown')
        
        # Create hash for privacy
        client_string = f"{client_ip}:{user_agent}"
        return hashlib.md5(client_string.encode()).hexdigest()
    
    def is_rate_limited(
        self, 
        client_id: str, 
        endpoint_type: str = 'default',
        custom_limits: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """Check if client is rate limited"""
        current_time = time.time()
        config = self.configs.get(endpoint_type, self.configs['default'])
        
        # Apply custom limits if provided
        if custom_limits:
            config = {**config, **custom_limits}
        
        # Check if IP is blocked
        if client_id in self.blocked_ips:
            block_until = self.blocked_ips[client_id]
            if datetime.now() < block_until:
                return {
                    'is_limited': True,
                    'reason': 'ip_blocked',
                    'retry_after': int((block_until - datetime.now()).total_seconds()),
                    'limit_type': 'blocked'
                }
            else:
                # Unblock IP
                del self.blocked_ips[client_id]
        
        # Initialize client data if not exists
        if client_id not in self.rate_limit_store:
            self.rate_limit_store[client_id] = {
                'requests': [],
                'last_cleanup': current_time,
                'violations': 0,
                'first_request': current_time
            }
        
        client_data = self.rate_limit_store[client_id]
        
        # Clean up old requests
        self._cleanup_old_requests(client_data, current_time)
        
        # Add current request
        client_data['requests'].append(current_time)
        
        # Check various rate limits
        violations = []
        
        # Per-minute limit
        minute_requests = [req for req in client_data['requests'] 
                          if current_time - req < 60]
        if len(minute_requests) > config['requests_per_minute']:
            violations.append('per_minute')
        
        # Per-hour limit
        hour_requests = [req for req in client_data['requests'] 
                        if current_time - req < 3600]
        if len(hour_requests) > config['requests_per_hour']:
            violations.append('per_hour')
        
        # Per-day limit
        day_requests = [req for req in client_data['requests'] 
                       if current_time - req < 86400]
        if len(day_requests) > config['requests_per_day']:
            violations.append('per_day')
        
        # Burst limit (requests in last 10 seconds)
        burst_requests = [req for req in client_data['requests'] 
                         if current_time - req < 10]
        if len(burst_requests) > config['burst_limit']:
            violations.append('burst')
        
        if violations:
            client_data['violations'] += 1
            
            # Progressive penalties
            if client_data['violations'] >= 10:
                # Block IP for 1 hour
                self.blocked_ips[client_id] = datetime.now() + timedelta(hours=1)
                return {
                    'is_limited': True,
                    'reason': 'ip_blocked',
                    'retry_after': 3600,
                    'limit_type': 'blocked',
                    'violations': client_data['violations']
                }
            elif client_data['violations'] >= 5:
                # Block for 10 minutes
                return {
                    'is_limited': True,
                    'reason': 'too_many_violations',
                    'retry_after': 600,
                    'limit_type': 'temporary_block',
                    'violations': client_data['violations']
                }
            else:
                # Standard rate limit
                return {
                    'is_limited': True,
                    'reason': 'rate_limit_exceeded',
                    'retry_after': 60,
                    'limit_type': 'rate_limit',
                    'violations': violations,
                    'current_requests': len(client_data['requests'])
                }
        
        # Reset violations if no recent violations
        if current_time - client_data.get('last_violation', 0) > 3600:
            client_data['violations'] = 0
        
        return {
            'is_limited': False,
            'current_requests': len(client_data['requests']),
            'violations': client_data['violations']
        }
    
    def _cleanup_old_requests(self, client_data: Dict[str, Any], current_time: float):
        """Clean up old requests to prevent memory leaks"""
        # Keep only requests from last 24 hours
        client_data['requests'] = [
            req for req in client_data['requests'] 
            if current_time - req < 86400
        ]
        client_data['last_cleanup'] = current_time
    
    def get_rate_limit_headers(self, client_id: str, endpoint_type: str = 'default') -> Dict[str, str]:
        """Get rate limit headers for response"""
        config = self.configs.get(endpoint_type, self.configs['default'])
        client_data = self.rate_limit_store.get(client_id, {'requests': []})
        
        current_time = time.time()
        minute_requests = len([req for req in client_data['requests'] 
                              if current_time - req < 60])
        hour_requests = len([req for req in client_data['requests'] 
                            if current_time - req < 3600])
        
        return {
            'X-RateLimit-Limit-Minute': str(config['requests_per_minute']),
            'X-RateLimit-Remaining-Minute': str(max(0, config['requests_per_minute'] - minute_requests)),
            'X-RateLimit-Limit-Hour': str(config['requests_per_hour']),
            'X-RateLimit-Remaining-Hour': str(max(0, config['requests_per_hour'] - hour_requests)),
            'X-RateLimit-Reset': str(int(current_time + 60)),
            'X-RateLimit-Violations': str(client_data.get('violations', 0))
        }
    
    def reset_client_limits(self, client_id: str):
        """Reset rate limits for a specific client (admin function)"""
        if client_id in self.rate_limit_store:
            del self.rate_limit_store[client_id]
        if client_id in self.blocked_ips:
            del self.blocked_ips[client_id]
    
    def get_rate_limit_stats(self) -> Dict[str, Any]:
        """Get rate limiting statistics"""
        current_time = time.time()
        active_clients = 0
        blocked_clients = len(self.blocked_ips)
        total_requests = 0
        total_violations = 0
        
        for client_data in self.rate_limit_store.values():
            # Count active clients (requests in last hour)
            recent_requests = [req for req in client_data['requests'] 
                              if current_time - req < 3600]
            if recent_requests:
                active_clients += 1
                total_requests += len(recent_requests)
                total_violations += client_data.get('violations', 0)
        
        return {
            'active_clients': active_clients,
            'blocked_clients': blocked_clients,
            'total_requests_last_hour': total_requests,
            'total_violations': total_violations,
            'rate_limit_store_size': len(self.rate_limit_store),
            'blocked_ips_size': len(self.blocked_ips)
        }

# Initialize rate limiter
rate_limiter = RateLimiter()

def rate_limit_middleware(endpoint_type: str = 'default', custom_limits: Optional[Dict[str, int]] = None):
    """Rate limiting middleware decorator"""
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            client_id = rate_limiter.get_client_id(request)
            
            # Check rate limits
            limit_result = rate_limiter.is_rate_limited(client_id, endpoint_type, custom_limits)
            
            if limit_result['is_limited']:
                # Log rate limit violation
                logger.warning(f"Rate limit exceeded for client {client_id}: {limit_result}")
                
                # Return rate limit error
                error_response = {
                    'error': 'Rate limit exceeded',
                    'message': f"Too many requests. {limit_result['reason']}",
                    'retry_after': limit_result['retry_after'],
                    'limit_type': limit_result['limit_type'],
                    'timestamp': datetime.now().isoformat()
                }
                
                if 'violations' in limit_result:
                    error_response['violations'] = limit_result['violations']
                
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content=error_response,
                    headers={
                        'Retry-After': str(limit_result['retry_after']),
                        **rate_limiter.get_rate_limit_headers(client_id, endpoint_type)
                    }
                )
            
            # Add rate limit headers to response
            response = await func(request, *args, **kwargs)
            if hasattr(response, 'headers'):
                response.headers.update(rate_limiter.get_rate_limit_headers(client_id, endpoint_type))
            
            return response
        
        return wrapper
    return decorator

async def rate_limit_middleware_func(request: Request, call_next):
    """FastAPI middleware function for rate limiting"""
    client_id = rate_limiter.get_client_id(request)
    
    # Determine endpoint type based on path
    path = request.url.path
    if path.startswith('/v1/auth'):
        endpoint_type = 'auth'
    elif path.startswith('/v1/trades') or path.startswith('/v1/options'):
        endpoint_type = 'trading'
    elif path.startswith('/v1/'):
        endpoint_type = 'api'
    else:
        endpoint_type = 'default'
    
    # Check rate limits
    limit_result = rate_limiter.is_rate_limited(client_id, endpoint_type)
    
    if limit_result['is_limited']:
        # Log rate limit violation
        logger.warning(f"Rate limit exceeded for client {client_id} on {path}: {limit_result}")
        
        # Return rate limit error
        error_response = {
            'error': 'Rate limit exceeded',
            'message': f"Too many requests. {limit_result['reason']}",
            'retry_after': limit_result['retry_after'],
            'limit_type': limit_result['limit_type'],
            'timestamp': datetime.now().isoformat()
        }
        
        if 'violations' in limit_result:
            error_response['violations'] = limit_result['violations']
        
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content=error_response,
            headers={
                'Retry-After': str(limit_result['retry_after']),
                **rate_limiter.get_rate_limit_headers(client_id, endpoint_type)
            }
        )
    
    # Process request
    response = await call_next(request)
    
    # Add rate limit headers
    response.headers.update(rate_limiter.get_rate_limit_headers(client_id, endpoint_type))
    
    return response

# Rate limit endpoints for monitoring
async def get_rate_limit_stats():
    """Get rate limiting statistics endpoint"""
    return rate_limiter.get_rate_limit_stats()

async def reset_client_limits(client_id: str):
    """Reset rate limits for a specific client (admin endpoint)"""
    rate_limiter.reset_client_limits(client_id)
    return {"message": f"Rate limits reset for client {client_id}"}

async def get_rate_limit_config():
    """Get current rate limiting configuration"""
    return rate_limiter.configs
