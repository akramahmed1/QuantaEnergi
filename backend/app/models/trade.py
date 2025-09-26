"""
Trade Model - PRD 4.1 DB schema
SQLAlchemy model for trade capture
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Trade(Base):
    """Trade model matching PRD 4.1 schema"""
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True, index=True)
    asset = Column(String(50), nullable=False)
    volume = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    region = Column(String(50), nullable=False)
    amendments = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default='captured')