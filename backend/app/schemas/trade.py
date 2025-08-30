from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class TradeType(str, Enum):
    BUY = "buy"
    SELL = "sell"
    SHORT = "short"
    COVER = "cover"

class EnergyCommodity(str, Enum):
    CRUDE_OIL = "crude_oil"
    NATURAL_GAS = "natural_gas"
    COAL = "coal"
    RENEWABLES = "renewables"
    ELECTRICITY = "electricity"

class TradeStatus(str, Enum):
    PENDING = "pending"
    EXECUTED = "executed"
    CANCELLED = "cancelled"
    FAILED = "failed"

class Trade(BaseModel):
    """Energy trading model with comprehensive validation"""
    
    id: Optional[str] = Field(None, description="Unique trade identifier")
    user_id: str = Field(..., description="User who initiated the trade")
    trade_type: TradeType = Field(..., description="Type of trade")
    commodity: EnergyCommodity = Field(..., description="Energy commodity being traded")
    quantity: float = Field(..., gt=0, description="Quantity in standard units")
    price_per_unit: float = Field(..., gt=0, description="Price per unit")
    total_value: float = Field(..., gt=0, description="Total trade value")
    region: str = Field(..., description="Trading region")
    status: TradeStatus = Field(default=TradeStatus.PENDING, description="Current trade status")
    
    # ESG and compliance fields
    esg_score: Optional[float] = Field(None, ge=0, le=100, description="ESG score")
    compliance_verified: bool = Field(default=False, description="Compliance verification status")
    carbon_offset: Optional[float] = Field(None, ge=0, description="Carbon offset amount")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Trade creation time")
    executed_at: Optional[datetime] = Field(None, description="Trade execution time")
    expires_at: Optional[datetime] = Field(None, description="Trade expiration time")
    
    # Risk management
    stop_loss: Optional[float] = Field(None, gt=0, description="Stop loss price")
    take_profit: Optional[float] = Field(None, gt=0, description="Take profit price")
    risk_score: Optional[float] = Field(None, ge=0, le=100, description="Risk assessment score")
    
    # Additional metadata
    notes: Optional[str] = Field(None, max_length=500, description="Trade notes")
    tags: List[str] = Field(default_factory=list, description="Trade tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('total_value')
    def validate_total_value(cls, v, values):
        """Ensure total value matches quantity * price"""
        if 'quantity' in values and 'price_per_unit' in values:
            expected = values['quantity'] * values['price_per_unit']
            if abs(v - expected) > 0.01:  # Allow small rounding differences
                raise ValueError(f"Total value {v} must equal quantity * price_per_unit ({expected})")
        return v
    
    @validator('expires_at')
    def validate_expires_at(cls, v, values):
        """Ensure expiration is in the future"""
        if v and v <= datetime.utcnow():
            raise ValueError("Expiration time must be in the future")
        return v
    
    @validator('stop_loss', 'take_profit')
    def validate_stop_loss_take_profit(cls, v, values):
        """Validate stop loss and take profit logic"""
        if 'price_per_unit' in values and v:
            if 'trade_type' in values:
                if values['trade_type'] in [TradeType.BUY, TradeType.COVER]:
                    # For long positions, stop loss should be below entry price
                    if v >= values['price_per_unit']:
                        raise ValueError("Stop loss for long positions must be below entry price")
                elif values['trade_type'] in [TradeType.SELL, TradeType.SHORT]:
                    # For short positions, stop loss should be above entry price
                    if v <= values['price_per_unit']:
                        raise ValueError("Stop loss for short positions must be above entry price")
        return v
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "user_id": "user123",
                "trade_type": "buy",
                "commodity": "crude_oil",
                "quantity": 1000.0,
                "price_per_unit": 85.50,
                "total_value": 85500.0,
                "region": "US",
                "esg_score": 75.0,
                "compliance_verified": True,
                "stop_loss": 80.0,
                "take_profit": 90.0,
                "risk_score": 25.0,
                "notes": "Strategic position based on AI forecast",
                "tags": ["AI-driven", "strategic", "ESG-focused"]
            }
        }

class TradeCreate(BaseModel):
    """Model for creating new trades"""
    trade_type: TradeType
    commodity: EnergyCommodity
    quantity: float = Field(..., gt=0)
    price_per_unit: float = Field(..., gt=0)
    region: str
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    notes: Optional[str] = None
    tags: List[str] = []

class TradeUpdate(BaseModel):
    """Model for updating existing trades"""
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[TradeStatus] = None

class TradeResponse(BaseModel):
    """Model for trade responses"""
    trade: Trade
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
