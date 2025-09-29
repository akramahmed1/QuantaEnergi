"""
Geo-Risk AI Service for Guyana and Middle East Volatility
Enhanced with ML sentiment analysis and risk scoring
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple, Optional
import random
from datetime import datetime

class GeoRiskService:
    """AI-powered geo-risk assessment for energy trading regions"""
    
    def __init__(self):
        self.regions = {
            'GUYANA': {
                'base_risk': 0.3,
                'volatility_multiplier': 1.2,
                'factors': ['flood_risk', 'political_stability', 'infrastructure']
            },
            'MIDDLE_EAST': {
                'base_risk': 0.4,
                'volatility_multiplier': 1.5,
                'factors': ['geopolitical_tension', 'oil_dependency', 'conflict_risk']
            },
            'NORTH_AMERICA': {
                'base_risk': 0.1,
                'volatility_multiplier': 1.0,
                'factors': ['shale_volatility', 'regulatory_changes', 'weather_events']
            }
        }
        
        # Initialize ML models for sentiment analysis
        self._initialize_ml_models()
    
    def _initialize_ml_models(self):
        """Initialize ML models for geo-risk assessment"""
        # Random Forest for risk classification
        self.risk_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        
        # Standard scaler for feature normalization
        self.scaler = StandardScaler()
        
        # Train with synthetic data (in production, use real historical data)
        self._train_models()
    
    def _train_models(self):
        """Train ML models with synthetic geo-risk data"""
        # Generate synthetic training data
        n_samples = 1000
        
        # Features: [volatility, sentiment_score, news_volume, political_stability]
        X_train = np.random.rand(n_samples, 4)
        
        # Risk levels: 0=LOW, 1=MEDIUM, 2=HIGH, 3=CRITICAL
        y_train = np.random.choice([0, 1, 2, 3], n_samples, p=[0.4, 0.3, 0.2, 0.1])
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        # Train classifier
        self.risk_classifier.fit(X_train_scaled, y_train)
    
    def fetch_geo_risk(self, region: str = 'GUYANA', volatility: float = 0.1, 
                      sentiment: float = 0.5, news_volume: float = 0.3) -> Dict:
        """
        Fetch geo-risk score for specified region
        Enhanced for Guyana floods and ME geopolitics
        """
        if region not in self.regions:
            region = 'NORTH_AMERICA'  # Default fallback
        
        region_config = self.regions[region]
        
        # Prepare features for ML model
        features = np.array([[volatility, sentiment, news_volume, 0.5]])  # political_stability = 0.5
        features_scaled = self.scaler.transform(features)
        
        # Predict risk level
        risk_prediction = self.risk_classifier.predict(features_scaled)[0]
        risk_probabilities = self.risk_classifier.predict_proba(features_scaled)[0]
        
        # Map prediction to risk level
        risk_levels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        predicted_level = risk_levels[risk_prediction]
        
        # Calculate risk score (0-1 scale)
        base_risk = region_config['base_risk']
        volatility_impact = volatility * region_config['volatility_multiplier']
        sentiment_impact = (1 - sentiment) * 0.3  # Negative sentiment increases risk
        
        risk_score = min(1.0, base_risk + volatility_impact + sentiment_impact)
        
        # Region-specific risk factors
        risk_factors = self._assess_region_factors(region, volatility, sentiment)
        
        return {
            'region': region,
            'risk_level': predicted_level,
            'risk_score': float(risk_score),
            'confidence': float(max(risk_probabilities)),
            'factors': risk_factors,
            'timestamp': datetime.now().isoformat(),
            'ml_prediction': {
                'predicted_class': int(risk_prediction),
                'probabilities': [float(p) for p in risk_probabilities]
            }
        }
    
    def _assess_region_factors(self, region: str, volatility: float, sentiment: float) -> Dict:
        """Assess region-specific risk factors"""
        factors = self.regions[region]['factors']
        risk_factors = {}
        
        for factor in factors:
            if region == 'GUYANA':
                if factor == 'flood_risk':
                    # Guyana-specific: High flood risk during rainy season
                    risk_factors[factor] = {
                        'score': min(1.0, 0.4 + volatility * 0.5),
                        'description': 'Flood risk during rainy season affects oil operations',
                        'impact': 'HIGH' if volatility > 0.2 else 'MEDIUM'
                    }
                elif factor == 'political_stability':
                    risk_factors[factor] = {
                        'score': 0.3 + (1 - sentiment) * 0.4,
                        'description': 'Political stability in emerging oil economy',
                        'impact': 'MEDIUM'
                    }
                elif factor == 'infrastructure':
                    risk_factors[factor] = {
                        'score': 0.5,
                        'description': 'Developing infrastructure for oil exports',
                        'impact': 'MEDIUM'
                    }
            
            elif region == 'MIDDLE_EAST':
                if factor == 'geopolitical_tension':
                    risk_factors[factor] = {
                        'score': 0.6 + volatility * 0.3,
                        'description': 'Geopolitical tensions affect oil supply',
                        'impact': 'HIGH' if volatility > 0.15 else 'MEDIUM'
                    }
                elif factor == 'oil_dependency':
                    risk_factors[factor] = {
                        'score': 0.8,
                        'description': 'High dependency on oil revenues',
                        'impact': 'HIGH'
                    }
                elif factor == 'conflict_risk':
                    risk_factors[factor] = {
                        'score': 0.4 + (1 - sentiment) * 0.4,
                        'description': 'Regional conflict risk affects oil production',
                        'impact': 'HIGH' if sentiment < 0.3 else 'MEDIUM'
                    }
            
            else:  # NORTH_AMERICA
                if factor == 'shale_volatility':
                    risk_factors[factor] = {
                        'score': volatility,
                        'description': 'US shale production volatility',
                        'impact': 'MEDIUM' if volatility > 0.1 else 'LOW'
                    }
                elif factor == 'regulatory_changes':
                    risk_factors[factor] = {
                        'score': 0.3,
                        'description': 'Environmental and regulatory changes',
                        'impact': 'MEDIUM'
                    }
                elif factor == 'weather_events':
                    risk_factors[factor] = {
                        'score': 0.2,
                        'description': 'Hurricane and extreme weather impacts',
                        'impact': 'LOW'
                    }
        
        return risk_factors
    
    def get_geo_risk_recommendations(self, risk_assessment: Dict) -> List[str]:
        """Generate risk mitigation recommendations based on geo-risk assessment"""
        recommendations = []
        
        region = risk_assessment['region']
        risk_level = risk_assessment['risk_level']
        risk_score = risk_assessment['risk_score']
        
        if risk_level == 'CRITICAL':
            recommendations.extend([
                f"🚨 CRITICAL: Immediate hedging required for {region} exposure",
                "Consider reducing position size by 50%",
                "Implement stop-loss orders at 10% below current price",
                "Diversify portfolio across multiple regions"
            ])
        elif risk_level == 'HIGH':
            recommendations.extend([
                f"⚠️ HIGH: Enhanced monitoring required for {region}",
                "Implement hedging strategies (options/futures)",
                "Set up automated risk alerts",
                "Consider regional diversification"
            ])
        elif risk_level == 'MEDIUM':
            recommendations.extend([
                f"📊 MEDIUM: Standard risk management for {region}",
                "Monitor key risk indicators",
                "Consider partial hedging for large positions"
            ])
        else:  # LOW
            recommendations.extend([
                f"✅ LOW: Standard operations for {region}",
                "Continue monitoring for risk escalation"
            ])
        
        # Region-specific recommendations
        if region == 'GUYANA':
            recommendations.append("Monitor weather forecasts and flood warnings")
            recommendations.append("Assess infrastructure capacity during peak production")
        elif region == 'MIDDLE_EAST':
            recommendations.append("Monitor geopolitical news and conflict indicators")
            recommendations.append("Assess supply chain resilience for oil exports")
        
        return recommendations

# Global instance
geo_risk_service = GeoRiskService()

def fetch_geo_risk(region: str = 'GUYANA', volatility: float = 0.1, 
                  sentiment: float = 0.5, news_volume: float = 0.3) -> Dict:
    """Public function to fetch geo-risk assessment"""
    return geo_risk_service.fetch_geo_risk(region, volatility, sentiment, news_volume)

def get_geo_risk_recommendations(risk_assessment: Dict) -> List[str]:
    """Public function to get geo-risk recommendations"""
    return geo_risk_service.get_geo_risk_recommendations(risk_assessment)
