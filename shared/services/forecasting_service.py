import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import structlog
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib
import os
from pathlib import Path
import warnings
import requests
import json
import redis
import pickle
import hashlib

logger = structlog.get_logger()

class ForecastingService:
    """Advanced forecasting service with ML models, Prophet integration, and Grok AI"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.model_dir = Path("models")
        self.model_dir.mkdir(exist_ok=True)
        self.retrain_interval = 24  # hours
        self.grok_api_key = os.getenv("GROK_API_KEY")
        self.grok_base_url = os.getenv("GROK_BASE_URL", "https://api.grok.ai/v1")
        
        # Redis caching configuration
        self.redis_client = None
        self.redis_enabled = False
        self.cache_ttl = 3600  # 1 hour default
        
        try:
            redis_host = os.getenv("REDIS_HOST", "localhost")
            redis_port = int(os.getenv("REDIS_PORT", 6379))
            redis_db = int(os.getenv("REDIS_DB", 0))
            
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                decode_responses=False,  # Keep as bytes for pickle
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test connection
            self.redis_client.ping()
            self.redis_enabled = True
            logger.info(f"Redis caching enabled at {redis_host}:{redis_port}")
            
        except Exception as e:
            logger.warning(f"Redis not available: {e}. Caching disabled.")
            self.redis_enabled = False
        
        # Try to import Prophet
        try:
            from prophet import Prophet
            self.prophet_available = True
            self.Prophet = Prophet
            logger.info("Prophet forecasting library available")
        except ImportError:
            self.prophet_available = False
            logger.warning("Prophet not available, using ML models only")
        
        # Try to import advanced ML libraries
        try:
            from xgboost import XGBRegressor
            self.xgb_available = True
            self.XGBRegressor = XGBRegressor
            logger.info("XGBoost available for advanced forecasting")
        except ImportError:
            self.xgb_available = False
            logger.warning("XGBoost not available")
    
    def _generate_cache_key(self, method: str, **kwargs) -> str:
        """Generate a unique cache key for caching operations"""
        try:
            # Create a string representation of the method and parameters
            key_data = f"{method}:{sorted(kwargs.items())}"
            # Generate hash for consistent key length
            return hashlib.md5(key_data.encode()).hexdigest()
        except Exception as e:
            logger.warning(f"Error generating cache key: {e}")
            return f"{method}_{hash(str(kwargs))}"
    
    def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached result from Redis"""
        if not self.redis_enabled or not self.redis_client:
            return None
        
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                result = pickle.loads(cached_data)
                logger.info(f"Cache hit for key: {cache_key}")
                return result
        except Exception as e:
            logger.warning(f"Error retrieving from cache: {e}")
        
        return None
    
    def _set_cached_result(self, cache_key: str, result: Dict[str, Any], ttl: int = None) -> bool:
        """Set result in Redis cache"""
        if not self.redis_enabled or not self.redis_client:
            return False
        
        try:
            ttl = ttl or self.cache_ttl
            serialized_result = pickle.dumps(result)
            self.redis_client.setex(cache_key, ttl, serialized_result)
            logger.info(f"Cached result for key: {cache_key} with TTL: {ttl}s")
            return True
        except Exception as e:
            logger.warning(f"Error setting cache: {e}")
            return False
    
    def _load_or_create_model(self, commodity: str, model_type: str = "ensemble"):
        """Load existing model or create new one with advanced ensemble methods"""
        model_path = self.model_dir / f"{commodity}_{model_type}.pkl"
        scaler_path = self.model_dir / f"{commodity}_{model_type}_scaler.pkl"
        
        if model_path.exists() and scaler_path.exists():
            try:
                self.models[commodity] = joblib.load(model_path)
                self.scalers[commodity] = joblib.load(scaler_path)
                logger.info(f"Loaded existing model for {commodity}")
                return True
            except Exception as e:
                logger.warning(f"Failed to load model for {commodity}: {e}")
        
        # Create advanced ensemble model
        if model_type == "ensemble":
            estimators = [
                ('rf', RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)),
                ('gb', GradientBoostingRegressor(n_estimators=100, random_state=42))
            ]
            
            if self.xgb_available:
                estimators.append(('xgb', self.XGBRegressor(n_estimators=100, random_state=42)))
            
            self.models[commodity] = VotingRegressor(estimators=estimators)
        else:
            self.models[commodity] = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
        
        self.scalers[commodity] = StandardScaler()
        logger.info(f"Created new {model_type} model for {commodity}")
        return False
    
    def _prepare_features(self, historical_data: List[Dict[str, Any]]) -> tuple:
        """Prepare features for ML model with advanced feature engineering"""
        if not historical_data:
            return None, None
        
        df = pd.DataFrame(historical_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Create time-based features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['month'] = df['timestamp'].dt.month
        df['day_of_year'] = df['timestamp'].dt.dayofyear
        df['quarter'] = df['timestamp'].dt.quarter
    
    def _apply_ai_correction(self, forecast: float, market_context: Dict[str, Any]) -> float:
        """Apply AI-powered correction to forecasts based on market context"""
        try:
            # Get market sentiment and volatility
            volatility = market_context.get("volatility", 0.1)
            sentiment = market_context.get("sentiment", "neutral")
            news_impact = market_context.get("news_impact", 0)
            
            # Calculate correction factor
            correction_factor = 1.0
            
            # Volatility-based correction
            if volatility > 0.3:
                correction_factor *= 0.9  # Reduce forecast in high volatility
            elif volatility < 0.05:
                correction_factor *= 1.1  # Increase forecast in low volatility
            
            # Sentiment-based correction
            if sentiment == "bullish":
                correction_factor *= 1.05
            elif sentiment == "bearish":
                correction_factor *= 0.95
            
            # News impact correction
            if abs(news_impact) > 0.1:
                correction_factor *= (1 + news_impact * 0.1)
            
            # Apply correction with bounds
            corrected_forecast = forecast * correction_factor
            return max(0, corrected_forecast)  # Ensure non-negative
            
        except Exception as e:
            logger.warning(f"AI correction failed: {e}, using original forecast")
            return forecast
    
    def _validate_forecast(self, forecast: float, historical_range: Tuple[float, float]) -> float:
        """Validate forecast against historical data range"""
        min_val, max_val = historical_range
        
        # If forecast is outside historical range, apply AI correction
        if forecast < min_val or forecast > max_val:
            logger.info(f"Forecast {forecast} outside historical range [{min_val}, {max_val}], applying correction")
            
            # Move forecast towards the mean of historical range
            historical_mean = (min_val + max_val) / 2
            correction_factor = 0.8  # Move 80% towards mean
            
            corrected_forecast = forecast * (1 - correction_factor) + historical_mean * correction_factor
            return max(min_val, min(max_val, corrected_forecast))
        
        return forecast
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['is_month_start'] = df['timestamp'].dt.is_month_start.astype(int)
        df['is_month_end'] = df['timestamp'].dt.is_month_end.astype(int)
        
        # Create lag features
        for lag in [1, 2, 3, 6, 12, 24]:
            df[f'price_lag_{lag}'] = df['price'].shift(lag)
            df[f'volume_lag_{lag}'] = df['volume'].shift(lag)
        
        # Create rolling features
        for window in [3, 6, 12, 24]:
            df[f'price_rolling_mean_{window}'] = df['price'].rolling(window).mean()
            df[f'price_rolling_std_{window}'] = df['price'].rolling(window).std()
            df[f'price_rolling_min_{window}'] = df['price'].rolling(window).min()
            df[f'price_rolling_max_{window}'] = df['price'].rolling(window).max()
            df[f'volume_rolling_mean_{window}'] = df['volume'].rolling(window).mean()
        
        # Create price change features
        df['price_change'] = df['price'].pct_change()
        df['price_change_abs'] = df['price_change'].abs()
        df['price_momentum'] = df['price_change'].rolling(6).mean()
        
        # Create volatility features
        df['volatility'] = df['price'].rolling(24).std()
        df['volatility_ratio'] = df['volatility'] / df['price']
        
        # Drop NaN values
        df = df.dropna()
        
        if len(df) < 50:  # Increased minimum data requirement
            return None, None
        
        # Prepare features and target
        feature_columns = [col for col in df.columns if col not in ['timestamp', 'price']]
        
        X = df[feature_columns].values
        y = df['price'].values
        
        logger.info(f"Training data features: {len(feature_columns)} = {feature_columns}")
        
        return X, y
    
    def _call_grok_ai(self, prompt: str, context: str = "") -> Optional[str]:
        """Call Grok AI for advanced forecasting insights"""
        if not self.grok_api_key:
            logger.warning("Grok API key not configured")
            return None
        
        try:
            headers = {
                "Authorization": f"Bearer {self.grok_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "prompt": f"{context}\n\n{prompt}",
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            response = requests.post(
                f"{self.grok_base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("choices", [{}])[0].get("message", {}).get("content", "")
            else:
                logger.warning(f"Grok API call failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error calling Grok AI: {e}")
            return None
    
    def train_model(self, commodity: str, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Train advanced ML model for a specific commodity"""
        try:
            X, y = self._prepare_features(historical_data)
            if X is None or y is None:
                return {"error": "Insufficient data for training"}
            
            # Load or create model
            self._load_or_create_model(commodity, "ensemble")
            
            # Scale features
            X_scaled = self.scalers[commodity].fit_transform(X)
            
            # Train model
            self.models[commodity].fit(X_scaled, y)
            
            # Make predictions on training data
            y_pred = self.models[commodity].predict(X_scaled)
            
            # Calculate metrics
            mae = mean_absolute_error(y, y_pred)
            mse = mean_squared_error(y, y_pred)
            rmse = np.sqrt(mse)
            
            # Calculate additional metrics
            mape = np.mean(np.abs((y - y_pred) / y)) * 100
            r2 = 1 - (np.sum((y - y_pred) ** 2) / np.sum((y - np.mean(y)) ** 2))
            
            # Save model
            model_path = self.model_dir / f"{commodity}_ensemble.pkl"
            scaler_path = self.model_dir / f"{commodity}_ensemble_scaler.pkl"
            
            joblib.dump(self.models[commodity], model_path)
            joblib.dump(self.scalers[commodity], scaler_path)
            
            logger.info(f"Advanced model trained successfully for {commodity}")
            
            return {
                "commodity": commodity,
                "training_samples": len(X),
                "model_type": "Ensemble",
                "metrics": {
                    "mae": round(mae, 4),
                    "mse": round(mse, 4),
                    "rmse": round(rmse, 4),
                    "mape": round(mape, 2),
                    "r2": round(r2, 4)
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error training model for {commodity}: {e}")
            return {"error": str(e)}
    
    def forecast_with_prophet(self, commodity: str, historical_data: List[Dict[str, Any]], days: int = 7) -> Dict[str, Any]:
        """Forecast using Prophet library for time series analysis"""
        if not self.prophet_available:
            return {"error": "Prophet library not available"}
        
        try:
            # Prepare data for Prophet
            df = pd.DataFrame(historical_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            # Prophet requires 'ds' for dates and 'y' for values
            prophet_df = df[['timestamp', 'price']].rename(columns={'timestamp': 'ds', 'price': 'y'})
            
            # Create and fit Prophet model
            model = self.Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=True,
                changepoint_prior_scale=0.05
            )
            
            model.fit(prophet_df)
            
            # Make future predictions
            future = model.make_future_dataframe(periods=days * 24, freq='H')
            forecast = model.predict(future)
            
            # Extract forecast data
            forecast_data = []
            for i in range(len(prophet_df), len(forecast)):
                row = forecast.iloc[i]
                forecast_data.append({
                    "timestamp": row['ds'].isoformat(),
                    "predicted_price": round(row['yhat'], 2),
                    "lower_bound": round(row['yhat_lower'], 2),
                    "upper_bound": round(row['yhat_upper'], 2),
                    "confidence": 0.9,
                    "forecast_horizon": i - len(prophet_df)
                })
            
            return {
                "commodity": commodity,
                "forecast_period_days": days,
                "forecast_data": forecast_data,
                "model_info": {
                    "type": "Prophet",
                    "seasonality": "yearly, weekly, daily",
                    "changepoint_prior_scale": 0.05
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error forecasting with Prophet for {commodity}: {e}")
            return {"error": str(e)}
    
    def forecast_future_consumption(self, commodity: str, days: int = 7) -> Dict[str, Any]:
        """Forecast future prices using ensemble model"""
        try:
            if commodity not in self.models:
                return {"error": f"No trained model found for {commodity}"}
            
            # Generate future timestamps
            future_dates = []
            current_time = datetime.now()
            
            for i in range(days * 24):  # Hourly forecasts
                future_time = current_time + timedelta(hours=i)
                future_dates.append(future_time)
            
            # Prepare future features with advanced engineering
            future_features = []
            for timestamp in future_dates:
                # Calculate quarter manually since datetime doesn't have quarter attribute
                quarter = (timestamp.month - 1) // 3 + 1
                
                features = [
                    0,  # volume (placeholder, will be filled with recent data)
                    timestamp.hour,
                    timestamp.weekday(),
                    timestamp.month,
                    timestamp.timetuple().tm_yday,
                    quarter,  # Fixed: calculate quarter manually
                    1 if timestamp.weekday() in [5, 6] else 0,
                    1 if timestamp.day == 1 else 0,
                    1 if timestamp.day == 1 else 0  # Simplified month end check
                ]
                
                # Add lag features (will be filled with recent data)
                for lag in [1, 2, 3, 6, 12, 24]:
                    features.extend([0, 0])  # price_lag, volume_lag
                
                # Add rolling features
                for window in [3, 6, 12, 24]:
                    features.extend([0, 0, 0, 0, 0])  # rolling features
                
                # Add other features
                features.extend([0, 0, 0, 0, 0])  # price_change, momentum, volatility features
                
                future_features.append(features)
            
            # Scale features
            X_future = np.array(future_features)
            X_future_scaled = self.scalers[commodity].transform(X_future)
            
            # Make predictions
            predictions = self.models[commodity].predict(X_future_scaled)
            
            # Create forecast data
            forecast_data = []
            for i, (timestamp, pred) in enumerate(zip(future_dates, predictions)):
                forecast_data.append({
                    "timestamp": timestamp.isoformat(),
                    "predicted_price": round(pred, 2),
                    "confidence": max(0.6, 0.95 - (i * 0.01)),  # Better confidence model
                    "forecast_horizon": i
                })
            
            # Get Grok AI insights if available
            grok_insights = None
            if self.grok_api_key:
                context = f"Energy commodity: {commodity}, Current price trend: {predictions[:24].mean():.2f}"
                prompt = f"Analyze the energy price forecast for {commodity} and provide 2-3 key trading insights"
                grok_insights = self._call_grok_ai(prompt, context)
            
            return {
                "commodity": commodity,
                "forecast_period_days": days,
                "forecast_data": forecast_data,
                "model_info": {
                    "type": "Ensemble",
                    "last_trained": datetime.now().isoformat(),
                    "confidence_trend": "adaptive"
                },
                "grok_ai_insights": grok_insights,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error forecasting for {commodity}: {e}")
            return {"error": str(e)}
    
    def get_forecast_insights(self, commodity: str, forecast_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate insights from forecast data"""
        try:
            if not forecast_data:
                return {"error": "No forecast data provided"}
            
            prices = [item['predicted_price'] for item in forecast_data]
            current_price = prices[0]
            max_price = max(prices)
            min_price = min(prices)
            avg_price = np.mean(prices)
            
            # Calculate trends
            price_change = ((max_price - current_price) / current_price) * 100
            volatility = np.std(prices)
            
            # Generate insights
            insights = []
            if price_change > 5:
                insights.append("Strong upward trend expected")
            elif price_change < -5:
                insights.append("Downward pressure anticipated")
            else:
                insights.append("Stable price movement expected")
            
            if volatility > np.mean(prices) * 0.1:
                insights.append("High volatility expected")
            else:
                insights.append("Low volatility expected")
            
            # Trading recommendations
            recommendations = []
            if price_change > 3:
                recommendations.append("Consider long positions")
            elif price_change < -3:
                recommendations.append("Consider short positions")
            else:
                recommendations.append("Hold current positions")
            
            return {
                "commodity": commodity,
                "current_price": current_price,
                "forecast_range": {
                    "min": min_price,
                    "max": max_price,
                    "average": round(avg_price, 2)
                },
                "price_change_percent": round(price_change, 2),
                "volatility": round(volatility, 2),
                "insights": insights,
                "recommendations": recommendations,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating insights for {commodity}: {e}")
            return {"error": str(e)}
    
    def calculate_esg_score(self, commodity: str, forecast_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate ESG (Environmental, Social, Governance) score for energy trading"""
        try:
            if not forecast_data:
                return {"error": "No forecast data provided"}
            
            # Environmental factors
            carbon_intensity = {
                "crude_oil": 0.85,
                "natural_gas": 0.45,
                "coal": 0.95,
                "renewables": 0.05
            }
            
            # Social factors (simplified scoring)
            social_impact = {
                "crude_oil": 0.6,
                "natural_gas": 0.7,
                "coal": 0.4,
                "renewables": 0.9
            }
            
            # Governance factors (compliance and transparency)
            governance_score = 0.8  # Base score, could be enhanced with actual compliance data
            
            # Calculate commodity-specific scores
            env_score = 1 - carbon_intensity.get(commodity.lower(), 0.5)
            soc_score = social_impact.get(commodity.lower(), 0.5)
            
            # Weighted ESG score
            esg_score = (env_score * 0.4 + soc_score * 0.3 + governance_score * 0.3) * 100
            
            # ESG rating
            if esg_score >= 80:
                rating = "A"
            elif esg_score >= 60:
                rating = "B"
            elif esg_score >= 40:
                rating = "C"
            else:
                rating = "D"
            
            return {
                "commodity": commodity,
                "esg_score": round(esg_score, 2),
                "rating": rating,
                "breakdown": {
                    "environmental": round(env_score * 100, 2),
                    "social": round(soc_score * 100, 2),
                    "governance": round(governance_score * 100, 2)
                },
                "recommendations": self._generate_esg_recommendations(esg_score, commodity),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating ESG score for {commodity}: {e}")
            return {"error": str(e)}
    
    def _generate_esg_recommendations(self, esg_score: float, commodity: str) -> List[str]:
        """Generate ESG improvement recommendations"""
        recommendations = []
        
        if esg_score < 60:
            recommendations.append("Consider diversifying portfolio with renewable energy sources")
            recommendations.append("Implement carbon offset strategies")
            recommendations.append("Enhance transparency and reporting")
        
        if commodity.lower() in ["coal", "crude_oil"]:
            recommendations.append("Explore transition to cleaner energy alternatives")
            recommendations.append("Implement carbon capture and storage technologies")
        
        if esg_score >= 80:
            recommendations.append("Maintain high ESG standards")
            recommendations.append("Consider ESG leadership initiatives")
        
        return recommendations
    
    def retrain_model(self, commodity: str, new_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Retrain model with new data"""
        try:
            # Combine historical and new data
            if commodity in self.models:
                # In production, you'd load historical data from database
                historical_data = new_data  # For now, just use new data
            else:
                historical_data = new_data
            
            return self.train_model(commodity, historical_data)
            
        except Exception as e:
            logger.error(f"Error retraining model for {commodity}: {e}")
            return {"error": str(e)}
    
    def get_model_status(self, commodity: str = None) -> Dict[str, Any]:
        """Get status of trained models"""
        try:
            if commodity:
                if commodity in self.models:
                    model_path = self.model_dir / f"{commodity}_ensemble.pkl"
                    return {
                        "commodity": commodity,
                        "status": "trained",
                        "last_modified": datetime.fromtimestamp(model_path.stat().st_mtime).isoformat(),
                        "model_type": "Ensemble"
                    }
                else:
                    return {"commodity": commodity, "status": "not_trained"}
            
            # Return status of all models
            all_models = {}
            for model_file in self.model_dir.glob("*_ensemble.pkl"):
                commodity_name = model_file.stem.replace("_ensemble", "")
                all_models[commodity_name] = {
                    "status": "trained",
                    "last_modified": datetime.fromtimestamp(model_file.stat().st_mtime).isoformat(),
                    "model_type": "Ensemble"
                }
            
            return {
                "total_models": len(all_models),
                "models": all_models,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting model status: {e}")
            return {"error": str(e)}

# Global instance
forecasting_service = ForecastingService()
