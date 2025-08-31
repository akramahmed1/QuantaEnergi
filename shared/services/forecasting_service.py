import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import structlog
import time
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
        
        # Redis caching configuration with clustering support
        self.redis_client = None
        self.redis_cluster = None
        self.redis_enabled = False
        self.cache_ttl = 3600  # 1 hour default
        
        try:
            # Try Redis Cluster first
            redis_cluster_hosts = os.getenv("REDIS_CLUSTER_HOSTS")
            if redis_cluster_hosts:
                try:
                    from redis.cluster import RedisCluster
                    cluster_hosts = [host.strip() for host in redis_cluster_hosts.split(",")]
                    self.redis_cluster = RedisCluster(
                        startup_nodes=[{"host": host.split(":")[0], "port": int(host.split(":")[1])} 
                                     for host in cluster_hosts],
                        decode_responses=False,
                        socket_connect_timeout=5,
                        socket_timeout=5,
                        retry_on_timeout=True,
                        max_connections=20
                    )
                    # Test cluster connection
                    self.redis_cluster.ping()
                    self.redis_enabled = True
                    logger.info(f"Redis Cluster enabled with {len(cluster_hosts)} nodes")
                    
                except Exception as cluster_error:
                    logger.warning(f"Redis Cluster failed: {cluster_error}. Falling back to single Redis.")
                    self.redis_cluster = None
            
            # Fallback to single Redis if cluster not available
            if not self.redis_cluster:
                redis_host = os.getenv("REDIS_HOST", "localhost")
                redis_port = int(os.getenv("REDIS_PORT", 6379))
                redis_db = int(os.getenv("REDIS_DB", 0))
                redis_password = os.getenv("REDIS_PASSWORD")
                
                # Connection pooling for single Redis
                self.redis_client = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    db=redis_db,
                    password=redis_password,
                    decode_responses=False,  # Keep as bytes for pickle
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    max_connections=20,
                    connection_pool=redis.ConnectionPool(
                        host=redis_host,
                        port=redis_port,
                        db=redis_db,
                        password=redis_password,
                        max_connections=20,
                        retry_on_timeout=True
                    )
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
        
        # News API configuration
        self.news_api_key = os.getenv("NEWS_API_KEY")
        self.news_base_url = "https://newsapi.org/v2"
        self.news_cache_ttl = 1800  # 30 minutes for news
        
        # Anomaly detection configuration
        self.anomaly_detection_enabled = True
        self.anomaly_threshold = 2.0  # Standard deviations for anomaly detection
    
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
    
    def _get_redis_client(self):
        """Get the appropriate Redis client (cluster or single)"""
        return self.redis_cluster if self.redis_cluster else self.redis_client
    
    def _cache_get(self, key: str) -> Optional[Any]:
        """Get value from cache with failover handling"""
        if not self.redis_enabled:
            return None
        
        try:
            client = self._get_redis_client()
            cached_data = client.get(key)
            if cached_data:
                return pickle.loads(cached_data)
        except Exception as e:
            logger.warning(f"Cache get failed for key {key}: {e}")
            # Try to recover from cache corruption
            self._cache_delete(key)
        
        return None
    
    def _cache_set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache with failover handling"""
        if not self.redis_enabled:
            return False
        
        try:
            client = self._get_redis_client()
            ttl = ttl or self.cache_ttl
            serialized_data = pickle.dumps(value)
            return client.setex(key, ttl, serialized_data)
        except Exception as e:
            logger.warning(f"Cache set failed for key {key}: {e}")
            return False
    
    def _cache_delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not self.redis_enabled:
            return False
        
        try:
            client = self._get_redis_client()
            return bool(client.delete(key))
        except Exception as e:
            logger.warning(f"Cache delete failed for key {key}: {e}")
            return False
    
    def _cache_invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache keys matching a pattern"""
        if not self.redis_enabled:
            return 0
        
        try:
            client = self._get_redis_client()
            if self.redis_cluster:
                # For Redis Cluster, scan all nodes
                deleted_count = 0
                for node in client.get_nodes():
                    keys = client.scan_iter(match=pattern, target_nodes=[node])
                    for key in keys:
                        if client.delete(key):
                            deleted_count += 1
                return deleted_count
            else:
                # For single Redis, use scan
                keys = client.scan_iter(match=pattern)
                deleted_count = 0
                for key in keys:
                    if client.delete(key):
                        deleted_count += 1
                return deleted_count
        except Exception as e:
            logger.warning(f"Cache pattern invalidation failed for {pattern}: {e}")
            return 0
    
    def _cache_health_check(self) -> Dict[str, Any]:
        """Check cache health and performance"""
        if not self.redis_enabled:
            return {"status": "disabled", "error": "Redis not available"}
        
        try:
            client = self._get_redis_client()
            start_time = time.time()
            
            # Test basic operations
            test_key = "_health_check_test"
            test_value = {"test": "data", "timestamp": datetime.now().isoformat()}
            
            # Test set
            set_success = self._cache_set(test_key, test_value, 60)
            set_time = time.time() - start_time
            
            # Test get
            get_start = time.time()
            retrieved_value = self._cache_get(test_key)
            get_time = time.time() - get_start
            
            # Test delete
            delete_success = self._cache_delete(test_key)
            
            # Get cache info
            info = client.info()
            
            return {
                "status": "healthy" if all([set_success, retrieved_value == test_value, delete_success]) else "degraded",
                "operations": {
                    "set": {"success": set_success, "time_ms": round(set_time * 1000, 2)},
                    "get": {"success": retrieved_value == test_value, "time_ms": round(get_time * 1000, 2)},
                    "delete": {"success": delete_success}
                },
                "redis_info": {
                    "version": info.get("redis_version", "unknown"),
                    "connected_clients": info.get("connected_clients", 0),
                    "used_memory_human": info.get("used_memory_human", "unknown"),
                    "total_commands_processed": info.get("total_commands_processed", 0)
                },
                "cluster": bool(self.redis_cluster),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached result from Redis using enhanced caching"""
        if not self.redis_enabled:
            return None
        
        try:
            result = self._cache_get(cache_key)
            if result:
                logger.info(f"Cache hit for key: {cache_key}")
            return result
        except Exception as e:
            logger.warning(f"Error retrieving from cache: {e}")
        
        return None
    
    def _set_cached_result(self, cache_key: str, result: Dict[str, Any], ttl: int = None) -> bool:
        """Set result in Redis cache using enhanced caching"""
        if not self.redis_enabled:
            return False
        
        try:
            success = self._cache_set(cache_key, result, ttl)
            if success:
                logger.info(f"Cached result for key: {cache_key} with TTL: {ttl or self.cache_ttl}s")
            return success
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
    
    def get_energy_news(self, commodity: str = None, days: int = 7) -> Dict[str, Any]:
        """Get energy-related news for forecasting context"""
        try:
            cache_key = self._generate_cache_key("news", commodity=commodity, days=days)
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            if not self.news_api_key:
                # Return mock news data if API key not available
                mock_news = self._generate_mock_energy_news(commodity, days)
                return mock_news
            
            # Query News API
            query = f"energy {commodity}" if commodity else "energy"
            url = f"{self.news_base_url}/everything"
            params = {
                "q": query,
                "from": (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d"),
                "sortBy": "relevancy",
                "apiKey": self.news_api_key,
                "language": "en",
                "pageSize": 20
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            news_data = response.json()
            
            # Process and analyze news sentiment
            processed_news = self._process_news_data(news_data, commodity)
            
            # Cache the result
            self._cache_result(cache_key, processed_news, self.news_cache_ttl)
            
            return processed_news
            
        except Exception as e:
            logger.error(f"Error fetching energy news: {e}")
            # Return mock data on error
            return self._generate_mock_energy_news(commodity, days)
    
    def _generate_mock_energy_news(self, commodity: str = None, days: int = 7) -> Dict[str, Any]:
        """Generate mock energy news for testing"""
        mock_articles = []
        base_date = datetime.now() - timedelta(days=days)
        
        news_templates = [
            "Oil prices {trend} as {factor} affects market",
            "Renewable energy adoption {trend} in {region}",
            "Energy companies announce {announcement}",
            "Global energy demand {trend} due to {factor}",
            "New regulations impact {sector} energy market"
        ]
        
        trends = ["rise", "fall", "stabilize", "fluctuate"]
        factors = ["geopolitical tensions", "economic growth", "climate policies", "technological advances"]
        regions = ["Europe", "Asia", "North America", "Middle East"]
        announcements = ["major investments", "strategic partnerships", "sustainability initiatives"]
        sectors = ["renewable", "fossil fuel", "nuclear", "hydroelectric"]
        
        for i in range(10):
            template = np.random.choice(news_templates)
            article = {
                "title": template.format(
                    trend=np.random.choice(trends),
                    factor=np.random.choice(factors),
                    region=np.random.choice(regions),
                    announcement=np.random.choice(announcements),
                    sector=np.random.choice(sectors)
                ),
                "description": f"Energy market update for {commodity or 'general energy'} sector",
                "publishedAt": (base_date + timedelta(hours=i*2)).isoformat(),
                "sentiment": np.random.choice(["positive", "neutral", "negative"]),
                "relevance_score": round(np.random.uniform(0.6, 1.0), 2)
            }
            mock_articles.append(article)
        
        return {
            "commodity": commodity,
            "total_articles": len(mock_articles),
            "articles": mock_articles,
            "sentiment_analysis": {
                "positive": len([a for a in mock_articles if a["sentiment"] == "positive"]),
                "neutral": len([a for a in mock_articles if a["sentiment"] == "neutral"]),
                "negative": len([a for a in mock_articles if a["sentiment"] == "negative"])
            },
            "source": "mock_data",
            "timestamp": datetime.now().isoformat()
        }
    
    def _process_news_data(self, news_data: Dict[str, Any], commodity: str) -> Dict[str, Any]:
        """Process and analyze news data for sentiment and relevance"""
        try:
            articles = news_data.get("articles", [])
            processed_articles = []
            
            for article in articles:
                # Simple sentiment analysis based on keywords
                title = article.get("title", "").lower()
                description = article.get("description", "").lower()
                
                positive_words = ["rise", "growth", "positive", "gain", "increase", "bullish"]
                negative_words = ["fall", "decline", "negative", "loss", "decrease", "bearish"]
                
                sentiment = "neutral"
                positive_count = sum(1 for word in positive_words if word in title or word in description)
                negative_count = sum(1 for word in negative_words if word in title or word in description)
                
                if positive_count > negative_count:
                    sentiment = "positive"
                elif negative_count > positive_count:
                    sentiment = "negative"
                
                # Calculate relevance score
                relevance_score = 0.5  # Base score
                if commodity and commodity.lower() in title.lower():
                    relevance_score += 0.3
                if "energy" in title.lower() or "energy" in description.lower():
                    relevance_score += 0.2
                
                processed_article = {
                    "title": article.get("title"),
                    "description": article.get("description"),
                    "publishedAt": article.get("publishedAt"),
                    "url": article.get("url"),
                    "sentiment": sentiment,
                    "relevance_score": min(relevance_score, 1.0)
                }
                processed_articles.append(processed_article)
            
            # Sort by relevance and sentiment
            processed_articles.sort(key=lambda x: (x["relevance_score"], x["sentiment"] != "negative"), reverse=True)
            
            return {
                "commodity": commodity,
                "total_articles": len(processed_articles),
                "articles": processed_articles[:10],  # Top 10 most relevant
                "sentiment_analysis": {
                    "positive": len([a for a in processed_articles if a["sentiment"] == "positive"]),
                    "neutral": len([a for a in processed_articles if a["sentiment"] == "neutral"]),
                    "negative": len([a for a in processed_articles if a["sentiment"] == "negative"])
                },
                "source": "news_api",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing news data: {e}")
            return {"error": str(e)}
    
    def integrate_news_with_forecast(self, commodity: str, forecast_data: Dict[str, Any], days: int = 7) -> Dict[str, Any]:
        """Integrate news sentiment with price forecasts"""
        try:
            # Get news data
            news_data = self.get_energy_news(commodity, days)
            
            if "error" in news_data:
                return forecast_data
            
            # Calculate news impact factor
            sentiment_scores = news_data.get("sentiment_analysis", {})
            total_articles = sentiment_scores.get("positive", 0) + sentiment_scores.get("neutral", 0) + sentiment_scores.get("negative", 0)
            
            if total_articles == 0:
                return forecast_data
            
            positive_ratio = sentiment_scores.get("positive", 0) / total_articles
            negative_ratio = sentiment_scores.get("negative", 0) / total_articles
            
            # News impact factor: positive news tends to increase prices, negative news decreases them
            news_impact = (positive_ratio - negative_ratio) * 0.1  # 10% max impact
            
            # Apply news impact to forecast
            enhanced_forecast = forecast_data.copy()
            if "forecast_data" in enhanced_forecast:
                for i, point in enumerate(enhanced_forecast["forecast_data"]):
                    if "price" in point:
                        original_price = point["price"]
                        adjusted_price = original_price * (1 + news_impact)
                        point["price"] = round(adjusted_price, 2)
                        point["news_adjustment"] = round(news_impact * 100, 2)
                        point["original_price"] = original_price
            
            enhanced_forecast["news_integration"] = {
                "news_impact_factor": round(news_impact, 4),
                "sentiment_analysis": sentiment_scores,
                "total_articles_analyzed": total_articles,
                "integration_method": "sentiment_weighted_adjustment"
            }
            
            return enhanced_forecast
            
        except Exception as e:
            logger.error(f"Error integrating news with forecast: {e}")
            return forecast_data
    
    def detect_anomalies(self, data: List[float], method: str = "isolation_forest") -> Dict[str, Any]:
        """Detect anomalies in time series data using multiple methods"""
        try:
            if not self.anomaly_detection_enabled:
                return {"anomalies": [], "method": "disabled"}
            
            if method == "isolation_forest":
                return self._detect_anomalies_isolation_forest(data)
            elif method == "statistical":
                return self._detect_anomalies_statistical(data)
            elif method == "zscore":
                return self._detect_anomalies_zscore(data)
            else:
                logger.warning(f"Unknown anomaly detection method: {method}")
                return self._detect_anomalies_statistical(data)
                
        except Exception as e:
            logger.error(f"Error in anomaly detection: {e}")
            return {"anomalies": [], "method": "failed", "error": str(e)}
    
    def _detect_anomalies_isolation_forest(self, data: List[float]) -> Dict[str, Any]:
        """Detect anomalies using Isolation Forest algorithm"""
        try:
            from sklearn.ensemble import IsolationForest
            
            # Reshape data for sklearn
            X = np.array(data).reshape(-1, 1)
            
            # Fit isolation forest
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            predictions = iso_forest.fit_predict(X)
            
            # Find anomalies (predictions == -1)
            anomalies = [i for i, pred in enumerate(predictions) if pred == -1]
            
            return {
                "anomalies": anomalies,
                "method": "isolation_forest",
                "total_points": len(data),
                "anomaly_count": len(anomalies),
                "anomaly_percentage": round(len(anomalies) / len(data) * 100, 2)
            }
            
        except ImportError:
            logger.warning("IsolationForest not available, falling back to statistical method")
            return self._detect_anomalies_statistical(data)
        except Exception as e:
            logger.error(f"Error in isolation forest anomaly detection: {e}")
            return {"anomalies": [], "method": "isolation_forest_failed", "error": str(e)}
    
    def _detect_anomalies_statistical(self, data: List[float]) -> Dict[str, Any]:
        """Detect anomalies using statistical methods (mean + standard deviation)"""
        try:
            data_array = np.array(data)
            mean_val = np.mean(data_array)
            std_val = np.std(data_array)
            
            # Define anomaly threshold
            lower_bound = mean_val - (self.anomaly_threshold * std_val)
            upper_bound = mean_val + (self.anomaly_threshold * std_val)
            
            # Find anomalies
            anomalies = []
            for i, value in enumerate(data_array):
                if value < lower_bound or value > upper_bound:
                    anomalies.append({
                        "index": i,
                        "value": value,
                        "deviation": round((value - mean_val) / std_val, 2)
                    })
            
            return {
                "anomalies": anomalies,
                "method": "statistical",
                "total_points": len(data),
                "anomaly_count": len(anomalies),
                "anomaly_percentage": round(len(anomalies) / len(data) * 100, 2),
                "statistics": {
                    "mean": round(mean_val, 4),
                    "std": round(std_val, 4),
                    "lower_bound": round(lower_bound, 4),
                    "upper_bound": round(upper_bound, 4)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in statistical anomaly detection: {e}")
            return {"anomalies": [], "method": "statistical_failed", "error": str(e)}
    
    def _detect_anomalies_zscore(self, data: List[float]) -> Dict[str, Any]:
        """Detect anomalies using Z-score method"""
        try:
            data_array = np.array(data)
            mean_val = np.mean(data_array)
            std_val = np.std(data_array)
            
            if std_val == 0:
                return {"anomalies": [], "method": "zscore", "error": "Zero standard deviation"}
            
            # Calculate Z-scores
            z_scores = np.abs((data_array - mean_val) / std_val)
            
            # Find anomalies (Z-score > threshold)
            anomalies = []
            for i, z_score in enumerate(z_scores):
                if z_score > self.anomaly_threshold:
                    anomalies.append({
                        "index": i,
                        "value": data_array[i],
                        "z_score": round(z_score, 2)
                    })
            
            return {
                "anomalies": anomalies,
                "method": "zscore",
                "total_points": len(data),
                "anomaly_count": len(anomalies),
                "anomaly_percentage": round(len(anomalies) / len(data) * 100, 2),
                "threshold": self.anomaly_threshold
            }
            
        except Exception as e:
            logger.error(f"Error in Z-score anomaly detection: {e}")
            return {"anomalies": [], "method": "zscore_failed", "error": str(e)}
    
    def forecast_with_anomaly_detection(self, commodity: str, days: int = 30) -> Dict[str, Any]:
        """Generate forecast with integrated anomaly detection"""
        try:
            # Get base forecast
            base_forecast = self.forecast_prices(commodity, days)
            
            if "error" in base_forecast:
                return base_forecast
            
            # Extract price data for anomaly detection
            if "forecast_data" in base_forecast:
                prices = [point.get("price", 0) for point in base_forecast["forecast_data"]]
                
                # Detect anomalies
                anomalies = self.detect_anomalies(prices)
                
                # Add anomaly information to forecast
                base_forecast["anomaly_detection"] = anomalies
                
                # Apply anomaly corrections if needed
                if anomalies.get("anomalies"):
                    base_forecast["anomaly_corrections"] = self._apply_anomaly_corrections(
                        base_forecast["forecast_data"], anomalies
                    )
            
            return base_forecast
            
        except Exception as e:
            logger.error(f"Error in forecast with anomaly detection: {e}")
            return {"error": f"Forecast with anomaly detection failed: {str(e)}"}
    
    def _apply_anomaly_corrections(self, forecast_data: List[Dict], anomalies: Dict) -> List[Dict]:
        """Apply corrections to anomalous forecast points"""
        try:
            corrected_data = forecast_data.copy()
            
            for anomaly in anomalies.get("anomalies", []):
                idx = anomaly.get("index", 0)
                if idx < len(corrected_data):
                    # Apply smoothing correction
                    if idx > 0 and idx < len(corrected_data) - 1:
                        # Use moving average of surrounding points
                        prev_price = corrected_data[idx - 1].get("price", 0)
                        next_price = corrected_data[idx + 1].get("price", 0)
                        corrected_price = (prev_price + next_price) / 2
                        
                        corrected_data[idx]["price"] = round(corrected_price, 2)
                        corrected_data[idx]["anomaly_corrected"] = True
                        corrected_data[idx]["correction_method"] = "moving_average_smoothing"
            
            return corrected_data
            
        except Exception as e:
            logger.error(f"Error applying anomaly corrections: {e}")
            return forecast_data

# Global instance
forecasting_service = ForecastingService()
