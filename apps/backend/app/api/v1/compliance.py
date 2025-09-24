"""
Compliance API endpoints for Sharia compliance, regulatory reporting, and billing
"""

import sys
import os
# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import StreamingResponse
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import structlog
import io

from app.core.jwt_auth import verify_token, TokenData
from app.services.sharia_compliance import sharia_compliance_service
from app.services.compliance_reporting import compliance_reporting_service
from app.services.billing_service import billing_service

logger = structlog.get_logger(__name__)

router = APIRouter()

def get_current_user(token: str = Depends(verify_token)) -> TokenData:
    """Get current authenticated user."""
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

@router.post("/sharia/check")
async def check_sharia_compliance(
    request: Dict,
    current_user: TokenData = Depends(get_current_user)
):
    """Check Sharia compliance for a trade"""
    try:
        logger.info("Sharia compliance check request", 
                   user=current_user.username,
                   trade_id=request.get('id'))
        
        compliance_result = sharia_compliance_service.check_trade_compliance(request)
        
        return compliance_result
        
    except Exception as e:
        logger.error("Sharia compliance check failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sharia compliance check failed: {str(e)}"
        )

@router.post("/sharia/approval/{trade_id}")
async def get_sharia_approval(
    trade_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Get Sharia board approval for a trade"""
    try:
        logger.info("Sharia board approval request", 
                   user=current_user.username,
                   trade_id=trade_id)
        
        approval = sharia_compliance_service.get_sharia_board_approval(trade_id)
        
        return approval
        
    except Exception as e:
        logger.error("Sharia board approval failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sharia board approval failed: {str(e)}"
        )

@router.post("/reports/generate")
async def generate_compliance_report(
    request: Dict,
    current_user: TokenData = Depends(get_current_user)
):
    """Generate compliance report for specified regulation"""
    try:
        report_type = request.get('report_type', 'cftc')
        start_date = datetime.fromisoformat(request.get('start_date', (datetime.now() - timedelta(days=30)).isoformat()))
        end_date = datetime.fromisoformat(request.get('end_date', datetime.now().isoformat()))
        data = request.get('data', [])
        anonymize = request.get('anonymize', True)
        
        logger.info("Generating compliance report", 
                   user=current_user.username,
                   report_type=report_type)
        
        report = compliance_reporting_service.generate_report(
            report_type=report_type,
            start_date=start_date,
            end_date=end_date,
            data=data,
            anonymize=anonymize
        )
        
        return report
        
    except Exception as e:
        logger.error("Compliance report generation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Compliance report generation failed: {str(e)}"
        )

@router.post("/reports/consolidated")
async def generate_consolidated_report(
    request: Dict,
    current_user: TokenData = Depends(get_current_user)
):
    """Generate consolidated compliance report for multiple regulations"""
    try:
        report_types = request.get('report_types', ['cftc', 'emir', 'gdpr'])
        start_date = datetime.fromisoformat(request.get('start_date', (datetime.now() - timedelta(days=30)).isoformat()))
        end_date = datetime.fromisoformat(request.get('end_date', datetime.now().isoformat()))
        data = request.get('data', [])
        
        logger.info("Generating consolidated compliance report", 
                   user=current_user.username,
                   report_types=report_types)
        
        consolidated_report = compliance_reporting_service.generate_consolidated_report(
            report_types=report_types,
            start_date=start_date,
            end_date=end_date,
            data=data
        )
        
        return consolidated_report
        
    except Exception as e:
        logger.error("Consolidated report generation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Consolidated report generation failed: {str(e)}"
        )

@router.post("/reports/export/{report_id}")
async def export_report_csv(
    report_id: str,
    request: Dict,
    current_user: TokenData = Depends(get_current_user)
):
    """Export compliance report as CSV"""
    try:
        logger.info("Exporting report to CSV", 
                   user=current_user.username,
                   report_id=report_id)
        
        # Get report data (in a real implementation, this would be retrieved from storage)
        report_data = request.get('report_data', {})
        
        csv_content = compliance_reporting_service.export_report_csv(report_data)
        
        # Create CSV response
        csv_io = io.StringIO(csv_content)
        
        return StreamingResponse(
            io.BytesIO(csv_content.encode('utf-8')),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={report_id}.csv"}
        )
        
    except Exception as e:
        logger.error("CSV export failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"CSV export failed: {str(e)}"
        )

@router.post("/billing/customers")
async def create_customer(
    request: Dict,
    current_user: TokenData = Depends(get_current_user)
):
    """Create a new billing customer"""
    try:
        logger.info("Creating billing customer", 
                   user=current_user.username,
                   email=request.get('email'))
        
        customer = billing_service.create_customer(request)
        
        return customer
        
    except Exception as e:
        logger.error("Customer creation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Customer creation failed: {str(e)}"
        )

@router.post("/billing/subscriptions")
async def create_subscription(
    request: Dict,
    current_user: TokenData = Depends(get_current_user)
):
    """Create a subscription for a customer"""
    try:
        customer_id = request.get('customer_id')
        plan_tier = request.get('plan_tier', 'basic')
        payment_method_id = request.get('payment_method_id')
        
        logger.info("Creating subscription", 
                   user=current_user.username,
                   customer_id=customer_id,
                   plan_tier=plan_tier)
        
        subscription = billing_service.create_subscription(
            customer_id=customer_id,
            plan_tier=plan_tier,
            payment_method_id=payment_method_id
        )
        
        return subscription
        
    except Exception as e:
        logger.error("Subscription creation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Subscription creation failed: {str(e)}"
        )

@router.get("/billing/subscriptions/{subscription_id}")
async def get_subscription(
    subscription_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Get subscription details"""
    try:
        logger.info("Retrieving subscription", 
                   user=current_user.username,
                   subscription_id=subscription_id)
        
        subscription = billing_service.get_subscription(subscription_id)
        
        return subscription
        
    except Exception as e:
        logger.error("Failed to retrieve subscription", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve subscription: {str(e)}"
        )

@router.delete("/billing/subscriptions/{subscription_id}")
async def cancel_subscription(
    subscription_id: str,
    immediately: bool = False,
    current_user: TokenData = Depends(get_current_user)
):
    """Cancel a subscription"""
    try:
        logger.info("Cancelling subscription", 
                   user=current_user.username,
                   subscription_id=subscription_id,
                   immediately=immediately)
        
        cancellation = billing_service.cancel_subscription(
            subscription_id=subscription_id,
            immediately=immediately
        )
        
        return cancellation
        
    except Exception as e:
        logger.error("Subscription cancellation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Subscription cancellation failed: {str(e)}"
        )

@router.post("/billing/payment-intents")
async def create_payment_intent(
    request: Dict,
    current_user: TokenData = Depends(get_current_user)
):
    """Create a payment intent for one-time payments"""
    try:
        amount = request.get('amount', 0.0)
        currency = request.get('currency', 'usd')
        customer_id = request.get('customer_id')
        
        logger.info("Creating payment intent", 
                   user=current_user.username,
                   amount=amount,
                   currency=currency)
        
        payment_intent = billing_service.create_payment_intent(
            amount=amount,
            currency=currency,
            customer_id=customer_id
        )
        
        return payment_intent
        
    except Exception as e:
        logger.error("Payment intent creation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment intent creation failed: {str(e)}"
        )

@router.get("/billing/usage/{customer_id}")
async def get_usage_stats(
    customer_id: str,
    period_days: int = 30,
    current_user: TokenData = Depends(get_current_user)
):
    """Get usage statistics for billing"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        logger.info("Retrieving usage stats", 
                   user=current_user.username,
                   customer_id=customer_id,
                   period_days=period_days)
        
        usage_stats = billing_service.get_usage_stats(
            customer_id=customer_id,
            period_start=start_date,
            period_end=end_date
        )
        
        return usage_stats
        
    except Exception as e:
        logger.error("Failed to retrieve usage stats", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve usage stats: {str(e)}"
        )

@router.get("/billing/plans")
async def get_available_plans(
    current_user: TokenData = Depends(get_current_user)
):
    """Get available subscription plans"""
    try:
        logger.info("Retrieving available plans", user=current_user.username)
        
        plans = billing_service.get_available_plans()
        
        return plans
        
    except Exception as e:
        logger.error("Failed to retrieve plans", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve plans: {str(e)}"
        )
