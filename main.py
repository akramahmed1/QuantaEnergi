import logging
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import time

logging.basicConfig(level=logging.INFO, filename='app.log')
logger = logging.getLogger(__name__)

load_dotenv()
api_key = os.getenv("API_KEY", "a1009144b7a5520439407190f9064793")
app = FastAPI()

# Token bucket rate limiter with sliding window
rate_limits = {}  # IP -> (requests, last_reset_time)
MAX_REQUESTS = 100
WINDOW_SECONDS = 60

def rate_limit_check(ip):
    current_time = time.time()
    if ip not in rate_limits:
        rate_limits[ip] = ([current_time], current_time)
    else:
        requests, last_reset = rate_limits[ip]
        requests = [t for t in requests if current_time - t < WINDOW_SECONDS]
        if len(requests) >= MAX_REQUESTS:
            return False
        requests.append(current_time)
        rate_limits[ip] = (requests, last_reset if len(requests) < MAX_REQUESTS else current_time)
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
