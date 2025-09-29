"""
Risk Management Domain API Routers
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from ..base import get_db
from .services import VaRCalculator, RiskAnalytics

router = APIRouter(prefix="/risk", tags=["Risk Management"])

@router.post("/var/parametric")
async def calculate_parametric_var(
    positions: List[Dict[str, Any]],
    confidence_level: float = Query(0.95, ge=0.9, le=0.99),
    time_horizon: int = Query(1, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """Calculate parametric VaR using normal distribution assumption"""
    var_calculator = VaRCalculator(db)
    result = var_calculator.calculate_parametric_var(positions, confidence_level, time_horizon)
    
    if not result.get("success", True):
        raise HTTPException(status_code=500, detail=result.get("error", "VaR calculation failed"))
    
    return result

@router.post("/var/monte-carlo")
async def calculate_monte_carlo_var(
    positions: List[Dict[str, Any]],
    confidence_level: float = Query(0.95, ge=0.9, le=0.99),
    time_horizon: int = Query(1, ge=1, le=30),
    num_simulations: int = Query(10000, ge=1000, le=100000),
    db: Session = Depends(get_db)
):
    """Calculate VaR using Monte Carlo simulation with 10k paths"""
    var_calculator = VaRCalculator(db)
    result = var_calculator.calculate_monte_carlo_var(
        positions, confidence_level, time_horizon, num_simulations
    )
    
    if not result.get("success", True):
        raise HTTPException(status_code=500, detail=result.get("error", "Monte Carlo VaR calculation failed"))
    
    return result

@router.post("/var/historical")
async def calculate_historical_var(
    historical_returns: List[float],
    confidence_level: float = Query(0.95, ge=0.9, le=0.99),
    db: Session = Depends(get_db)
):
    """Calculate VaR using historical simulation method"""
    var_calculator = VaRCalculator(db)
    result = var_calculator.calculate_historical_var(historical_returns, confidence_level)
    
    if not result.get("success", True):
        raise HTTPException(status_code=500, detail=result.get("error", "Historical VaR calculation failed"))
    
    return result

@router.post("/analytics/portfolio-metrics")
async def calculate_portfolio_risk_metrics(
    positions: List[Dict[str, Any]],
    db: Session = Depends(get_db)
):
    """Calculate comprehensive portfolio risk metrics"""
    risk_analytics = RiskAnalytics(db)
    result = risk_analytics.calculate_portfolio_risk_metrics(positions)
    
    if not result.get("success", True):
        raise HTTPException(status_code=500, detail=result.get("error", "Risk metrics calculation failed"))
    
    return result
