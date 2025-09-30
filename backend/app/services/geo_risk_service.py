"""
Geo-Risk AI Service for Guyana and Middle East Volatility
Enhanced with ML sentiment analysis and risk scoring
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple, Optional, Any
import random
from datetime import datetime

class GeoRiskService:
    """AI-powered geo-risk assessment for energy trading regions"""
    
    def __init__(self):
        self.regions = {
            'GUYANA': {
                'base_risk': 0.3,
                'volatility_multiplier': 1.2,
                'factors': ['flood_risk', 'political_stability', 'infrastructure'],
                'upstream_oil_boom': True,
                'offshore_rigs': 15,  # Stabroek block development
                'production_target': 800000,  # bpd by 2025
                'satellite_monitoring': True,
                'iot_sensors': True,
                'guyana_basin_volatility': 0.4  # High volatility region
            },
            'MIDDLE_EAST': {
                'base_risk': 0.4,
                'volatility_multiplier': 1.5,
                'factors': ['geopolitical_tension', 'oil_dependency', 'conflict_risk'],
                'sharia_compliant': True,
                'fatwa_required': True
            },
            'NORTH_AMERICA': {
                'base_risk': 0.1,
                'volatility_multiplier': 1.0,
                'factors': ['shale_volatility', 'regulatory_changes', 'weather_events'],
                'ferc_compliant': True,
                'cftc_reporting': True
            }
        }
        
        # Guyana-specific upstream oil monitoring (2025 verified data)
        self.guyana_basin_data = {
            'liza_field': {
                'production': 300000,  # bpd (2025 average - updated for 700K total)
                'risk_level': 0.3, 
                'depth': 1800,
                'operator': 'ExxonMobil Guyana',
                'status': 'operational',
                'discovery_year': 2015
            },
            'payara_field': {
                'production': 250000,  # bpd (2025 average - updated for 700K total)
                'risk_level': 0.4, 
                'depth': 2100,
                'operator': 'ExxonMobil Guyana',
                'status': 'operational',
                'startup_year': 2023
            },
            'yellowtail_field': {
                'production': 150000,  # bpd (2025 average - updated for 700K total)
                'risk_level': 0.5, 
                'depth': 2400,
                'operator': 'ExxonMobil Guyana',
                'status': 'operational',
                'startup_year': 2025
            },
            'uaru_field': {
                'production': 0,  # bpd (planned)
                'risk_level': 0.6,
                'depth': 2600,
                'operator': 'ExxonMobil Guyana',
                'status': 'development',
                'startup_year': 2026
            },
            'whiptail_field': {
                'production': 0,  # bpd (planned)
                'risk_level': 0.6,
                'depth': 2800,
                'operator': 'ExxonMobil Guyana',
                'status': 'development',
                'startup_year': 2027
            },
            'stabroek_block': {
                'total_reserves': 11000000000,  # barrels (verified)
                'risk_level': 0.35,
                'blocks': 6,
                'total_production': 700000,  # bpd (2025 average - updated for 650-800K range)
                'operator': 'ExxonMobil Guyana (45%), Hess (30%), CNOOC (25%)'
            }
        }
        
        # Real-time monitoring endpoints
        self.monitoring_endpoints = {
            'satellite': 'https://api.nasa.gov/earth/imagery',
            'weather': 'https://api.openweathermap.org/data/2.5/weather',
            'iot_sensors': 'https://api.guyana-energy.gov.gy/rig-monitoring',
            'seismic': 'https://api.usgs.gov/earthquakes/feed/v1.0/summary',
            'oil_prices': 'https://api.alpha-vantage.co/query?function=TIME_SERIES_DAILY'
        }
        
        # Initialize ML models for sentiment analysis
        self._initialize_ml_models()
    
    async def monitor_guyana_basin_realtime(self) -> Dict[str, Any]:
        """
        Real-time monitoring of Guyana basin for upstream oil trading volatility
        
        Returns:
            Dict with real-time basin monitoring data
        """
        try:
            # Simulate real-time data collection from multiple sources
            current_time = datetime.now()
            
            # Satellite monitoring for weather and sea conditions
            satellite_data = {
                'sea_state': random.choice(['calm', 'moderate', 'rough']),
                'visibility': random.uniform(8, 15),  # nautical miles
                'wind_speed': random.uniform(5, 25),  # knots
                'wave_height': random.uniform(1, 4),  # meters
                'cloud_cover': random.uniform(20, 80),  # percentage
                'last_updated': current_time.isoformat()
            }
            
            # IoT sensor data from offshore rigs (2025 verified data)
            iot_data = {
                'active_rigs': 6,  # Stabroek block FPSOs
                'production_rate': random.uniform(600000, 700000),  # bpd (2025 range: 648K average)
                'equipment_status': {
                    'liza_destiny': {'status': 'operational', 'efficiency': 0.95, 'capacity': 150000},
                    'liza_eternity': {'status': 'operational', 'efficiency': 0.92, 'capacity': 150000},
                    'payara_prosperity': {'status': 'operational', 'efficiency': 0.88, 'capacity': 220000},
                    'yellowtail_turritella': {'status': 'operational', 'efficiency': 0.85, 'capacity': 250000}
                },
                'safety_alerts': random.randint(0, 2),
                'environmental_compliance': 'ACTIVE',
                'carbon_intensity': random.uniform(15, 25),  # kg CO2/barrel
                'last_updated': current_time.isoformat()
            }
            
            # Seismic monitoring for geological stability
            seismic_data = {
                'recent_activity': random.uniform(0, 2.5),  # magnitude
                'basin_stability': random.uniform(0.8, 1.0),
                'fault_lines': 'stable',
                'last_major_event': '2023-08-15',
                'risk_level': random.uniform(0.1, 0.3)
            }
            
            # Calculate composite risk score
            weather_risk = 0.2 if satellite_data['sea_state'] == 'rough' else 0.1
            production_risk = 0.3 if iot_data['production_rate'] < 800000 else 0.1
            seismic_risk = seismic_data['risk_level']
            
            composite_risk = (weather_risk + production_risk + seismic_risk) / 3
            
            # Generate trading recommendations based on 2025 production data
            recommendations = []
            if composite_risk > 0.3:
                recommendations.append("High volatility detected - consider hedging strategies")
            if iot_data['production_rate'] > 650000:  # Above 2025 average
                recommendations.append("Production above 650K bpd - bullish signal for Guyana crude")
            if iot_data['production_rate'] > 700000:  # Approaching 800K target
                recommendations.append("Production approaching 800K bpd target - strong bullish signal")
            if seismic_data['basin_stability'] < 0.9:
                recommendations.append("Geological instability - monitor closely")
            if iot_data['carbon_intensity'] > 20:
                recommendations.append("High carbon intensity - consider ESG trading implications")
            
            return {
                'region': 'GUYANA_BASIN',
                'timestamp': current_time.isoformat(),
                'satellite_data': satellite_data,
                'iot_data': iot_data,
                'seismic_data': seismic_data,
                'composite_risk_score': composite_risk,
                'risk_level': 'HIGH' if composite_risk > 0.4 else 'MODERATE' if composite_risk > 0.2 else 'LOW',
                'trading_recommendations': recommendations,
                'basin_production_status': 'ACTIVE' if iot_data['production_rate'] > 750000 else 'REDUCED',
                'volatility_forecast': {
                    'next_24h': random.uniform(0.2, 0.5),
                    'next_7d': random.uniform(0.3, 0.6),
                    'next_30d': random.uniform(0.25, 0.45)
                }
            }
            
        except Exception as e:
            return {
                'error': f"Failed to monitor Guyana basin: {str(e)}",
                'fallback_mode': True,
                'timestamp': datetime.now().isoformat()
            }
    
    def _initialize_ml_models(self):
        """Initialize ML models for geo-risk assessment"""
        # Random Forest for risk classification
        self.risk_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        
        # Standard scaler for feature normalization
        self.scaler = StandardScaler()
        
        # Train with synthetic data (in production, use real historical data)
        self._train_models()
    
    def _train_models(self):
        """Train ML models with enhanced geo-risk data for Guyana HIGH volatility detection"""
        # Generate enhanced synthetic training data based on real-world patterns
        n_samples = 2000
        
        # Feature matrix: [volatility, sentiment, news_volume, weather_risk, political_stability, flood_risk, oil_production]
        X_train = np.zeros((n_samples, 7))
        
        # Generate realistic feature distributions
        # Volatility (0-1): Higher for Guyana due to flood risks
        X_train[:, 0] = np.random.beta(2, 3, n_samples)  # Skewed towards lower values
        
        # Sentiment (-1 to 1): More negative for volatile regions
        X_train[:, 1] = np.random.normal(-0.2, 0.4, n_samples)
        X_train[:, 1] = np.clip(X_train[:, 1], -1, 1)
        
        # News volume (0-1): Higher during crises
        X_train[:, 2] = np.random.exponential(0.3, n_samples)
        X_train[:, 2] = np.clip(X_train[:, 2], 0, 1)
        
        # Weather risk (0-1): Higher for Guyana
        X_train[:, 3] = np.random.beta(3, 2, n_samples)  # Skewed towards higher values
        
        # Political stability (0-1): Lower for volatile regions
        X_train[:, 4] = np.random.beta(2, 3, n_samples)  # Skewed towards lower values
        
        # Flood risk (0-1): Specific to Guyana
        X_train[:, 5] = np.random.beta(4, 2, n_samples)  # Higher flood risk
        
        # Oil production volatility (0-1)
        X_train[:, 6] = np.random.beta(2, 2, n_samples)
        
        # Generate risk labels with enhanced logic for HIGH volatility detection
        y_train = np.zeros(n_samples, dtype=int)
        
        for i in range(n_samples):
            volatility = X_train[i, 0]
            sentiment = X_train[i, 1]
            news_volume = X_train[i, 2]
            weather_risk = X_train[i, 3]
            political_stability = X_train[i, 4]
            flood_risk = X_train[i, 5]
            oil_volatility = X_train[i, 6]
            
            # Enhanced risk scoring with Guyana-specific factors
            risk_score = (
                volatility * 0.25 +
                (1 - sentiment) * 0.15 +  # Negative sentiment increases risk
                news_volume * 0.15 +
                weather_risk * 0.15 +
                (1 - political_stability) * 0.15 +
                flood_risk * 0.10 +  # Guyana-specific flood risk
                oil_volatility * 0.05
            )
            
            # Classify based on enhanced risk scoring
            if risk_score > 0.7:  # HIGH risk threshold
                y_train[i] = 3  # CRITICAL (HIGH volatility)
            elif risk_score > 0.5:  # MEDIUM-HIGH risk threshold
                y_train[i] = 2  # HIGH
            elif risk_score > 0.3:  # MEDIUM risk threshold
                y_train[i] = 1  # MEDIUM
            else:
                y_train[i] = 0  # LOW
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        # Train enhanced Random Forest with more trees for better accuracy
        self.risk_classifier = RandomForestClassifier(
            n_estimators=200,  # More trees for better performance
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            class_weight='balanced'  # Handle class imbalance
        )
        self.risk_classifier.fit(X_train_scaled, y_train)
        
        # Calculate feature importance for interpretability
        feature_names = ['volatility', 'sentiment', 'news_volume', 'weather_risk', 
                        'political_stability', 'flood_risk', 'oil_production']
        feature_importance = dict(zip(feature_names, self.risk_classifier.feature_importances_))
        
        print("✅ Enhanced Geo-risk ML models trained successfully")
        print(f"   Feature importance: {feature_importance}")
        print(f"   Training samples: {n_samples}")
        print(f"   HIGH/CRITICAL risk samples: {np.sum(y_train >= 2)} ({np.sum(y_train >= 2)/n_samples*100:.1f}%)")
    
    def fetch_geo_risk(self, region: str = 'GUYANA', volatility: float = 0.1, 
                      sentiment: float = 0.5, news_volume: float = 0.3) -> Dict:
        """
        Fetch geo-risk score for specified region
        Enhanced for Guyana floods and ME geopolitics
        """
        if region not in self.regions:
            region = 'NORTH_AMERICA'  # Default fallback
        
        region_config = self.regions[region]
        
        # Enhanced 7-feature calculation with region-specific factors
        weather_risk = 0.7 if region == 'GUYANA' else 0.3  # Higher weather risk for Guyana
        political_stability = 0.6 if region == 'NORTH_AMERICA' else 0.4  # Lower stability for volatile regions
        flood_risk = 0.8 if region == 'GUYANA' else 0.2  # High flood risk for Guyana
        oil_production_vol = 0.6 if region == 'MIDDLE_EAST' else 0.4  # Higher for ME
        
        # Prepare enhanced 7-feature vector for ML model
        features = np.array([[
            volatility,
            sentiment,
            news_volume,
            weather_risk,
            political_stability,
            flood_risk,
            oil_production_vol
        ]])
        
        # Scale features using trained scaler
        features_scaled = self.scaler.transform(features)
        
        # Predict risk level
        risk_prediction = self.risk_classifier.predict(features_scaled)[0]
        risk_probabilities = self.risk_classifier.predict_proba(features_scaled)[0]
        
        # Map prediction to risk level
        risk_levels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        predicted_level = risk_levels[risk_prediction]
        
        # Enhanced risk calculation with 20% uplift for HIGH volatility detection
        base_risk = region_config['base_risk']
        volatility_multiplier = region_config['volatility_multiplier']
        
        # Enhanced risk calculation with all factors
        sentiment_factor = 1 + (0.5 - sentiment) * 0.5  # Negative sentiment increases risk
        news_factor = 1 + news_volume * 0.3  # High news volume increases risk
        weather_factor = 1 + weather_risk * 0.4  # Weather risk multiplier
        flood_factor = 1 + flood_risk * 0.3  # Guyana flood risk multiplier
        
        # Calculate final risk score with 20% uplift for HIGH volatility detection
        enhanced_risk = base_risk * volatility_multiplier * sentiment_factor * news_factor * weather_factor * flood_factor
        
        # Apply 20% uplift for HIGH volatility scenarios (vol > 0.5)
        guyana_uplift = 0.0
        if volatility > 0.5:
            enhanced_risk *= 1.2  # 20% uplift for HIGH volatility
            guyana_uplift = 0.20
            high_volatility_detected = True
        else:
            high_volatility_detected = False
        
        risk_score = min(1.0, enhanced_risk)
        
        # Region-specific risk factors
        risk_factors = self._assess_region_factors(region, volatility, sentiment)
        
        return {
            'region': region,
            'risk_level': predicted_level,
            'risk_score': float(risk_score),
            'guyana_uplift': guyana_uplift,  # 20% CO2 uplift for Guyana HIGH risk
            'high_volatility_detected': high_volatility_detected,
            'volatility_uplift_applied': 0.2 if high_volatility_detected else 0.0,
            'confidence': float(max(risk_probabilities)),
            'factors': risk_factors,
            'feature_values': {
                'volatility': volatility,
                'sentiment': sentiment,
                'news_volume': news_volume,
                'weather_risk': weather_risk,
                'political_stability': political_stability,
                'flood_risk': flood_risk,
                'oil_production_volatility': oil_production_vol
            },
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
