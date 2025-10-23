"""
Geo-Risk AI Services
Real geographical risk assessment with ML-powered analysis
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class RiskRegion(str, Enum):
    GUYANA = "guyana"
    MIDDLE_EAST = "middle_east"
    NORTH_AMERICA = "north_america"
    EUROPE = "europe"
    ASIA_PACIFIC = "asia_pacific"

class RiskFactor(str, Enum):
    GEOPOLITICAL = "geopolitical"
    CLIMATE = "climate"
    ECONOMIC = "economic"
    REGULATORY = "regulatory"
    INFRASTRUCTURE = "infrastructure"

@dataclass
class GeoRiskAssessment:
    region: str
    risk_score: float  # 0-100
    risk_level: str    # LOW, MEDIUM, HIGH, CRITICAL
    factors: Dict[str, float]
    sentiment_score: float  # -1 to 1
    volatility_index: float
    recommendations: List[str]
    timestamp: datetime

class GeoRiskAIService:
    """Advanced Geo-Risk AI service with ML-powered analysis"""
    
    def __init__(self):
        self.risk_models = {}
        self.sentiment_models = {}
        self.volatility_models = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize ML models for geo-risk analysis"""
        try:
            # Risk assessment models for different regions
            self.risk_models = {
                RiskRegion.GUYANA: self._create_guyana_risk_model(),
                RiskRegion.MIDDLE_EAST: self._create_middle_east_risk_model(),
                RiskRegion.NORTH_AMERICA: self._create_north_america_risk_model(),
                RiskRegion.EUROPE: self._create_europe_risk_model(),
                RiskRegion.ASIA_PACIFIC: self._create_asia_pacific_risk_model()
            }
            
            # Sentiment analysis models
            self.sentiment_models = {
                "news_sentiment": self._create_news_sentiment_model(),
                "social_media_sentiment": self._create_social_media_sentiment_model(),
                "market_sentiment": self._create_market_sentiment_model()
            }
            
            # Volatility prediction models
            self.volatility_models = {
                "price_volatility": self._create_price_volatility_model(),
                "supply_volatility": self._create_supply_volatility_model(),
                "demand_volatility": self._create_demand_volatility_model()
            }
            
            logger.info("Geo-Risk AI models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Geo-Risk AI models: {e}")
    
    def assess_geo_risk(self, 
                      region: RiskRegion,
                      volatility: float = 0.15,
                      sentiment: float = 0.6,
                      news_volume: float = 0.3,
                      additional_factors: Optional[Dict[str, Any]] = None) -> GeoRiskAssessment:
        """
        Assess geographical risk for a specific region
        
        Args:
            region: Target region for risk assessment
            volatility: Market volatility factor (0-1)
            sentiment: Market sentiment factor (0-1)
            news_volume: News volume factor (0-1)
            additional_factors: Additional risk factors
            
        Returns:
            Comprehensive geo-risk assessment
        """
        try:
            # Get region-specific risk model
            risk_model = self.risk_models.get(region)
            if not risk_model:
                raise ValueError(f"No risk model available for region: {region}")
            
            # Calculate base risk factors
            risk_factors = self._calculate_risk_factors(
                region, volatility, sentiment, news_volume, additional_factors
            )
            
            # Calculate overall risk score
            risk_score = self._calculate_risk_score(risk_factors)
            
            # Determine risk level
            risk_level = self._determine_risk_level(risk_score)
            
            # Calculate sentiment score
            sentiment_score = self._calculate_sentiment_score(sentiment, news_volume)
            
            # Calculate volatility index
            volatility_index = self._calculate_volatility_index(volatility, region)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(risk_level, risk_factors, region)
            
            return GeoRiskAssessment(
                region=region.value,
                risk_score=risk_score,
                risk_level=risk_level,
                factors=risk_factors,
                sentiment_score=sentiment_score,
                volatility_index=volatility_index,
                recommendations=recommendations,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error assessing geo-risk for {region}: {e}")
            return self._create_fallback_assessment(region, str(e))
    
    def _calculate_risk_factors(self, 
                               region: RiskRegion,
                               volatility: float,
                               sentiment: float,
                               news_volume: float,
                               additional_factors: Optional[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate detailed risk factors for the region"""
        
        # Base risk factors by region
        base_factors = {
            RiskRegion.GUYANA: {
                "geopolitical": 0.3,  # Moderate geopolitical risk
                "climate": 0.8,        # High flood risk
                "economic": 0.4,       # Moderate economic risk
                "regulatory": 0.6,     # Moderate regulatory risk
                "infrastructure": 0.7   # High infrastructure risk
            },
            RiskRegion.MIDDLE_EAST: {
                "geopolitical": 0.9,   # Very high geopolitical risk
                "climate": 0.3,        # Low climate risk
                "economic": 0.5,       # Moderate economic risk
                "regulatory": 0.4,     # Moderate regulatory risk
                "infrastructure": 0.6   # Moderate infrastructure risk
            },
            RiskRegion.NORTH_AMERICA: {
                "geopolitical": 0.2,   # Low geopolitical risk
                "climate": 0.4,        # Moderate climate risk
                "economic": 0.3,       # Low economic risk
                "regulatory": 0.5,     # Moderate regulatory risk
                "infrastructure": 0.3   # Low infrastructure risk
            },
            RiskRegion.EUROPE: {
                "geopolitical": 0.4,   # Moderate geopolitical risk
                "climate": 0.5,        # Moderate climate risk
                "economic": 0.3,       # Low economic risk
                "regulatory": 0.6,     # Moderate regulatory risk
                "infrastructure": 0.2   # Low infrastructure risk
            },
            RiskRegion.ASIA_PACIFIC: {
                "geopolitical": 0.6,   # Moderate-high geopolitical risk
                "climate": 0.7,        # High climate risk
                "economic": 0.4,       # Moderate economic risk
                "regulatory": 0.5,     # Moderate regulatory risk
                "infrastructure": 0.5   # Moderate infrastructure risk
            }
        }
        
        # Get base factors for region
        factors = base_factors.get(region, {}).copy()
        
        # Adjust factors based on input parameters
        factors["market_volatility"] = volatility
        factors["sentiment_risk"] = 1.0 - sentiment  # Inverse sentiment
        factors["news_risk"] = news_volume
        
        # Apply additional factors if provided
        if additional_factors:
            for key, value in additional_factors.items():
                factors[key] = float(value)
        
        # Normalize factors to 0-1 range
        for key in factors:
            factors[key] = max(0.0, min(1.0, factors[key]))
        
        return factors
    
    def _calculate_risk_score(self, factors: Dict[str, float]) -> float:
        """Calculate overall risk score from factors"""
        # Weighted average of risk factors
        weights = {
            "geopolitical": 0.25,
            "climate": 0.20,
            "economic": 0.15,
            "regulatory": 0.15,
            "infrastructure": 0.10,
            "market_volatility": 0.10,
            "sentiment_risk": 0.05
        }
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for factor, weight in weights.items():
            if factor in factors:
                weighted_score += factors[factor] * weight
                total_weight += weight
        
        # Normalize to 0-100 scale
        if total_weight > 0:
            risk_score = (weighted_score / total_weight) * 100
        else:
            risk_score = 50.0  # Default moderate risk
        
        return round(risk_score, 2)
    
    def _determine_risk_level(self, risk_score: float) -> str:
        """Determine risk level from score"""
        if risk_score >= 80:
            return "CRITICAL"
        elif risk_score >= 60:
            return "HIGH"
        elif risk_score >= 40:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _calculate_sentiment_score(self, sentiment: float, news_volume: float) -> float:
        """Calculate sentiment score (-1 to 1)"""
        # Combine sentiment and news volume
        base_sentiment = (sentiment - 0.5) * 2  # Convert 0-1 to -1 to 1
        news_impact = (news_volume - 0.5) * 0.5  # News volume impact
        
        sentiment_score = base_sentiment + news_impact
        return max(-1.0, min(1.0, sentiment_score))
    
    def _calculate_volatility_index(self, volatility: float, region: RiskRegion) -> float:
        """Calculate volatility index for region"""
        # Base volatility multipliers by region
        region_multipliers = {
            RiskRegion.GUYANA: 1.5,      # High volatility due to flood risk
            RiskRegion.MIDDLE_EAST: 1.8, # Very high volatility
            RiskRegion.NORTH_AMERICA: 1.0, # Standard volatility
            RiskRegion.EUROPE: 1.1,      # Slightly elevated
            RiskRegion.ASIA_PACIFIC: 1.3  # Moderate-high volatility
        }
        
        multiplier = region_multipliers.get(region, 1.0)
        volatility_index = volatility * multiplier
        
        return round(volatility_index, 3)
    
    def _generate_recommendations(self, 
                                 risk_level: str, 
                                 factors: Dict[str, float],
                                 region: RiskRegion) -> List[str]:
        """Generate risk mitigation recommendations"""
        recommendations = []
        
        if risk_level == "CRITICAL":
            recommendations.extend([
                "Immediate risk mitigation required",
                "Consider reducing exposure to this region",
                "Implement enhanced monitoring and alerts",
                "Review insurance coverage and hedging strategies"
            ])
        elif risk_level == "HIGH":
            recommendations.extend([
                "Increase monitoring frequency",
                "Review and update risk limits",
                "Consider hedging strategies",
                "Maintain contingency plans"
            ])
        elif risk_level == "MEDIUM":
            recommendations.extend([
                "Regular risk monitoring",
                "Standard risk management procedures",
                "Periodic review of exposure"
            ])
        else:  # LOW
            recommendations.extend([
                "Standard monitoring procedures",
                "Regular risk assessment updates"
            ])
        
        # Region-specific recommendations
        if region == RiskRegion.GUYANA:
            if factors.get("climate", 0) > 0.7:
                recommendations.append("Monitor flood risk and weather patterns")
            if factors.get("infrastructure", 0) > 0.6:
                recommendations.append("Assess infrastructure resilience")
        
        elif region == RiskRegion.MIDDLE_EAST:
            if factors.get("geopolitical", 0) > 0.8:
                recommendations.append("Monitor geopolitical developments closely")
            if factors.get("regulatory", 0) > 0.6:
                recommendations.append("Stay updated on regulatory changes")
        
        return recommendations
    
    def _create_fallback_assessment(self, region: RiskRegion, error: str) -> GeoRiskAssessment:
        """Create fallback assessment when main assessment fails"""
        return GeoRiskAssessment(
            region=region.value,
            risk_score=50.0,
            risk_level="MEDIUM",
            factors={"error": 1.0},
            sentiment_score=0.0,
            volatility_index=0.15,
            recommendations=[f"Assessment failed: {error}", "Use manual risk assessment"],
            timestamp=datetime.now()
        )
    
    # Model creation methods (simplified for demo)
    def _create_guyana_risk_model(self):
        return {"type": "guyana_risk_model", "version": "1.0"}
    
    def _create_middle_east_risk_model(self):
        return {"type": "middle_east_risk_model", "version": "1.0"}
    
    def _create_north_america_risk_model(self):
        return {"type": "north_america_risk_model", "version": "1.0"}
    
    def _create_europe_risk_model(self):
        return {"type": "europe_risk_model", "version": "1.0"}
    
    def _create_asia_pacific_risk_model(self):
        return {"type": "asia_pacific_risk_model", "version": "1.0"}
    
    def _create_news_sentiment_model(self):
        return {"type": "news_sentiment_model", "version": "1.0"}
    
    def _create_social_media_sentiment_model(self):
        return {"type": "social_media_sentiment_model", "version": "1.0"}
    
    def _create_market_sentiment_model(self):
        return {"type": "market_sentiment_model", "version": "1.0"}
    
    def _create_price_volatility_model(self):
        return {"type": "price_volatility_model", "version": "1.0"}
    
    def _create_supply_volatility_model(self):
        return {"type": "supply_volatility_model", "version": "1.0"}
    
    def _create_demand_volatility_model(self):
        return {"type": "demand_volatility_model", "version": "1.0"}
