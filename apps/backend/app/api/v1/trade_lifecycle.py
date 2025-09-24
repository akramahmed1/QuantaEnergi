from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
from typing import List
import structlog
import uuid

import sys
import os
# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from libs.shared.models import Trade
from app.core.jwt_auth import verify_token, TokenData

logger = structlog.get_logger(__name__)

router = APIRouter()

# Mock database (replace with real database)
trades_db: List[Trade] = []

def get_current_user(token: str = Depends(verify_token)) -> TokenData:
    """Get current authenticated user."""
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

@router.post("/capture", response_model=Trade)
async def capture_trade(
    trade: Trade,
    current_user: TokenData = Depends(get_current_user)
):
    """Capture a new trade."""
    try:
        # Generate trade ID and timestamp
        trade.id = str(uuid.uuid4())
        trade.timestamp = datetime.utcnow()
        trade.user_id = current_user.username
        trade.status = "captured"
        
        # Add to database
        trades_db.append(trade)
        
        logger.info("Trade captured", 
                   trade_id=trade.id, 
                   commodity=trade.commodity,
                   user=current_user.username)
        
        return trade
        
    except Exception as e:
        logger.error("Failed to capture trade", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to capture trade"
        )

@router.post("/validate/{trade_id}", response_model=Trade)
async def validate_trade(
    trade_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Validate a captured trade."""
    try:
        # Find trade
        trade = next((t for t in trades_db if t.id == trade_id), None)
        if not trade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trade not found"
            )
        
        # Update status
        trade.status = "validated"
        
        logger.info("Trade validated", 
                   trade_id=trade_id,
                   user=current_user.username)
        
        return trade
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to validate trade", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate trade"
        )

@router.post("/settle/{trade_id}", response_model=Trade)
async def settle_trade(
    trade_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Settle a validated trade."""
    try:
        # Find trade
        trade = next((t for t in trades_db if t.id == trade_id), None)
        if not trade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trade not found"
            )
        
        if trade.status != "validated":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Trade must be validated before settlement"
            )
        
        # Update status
        trade.status = "settled"
        
        logger.info("Trade settled", 
                   trade_id=trade_id,
                   user=current_user.username)
        
        return trade
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to settle trade", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to settle trade"
        )

@router.get("/trades", response_model=List[Trade])
async def get_trades(
    current_user: TokenData = Depends(get_current_user)
):
    """Get all trades for the current user."""
    try:
        user_trades = [t for t in trades_db if t.user_id == current_user.username]
        
        logger.info("Retrieved trades", 
                   user=current_user.username,
                   count=len(user_trades))
        
        return user_trades
        
    except Exception as e:
        logger.error("Failed to retrieve trades", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve trades"
        )

@router.get("/trades/{trade_id}", response_model=Trade)
async def get_trade(
    trade_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Get a specific trade by ID."""
    try:
        trade = next((t for t in trades_db if t.id == trade_id and t.user_id == current_user.username), None)
        if not trade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trade not found"
            )
        
        return trade
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to retrieve trade", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve trade"
        )
