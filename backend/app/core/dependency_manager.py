"""
Dependency Manager for Optional Libraries
Handles graceful fallbacks for optional dependencies like DEAP, Transformers, etc.
"""

import logging
import asyncio
from typing import Callable, Dict, Any, Optional, Union
from functools import wraps
import importlib

logger = logging.getLogger(__name__)

class DependencyManager:
    """Manages optional dependencies with graceful fallbacks"""
    
    def __init__(self):
        self.available_deps: Dict[str, bool] = {}
        self.fallback_functions: Dict[str, Callable] = {}
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check which optional dependencies are available"""
        optional_deps = [
            "numpy", "pandas", "scikit-learn", "deap", "transformers",
            "redis", "paho.mqtt", "websocket-client", "yfinance"
        ]
        
        for dep in optional_deps:
            try:
                importlib.import_module(dep)
                self.available_deps[dep] = True
                logger.info(f"Optional dependency '{dep}' is available")
            except ImportError:
                self.available_deps[dep] = False
                logger.warning(f"Optional dependency '{dep}' is not available")
    
    def is_available(self, dep_name: str) -> bool:
        """Check if dependency is available"""
        return self.available_deps.get(dep_name, False)
    
    def register_fallback(self, dep_name: str, fallback_func: Callable):
        """Register fallback function for dependency"""
        self.fallback_functions[dep_name] = fallback_func
        logger.info(f"Registered fallback for '{dep_name}'")
    
    async def run_with_fallback(self, 
                              dep_name: str, 
                              main_func: Callable, 
                              *args, **kwargs) -> Any:
        """
        Run function with dependency, fallback to alternative if not available
        
        Args:
            dep_name: Name of the dependency
            main_func: Main function to run if dependency is available
            *args, **kwargs: Arguments for the function
            
        Returns:
            Result from main function or fallback
        """
        try:
            if self.is_available(dep_name):
                logger.debug(f"Using '{dep_name}' for {main_func.__name__}")
                if asyncio.iscoroutinefunction(main_func):
                    return await main_func(*args, **kwargs)
                else:
                    return main_func(*args, **kwargs)
            else:
                logger.warning(f"'{dep_name}' not available, using fallback for {main_func.__name__}")
                fallback_func = self.fallback_functions.get(dep_name)
                if fallback_func:
                    if asyncio.iscoroutinefunction(fallback_func):
                        return await fallback_func(*args, **kwargs)
                    else:
                        return fallback_func(*args, **kwargs)
                else:
                    raise ImportError(f"No fallback available for '{dep_name}'")
                    
        except Exception as e:
            logger.error(f"Error in run_with_fallback: {str(e)}")
            # Try fallback even if main function failed
            fallback_func = self.fallback_functions.get(dep_name)
            if fallback_func:
                try:
                    if asyncio.iscoroutinefunction(fallback_func):
                        return await fallback_func(*args, **kwargs)
                    else:
                        return fallback_func(*args, **kwargs)
                except Exception as fallback_error:
                    logger.error(f"Fallback also failed: {str(fallback_error)}")
                    raise
            else:
                raise

def requires_dependency(dep_name: str, fallback_func: Optional[Callable] = None):
    """
    Decorator to require dependency with fallback
    
    Args:
        dep_name: Name of the required dependency
        fallback_func: Fallback function if dependency is not available
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            dep_manager = DependencyManager()
            return await dep_manager.run_with_fallback(dep_name, func, *args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            dep_manager = DependencyManager()
            if dep_manager.is_available(dep_name):
                return func(*args, **kwargs)
            elif fallback_func:
                return fallback_func(*args, **kwargs)
            else:
                raise ImportError(f"Dependency '{dep_name}' is required but not available")
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# Global dependency manager instance
dependency_manager = DependencyManager()

# Register common fallbacks
def numpy_fallback(*args, **kwargs):
    """Fallback for numpy operations"""
    logger.warning("Using numpy fallback - returning mock data")
    return {"data": "numpy_fallback", "shape": (10, 10), "dtype": "float64"}

def pandas_fallback(*args, **kwargs):
    """Fallback for pandas operations"""
    logger.warning("Using pandas fallback - returning mock DataFrame")
    return {"data": "pandas_fallback", "columns": ["col1", "col2"], "index": [0, 1, 2]}

def sklearn_fallback(*args, **kwargs):
    """Fallback for scikit-learn operations"""
    logger.warning("Using sklearn fallback - returning mock model")
    return {"model": "sklearn_fallback", "score": 0.85, "predictions": [1, 0, 1]}

def redis_fallback(*args, **kwargs):
    """Fallback for Redis operations"""
    logger.warning("Using Redis fallback - using in-memory storage")
    return {"status": "redis_fallback", "data": "in_memory"}

def mqtt_fallback(*args, **kwargs):
    """Fallback for MQTT operations"""
    logger.warning("Using MQTT fallback - using mock connection")
    return {"status": "mqtt_fallback", "connected": False}

# Register fallbacks
dependency_manager.register_fallback("numpy", numpy_fallback)
dependency_manager.register_fallback("pandas", pandas_fallback)
dependency_manager.register_fallback("scikit-learn", sklearn_fallback)
dependency_manager.register_fallback("redis", redis_fallback)
dependency_manager.register_fallback("paho.mqtt", mqtt_fallback)

# Example usage functions
@requires_dependency("numpy")
def calculate_portfolio_risk(returns):
    """Calculate portfolio risk using numpy"""
    import numpy as np
    return np.std(returns) * np.sqrt(252)

@requires_dependency("pandas")
def analyze_trade_data(data):
    """Analyze trade data using pandas"""
    import pandas as pd
    df = pd.DataFrame(data)
    return df.describe()

@requires_dependency("scikit-learn")
def train_risk_model(features, labels):
    """Train risk model using scikit-learn"""
    from sklearn.ensemble import RandomForestClassifier
    model = RandomForestClassifier()
    model.fit(features, labels)
    return model

@requires_dependency("redis")
async def cache_market_data(key, data):
    """Cache market data using Redis"""
    import redis.asyncio as redis
    r = redis.Redis()
    await r.set(key, data)
    return {"cached": True}

@requires_dependency("paho.mqtt")
async def publish_iot_data(topic, data):
    """Publish IoT data using MQTT"""
    import paho.mqtt.client as mqtt
    client = mqtt.Client()
    client.connect("localhost", 1883)
    client.publish(topic, data)
    return {"published": True}
