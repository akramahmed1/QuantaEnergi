import logging
import os
logging.basicConfig(level=logging.INFO, filename='app.log')
logger = logging.getLogger(__name__)

from fastapi import FastAPI, HTTPException
from fastapi_limiter import FastAPILimiter, RateLimiter
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY", "a1009144b7a5520439407190f9064793")
app = FastAPI()
app.add_middleware(RateLimiter, max_requests=100, window_seconds=60)

class Input(BaseModel):
    value: float

@app.get("/health")
async def health():
    logger.info("Health check requested")
    return {"status": "healthy", "timestamp": str(os.times())}

@app.post("/predict")
async def predict(input_data: Input):
    logger.info(f"Predict request received with value={input_data.value}")
    try:
        prediction = input_data.value * 3.339726448059082
        logger.info(f"Prediction successful: {prediction}")
        return {"prediction": str(prediction), "history": [(input_data.value, prediction)], "commodity_price": 0, "compliance": True}
    except Exception as e:
        logger.error("Prediction failed", exc_info=True)
        raise HTTPException(status_code=500, detail="Prediction error")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server with compressed assets")
    # Note: Adjust static serving if needed (e.g., extract static.tar.gz here)
    uvicorn.run(app, host="0.0.0.0", port=8000)
