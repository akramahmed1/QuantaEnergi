"""
Trade Model for Multi-Tenant ETRM/CTRM Database
Supports organization isolation and comprehensive trade lifecycle management
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, String, DateTime, Boolean, JSON, Text, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uuid
import logging

from ..db.database import Base

logger = logging.getLogger(__name__)

class Trade(Base):
    """Trade model for multi-tenant ETRM/CTRM operations"""
    
    __tablename__ = "trades"
    
    # Primary key and organization isolation
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(PG_UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Trade identification
    trade_id = Column(String(100), unique=True, nullable=False, index=True)
    external_trade_id = Column(String(100), nullable=True)
    
    # Trade details
    trade_type = Column(String(50), nullable=False)  # spot, forward, futures, options, swap
    commodity = Column(String(50), nullable=False)   # crude_oil, natural_gas, electricity, etc.
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    
    # Counterparty information
    counterparty_id = Column(String(100), nullable=False)
    counterparty_name = Column(String(255), nullable=True)
    
    # Delivery information
    delivery_date = Column(DateTime, nullable=False)
    delivery_location = Column(String(255), nullable=False)
    delivery_term = Column(String(50), default="FOB")  # FOB, CIF, EXW, etc.
    
    # Trade direction and settlement
    trade_direction = Column(String(10), nullable=False)  # buy, sell
    settlement_type = Column(String(20), default="T+2")   # T+0, T+1, T+2, etc.
    settlement_date = Column(DateTime, nullable=True)
    
    # Islamic finance compliance
    is_islamic_compliant = Column(Boolean, default=False)
    sharia_approval = Column(String(255), nullable=True)
    islamic_compliance_notes = Column(Text, nullable=True)
    
    # Risk and compliance
    risk_category = Column(String(50), nullable=True)
    compliance_status = Column(String(50), default="pending")
    compliance_notes = Column(Text, nullable=True)
    
    # Trade lifecycle status
    status = Column(String(50), default="captured")  # captured, validated, confirmed, allocated, settled, completed
    lifecycle_stage = Column(String(50), default="capture")
    
    # Financial details
    notional_value = Column(Float, nullable=False)
    margin_requirement = Column(Float, default=0.0)
    commission = Column(Float, default=0.0)
    fees = Column(Float, default=0.0)
    
    # Additional data
    trade_data = Column(JSON, nullable=True)  # Flexible JSON for additional trade-specific data
    system_metadata = Column(JSON, nullable=True)    # System metadata
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String(100), nullable=False)
    updated_by = Column(String(100), nullable=True)
    
    # Soft delete
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(String(100), nullable=True)
    
    # Relationships - will be set up after Organization model is defined
    # organization = relationship("Organization", back_populates="trades")
    
    def __repr__(self):
        return f"<Trade(id={self.id}, trade_id='{self.trade_id}', commodity='{self.commodity}')>"
    
    @property
    def is_active(self) -> bool:
        """Check if trade is active (not deleted)"""
        return not self.is_deleted
    
    @property
    def net_value(self) -> float:
        """Calculate net trade value after fees"""
        return self.notional_value - self.commission - self.fees
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert trade to dictionary"""
        return {
            "id": str(self.id),
            "trade_id": self.trade_id,
            "organization_id": str(self.organization_id),
            "trade_type": self.trade_type,
            "commodity": self.commodity,
            "quantity": self.quantity,
            "price": self.price,
            "currency": self.currency,
            "counterparty_id": self.counterparty_id,
            "counterparty_name": self.counterparty_name,
            "delivery_date": self.delivery_date.isoformat() if self.delivery_date else None,
            "delivery_location": self.delivery_location,
            "trade_direction": self.trade_direction,
            "settlement_type": self.settlement_type,
            "is_islamic_compliant": self.is_islamic_compliant,
            "status": self.status,
            "notional_value": self.notional_value,
            "net_value": self.net_value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

class TradeAllocation(Base):
    """Trade allocation model for position management"""
    
    __tablename__ = "trade_allocations"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trade_id = Column(PG_UUID(as_uuid=True), ForeignKey("trades.id"), nullable=False)
    organization_id = Column(PG_UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    
    # Allocation details
    allocation_type = Column(String(50), nullable=False)  # physical, financial, hedge
    allocated_quantity = Column(Float, nullable=False)
    allocated_price = Column(Float, nullable=False)
    allocation_percentage = Column(Float, nullable=False)
    
    # Allocation metadata
    allocation_notes = Column(Text, nullable=True)
    allocation_data = Column(JSON, nullable=True)
    
    # Status and timing
    status = Column(String(50), default="pending")
    allocated_at = Column(DateTime, default=datetime.utcnow)
    allocated_by = Column(String(100), nullable=False)
    
    # Relationships - will be set up after models are defined
    # trade = relationship("Trade")
    # organization = relationship("Organization")
    
    def __repr__(self):
        return f"<TradeAllocation(id={self.id}, trade_id={self.trade_id}, type='{self.allocation_type}')>"

class TradeSettlement(Base):
    """Trade settlement model for payment processing"""
    
    __tablename__ = "trade_settlements"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trade_id = Column(PG_UUID(as_uuid=True), ForeignKey("trades.id"), nullable=False)
    organization_id = Column(PG_UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    
    # Settlement details
    settlement_amount = Column(Float, nullable=False)
    settlement_currency = Column(String(10), default="USD")
    settlement_type = Column(String(50), nullable=False)  # cash, physical, netting
    
    # Payment information
    payment_method = Column(String(50), nullable=True)  # wire_transfer, ach, check
    payment_reference = Column(String(255), nullable=True)
    payment_date = Column(DateTime, nullable=True)
    
    # Settlement status
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    settlement_notes = Column(Text, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100), nullable=False)
    
    # Relationships - will be set up after models are defined
    # trade = relationship("Trade")
    # organization = relationship("Organization")
    
    def __repr__(self):
        return f"<TradeSettlement(id={self.id}, trade_id={self.trade_id}, amount={self.settlement_amount})>"
