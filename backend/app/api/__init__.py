"""
API module for EnergyOpti-Pro backend.

This module contains all FastAPI routers including:
- Authentication API
- Disruptive Features API
- Admin API
- Energy Data API
"""

from .auth import router as auth_router
from .disruptive_features import router as disruptive_router
from .admin import router as admin_router
from .energy_data import router as energy_data_router

__all__ = [
    "auth_router",
    "disruptive_router", 
    "admin_router",
    "energy_data_router"
]
