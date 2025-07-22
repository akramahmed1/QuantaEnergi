# -*- coding: utf-8 -*-
import redis.asyncio as redis

async def test_redis():
    r = await redis.from_url('redis://localhost:6379')
    await r.set('test', 'hello')
    value = await r.get('test')
    print(value.decode())

import asyncio
asyncio.run(test_redis())
