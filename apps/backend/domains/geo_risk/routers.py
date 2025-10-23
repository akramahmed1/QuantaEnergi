"""
Geo-Risk AI API Routers
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from ..base import get_db
from .services import GeoRiskAIService, RiskRegion

router = APIRouter(prefix="/geo-risk", tags=["Geo-Risk AI"])

@router.post("/assess")
async def assess_geo_risk(
    region: RiskRegion = Query(..., description="Target region for risk assessment"),
    volatility: float = Query(0.15, ge=0.0, le=1.0, description="Market volatility factor"),
    sentiment: float = Query(0.6, ge=0.0, le=1.0, description="Market sentiment factor"),
    news_volume: float = Query(0.3, ge=0.0, le=1.0, description="News volume factor"),
    additional_factors: Dict[str, Any] = None,
    db: Session = Depends(get_db)
):
    """Assess geographical risk for a specific region using AI"""
    geo_risk_service = GeoRiskAIService()
    assessment = geo_risk_service.assess_geo_risk(
        region, volatility, sentiment, news_volume, additional_factors
    )
    
    return {
        "success": True,
        "assessment": {
            "region": assessment.region,
            "risk_score": assessment.risk_score,
            "risk_level": assessment.risk_level,
            "factors": assessment.factors,
            "sentiment_score": assessment.sentiment_score,
            "volatility_index": assessment.volatility_index,
            "recommendations": assessment.recommendations,
            "timestamp": assessment.timestamp.isoformat()
        }
    }

@router.get("/regions")
async def get_supported_regions():
    """Get list of supported geo-risk regions"""
    return {
        "regions": [
            {
                "code": "guyana",
                "name": "Guyana",
                "description": "South American oil production with flood risk factors",
                "risk_factors": ["climate", "infrastructure", "geopolitical"]
            },
            {
                "code": "middle_east",
                "name": "Middle East",
                "description": "Traditional oil region with geopolitical risk factors",
                "risk_factors": ["geopolitical", "economic", "regulatory"]
            },
            {
                "code": "north_america",
                "name": "North America",
                "description": "US shale production with regulatory risk factors",
                "risk_factors": ["regulatory", "economic", "infrastructure"]
            },
            {
                "code": "europe",
                "name": "Europe",
                "description": "European energy markets with regulatory compliance",
                "risk_factors": ["regulatory", "geopolitical", "economic"]
            },
            {
                "code": "asia_pacific",
                "name": "Asia Pacific",
                "description": "Asian energy markets with climate and geopolitical risks",
                "risk_factors": ["climate", "geopolitical", "economic"]
            }
        ]
    }

@router.get("/risk-factors")
async def get_risk_factors():
    """Get available risk factors for geo-risk assessment"""
    return {
        "risk_factors": [
            {
                "factor": "geopolitical",
                "description": "Political stability and international relations",
                "weight": 0.25
            },
            {
                "factor": "climate",
                "description": "Weather patterns and climate change impacts",
                "weight": 0.20
            },
            {
                "factor": "economic",
                "description": "Economic stability and market conditions",
                "weight": 0.15
            },
            {
                "factor": "regulatory",
                "description": "Regulatory environment and compliance requirements",
                "weight": 0.15
            },
            {
                "factor": "infrastructure",
                "description": "Physical infrastructure and logistics",
                "weight": 0.10
            },
            {
                "factor": "market_volatility",
                "description": "Market volatility and price fluctuations",
                "weight": 0.10
            },
            {
                "factor": "sentiment_risk",
                "description": "Market sentiment and investor confidence",
                "weight": 0.05
            }
        ]
    }
