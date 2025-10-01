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
from app.services.enhanced_trade_service import TradeLifecycleService
from app.services.risk_service import calculate_var, monte_carlo_var, calculate_enhanced_var
from app.services.ai_service import forecast_price, quantum_optimize_portfolio, forecast_load, ensemble_forecast
from app.services.market_service import market_data_broadcaster, fetch_energy_prices, get_market_volatility
from app.services.geo_risk_service import fetch_geo_risk, get_geo_risk_recommendations
from app.services.compliance_service import ComplianceService, ComplianceFramework
from app.services.esg_service import track_esg
from app.services.integration_service import fetch_erp_data
from app.api.v1 import market_data, monte_carlo_var, real_pnl
from app.core.auth import auth_manager, get_current_user
from app.domains.trading.routers import router as trading_router
from app.domains.risk.routers import router as risk_router
from app.domains.ai_forecasting.services import AIForecastingService
from app.domains.geo_risk.routers import router as geo_risk_router
from app.domains.quantum.routers import router as quantum_router
from app.domains.blockchain.routers import router as blockchain_router
from app.domains.compliance.routers import router as compliance_router
from app.core.trade_engine import TradeEngine
from app.core.risk_calculator import RiskCalculator
import numpy as np
import websockets
from typing import List, Dict, Any
from prometheus_client import Counter
from datetime import datetime
from fastapi import Query

# Pydantic models
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

c = Counter('test_metric', 'Test counter for QuantaEnergi debugging')  # Name first, docs second

# Create FastAPI application
app = FastAPI(
    title="QuantaEnergi ETRM/CTRM API",
    description="""...""",  # (Omitted for brevity; keep the long description from main)
    version="2.0.0",
    contact={
        "name": "QuantaEnergi Team",
        "email": "team@quantaenergi.com",
        "url": "https://github.com/akramahmed1/QuantaEnergi"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Local Development Server"
        },
        {
            "url": "https://quantaenergi-backend.railway.app",
            "description": "Production Server (Railway)"
        }
    ],
    tags_metadata=[
        # ... (keep all tags from main)
    ]
)

security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

trade_engine = TradeEngine()
risk_calculator = RiskCalculator()

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://quantaenergi.vercel.app",
        "https://*.vercel.app",
        "https://*.railway.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Health & Monitoring"])
def health():
    return {"status": "healthy"}

@app.post("/auth/login", tags=["Authentication"])
@app.post("/v1/auth/login", tags=["Authentication"])
async def login(form_data: dict = Body(...), db: Session = Depends(get_db)):
    username = form_data.get("username")
    password = form_data.get("password")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not auth_manager.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user_data = {
        "user_id": str(user.id),
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "organization_id": getattr(user, 'organization_id', 'default'),
        "is_active": True
    }
    token = auth_manager.create_access_token(user_data)
    return {
        "access_token": token, 
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "company_name": getattr(user, 'company_name', 'QuantaEnergi')
    }

# ... (all other endpoint definitions from main branch, unchanged) ...

# ... [existing code above unchanged] ...

# Include API routers
app.include_router(market_data.router, prefix="/api/v1")
app.include_router(monte_carlo_var.router, prefix="/api/v1")
app.include_router(real_pnl.router, prefix="/api/v1")

# ... [existing code above unchanged] ...

# Include API routers
app.include_router(market_data.router, prefix="/api/v1")
app.include_router(monte_carlo_var.router, prefix="/api/v1")
app.include_router(real_pnl.router, prefix="/api/v1")

# Include domain routers
app.include_router(trading_router, prefix="/api/v1")
app.include_router(risk_router, prefix="/api/v1")
app.include_router(geo_risk_router, prefix="/api/v1")
app.include_router(quantum_router, prefix="/api/v1")
app.include_router(blockchain_router, prefix="/api/v1")
app.include_router(compliance_router, prefix="/api/v1")

# Advanced ETRM router - fix collision and mount at /api/v1/advanced
from app.api.v1.advanced_etrm import router as advanced_etrm_router
app.include_router(advanced_etrm_router, prefix="/api/v1/advanced")

# Comprehensive ETRM/CTRM router remains at /api/v1
from app.api.etrm_api import router as etrm_router
app.include_router(etrm_router, prefix="/api/v1")
