"""
Trading Domain Models
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from ..base import Base

class TradeStatus(PyEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SETTLED = "settled"
    CANCELLED = "cancelled"

class TradeType(PyEnum):
    SPOT = "spot"
    FORWARD = "forward"
    FUTURES = "futures"
    SWAP = "swap"
    OPTION = "option"

class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(String, unique=True, index=True, nullable=False)
    asset = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    trade_type = Column(Enum(TradeType), default=TradeType.SPOT)
    status = Column(Enum(TradeStatus), default=TradeStatus.PENDING)
    direction = Column(String, nullable=False)  # buy/sell
    currency = Column(String, default="USD")
    counterparty = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_sharia_compliant = Column(Boolean, default=True)
    
    # Relationships
    positions = relationship("Position", back_populates="trade")
    settlements = relationship("Settlement", back_populates="trade")

class Position(Base):
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    position_id = Column(String, unique=True, index=True, nullable=False)
    trade_id = Column(Integer, nullable=False)
    asset = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    current_price = Column(Float)
    unrealized_pnl = Column(Float, default=0.0)
    realized_pnl = Column(Float, default=0.0)
    currency = Column(String, default="USD")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    trade = relationship("Trade", back_populates="positions")

class Settlement(Base):
    __tablename__ = "settlements"
    
    id = Column(Integer, primary_key=True, index=True)
    settlement_id = Column(String, unique=True, index=True, nullable=False)
    trade_id = Column(Integer, nullable=False)
    settlement_amount = Column(Float, nullable=False)
    settlement_date = Column(DateTime, nullable=False)
    currency = Column(String, default="USD")
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    trade = relationship("Trade", back_populates="settlements")
