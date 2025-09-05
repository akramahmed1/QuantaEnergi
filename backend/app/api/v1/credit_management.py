"""
Credit Management API endpoints for ETRM/CTRM operations
Handles credit limits, exposure tracking, and risk assessment
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from ...services.credit_manager import CreditManager
from ...schemas.trade import (
    CreditLimit, CreditExposure, CreditReport, ApiResponse, ErrorResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/credit", tags=["credit_management"])

# Initialize services
credit_manager = CreditManager()

# Mock user dependency for now
async def get_current_user():
    return {"id": "user123", "email": "trader@quantaenergi.com", "role": "trader"}

@router.post("/limits", response_model=ApiResponse)
async def set_credit_limit(
    credit_limit: CreditLimit,
    current_user: Dict = Depends(get_current_user)
):
    """
    Set credit limit for a counterparty
    """
    try:
        logger.info(f"Setting credit limit for counterparty {credit_limit.counterparty_id}")
        
        # Convert Pydantic model to dict
        limit_data = credit_limit.model_dump()
        limit_data["set_by"] = current_user["id"]
        limit_data["set_timestamp"] = datetime.now().isoformat()
        
        result = await credit_manager.set_credit_limit(
            credit_limit.counterparty_id, 
            limit_data
        )
        
        return ApiResponse(
            success=True,
            data=result,
            message=f"Credit limit set successfully for {credit_limit.counterparty_id}"
        )
        
    except Exception as e:
        logger.error(f"Credit limit setting failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Credit limit setting failed: {str(e)}")

@router.get("/limits/{counterparty_id}", response_model=ApiResponse)
async def get_credit_limit(
    counterparty_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get credit limit for a specific counterparty
    """
    try:
        logger.info(f"Getting credit limit for counterparty {counterparty_id}")
        
        limit = await credit_manager.get_credit_limit(counterparty_id)
        
        return ApiResponse(
            success=True,
            data=limit,
            message=f"Credit limit retrieved for {counterparty_id}"
        )
        
    except Exception as e:
        logger.error(f"Credit limit retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Credit limit retrieval failed: {str(e)}")

@router.get("/limits", response_model=ApiResponse)
async def get_all_credit_limits(
    risk_rating: Optional[str] = Query(None, description="Filter by risk rating"),
    limit: int = Query(100, description="Maximum number of limits to return"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get all credit limits with optional filtering
    """
    try:
        logger.info(f"Getting all credit limits for user {current_user['id']}")
        
        # Mock response for now - would query database
        limits = [
            {
                "counterparty_id": "CP001",
                "limit_amount": 1000000.0,
                "currency": "USD",
                "risk_rating": "A",
                "expiry_date": "2025-12-31T23:59:59",
                "set_by": "admin",
                "set_timestamp": "2024-01-01T00:00:00"
            }
        ]
        
        if risk_rating:
            limits = [l for l in limits if l["risk_rating"] == risk_rating]
        
        return ApiResponse(
            success=True,
            data=limits[:limit],
            message=f"Retrieved {len(limits[:limit])} credit limits"
        )
        
    except Exception as e:
        logger.error(f"Credit limits retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Credit limits retrieval failed: {str(e)}")

@router.post("/exposure/calculate", response_model=ApiResponse)
async def calculate_exposure(
    counterparty_id: str,
    positions: List[Dict[str, Any]],
    current_user: Dict = Depends(get_current_user)
):
    """
    Calculate current credit exposure for a counterparty
    """
    try:
        logger.info(f"Calculating exposure for counterparty {counterparty_id}")
        
        exposure = await credit_manager.calculate_exposure(counterparty_id, positions)
        
        return ApiResponse(
            success=True,
            data=exposure,
            message=f"Exposure calculated for {counterparty_id}"
        )
        
    except Exception as e:
        logger.error(f"Exposure calculation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Exposure calculation failed: {str(e)}")

@router.get("/exposure/{counterparty_id}", response_model=ApiResponse)
async def get_exposure(
    counterparty_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get current exposure for a specific counterparty
    """
    try:
        logger.info(f"Getting exposure for counterparty {counterparty_id}")
        
        # Mock positions for now
        mock_positions = [
            {"commodity": "crude_oil", "quantity": 1000, "price": 85.50},
            {"commodity": "natural_gas", "quantity": 500, "price": 3.20}
        ]
        
        exposure = await credit_manager.calculate_exposure(counterparty_id, mock_positions)
        
        return ApiResponse(
            success=True,
            data=exposure,
            message=f"Exposure retrieved for {counterparty_id}"
        )
        
    except Exception as e:
        logger.error(f"Exposure retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Exposure retrieval failed: {str(e)}")

@router.post("/availability/check", response_model=ApiResponse)
async def check_credit_availability(
    counterparty_id: str,
    trade_amount: float,
    current_user: Dict = Depends(get_current_user)
):
    """
    Check if credit is available for a new trade
    """
    try:
        logger.info(f"Checking credit availability for {counterparty_id}, amount: {trade_amount}")
        
        # Mock positions for now
        mock_positions = [
            {"commodity": "crude_oil", "quantity": 1000, "price": 85.50}
        ]
        
        availability = await credit_manager.check_credit_availability(
            counterparty_id, 
            trade_amount
        )
        
        return ApiResponse(
            success=True,
            data=availability,
            message=f"Credit availability checked for {counterparty_id}"
        )
        
    except Exception as e:
        logger.error(f"Credit availability check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Credit availability check failed: {str(e)}")

@router.get("/availability/{counterparty_id}", response_model=ApiResponse)
async def get_credit_availability(
    counterparty_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get current credit availability for a counterparty
    """
    try:
        logger.info(f"Getting credit availability for {counterparty_id}")
        
        # Get credit limit
        limit = await credit_manager.get_credit_limit(counterparty_id)
        
        # Mock positions for exposure calculation
        mock_positions = [
            {"commodity": "crude_oil", "quantity": 1000, "price": 85.50}
        ]
        
        # Calculate exposure
        exposure = await credit_manager.calculate_exposure(counterparty_id, mock_positions)
        
        # Calculate availability
        available_credit = limit.get("limit_amount", 0) - exposure.get("current_exposure", 0)
        
        availability_data = {
            "counterparty_id": counterparty_id,
            "credit_limit": limit.get("limit_amount", 0),
            "current_exposure": exposure.get("current_exposure", 0),
            "available_credit": max(0, available_credit),
            "utilization_percentage": (exposure.get("current_exposure", 0) / limit.get("limit_amount", 1)) * 100,
            "risk_level": exposure.get("risk_level", "unknown")
        }
        
        return ApiResponse(
            success=True,
            data=availability_data,
            message=f"Credit availability retrieved for {counterparty_id}"
        )
        
    except Exception as e:
        logger.error(f"Credit availability retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Credit availability retrieval failed: {str(e)}")

@router.post("/reports/generate", response_model=ApiResponse)
async def generate_credit_report(
    counterparty_id: Optional[str] = Query(None, description="Specific counterparty ID"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Generate credit report for counterparty(ies)
    """
    try:
        logger.info(f"Generating credit report for user {current_user['id']}")
        
        if counterparty_id:
            # Single counterparty report
            report = await credit_manager.generate_credit_report(counterparty_id)
        else:
            # Portfolio-wide report
            report = await credit_manager.generate_credit_report()
        
        return ApiResponse(
            success=True,
            data=report,
            message="Credit report generated successfully"
        )
        
    except Exception as e:
        logger.error(f"Credit report generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Credit report generation failed: {str(e)}")

@router.get("/reports/{counterparty_id}", response_model=ApiResponse)
async def get_credit_report(
    counterparty_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get credit report for a specific counterparty
    """
    try:
        logger.info(f"Getting credit report for {counterparty_id}")
        
        report = await credit_manager.generate_credit_report(counterparty_id)
        
        return ApiResponse(
            success=True,
            data=report,
            message=f"Credit report retrieved for {counterparty_id}"
        )
        
    except Exception as e:
        logger.error(f"Credit report retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Credit report retrieval failed: {str(e)}")

@router.get("/reports", response_model=ApiResponse)
async def get_all_credit_reports(
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    limit: int = Query(100, description="Maximum number of reports to return"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get all credit reports with optional filtering
    """
    try:
        logger.info(f"Getting all credit reports for user {current_user['id']}")
        
        # Generate portfolio report
        portfolio_report = await credit_manager.generate_credit_report()
        
        # Filter by risk level if specified
        if risk_level and "counterparties" in portfolio_report:
            portfolio_report["counterparties"] = [
                cp for cp in portfolio_report["counterparties"]
                if cp.get("risk_level") == risk_level
            ]
        
        return ApiResponse(
            success=True,
            data=portfolio_report,
            message="Credit reports retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Credit reports retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Credit reports retrieval failed: {str(e)}")

@router.put("/limits/{counterparty_id}", response_model=ApiResponse)
async def update_credit_limit(
    counterparty_id: str,
    updated_limit: CreditLimit,
    current_user: Dict = Depends(get_current_user)
):
    """
    Update credit limit for a counterparty
    """
    try:
        logger.info(f"Updating credit limit for {counterparty_id}")
        
        # Convert Pydantic model to dict
        limit_data = updated_limit.dict()
        limit_data["updated_by"] = current_user["id"]
        limit_data["updated_timestamp"] = datetime.now().isoformat()
        
        # Update limit
        result = await credit_manager.set_credit_limit(counterparty_id, limit_data)
        
        return ApiResponse(
            success=True,
            data=result,
            message=f"Credit limit updated for {counterparty_id}"
        )
        
    except Exception as e:
        logger.error(f"Credit limit update failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Credit limit update failed: {str(e)}")

@router.delete("/limits/{counterparty_id}")
async def delete_credit_limit(
    counterparty_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Delete credit limit for a counterparty
    """
    try:
        logger.info(f"Deleting credit limit for {counterparty_id}")
        
        # Check if counterparty has active exposure
        mock_positions = [{"commodity": "crude_oil", "quantity": 1000, "price": 85.50}]
        exposure = await credit_manager.calculate_exposure(counterparty_id, mock_positions)
        
        if exposure.get("current_exposure", 0) > 0:
            raise HTTPException(
                status_code=400, 
                detail="Cannot delete credit limit for counterparty with active exposure"
            )
        
        # Delete logic would go here
        return {"message": f"Credit limit deleted for {counterparty_id}"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Credit limit deletion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Credit limit deletion failed: {str(e)}")

@router.get("/dashboard", response_model=ApiResponse)
async def get_credit_dashboard(
    current_user: Dict = Depends(get_current_user)
):
    """
    Get credit management dashboard data
    """
    try:
        logger.info(f"Getting credit dashboard for user {current_user['id']}")
        
        # Mock dashboard data
        dashboard_data = {
            "total_counterparties": 25,
            "total_credit_limit": 50000000.0,
            "total_exposure": 35000000.0,
            "available_credit": 15000000.0,
            "average_utilization": 70.0,
            "high_risk_counterparties": 3,
            "expiring_limits": 5,
            "recent_activities": [
                {
                    "action": "Credit limit updated",
                    "counterparty": "CP001",
                    "timestamp": "2024-01-15T10:30:00Z"
                }
            ]
        }
        
        return ApiResponse(
            success=True,
            data=dashboard_data,
            message="Credit dashboard data retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Credit dashboard retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Credit dashboard retrieval failed: {str(e)}")
