"""
QuantaEnergi - AI-Powered Energy Trading Platform
Main FastAPI Application - Production Ready
"""

import os
import warnings
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import structlog

# Local imports
from .core.config import settings
from .db.session import get_db, create_tables
from .api.v1.auth import router as auth_router
from .api.v1.energy_data import router as energy_data_router
from .api.v1.admin import router as admin_router
from .api.v1.trade_lifecycle import router as trade_lifecycle_router
from .api.v1.risk_analytics import router as risk_analytics_router
from .api.v1.credit_management import router as credit_management_router
from .api.v1.options_trading import router as options_trading_router
from .api.v1.compliance import router as compliance_router
from .api.v1.websocket import router as websocket_router
from .schemas.user import User
from .core.security import verify_token

# Configure logging
warnings.filterwarnings("ignore")
logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting QuantaEnergi API")
    try:
        await create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down QuantaEnergi API")

# Create FastAPI application
app = FastAPI(
    title="QuantaEnergi - AI-Powered Energy Trading Platform",
    description="""
    ## 🌟 QuantaEnergi: Revolutionary Energy Trading SaaS
    
    **Transform your energy trading with AI, Quantum Computing, and Blockchain technology.**
    
    ### 🚀 Key Features
    
    * **AI-Powered Forecasting** with real-time market data
    * **Quantum Portfolio Optimization** for maximum returns
    * **Blockchain Smart Contracts** for transparent trading
    * **Multi-Region Compliance** (FERC, Dodd-Frank, REMIT, Islamic Finance)
    * **Real-time IoT Integration** for grid and weather data
    * **ESG Scoring & Sustainability** metrics
    
    ### 🔐 Security
    
    * JWT-based authentication with post-quantum cryptography
    * OWASP Top 10 compliance
    * Rate limiting and threat detection
    * Multi-factor authentication support
    
    ### 📊 Market Data
    
    * Real-time prices from CME, ICE, NYMEX
    * Weather correlation analysis
    * Renewable energy capacity tracking
    * Oilfield production data
    * Tariff impact analysis
    
    ### 🎯 Getting Started
    
    1. **Register**: Use `/api/auth/register` to create an account
    2. **Login**: Use `/api/auth/login` to get access token
    3. **Trade**: Access market data and execute trades
    4. **Optimize**: Use AI and quantum optimization
    5. **Comply**: Ensure regulatory compliance
    
    ### 🔗 API Endpoints
    
    * **Authentication**: `/api/auth/*`
    * **Market Data**: `/api/energy-data/*`
    * **Trading**: `/api/trade-lifecycle/*`
    * **Analytics**: `/api/risk-analytics/*`
    * **Compliance**: `/api/compliance/*`
    * **WebSocket**: `/ws/*`
    """,
    version="2.0.0",
    contact={
        "name": "QuantaEnergi Team",
        "email": "support@quantaenergi.com",
        "url": "https://quantaenergi.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(energy_data_router, prefix="/api/energy-data", tags=["Energy Data"])
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])
app.include_router(trade_lifecycle_router, prefix="/api/trade-lifecycle", tags=["Trade Lifecycle"])
app.include_router(risk_analytics_router, prefix="/api/risk-analytics", tags=["Risk Analytics"])
app.include_router(credit_management_router, prefix="/api/credit-management", tags=["Credit Management"])
app.include_router(options_trading_router, prefix="/api/options", tags=["Options Trading"])
app.include_router(compliance_router, prefix="/api/compliance", tags=["Compliance"])
app.include_router(websocket_router, prefix="/ws", tags=["WebSocket"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "QuantaEnergi API v2.0",
        "status": "operational",
        "version": "2.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "QuantaEnergi API",
        "version": "2.0.0",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/api/status")
async def api_status():
    """API status endpoint"""
    return {
        "api_status": "operational",
        "features": {
            "authentication": "enabled",
            "trade_lifecycle": "enabled",
            "risk_analytics": "enabled",
            "compliance": "enabled",
            "websocket": "enabled"
        },
        "rate_limit": "100 requests per minute per IP"
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
