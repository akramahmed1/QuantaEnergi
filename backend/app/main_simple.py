from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="QuantaEnergi",
    description="Energy Trading Platform with OpenWeather Integration",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenWeather API key
OPENWEATHER_API_KEY = "83f7b08451bbb075783156b10ce554ef"

@app.get("/")
async def root():
    return {"message": "QuantaEnergi API is running!"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "QuantaEnergi"}

@app.get("/api/weather/current")
async def get_current_weather(lat: float = 33.44, lon: float = -94.04):
    """Get current weather for a location"""
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
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
        logger.error(f"Weather request failed: {e}")
        return {"temp": 20, "success": False, "error": str(e)}

@app.get("/api/weather/forecast")
async def get_weather_forecast(lat: float = 33.44, lon: float = -94.04):
    """Get 5-day weather forecast"""
    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            forecasts = []
            for item in data.get("list", [])[:8]:  # Next 24 hours
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
        logger.error(f"Weather forecast request failed: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/market/prices")
async def get_market_prices():
    """Get mock market prices"""
    return {
        "crude_oil": {"price": 85.50, "change": "+2.3%", "source": "CME"},
        "natural_gas": {"price": 3.20, "change": "-1.1%", "source": "ICE"},
        "electricity": {"price": 45.80, "change": "+0.8%", "source": "NYMEX"}
    }

@app.get("/api/analytics")
async def get_analytics():
    """Get mock analytics data"""
    return {
        "portfolio_value": 125000.00,
        "daily_return": 2.5,
        "risk_score": 35.0,
        "esg_score": 78.0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
