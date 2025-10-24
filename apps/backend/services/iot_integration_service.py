"""
IoT Integration Service
Provides IoT device integration capabilities with OpenWeatherMap API
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import asyncio
import aiohttp
import json
from enum import Enum
import os

logger = logging.getLogger(__name__)

# OpenWeatherMap API configuration
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', 'your_api_key_here')
OPENWEATHER_BASE_URL = 'https://api.openweathermap.org/data/2.5'

class DeviceType(Enum):
    SENSOR = "sensor"
    ACTUATOR = "actuator"
    GATEWAY = "gateway"

class DataType(Enum):
    TEMPERATURE = "temperature"
    PRESSURE = "pressure"
    FLOW = "flow"
    VOLTAGE = "voltage"

class IoTIntegrationService:
    """Service for IoT device integration"""
    
    def __init__(self):
        self.devices = {}
        self.sensor_data = {}
        logger.info("IoT integration service initialized")
    
    async def register_device(self, device_id: str, device_type: str, location: str) -> Dict[str, Any]:
        """Register an IoT device"""
        device = {
            "device_id": device_id,
            "type": device_type,
            "location": location,
            "status": "active",
            "registered_at": datetime.utcnow().isoformat()
        }
        
        self.devices[device_id] = device
        return device
    
    async def collect_sensor_data(self, device_id: str, sensor_type: str) -> Dict[str, Any]:
        """Collect data from IoT sensors"""
        data = {
            "device_id": device_id,
            "sensor_type": sensor_type,
            "value": 25.5,  # Mock sensor reading
            "unit": "celsius",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.sensor_data[f"{device_id}_{sensor_type}"] = data
        return data
    
    async def get_weather_data(self, city: str, country_code: str = "US") -> Dict[str, Any]:
        """Get weather data from OpenWeatherMap API"""
        try:
            url = f"{OPENWEATHER_BASE_URL}/weather"
            params = {
                'q': f"{city},{country_code}",
                'appid': OPENWEATHER_API_KEY,
                'units': 'metric'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "city": data['name'],
                            "country": data['sys']['country'],
                            "temperature": data['main']['temp'],
                            "humidity": data['main']['humidity'],
                            "pressure": data['main']['pressure'],
                            "wind_speed": data['wind']['speed'],
                            "wind_direction": data['wind'].get('deg', 0),
                            "weather_description": data['weather'][0]['description'],
                            "solar_radiation": self._calculate_solar_radiation(data),
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    else:
                        logger.error(f"Weather API error: {response.status}")
                        return {"error": f"API error: {response.status}"}
        except Exception as e:
            logger.error(f"Weather data collection failed: {e}")
            return {"error": str(e)}
    
    def _calculate_solar_radiation(self, weather_data: Dict[str, Any]) -> float:
        """Calculate solar radiation based on weather conditions"""
        try:
            # Basic solar radiation calculation based on weather conditions
            cloud_cover = weather_data.get('clouds', {}).get('all', 50)  # Default 50% cloud cover
            weather_main = weather_data.get('weather', [{}])[0].get('main', 'Clear')
            
            # Base solar radiation (W/m²)
            base_radiation = 1000
            
            # Adjust based on weather conditions
            if weather_main == 'Clear':
                radiation_factor = 0.9
            elif weather_main == 'Clouds':
                radiation_factor = 0.6
            elif weather_main == 'Rain':
                radiation_factor = 0.3
            elif weather_main == 'Snow':
                radiation_factor = 0.2
            else:
                radiation_factor = 0.5
            
            # Adjust for cloud cover
            cloud_factor = 1 - (cloud_cover / 100) * 0.7
            
            solar_radiation = base_radiation * radiation_factor * cloud_factor
            return round(solar_radiation, 2)
            
        except Exception as e:
            logger.error(f"Solar radiation calculation failed: {e}")
            return 0.0