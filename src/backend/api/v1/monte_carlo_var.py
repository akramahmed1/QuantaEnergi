"""
Monte Carlo VaR API endpoints for ETRM/CTRM operations
Handles 10,000 simulation paths for energy commodity risk assessment
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from ...services.monte_carlo_var import monte_carlo_var_service
from ...core.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/monte-carlo-var", tags=["monte_carlo_var"])

@router.post("/calculate")
async def calculate_monte_carlo_var(
    portfolio: List[Dict[str, Any]] = Body(..., description="Portfolio positions"),
    confidence_level: float = Query(0.95, ge=0.9, le=0.999, description="VaR confidence level"),
    time_horizon: int = Query(1, ge=1, le=30, description="Time horizon in days"),
    num_simulations: int = Query(10000, ge=1000, le=100000, description="Number of Monte Carlo simulations"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Calculate Monte Carlo VaR for energy commodity portfolio
    
    Args:
        portfolio: List of positions with symbol, quantity, entry_price
        confidence_level: VaR confidence level (0.95, 0.99, 0.999)
        time_horizon: Time horizon in days
        num_simulations: Number of Monte Carlo simulations (default: 10,000)
        
    Returns:
        Monte Carlo VaR results with risk metrics
    """
    try:
        result = await monte_carlo_var_service.calculate_monte_carlo_var(
            portfolio=portfolio,
            confidence_level=confidence_level,
            time_horizon=time_horizon,
            num_simulations=num_simulations
        )
        
        logger.info(f"Monte Carlo VaR calculated: {num_simulations} simulations, {confidence_level*100}% confidence")
        return result
        
    except Exception as e:
        logger.error(f"Monte Carlo VaR calculation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Monte Carlo VaR calculation failed: {str(e)}")

@router.post("/stress-test")
async def stress_test_portfolio(
    portfolio: List[Dict[str, Any]] = Body(..., description="Portfolio positions"),
    stress_scenarios: List[Dict[str, Any]] = Body(..., description="Stress test scenarios"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Perform stress testing on energy commodity portfolio
    
    Args:
        portfolio: List of positions with symbol, quantity, entry_price
        stress_scenarios: List of stress scenarios with price shocks
        
    Returns:
        Stress test results for each scenario
    """
    try:
        result = await monte_carlo_var_service.stress_test_portfolio(
            portfolio=portfolio,
            stress_scenarios=stress_scenarios
        )
        
        logger.info(f"Stress test completed for {len(stress_scenarios)} scenarios")
        return result
        
    except Exception as e:
        logger.error(f"Stress testing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Stress testing failed: {str(e)}")

@router.get("/scenarios/energy-crisis")
async def get_energy_crisis_scenarios(current_user: Dict = Depends(get_current_user)):
    """
    Get predefined energy crisis stress scenarios
    
    Returns:
        List of energy crisis stress scenarios
    """
    try:
        scenarios = [
            {
                "name": "Oil Price Crash (-50%)",
                "description": "Simulate 2008-style oil price crash",
                "price_shocks": {
                    "CL=F": -0.50,  # -50% oil price
                    "BZ=F": -0.50,  # -50% Brent price
                    "RB=F": -0.40,  # -40% gasoline price
                    "HO=F": -0.45   # -45% heating oil price
                }
            },
            {
                "name": "Natural Gas Spike (+200%)",
                "description": "Simulate 2022-style natural gas price spike",
                "price_shocks": {
                    "NG=F": 2.00,   # +200% natural gas price
                    "CL=F": 0.20,   # +20% oil price
                    "BZ=F": 0.15    # +15% Brent price
                }
            },
            {
                "name": "Geopolitical Crisis (+100%)",
                "description": "Simulate Middle East crisis impact",
                "price_shocks": {
                    "CL=F": 1.00,   # +100% oil price
                    "BZ=F": 1.00,   # +100% Brent price
                    "RB=F": 0.80,   # +80% gasoline price
                    "NG=F": 0.50    # +50% natural gas price
                }
            },
            {
                "name": "Economic Recession (-30%)",
                "description": "Simulate economic downturn impact",
                "price_shocks": {
                    "CL=F": -0.30,  # -30% oil price
                    "BZ=F": -0.30,  # -30% Brent price
                    "NG=F": -0.25,  # -25% natural gas price
                    "RB=F": -0.35,  # -35% gasoline price
                    "HO=F": -0.30   # -30% heating oil price
                }
            }
        ]
        
        return {
            "status": "success",
            "scenarios": scenarios,
            "scenario_count": len(scenarios),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Energy crisis scenarios fetch failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Energy crisis scenarios fetch failed: {str(e)}")

@router.get("/scenarios/us-shale")
async def get_us_shale_scenarios(current_user: Dict = Depends(get_current_user)):
    """
    Get US shale-specific stress scenarios
    
    Returns:
        List of US shale stress scenarios
    """
    try:
        scenarios = [
            {
                "name": "Shale Production Surge (-40%)",
                "description": "Simulate shale production surge impact",
                "price_shocks": {
                    "CL=F": -0.40,  # -40% WTI price
                    "NG=F": -0.30,  # -30% natural gas price
                    "RB=F": -0.35   # -35% gasoline price
                }
            },
            {
                "name": "Pipeline Constraints (+25%)",
                "description": "Simulate pipeline capacity constraints",
                "price_shocks": {
                    "NG=F": 0.25,   # +25% natural gas price
                    "CL=F": 0.10,   # +10% oil price
                    "RB=F": 0.15    # +15% gasoline price
                }
            },
            {
                "name": "Regulatory Crackdown (-20%)",
                "description": "Simulate environmental regulation impact",
                "price_shocks": {
                    "CL=F": -0.20,  # -20% oil price
                    "NG=F": -0.15,  # -15% natural gas price
                    "RB=F": -0.25   # -25% gasoline price
                }
            }
        ]
        
        return {
            "status": "success",
            "scenarios": scenarios,
            "scenario_count": len(scenarios),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"US shale scenarios fetch failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"US shale scenarios fetch failed: {str(e)}")

@router.post("/metrics/portfolio-risk")
async def get_portfolio_risk_metrics(
    portfolio: List[Dict[str, Any]],
    current_user: Dict = Depends(get_current_user)
):
    """
    Get comprehensive portfolio risk metrics using Monte Carlo simulation
    
    Args:
        portfolio: List of positions with symbol, quantity, entry_price
        
    Returns:
        Comprehensive risk metrics for the portfolio
    """
    try:
        # Calculate VaR at multiple confidence levels
        var_95 = await monte_carlo_var_service.calculate_monte_carlo_var(
            portfolio=portfolio,
            confidence_level=0.95,
            num_simulations=10000
        )
        
        var_99 = await monte_carlo_var_service.calculate_monte_carlo_var(
            portfolio=portfolio,
            confidence_level=0.99,
            num_simulations=10000
        )
        
        # Get stress test scenarios
        stress_scenarios = [
            {"name": "Oil Crash", "price_shocks": {"CL=F": -0.50, "BZ=F": -0.50}},
            {"name": "Gas Spike", "price_shocks": {"NG=F": 1.00}},
            {"name": "Geopolitical", "price_shocks": {"CL=F": 0.50, "BZ=F": 0.50}}
        ]
        
        stress_test = await monte_carlo_var_service.stress_test_portfolio(
            portfolio=portfolio,
            stress_scenarios=stress_scenarios
        )
        
        return {
            "status": "success",
            "var_95": var_95,
            "var_99": var_99,
            "stress_test": stress_test,
            "risk_summary": {
                "var_95_value": var_95.get('var_results', {}).get('var_value', 0),
                "var_99_value": var_99.get('var_results', {}).get('var_value', 0),
                "expected_shortfall_95": var_95.get('var_results', {}).get('expected_shortfall', 0),
                "worst_stress_impact": min([r.get('total_impact', 0) for r in stress_test.get('stress_results', [])]) if stress_test.get('stress_results') else 0
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Portfolio risk metrics calculation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Portfolio risk metrics calculation failed: {str(e)}")
