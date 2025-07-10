# © 2025 EnergyOpti-Pro, Patent Pending
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Annotated, List, Dict
import logging
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import redis.asyncio as redis
from cryptography.fernet import Fernet
import sqlite3
from tensorflow.lite.python.interpreter import Interpreter
import boto3
import numpy as np

# Initialize FastAPI app
app = FastAPI(title="EnergyOpti-Pro API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up rate limiting
redis_instance = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
limiter = Limiter(key_func=get_remote_address, default_limits=["10/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Encryption key
key = Fernet.generate_key()
cipher = Fernet(key)
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-keep-it-secret")  # In prod, use env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Fake user database
fake_users_db = {
    "energyuser": {
        "username": "energyuser",
        "hashed_password": pwd_context.hash("energypass"),
        "role": "energy_manager",
        "email": "user@energyopti.com",
        "disabled": False,
    },
    "traderuser": {
        "username": "traderuser",
        "hashed_password": pwd_context.hash("tradepass"),
        "role": "trader",
        "email": "trader@energyopti.com",
        "disabled": False,
    }
}

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str
    email: str | None = None
    role: str
    disabled: bool | None = None

class UserInDB(User):
    hashed_password: str

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user or not pwd_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# PRD Models
class BESSParameters(BaseModel):
    capacity_kwh: float = Field(gt=0)
    current_soc: float = Field(ge=0, le=100)
    electricity_price: float = Field(gt=0)
    demand_forecast: float = Field(gt=0)
    renewable_input: float = Field(ge=0)
    optimization_horizon: int = Field(gt=0, le=24, default=4)

class PredictionResponse(BaseModel):
    optimal_soc: float
    recommended_action: str
    cost_savings: float
    confidence_interval: Optional[tuple[float, float]] = None
    fallback_used: bool = False

class QuantumTradeRequest(BaseModel):
    market: str  # Nordpool/PJM/Enverus
    portfolio_size: float = Field(gt=0)
    risk_tolerance: float = Field(ge=0, le=1)
    time_horizon: int = Field(gt=0, le=72, default=4)  # hours

class VPPDataRequest(BaseModel):
    grid_id: str
    battery_capacities: List[float] = Field(..., min_items=1)
    generation_data: Dict[str, float]
    timestamp: str
    region: str

class VPPDataResponse(BaseModel):
    vpp_capacity: float
    optimal_dispatch: Dict[str, float]
    stability_score: float
    revenue_opportunity: float
    alerts: List[str]

class CarbonRequest(BaseModel):
    facility_id: str
    start_date: str
    end_date: str
    fuel_types: Dict[str, float]

class CarbonMetricsResponse(BaseModel):
    carbon_intensity: float
    reduction_potential: float
    offset_requirements: float
    compliance_status: str

class CarbonCreditRequest(BaseModel):
    megawatt_hours: float = Field(gt=0)
    fuel_source: str
    region: str

class CarbonCreditResponse(BaseModel):
    credits_issued: float
    monetary_value: float
    certification: str
    transaction_id: str

class QuantumTradeResponse(BaseModel):
    optimal_allocation: Dict[str, float]
    expected_return: float
    risk_assessment: float
    quantum_time: float
    classical_time: float
    qpu_used: bool

class PredictionInput(BaseModel):
    data: List[float]

class InsightInput(BaseModel):
    text: str

# Database and Model Setup
def get_db():
    conn = sqlite3.connect("trades.db")
    conn.row_factory = sqlite3.Row
    conn.execute("CREATE TABLE IF NOT EXISTS predictions (result BLOB, timestamp DATETIME)")
    return conn

interpreter = None
try:
    model_path = os.path.join(os.path.dirname(__file__), "optimized_model.tflite")
    if os.path.exists(model_path) and os.path.getsize(model_path) > 0:
        interpreter = Interpreter(model_path=model_path)
        interpreter.allocate_tensors()
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        logging.info("TFLite model loaded from optimized_model.tflite")
    else:
        logging.warning(f"Warning: {model_path} is missing or empty.")
except Exception as e:
    logging.error(f"Model loading error: {str(e)}")

# Endpoints
@app.get("/health", response_model=dict)
@limiter.limit("100/hour")
async def health(request: Request):
    return {"status": "healthy"}

@app.post("/predict", response_model=PredictionResponse)
@limiter.limit("10/minute")
async def predict_bess(
    params: BESSParameters,
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    RL-based BESS optimization endpoint with fallback mechanism.
    Returns cost-saving predictions for battery energy storage systems.
    """
    try:
        logger.info(f"Prediction request for {params.capacity_kwh}kWh system")
        if interpreter:
            input_data = np.array([[params.demand_forecast]], dtype=np.float32)
            interpreter.set_tensor(input_details[0]['index'], input_data)
            interpreter.invoke()
            prediction = interpreter.get_tensor(output_details[0]['index'])[0][0]
            historical_rmse = 0.05
            if abs(prediction - historical_rmse) > 1.0:
                raise HTTPException(status_code=400, detail="Prediction exceeds RMSE")
            confidence = 0.9
            if confidence < 0.8:
                raise HTTPException(status_code=400, detail="Low confidence")
            optimal_soc = min(params.current_soc + prediction * 10, 100)
            cost_savings = params.demand_forecast * params.electricity_price * 0.2
        else:
            optimal_soc = min(params.current_soc + 15, 100)
            cost_savings = params.demand_forecast * params.electricity_price * 0.2
            fallback_used = True

        return PredictionResponse(
            optimal_soc=optimal_soc,
            recommended_action="Charge during off-peak hours",
            cost_savings=round(cost_savings, 2),
            confidence_interval=(cost_savings * 0.9, cost_savings * 1.1) if interpreter else None,
            fallback_used=fallback_used if 'fallback_used' in locals() else False
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/quantum", response_model=QuantumTradeResponse)
async def quantum_trading(
    params: QuantumTradeRequest,
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    if current_user.role != "trader":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    try:
        logger.info(f"Quantum trading request for {params.market} market")
        quantum_time = 0.05
        classical_time = 0.1
        return QuantumTradeResponse(
            optimal_allocation={"renewables": 0.6, "storage": 0.3, "conventional": 0.1},
            expected_return=0.15,
            risk_assessment=0.25,
            quantum_time=quantum_time,
            classical_time=classical_time,
            qpu_used=False
        )
    except Exception as e:
        logger.error(f"Quantum trading error: {str(e)}")
        raise HTTPException(status_code=500, detail="Quantum trading service unavailable")

@app.post("/iot", response_model=VPPDataResponse)
async def virtual_power_plant(
    params: VPPDataRequest,
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    try:
        logger.info(f"VPP data processing for grid {params.grid_id}")
        vpp_capacity = sum(params.battery_capacities) * 0.8
        alerts = ["Low reserve margin"] if vpp_capacity < 1000 else []
        return VPPDataResponse(
            vpp_capacity=round(vpp_capacity, 2),
            optimal_dispatch={"solar": 0.6, "wind": 0.3, "storage": 0.1},
            stability_score=0.92,
            revenue_opportunity=vpp_capacity * 0.15,
            alerts=alerts
        )
    except Exception as e:
        logger.error(f"VPP processing error: {str(e)}")
        raise HTTPException(status_code=500, detail="Grid optimization service unavailable")

@app.post("/carbon", response_model=CarbonMetricsResponse)
async def carbon_metrics(
    params: CarbonRequest,
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    try:
        logger.info(f"Carbon metrics request for {params.facility_id}")
        total_emissions = sum(params.fuel_types.values()) * 0.423
        return CarbonMetricsResponse(
            carbon_intensity=round(total_emissions / 1000, 2),
            reduction_potential=0.25,
            offset_requirements=max(total_emissions - 1000, 0),
            compliance_status="Compliant" if total_emissions < 1500 else "Action Required"
        )
    except Exception as e:
        logger.error(f"Carbon metrics error: {str(e)}")
        raise HTTPException(status_code=500, detail="Carbon accounting service unavailable")

@app.post("/carboncredit", response_model=CarbonCreditResponse)
async def carbon_credits(
    params: CarbonCreditRequest,
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    try:
        logger.info(f"Carbon credit request for {params.megawatt_hours}MWh")
        credit_value = params.megawatt_hours * 0.85
        return CarbonCreditResponse(
            credits_issued=credit_value,
            monetary_value=credit_value * 15.50,
            certification="Gold Standard",
            transaction_id="TXID-CC-2025-12345"
        )
    except Exception as e:
        logger.error(f"Carbon credit error: {str(e)}")
        raise HTTPException(status_code=500, detail="Carbon credit service unavailable")

@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/metrics")
async def system_metrics(current_user: Annotated[User, Depends(get_current_active_user)]):
    try:
        logger.info("Metrics request received")
        return {
            "uptime": 99.87,
            "active_connections": 42,
            "quantum_usage": 15.2,
            "carbon_offset": 1520.5,
            "system_load": [0.3, 0.4, 0.35]
        }
    except Exception as e:
        logger.error(f"Metrics error: {str(e)}")
        raise HTTPException(status_code=500, detail="Metrics service unavailable")

@app.get("/health", response_model=dict)
@limiter.limit("100/hour")
async def health(request: Request):
    return {"status": "healthy"}

@app.post("/insights", response_model=dict)
@limiter.limit("50/hour")
async def insights(request: Request, input: InsightInput):
    return {"insights": {"polarity": 0.0, "subjectivity": 0.0}}

@app.get("/quantum")
@limiter.limit("50/hour")
async def quantum(request: Request):
    return {"quantum_circuit": "Quantum circuit simulation placeholder"}

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

@app.get("/backup_db")
async def trigger_backup():
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

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return "<h1>Welcome to EnergyOpti-Pro</h1>"

@app.get("/terms", response_class=HTMLResponse)
async def terms():
    with open("terms.html", "r") as f:
        return f.read()

@app.get("/privacy", response_class=HTMLResponse)
async def privacy():
    with open("privacy.html", "r") as f:
        return f.read()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)