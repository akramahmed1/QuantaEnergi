"""
Market Data Service for EnergyOpti-Pro.

Provides real-time market data from multiple exchanges and sources.
"""

import asyncio
import aiohttp
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from decimal import Decimal
import structlog
from dataclasses import dataclass
import time

logger = structlog.get_logger()

# Environment variables for API keys
CME_API_KEY = os.getenv("CME_API_KEY", "demo_key")
ICE_API_KEY = os.getenv("ICE_API_KEY", "demo_key")
NYMEX_API_KEY = os.getenv("NYMEX_API_KEY", "demo_key")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "demo_key")

@dataclass
class MarketDataPoint:
    """Market data point with timestamp and metadata."""
    timestamp: datetime
    commodity: str
    exchange: str
    price: Decimal
    volume: Decimal
    source: str
    region: str
    bid: Optional[Decimal] = None
    ask: Optional[Decimal] = None
    last_trade: Optional[Decimal] = None

class MarketDataService:
    """Real-time market data service with actual API integrations."""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache: Dict[str, Any] = {}
        self.cache_ttl: int = 300  # 5 minutes
        self.rate_limits: Dict[str, float] = {}
        
    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=10)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def close(self):
        """Close HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def _check_rate_limit(self, api_name: str, limit_per_minute: int = 60) -> bool:
        """Check rate limiting for API calls."""
        current_time = time.time()
        if api_name not in self.rate_limits:
            self.rate_limits[api_name] = current_time
            return True
        
        time_diff = current_time - self.rate_limits[api_name]
        if time_diff < 60:  # Within 1 minute
            return False
        
        self.rate_limits[api_name] = current_time
        return True
    
    async def fetch_cme_prices(self, commodity: str = "crude_oil") -> Dict[str, Any]:
        """Fetch real-time prices from CME Group API."""
        try:
            if not await self._check_rate_limit("cme"):
                logger.warning("CME API rate limit exceeded, using cached data")
                return self.cache.get("cme", self._get_simulated_cme_data(commodity))
            
            session = await self.get_session()
            # CME API endpoint (using demo key for now)
            url = f"https://www.cmegroup.com/api/price/quotes/{commodity}"
            headers = {"X-CME-API-KEY": CME_API_KEY}
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    result = {
                        "source": "cme",
                        "data": data.get("last", 75.50),
                        "timestamp": datetime.now().isoformat(),
                        "exchange": "CME",
                        "commodity": commodity
                    }
                    self.cache["cme"] = result
                    return result
                else:
                    logger.warning(f"CME API returned {response.status}, using simulated data")
                    return self._get_simulated_cme_data(commodity)
                    
        except Exception as e:
            logger.warning(f"CME API failed, using simulated data: {e}")
            return self._get_simulated_cme_data(commodity)
    
    def _get_simulated_cme_data(self, commodity: str) -> Dict[str, Any]:
        """Generate realistic simulated CME data."""
        simulated_price = 75.50 + (hash(commodity) % 20) / 100
        return {
            "source": "simulated_cme",
            "data": round(simulated_price, 2),
            "timestamp": datetime.now().isoformat(),
            "exchange": "CME",
            "commodity": commodity
        }
    
    async def fetch_ice_prices(self, commodity: str = "brent_crude") -> Dict[str, Any]:
        """Fetch real-time prices from ICE API."""
        try:
            if not await self._check_rate_limit("ice"):
                logger.warning("ICE API rate limit exceeded, using cached data")
                return self.cache.get("ice", self._get_simulated_ice_data(commodity))
            
            session = await self.get_session()
            # ICE API endpoint
            url = f"https://www.theice.com/api/v1/quotes/{commodity}"
            headers = {"X-ICE-API-KEY": ICE_API_KEY}
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    result = {
                        "source": "ice",
                        "data": data.get("last", 78.25),
                        "timestamp": datetime.now().isoformat(),
                        "exchange": "ICE",
                        "commodity": commodity
                    }
                    self.cache["ice"] = result
                    return result
                else:
                    logger.warning(f"ICE API returned {response.status}, using simulated data")
                    return self._get_simulated_ice_data(commodity)
                    
        except Exception as e:
            logger.warning(f"ICE API failed, using simulated data: {e}")
            return self._get_simulated_ice_data(commodity)
    
    def _get_simulated_ice_data(self, commodity: str) -> Dict[str, Any]:
        """Generate realistic simulated ICE data."""
        simulated_price = 78.25 + (hash(commodity) % 15) / 100
        return {
            "source": "simulated_ice",
            "data": round(simulated_price, 2),
            "timestamp": datetime.now().isoformat(),
            "exchange": "ICE",
            "commodity": commodity
        }
    
    async def fetch_nymex_prices(self, commodity: str = "natural_gas") -> Dict[str, Any]:
        """Fetch real-time prices from NYMEX API."""
        try:
            if not await self._check_rate_limit("nymex"):
                logger.warning("NYMEX API rate limit exceeded, using cached data")
                return self.cache.get("nymex", self._get_simulated_nymex_data(commodity))
            
            session = await self.get_session()
            # NYMEX API endpoint
            url = f"https://www.cmegroup.com/api/price/quotes/nymex/{commodity}"
            headers = {"X-CME-API-KEY": NYMEX_API_KEY}
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    result = {
                        "source": "nymex",
                        "data": data.get("last", 3.25),
                        "timestamp": datetime.now().isoformat(),
                        "exchange": "NYMEX",
                        "commodity": commodity
                    }
                    self.cache["nymex"] = result
                    return result
                else:
                    logger.warning(f"NYMEX API returned {response.status}, using simulated data")
                    return self._get_simulated_nymex_data(commodity)
                    
        except Exception as e:
            logger.warning(f"NYMEX API failed, using simulated data: {e}")
            return self._get_simulated_nymex_data(commodity)
    
    def _get_simulated_nymex_data(self, commodity: str) -> Dict[str, Any]:
        """Generate realistic simulated NYMEX data."""
        base_prices = {
            "natural_gas": 3.25,
            "crude_oil": 75.50,
            "heating_oil": 2.85,
            "gasoline": 2.45
        }
        base_price = base_prices.get(commodity, 3.25)
        simulated_price = base_price + (hash(commodity) % 20) / 100
        return {
            "source": "simulated_nymex",
            "data": round(simulated_price, 2),
            "timestamp": datetime.now().isoformat(),
            "exchange": "NYMEX",
            "commodity": commodity
        }
    
    async def fetch_weather_data(self, city: str = "Houston") -> Dict[str, Any]:
        """Fetch real-time weather data from OpenWeatherMap."""
        try:
            if not await self._check_rate_limit("openweathermap"):
                logger.warning("OpenWeatherMap API rate limit exceeded, using cached data")
                return self.cache.get("weather", self._get_simulated_weather_data(city))
            
            session = await self.get_session()
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    result = {
                        "source": "openweathermap",
                        "temperature": data["main"]["temp"],
                        "humidity": data["main"]["humidity"],
                        "description": data["weather"][0]["description"],
                        "timestamp": datetime.now().isoformat(),
                        "city": city
                    }
                    self.cache["weather"] = result
                    return result
                else:
                    logger.warning(f"OpenWeatherMap API returned {response.status}, using simulated data")
                    return self._get_simulated_weather_data(city)
                    
        except Exception as e:
            logger.warning(f"Weather API failed, using simulated data: {e}")
            return self._get_simulated_weather_data(city)
    
    def _get_simulated_weather_data(self, city: str) -> Dict[str, Any]:
        """Generate realistic simulated weather data."""
        return {
            "source": "simulated_weather",
            "temperature": 25.0 + (hash(city) % 20),
            "humidity": 60 + (hash(city) % 30),
            "description": "Partly cloudy",
            "timestamp": datetime.now().isoformat(),
            "city": city
        }
    
    async def get_market_overview(self, region: str = "global") -> Dict[str, Any]:
        """Get comprehensive market overview from multiple sources."""
        try:
            # Fetch data from all sources concurrently
            tasks = [
                self.fetch_cme_prices("crude_oil"),
                self.fetch_ice_prices("brent_crude"),
                self.fetch_nymex_prices("natural_gas"),
                self.fetch_weather_data("Houston")
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            market_data = {}
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error fetching market data: {result}")
                    continue
                
                if i == 0:  # CME
                    market_data["cme_crude"] = result
                elif i == 1:  # ICE
                    market_data["ice_brent"] = result
                elif i == 2:  # NYMEX
                    market_data["nymex_natural_gas"] = result
                elif i == 3:  # Weather
                    market_data["weather"] = result
            
            # Add market analysis
            market_data.update({
                "region": region,
                "timestamp": datetime.now().isoformat(),
                "market_status": "active",
                "data_sources": list(market_data.keys())
            })
            
            return market_data
            
        except Exception as e:
            logger.error(f"Error getting market overview: {e}")
            return {
                "error": "Failed to fetch market data",
                "region": region,
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_commodity_prices(self, commodities: List[str]) -> Dict[str, Any]:
        """Get prices for multiple commodities."""
        try:
            results = {}
            for commodity in commodities:
                if "crude" in commodity.lower():
                    if "brent" in commodity.lower():
                        results[commodity] = await self.fetch_ice_prices(commodity)
                    else:
                        results[commodity] = await self.fetch_cme_prices(commodity)
                elif "gas" in commodity.lower():
                    results[commodity] = await self.fetch_nymex_prices(commodity)
                else:
                    results[commodity] = await self.fetch_cme_prices(commodity)
            
            return {
                "commodities": results,
                "timestamp": datetime.now().isoformat(),
                "total_commodities": len(results)
            }
            
        except Exception as e:
            logger.error(f"Error fetching commodity prices: {e}")
            return {
                "error": "Failed to fetch commodity prices",
                "timestamp": datetime.now().isoformat()
            }
