"""
Trading Domain API Routers
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from ..base import get_db
from .services import TradingService, PositionManager
from .schemas import TradeCreate, TradeResponse, PositionResponse

router = APIRouter(prefix="/trading", tags=["Trading"])

@router.post("/trades", response_model=TradeResponse)
async def create_trade(
    trade_data: TradeCreate,
    db: Session = Depends(get_db)
):
    """Create a new trade with real P&L calculations"""
    trading_service = TradingService(db)
    result = trading_service.create_trade(trade_data.dict())
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return TradeResponse(**result)

@router.get("/positions/{position_id}/pnl")
async def get_position_pnl(
    position_id: str,
    current_price: float = Query(..., description="Current market price"),
    db: Session = Depends(get_db)
):
    """Calculate real P&L for position"""
    trading_service = TradingService(db)
    result = trading_service.calculate_real_pnl(position_id, current_price)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

@router.get("/portfolio/summary")
async def get_portfolio_summary(
    user_id: str = Query(None, description="User ID filter"),
    db: Session = Depends(get_db)
):
    """Get portfolio summary with real calculations"""
    trading_service = TradingService(db)
    result = trading_service.get_portfolio_summary(user_id)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result

@router.post("/positions/reconcile")
async def reconcile_positions(
    db: Session = Depends(get_db)
):
    """Reconcile all positions with current market data"""
    position_manager = PositionManager(db)
    result = position_manager.reconcile_positions()
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result
