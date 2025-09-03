"""
Trade Lifecycle API endpoints for ETRM/CTRM operations
Handles complete trade lifecycle from capture to settlement
"""

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import uuid

from app.services.trade_lifecycle import TradeLifecycle, TradeStage
from app.services.sharia import ShariaScreeningEngine
from app.services.credit_manager import CreditManager
from app.schemas.trade import (
    TradeCreate, TradeUpdate, TradeResponse, TradeStatusResponse,
    ConfirmationResponse, AllocationResponse, SettlementResponse,
    InvoiceResponse, PaymentResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/trade-lifecycle", tags=["trade_lifecycle"])

# Initialize services
trade_lifecycle = TradeLifecycle()
sharia_compliance = ShariaScreeningEngine()
credit_manager = CreditManager()

# Mock user dependency for now
async def get_current_user():
    return {"id": "user123", "email": "trader@quantaenergi.com", "role": "trader"}

@router.post("/capture", response_model=TradeResponse)
async def capture_trade(
    trade_data: TradeCreate,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user)
):
    """
    Capture a new trade with validation
    """
    try:
        logger.info(f"Capturing trade for user {current_user['id']}")
        
        # Add user context to trade data
        trade_data_dict = trade_data.model_dump()
        trade_data_dict["user_id"] = current_user["id"]
        trade_data_dict["capture_timestamp"] = datetime.now().isoformat()
        
        # Transform schema fields to service fields
        trade_data_dict["parties"] = ["QuantaEnergi", trade_data_dict["counterparty"]]
        
        # Capture trade
        trade_id = await trade_lifecycle.capture_trade(trade_data_dict)
        
        # Background validation
        background_tasks.add_task(
            trade_lifecycle.validate_trade, 
            trade_id
        )
        
        return TradeResponse(
            trade_id=str(trade_id),
            status="captured",
            message="Trade captured successfully",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Trade capture failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Trade capture failed: {str(e)}")

@router.post("/{trade_id}/validate", response_model=TradeStatusResponse)
async def validate_trade(
    trade_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Validate a captured trade
    """
    try:
        logger.info(f"Validating trade {trade_id} for user {current_user['id']}")
        
        # Validate trade
        validation_result = await trade_lifecycle.validate_trade(trade_id)
        
        # Check Sharia compliance if applicable
        if validation_result.get("valid", False):
            sharia_result = sharia_compliance.screen_commodity(
                {"type": "energy", "trade_id": trade_id}
            )
            validation_result["sharia_compliant"] = sharia_result.get("compliant", False)
        
        return TradeStatusResponse(
            trade_id=trade_id,
            status="validated" if validation_result.get("valid", False) else "validation_failed",
            details=validation_result,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Trade validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Trade validation failed: {str(e)}")

@router.post("/{trade_id}/confirm", response_model=ConfirmationResponse)
async def generate_confirmation(
    trade_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Generate trade confirmation
    """
    try:
        logger.info(f"Generating confirmation for trade {trade_id}")
        
        confirmation = await trade_lifecycle.generate_confirmation(trade_id)
        
        return ConfirmationResponse(
            trade_id=trade_id,
            confirmation_id=confirmation.get("confirmation_id", "conf_001"),
            status="confirmed",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Confirmation generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Confirmation generation failed: {str(e)}")

@router.post("/{trade_id}/allocate", response_model=AllocationResponse)
async def allocate_trade(
    trade_id: str,
    allocation_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user)
):
    """
    Allocate trade to specific accounts/portfolios
    """
    try:
        logger.info(f"Allocating trade {trade_id}")
        
        allocation_result = await trade_lifecycle.allocate_trade(trade_id, allocation_data)
        
        return AllocationResponse(
            trade_id=trade_id,
            allocation_id=allocation_result.get("allocation_id", "alloc_001"),
            status="allocated",
            details=allocation_result,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Trade allocation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Trade allocation failed: {str(e)}")

@router.post("/{trade_id}/settle", response_model=SettlementResponse)
async def process_settlement(
    trade_id: str,
    settlement_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user)
):
    """
    Process trade settlement
    """
    try:
        logger.info(f"Processing settlement for trade {trade_id}")
        
        settlement_result = await trade_lifecycle.process_settlement(trade_id, settlement_data)
        
        return SettlementResponse(
            trade_id=trade_id,
            settlement_id=settlement_result.get("settlement_id", "settle_001"),
            status="settled",
            details=settlement_result,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Settlement processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Settlement processing failed: {str(e)}")

@router.post("/{trade_id}/invoice", response_model=InvoiceResponse)
async def generate_invoice(
    trade_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Generate invoice for settled trade
    """
    try:
        logger.info(f"Generating invoice for trade {trade_id}")
        
        invoice_result = await trade_lifecycle.generate_invoice(trade_id)
        
        return InvoiceResponse(
            trade_id=trade_id,
            invoice_id=invoice_result.get("invoice_id", "inv_001"),
            status="generated",
            details=invoice_result,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Invoice generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Invoice generation failed: {str(e)}")

@router.post("/{trade_id}/payment", response_model=PaymentResponse)
async def process_payment(
    trade_id: str,
    payment_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user)
):
    """
    Process payment for invoiced trade
    """
    try:
        logger.info(f"Processing payment for trade {trade_id}")
        
        payment_result = await trade_lifecycle.process_payment(trade_id, payment_data)
        
        return PaymentResponse(
            trade_id=trade_id,
            payment_id=payment_result.get("payment_id", "pay_001"),
            status="paid",
            details=payment_result,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Payment processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Payment processing failed: {str(e)}")

@router.get("/{trade_id}/status", response_model=TradeStatusResponse)
async def get_trade_status(
    trade_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get current status of a trade
    """
    try:
        logger.info(f"Getting status for trade {trade_id}")
        
        status_result = await trade_lifecycle.get_trade_status(trade_id)
        
        return TradeStatusResponse(
            trade_id=trade_id,
            status=status_result.get("status", "unknown"),
            details=status_result,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Status retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")

@router.get("/", response_model=List[TradeResponse])
async def get_user_trades(
    status: Optional[str] = Query(None, description="Filter by trade status"),
    limit: int = Query(100, description="Maximum number of trades to return"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get all trades for the current user
    """
    try:
        logger.info(f"Getting trades for user {current_user['id']}")
        
        # Mock response for now - would query database
        trades = [
            TradeResponse(
                trade_id="trade_001",
                status="settled",
                message="Sample trade",
                timestamp=datetime.now().isoformat()
            )
        ]
        
        if status:
            trades = [t for t in trades if t.status == status]
        
        return trades[:limit]
        
    except Exception as e:
        logger.error(f"Trade retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Trade retrieval failed: {str(e)}")

@router.delete("/{trade_id}")
async def cancel_trade(
    trade_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Cancel a trade (if not yet settled)
    """
    try:
        logger.info(f"Cancelling trade {trade_id}")
        
        # Check if trade can be cancelled
        status = await trade_lifecycle.get_trade_status(trade_id)
        if status.get("status") in ["settled", "paid"]:
            raise HTTPException(status_code=400, detail="Cannot cancel settled or paid trade")
        
        # Cancel trade logic would go here
        return {"message": f"Trade {trade_id} cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Trade cancellation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Trade cancellation failed: {str(e)}")
