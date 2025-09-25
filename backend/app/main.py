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

# Configure logging
warnings.filterwarnings("ignore")
logger = structlog.get_logger(__name__)

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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
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

# Import error handling middleware
from app.middleware.error_handler import setup_error_handlers

# Import GraphQL router
from app.graphql import graphql_router

# Import new API routers
from app.api.v1.risk_forecast import router as risk_forecast_router
from app.api.v1.quantum_var import router as quantum_var_router

# Import security middleware
from app.middleware.waf_middleware import setup_waf_middleware

# Import federated auth
from app.security.federated_auth import get_federated_auth_manager, create_federated_auth_routes

# Import tenant management
from app.api.tenant_management import router as tenant_router

# Import monitoring
from app.monitoring.metrics import MetricsMiddleware, get_metrics, start_metrics_server

# Import Celery
from app.core.celery_app import get_celery_app

# Setup comprehensive error handlers
setup_error_handlers(app)

# Setup WAF middleware
setup_waf_middleware(app)

# Setup metrics middleware
metrics_middleware = MetricsMiddleware(get_metrics())
app.middleware("http")(metrics_middleware)

# Add GraphQL endpoint
app.include_router(graphql_router, prefix="/api", tags=["GraphQL"])

# Add new API routers
app.include_router(risk_forecast_router, tags=["AI/ML Risk Forecast"])
app.include_router(quantum_var_router, tags=["Quantum VaR"])

# Add tenant management routes
app.include_router(tenant_router)

# Add federated authentication routes
auth_manager = get_federated_auth_manager()
# Note: create_federated_auth_routes is called during app startup

# Start metrics server
start_metrics_server(port=8001)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
