import redis
from urllib.parse import urlparse
import os
from fastapi import FastAPI
from starlette.requests import Request

app = FastAPI()

# Get REDIS_URL from environment or use the hardcoded value from Heroku
redis_url = os.getenv("REDIS_URL", "rediss://:p8ed102d8362feafa2a1def2e439ac84c169a69bca6815e182cf1a3da43130c7d@ec2-34-236-184-217.compute-1.amazonaws.com:29730")
url = urlparse(redis_url)
redis_client = redis.Redis(
    host=url.hostname,
    port=url.port,
    password=url.password,
    db=0,
    ssl=True,
    ssl_cert_reqs=None  # Temporary for testing; secure in production
)

def rate_limit_check(ip):
    if redis_client:
        # Simple rate limiting logic (customize as needed)
        return True  # Replace with actual rate limiting logic
    return False

@app.get("/health")
async def health(request: Request):
    ip = request.client.host
    if not rate_limit_check(ip):
        return {"status": "error"}, 500
    return {"status": "ok"}, 200
