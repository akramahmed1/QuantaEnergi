"""
Connection Manager for MQTT and Redis
Handles connection retries and error handling for external services
"""

from fastapi import HTTPException
import asyncio
import logging
from typing import Optional
import time

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages connections to external services with retry logic"""
    
    def __init__(self):
        self.mqtt_client = None
        self.redis_client = None
        self.connection_retries = 3
        self.retry_delay = 2
    
    async def connect_mqtt(self, host: str = "localhost", port: int = 1883, retries: int = 3) -> Optional[object]:
        """
        Connect to MQTT broker with retry logic
        
        Args:
            host: MQTT broker host
            port: MQTT broker port
            retries: Number of retry attempts
            
        Returns:
            MQTT client object or None if connection failed
        """
        try:
            import paho.mqtt.client as mqtt
            
            client = mqtt.Client()
            client.on_connect = self._on_mqtt_connect
            client.on_disconnect = self._on_mqtt_disconnect
            
            for attempt in range(retries):
                try:
                    logger.info(f"Attempting MQTT connection to {host}:{port} (attempt {attempt + 1}/{retries})")
                    client.connect(host, port, 60)
                    client.loop_start()
                    
                    # Wait a bit to ensure connection is established
                    await asyncio.sleep(1)
                    
                    if client.is_connected():
                        logger.info("MQTT connected successfully")
                        self.mqtt_client = client
                        return client
                    else:
                        logger.warning(f"MQTT connection attempt {attempt + 1} failed")
                        
                except Exception as e:
                    logger.warning(f"MQTT attempt {attempt + 1} failed: {str(e)}")
                    if attempt < retries - 1:
                        await asyncio.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
                    
            logger.error("MQTT connection failed after all retries")
            raise HTTPException(status_code=500, detail="MQTT connection failed after retries")
            
        except ImportError:
            logger.error("paho-mqtt not available")
            raise HTTPException(status_code=500, detail="MQTT library not available")
        except Exception as e:
            logger.error(f"MQTT connection error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"MQTT connection error: {str(e)}")
    
    async def connect_redis(self, host: str = "localhost", port: int = 6379, retries: int = 3) -> Optional[object]:
        """
        Connect to Redis server with retry logic
        
        Args:
            host: Redis server host
            port: Redis server port
            retries: Number of retry attempts
            
        Returns:
            Redis client object or None if connection failed
        """
        try:
            import redis.asyncio as redis
            
            for attempt in range(retries):
                try:
                    logger.info(f"Attempting Redis connection to {host}:{port} (attempt {attempt + 1}/{retries})")
                    r = redis.Redis(host=host, port=port, decode_responses=True)
                    
                    # Test connection with ping
                    await r.ping()
                    
                    logger.info("Redis connected successfully")
                    self.redis_client = r
                    return r
                    
                except Exception as e:
                    logger.warning(f"Redis attempt {attempt + 1} failed: {str(e)}")
                    if attempt < retries - 1:
                        await asyncio.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
                    
            logger.error("Redis connection failed after all retries")
            raise HTTPException(status_code=500, detail="Redis connection failed after retries")
            
        except ImportError:
            logger.error("redis not available")
            raise HTTPException(status_code=500, detail="Redis library not available")
        except Exception as e:
            logger.error(f"Redis connection error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Redis connection error: {str(e)}")
    
    def _on_mqtt_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            logger.info("MQTT broker connected")
        else:
            logger.error(f"MQTT connection failed with code {rc}")
    
    def _on_mqtt_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        if rc != 0:
            logger.warning(f"MQTT broker disconnected unexpectedly (code {rc})")
        else:
            logger.info("MQTT broker disconnected")
    
    async def disconnect_mqtt(self):
        """Disconnect from MQTT broker"""
        if self.mqtt_client:
            try:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()
                logger.info("MQTT disconnected")
            except Exception as e:
                logger.error(f"Error disconnecting MQTT: {str(e)}")
            finally:
                self.mqtt_client = None
    
    async def disconnect_redis(self):
        """Disconnect from Redis server"""
        if self.redis_client:
            try:
                await self.redis_client.close()
                logger.info("Redis disconnected")
            except Exception as e:
                logger.error(f"Error disconnecting Redis: {str(e)}")
            finally:
                self.redis_client = None
    
    async def health_check(self) -> dict:
        """Check health of all connections"""
        health_status = {
            "mqtt": {"connected": False, "error": None},
            "redis": {"connected": False, "error": None}
        }
        
        # Check MQTT
        if self.mqtt_client:
            try:
                health_status["mqtt"]["connected"] = self.mqtt_client.is_connected()
            except Exception as e:
                health_status["mqtt"]["error"] = str(e)
        
        # Check Redis
        if self.redis_client:
            try:
                await self.redis_client.ping()
                health_status["redis"]["connected"] = True
            except Exception as e:
                health_status["redis"]["error"] = str(e)
        
        return health_status
    
    async def reconnect_all(self):
        """Reconnect to all services"""
        logger.info("Reconnecting to all services...")
        
        # Disconnect existing connections
        await self.disconnect_mqtt()
        await self.disconnect_redis()
        
        # Reconnect
        try:
            await self.connect_mqtt()
        except Exception as e:
            logger.error(f"Failed to reconnect MQTT: {str(e)}")
        
        try:
            await self.connect_redis()
        except Exception as e:
            logger.error(f"Failed to reconnect Redis: {str(e)}")

# Global connection manager instance
connection_manager = ConnectionManager()