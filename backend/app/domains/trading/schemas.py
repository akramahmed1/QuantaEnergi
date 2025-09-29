"""
Trading Domain Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class TradeDirection(str, Enum):
    BUY = "buy"
    SELL = "sell"

class TradeCreate(BaseModel):
    asset: str = Field(..., description="Trading asset")
    quantity: float = Field(..., gt=0, description="Trade quantity")
    price: float = Field(..., gt=0, description="Trade price")
    direction: TradeDirection = Field(TradeDirection.BUY, description="Trade direction")
    counterparty: Optional[str] = Field(None, description="Counterparty")
    is_sharia_compliant: bool = Field(True, description="Sharia compliance")

class TradeResponse(BaseModel):
    success: bool
    trade_id: str
    position_id: str
    trade: Dict[str, Any]
    position: Dict[str, Any]

class PositionResponse(BaseModel):
    position_id: str
    asset: str
    quantity: float
    entry_price: float
    current_price: Optional[float]
    unrealized_pnl: float
    currency: str

class PnLResponse(BaseModel):
    success: bool
    position_id: str
    unrealized_pnl: float
    pnl_percentage: float
    current_price: float
    entry_price: float

class PortfolioSummary(BaseModel):
    success: bool
    total_positions: int
    total_value: float
    total_pnl: float
    pnl_percentage: float
    positions: List[Dict[str, Any]]
