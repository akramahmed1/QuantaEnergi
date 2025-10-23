"""
Database configuration and setup for EnergyOpti-Pro.

This module provides database connection, session management, and model base class.
"""

from .session import engine, Base, SessionLocal, get_db, create_tables, get_user_scoped_query

__all__ = [
    "engine",
    "Base", 
    "SessionLocal",
    "get_db",
    "create_tables",
    "get_user_scoped_query"
]
