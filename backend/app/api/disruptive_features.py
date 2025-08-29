from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import structlog

from ..core.security import get_current_user
from ..services.forecasting_service import forecasting_service
from ..services.quantum_optimization_service import quantum_optimization_service, PortfolioAsset
from ..services.blockchain_service import blockchain_service
from ..services.iot_integration_service import iot_integration_service
from ..services.compliance_service import compliance_service, ComplianceRegion

logger = structlog.get_logger()

router = APIRouter(prefix="/api/disruptive", tags=["disruptive-features"])

# AI Forecasting Endpoints
@router.post("/ai/forecast")
async def create_ai_forecast(
    commodity: str = Query(..., description="Energy commodity to forecast"),
    days: int = Query(7, description="Number of days to forecast"),
    use_prophet: bool = Query(False, description="Use Prophet library for forecasting"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create AI-powered energy price forecast"""
    try:
        # Generate sample historical data for demonstration
        historical_data = _generate_sample_historical_data(commodity, 100)
        
        if use_prophet:
            forecast_result = forecasting_service.forecast_with_prophet(
                commodity, historical_data, days
            )
        else:
            forecast_result = forecasting_service.forecast_future_consumption(
                commodity, days
            )
        
        # Calculate ESG score
        esg_score = forecasting_service.calculate_esg_score(
            commodity, forecast_result.get("forecast_data", [])
        )
        
        # Get Grok AI insights if available
        grok_insights = None
        if hasattr(forecasting_service, 'grok_api_key') and forecasting_service.grok_api_key:
            grok_insights = "Grok AI insights would be available with proper API key"
        
        return {
            "forecast": forecast_result,
            "esg_score": esg_score,
            "grok_ai_insights": grok_insights,
            "user_id": current_user["id"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error creating AI forecast: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ai/train")
async def train_ai_model(
    commodity: str = Query(..., description="Energy commodity to train model for"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Train AI model for energy forecasting"""
    try:
        # Generate sample training data
        training_data = _generate_sample_historical_data(commodity, 200)
        
        training_result = forecasting_service.train_model(commodity, training_data)
        
        return {
            "training_result": training_result,
            "user_id": current_user["id"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error training AI model: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Quantum Optimization Endpoints
@router.post("/quantum/optimize-portfolio")
async def optimize_portfolio_quantum(
    assets: List[Dict[str, Any]],
    target_return: Optional[float] = Query(None, description="Target return for portfolio"),
    risk_tolerance: float = Query(0.5, description="Risk tolerance (0-1)"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Optimize portfolio using quantum algorithms"""
    try:
        # Convert to PortfolioAsset objects
        portfolio_assets = []
        for asset in assets:
            portfolio_assets.append(PortfolioAsset(
                symbol=asset["symbol"],
                weight=asset.get("weight", 0.0),
                expected_return=asset["expected_return"],
                volatility=asset["volatility"],
                sector=asset.get("sector", "energy"),
                region=asset.get("region", "global"),
                esg_score=asset.get("esg_score", 50.0)
            ))
        
        optimization_result = quantum_optimization_service.optimize_portfolio_quantum(
            portfolio_assets, target_return, risk_tolerance
        )
        
        return {
            "optimization_result": optimization_result,
            "user_id": current_user["id"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in quantum portfolio optimization: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/quantum/risk-assessment")
async def quantum_risk_assessment(
    portfolio_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Perform quantum-enhanced risk assessment"""
    try:
        risk_result = quantum_optimization_service.quantum_risk_assessment(portfolio_data)
        
        return {
            "risk_assessment": risk_result,
            "user_id": current_user["id"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in quantum risk assessment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/quantum/status")
async def get_quantum_status(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get quantum computing service status"""
    try:
        status = quantum_optimization_service.get_quantum_status()
        
        return {
            "quantum_status": status,
            "user_id": current_user["id"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting quantum status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Blockchain Smart Contracts Endpoints
@router.post("/blockchain/deploy-energy-contract")
async def deploy_energy_trade_contract(
    owner: str = Query(..., description="Contract owner address"),
    participants: List[str] = Query(..., description="Contract participants"),
    energy_type: str = Query(..., description="Type of energy being traded"),
    total_volume: float = Query(..., description="Total volume for contract"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Deploy energy trading smart contract"""
    try:
        contract_result = blockchain_service.deploy_energy_trade_contract(
            owner, participants, energy_type, total_volume
        )
        
        return {
            "contract_deployment": contract_result,
            "user_id": current_user["id"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error deploying energy contract: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/blockchain/execute-energy-trade")
async def execute_energy_trade(
    contract_id: str = Query(..., description="Smart contract ID"),
    seller: str = Query(..., description="Seller address"),
    buyer: str = Query(..., description="Buyer address"),
    energy_amount: float = Query(..., description="Amount of energy to trade"),
    price_per_unit: float = Query(..., description="Price per unit of energy"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Execute energy trade on blockchain"""
    try:
        trade_result = blockchain_service.execute_energy_trade(
            contract_id, seller, buyer, energy_amount, price_per_unit
        )
        
        return {
            "energy_trade": trade_result,
            "user_id": current_user["id"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error executing energy trade: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/blockchain/carbon-credits")
async def create_carbon_credit_contract(
    issuer: str = Query(..., description="Credit issuer address"),
    credit_amount: float = Query(..., description="Amount of carbon credits"),
    project_type: str = Query(..., description="Type of carbon project"),
    verification_data: Dict[str, Any] = Body(..., description="Verification data"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create carbon credit smart contract"""
    try:
        credit_result = blockchain_service.create_carbon_credit_contract(
            issuer, credit_amount, project_type, verification_data
        )
        
        return {
            "carbon_credit_contract": credit_result,
            "user_id": current_user["id"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error creating carbon credit contract: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/blockchain/contract/{contract_id}")
async def get_contract_history(
    contract_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get smart contract transaction history"""
    try:
        contract_history = blockchain_service.get_contract_history(contract_id)
        
        return {
            "contract_history": contract_history,
            "user_id": current_user["id"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting contract history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/blockchain/status")
async def get_blockchain_status(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get blockchain service status"""
    try:
        status = blockchain_service.get_blockchain_status()
        
        return {
            "blockchain_status": status,
            "user_id": current_user["id"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting blockchain status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# IoT Integration Endpoints
@router.get("/iot/grid-data/{location}")
async def get_real_time_grid_data(
    location: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get real-time grid data from IoT sensors"""
    try:
        grid_data = await iot_integration_service.get_real_time_grid_data(location)
        
        # Analyze grid stability
        stability_analysis = await iot_integration_service.analyze_grid_stability(grid_data)
        
        return {
            "grid_data": grid_data,
            "stability_analysis": stability_analysis,
            "user_id": current_user["id"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting grid data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/iot/weather")
async def get_weather_data(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get weather data for energy optimization"""
    try:
        weather_data = await iot_integration_service.get_weather_data(lat, lon)
        
        return {
            "weather_data": weather_data,
            "user_id": current_user["id"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting weather data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/iot/solar-radiation")
async def get_solar_radiation_data(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get solar radiation data for renewable energy optimization"""
    try:
        solar_data = await iot_integration_service.get_solar_radiation_data(lat, lon)
        
        return {
            "solar_data": solar_data,
            "user_id": current_user["id"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting solar radiation data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/iot/sensor-network-status")
async def get_sensor_network_status(
    network_id: str = Query("main", description="Sensor network ID"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get IoT sensor network status"""
    try:
        network_status = await iot_integration_service.get_sensor_network_status(network_id)
        
        return {
            "sensor_network_status": network_status,
            "user_id": current_user["id"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting sensor network status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/iot/sensor-alerts")
async def get_sensor_alerts(
    sensor_type: Optional[str] = Query(None, description="Type of sensor alerts"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get active sensor alerts"""
    try:
        alerts = await iot_integration_service.get_sensor_alerts(sensor_type)
        
        return {
            "sensor_alerts": alerts,
            "user_id": current_user["id"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting sensor alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/iot/status")
async def get_iot_status(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get IoT integration service status"""
    try:
        status = iot_integration_service.get_iot_status()
        
        return {
            "iot_status": status,
            "user_id": current_user["id"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting IoT status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Compliance Endpoints
@router.post("/compliance/check")
async def check_compliance(
    trading_data: Dict[str, Any],
    regions: Optional[List[str]] = Query(None, description="Compliance regions to check"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Check compliance across multiple regions"""
    try:
        if regions:
            # Convert string regions to ComplianceRegion enum
            compliance_regions = []
            for region_str in regions:
                try:
                    compliance_regions.append(ComplianceRegion(region_str))
                except ValueError:
                    logger.warning(f"Invalid region: {region_str}")
        else:
            compliance_regions = None
        
        compliance_result = compliance_service.comprehensive_compliance_check(
            trading_data, compliance_regions
        )
        
        return {
            "compliance_check": compliance_result,
            "user_id": current_user["id"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error checking compliance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compliance/history")
async def get_compliance_history(
    region: Optional[str] = Query(None, description="Filter by compliance region"),
    limit: int = Query(100, description="Maximum number of records to return"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get compliance check history"""
    try:
        history = compliance_service.get_compliance_history(region, limit)
        
        return {
            "compliance_history": history,
            "user_id": current_user["id"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting compliance history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compliance/status")
async def get_compliance_status(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get compliance service status"""
    try:
        status = compliance_service.get_compliance_status()
        
        return {
            "compliance_status": status,
            "user_id": current_user["id"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting compliance status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Utility function to generate sample historical data
def _generate_sample_historical_data(commodity: str, data_points: int) -> List[Dict[str, Any]]:
    """Generate sample historical data for testing"""
    import random
    from datetime import datetime, timedelta
    
    data = []
    base_price = {"crude_oil": 80.0, "natural_gas": 3.5, "coal": 120.0, "renewables": 0.05}
    base_price = base_price.get(commodity.lower(), 50.0)
    
    start_time = datetime.now() - timedelta(days=data_points)
    
    for i in range(data_points):
        timestamp = start_time + timedelta(hours=i)
        
        # Simulate price variations
        price_variation = random.uniform(-0.1, 0.1)
        price = base_price * (1 + price_variation)
        
        # Simulate volume
        volume = random.uniform(100, 1000)
        
        data.append({
            "timestamp": timestamp.isoformat(),
            "price": round(price, 2),
            "volume": round(volume, 2)
        })
    
    return data
