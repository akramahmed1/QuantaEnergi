import logging
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from collections import deque
import time

logging.basicConfig(level=logging.INFO, filename='app.log')
logger = logging.getLogger(__name__)

load_dotenv()
api_key = os.getenv("API_KEY", "a1009144b7a5520439407190f9064793")
app = FastAPI()

# Token bucket rate limiter
rate_limits = {}  # IP -> (tokens, last_refill_time)
MAX_TOKENS = 100
REFILL_RATE = 100 / 60  # 100 tokens per minute
WINDOW_SECONDS = 60

def refill_tokens(ip):
    current_time = time.time()
    if ip not in rate_limits:
        rate_limits[ip] = [MAX_TOKENS, current_time]
    else:
        tokens, last_time = rate_limits[ip]
        time_passed = current_time - last_time
        new_tokens = time_passed * REFILL_RATE
        rate_limits[ip] = [min(MAX_TOKENS, tokens + new_tokens), current_time]

def rate_limit_check(ip):
    refill_tokens(ip)
    tokens, _ = rate_limits[ip]
    if tokens < 1:
        return False
    rate_limits[ip][0] -= 1
    return True

class Input(BaseModel):
    value: float

@app.get("/health")
async def health():
    ip = "127.0.0.1"  # Replace with request.client.host in production
    logger.info(f"Health check requested from IP {ip}")
    if not rate_limit_check(ip):
        logger.warning(f"Rate limit exceeded for IP {ip}")
        raise HTTPException(status_code=429, detail="Too many requests")
    return {"status": "healthy", "timestamp": str(os.times())}

@app.post("/predict")
async def predict(input_data: Input):
    ip = "127.0.0.1"  # Replace with request.client.host in production
    logger.info(f"Predict request from IP {ip} with value={input_data.value}")
    if not rate_limit_check(ip):
        logger.warning(f"Rate limit exceeded for IP {ip}")
        raise HTTPException(status_code=429, detail="Too many requests")
    try:
        prediction = input_data.value * 3.339726448059082
        logger.info(f"Prediction successful: {prediction}")
        return {"prediction": str(prediction), "history": [(input_data.value, prediction)], "commodity_price": 0, "compliance": True}
    except Exception as e:
        logger.error("Prediction failed", exc_info=True)
        raise HTTPException(status_code=500, detail="Prediction error")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server")
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
