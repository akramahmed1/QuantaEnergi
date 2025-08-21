from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Enum, Numeric, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
import uuid
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import UUID

Base = declarative_base()

# Base class for all tenant-scoped models
class CompanyScopedModel(Base):
    """Base class for all models that require company-level data isolation."""
    __abstract__ = True
    
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("companies.id"), nullable=False, index=True
    )
    company: Mapped["Company"] = relationship("Company", back_populates="entities")

class User(CompanyScopedModel):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    last_login = Column(DateTime)
    region = Column(String)
    # company_id and company relationship inherited from CompanyScopedModel

class Company(Base):
    __tablename__ = "companies"
    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    registration_number = Column(String, unique=True)
    country = Column(String, nullable=False)
    region = Column(String, nullable=False)
    industry = Column(String)
    created_at = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships to all tenant-scoped entities
    entities = relationship("CompanyScopedModel", back_populates="company")
    users = relationship("User", back_populates="company")
    contracts = relationship("Contract", back_populates="company")
    trades = relationship("Trade", back_populates="company")
    positions = relationship("Position", back_populates="company")
    risk_metrics = relationship("RiskMetrics", back_populates="company")
    compliance_records = relationship("Compliance", back_populates="company")
    market_data = relationship("MarketData", back_populates="company")
    settlements = relationship("Settlement", back_populates="company")

class EmissionFactor(Base):
    __tablename__ = "emission_factors"
    id = Column(Integer, primary_key=True)
    fuel_type = Column(String, nullable=False)
    emission_factor = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    region = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())

class Contract(CompanyScopedModel):
    __tablename__ = "contracts"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    contract_number = Column(String, unique=True)
    contract_type = Column(String)
    counterparty_id = Column(String, ForeignKey("counterparties.id"))
    commodity = Column(String)
    delivery_location = Column(String)
    delivery_period_start = Column(DateTime)
    delivery_period_end = Column(DateTime)
    quantity = Column(Float)
    unit = Column(String)
    price = Column(Numeric(10, 2))
    currency = Column(String)
    status = Column(String)
    compliance_flags = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    # company_id and company relationship inherited from CompanyScopedModel
    
    # Additional relationships
    counterparty = relationship("Counterparty", back_populates="contracts")
    trades = relationship("Trade", back_populates="contract")

class Counterparty(CompanyScopedModel):
    __tablename__ = "counterparties"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    type = Column(String)  # customer, supplier, broker
    country = Column(String)
    credit_rating = Column(String)
    created_at = Column(DateTime, default=func.now())
    # company_id and company relationship inherited from CompanyScopedModel
    
    # Relationships
    contracts = relationship("Contract", back_populates="counterparty")

class Trade(CompanyScopedModel):
    __tablename__ = "trades"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    trade_id = Column(String, unique=True)
    contract_id = Column(String, ForeignKey("contracts.id"))
    trader_id = Column(Integer, ForeignKey("users.id"))
    side = Column(String)  # buy, sell
    quantity = Column(Float)
    price = Column(Numeric(10, 2))
    trade_date = Column(DateTime)
    status = Column(String)  # executed, pending, cancelled
    region = Column(String)
    created_at = Column(DateTime, default=func.now())
    # company_id and company relationship inherited from CompanyScopedModel
    
    # Relationships
    contract = relationship("Contract", back_populates="trades")
    trader = relationship("User")

class Position(CompanyScopedModel):
    __tablename__ = "positions"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    contract_id = Column(String, ForeignKey("contracts.id"))
    trader_id = Column(Integer, ForeignKey("users.id"))
    quantity = Column(Float)
    average_price = Column(Numeric(10, 2))
    mark_to_market = Column(Numeric(10, 2))
    unrealized_pnl = Column(Numeric(10, 2))
    region = Column(String)
    created_at = Column(DateTime, default=func.now())
    # company_id and company relationship inherited from CompanyScopedModel
    
    # Relationships
    contract = relationship("Contract")
    trader = relationship("User")

class RiskMetrics(CompanyScopedModel):
    __tablename__ = "risk_metrics"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    portfolio_id = Column(String)
    var_95 = Column(Float)
    var_99 = Column(Float)
    expected_shortfall = Column(Float)
    stress_test_result = Column(Float)
    correlation_matrix = Column(JSON)
    region = Column(String)
    calculation_date = Column(DateTime, default=func.now())
    # company_id and company relationship inherited from CompanyScopedModel

class Compliance(CompanyScopedModel):
    __tablename__ = "compliance"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    regulation_name = Column(String)
    compliance_status = Column(String)
    last_check_date = Column(DateTime)
    next_check_date = Column(DateTime)
    violations = Column(JSON)
    region = Column(String)
    created_at = Column(DateTime, default=func.now())
    # company_id and company relationship inherited from CompanyScopedModel

class MarketData(CompanyScopedModel):
    __tablename__ = "market_data"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol = Column(String)
    price = Column(Float)
    volume = Column(Float)
    timestamp = Column(DateTime)
    source = Column(String)
    region = Column(String)
    created_at = Column(DateTime, default=func.now())
    # company_id and company relationship inherited from CompanyScopedModel

class Settlement(CompanyScopedModel):
    __tablename__ = "settlements"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    trade_id = Column(String, ForeignKey("trades.id"))
    settlement_date = Column(DateTime)
    settlement_amount = Column(Numeric(10, 2))
    currency = Column(String)
    status = Column(String)
    region = Column(String)
    created_at = Column(DateTime, default=func.now())
    # company_id and company relationship inherited from CompanyScopedModel
    
    # Relationships
    trade = relationship("Trade")

class AuditTrail(CompanyScopedModel):
    __tablename__ = "audit_trail"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)
    table_name = Column(String)
    record_id = Column(String)
    old_values = Column(JSON)
    new_values = Column(JSON)
    timestamp = Column(DateTime, default=func.now())
    ip_address = Column(String)
    # company_id and company relationship inherited from CompanyScopedModel
    
    # Relationships
    user = relationship("User")

class RegionalCompliance(Base):
    __tablename__ = "regional_compliance"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    region = Column(String, nullable=False)
    regulation_name = Column(String, nullable=False)
    regulation_version = Column(String)
    effective_date = Column(DateTime)
    requirements = Column(JSON)
    penalties = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())