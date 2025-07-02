# © 2025 EnergyOpti-Pro, Patent Pending
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel
import redis.asyncio as redis
from cryptography.fernet import Fernet
import sqlite3
import tflite_runtime.interpreter as tflite
from fastapi.responses import HTMLResponse
from jose import JWTError, jwt
from datetime import datetime, timedelta
from qiskit import QuantumCircuit
from huggingface_hub import hf_hub_download
from transformers import pipeline

app = FastAPI(title="EnergyOpti-Pro", version="0.0.48")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Security: Initialize Redis and Limiter
redis_instance = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security: AES encryption
key = Fernet.generate_key()
cipher = Fernet(key)

# JWT setup
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"

# NLP pipeline (lazy-loaded in /insights)
nlp = None

class PredictionInput(BaseModel):
    data: list[float]

def get_db():
    conn = sqlite3.connect("trades.db")
    conn.row_factory = sqlite3.Row
    return conn

# Load TFLite model (with check)
interpreter = None
try:
    if os.path.exists("optimized_model.tflite") and os.path.getsize("optimized_model.tflite") > 0:
        interpreter = tflite.Interpreter(model_path="optimized_model.tflite")
        interpreter.allocate_tensors()
    else:
        print("Warning: optimized_model.tflite is missing or empty. /predict endpoint will not work.")
except Exception as e:
    print(f"Error loading TFLite model: {e}")

@app.get("/health")
@limiter.limit("100/hour")
async def health(request: Request):
    return {"status": "healthy"}

@app.post("/predict")
@limiter.limit("50/hour")
async def predict(request: Request, input: PredictionInput):
    if interpreter is None:
        raise HTTPException(status_code=503, detail="Prediction model is not available")
    try:
        if not all(isinstance(x, (int, float)) for x in input.data):
            raise HTTPException(status_code=422, detail="Invalid input data")
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        interpreter.set_tensor(input_details[0]["index"], input.data)
        interpreter.invoke()
        prediction = interpreter.get_tensor(output_details[0]["index"])
        encrypted_result = cipher.encrypt(str(prediction).encode())
        with get_db() as db:
            db.execute("INSERT INTO predictions (result, timestamp) VALUES (?, ?)",
                      (encrypted_result, datetime.utcnow()))
            db.commit()
        return {"prediction": prediction.tolist()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/terms", response_class=HTMLResponse)
async def terms():
    with open("terms.html", "r") as f:
        return f.read()

@app.get("/privacy", response_class=HTMLResponse)
async def privacy():
    with open("privacy.html", "r") as f:
        return f.read()

@app.post("/insights")
@limiter.limit("50/hour")
async def insights(request: Request, text: str):
    global nlp
    if nlp is None:
        nlp = pipeline("text-classification", model=hf_hub_download("distilbert-base-uncased-finetuned-sst-2-english"))
    result = nlp(text)
    return {"insights": result}

@app.get("/quantum")
@limiter.limit("50/hour")
async def quantum(request: Request):
    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.cx(0, 1)
    return {"quantum_circuit": str(circuit)}

import boto3
def backup_db():
    s3 = boto3.client("s3")
    s3.upload_file("trades.db", "energyopti-pro-backup--use2-az1--x-s3", "trades.db")

@app.get("/backup_db")
async def trigger_backup():
    backup_db()
    return {"status": "backup completed"}
