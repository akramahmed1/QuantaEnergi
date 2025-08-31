import requests
import logging
from pydantic_settings import BaseSettings
from typing import Dict, Any

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    openweather_api_key: str = "83f7b08451bbb075783156b10ce554ef"
    
    class Config:
        env_file = ".env"

settings = Settings()

async def get_weather(lat: float, lon: float) -> Dict[str, Any]:
    """Get weather data from OpenWeather API"""
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={settings.openweather_api_key}&units=metric"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "temp": data.get("main", {}).get("temp", 20),
                "humidity": data.get("main", {}).get("humidity", 50),
                "description": data.get("weather", [{}])[0].get("description", "Unknown"),
                "wind_speed": data.get("wind", {}).get("speed", 0),
                "success": True
            }
        else:
            logger.error(f"OpenWeather API error: {response.status_code}")
            return {"temp": 20, "success": False, "error": f"API Error: {response.status_code}"}
            
    except Exception as e:
        logger.error(f"OpenWeather request failed: {e}")
        return {"temp": 20, "success": False, "error": str(e)}

async def get_weather_forecast(lat: float, lon: float) -> Dict[str, Any]:
    """Get 5-day weather forecast"""
    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={settings.openweather_api_key}&units=metric"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            forecasts = []
            for item in data.get("list", [])[:8]:  # Next 24 hours (3-hour intervals)
                forecasts.append({
                    "time": item.get("dt_txt"),
                    "temp": item.get("main", {}).get("temp"),
                    "description": item.get("weather", [{}])[0].get("description")
                })
            return {"forecasts": forecasts, "success": True}
        else:
            logger.error(f"OpenWeather forecast API error: {response.status_code}")
            return {"success": False, "error": f"API Error: {response.status_code}"}
            
    except Exception as e:
        logger.error(f"OpenWeather forecast request failed: {e}")
        return {"success": False, "error": str(e)}
