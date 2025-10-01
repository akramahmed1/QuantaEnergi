"""
Trade Schema - ETRM/CTRM Trade Models
"""

from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class TradeStatus(str, Enum):
    PENDING = "pending"
    CAPTURED = "captured"
    CONFIRMED = "confirmed"
    SETTLED = "settled"
    CANCELLED = "cancelled"

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

class TradeRequest(BaseModel):
    """Schema for trade requests with conditional validation"""
    commodity: str
    asset: str
    volume: float
    order_type: OrderType = OrderType.MARKET
    price: Optional[float] = None
    region: str
    counterparty: str
    trade_date: datetime
    settlement_date: Optional[datetime] = None
    currency: str = "USD"
    trade_type: str = "spot"
    description: Optional[str] = None

    @validator('price')
    def validate_price_for_limit_orders(cls, v, values):
        """Validate that price is required for LIMIT orders"""
        order_type = values.get('order_type')
        if order_type == OrderType.LIMIT and v is None:
            raise ValueError('Price is required for LIMIT orders')
        if order_type == OrderType.STOP_LIMIT and v is None:
            raise ValueError('Price is required for STOP_LIMIT orders')
        return v

    @validator('volume')
    def validate_volume(cls, v):
        """Validate volume is positive"""
        if v <= 0:
            raise ValueError('Volume must be positive')
        return v

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