"""
Market Intelligence API
Phase 3: Disruptive Innovations & Market Dominance
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Any, Optional
from datetime import datetime

from ...services.market_intelligence import GlobalMarketIntelligenceNetwork, MarketIntelligenceValidator
from ...schemas.trade import (
    ApiResponse, ErrorResponse, IslamicComplianceResponse
)

router = APIRouter(prefix="/market-intelligence", tags=["Market Intelligence"])

# Initialize services
intelligence_network = GlobalMarketIntelligenceNetwork()
intelligence_validator = MarketIntelligenceValidator()


@router.post("/collect-intelligence", response_model=ApiResponse)
async def collect_market_intelligence(
    region: str,
    commodity: str,
    intelligence_type: str = "comprehensive"
):
    """Collect real-time market intelligence"""
    try:
        intelligence = intelligence_network.collect_market_intelligence(
            region, commodity, intelligence_type
        )
        return ApiResponse(
            success=True,
            data=intelligence,
            message="Market intelligence collected successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/surveillance-analysis", response_model=ApiResponse)
async def analyze_market_surveillance(
    surveillance_targets: List[str],
    analysis_period: str = "24h"
):
    """Analyze market surveillance data for anomalies"""
    try:
        surveillance = intelligence_network.analyze_market_surveillance(
            surveillance_targets, analysis_period
        )
        return ApiResponse(
            success=True,
            data=surveillance,
            message="Market surveillance analysis completed successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-forecasts", response_model=ApiResponse)
async def generate_market_forecasts(
    forecast_horizon: str,
    commodities: List[str],
    regions: List[str]
):
    """Generate market forecasts using AI/ML models"""
    try:
        forecasts = intelligence_network.generate_market_forecasts(
            forecast_horizon, commodities, regions
        )
        return ApiResponse(
            success=True,
            data=forecasts,
            message="Market forecasts generated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/monitor-regulatory-changes", response_model=ApiResponse)
async def monitor_regulatory_changes(
    jurisdictions: List[str],
    sectors: List[str]
):
    """Monitor regulatory changes across jurisdictions"""
    try:
        changes = intelligence_network.monitor_regulatory_changes(
            jurisdictions, sectors
        )
        return ApiResponse(
            success=True,
            data=changes,
            message="Regulatory changes monitoring completed successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-competitive-intelligence", response_model=ApiResponse)
async def analyze_competitive_intelligence(
    competitors: List[str],
    analysis_focus: str = "comprehensive"
):
    """Analyze competitive intelligence"""
    try:
        competitive = intelligence_network.analyze_competitive_intelligence(
            competitors, analysis_focus
        )
        return ApiResponse(
            success=True,
            data=competitive,
            message="Competitive intelligence analysis completed successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-risk-alerts", response_model=ApiResponse)
async def generate_risk_alerts(
    risk_threshold: float = 0.7,
    alert_categories: List[str] = None
):
    """Generate risk alerts based on intelligence data"""
    try:
        alerts = intelligence_network.generate_risk_alerts(
            risk_threshold, alert_categories
        )
        return ApiResponse(
            success=True,
            data=alerts,
            message="Risk alerts generated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/provide-market-insights", response_model=ApiResponse)
async def provide_market_insights(
    insight_type: str = "daily",
    focus_areas: List[str] = None
):
    """Provide comprehensive market insights"""
    try:
        insights = intelligence_network.provide_market_insights(
            insight_type, focus_areas
        )
        return ApiResponse(
            success=True,
            data=insights,
            message="Market insights provided successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/network-performance", response_model=ApiResponse)
async def get_network_performance():
    """Get network performance metrics"""
    try:
        metrics = intelligence_network.get_network_performance_metrics()
        return ApiResponse(
            success=True,
            data=metrics,
            message="Network performance metrics retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Islamic Compliance Validation Endpoints

@router.post("/islamic/validate-intelligence-quality", response_model=IslamicComplianceResponse)
async def validate_intelligence_quality(intelligence_data: Dict[str, Any]):
    """Validate intelligence data quality"""
    try:
        validation = intelligence_validator.validate_intelligence_quality(intelligence_data)
        return IslamicComplianceResponse(
            success=True,
            data=validation,
            message="Intelligence quality validation completed"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/islamic/validate-forecast-accuracy", response_model=IslamicComplianceResponse)
async def validate_forecast_accuracy(forecast_data: Dict[str, Any]):
    """Validate forecast accuracy"""
    try:
        validation = intelligence_validator.validate_forecast_accuracy(forecast_data)
        return IslamicComplianceResponse(
            success=True,
            data=validation,
            message="Forecast accuracy validation completed"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
