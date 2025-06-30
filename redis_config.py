import redis
from urllib.parse import urlparse
import os
from typing import Optional, Dict
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedisClient:
    _instance = None
    _health_report = {}

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
            ssl_cert_reqs=None,
            decode_responses=True
        )
        self._test_connection()
        self._log_grok_insight()

    def _test_connection(self) -> bool:
        try:
            self.client.ping()
            logger.info("Redis connection established successfully")
            return True
        except redis.ConnectionError as e:
            logger.error(f"Redis connection failed: {e}")
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
            logger.info("Redis connection closed")
            self._instance = None

    def diagnose(self) -> Dict:
        return {
            "connection_active": self._test_connection(),
            "memory_usage": self.client.info("memory").get("used_memory_human", "N/A"),
            "uptime": self.client.info("server").get("uptime_in_seconds", "N/A"),
            "last_health_check": self._health_report.get("timestamp", "N/A")
        }

    def _log_grok_insight(self):
        self._health_report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M %Z", time.localtime()),
            "connection_status": self._test_connection(),
            "prediction": "Stable" if self._test_connection() else "Potential Issue"
        }
        logger.info(f"Grok Insight: {self._health_report}")
