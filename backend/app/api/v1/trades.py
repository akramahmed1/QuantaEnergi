"""
Trading API endpoints for ETRM/CTRM operations
Handles deal capture, position management, and trading operations
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

from app.services.deal_capture import DealCaptureService, DealValidationService
from app.services.position_manager import PositionManager
from app.services.sharia import ShariaScreeningEngine, IslamicTradingValidator
from app.schemas.trade import TradeCreate, TradeUpdate, TradeResponse, PositionResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/trades", tags=["trading"])

# Initialize services
deal_service = DealCaptureService()
deal_validator = DealValidationService()
position_manager = PositionManager()
sharia_engine = ShariaScreeningEngine()
islamic_validator = IslamicTradingValidator()


@router.post("/deals/capture", response_model=TradeResponse)
async def capture_deal(deal: TradeCreate):
    """
    Capture a new trading deal with Islamic compliance validation
    """
    try:
        # Validate deal data
        validation_result = deal_validator.validate_deal_data(deal.dict())
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Deal validation failed: {validation_result['errors']}"
            )
        
        # Check Islamic compliance
        commodity_data = {"type": deal.commodity}
        sharia_result = sharia_engine.screen_commodity(commodity_data)
        
        if not sharia_result["compliant"]:
            raise HTTPException(
                status_code=400,
                detail=f"Sharia compliance failed: {sharia_result['reason']}"
            )
        
        # Validate trading structure
        trade_data = {
            "interest_rate": 0,  # Islamic finance - no interest
            "asset_backing_ratio": 1.0  # Full asset backing
        }
        structure_result = sharia_engine.validate_trading_structure(trade_data)
        
        if not structure_result["compliant"]:
            raise HTTPException(
                status_code=400,
                detail=f"Trading structure validation failed: {structure_result['reason']}"
            )
        
        # Capture deal
        deal_data = deal.dict()
        deal_data["sharia_compliant"] = True
        
        result = deal_service.capture_deal(deal_data)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Create position
        position_result = position_manager.create_position(result["deal"])
        
        return TradeResponse(
            trade_id=result["deal_id"],
            status="captured",
            message="Deal captured successfully",
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error capturing deal: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/deals/{deal_id}", response_model=Dict[str, Any])
async def get_deal(deal_id: str):
    """
    Retrieve deal by ID
    """
    try:
        deal = deal_service.get_deal(deal_id)
        if not deal:
            raise HTTPException(status_code=404, detail="Deal not found")
        
        return deal
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving deal: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/deals/{deal_id}", response_model=Dict[str, Any])
async def update_deal(deal_id: str, updates: TradeUpdate):
    """
    Update existing deal
    """
    try:
        result = deal_service.update_deal(deal_id, updates.dict(exclude_unset=True))
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating deal: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/deals", response_model=List[Dict[str, Any]])
async def list_deals(
    commodity: Optional[str] = Query(None, description="Filter by commodity"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, description="Maximum number of deals to return")
):
    """
    List deals with optional filtering
    """
    try:
        filters = {}
        if commodity:
            filters["commodity"] = commodity
        if status:
            filters["status"] = status
        
        deals = deal_service.list_deals(filters)
        return deals[:limit]
        
    except Exception as e:
        logger.error(f"Error listing deals: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/positions/{position_id}", response_model=Dict[str, Any])
async def get_position(position_id: str):
    """
    Retrieve position by ID
    """
    try:
        position = position_manager.get_position(position_id)
        if not position:
            raise HTTPException(status_code=404, detail="Position not found")
        
        return position
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving position: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/positions/{position_id}/close")
async def close_position(
    position_id: str,
    exit_price: float = Query(..., description="Exit price for position"),
    exit_quantity: Optional[float] = Query(None, description="Quantity to close (None for full close)")
):
    """
    Close or partially close a position
    """
    try:
        result = position_manager.close_position(position_id, exit_price, exit_quantity)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error closing position: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/positions/{position_id}/pnl")
async def calculate_pnl(
    position_id: str,
    current_price: float = Query(..., description="Current market price")
):
    """
    Calculate P&L for position
    """
    try:
        result = position_manager.calculate_pnl(position_id, current_price)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating P&L: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/portfolio/summary")
async def get_portfolio_summary():
    """
    Get portfolio summary
    """
    try:
        summary = position_manager.get_portfolio_summary()
        return summary
        
    except Exception as e:
        logger.error(f"Error getting portfolio summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/sharia/screen")
async def screen_commodity(commodity_data: Dict[str, Any]):
    """
    Screen commodity for Sharia compliance
    """
    try:
        result = sharia_engine.screen_commodity(commodity_data)
        return result
        
    except Exception as e:
        logger.error(f"Error screening commodity: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/sharia/validate-structure")
async def validate_trading_structure(trade_data: Dict[str, Any]):
    """
    Validate trading structure for Islamic compliance
    """
    try:
        result = sharia_engine.validate_trading_structure(trade_data)
        return result
        
    except Exception as e:
        logger.error(f"Error validating trading structure: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/sharia/zakat")
async def calculate_zakat(portfolio_value: float = Query(..., description="Portfolio value for Zakat calculation")):
    """
    Calculate Zakat obligation
    """
    try:
        result = sharia_engine.calculate_zakat_obligation(portfolio_value)
        return result
        
    except Exception as e:
        logger.error(f"Error calculating Zakat: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/islamic/validate-murabaha")
async def validate_murabaha_contract(contract_data: Dict[str, Any]):
    """
    Validate Murabaha contract
    """
    try:
        result = islamic_validator.validate_murabaha_contract(contract_data)
        return result
        
    except Exception as e:
        logger.error(f"Error validating Murabaha contract: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/islamic/check-gharar")
async def check_gharar_level(trade_data: Dict[str, Any]):
    """
    Check Gharar level in trade
    """
    try:
        result = islamic_validator.check_gharar_level(trade_data)
        return result
        
    except Exception as e:
        logger.error(f"Error checking Gharar level: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
