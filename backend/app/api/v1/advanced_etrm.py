"""
Advanced ETRM/CTRM API Endpoints
Comprehensive API for multi-region energy trading
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime
import logging

from ...services.advanced_etrm_features import AdvancedETRMService, RegionalETRMFeatures
from ...services.advanced_risk_management import AdvancedRiskManager
from ...services.advanced_trading_engine import AdvancedTradingEngine
from ...services.comprehensive_compliance import ComprehensiveComplianceEngine
from ...schemas.trade import ApiResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/etrm", tags=["Advanced ETRM"])

# Initialize services
etrm_service = AdvancedETRMService()
risk_manager = AdvancedRiskManager()
trading_engine = AdvancedTradingEngine()
compliance_engine = ComprehensiveComplianceEngine()


class TradingInstrumentRequest(BaseModel):
    """Request model for trading instruments"""
    region: str
    commodity_type: Optional[str] = None


class OrderRequest(BaseModel):
    """Request model for trading orders"""
    instrument_id: str
    side: str
    order_type: str
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: str = "GTC"
    region: str = "US"
    is_sharia_compliant: bool = False


class RiskAnalysisRequest(BaseModel):
    """Request model for risk analysis"""
    positions: List[Dict[str, Any]]
    region: str
    confidence_level: float = 0.95


class ComplianceCheckRequest(BaseModel):
    """Request model for compliance checking"""
    region: str
    data: Dict[str, Any]


@router.get("/instruments", response_model=ApiResponse)
async def get_trading_instruments(
    region: str = Query(..., description="Trading region"),
    commodity_type: Optional[str] = Query(None, description="Commodity type filter")
):
    """Get available trading instruments for a region"""
    try:
        instruments = etrm_service.get_available_instruments(region, commodity_type)
        
        return ApiResponse(
            success=True,
            data={
                "instruments": [
                    {
                        "instrument_id": inst.instrument_id,
                        "name": inst.name,
                        "commodity_type": inst.commodity_type.value,
                        "market_type": inst.market_type.value,
                        "venue": inst.venue.value,
                        "region": inst.region,
                        "contract_specs": inst.contract_specs,
                        "pricing_model": inst.pricing_model,
                        "settlement_type": inst.settlement_type,
                        "is_sharia_compliant": inst.is_sharia_compliant
                    }
                    for inst in instruments
                ],
                "total_count": len(instruments),
                "region": region
            },
            message=f"Retrieved {len(instruments)} instruments for {region}"
        )
    except Exception as e:
        logger.error(f"Error getting instruments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/orders", response_model=ApiResponse)
async def create_trading_order(order_request: OrderRequest):
    """Create a new trading order"""
    try:
        order_data = order_request.dict()
        result = trading_engine.create_order(order_data)
        
        return ApiResponse(
            success=result["success"],
            data=result if result["success"] else None,
            message="Order created successfully" if result["success"] else result.get("error", "Order creation failed")
        )
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/risk/analysis", response_model=ApiResponse)
async def analyze_risk(risk_request: RiskAnalysisRequest):
    """Perform comprehensive risk analysis"""
    try:
        var_results = risk_manager.calculate_var(
            risk_request.positions, 
            risk_request.confidence_level
        )
        
        credit_results = risk_manager.calculate_credit_exposure([
            {"id": "cp1", "exposure": 1000000, "credit_rating": "A"}
        ])
        
        limit_results = risk_manager.monitor_risk_limits(
            risk_request.positions, 
            risk_request.region
        )
        
        return ApiResponse(
            success=True,
            data={
                "var_analysis": var_results,
                "credit_analysis": credit_results,
                "limit_monitoring": limit_results,
                "region": risk_request.region
            },
            message="Risk analysis completed successfully"
        )
    except Exception as e:
        logger.error(f"Error analyzing risk: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compliance/check", response_model=ApiResponse)
async def check_compliance(compliance_request: ComplianceCheckRequest):
    """Check compliance for a specific region"""
    try:
        result = compliance_engine.check_compliance(
            compliance_request.region,
            compliance_request.data
        )
        
        return ApiResponse(
            success=True,
            data=result,
            message=f"Compliance check completed for {compliance_request.region}"
        )
    except Exception as e:
        logger.error(f"Error checking compliance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compliance/reports", response_model=ApiResponse)
async def generate_compliance_report(
    region: str = Query(..., description="Compliance region"),
    report_type: str = Query(..., description="Report type"),
    data: Dict[str, Any] = {}
):
    """Generate compliance report for specific region and type"""
    try:
        result = compliance_engine.generate_compliance_report(region, report_type, data)
        
        return ApiResponse(
            success=True,
            data=result,
            message=f"Compliance report generated for {region} - {report_type}"
        )
    except Exception as e:
        logger.error(f"Error generating compliance report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trading/algorithmic", response_model=ApiResponse)
async def execute_algorithmic_strategy(strategy_data: Dict[str, Any]):
    """Execute algorithmic trading strategy"""
    try:
        result = trading_engine.execute_algorithmic_strategy(strategy_data)
        
        return ApiResponse(
            success=True,
            data=result,
            message="Algorithmic strategy executed successfully"
        )
    except Exception as e:
        logger.error(f"Error executing algorithmic strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market-data", response_model=ApiResponse)
async def get_market_data(
    instrument_ids: List[str] = Query(..., description="Instrument IDs")
):
    """Get market data for instruments"""
    try:
        result = trading_engine.get_market_data(instrument_ids)
        
        return ApiResponse(
            success=True,
            data=result,
            message=f"Market data retrieved for {len(instrument_ids)} instruments"
        )
    except Exception as e:
        logger.error(f"Error getting market data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trading/pnl", response_model=ApiResponse)
async def calculate_pnl(
    positions: List[Dict[str, Any]],
    market_prices: Dict[str, float]
):
    """Calculate profit and loss for positions"""
    try:
        result = trading_engine.calculate_pnl(positions, market_prices)
        
        return ApiResponse(
            success=True,
            data=result,
            message="PnL calculation completed successfully"
        )
    except Exception as e:
        logger.error(f"Error calculating PnL: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/regional-features/{region}", response_model=ApiResponse)
async def get_regional_features(region: str):
    """Get regional-specific ETRM features"""
    try:
        if region.lower() == "me":
            features = RegionalETRMFeatures.get_middle_east_features()
        elif region.lower() == "us":
            features = RegionalETRMFeatures.get_us_features()
        elif region.lower() in ["eu", "europe"]:
            features = RegionalETRMFeatures.get_european_features()
        elif region.lower() == "guyana":
            features = RegionalETRMFeatures.get_guyana_features()
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported region: {region}")
        
        return ApiResponse(
            success=True,
            data=features,
            message=f"Regional features retrieved for {region}"
        )
    except Exception as e:
        logger.error(f"Error getting regional features: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/risk/stress-test", response_model=ApiResponse)
async def run_stress_tests(
    portfolio: List[Dict[str, Any]],
    scenarios: List[str] = Query(..., description="Stress test scenarios")
):
    """Run stress tests on portfolio"""
    try:
        result = risk_manager.run_stress_tests(portfolio, scenarios)
        
        return ApiResponse(
            success=True,
            data=result,
            message=f"Stress tests completed for {len(scenarios)} scenarios"
        )
    except Exception as e:
        logger.error(f"Error running stress tests: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/risk/report/{region}", response_model=ApiResponse)
async def generate_risk_report(
    region: str,
    positions: List[Dict[str, Any]] = []
):
    """Generate comprehensive risk report"""
    try:
        result = risk_manager.generate_risk_report(region, positions)
        
        return ApiResponse(
            success=True,
            data=result,
            message=f"Risk report generated for {region}"
        )
    except Exception as e:
        logger.error(f"Error generating risk report: {e}")
        raise HTTPException(status_code=500, detail=str(e))
