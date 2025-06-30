from fastapi import FastAPI
from starlette.requests import Request
from redis_config import RedisClient
import os

app = FastAPI()

# Initialize Redis client with GECP
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
        "grok_insight": health["prediction"],
        "evolved_threshold": health["evolved_threshold"],
        "victory_count": health["victory_count"]
    }

@app.get("/grok-diagnose")
async def grok_diagnose():
    return redis_client_instance.diagnose()

@app.get("/grok-diagnostic")
async def grok_diagnostic():
    diagnostic = redis_client_instance._startup_diagnostic
    timestamp = diagnostic["timestamp"]
    victory_count = redis_client_instance._usage_pattern["victory_count"]
    legacy_message = f"Victory {victory_count} at {timestamp}: App resilience achieved"
    return {
        "status": "ok",
        "diagnostic": diagnostic,
        "legacy_chronicle": legacy_message,
        "legacy_suggestion": f"Store in Redis with SET legacy:{victory_count} '{legacy_message}'"
    }

@app.on_event("shutdown")
def shutdown_event():
    redis_client_instance.close()
