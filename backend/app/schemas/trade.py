"""
Trade Schema - ETRM/CTRM Trade Models
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class TradeStatus(str, Enum):
    PENDING = "pending"
    CAPTURED = "captured"
    CONFIRMED = "confirmed"
    SETTLED = "settled"
    CANCELLED = "cancelled"

class TradeCapture(BaseModel):
    asset: str
    volume: float
    price: float
    region: str

class TradeCreate(BaseModel):
    """Schema for creating new trades"""
    commodity: str
    asset: str
    volume: float
    price: float
    region: str
    counterparty: str
    trade_date: datetime
    settlement_date: Optional[datetime] = None
    currency: str = "USD"
    trade_type: str = "spot"
    description: Optional[str] = None

class TradeUpdate(BaseModel):
    """Schema for updating existing trades"""
    volume: Optional[float] = None
    price: Optional[float] = None
    settlement_date: Optional[datetime] = None
    status: Optional[TradeStatus] = None
    description: Optional[str] = None

class TradeResponse(BaseModel):
    """Schema for trade API responses"""
    trade_id: str
    status: str
    message: str
    timestamp: str
    data: Optional[Dict[str, Any]] = None


class ApiResponse(BaseModel):
    """Standard API response schema"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: str
    timestamp: Optional[str] = None