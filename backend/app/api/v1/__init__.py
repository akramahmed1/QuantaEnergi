"""
API v1 module for QuantaEnergi backend.

This module contains v1 API routers including:
- Trading API
- Risk Management API
- Logistics & Inventory API
- Health & Monitoring API
- Metrics API
- Authentication API
"""

from .trades import router as trades_router
from .risk import router as risk_router
from .logistics import router as logistics_router
from .health import router as health_router
from .metrics import router as metrics_router
from .auth import router as auth_router

__all__ = [
    "trades_router",
    "risk_router", 
    "logistics_router",
    "health_router",
    "metrics_router",
    "auth_router"
]
