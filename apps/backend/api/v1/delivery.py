"""
Delivery API endpoints for physical delivery scheduling and tracking
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from ...services.delivery_service import delivery_service
from ...core.security import get_current_user
from ...schemas.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/delivery", tags=["delivery"])

@router.post("/schedule")
async def schedule_delivery(
    delivery_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Schedule a new delivery
    
    Args:
        delivery_data: Delivery information including cargo, route, timing
        current_user: Current authenticated user
        
    Returns:
        Dict with scheduled delivery details
    """
    try:
        result = await delivery_service.schedule_delivery(delivery_data)
        logger.info(f"Delivery scheduled by user {current_user.id}: {result['delivery_id']}")
        return result
    except Exception as e:
        logger.error(f"Failed to schedule delivery: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{delivery_id}/start")
async def start_delivery(
    delivery_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Start a scheduled delivery
    
    Args:
        delivery_id: Delivery identifier
        current_user: Current authenticated user
        
    Returns:
        Dict with updated delivery details
    """
    try:
        result = await delivery_service.start_delivery(delivery_id, current_user.id)
        logger.info(f"Delivery started by user {current_user.id}: {delivery_id}")
        return result
    except Exception as e:
        logger.error(f"Failed to start delivery {delivery_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/{delivery_id}/status")
async def update_delivery_status(
    delivery_id: str,
    status_update: Dict[str, Any],
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Update delivery status and progress
    
    Args:
        delivery_id: Delivery identifier
        status_update: Status update information
        current_user: Current authenticated user
        
    Returns:
        Dict with updated delivery details
    """
    try:
        status_update["updated_by"] = current_user.id
        result = await delivery_service.update_delivery_status(delivery_id, status_update)
        logger.info(f"Delivery status updated by user {current_user.id}: {delivery_id}")
        return result
    except Exception as e:
        logger.error(f"Failed to update delivery status {delivery_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{delivery_id}/track")
async def track_delivery(
    delivery_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Track delivery progress and current status
    
    Args:
        delivery_id: Delivery identifier
        current_user: Current authenticated user
        
    Returns:
        Dict with tracking information
    """
    try:
        result = await delivery_service.track_delivery(delivery_id)
        return result
    except Exception as e:
        logger.error(f"Failed to track delivery {delivery_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{delivery_id}/complete")
async def complete_delivery(
    delivery_id: str,
    completion_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Complete a delivery
    
    Args:
        delivery_id: Delivery identifier
        completion_data: Completion information including delivery confirmation
        current_user: Current authenticated user
        
    Returns:
        Dict with completed delivery details
    """
    try:
        completion_data["delivered_by"] = current_user.id
        result = await delivery_service.complete_delivery(delivery_id, completion_data)
        logger.info(f"Delivery completed by user {current_user.id}: {delivery_id}")
        return result
    except Exception as e:
        logger.error(f"Failed to complete delivery {delivery_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/schedule")
async def get_delivery_schedule(
    date: Optional[str] = None,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get delivery schedule for a specific date or today
    
    Args:
        date: Specific date to get schedule for (ISO format, defaults to today)
        current_user: Current authenticated user
        
    Returns:
        Dict with delivery schedule
    """
    try:
        schedule_date = None
        if date:
            schedule_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
        
        result = await delivery_service.get_delivery_schedule(schedule_date)
        return result
    except Exception as e:
        logger.error(f"Failed to get delivery schedule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/analytics")
async def get_delivery_analytics(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get delivery analytics and performance metrics
    
    Args:
        date_from: Start date for analytics (ISO format, defaults to 30 days ago)
        date_to: End date for analytics (ISO format, defaults to today)
        current_user: Current authenticated user
        
    Returns:
        Dict with analytics data
    """
    try:
        date_from_dt = None
        date_to_dt = None
        
        if date_from:
            date_from_dt = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
        if date_to:
            date_to_dt = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
        
        result = await delivery_service.get_delivery_analytics(date_from_dt, date_to_dt)
        return result
    except Exception as e:
        logger.error(f"Failed to get delivery analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
