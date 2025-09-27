"""
Trade Model - ETRM Trade Capture
SQLAlchemy model for trade capture
"""

from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from .base import Base

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    asset = Column(String)
    quantity = Column(Float)
    price = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())