from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, confloat, conint
from typing import Optional, Annotated
import logging
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

app = FastAPI(title="EnergyOpti-Pro API", version="0.1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup logging
logger = logging.getLogger("predict")
logger.setLevel(logging.INFO)

# Security constants
SECRET_KEY = "your-secret-key-keep-it-secret"  # In prod, use env variable
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

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

class BESSParameters(BaseModel):
    capacity_kwh: confloat(gt=0)
    current_soc: confloat(ge=0, le=100)
    electricity_price: confloat(gt=0)
    demand_forecast: confloat(gt=0)
    renewable_input: confloat(ge=0)
    optimization_horizon: conint(gt=0, le=24) = 4

class PredictionResponse(BaseModel):
    optimal_soc: float
    recommended_action: str
    cost_savings: float
    confidence_interval: Optional[tuple[float, float]] = None
    fallback_used: bool = False

class QuantumTradeRequest(BaseModel):
    market: str  # Nordpool/PJM/Enverus
    portfolio_size: confloat(gt=0)
    risk_tolerance: confloat(ge=0, le=1)
    time_horizon: conint(gt=0, le=72) = 4  # hours

class QuantumTradeResponse(BaseModel):
    optimal_allocation: dict
    expected_return: float
    risk_assessment: float
    quantum_time: float
    classical_time: float
    qpu_used: bool

@app.post("/quantum", response_model=QuantumTradeResponse)
async def quantum_trading(
    params: QuantumTradeRequest,
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    Quantum-accelerated trading optimization endpoint with market integration.
    Returns portfolio allocations with risk-adjusted returns.
    """
    try:
        # Mocked quantum simulation - PRD specifies Qiskit-aer integration
        logger.info(f"Quantum trading request for {params.market} market")
        
        # Placeholder for actual quantum circuit
        quantum_time = 0.05  # Simulated quantum computation time
        classical_time = 0.1  # Simulated classical computation time
        
        return QuantumTradeResponse(
            optimal_allocation={"renewables": 0.6, "storage": 0.3, "fossil": 0.1},
            expected_return=0.15,
            risk_assessment=0.25,
            quantum_time=quantum_time,
            classical_time=classical_time,
            qpu_used=False  # Indicate we're using simulator
        )
        
    except Exception as e:
        logger.error(f"Quantum trading error: {str(e)}")
        raise HTTPException(status_code=500, detail="Quantum trading service unavailable")

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
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/predict", response_model=PredictionResponse)
async def predict_bess(
    params: BESSParameters,
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    RL-based BESS optimization endpoint with fallback mechanism.
    Returns cost-saving predictions for battery energy storage systems.
    """
    try:
        # Placeholder for RL model - PRD specifies this should be implemented
        # For MVP, use simple heuristic with fallback data
        logger.info(f"Prediction request for {params.capacity_kwh}kWh system")
        
        # Simple heuristic model (to be replaced with RL model)
        optimal_soc = min(params.current_soc + 15, 100)  # Simple SOC adjustment
        cost_savings = params.demand_forecast * params.electricity_price * 0.2  # 20% savings
        
        return PredictionResponse(
            optimal_soc=optimal_soc,
            recommended_action="Charge during off-peak hours",
            cost_savings=round(cost_savings, 2),
            fallback_used=True  # Indicate we're using sample data
        )
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail="Prediction service unavailable")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
