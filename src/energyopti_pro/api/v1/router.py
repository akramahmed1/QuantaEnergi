"""
Main API router for EnergyOpti-Pro v1.

This module provides the main API router and includes all sub-routers
for different functional areas of the application.
"""

from fastapi import APIRouter

from .endpoints import auth, esg, forecast, iot, predict, quantum, etrm, arabic_i18n, us_market_data

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(esg.router, prefix="/esg", tags=["ESG"])
api_router.include_router(forecast.router, prefix="/forecast", tags=["Forecasting"])
api_router.include_router(iot.router, prefix="/iot", tags=["IoT & VPP"])
api_router.include_router(predict.router, prefix="/predict", tags=["Predictive Analytics (RL)"])
api_router.include_router(quantum.router, prefix="/quantum", tags=["Quantum Trading"])
api_router.include_router(etrm.router, prefix="/etrm", tags=["ETRM/CTRM"])
api_router.include_router(arabic_i18n.router, prefix="/i18n", tags=["Arabic i18n & RTL Support"])
api_router.include_router(us_market_data.router, prefix="/us-market", tags=["US Power & Gas Markets"])