# -*- coding: utf-8 -*-
import redis.asyncio as redis
import pytest

async def test_redis():
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
