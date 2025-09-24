"""
Analytics API endpoints for AI forecasting, quantum optimization, and blockchain
"""

import sys
import os
# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List, Optional
import structlog

from app.core.jwt_auth import verify_token, TokenData
from app.services.forecasting_service import forecasting_service
from app.services.quantum_optimization_service import quantum_optimization_service
from app.services.blockchain_service import blockchain_service

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

@router.post("/forecast")
async def create_forecast(
    request: Dict,
    current_user: TokenData = Depends(get_current_user)
):
    """Create AI-powered price forecast"""
    try:
        commodity = request.get('commodity', 'crude_oil')
        days_ahead = request.get('days_ahead', 30)
        include_components = request.get('include_components', True)
        
        logger.info("Creating forecast request", 
                   user=current_user.username,
                   commodity=commodity,
                   days_ahead=days_ahead)
        
        forecast = forecasting_service.create_forecast(
            commodity=commodity,
            days_ahead=days_ahead,
            include_components=include_components
        )
        
        return forecast
        
    except Exception as e:
        logger.error("Forecast creation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create forecast: {str(e)}"
        )

@router.get("/forecast/insights/{commodity}")
async def get_market_insights(
    commodity: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Get market insights and recommendations"""
    try:
        logger.info("Retrieving market insights", 
                   user=current_user.username,
                   commodity=commodity)
        
        insights = forecasting_service.get_market_insights(commodity=commodity)
        
        return insights
        
    except Exception as e:
        logger.error("Failed to retrieve market insights", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve insights: {str(e)}"
        )

@router.post("/optimize/portfolio")
async def optimize_portfolio(
    request: Dict,
    current_user: TokenData = Depends(get_current_user)
):
    """Optimize portfolio using quantum algorithms"""
    try:
        assets = request.get('assets', ['crude_oil', 'natural_gas', 'electricity'])
        expected_returns = request.get('expected_returns', [0.05, 0.03, 0.02])
        risk_matrix = request.get('risk_matrix', [[0.01, 0.005, 0.002], [0.005, 0.02, 0.001], [0.002, 0.001, 0.03]])
        risk_tolerance = request.get('risk_tolerance', 0.5)
        budget = request.get('budget', 1000000.0)
        
        logger.info("Portfolio optimization request", 
                   user=current_user.username,
                   assets=len(assets),
                   budget=budget)
        
        optimization = quantum_optimization_service.optimize_portfolio(
            assets=assets,
            expected_returns=expected_returns,
            risk_matrix=risk_matrix,
            risk_tolerance=risk_tolerance,
            budget=budget
        )
        
        return optimization
        
    except Exception as e:
        logger.error("Portfolio optimization failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Portfolio optimization failed: {str(e)}"
        )

@router.post("/optimize/strategy")
async def optimize_trading_strategy(
    request: Dict,
    current_user: TokenData = Depends(get_current_user)
):
    """Optimize trading strategy using quantum algorithms"""
    try:
        market_data = request.get('market_data', {})
        constraints = request.get('constraints', {})
        
        logger.info("Strategy optimization request", 
                   user=current_user.username)
        
        strategy = quantum_optimization_service.optimize_trading_strategy(
            market_data=market_data,
            constraints=constraints
        )
        
        return strategy
        
    except Exception as e:
        logger.error("Strategy optimization failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Strategy optimization failed: {str(e)}"
        )

@router.post("/blockchain/carbon-trade")
async def create_carbon_trade(
    request: Dict,
    current_user: TokenData = Depends(get_current_user)
):
    """Create carbon credit trade on blockchain"""
    try:
        trade_id = request.get('trade_id')
        carbon_amount = request.get('carbon_amount', 100.0)
        price_per_ton = request.get('price_per_ton', 50.0)
        seller_address = request.get('seller_address', '0x1234567890123456789012345678901234567890')
        buyer_address = request.get('buyer_address', '0x0987654321098765432109876543210987654321')
        
        if not trade_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="trade_id is required"
            )
        
        logger.info("Creating carbon trade", 
                   user=current_user.username,
                   trade_id=trade_id)
        
        carbon_trade = blockchain_service.create_carbon_trade(
            trade_id=trade_id,
            carbon_amount=carbon_amount,
            price_per_ton=price_per_ton,
            seller_address=seller_address,
            buyer_address=buyer_address
        )
        
        return carbon_trade
        
    except Exception as e:
        logger.error("Carbon trade creation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create carbon trade: {str(e)}"
        )

@router.get("/blockchain/carbon-trade/{trade_id}")
async def get_carbon_trade(
    trade_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Get carbon trade details from blockchain"""
    try:
        logger.info("Retrieving carbon trade", 
                   user=current_user.username,
                   trade_id=trade_id)
        
        carbon_trade = blockchain_service.get_carbon_trade(trade_id=trade_id)
        
        return carbon_trade
        
    except Exception as e:
        logger.error("Failed to retrieve carbon trade", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve carbon trade: {str(e)}"
        )

@router.post("/blockchain/carbon-trade/{trade_id}/settle")
async def settle_carbon_trade(
    trade_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Settle carbon trade on blockchain"""
    try:
        logger.info("Settling carbon trade", 
                   user=current_user.username,
                   trade_id=trade_id)
        
        settlement = blockchain_service.settle_carbon_trade(trade_id=trade_id)
        
        return settlement
        
    except Exception as e:
        logger.error("Carbon trade settlement failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to settle carbon trade: {str(e)}"
        )

@router.get("/blockchain/esg-score/{company_address}")
async def get_esg_score(
    company_address: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Get ESG score for company from blockchain"""
    try:
        logger.info("Retrieving ESG score", 
                   user=current_user.username,
                   company_address=company_address)
        
        esg_score = blockchain_service.get_esg_score(company_address=company_address)
        
        return esg_score
        
    except Exception as e:
        logger.error("Failed to retrieve ESG score", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve ESG score: {str(e)}"
        )
