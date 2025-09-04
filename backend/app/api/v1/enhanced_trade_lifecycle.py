"""
Enhanced Trade Lifecycle API Endpoints
Integrates with event bus and supports multi-tenant architecture
"""

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from app.services.enhanced_trade_lifecycle import enhanced_trade_service, EnhancedTradeLifecycleService
from app.schemas.trade import (
    TradeCreate, TradeUpdate, TradeResponse, TradeStatusResponse,
    TradeDetails, TradeConfirmation, TradeAllocation, TradeSettlement,
    TradeInvoice, TradePayment, TradeFilter, TradeSearchResponse,
    TradeAnalytics, ShariaComplianceCheck
)
from app.core.event_bus import event_bus, EventType
from app.core.auth import get_current_user

router = APIRouter(prefix="/enhanced/trades", tags=["Enhanced Trade Lifecycle"])

# Mock user authentication for demo (replace with real auth in production)
async def get_current_user_mock():
    """Mock current user for demo purposes"""
    return {
        "user_id": "user_123",
        "username": "demo_user",
        "email": "demo@quantaenergi.com",
        "organization_id": "123e4567-e89b-12d3-a456-426614174000"  # Saudi Aramco
    }

@router.post("/capture", response_model=TradeResponse)
async def capture_trade(
    trade_data: TradeCreate,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user_mock)
):
    """
    Capture a new trade with event publishing
    """
    try:
        user_id = current_user["user_id"]
        organization_id = current_user["organization_id"]
        
        # Capture the trade
        response = await enhanced_trade_service.capture_trade(
            trade_data=trade_data,
            user_id=user_id,
            organization_id=organization_id
        )
        
        # Start event bus if not running
        if not event_bus._is_running:
            background_tasks.add_task(event_bus.start)
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/{trade_id}/validate", response_model=TradeStatusResponse)
async def validate_trade(
    trade_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user_mock)
):
    """
    Validate a captured trade
    """
    try:
        user_id = current_user["user_id"]
        
        response = await enhanced_trade_service.validate_trade(
            trade_id=trade_id,
            user_id=user_id
        )
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/{trade_id}/confirm", response_model=TradeConfirmation)
async def confirm_trade(
    trade_id: str,
    confirmation_notes: Optional[str] = Query(None, description="Confirmation notes"),
    current_user: Dict[str, Any] = Depends(get_current_user_mock)
):
    """
    Confirm a validated trade
    """
    try:
        user_id = current_user["user_id"]
        
        response = await enhanced_trade_service.confirm_trade(
            trade_id=trade_id,
            user_id=user_id,
            confirmation_notes=confirmation_notes
        )
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/{trade_id}/allocate", response_model=TradeAllocation)
async def allocate_trade(
    trade_id: str,
    allocation_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user_mock)
):
    """
    Allocate a confirmed trade
    """
    try:
        user_id = current_user["user_id"]
        
        response = await enhanced_trade_service.allocate_trade(
            trade_id=trade_id,
            user_id=user_id,
            allocation_data=allocation_data
        )
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/{trade_id}/settle", response_model=TradeSettlement)
async def settle_trade(
    trade_id: str,
    settlement_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user_mock)
):
    """
    Settle an allocated trade
    """
    try:
        user_id = current_user["user_id"]
        
        response = await enhanced_trade_service.settle_trade(
            trade_id=trade_id,
            user_id=user_id,
            settlement_data=settlement_data
        )
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{trade_id}/status", response_model=TradeStatusResponse)
async def get_trade_status(
    trade_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user_mock)
):
    """
    Get current status of a trade
    """
    try:
        response = await enhanced_trade_service.get_trade_status(trade_id=trade_id)
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/user", response_model=TradeSearchResponse)
async def get_user_trades(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Page size"),
    current_user: Dict[str, Any] = Depends(get_current_user_mock)
):
    """
    Get trades for the current user with pagination
    """
    try:
        user_id = current_user["user_id"]
        organization_id = current_user["organization_id"]
        
        response = await enhanced_trade_service.get_user_trades(
            user_id=user_id,
            organization_id=organization_id,
            page=page,
            page_size=page_size
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/analytics", response_model=TradeAnalytics)
async def get_trade_analytics(
    date_from: Optional[datetime] = Query(None, description="Start date for analytics"),
    date_to: Optional[datetime] = Query(None, description="End date for analytics"),
    current_user: Dict[str, Any] = Depends(get_current_user_mock)
):
    """
    Get trade analytics for the current user's organization
    """
    try:
        organization_id = current_user["organization_id"]
        
        response = await enhanced_trade_service.get_trade_analytics(
            organization_id=organization_id,
            date_from=date_from,
            date_to=date_to
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/{trade_id}/cancel", response_model=TradeResponse)
async def cancel_trade(
    trade_id: str,
    reason: str = Query(..., description="Reason for cancellation"),
    current_user: Dict[str, Any] = Depends(get_current_user_mock)
):
    """
    Cancel a trade
    """
    try:
        user_id = current_user["user_id"]
        
        response = await enhanced_trade_service.cancel_trade(
            trade_id=trade_id,
            user_id=user_id,
            reason=reason
        )
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/organizations/{organization_id}/trades", response_model=TradeSearchResponse)
async def get_organization_trades(
    organization_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Page size"),
    trade_type: Optional[str] = Query(None, description="Filter by trade type"),
    commodity: Optional[str] = Query(None, description="Filter by commodity"),
    status: Optional[str] = Query(None, description="Filter by status"),
    date_from: Optional[datetime] = Query(None, description="Filter by start date"),
    date_to: Optional[datetime] = Query(None, description="Filter by end date"),
    current_user: Dict[str, Any] = Depends(get_current_user_mock)
):
    """
    Get trades for a specific organization with filtering and pagination
    """
    try:
        # For demo purposes, allow access to any organization
        # In production, implement proper authorization
        
        # Get all trades for the organization
        org_trades = [
            trade for trade in enhanced_trade_service.trade_history
            if trade.get("organization_id") == organization_id
        ]
        
        # Apply filters
        if trade_type:
            org_trades = [t for t in org_trades if t.get("trade_type") == trade_type]
        if commodity:
            org_trades = [t for t in org_trades if t.get("commodity") == commodity]
        if status:
            org_trades = [t for t in org_trades if t.get("status") == status]
        if date_from:
            org_trades = [t for t in org_trades if t["created_at"] >= date_from]
        if date_to:
            org_trades = [t for t in org_trades if t["created_at"] <= date_to]
        
        # Apply pagination
        total_count = len(org_trades)
        total_pages = (total_count + page_size - 1) // page_size
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        paginated_trades = org_trades[start_idx:end_idx]
        
        # Convert to TradeDetails
        trade_details = []
        for trade in paginated_trades:
            trade_detail = enhanced_trade_service._create_trade_detail(trade)
            trade_details.append(trade_detail)
        
        # Create filter object
        filters = TradeFilter(
            organization_id=uuid.UUID(organization_id),
            trade_type=trade_type,
            commodity=commodity,
            status=status,
            date_from=date_from,
            date_to=date_to
        )
        
        return TradeSearchResponse(
            trades=trade_details,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            filters_applied=filters
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/organizations/{organization_id}/analytics", response_model=TradeAnalytics)
async def get_organization_analytics(
    organization_id: str,
    date_from: Optional[datetime] = Query(None, description="Start date for analytics"),
    date_to: Optional[datetime] = Query(None, description="End date for analytics"),
    current_user: Dict[str, Any] = Depends(get_current_user_mock)
):
    """
    Get trade analytics for a specific organization
    """
    try:
        response = await enhanced_trade_service.get_trade_analytics(
            organization_id=organization_id,
            date_from=date_from,
            date_to=date_to
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/event-bus/stats")
async def get_event_bus_stats():
    """
    Get event bus statistics
    """
    try:
        stats = event_bus.get_stats()
        return {
            "success": True,
            "data": stats,
            "message": "Event bus statistics retrieved successfully",
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/event-bus/start")
async def start_event_bus():
    """
    Start the event bus
    """
    try:
        await event_bus.start()
        return {
            "success": True,
            "message": "Event bus started successfully",
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/event-bus/stop")
async def stop_event_bus():
    """
    Stop the event bus
    """
    try:
        await event_bus.stop()
        return {
            "success": True,
            "message": "Event bus stopped successfully",
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/event-bus/history")
async def get_event_history(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    limit: int = Query(100, ge=1, le=1000, description="Number of events to retrieve")
):
    """
    Get event history
    """
    try:
        if event_type:
            # Convert string to EventType enum
            try:
                event_type_enum = EventType(event_type)
                history = event_bus.get_event_history(event_type=event_type_enum, limit=limit)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid event type: {event_type}")
        else:
            history = event_bus.get_event_history(limit=limit)
        
        # Convert events to serializable format
        serializable_history = []
        for event in history:
            serializable_history.append({
                "event_id": event.metadata.event_id,
                "event_type": event.metadata.event_type.value,
                "timestamp": event.metadata.timestamp.isoformat(),
                "correlation_id": event.metadata.correlation_id,
                "user_id": event.metadata.user_id,
                "organization_id": event.metadata.organization_id,
                "source_service": event.metadata.source_service,
                "payload": event.payload
            })
        
        return {
            "success": True,
            "data": {
                "events": serializable_history,
                "total_count": len(serializable_history)
            },
            "message": "Event history retrieved successfully",
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Add helper method to the service for creating trade details
def _create_trade_detail(self, trade: Dict[str, Any]) -> TradeDetails:
    """Helper method to create TradeDetails from trade dictionary"""
    return TradeDetails(
        trade_id=trade["trade_id"],
        trade_type=trade["trade_type"],
        commodity=trade["commodity"],
        quantity=trade["quantity"],
        price=trade["price"],
        currency=trade["currency"],
        counterparty=trade["counterparty"],
        delivery_date=trade["delivery_date"],
        delivery_location=trade["delivery_location"],
        status=trade["status"],
        trade_direction=trade.get("trade_direction", "buy"),
        settlement_type=trade.get("settlement_type", "T+2"),
        organization_id=trade.get("organization_id"),
        user_id=trade.get("user_id"),
        is_islamic_compliant=trade.get("is_islamic_compliant", False),
        compliance_status="approved" if trade["status"] not in ["failed", "cancelled"] else "rejected",
        risk_category=trade.get("risk_category"),
        risk_score=trade.get("risk_score"),
        created_at=trade["created_at"],
        updated_at=trade["updated_at"],
        captured_at=trade.get("captured_at"),
        validated_at=trade.get("validated_at"),
        confirmed_at=trade.get("confirmed_at"),
        settled_at=trade.get("settled_at"),
        additional_terms=trade.get("additional_terms", {}),
        correlation_id=trade.get("correlation_id")
    )

# Add the helper method to the service
EnhancedTradeLifecycleService._create_trade_detail = _create_trade_detail
