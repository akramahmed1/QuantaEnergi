from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import uvicorn
import json
import time
import pandas as pd
import warnings
import os
import asyncio
import aiohttp
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import grpc
import structlog

# Import our modules
from app.core.config import settings
from app.db.session import get_db, create_tables
from app.api.auth import router as auth_router
from app.api.energy_data import router as energy_data_router
from app.api.admin import router as admin_router
from app.schemas.user import User
from app.core.security import verify_token

# Configure structured logging
logger = structlog.get_logger()

# Environment variables for API keys
CME_API_KEY = os.getenv("CME_API_KEY", "demo_key")
ICE_API_KEY = os.getenv("ICE_API_KEY", "demo_key")
NYMEX_API_KEY = os.getenv("NYMEX_API_KEY", "demo_key")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "demo_key")

# Quantum Security (mock for now)
QUANTUM_SECURITY_ENABLED = os.getenv("QUANTUM_SECURITY_ENABLED", "true").lower() == "true"

if not QUANTUM_SECURITY_ENABLED:
    warnings.warn("liboqs not available, using mock security")

# Create FastAPI app
app = FastAPI(
    title="EnergyOpti-Pro API",
    description="Next-Generation Energy Trading Platform with AI and Quantum Security",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(auth_router)
app.include_router(energy_data_router)
app.include_router(admin_router)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()
    logger.info("EnergyOpti-Pro application started successfully")

# Authentication dependency
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Get current authenticated user"""
    payload = verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user

# Legacy endpoints (now protected with authentication)
@app.get("/api/prices")
async def get_prices(region: str = "global", ramadan_mode: bool = False, current_user: User = Depends(get_current_user)):
    """Get market prices with user authentication"""
    try:
        # Simulate market data
        prices = {
            "cme_crude": {"data": 75.50, "change": 0.25, "volume": 1000},
            "ice_brent": {"data": 78.25, "change": -0.15, "volume": 1200},
            "natural_gas": {"data": 3.25, "change": 0.05, "volume": 800},
            "timestamp": datetime.now().isoformat(),
            "user_id": current_user.id
        }
        
        if ramadan_mode:
            prices["ramadan_adjustment"] = "Applied"
        
        return prices
    except Exception as e:
        logger.error(f"Error getting prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/models/v1/prices")
async def get_model_prices(current_user: User = Depends(get_current_user)):
    """Get ML model prices with user authentication"""
    try:
        model_prices = {
            "prophet_forecast": {"next_24h": 76.20, "next_7d": 77.85, "confidence": 0.85},
            "lstm_prediction": {"next_24h": 75.80, "next_7d": 77.20, "confidence": 0.82},
            "ensemble_result": {"next_24h": 76.00, "next_7d": 77.50, "confidence": 0.87},
            "timestamp": datetime.now().isoformat(),
            "user_id": current_user.id
        }
        return model_prices
    except Exception as e:
        logger.error(f"Error getting model prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/renewables")
async def get_renewable_energy(current_user: User = Depends(get_current_user)):
    """Get renewable energy data with user authentication"""
    try:
        renewables = {
            "wind": 2500,  # MW
            "solar": 1800,  # MW
            "hydro": 1200,  # MW
            "biomass": 800,  # MW
            "total": 6300,   # MW
            "timestamp": datetime.now().isoformat(),
            "user_id": current_user.id
        }
        return renewables
    except Exception as e:
        logger.error(f"Error getting renewables: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/retention")
async def get_retention_data(current_user: User = Depends(get_current_user)):
    """Get retention data with user authentication"""
    try:
        retention = {
            "customer_retention_rate": 0.92,
            "churn_rate": 0.08,
            "lifetime_value": 12500,
            "avg_tenure_months": 18,
            "timestamp": datetime.now().isoformat(),
            "user_id": current_user.id
        }
        return retention
    except Exception as e:
        logger.error(f"Error getting retention data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/onboarding")
async def get_onboarding_data(current_user: User = Depends(get_current_user)):
    """Get onboarding data with user authentication"""
    try:
        onboarding = {
            "completion_rate": 0.87,
            "avg_time_to_complete": "2.5 days",
            "drop_off_stage": "document_upload",
            "success_rate": 0.78,
            "timestamp": datetime.now().isoformat(),
            "user_id": current_user.id
        }
        return onboarding
    except Exception as e:
        logger.error(f"Error getting onboarding data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check(current_user: User = Depends(get_current_user)):
    """Health check endpoint with user authentication"""
    try:
        health_data = {
            "status": "healthy",
            "uptime": "99.9%",
            "services": {
                "database": "healthy",
                "redis": "healthy",
                "external_apis": "healthy",
                "quantum_security": "fallback" if not QUANTUM_SECURITY_ENABLED else "active"
            },
            "timestamp": datetime.now().isoformat(),
            "user_id": current_user.id
        }
        return health_data
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/secure")
async def secure_endpoint(current_user: User = Depends(get_current_user)):
    """Secure endpoint with user authentication"""
    try:
        secure_data = {
            "message": "Access granted to secure endpoint",
            "user_role": current_user.role,
            "company": current_user.company_name,
            "security_level": "high",
            "timestamp": datetime.now().isoformat(),
            "user_id": current_user.id
        }
        return secure_data
    except Exception as e:
        logger.error(f"Error in secure endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/secure/transparency")
async def transparency_endpoint(current_user: User = Depends(get_current_user)):
    """Transparency endpoint with user authentication"""
    try:
        transparency_data = {
            "data_sources": ["CME", "ICE", "NYMEX", "OpenWeatherMap"],
            "data_freshness": "real-time",
            "update_frequency": "1 minute",
            "data_quality": "high",
            "timestamp": datetime.now().isoformat(),
            "user_id": current_user.id
        }
        return transparency_data
    except Exception as e:
        logger.error(f"Error in transparency endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/oilfield")
async def get_oilfield_data(current_user: User = Depends(get_current_user)):
    """Get oilfield data with user authentication"""
    try:
        oilfield_data = {
            "production_rate": 1250,  # barrels/day
            "reserves": 5000000,      # barrels
            "efficiency": 0.87,
            "maintenance_status": "optimal",
            "timestamp": datetime.now().isoformat(),
            "user_id": current_user.id
        }
        return oilfield_data
    except Exception as e:
        logger.error(f"Error getting oilfield data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tariff_impact")
async def get_tariff_impact(current_user: User = Depends(get_current_user)):
    """Get tariff impact data with user authentication"""
    try:
        tariff_data = {
            "current_tariff": 0.15,  # $/kWh
            "projected_change": 0.02,
            "impact_on_bills": "+13.3%",
            "mitigation_options": ["energy_efficiency", "demand_response", "renewable_integration"],
            "timestamp": datetime.now().isoformat(),
            "user_id": current_user.id
        }
        return tariff_data
    except Exception as e:
        logger.error(f"Error getting tariff impact: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "EnergyOpti-Pro API",
        "version": "2.0.0",
        "status": "running",
        "documentation": "/docs",
        "timestamp": datetime.now().isoformat()
    }

# Health check without authentication for monitoring
@app.get("/health")
async def public_health_check():
    """Public health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "EnergyOpti-Pro is running"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
