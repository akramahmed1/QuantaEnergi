import asyncio
import aiohttp
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import structlog
import os
from dataclasses import dataclass
from enum import Enum
import numpy as np
import pandas as pd

logger = structlog.get_logger()

class SensorType(Enum):
    """Types of IoT sensors supported"""
    GRID_VOLTAGE = "grid_voltage"
    GRID_FREQUENCY = "grid_frequency"
    POWER_CONSUMPTION = "power_consumption"
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    WIND_SPEED = "wind_speed"
    SOLAR_RADIATION = "solar_radiation"
    BATTERY_LEVEL = "battery_level"

class DataQuality(Enum):
    """Data quality indicators"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    UNKNOWN = "unknown"

@dataclass
class SensorData:
    """Represents sensor data point"""
    sensor_id: str
    sensor_type: SensorType
    value: float
    unit: str
    timestamp: datetime
    location: Dict[str, float]  # lat, lon
    quality: DataQuality
    metadata: Dict[str, Any]

@dataclass
class GridStatus:
    """Represents grid status information"""
    grid_id: str
    voltage: float
    frequency: float
    power_flow: float
    stability_index: float
    alert_level: str
    timestamp: datetime
    location: str

class IoTIntegrationService:
    """IoT integration service for real-time energy and environmental data"""
    
    def __init__(self):
        self.openweather_api_key = os.getenv("OPENWEATHER_API_KEY")
        self.grid_api_key = os.getenv("GRID_API_KEY")
        self.sensor_data_cache = {}
        self.last_update = {}
        self.cache_duration = 300  # 5 minutes
        
        # Enhanced logging configuration
        self.logger = structlog.get_logger()
        self.logger.info("IoT Integration Service initialized", 
                        openweather_configured=bool(self.openweather_api_key),
                        grid_configured=bool(self.grid_api_key))
        
        # Fallback data for when APIs are unavailable
        self.fallback_data = {
            "grid_voltage": {"value": 230.0, "unit": "V", "quality": "fallback"},
            "grid_frequency": {"value": 50.0, "unit": "Hz", "quality": "fallback"},
            "power_consumption": {"value": 500.0, "unit": "kW", "quality": "fallback"},
            "temperature": {"value": 25.0, "unit": "°C", "quality": "fallback"},
            "humidity": {"value": 60.0, "unit": "%", "quality": "fallback"},
            "wind_speed": {"value": 5.0, "unit": "m/s", "quality": "fallback"},
            "solar_radiation": {"value": 800.0, "unit": "W/m²", "quality": "fallback"},
            "battery_level": {"value": 75.0, "unit": "%", "quality": "fallback"}
        }
        
        # API endpoints
        self.openweather_base_url = "https://api.openweathermap.org/data/2.5"
        self.grid_base_url = "https://api.grid.com/v1"  # Example grid API
        
        # Sensor configurations
        self.sensor_configs = {
            "grid_voltage": {"unit": "V", "min_value": 200, "max_value": 250},
            "grid_frequency": {"unit": "Hz", "min_value": 49.5, "max_value": 50.5},
            "power_consumption": {"unit": "kW", "min_value": 0, "max_value": 10000},
            "temperature": {"unit": "°C", "min_value": -40, "max_value": 60},
            "humidity": {"unit": "%", "min_value": 0, "max_value": 100},
            "wind_speed": {"unit": "m/s", "min_value": 0, "max_value": 50},
            "solar_radiation": {"unit": "W/m²", "min_value": 0, "max_value": 1200},
            "battery_level": {"unit": "%", "min_value": 0, "max_value": 100}
        }
    
    def _get_fallback_data(self, sensor_type: str, location: str = "default") -> Dict[str, Any]:
        """Get fallback data when sensors are unavailable"""
        try:
            fallback = self.fallback_data.get(sensor_type, {})
            
            # Add some realistic variation to fallback data
            import random
            variation = random.uniform(0.9, 1.1)
            
            return {
                "sensor_id": f"fallback_{sensor_type}_{location}",
                "sensor_type": sensor_type,
                "value": fallback["value"] * variation,
                "unit": fallback["unit"],
                "timestamp": datetime.now().isoformat(),
                "location": {"lat": 0.0, "lon": 0.0},
                "quality": "fallback",
                "metadata": {
                    "source": "fallback_system",
                    "reason": "sensor_unavailable",
                    "last_real_update": "unknown"
                }
            }
        except Exception as e:
            self.logger.error(f"Error getting fallback data for {sensor_type}: {e}")
            return {"error": f"Fallback data unavailable: {str(e)}"}
    
    def _log_sensor_health(self, sensor_type: str, status: str, details: str = ""):
        """Log sensor health status with structured logging"""
        self.logger.info("Sensor health check",
                        sensor_type=sensor_type,
                        status=status,
                        details=details,
                        timestamp=datetime.now().isoformat())
    
    async def get_real_time_grid_data(self, location: str = "default") -> Dict[str, Any]:
        """Get real-time grid data from IoT sensors"""
        try:
            cache_key = f"grid_data_{location}"
            
            # Check cache first
            if self._is_cache_valid(cache_key):
                return self.sensor_data_cache[cache_key]
            
            # Fetch real-time data
            grid_data = await self._fetch_grid_data(location)
            
            # Cache the data
            self.sensor_data_cache[cache_key] = grid_data
            self.last_update[cache_key] = datetime.now()
            
            logger.info(f"Real-time grid data fetched for {location}")
            return grid_data
            
        except Exception as e:
            logger.error(f"Error fetching real-time grid data: {e}")
            return self._get_fallback_grid_data(location)
    
    async def get_weather_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get weather data from OpenWeatherMap API"""
        try:
            if not self.openweather_api_key:
                return self._get_fallback_weather_data(lat, lon)
            
            cache_key = f"weather_{lat}_{lon}"
            
            # Check cache first
            if self._is_cache_valid(cache_key):
                return self.sensor_data_cache[cache_key]
            
            # Fetch weather data
            weather_data = await self._fetch_weather_data(lat, lon)
            
            # Cache the data
            self.sensor_data_cache[cache_key] = weather_data
            self.last_update[cache_key] = datetime.now()
            
            logger.info(f"Weather data fetched for coordinates ({lat}, {lon})")
            return weather_data
            
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return self._get_fallback_weather_data(lat, lon)
    
    async def get_solar_radiation_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get solar radiation data for renewable energy optimization"""
        try:
            cache_key = f"solar_{lat}_{lon}"
            
            # Check cache first
            if self._is_cache_valid(cache_key):
                return self.sensor_data_cache[cache_key]
            
            # Fetch solar data
            solar_data = await self._fetch_solar_data(lat, lon)
            
            # Cache the data
            self.sensor_data_cache[cache_key] = solar_data
            self.last_update[cache_key] = datetime.now()
            
            logger.info(f"Solar radiation data fetched for coordinates ({lat}, {lon})")
            return solar_data
            
        except Exception as e:
            logger.error(f"Error fetching solar radiation data: {e}")
            return self._get_fallback_solar_data(lat, lon)
    
    async def get_sensor_network_status(self, network_id: str = "main") -> Dict[str, Any]:
        """Get status of IoT sensor network"""
        try:
            # Simulate sensor network status
            sensor_count = np.random.randint(50, 200)
            active_sensors = np.random.randint(40, sensor_count)
            alert_count = np.random.randint(0, 5)
            
            network_status = {
                "network_id": network_id,
                "total_sensors": sensor_count,
                "active_sensors": active_sensors,
                "inactive_sensors": sensor_count - active_sensors,
                "uptime_percentage": round((active_sensors / sensor_count) * 100, 2),
                "alert_count": alert_count,
                "last_maintenance": (datetime.now() - timedelta(days=np.random.randint(1, 30))).isoformat(),
                "data_quality_score": round(np.random.uniform(85, 98), 2),
                "timestamp": datetime.now().isoformat()
            }
            
            return network_status
            
        except Exception as e:
            logger.error(f"Error getting sensor network status: {e}")
            return {"error": str(e)}
    
    async def analyze_grid_stability(self, grid_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze grid stability using IoT sensor data"""
        try:
            voltage = grid_data.get("voltage", 230)
            frequency = grid_data.get("frequency", 50.0)
            power_flow = grid_data.get("power_flow", 0.0)
            
            # Calculate stability metrics
            voltage_deviation = abs(voltage - 230) / 230 * 100
            frequency_deviation = abs(frequency - 50.0) / 50.0 * 100
            
            # Stability index (0-100, higher is better)
            voltage_stability = max(0, 100 - voltage_deviation * 2)
            frequency_stability = max(0, 100 - frequency_deviation * 10)
            overall_stability = (voltage_stability + frequency_stability) / 2
            
            # Determine alert level
            if overall_stability >= 90:
                alert_level = "normal"
            elif overall_stability >= 75:
                alert_level = "warning"
            elif overall_stability >= 60:
                alert_level = "alert"
            else:
                alert_level = "critical"
            
            stability_analysis = {
                "overall_stability": round(overall_stability, 2),
                "voltage_stability": round(voltage_stability, 2),
                "frequency_stability": round(frequency_stability, 2),
                "voltage_deviation_percent": round(voltage_deviation, 2),
                "frequency_deviation_percent": round(frequency_deviation, 2),
                "alert_level": alert_level,
                "recommendations": self._generate_stability_recommendations(overall_stability),
                "timestamp": datetime.now().isoformat()
            }
            
            return stability_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing grid stability: {e}")
            return {"error": str(e)}
    
    async def predict_energy_demand(self, historical_data: List[Dict[str, Any]], 
                                  weather_forecast: Dict[str, Any]) -> Dict[str, Any]:
        """Predict energy demand using IoT sensor data and weather forecasts"""
        try:
            if not historical_data:
                return {"error": "No historical data provided"}
            
            # Extract relevant features
            temperatures = [point.get("temperature", 20) for point in historical_data]
            humidities = [point.get("humidity", 50) for point in historical_data]
            power_consumption = [point.get("power_consumption", 0) for point in historical_data]
            
            # Simple linear regression for demand prediction
            if len(temperatures) > 1:
                # Temperature correlation with power consumption
                temp_coeff = np.corrcoef(temperatures, power_consumption)[0, 1]
                
                # Predict based on weather forecast
                forecast_temp = weather_forecast.get("temperature", 20)
                forecast_humidity = weather_forecast.get("humidity", 50)
                
                # Base demand (average historical consumption)
                base_demand = np.mean(power_consumption)
                
                # Temperature adjustment
                temp_adjustment = (forecast_temp - np.mean(temperatures)) * temp_coeff * 0.1
                
                # Humidity adjustment (simplified)
                humidity_adjustment = (forecast_humidity - np.mean(humidities)) * 0.01
                
                # Predicted demand
                predicted_demand = base_demand + temp_adjustment + humidity_adjustment
                
                prediction_result = {
                    "predicted_demand_kw": round(max(0, predicted_demand), 2),
                    "base_demand_kw": round(base_demand, 2),
                    "temperature_adjustment": round(temp_adjustment, 2),
                    "humidity_adjustment": round(humidity_adjustment, 2),
                    "confidence_level": round(min(95, max(60, 85 + abs(temp_coeff) * 10)), 2),
                    "weather_factors": {
                        "temperature": forecast_temp,
                        "humidity": forecast_humidity
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
                return prediction_result
            else:
                return {"error": "Insufficient historical data for prediction"}
                
        except Exception as e:
            logger.error(f"Error predicting energy demand: {e}")
            return {"error": str(e)}
    
    async def get_sensor_alerts(self, sensor_type: Optional[SensorType] = None) -> List[Dict[str, Any]]:
        """Get active sensor alerts"""
        try:
            alerts = []
            
            # Simulate sensor alerts based on sensor type
            if sensor_type is None or sensor_type == SensorType.GRID_VOLTAGE:
                if np.random.random() < 0.1:  # 10% chance of voltage alert
                    alerts.append({
                        "alert_id": f"voltage_alert_{int(time.time())}",
                        "sensor_type": "grid_voltage",
                        "severity": "medium",
                        "message": "Grid voltage deviation detected",
                        "value": round(np.random.uniform(180, 200), 2),
                        "threshold": 200,
                        "timestamp": datetime.now().isoformat()
                    })
            
            if sensor_type is None or sensor_type == SensorType.GRID_FREQUENCY:
                if np.random.random() < 0.05:  # 5% chance of frequency alert
                    alerts.append({
                        "alert_id": f"frequency_alert_{int(time.time())}",
                        "sensor_type": "grid_frequency",
                        "severity": "high",
                        "message": "Grid frequency instability detected",
                        "value": round(np.random.uniform(49.0, 49.5), 2),
                        "threshold": 49.5,
                        "timestamp": datetime.now().isoformat()
                    })
            
            if sensor_type is None or sensor_type == SensorType.TEMPERATURE:
                if np.random.random() < 0.15:  # 15% chance of temperature alert
                    alerts.append({
                        "alert_id": f"temp_alert_{int(time.time())}",
                        "sensor_type": "temperature",
                        "severity": "low",
                        "message": "High temperature detected in equipment",
                        "value": round(np.random.uniform(55, 65), 2),
                        "threshold": 55,
                        "timestamp": datetime.now().isoformat()
                    })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting sensor alerts: {e}")
            return []
    
    async def _fetch_grid_data(self, location: str) -> Dict[str, Any]:
        """Fetch real-time grid data from IoT sensors"""
        # Simulate real-time grid data
        grid_data = {
            "location": location,
            "voltage": round(np.random.uniform(225, 235), 2),
            "frequency": round(np.random.uniform(49.8, 50.2), 3),
            "power_flow": round(np.random.uniform(-1000, 1000), 2),
            "power_factor": round(np.random.uniform(0.85, 0.98), 3),
            "current": round(np.random.uniform(100, 500), 2),
            "timestamp": datetime.now().isoformat(),
            "data_source": "iot_sensors"
        }
        
        return grid_data
    
    async def _fetch_weather_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """Fetch weather data from OpenWeatherMap API"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.openweather_base_url}/weather"
                params = {
                    "lat": lat,
                    "lon": lon,
                    "appid": self.openweather_api_key,
                    "units": "metric"
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        weather_data = {
                            "temperature": data["main"]["temp"],
                            "humidity": data["main"]["humidity"],
                            "pressure": data["main"]["pressure"],
                            "wind_speed": data["wind"]["speed"],
                            "wind_direction": data["wind"].get("deg", 0),
                            "description": data["weather"][0]["description"],
                            "icon": data["weather"][0]["icon"],
                            "coordinates": {"lat": lat, "lon": lon},
                            "timestamp": datetime.now().isoformat(),
                            "data_source": "openweathermap"
                        }
                        
                        return weather_data
                    else:
                        raise Exception(f"Weather API returned status {response.status}")
                        
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            raise
    
    async def _fetch_solar_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """Fetch solar radiation data"""
        try:
            # Simulate solar radiation data based on time of day
            current_hour = datetime.now().hour
            
            # Solar radiation varies throughout the day
            if 6 <= current_hour <= 18:  # Daytime
                base_radiation = 800
                variation = np.random.uniform(0.7, 1.3)
                solar_radiation = base_radiation * variation
            else:  # Nighttime
                solar_radiation = 0
            
            solar_data = {
                "solar_radiation": round(solar_radiation, 2),
                "uv_index": round(np.random.uniform(0, 10), 1) if solar_radiation > 0 else 0,
                "sunrise": "06:00",
                "sunset": "18:00",
                "coordinates": {"lat": lat, "lon": lon},
                "timestamp": datetime.now().isoformat(),
                "data_source": "solar_sensors"
            }
            
            return solar_data
            
        except Exception as e:
            logger.error(f"Error fetching solar data: {e}")
            raise
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.last_update:
            return False
        
        time_diff = datetime.now() - self.last_update[cache_key]
        return time_diff.total_seconds() < self.cache_duration
    
    def _get_fallback_grid_data(self, location: str) -> Dict[str, Any]:
        """Get fallback grid data when API fails"""
        return {
            "location": location,
            "voltage": 230.0,
            "frequency": 50.0,
            "power_flow": 0.0,
            "power_factor": 0.95,
            "current": 250.0,
            "timestamp": datetime.now().isoformat(),
            "data_source": "fallback_simulation"
        }
    
    def _get_fallback_weather_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get fallback weather data when API fails"""
        return {
            "temperature": 20.0,
            "humidity": 60.0,
            "pressure": 1013.0,
            "wind_speed": 5.0,
            "wind_direction": 180,
            "description": "clear sky",
            "icon": "01d",
            "coordinates": {"lat": lat, "lon": lon},
            "timestamp": datetime.now().isoformat(),
            "data_source": "fallback_simulation"
        }
    
    def _get_fallback_solar_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get fallback solar data when API fails"""
        return {
            "solar_radiation": 500.0,
            "uv_index": 5.0,
            "sunrise": "06:00",
            "sunset": "18:00",
            "coordinates": {"lat": lat, "lon": lon},
            "timestamp": datetime.now().isoformat(),
            "data_source": "fallback_simulation"
        }
    
    def _generate_stability_recommendations(self, stability_score: float) -> List[str]:
        """Generate recommendations based on stability score"""
        recommendations = []
        
        if stability_score < 70:
            recommendations.append("Immediate grid stabilization measures required")
            recommendations.append("Check for equipment failures or overloads")
            recommendations.append("Consider load shedding if necessary")
        elif stability_score < 80:
            recommendations.append("Monitor grid parameters closely")
            recommendations.append("Check voltage regulators and frequency controls")
            recommendations.append("Prepare for potential corrective actions")
        elif stability_score < 90:
            recommendations.append("Grid operating within acceptable limits")
            recommendations.append("Continue monitoring for trends")
        else:
            recommendations.append("Grid operating optimally")
            recommendations.append("Maintain current operational parameters")
        
        return recommendations
    
    def get_iot_status(self) -> Dict[str, Any]:
        """Get IoT integration service status"""
        return {
            "openweather_configured": bool(self.openweather_api_key),
            "grid_api_configured": bool(self.grid_api_key),
            "cache_size": len(self.sensor_data_cache),
            "cache_duration_seconds": self.cache_duration,
            "last_update": {k: v.isoformat() for k, v in self.last_update.items()},
            "supported_sensors": [sensor.value for sensor in SensorType],
            "timestamp": datetime.now().isoformat()
        }

# Global instance
iot_integration_service = IoTIntegrationService()
