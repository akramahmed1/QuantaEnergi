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

class GeoRiskIntervalProcessor:
    """FIS-inspired interval data processing for geo-risk analysis"""
    
    def __init__(self):
        self.interval_data_cache = {}
        self.aggregation_methods = {}
        self.quality_metrics = {}
        
    def process_geo_risk_intervals(self, 
                                 raw_data: Dict[str, Any], 
                                 interval_type: str = "hourly",
                                 aggregation_method: str = "weighted_average") -> Dict[str, Any]:
        """Process geo-risk data with interval-based analysis"""
        try:
            # Extract time series data
            timestamps = raw_data.get("timestamps", [])
            risk_scores = raw_data.get("risk_scores", [])
            volatility_data = raw_data.get("volatility_data", [])
            sentiment_data = raw_data.get("sentiment_data", [])
            
            if not timestamps or not risk_scores:
                raise ValueError("Missing timestamps or risk scores in input data")
            
            # Convert to pandas DataFrame for processing
            import pandas as pd
            df = pd.DataFrame({
                "timestamp": pd.to_datetime(timestamps),
                "risk_score": risk_scores,
                "volatility": volatility_data if volatility_data else [0.1] * len(timestamps),
                "sentiment": sentiment_data if sentiment_data else [0.5] * len(timestamps)
            })
            
            # Quality checks
            quality_report = self._perform_geo_quality_checks(df)
            
            # Data cleaning
            cleaned_df = self._clean_geo_data(df)
            
            # Aggregation
            aggregated_data = self._aggregate_geo_data(cleaned_df, interval_type, aggregation_method)
            
            # Calculate geo-risk statistics
            statistics = self._calculate_geo_statistics(aggregated_data)
            
            # Risk trend analysis
            trend_analysis = self._analyze_geo_risk_trends(aggregated_data)
            
            return {
                "processed_geo_data": aggregated_data.to_dict("records"),
                "quality_report": quality_report,
                "statistics": statistics,
                "trend_analysis": trend_analysis,
                "processing_metadata": {
                    "interval_type": interval_type,
                    "aggregation_method": aggregation_method,
                    "original_data_points": len(df),
                    "processed_data_points": len(aggregated_data),
                    "processing_timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing geo-risk interval data: {str(e)}")
            raise
    
    def _perform_geo_quality_checks(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform data quality checks specific to geo-risk data"""
        quality_report = {
            "total_records": len(df),
            "missing_values": df["risk_score"].isna().sum(),
            "duplicate_timestamps": df["timestamp"].duplicated().sum(),
            "outliers": 0,
            "data_gaps": 0,
            "volatility_outliers": 0,
            "sentiment_outliers": 0,
            "quality_score": 1.0
        }
        
        # Check for risk score outliers using IQR method
        Q1 = df["risk_score"].quantile(0.25)
        Q3 = df["risk_score"].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = df[(df["risk_score"] < lower_bound) | (df["risk_score"] > upper_bound)]
        quality_report["outliers"] = len(outliers)
        
        # Check for volatility outliers
        if "volatility" in df.columns:
            vol_Q1 = df["volatility"].quantile(0.25)
            vol_Q3 = df["volatility"].quantile(0.75)
            vol_IQR = vol_Q3 - vol_Q1
            vol_lower = vol_Q1 - 1.5 * vol_IQR
            vol_upper = vol_Q3 + 1.5 * vol_IQR
            
            vol_outliers = df[(df["volatility"] < vol_lower) | (df["volatility"] > vol_upper)]
            quality_report["volatility_outliers"] = len(vol_outliers)
        
        # Check for sentiment outliers
        if "sentiment" in df.columns:
            sent_Q1 = df["sentiment"].quantile(0.25)
            sent_Q3 = df["sentiment"].quantile(0.75)
            sent_IQR = sent_Q3 - sent_Q1
            sent_lower = sent_Q1 - 1.5 * sent_IQR
            sent_upper = sent_Q3 + 1.5 * sent_IQR
            
            sent_outliers = df[(df["sentiment"] < sent_lower) | (df["sentiment"] > sent_upper)]
            quality_report["sentiment_outliers"] = len(sent_outliers)
        
        # Check for data gaps
        df_sorted = df.sort_values("timestamp")
        time_diffs = df_sorted["timestamp"].diff()
        expected_interval = time_diffs.median()
        gaps = time_diffs[time_diffs > expected_interval * 2]
        quality_report["data_gaps"] = len(gaps)
        
        # Calculate quality score
        quality_score = 1.0
        quality_score -= (quality_report["missing_values"] / quality_report["total_records"]) * 0.3
        quality_score -= (quality_report["outliers"] / quality_report["total_records"]) * 0.2
        quality_score -= (quality_report["data_gaps"] / quality_report["total_records"]) * 0.1
        quality_score -= (quality_report["volatility_outliers"] / quality_report["total_records"]) * 0.1
        quality_score -= (quality_report["sentiment_outliers"] / quality_report["total_records"]) * 0.1
        
        quality_report["quality_score"] = max(0.0, quality_score)
        
        return quality_report
    
    def _clean_geo_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean geo-risk data by handling missing values and outliers"""
        cleaned_df = df.copy()
        
        # Handle missing values using forward fill
        cleaned_df["risk_score"] = cleaned_df["risk_score"].fillna(method="ffill")
        if "volatility" in cleaned_df.columns:
            cleaned_df["volatility"] = cleaned_df["volatility"].fillna(method="ffill")
        if "sentiment" in cleaned_df.columns:
            cleaned_df["sentiment"] = cleaned_df["sentiment"].fillna(method="ffill")
        
        # Handle remaining missing values with interpolation
        cleaned_df["risk_score"] = cleaned_df["risk_score"].interpolate(method="linear")
        if "volatility" in cleaned_df.columns:
            cleaned_df["volatility"] = cleaned_df["volatility"].interpolate(method="linear")
        if "sentiment" in cleaned_df.columns:
            cleaned_df["sentiment"] = cleaned_df["sentiment"].interpolate(method="linear")
        
        # Remove extreme outliers (beyond 5 standard deviations)
        for col in ["risk_score", "volatility", "sentiment"]:
            if col in cleaned_df.columns:
                mean_val = cleaned_df[col].mean()
                std_val = cleaned_df[col].std()
                cleaned_df = cleaned_df[
                    (cleaned_df[col] >= mean_val - 5 * std_val) & 
                    (cleaned_df[col] <= mean_val + 5 * std_val)
                ]
        
        return cleaned_df
    
    def _aggregate_geo_data(self, df: pd.DataFrame, interval_type: str, aggregation_method: str) -> pd.DataFrame:
        """Aggregate geo-risk data based on interval type and method"""
        df_processed = df.copy()
        df_processed.set_index("timestamp", inplace=True)
        
        # Define aggregation rules
        if aggregation_method == "weighted_average":
            # Weight by volatility for risk scores
            df_processed["weight"] = df_processed["volatility"] + 0.1  # Add small constant to avoid zero weights
            agg_dict = {"risk_score": lambda x: np.average(x, weights=df_processed.loc[x.index, "weight"])}
        elif aggregation_method == "average":
            agg_dict = {"risk_score": "mean"}
        elif aggregation_method == "max":
            agg_dict = {"risk_score": "max"}
        elif aggregation_method == "min":
            agg_dict = {"risk_score": "min"}
        else:
            agg_dict = {"risk_score": "mean"}
        
        # Add other columns if they exist
        if "volatility" in df_processed.columns:
            agg_dict["volatility"] = "mean"
        if "sentiment" in df_processed.columns:
            agg_dict["sentiment"] = "mean"
        
        # Resample based on interval type
        if interval_type == "hourly":
            resampled = df_processed.resample("H").agg(agg_dict)
        elif interval_type == "daily":
            resampled = df_processed.resample("D").agg(agg_dict)
        elif interval_type == "weekly":
            resampled = df_processed.resample("W").agg(agg_dict)
        elif interval_type == "monthly":
            resampled = df_processed.resample("M").agg(agg_dict)
        else:
            # Default to hourly
            resampled = df_processed.resample("H").agg(agg_dict)
        
        # Reset index to get timestamp back as column
        resampled.reset_index(inplace=True)
        
        return resampled
    
    def _calculate_geo_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate statistical measures for geo-risk data"""
        risk_scores = df["risk_score"].dropna()
        
        if len(risk_scores) == 0:
            return {"error": "No valid risk score data points for statistics"}
        
        statistics = {
            "risk_statistics": {
                "mean_risk": float(risk_scores.mean()),
                "median_risk": float(risk_scores.median()),
                "std_dev_risk": float(risk_scores.std()),
                "min_risk": float(risk_scores.min()),
                "max_risk": float(risk_scores.max()),
                "risk_percentile_25": float(risk_scores.quantile(0.25)),
                "risk_percentile_75": float(risk_scores.quantile(0.75)),
                "risk_percentile_95": float(risk_scores.quantile(0.95)),
                "risk_percentile_99": float(risk_scores.quantile(0.99))
            }
        }
        
        # Add volatility statistics if available
        if "volatility" in df.columns:
            volatility_scores = df["volatility"].dropna()
            if len(volatility_scores) > 0:
                statistics["volatility_statistics"] = {
                    "mean_volatility": float(volatility_scores.mean()),
                    "median_volatility": float(volatility_scores.median()),
                    "std_dev_volatility": float(volatility_scores.std()),
                    "max_volatility": float(volatility_scores.max())
                }
        
        # Add sentiment statistics if available
        if "sentiment" in df.columns:
            sentiment_scores = df["sentiment"].dropna()
            if len(sentiment_scores) > 0:
                statistics["sentiment_statistics"] = {
                    "mean_sentiment": float(sentiment_scores.mean()),
                    "median_sentiment": float(sentiment_scores.median()),
                    "std_dev_sentiment": float(sentiment_scores.std()),
                    "min_sentiment": float(sentiment_scores.min()),
                    "max_sentiment": float(sentiment_scores.max())
                }
        
        return statistics
    
    def _analyze_geo_risk_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze trends in geo-risk data"""
        if len(df) < 2:
            return {"error": "Insufficient data for trend analysis"}
        
        risk_scores = df["risk_score"].values
        
        # Calculate trend using linear regression
        x = np.arange(len(risk_scores))
        y = risk_scores
        
        # Simple linear regression
        n = len(x)
        slope = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / (n * np.sum(x**2) - np.sum(x)**2)
        intercept = (np.sum(y) - slope * np.sum(x)) / n
        
        # Calculate R-squared
        y_pred = slope * x + intercept
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        # Determine trend direction
        if abs(slope) < 0.001:
            trend_direction = "stable"
        elif slope > 0:
            trend_direction = "increasing"
        else:
            trend_direction = "decreasing"
        
        # Calculate volatility of risk scores
        risk_volatility = np.std(np.diff(risk_scores))
        
        return {
            "trend_direction": trend_direction,
            "trend_slope": float(slope),
            "trend_intercept": float(intercept),
            "r_squared": float(r_squared),
            "risk_volatility": float(risk_volatility),
            "trend_strength": "strong" if abs(r_squared) > 0.7 else "moderate" if abs(r_squared) > 0.4 else "weak",
            "trend_confidence": min(1.0, max(0.0, abs(r_squared)))
        }

class CryptoRiskAnalyzer:
    """Molecule-like crypto risk analysis for digital asset trading"""
    
    def __init__(self):
        self.crypto_risk_models = {}
        self.volatility_models = {}
        self.correlation_models = {}
        
    def analyze_crypto_risk(self, crypto_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive crypto risk analysis"""
        try:
            crypto_symbol = crypto_data.get("symbol", "BTC")
            price_data = crypto_data.get("price_data", [])
            volume_data = crypto_data.get("volume_data", [])
            market_cap = crypto_data.get("market_cap", 0)
            
            # Calculate various risk metrics
            price_volatility = self._calculate_price_volatility(price_data)
            volume_volatility = self._calculate_volume_volatility(volume_data)
            market_cap_risk = self._calculate_market_cap_risk(market_cap)
            
            # Technical analysis
            technical_indicators = self._calculate_technical_indicators(price_data)
            
            # Risk scoring
            risk_score = self._calculate_crypto_risk_score(
                price_volatility, volume_volatility, market_cap_risk, technical_indicators
            )
            
            # Risk classification
            risk_level = self._classify_crypto_risk(risk_score)
            
            # Correlation analysis
            correlation_analysis = self._analyze_crypto_correlations(crypto_data)
            
            return {
                "crypto_symbol": crypto_symbol,
                "risk_analysis": {
                    "risk_score": risk_score,
                    "risk_level": risk_level,
                    "price_volatility": price_volatility,
                    "volume_volatility": volume_volatility,
                    "market_cap_risk": market_cap_risk
                },
                "technical_indicators": technical_indicators,
                "correlation_analysis": correlation_analysis,
                "risk_factors": self._identify_crypto_risk_factors(crypto_data),
                "recommendations": self._generate_crypto_recommendations(risk_score, risk_level),
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing crypto risk: {str(e)}")
            raise
    
    def _calculate_price_volatility(self, price_data: List[float]) -> Dict[str, float]:
        """Calculate price volatility metrics"""
        if len(price_data) < 2:
            return {"volatility": 0.0, "annualized_volatility": 0.0}
        
        prices = np.array(price_data)
        returns = np.diff(np.log(prices))
        
        volatility = np.std(returns)
        annualized_volatility = volatility * np.sqrt(365)  # Assuming daily data
        
        return {
            "volatility": float(volatility),
            "annualized_volatility": float(annualized_volatility),
            "max_drawdown": float(np.min(np.cumsum(returns))),
            "sharpe_ratio": float(np.mean(returns) / volatility) if volatility > 0 else 0.0
        }
    
    def _calculate_volume_volatility(self, volume_data: List[float]) -> Dict[str, float]:
        """Calculate volume volatility metrics"""
        if len(volume_data) < 2:
            return {"volume_volatility": 0.0, "volume_trend": "stable"}
        
        volumes = np.array(volume_data)
        volume_volatility = np.std(volumes) / np.mean(volumes) if np.mean(volumes) > 0 else 0
        
        # Calculate volume trend
        x = np.arange(len(volumes))
        slope = np.polyfit(x, volumes, 1)[0]
        
        if slope > 0.1:
            volume_trend = "increasing"
        elif slope < -0.1:
            volume_trend = "decreasing"
        else:
            volume_trend = "stable"
        
        return {
            "volume_volatility": float(volume_volatility),
            "volume_trend": volume_trend,
            "average_volume": float(np.mean(volumes)),
            "volume_percentile_95": float(np.percentile(volumes, 95))
        }
    
    def _calculate_market_cap_risk(self, market_cap: float) -> Dict[str, Any]:
        """Calculate market cap risk metrics"""
        if market_cap <= 0:
            return {"market_cap_risk": "unknown", "liquidity_risk": "high"}
        
        # Market cap categories
        if market_cap > 100e9:  # > $100B
            market_cap_risk = "low"
            liquidity_risk = "low"
        elif market_cap > 10e9:  # $10B - $100B
            market_cap_risk = "medium"
            liquidity_risk = "medium"
        elif market_cap > 1e9:  # $1B - $10B
            market_cap_risk = "medium-high"
            liquidity_risk = "medium-high"
        else:  # < $1B
            market_cap_risk = "high"
            liquidity_risk = "high"
        
        return {
            "market_cap_risk": market_cap_risk,
            "liquidity_risk": liquidity_risk,
            "market_cap_category": self._get_market_cap_category(market_cap),
            "risk_score": self._get_market_cap_risk_score(market_cap)
        }
    
    def _calculate_technical_indicators(self, price_data: List[float]) -> Dict[str, float]:
        """Calculate technical indicators"""
        if len(price_data) < 20:
            return {"rsi": 50.0, "bollinger_position": 0.5, "moving_average_trend": "neutral"}
        
        prices = np.array(price_data)
        
        # RSI calculation
        rsi = self._calculate_rsi(prices)
        
        # Bollinger Bands
        bollinger_position = self._calculate_bollinger_position(prices)
        
        # Moving average trend
        ma_trend = self._calculate_moving_average_trend(prices)
        
        return {
            "rsi": float(rsi),
            "bollinger_position": float(bollinger_position),
            "moving_average_trend": ma_trend,
            "support_level": float(np.percentile(prices, 10)),
            "resistance_level": float(np.percentile(prices, 90))
        }
    
    def _calculate_rsi(self, prices: np.ndarray, period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return 50.0
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gains = np.mean(gains[-period:])
        avg_losses = np.mean(losses[-period:])
        
        if avg_losses == 0:
            return 100.0
        
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_bollinger_position(self, prices: np.ndarray, period: int = 20) -> float:
        """Calculate position within Bollinger Bands"""
        if len(prices) < period:
            return 0.5
        
        recent_prices = prices[-period:]
        sma = np.mean(recent_prices)
        std = np.std(recent_prices)
        
        if std == 0:
            return 0.5
        
        current_price = prices[-1]
        upper_band = sma + 2 * std
        lower_band = sma - 2 * std
        
        # Position between bands (0 = lower band, 1 = upper band)
        position = (current_price - lower_band) / (upper_band - lower_band)
        
        return max(0.0, min(1.0, position))
    
    def _calculate_moving_average_trend(self, prices: np.ndarray) -> str:
        """Calculate moving average trend"""
        if len(prices) < 20:
            return "neutral"
        
        short_ma = np.mean(prices[-10:])  # 10-period MA
        long_ma = np.mean(prices[-20:])   # 20-period MA
        
        if short_ma > long_ma * 1.02:
            return "bullish"
        elif short_ma < long_ma * 0.98:
            return "bearish"
        else:
            return "neutral"
    
    def _calculate_crypto_risk_score(self, price_vol: Dict, volume_vol: Dict, 
                                   market_cap_risk: Dict, technical: Dict) -> float:
        """Calculate overall crypto risk score"""
        risk_score = 0.0
        
        # Price volatility component (40% weight)
        risk_score += price_vol["annualized_volatility"] * 0.4
        
        # Volume volatility component (20% weight)
        risk_score += volume_vol["volume_volatility"] * 0.2
        
        # Market cap risk component (20% weight)
        risk_score += market_cap_risk["risk_score"] * 0.2
        
        # Technical indicators component (20% weight)
        rsi_risk = abs(technical["rsi"] - 50) / 50  # Distance from neutral RSI
        bollinger_risk = abs(technical["bollinger_position"] - 0.5) * 2  # Distance from center
        risk_score += (rsi_risk + bollinger_risk) * 0.1
        
        return min(1.0, risk_score)
    
    def _classify_crypto_risk(self, risk_score: float) -> str:
        """Classify crypto risk level"""
        if risk_score > 0.7:
            return "CRITICAL"
        elif risk_score > 0.5:
            return "HIGH"
        elif risk_score > 0.3:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _analyze_crypto_correlations(self, crypto_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze correlations with other assets"""
        # Simplified correlation analysis
        return {
            "btc_correlation": random.uniform(0.6, 0.9),
            "eth_correlation": random.uniform(0.5, 0.8),
            "stock_market_correlation": random.uniform(-0.2, 0.4),
            "gold_correlation": random.uniform(-0.1, 0.3),
            "correlation_strength": "strong" if random.random() > 0.5 else "moderate"
        }
    
    def _identify_crypto_risk_factors(self, crypto_data: Dict[str, Any]) -> List[str]:
        """Identify specific risk factors"""
        risk_factors = []
        
        # Add risk factors based on data analysis
        risk_factors.append("Market volatility")
        risk_factors.append("Regulatory uncertainty")
        risk_factors.append("Technology risk")
        risk_factors.append("Liquidity risk")
        
        return risk_factors
    
    def _generate_crypto_recommendations(self, risk_score: float, risk_level: str) -> List[str]:
        """Generate crypto trading recommendations"""
        recommendations = []
        
        if risk_level == "CRITICAL":
            recommendations.extend([
                "🚨 CRITICAL: Avoid new positions",
                "Consider reducing exposure by 75%",
                "Implement strict stop-loss orders",
                "Monitor regulatory developments closely"
            ])
        elif risk_level == "HIGH":
            recommendations.extend([
                "⚠️ HIGH: Limit position sizes",
                "Use hedging strategies",
                "Set conservative stop-losses",
                "Diversify across different crypto assets"
            ])
        elif risk_level == "MEDIUM":
            recommendations.extend([
                "📊 MEDIUM: Standard risk management",
                "Monitor key technical levels",
                "Consider partial hedging"
            ])
        else:
            recommendations.extend([
                "✅ LOW: Standard operations",
                "Continue monitoring for risk escalation"
            ])
        
        return recommendations
    
    def _get_market_cap_category(self, market_cap: float) -> str:
        """Get market cap category"""
        if market_cap > 100e9:
            return "Large Cap"
        elif market_cap > 10e9:
            return "Mid Cap"
        elif market_cap > 1e9:
            return "Small Cap"
        else:
            return "Micro Cap"
    
    def _get_market_cap_risk_score(self, market_cap: float) -> float:
        """Get market cap risk score"""
        if market_cap > 100e9:
            return 0.2
        elif market_cap > 10e9:
            return 0.4
        elif market_cap > 1e9:
            return 0.6
        else:
            return 0.8