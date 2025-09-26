"""
Energy Service - Mock gRPC validation for trade capture
"""

from typing import Dict, Any
from app.schemas.trade_capture import TradeCapture

def validate_forecast(trade: TradeCapture) -> Dict[str, Any]:
    """
    Mock forecast validation function
    Returns validation result for trade capture
    """
    # Mock validation - always returns valid for now
    return {
        "is_valid": True,
        "forecast_price": trade.price * 1.02,  # 2% higher than trade price
        "confidence": 0.85,
        "message": "Forecast validation passed (mock)"
    }
