"""
QuantaEnergi - AI-Powered Energy Trading Platform
Main FastAPI Application - Monorepo Structure
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
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Configure logging
warnings.filterwarnings("ignore")
logger = structlog.get_logger(__name__)

# Configure rate limiting
limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting QuantaEnergi API")
    
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

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware for localhost:5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Include API routers
from app.api.v1 import trade_lifecycle, auth, analytics, compliance
app.include_router(trade_lifecycle.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(compliance.router, prefix="/api/v1")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if True else "An unexpected error occurred"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
