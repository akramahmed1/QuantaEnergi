import redis
from urllib.parse import urlparse
import os
from typing import Optional

class RedisClient:
    _instance = None

    def __init__(self, redis_url: Optional[str] = None):
        if not redis_url:
            redis_url = os.getenv("REDIS_URL", "rediss://:p8ed102d8362feafa2a1def2e439ac84c169a69bca6815e182cf1a3da43130c7d@ec2-34-236-184-217.compute-1.amazonaws.com:29730")
        url = urlparse(redis_url)
        self.client = redis.Redis(
            host=url.hostname,
            port=url.port,
            password=url.password,
            db=0,
            ssl=True,
            ssl_cert_reqs=None,  # To be upgraded in production
            decode_responses=True  # Enable string decoding for convenience
        )
        self._test_connection()

    def _test_connection(self) -> bool:
        try:
            self.client.ping()
            return True
        except redis.ConnectionError as e:
            print(f"Redis connection failed: {e}")
            return False

    @classmethod
    def get_instance(cls) -> 'RedisClient':
        if cls._instance is None:
            cls._instance = RedisClient()
        return cls._instance

    def get_client(self):
        return self.client

    def close(self):
        if self.client:
            self.client.close()
            self._instance = None
