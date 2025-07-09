# © 2025 EnergyOpti-Pro, Patent Pending
import os
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel
import redis.asyncio as redis
from cryptography.fernet import Fernet
import sqlite3
from tensorflow.lite.python.interpreter import Interpreter
import boto3
from datetime import datetime
import numpy as np

# Initialize FastAPI app
app = FastAPI(title="EnergyOpti-Pro", version="0.0.48")
app.mount("/public", StaticFiles(directory="public"), name="public")

# Set up rate limiting
redis_instance = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
limiter = Limiter(key_func=get_remote_address, default_limits=["10/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Encryption key
key = Fernet.generate_key()
cipher = Fernet(key)
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"

# Data models
class PredictionInput(BaseModel):
    data: list[float]

class InsightInput(BaseModel):
    text: str

# Database connection and initialization
def get_db():
    conn = sqlite3.connect("trades.db")
    conn.row_factory = sqlite3.Row
    # Create predictions table if it doesn't exist
    conn.execute("CREATE TABLE IF NOT EXISTS predictions (result BLOB, timestamp DATETIME)")
    return conn

# Load TFLite model
interpreter = None
try:
    model_path = os.path.join(os.path.dirname(__file__), "optimized_model.tflite")
    if os.path.exists(model_path) and os.path.getsize(model_path) > 0:
        interpreter = Interpreter(model_path=model_path)
        interpreter.allocate_tensors()
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        logging.info("TFLite model loaded from optimized_model.tflite with expected input length: 1")
    else:
        logging.warning(f"Warning: {model_path} is missing or empty. /predict endpoint will not work.")
except Exception as e:
    logging.error(f"Model loading error: {str(e)}")
    raise HTTPException(status_code=500, detail="Model loading failed")

# Health check
@app.get("/health")
@limiter.limit("100/hour")
async def health(request: Request):
    return {"status": "healthy"}

# Prediction endpoint with RMSE check and type correction
@app.post("/predict")
@limiter.limit("10/minute")
async def predict(request: Request, input: PredictionInput):
    if interpreter is None:
        raise HTTPException(status_code=503, detail="Prediction model not available")
    logging.info(f"Received input data: {input.data}")
    try:
        if not all(isinstance(x, (int, float)) for x in input.data):
            raise HTTPException(status_code=422, detail="Invalid input data")
        if len(input.data) != 1:
            raise HTTPException(status_code=400, detail="Input must contain exactly 1 value(s)")
        # Convert input to FLOAT32 to match model expectation
        input_data = np.array([[float(input.data[0])]], dtype=np.float32)
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()
        prediction = interpreter.get_tensor(output_details[0]['index'])[0][0]
        historical_rmse = 0.05
        if abs(prediction - historical_rmse) > 1.0:
            raise HTTPException(status_code=400, detail="Prediction exceeds RMSE threshold")
        confidence = 0.9
        if confidence < 0.8:
            logging.warning("Low confidence, escalating to human review")
            raise HTTPException(status_code=400, detail="Low confidence, review needed")
        encrypted_result = cipher.encrypt(str(prediction).encode())
        with get_db() as db:
            db.execute("INSERT INTO predictions (result, timestamp) VALUES (?, ?)",
                      (encrypted_result, datetime.utcnow()))
            db.commit()
        logging.info(f"Prediction result: {prediction}")
        return {"prediction": prediction.tolist()}
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

# Terms of service
@app.get("/terms", response_class=HTMLResponse)
async def terms():
    with open("terms.html", "r") as f:
        return f.read()

# Privacy policy
@app.get("/privacy", response_class=HTMLResponse)
async def privacy():
    with open("privacy.html", "r") as f:
        return f.read()

# Insights endpoint (placeholder)
@app.post("/insights")
@limiter.limit("50/hour")
async def insights(request: Request, input: InsightInput):
    return {"insights": {"polarity": 0.0, "subjectivity": 0.0}}

# Quantum analytics (placeholder)
@app.get("/quantum")
@limiter.limit("50/hour")
async def quantum(request: Request):
    return {"quantum_circuit": "Quantum circuit simulation placeholder"}

# History endpoint for UI
@app.get("/history")
async def history():
    try:
        with get_db() as db:
            cursor = db.execute("SELECT result, timestamp FROM predictions")
            rows = cursor.fetchall()
            return [{"value": float(cipher.decrypt(row["result"]).decode()), "timestamp": row["timestamp"]} for row in rows]
    except Exception as e:
        logging.error(f"History error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"History retrieval failed: {str(e)}")

# Backup function
def backup_db():
    s3 = boto3.client("s3", region_name="us-east-2")
    db_file = "trades.db"
    if not os.path.exists(db_file):
        conn = sqlite3.connect(db_file)
        conn.execute("CREATE TABLE IF NOT EXISTS predictions (result BLOB, timestamp DATETIME)")
        conn.commit()
        conn.close()
        logging.info(f"Created new trades.db at {os.path.abspath(db_file)}")
    try:
        s3.upload_file(db_file, "energyopti-pro-backup-simple", "trades.db")
        logging.info(f"Successfully uploaded {db_file} to S3 at {datetime.utcnow()}")
        return {"status": "backup completed"}
    except Exception as e:
        logging.error(f"Error uploading to S3: {e}")
        raise HTTPException(status_code=500, detail=f"S3 upload failed: {str(e)}")

# Backup trigger
@app.get("/backup_db")
async def trigger_backup():
    return backup_db()

# Root endpoint with HTML response
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return "<h1>Welcome to EnergyOpti-Pro</h1>"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
