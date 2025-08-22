"""
Redis Caching Service for EnergyOpti-Pro.

Provides high-performance caching with automatic invalidation, TTL management, and connection pooling.
"""

import asyncio
import json
import pickle
import hashlib
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timedelta
import structlog
from functools import wraps
import redis.asyncio as redis
from redis.asyncio import ConnectionPool

logger = structlog.get_logger()

class CacheService:
    """High-performance Redis caching service."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url
        self.pool = None
        self.client = None
        self.default_ttl = 300  # 5 minutes
        self.max_ttl = 86400    # 24 hours
        self.connection_timeout = 5
        self.max_connections = 20
        
        # Cache statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0
        }
    
    async def initialize(self):
        """Initialize Redis connection pool and client."""
        try:
            self.pool = ConnectionPool.from_url(
                self.redis_url,
                max_connections=self.max_connections,
                socket_timeout=self.connection_timeout,
                socket_connect_timeout=self.connection_timeout,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            self.client = redis.Redis(connection_pool=self.pool)
            
            # Test connection
            await self.client.ping()
            logger.info("Redis cache service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis cache: {e}")
            self.client = None
    
    async def close(self):
        """Close Redis connections."""
        if self.client:
            await self.client.close()
        if self.pool:
            await self.pool.disconnect()
        logger.info("Redis cache service closed")
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from prefix and arguments."""
        key_parts = [prefix]
        
        # Add positional arguments
        for arg in args:
            if isinstance(arg, (str, int, float, bool)):
                key_parts.append(str(arg))
            else:
                # Hash complex objects
                key_parts.append(hashlib.md5(pickle.dumps(arg)).hexdigest()[:8])
        
        # Add keyword arguments (sorted for consistency)
        for key, value in sorted(kwargs.items()):
            if isinstance(value, (str, int, float, bool)):
                key_parts.append(f"{key}:{value}")
            else:
                key_parts.append(f"{key}:{hashlib.md5(pickle.dumps(value)).hexdigest()[:8]}")
        
        return ":".join(key_parts)
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache."""
        if not self.client:
            return default
        
        try:
            value = await self.client.get(key)
            if value is not None:
                self.stats["hits"] += 1
                try:
                    # Try to deserialize as JSON first
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    # Fallback to pickle
                    return pickle.loads(value)
            else:
                self.stats["misses"] += 1
                return default
                
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            self.stats["errors"] += 1
            return default
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        nx: bool = False,
        xx: bool = False
    ) -> bool:
        """Set value in cache with TTL."""
        if not self.client:
            return False
        
        try:
            # Serialize value
            if isinstance(value, (dict, list, str, int, float, bool)):
                serialized = json.dumps(value)
            else:
                serialized = pickle.dumps(value)
            
            # Set TTL
            if ttl is None:
                ttl = self.default_ttl
            ttl = min(ttl, self.max_ttl)
            
            # Set in Redis
            result = await self.client.set(
                key,
                serialized,
                ex=ttl,
                nx=nx,
                xx=xx
            )
            
            if result:
                self.stats["sets"] += 1
                logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
            
            return bool(result)
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            self.stats["errors"] += 1
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.client:
            return False
        
        try:
            result = await self.client.delete(key)
            if result:
                self.stats["deletes"] += 1
                logger.debug(f"Cache delete: {key}")
            return bool(result)
            
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            self.stats["errors"] += 1
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """Delete multiple keys matching pattern."""
        if not self.client:
            return 0
        
        try:
            keys = await self.client.keys(pattern)
            if keys:
                result = await self.client.delete(*keys)
                self.stats["deletes"] += len(keys)
                logger.debug(f"Cache delete pattern: {pattern} ({len(keys)} keys)")
                return result
            return 0
            
        except Exception as e:
            logger.error(f"Cache delete pattern error for {pattern}: {e}")
            self.stats["errors"] += 1
            return 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self.client:
            return False
        
        try:
            return bool(await self.client.exists(key))
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Set TTL for existing key."""
        if not self.client:
            return False
        
        try:
            return bool(await self.client.expire(key, ttl))
        except Exception as e:
            logger.error(f"Cache expire error for key {key}: {e}")
            return False
    
    async def ttl(self, key: str) -> int:
        """Get TTL for key."""
        if not self.client:
            return -1
        
        try:
            return await self.client.ttl(key)
        except Exception as e:
            logger.error(f"Cache TTL error for key {key}: {e}")
            return -1
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment counter in cache."""
        if not self.client:
            return None
        
        try:
            return await self.client.incr(key, amount)
        except Exception as e:
            logger.error(f"Cache increment error for key {key}: {e}")
            return None
    
    async def get_or_set(
        self,
        key: str,
        default_func,
        ttl: Optional[int] = None,
        *args,
        **kwargs
    ) -> Any:
        """Get from cache or set default value if not exists."""
        # Try to get from cache
        value = await self.get(key)
        if value is not None:
            return value
        
        # Generate default value
        if asyncio.iscoroutinefunction(default_func):
            default_value = await default_func(*args, **kwargs)
        else:
            default_value = default_func(*args, **kwargs)
        
        # Set in cache
        await self.set(key, default_value, ttl)
        return default_value
    
    async def invalidate_by_prefix(self, prefix: str) -> int:
        """Invalidate all keys with given prefix."""
        return await self.delete_pattern(f"{prefix}:*")
    
    async def invalidate_by_tags(self, tags: List[str]) -> int:
        """Invalidate cache entries by tags."""
        total_deleted = 0
        for tag in tags:
            pattern = f"tag:{tag}:*"
            deleted = await self.delete_pattern(pattern)
            total_deleted += deleted
        return total_deleted
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not self.client:
            return self.stats
        
        try:
            # Get Redis info
            info = await self.client.info()
            
            stats = self.stats.copy()
            stats.update({
                "redis_connected": True,
                "redis_version": info.get("redis_version", "unknown"),
                "used_memory": info.get("used_memory_human", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0)
            })
            
            # Calculate hit rate
            total_requests = stats["hits"] + stats["misses"]
            if total_requests > 0:
                stats["hit_rate"] = stats["hits"] / total_requests
            else:
                stats["hit_rate"] = 0.0
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            stats = self.stats.copy()
            stats["redis_connected"] = False
            return stats
    
    async def clear_stats(self):
        """Clear cache statistics."""
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0
        }
        logger.info("Cache statistics cleared")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on cache service."""
        try:
            if not self.client:
                return {
                    "status": "unhealthy",
                    "error": "Redis client not initialized",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Test basic operations
            test_key = "health_check_test"
            test_value = {"test": True, "timestamp": datetime.now().isoformat()}
            
            # Set test value
            set_success = await self.set(test_key, test_value, ttl=10)
            if not set_success:
                return {
                    "status": "unhealthy",
                    "error": "Failed to set test value",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Get test value
            retrieved_value = await self.get(test_key)
            if retrieved_value != test_value:
                return {
                    "status": "unhealthy",
                    "error": "Failed to retrieve test value",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Delete test value
            await self.delete(test_key)
            
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "stats": await self.get_stats()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

def cache_result(
    ttl: int = 300,
    key_prefix: str = "func",
    include_args: bool = True,
    include_kwargs: bool = True
):
    """Decorator to cache function results."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if include_args and include_kwargs:
                cache_key = f"{key_prefix}:{func.__name__}:{hashlib.md5(pickle.dumps((args, kwargs))).hexdigest()}"
            elif include_args:
                cache_key = f"{key_prefix}:{func.__name__}:{hashlib.md5(pickle.dumps(args)).hexdigest()}"
            elif include_kwargs:
                cache_key = f"{key_prefix}:{func.__name__}:{hashlib.md5(pickle.dumps(kwargs)).hexdigest()}"
            else:
                cache_key = f"{key_prefix}:{func.__name__}"
            
            # Try to get from cache
            cache_service = getattr(wrapper, '_cache_service', None)
            if cache_service:
                cached_result = await cache_service.get(cache_key)
                if cached_result is not None:
                    return cached_result
            
            # Execute function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Cache result
            if cache_service:
                await cache_service.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator

# Global cache service instance
_cache_service: Optional[CacheService] = None

async def get_cache_service() -> CacheService:
    """Get global cache service instance."""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
        await _cache_service.initialize()
    return _cache_service

async def close_cache_service():
    """Close global cache service."""
    global _cache_service
    if _cache_service:
        await _cache_service.close()
        _cache_service = None
