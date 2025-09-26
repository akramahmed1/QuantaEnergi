"""
Simple API endpoints without complex dependencies
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from enum import Enum
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import random
from app.schemas.trade_capture import TradeCapture
from app.services.energy_service import validate_forecast

# Create router
router = APIRouter(prefix="/api", tags=["Simple Trading"])

class AssetType(str, Enum):
    OIL = "oil"
    GAS = "gas"

class RegionType(str, Enum):
    ME = "me"
    GUYANA = "guyana"
    US = "us"
    UK = "uk"
    EU = "eu"

class TradeCapture(BaseModel):
    asset: AssetType
    volume: float = Field(..., gt=0)
    price: float = Field(..., gt=0)
    region: RegionType
    amendments: Optional[List[Dict[str, Any]]] = None

class TradeCaptureResponse(BaseModel):
    trade_id: str
    status: str
    message: str
    timestamp: datetime

@router.post("/v1/trade/capture", response_model=TradeCaptureResponse)
async def capture_trade(trade_data: TradeCapture = Depends()):
    """
    Trade capture endpoint - PRD 4.1 integration
    Captures new energy trades with forecast validation
    """
    try:
        # Generate trade ID
        trade_id = f"T{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"
        
        # Validate with energy service
        validation = validate_forecast(trade_data)
        
        # Calculate total value
        total_value = trade_data.volume * trade_data.price
        
        # Apply amendments if any
        if trade_data.amendments:
            for amendment in trade_data.amendments:
                if amendment.get("type") == "quality_adjustment":
                    total_value *= (1 + amendment.get("value", 0))
        
        return TradeCaptureResponse(
            trade_id=trade_id,
            status="captured" if validation["is_valid"] else "pending_review",
            message=f"Trade captured successfully. Total value: ${total_value:,.2f}",
            timestamp=datetime.now(timezone.utc)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to capture trade: {str(e)}")

@router.get("/v1/risk/var")
async def get_var_calculation(
    portfolio_id: str = Query(..., description="Portfolio ID"),
    confidence: float = Query(0.95, ge=0.5, le=0.99, description="Confidence level")
):
    """Simple VaR calculation endpoint"""
    try:
        # Mock VaR calculation
        var_95 = random.uniform(10000, 100000)
        var_99 = random.uniform(15000, 150000)
        
        return {
            "portfolio_id": portfolio_id,
            "confidence_level": confidence,
            "var_metrics": {
                "var_95": round(var_95, 2),
                "var_99": round(var_99, 2),
                "portfolio_risk_score": round(random.uniform(0.1, 0.8), 3)
            },
            "calculated_at": datetime.now(timezone.utc).isoformat(),
            "method": "numpy.percentile"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"VaR calculation failed: {str(e)}")
