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

class MetalsTrade(Base):
    __tablename__ = "metals_trades"

    id = Column(Integer, primary_key=True, index=True)
    metal_type = Column(String, nullable=False)  # gold, silver, copper, etc.
    quantity = Column(Float, nullable=False)
    unit = Column(String, default="oz")  # ounces, tonnes, etc.
    price_per_unit = Column(Float, nullable=False)
    total_value = Column(Float, nullable=False)
    purity = Column(Float)  # for precious metals
    storage_location = Column(String)
    delivery_date = Column(DateTime(timezone=True))
    counterparty = Column(String, nullable=False)
    trade_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, default="pending")
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class AgriculturalTrade(Base):
    __tablename__ = "agricultural_trades"

    id = Column(Integer, primary_key=True, index=True)
    commodity_type = Column(String, nullable=False)  # wheat, corn, soybeans, etc.
    quantity = Column(Float, nullable=False)
    unit = Column(String, default="bushel")  # bushels, tonnes, etc.
    price_per_unit = Column(Float, nullable=False)
    total_value = Column(Float, nullable=False)
    grade = Column(String)  # commodity grade
    origin = Column(String)  # country/region of origin
    delivery_location = Column(String)
    delivery_date = Column(DateTime(timezone=True))
    counterparty = Column(String, nullable=False)
    trade_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, default="pending")
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class DerivativesTrade(Base):
    __tablename__ = "derivatives_trades"

    id = Column(Integer, primary_key=True, index=True)
    derivative_type = Column(String, nullable=False)  # futures, options, swaps, forwards
    underlying_asset = Column(String, nullable=False)
    contract_size = Column(Float, nullable=False)
    strike_price = Column(Float)  # for options
    premium = Column(Float)  # for options
    expiry_date = Column(DateTime(timezone=True))
    settlement_date = Column(DateTime(timezone=True))
    counterparty = Column(String, nullable=False)
    trade_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, default="pending")
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class PPATrade(Base):
    __tablename__ = "ppa_trades"

    id = Column(Integer, primary_key=True, index=True)
    ppa_type = Column(String, nullable=False)  # fixed_price, indexed_price, hybrid, virtual, physical
    capacity_mw = Column(Float, nullable=False)
    contract_duration_years = Column(Integer, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    fixed_price = Column(Float)
    indexed_price_formula = Column(Text)
    escalation_rate = Column(Float, default=0.0)
    availability_factor = Column(Float, default=0.95)
    counterparty = Column(String, nullable=False)
    counterparty_rating = Column(String, default="BBB")
    credit_limit = Column(Float, default=1000000.0)
    trade_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, default="pending")
    timestamp = Column(DateTime(timezone=True), server_default=func.now())