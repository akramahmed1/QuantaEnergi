"""
Shared Pydantic Models for QuantaEnergi Platform
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class TradeDirection(str, Enum):
    BUY = "buy"
    SELL = "sell"

class TradeType(str, Enum):
    SPOT = "spot"
    FORWARD = "forward"
    FUTURES = "futures"
    OPTIONS = "options"
    SWAP = "swap"

class TradeStatus(str, Enum):
    CAPTURED = "captured"
    VALIDATED = "validated"
    CONFIRMED = "confirmed"
    ALLOCATED = "allocated"
    SETTLED = "settled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TradeCreate(BaseModel):
    """Trade creation model"""
    trade_type: TradeType
    commodity: str = Field(..., description="Commodity type (crude_oil, natural_gas, electricity)")
    quantity: float = Field(..., gt=0, description="Trade quantity")
    price: float = Field(..., gt=0, description="Trade price per unit")
    currency: str = Field(default="USD", description="Currency code")
    counterparty_id: str = Field(..., description="Counterparty identifier")
    counterparty_name: str = Field(..., description="Counterparty name")
    delivery_date: datetime = Field(..., description="Delivery date")
    delivery_location: str = Field(..., description="Delivery location")
    trade_direction: TradeDirection
    settlement_type: str = Field(default="T+2", description="Settlement type")
    is_islamic_compliant: bool = Field(default=False, description="Islamic compliance flag")
    trade_data: Optional[Dict[str, Any]] = Field(default=None, description="Additional trade data")

class TradeUpdate(BaseModel):
    """Trade update model"""
    status: Optional[TradeStatus] = None
    price: Optional[float] = Field(None, gt=0)
    quantity: Optional[float] = Field(None, gt=0)
    delivery_date: Optional[datetime] = None
    trade_data: Optional[Dict[str, Any]] = None

class TradeResponse(BaseModel):
    """Trade response model"""
    id: str
    trade_id: str
    trade_type: TradeType
    commodity: str
    quantity: float
    price: float
    currency: str
    counterparty_id: str
    counterparty_name: str
    delivery_date: datetime
    delivery_location: str
    trade_direction: TradeDirection
    settlement_type: str
    status: TradeStatus
    is_islamic_compliant: bool
    notional_value: float
    created_at: datetime
    updated_at: datetime

class TradeValidation(BaseModel):
    """Trade validation model"""
    trade_id: str
    is_valid: bool
    validation_errors: List[str] = Field(default_factory=list)
    sharia_compliant: bool = Field(default=False)
    compliance_notes: Optional[str] = None

class TradeSettlement(BaseModel):
    """Trade settlement model"""
    trade_id: str
    settlement_amount: float
    settlement_currency: str = Field(default="USD")
    settlement_type: str
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None
    settlement_date: Optional[datetime] = None
    status: str = Field(default="pending")

class UserLogin(BaseModel):
    """User login model"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)

class UserRegister(BaseModel):
    """User registration model"""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., description="Valid email address")
    password: str = Field(..., min_length=6, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=100)
    organization: str = Field(..., min_length=2, max_length=100)

class TokenResponse(BaseModel):
    """JWT token response model"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    username: str

class ApiResponse(BaseModel):
    """Generic API response model"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None

class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    message: str
    errors: List[str] = Field(default_factory=list)
    error_code: Optional[str] = None
