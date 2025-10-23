"""
Base domain configuration
"""
from sqlalchemy.orm import Session
from app.db.session import get_db

# Re-export for domain imports
__all__ = ["get_db"]
