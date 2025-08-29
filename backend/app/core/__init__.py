"""
Core module for EnergyOpti-Pro backend.

This module contains core functionality including:
- Configuration management
- Security and authentication
- Database connections
- Logging setup
- Common utilities
"""

from .config import settings
from .security import get_current_user, create_access_token, verify_token
from .security_audit import SecurityAuditor, SecurityMiddleware

__all__ = [
    "settings",
    "get_current_user", 
    "create_access_token",
    "verify_token",
    "SecurityAuditor",
    "SecurityMiddleware"
]
