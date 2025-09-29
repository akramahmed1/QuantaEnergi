"""
Trade Model - ETRM Trade Capture
SQLAlchemy model for trade capture
"""

from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Trade(Base):
    """Trade model for ETRM trade capture"""
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True)
    asset = Column(String)
    quantity = Column(Float)
    price = Column(Float)
    timestamp = Column(DateTime)