"""
Trade Model - ETRM Trade Capture
SQLAlchemy model for trade capture
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.sql import func
from .base import Base

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    asset = Column(String, nullable=False)
    commodity = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    region = Column(String, nullable=False)
    counterparty = Column(String, nullable=False)
    trade_date = Column(DateTime(timezone=True), nullable=False)
    settlement_date = Column(DateTime(timezone=True))
    currency = Column(String, default="USD")
    trade_type = Column(String, default="spot")
    status = Column(String, default="pending")
    description = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class TradeAllocation(Base):
    __tablename__ = "trade_allocations"

    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(Integer, nullable=False)
    allocation_type = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class TradeSettlement(Base):
    __tablename__ = "trade_settlements"

    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(Integer, nullable=False)
    settlement_amount = Column(Float, nullable=False)
    settlement_currency = Column(String, default="USD")
    settlement_date = Column(DateTime(timezone=True), nullable=False)
    settlement_status = Column(String, default="pending")
    timestamp = Column(DateTime(timezone=True), server_default=func.now())