from fastapi import FastAPI
from starlette.requests import Request
from redis_config import RedisClient
import os

app = FastAPI()

# Initialize Redis client with GTS
redis_client_instance = RedisClient.get_instance()
redis_client = redis_client_instance.get_client()

def rate_limit_check(ip: str) -> bool:
    if redis_client:
        key = f"rate_limit:{ip}"
        count = redis_client.get(key)
        if count is None:
            redis_client.setex(key, 3600, 1)  # 1 request per hour
            return True
        count = int(count)
        if count < 10:  # Limit to 10 requests per hour
            redis_client.incr(key)
            return True
        return False
    return False

@app.get("/health")
async def health(request: Request):
    ip = request.client.host
    if not rate_limit_check(ip):
        return {"status": "error", "message": "Rate limit exceeded"}, 500
    return {"status": "ok", "message": "Service is healthy"}, 200

@app.get("/grok-monitor")
async def grok_monitor():
    health = redis_client_instance.diagnose()
    return {
        "status": "ok",
        "redis_status": "Connected" if health["connection_active"] else "Disconnected",
        "timestamp": health["last_health_check"],
        "message": "Grok-enhanced monitoring active",
        "grok_insight": "Stable" if health["connection_active"] else "Potential Issue"
    }

@app.get("/grok-diagnose")
async def grok_diagnose():
    return redis_client_instance.diagnose()

@app.on_event("shutdown")
def shutdown_event():
    redis_client_instance.close()
