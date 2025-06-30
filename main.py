import logging
import os
from fastapi import FastAPI, HTTPException, Form, Request
from dotenv import load_dotenv
import time
import redis
from redis.exceptions import ConnectionError

logging.basicConfig(level=logging.INFO, filename='app.log')
logger = logging.getLogger(__name__)

load_dotenv()
api_key = os.getenv("API_KEY", "a1009144b7a5520439407190f9064793")
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = None  # Initialize outside try block to avoid unbinding
try:
    redis_client = redis.Redis.from_url(redis_url)  # Let rediss:// handle TLS
    redis_client.ping()
    logger.info("Connected to Redis successfully")
except ConnectionError as e:
    logger.error(f"Failed to connect to Redis: {e}, falling back to in-memory")
    redis_client = None

app = FastAPI()

# Sliding window rate limiter with Redis
MAX_REQUESTS = 100
WINDOW_SECONDS = 60

def rate_limit_check(ip):
    current_time = time.time()
    key = f"rate_limit:{ip}"
    if redis_client:
        try:
            requests = [float(t) for t in redis_client.lrange(key, 0, -1)]
            requests = [t for t in requests if current_time - t < WINDOW_SECONDS]
            request_count = len(requests)
            logger.info(f"IP {ip} - Requests: {request_count}, Current: {current_time}")
            if request_count >= MAX_REQUESTS:
                logger.warning(f"Rate limit exceeded for IP {ip}, count: {request_count}")
                return False
            redis_client.lpush(key, current_time)
            redis_client.ltrim(key, 0, MAX_REQUESTS - 1)  # Keep only last 100
        except Exception as e:
            logger.error(f"Redis operation failed: {e}, falling back to in-memory")
            redis_client = None
    if not redis_client:
        if ip not in rate_limits:
            rate_limits[ip] = ([current_time], current_time)
            logger.info(f"New IP {ip} initialized with 1 request at {current_time}")
        else:
            requests, last_reset = rate_limits[ip]
            requests = [t for t in requests if current_time - t < WINDOW_SECONDS]
            request_count = len(requests)
            logger.info(f"IP {ip} - Requests: {request_count}, Current: {current_time}, Last Reset: {last_reset}")
            if request_count >= MAX_REQUESTS:
                logger.warning(f"Rate limit exceeded for IP {ip}, count: {request_count}")
                return False
            requests.append(current_time)
            rate_limits[ip] = (requests, current_time)
    return True

rate_limits = {}  # Fallback in-memory store

@app.get("/health")
async def health(request: Request):
    ip = request.headers.get("X-Forwarded-For", "127.0.0.1").split(",")[0]
    logger.info(f"Health check requested from IP {ip}")
    if not rate_limit_check(ip):
        logger.warning(f"Rate limit exceeded for IP {ip}")
        raise HTTPException(status_code=429, detail="Too many requests")
    return {"status": "healthy", "timestamp": str(os.times())}

@app.post("/predict")
async def predict(request: Request, value: float = Form(...)):  # Fixed SyntaxError
    ip = request.headers.get("X-Forwarded-For", "127.0.0.1").split(",")[0]
    logger.info(f"Predict request from IP {ip} with value={value}")
    if not rate_limit_check(ip):
        logger.warning(f"Rate limit exceeded for IP {ip}")
        raise HTTPException(status_code=429, detail="Too many requests")
    try:
        prediction = value * 3.339726448059082
        logger.info(f"Prediction successful: {prediction}")
        return {"prediction": str(prediction), "history": [(value, prediction)], "commodity_price": 0, "compliance": True}
    except Exception as e:
        logger.error("Prediction failed", exc_info=True)
        raise HTTPException(status_code=500, detail="Prediction error")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server")
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
