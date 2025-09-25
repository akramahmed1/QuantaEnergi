"""
Settlements API endpoints for multi-currency netting and reconciliation
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from ...services.billing_service import billing_service
from ...core.security import get_current_user
from ...schemas.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/settlements", tags=["settlements"])

@router.post("/batch")
async def create_settlement_batch(
    settlement_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Create a settlement batch for multi-currency netting
    
    Args:
        settlement_data: Settlement information including trades, currencies, parties
        current_user: Current authenticated user
        
    Returns:
        Dict with settlement batch details
    """
    try:
        settlement_data["created_by"] = current_user.id
        result = billing_service.create_settlement_batch(settlement_data)
        logger.info(f"Settlement batch created by user {current_user.id}: {result['batch_id']}")
        return result
    except Exception as e:
        logger.error(f"Failed to create settlement batch: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{batch_id}/reconcile")
async def reconcile_settlement(
    batch_id: str,
    reconciliation_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Process settlement reconciliation with external systems
    
    Args:
        batch_id: Settlement batch identifier
        reconciliation_data: Reconciliation information including external confirmations
        current_user: Current authenticated user
        
    Returns:
        Dict with reconciliation results
    """
    try:
        reconciliation_data["reconciled_by"] = current_user.id
        result = billing_service.process_settlement_reconciliation(batch_id, reconciliation_data)
        logger.info(f"Settlement reconciled by user {current_user.id}: {batch_id}")
        return result
    except Exception as e:
        logger.error(f"Failed to reconcile settlement {batch_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/automated-task")
async def create_automated_reconciliation_task(
    schedule_config: Dict[str, Any],
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Create automated reconciliation task using Celery
    
    Args:
        schedule_config: Configuration for automated reconciliation
        current_user: Current authenticated user
        
    Returns:
        Dict with task details
    """
    try:
        schedule_config["created_by"] = current_user.id
        result = billing_service.create_automated_reconciliation_task(schedule_config)
        logger.info(f"Automated reconciliation task created by user {current_user.id}")
        return result
    except Exception as e:
        logger.error(f"Failed to create automated reconciliation task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/analytics")
async def get_settlement_analytics(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get settlement analytics and performance metrics
    
    Args:
        date_from: Start date for analytics (ISO format, defaults to 30 days ago)
        date_to: End date for analytics (ISO format, defaults to today)
        current_user: Current authenticated user
        
    Returns:
        Dict with settlement analytics
    """
    try:
        date_from_dt = None
        date_to_dt = None
        
        if date_from:
            date_from_dt = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
        if date_to:
            date_to_dt = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
        
        result = billing_service.get_settlement_analytics(date_from_dt, date_to_dt)
        return result
    except Exception as e:
        logger.error(f"Failed to get settlement analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
