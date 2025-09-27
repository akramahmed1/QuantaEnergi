"""
QuantaEnergi - Minimal FastAPI Application
"""

from fastapi import FastAPI, Body, Depends, Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.config import settings
from app.db.session import engine, get_db
from app.models import Base, Trade, ESG, User
from passlib.context import CryptContext
from app.services.trade_service import reconcile_position
from app.services.risk_service import calculate_var
from app.services.ai_service import forecast_price, quantum_optimize_portfolio, forecast_load, ensemble_forecast
from app.services.market_service import market_data_broadcaster
from app.services.compliance_service import ComplianceService, ComplianceFramework
from app.services.esg_service import track_esg
from app.services.integration_service import fetch_erp_data
from app.security.auth import create_access_token, verify_token
import numpy as np
import websockets
from typing import List
from prometheus_client import Counter

c = Counter('test_metric', 'Test counter for QuantaEnergi debugging')  # Name first, docs second

# Create FastAPI application
app = FastAPI(
    title="QuantaEnergi API",
    version="0.1.0"
)

# Security scheme for JWT Bearer authentication
security = HTTPBearer()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Get current user from JWT token"""
    if credentials:
        token = credentials.credentials
        user = verify_token(token)
        if user:
            return user
    raise HTTPException(status_code=401, detail="Invalid or missing token")

# Create database tables
Base.metadata.create_all(bind=engine)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/auth/login")
async def login(form_data: dict = Body(...), db: Session = Depends(get_db)):
    """Login endpoint to generate JWT token"""
    user = db.query(User).filter(User.username == form_data.get("username")).first()
    if user and pwd_context.verify(form_data.get("password"), user.hashed_password):
        token = create_access_token(subject=user.username)
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/trades")
async def create_trade(
    trade: TradeCreate = Body(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new trade (requires JWT authentication)"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Auth failed")

    # Create & save trade
    trade_obj = Trade(
        asset=trade.asset,
        quantity=trade.quantity,
        price=trade.price,
        # Add user_id= current_user.id if models link (e.g., owner_id FK)
    )
    db.add(trade_obj)
    db.commit()
    db.refresh(trade_obj)  # Fetches real ID/timestamp

    # Auto-generate ESG
    esg_result = track_esg(trade_obj.id, db)  # Your service—assumes it inserts ESG row

    return {
        "id": trade_obj.id,
        "trade": {
            "asset": trade_obj.asset,
            "quantity": trade_obj.quantity,
            "price": trade_obj.price,
            "timestamp": trade_obj.timestamp.isoformat() if trade_obj.timestamp else None
        },
        "user": current_user,
        "esg": ESGResponse(**esg_result)  # e.g., {"co2": 35.2, "certs": "silver"}
    }

@app.get("/trades/{id}/position")
def get_position(id: int, db=Depends(get_db), current_user = Depends(get_current_user)):
    """Get position for a trade"""
    return reconcile_position(db, id)

@app.post("/risk/var")
def var_endpoint(prices: List[float] = Body(...)):
    """Calculate Value at Risk for given price series"""
    return {"var": calculate_var(prices)}

@app.post("/forecast/price")
def forecast(historical: List[float] = Body(...)):
    """Forecast next price using AI/ML ensemble"""
    ensemble_result = ensemble_forecast(historical)
    return {"prediction": ensemble_result['pred'], "accuracy": ensemble_result['accuracy']}

@app.post("/esg/track")
async def track_esg_endpoint(trade_id: ESGTrack = Body(...), db=Depends(get_db), current_user = Depends(get_current_user)):
    """Track ESG metrics for a trade"""
    return track_esg(trade_id.trade_id, db)

class TradeCreate(BaseModel):
    asset: str
    quantity: float
    price: float

class ESGResponse(BaseModel):
    co2: float
    certs: str

class ESGTrack(BaseModel):
    trade_id: int

class OptRequest(BaseModel):
    returns: list[float]
    risks: list[float]

@app.post("/optimize/portfolio")
async def opt_endpoint(req: OptRequest, current_user = Depends(get_current_user)):
    """Quantum portfolio optimization"""
    return quantum_optimize_portfolio(req.returns, req.risks)

@app.get("/integrate/erp")
async def integrate_erp(current_user = Depends(get_current_user)):
    """ERP integration endpoint"""
    return fetch_erp_data("mock_endpoint")

@app.post("/forecast/load")
def forecast_load_endpoint(historical: List[float] = Body(...)):
    """Load forecasting endpoint"""
    return forecast_load(historical)

@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint"""
    return c

@app.get("/dashboard")
def dashboard(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Dashboard endpoint with user stats"""
    total_trades = db.query(func.count(Trade.id)).scalar()
    avg_co2 = db.query(func.avg(ESG.co2)).scalar() or 0
    return {
        "user": current_user,
        "stats": {"trades": total_trades, "avg_co2": round(avg_co2, 2)}
    }

# WebSocket endpoint for market data
@app.websocket("/ws/market")
async def websocket_market_data(websocket):
    """WebSocket endpoint for real-time market data"""
    await market_data_broadcaster(websocket, "/ws/market")

@app.post("/compliance/validate")
def validate_compliance(request: dict = Body(...), current_user = Depends(get_current_user)):
    """Validate trade compliance against regulatory framework"""
    trade_data = request.get("trade", {})
    framework_str = request.get("framework", "REMIT")
    
    try:
        framework = ComplianceFramework(framework_str)
        result = ComplianceService.validate_trade_compliance(trade_data, framework)
        return result
    except ValueError:
        return {"error": f"Invalid framework. Supported: {[f.value for f in ComplianceFramework]}"}

@app.post("/compliance/report")
def generate_compliance_report(request: dict = Body(...), current_user = Depends(get_current_user)):
    """Generate compliance report for multiple trades"""
    trades = request.get("trades", [])
    framework_str = request.get("framework", "REMIT")
    
    try:
        framework = ComplianceFramework(framework_str)
        report = ComplianceService.generate_compliance_report(trades, framework)
        return report
    except ValueError:
        return {"error": f"Invalid framework. Supported: {[f.value for f in ComplianceFramework]}"}

# Placeholder for future routers
# app.include_router()  # Will be added when routers are created