# © 2025 EnergyOpti-Pro, Patent Pending
import os
import numpy as np
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
import tflite_runtime.interpreter as tflite
from jose import JWTError, jwt
from datetime import datetime, timedelta
from qiskit import QuantumCircuit
from textblob import TextBlob
import boto3

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

# Database connection
def get_db():
    conn = sqlite3.connect("trades.db")
    conn.row_factory = sqlite3.Row
    return conn

# Load TFLite model and detect input shape
interpreter = None
expected_input_length = None
try:
    model_path = "optimized_model.tflite"  # Relative to /app root on Heroku
    if os.path.exists(model_path) and os.path.getsize(model_path) > 0:
        interpreter = tflite.Interpreter(model_path=model_path)
        interpreter.allocate_tensors()
        input_details = interpreter.get_input_details()[0]
        expected_input_length = input_details["shape"][1]  # Get the expected length of the input dimension
        print(f"TFLite model loaded from {model_path} with expected input length: {expected_input_length}")
    else:
        print(f"Warning: {model_path} is missing or empty. /predict endpoint will not work.")
except Exception as e:
    print(f"Error loading TFLite model: {e}")

# Startup event to initialize database
@app.on_event("startup")
async def startup_event():
    with get_db() as db:
        db.execute("CREATE TABLE IF NOT EXISTS predictions (result BLOB, timestamp DATETIME)")
        db.commit()
        print("Initialized predictions table on startup")

# Root route to fix 404
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <html>
        <head><title>EnergyOpti-Pro</title></head>
        <body>
            <h1>Welcome to EnergyOpti-Pro</h1>
            <p>API is running. Try the following endpoints:</p>
            <ul>
                <li><a href="/health">/health</a></li>
                <li><a href="/predict" onclick="alert('Use POST with {\"data\":[value1, value2]}')">/predict</a></li>
                <li><a href="/insights" onclick="alert('Use POST with {\"text\":\"your text\"}')">/insights</a></li>
            </ul>
            <div id="chart">Chart will load here if /public/index.html exists</div>
            <script>
                // Placeholder for chart (replace with your chart.js code if needed)
                document.getElementById("chart").innerText = "Chart data loading...";
                fetch('/history').then(r => r.json()).then(data => console.log(data));
            </script>
        </body>
    </html>
    """

# Health check
@app.get("/health")
@limiter.limit("100/hour")
async def health(request: Request):
    return {"status": "healthy"}

# Prediction endpoint with RMSE check
@app.post("/predict")
@limiter.limit("10/minute")
async def predict(request: Request, input: PredictionInput):
    if interpreter is None:
        raise HTTPException(status_code=503, detail="Prediction model not available")
    try:
        if not all(isinstance(x, (int, float)) for x in input.data):
            raise HTTPException(status_code=422, detail="Invalid input data")
        if len(input.data) != expected_input_length:
            raise HTTPException(status_code=400, detail=f"Input must contain exactly {expected_input_length} value(s)")
        input_data = np.array([input.data], dtype=np.float32)  # Shape (1, expected_length)
        interpreter.set_tensor(interpreter.get_input_details()[0]["index"], input_data)
        interpreter.invoke()
        prediction = interpreter.get_tensor(interpreter.get_output_details()[0]["index"])[0][0]
        historical_rmse = 0.05
        if abs(prediction - historical_rmse) > 1.0:
            raise HTTPException(status_code=400, detail="Prediction exceeds RMSE threshold")
        confidence = 0.9
        if confidence < 0.8:
            print("Low confidence, escalating to human review")
            raise HTTPException(status_code=400, detail="Low confidence, review needed")
        encrypted_result = cipher.encrypt(str(prediction).encode())
        with get_db() as db:
            db.execute("CREATE TABLE IF NOT EXISTS predictions (result BLOB, timestamp DATETIME)")
            db.execute("INSERT INTO predictions (result, timestamp) VALUES (?, ?)",
                      (encrypted_result, datetime.utcnow()))
            db.commit()
        return {"prediction": prediction.tolist()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

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

# Insights endpoint
@app.post("/insights")
@limiter.limit("50/hour")
async def insights(request: Request, input: InsightInput):
    analysis = TextBlob(input.text)
    polarity = analysis.sentiment.polarity
    subjectivity = analysis.sentiment.subjectivity
    return {"insights": {"polarity": polarity, "subjectivity": subjectivity}}

# Quantum analytics
@app.get("/quantum")
@limiter.limit("50/hour")
async def quantum(request: Request):
    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.cx(0, 1)
    return {"quantum_circuit": str(circuit)}

# History endpoint for UI
@app.get("/history")
async def history():
    with get_db() as db:
        cursor = db.execute("SELECT result, timestamp FROM predictions")
        rows = cursor.fetchall()
        return [{"value": float(cipher.decrypt(row["result"]).decode()), "timestamp": row["timestamp"]} for row in rows]

# Backup function
def backup_db():
    s3 = boto3.client("s3", region_name="us-east-2")
    db_file = "trades.db"
    if not os.path.exists(db_file):
        conn = sqlite3.connect(db_file)
        conn.execute("CREATE TABLE IF NOT EXISTS predictions (result BLOB, timestamp DATETIME)")
        conn.commit()
        conn.close()
        print(f"Created new trades.db at {os.path.abspath(db_file)}")
    try:
        s3.upload_file(db_file, "energyopti-pro-backup-simple", "trades.db")
        print(f"Successfully uploaded {db_file} to S3 at {datetime.utcnow()}")
        return {"status": "backup completed"}
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        raise HTTPException(status_code=500, detail=f"S3 upload failed: {str(e)}")

# Backup trigger
@app.get("/backup_db")
async def trigger_backup():
    return backup_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
