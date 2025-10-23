# Standard library imports
import sys
import os
from typing import List, Optional, Dict, Any

# Third-party imports
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Local imports
from ..db.session import get_db
from ..schemas.user import User
from ..core.security import get_current_user
# Add shared services to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared', 'services'))

try:
    from data_integration_service import data_integration_service
    from forecasting_service import forecasting_service
    from optimization_engine import optimization_engine
    from generative_ai_service import generative_ai_service
    from quantum_optimization_service import quantum_optimization_service
except ImportError:
    # Fallback if services not available
    data_integration_service = None
    forecasting_service = None
    optimization_engine = None
    generative_ai_service = None
    quantum_optimization_service = None

router = APIRouter(prefix="/api/energy-data", tags=["energy_data"])

# Pydantic models for requests
class ForecastRequest(BaseModel):
    commodity: str
    days: int = 7

class OptimizationRequest(BaseModel):
    region: str = "Texas"
    use_quantum: bool = False

class ScenarioSimulationRequest(BaseModel):
    scenario_type: str
    commodity: str
    region: str
    severity: str = "moderate"
    duration_days: int = 30

class PortfolioOptimizationRequest(BaseModel):
    assets: List[Dict[str, Any]]
    constraints: Dict[str, Any]
    use_quantum: bool = True

class EnergySchedulingRequest(BaseModel):
    time_periods: int = 24
    demands: List[float]
    prices: List[float]
    storage_capacity: float = 100
    constraints: Dict[str, Any] = {}

# PR2: Market Intelligence & Forecasting
@router.get("/forecast")
async def get_forecast(
    commodity: str = "crude_oil",
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get price forecast for a commodity"""
    try:
        forecast = forecasting_service.forecast_future_consumption(commodity, days)
        
        if "error" in forecast:
            raise HTTPException(status_code=400, detail=forecast["error"])
        
        # Generate insights
        insights = forecasting_service.get_forecast_insights(commodity, forecast["forecast_data"])
        
        return {
            "forecast": forecast,
            "insights": insights,
            "user_id": current_user.id,
            "timestamp": forecast.get("timestamp")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/forecast")
async def create_forecast(
    request: ForecastRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new forecast for a commodity"""
    try:
        forecast = forecasting_service.forecast_future_consumption(
            request.commodity, 
            request.days
        )
        
        if "error" in forecast:
            raise HTTPException(status_code=400, detail=forecast["error"])
        
        return {
            "forecast": forecast,
            "user_id": current_user.id,
            "timestamp": forecast.get("timestamp")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/real-time")
async def get_real_time_data(
    commodities: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get real-time market data"""
    try:
        if commodities:
            commodity_list = [c.strip() for c in commodities.split(",")]
        else:
            commodity_list = None
        
        market_data = await data_integration_service.get_real_time_market_data(commodity_list)
        
        return {
            "market_data": market_data,
            "user_id": current_user.id,
            "timestamp": market_data.get("timestamp")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# PR3: Optimization Engine
@router.get("/optimize/analysis")
async def analyze_market_conditions(
    region: str = "Texas",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze market conditions for optimization opportunities"""
    try:
        analysis = await optimization_engine.analyze_market_conditions(region)
        
        if "error" in analysis:
            raise HTTPException(status_code=400, detail=analysis["error"])
        
        return {
            "analysis": analysis,
            "user_id": current_user.id,
            "timestamp": analysis.get("timestamp")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/optimize/recommendations")
async def get_optimization_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get optimization recommendations for the current user"""
    try:
        # First analyze market conditions
        analysis = await optimization_engine.analyze_market_conditions("Texas")
        
        if "error" in analysis:
            raise HTTPException(status_code=400, detail=analysis["error"])
        
        # Generate recommendations
        recommendations = await optimization_engine.generate_recommendations(
            current_user.id, 
            analysis
        )
        
        return {
            "recommendations": recommendations,
            "user_id": current_user.id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize/execute/{recommendation_id}")
async def execute_recommendation(
    recommendation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute a specific optimization recommendation"""
    try:
        result = await optimization_engine.execute_recommendation(
            recommendation_id, 
            current_user.id
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "execution_result": result,
            "user_id": current_user.id,
            "timestamp": result.get("timestamp")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/optimize/history")
async def get_optimization_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get optimization recommendation history for the current user"""
    try:
        history = optimization_engine.get_recommendation_history(current_user.id)
        stats = optimization_engine.get_recommendation_stats(current_user.id)
        
        return {
            "history": history,
            "statistics": stats,
            "user_id": current_user.id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# PR5: Generative AI for Scenario Simulation
@router.get("/scenarios/templates")
async def get_scenario_templates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available scenario simulation templates"""
    try:
        templates = await generative_ai_service.get_scenario_templates()
        
        return {
            "templates": templates,
            "user_id": current_user.id,
            "timestamp": templates.get("timestamp")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scenarios/simulate")
async def simulate_scenario(
    request: ScenarioSimulationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Simulate a market scenario using generative AI"""
    try:
        scenario_params = {
            "scenario_type": request.scenario_type,
            "commodity": request.commodity,
            "region": request.region,
            "severity": request.severity,
            "duration_days": request.duration_days
        }
        
        simulation = await generative_ai_service.simulate_scenario(scenario_params)
        
        if "error" in simulation:
            raise HTTPException(status_code=400, detail=simulation["error"])
        
        return {
            "simulation": simulation,
            "user_id": current_user.id,
            "timestamp": simulation.get("created_at")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# PR6: Quantum Hardware Integration
@router.get("/quantum/status")
async def get_quantum_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get quantum optimization service status"""
    try:
        status = await quantum_optimization_service.get_quantum_status()
        
        return {
            "quantum_status": status,
            "user_id": current_user.id,
            "timestamp": status.get("timestamp")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quantum/optimize/portfolio")
async def optimize_portfolio_quantum(
    request: PortfolioOptimizationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Optimize portfolio using quantum or classical methods"""
    try:
        result = await quantum_optimization_service.optimize_portfolio(
            request.assets, 
            request.constraints
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "optimization_result": result,
            "user_id": current_user.id,
            "timestamp": result.get("timestamp")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quantum/optimize/energy-scheduling")
async def optimize_energy_scheduling_quantum(
    request: EnergySchedulingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Optimize energy scheduling using quantum methods"""
    try:
        energy_data = {
            "time_periods": request.time_periods,
            "demands": request.demands,
            "prices": request.prices,
            "storage_capacity": request.storage_capacity,
            "constraints": request.constraints
        }
        
        result = await quantum_optimization_service.optimize_energy_scheduling(energy_data)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "optimization_result": result,
            "user_id": current_user.id,
            "timestamp": result.get("timestamp")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quantum/compare")
async def compare_quantum_classical(
    request: PortfolioOptimizationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Compare quantum vs classical optimization results"""
    try:
        problem_data = quantum_optimization_service._prepare_portfolio_problem(
            request.assets, 
            request.constraints
        )
        
        comparison = await quantum_optimization_service.compare_quantum_classical(problem_data)
        
        if "error" in comparison:
            raise HTTPException(status_code=400, detail=comparison["error"])
        
        return {
            "comparison": comparison,
            "user_id": current_user.id,
            "timestamp": comparison.get("timestamp")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/quantum/history")
async def get_quantum_optimization_history(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get quantum optimization history"""
    try:
        history = await quantum_optimization_service.get_optimization_history(limit)
        
        return {
            "optimization_history": history,
            "user_id": current_user.id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Additional utility endpoints
@router.get("/models/status")
async def get_model_status(
    commodity: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get status of trained ML models"""
    try:
        status = forecasting_service.get_model_status(commodity)
        
        return {
            "model_status": status,
            "user_id": current_user.id,
            "timestamp": status.get("timestamp")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/models/retrain")
async def retrain_model(
    commodity: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrain ML model for a specific commodity"""
    try:
        # For now, use simulated data
        # In production, you would load actual historical data
        simulated_data = [
            {
                "price": 75.0 + (i * 0.1),
                "volume": 1000 + (i * 10),
                "timestamp": f"2025-08-{26-i:02d}T00:00:00"
            }
            for i in range(30)
        ]
        
        result = forecasting_service.retrain_model(commodity, simulated_data)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "retrain_result": result,
            "user_id": current_user.id,
            "timestamp": result.get("timestamp")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Import datetime for timestamp generation
from datetime import datetime
