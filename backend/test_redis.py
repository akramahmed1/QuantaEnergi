# -*- coding: utf-8 -*-
import pytest
import pytest_asyncio

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

@pytest.mark.asyncio
async def test_redis():
    if not REDIS_AVAILABLE:
        pytest.skip("Redis library not available")
    
    try:
        r = await redis.from_url('redis://localhost:6379')
        await r.set('test', 'hello')
        value = await r.get('test')
        print(value.decode())
        await r.close()
    except redis.ConnectionError:
        pytest.skip("Redis server not available")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_redis())
