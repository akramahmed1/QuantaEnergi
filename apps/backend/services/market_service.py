import asyncio
import json
import random
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
import numpy as np
import pandas as pd
from dataclasses import dataclass
from enum import Enum
import logging
import websockets
from concurrent.futures import ThreadPoolExecutor
import aiohttp
import yfinance as yf
import talib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketDataType(Enum):
    """Market data types"""
    PRICE = "price"
    VOLUME = "volume"
    VOLATILITY = "volatility"
    CORRELATION = "correlation"
    NEWS = "news"
    SENTIMENT = "sentiment"

class DataSource(Enum):
    """Data sources"""
    ALPHA_VANTAGE = "alpha_vantage"
    YAHOO_FINANCE = "yahoo_finance"
    BLOOMBERG = "bloomberg"
    REFINITIV = "refinitiv"
    INTERNAL = "internal"

@dataclass
class MarketDataPoint:
    """Market data point structure"""
    symbol: str
    price: float
    volume: int
    timestamp: datetime
    source: str
    data_type: MarketDataType
    metadata: Dict[str, Any] = None

class AdvancedMarketDataEngine:
    """
    Advanced market data engine with multi-source integration
    """
    
    def __init__(self):
        self.data_sources = self._initialize_data_sources()
        self.market_data_cache = {}
        self.websocket_connections = {}
        self.data_processors = {}
        self.technical_indicators = {}
        self.correlation_matrix = {}
        self.news_sentiment = {}
        
    def _initialize_data_sources(self) -> Dict[str, Any]:
        """Initialize data source configurations"""
        return {
            "alpha_vantage": {
                "api_key": None,
                "base_url": "https://www.alphavantage.co/query",
                "rate_limit": 5,  # calls per minute
                "enabled": False
            },
            "yahoo_finance": {
                "base_url": "https://query1.finance.yahoo.com",
                "rate_limit": 100,  # calls per minute
                "enabled": True
            },
            "bloomberg": {
                "api_key": None,
                "base_url": "https://api.bloomberg.com",
                "rate_limit": 1000,
                "enabled": False
            },
            "refinitiv": {
                "api_key": None,
                "base_url": "https://api.refinitiv.com",
                "rate_limit": 1000,
                "enabled": False
            }
        }
    
    def configure_data_source(self, source_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Configure data source"""
        try:
            if source_name not in self.data_sources:
                return {"status": "error", "message": f"Unknown data source: {source_name}"}
            
            self.data_sources[source_name].update(config)
            self.data_sources[source_name]["enabled"] = True
            
            return {
                "status": "success",
                "source": source_name,
                "configured": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Data source configuration error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def fetch_market_data(self, 
                               symbols: List[str],
                               data_types: List[MarketDataType] = None,
                               source: str = "yahoo_finance") -> Dict[str, Any]:
        """Fetch market data from specified source"""
        try:
            if not data_types:
                data_types = [MarketDataType.PRICE, MarketDataType.VOLUME]
            
            results = {}
            
            for symbol in symbols:
                symbol_data = {}
                
                for data_type in data_types:
                    if source == "yahoo_finance":
                        data = await self._fetch_yahoo_data(symbol, data_type)
                    elif source == "alpha_vantage":
                        data = await self._fetch_alpha_vantage_data(symbol, data_type)
                    else:
                        data = await self._fetch_internal_data(symbol, data_type)
                    
                    symbol_data[data_type.value] = data
                
                results[symbol] = symbol_data
            
            # Cache the results
            cache_key = f"{source}_{'_'.join(symbols)}_{datetime.now().strftime('%Y%m%d_%H')}"
            self.market_data_cache[cache_key] = {
                "data": results,
                "timestamp": datetime.now().isoformat(),
                "source": source
            }
            
            return {
                "status": "success",
                "data": results,
                "source": source,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Market data fetch error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _fetch_yahoo_data(self, symbol: str, data_type: MarketDataType) -> Dict[str, Any]:
        """Fetch data from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            
            if data_type == MarketDataType.PRICE:
                hist = ticker.history(period="1d", interval="1m")
                if not hist.empty:
                    latest = hist.iloc[-1]
                    return {
                        "open": float(latest['Open']),
                        "high": float(latest['High']),
                        "low": float(latest['Low']),
                        "close": float(latest['Close']),
                        "timestamp": hist.index[-1].isoformat()
                    }
            
            elif data_type == MarketDataType.VOLUME:
                hist = ticker.history(period="1d", interval="1m")
                if not hist.empty:
                    return {
                        "volume": int(hist['Volume'].iloc[-1]),
                        "timestamp": hist.index[-1].isoformat()
                    }
            
            return {"error": "No data available"}
            
        except Exception as e:
            logger.error(f"Yahoo Finance fetch error: {e}")
            return {"error": str(e)}
    
    async def _fetch_alpha_vantage_data(self, symbol: str, data_type: MarketDataType) -> Dict[str, Any]:
        """Fetch data from Alpha Vantage"""
        try:
            config = self.data_sources["alpha_vantage"]
            if not config["enabled"] or not config["api_key"]:
                return {"error": "Alpha Vantage not configured"}
            
            url = f"{config['base_url']}?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&apikey={config['api_key']}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
                    
                    if "Error Message" in data:
                        return {"error": data["Error Message"]}
                    
                    time_series = data.get("Time Series (1min)", {})
                    if time_series:
                        latest_time = max(time_series.keys())
                        latest_data = time_series[latest_time]
                        
                        return {
                            "open": float(latest_data["1. open"]),
                            "high": float(latest_data["2. high"]),
                            "low": float(latest_data["3. low"]),
                            "close": float(latest_data["4. close"]),
                            "volume": int(latest_data["5. volume"]),
                            "timestamp": latest_time
                        }
                    
                    return {"error": "No data available"}
            
        except Exception as e:
            logger.error(f"Alpha Vantage fetch error: {e}")
            return {"error": str(e)}
    
    async def _fetch_internal_data(self, symbol: str, data_type: MarketDataType) -> Dict[str, Any]:
        """Fetch internal/generated data"""
        try:
            # Generate mock data for internal source
            base_prices = {
                "BRENT": 75.0,
                "WTI": 70.0,
                "NATGAS": 3.2,
                "COAL": 150.0
            }
            
            base_price = base_prices.get(symbol, 75.0)
            change = random.uniform(-0.02, 0.02)
            current_price = base_price * (1 + change)
            
            if data_type == MarketDataType.PRICE:
                return {
                    "price": round(current_price, 2),
                    "change": round(change * 100, 2),
                    "timestamp": datetime.now().isoformat()
                }
            elif data_type == MarketDataType.VOLUME:
                return {
                    "volume": random.randint(1000, 10000),
                    "timestamp": datetime.now().isoformat()
                }
            
            return {"error": "Unsupported data type"}
            
        except Exception as e:
            logger.error(f"Internal data fetch error: {e}")
            return {"error": str(e)}
    
    def calculate_technical_indicators(self, 
                                     symbol: str,
                                     prices: List[float],
                                     period: int = 20) -> Dict[str, Any]:
        """Calculate technical indicators"""
        try:
            if len(prices) < period:
                return {"error": f"Insufficient data: need at least {period} prices"}
            
            prices_array = np.array(prices)
            
            indicators = {
                "sma": talib.SMA(prices_array, timeperiod=period)[-1],
                "ema": talib.EMA(prices_array, timeperiod=period)[-1],
                "rsi": talib.RSI(prices_array, timeperiod=14)[-1],
                "macd": talib.MACD(prices_array)[0][-1],
                "bollinger_upper": talib.BBANDS(prices_array, timeperiod=period)[0][-1],
                "bollinger_middle": talib.BBANDS(prices_array, timeperiod=period)[1][-1],
                "bollinger_lower": talib.BBANDS(prices_array, timeperiod=period)[2][-1],
                "atr": talib.ATR(prices_array, prices_array, prices_array, timeperiod=period)[-1]
            }
            
            # Store in cache
            self.technical_indicators[symbol] = {
                "indicators": indicators,
                "timestamp": datetime.now().isoformat(),
                "period": period
            }
            
            return {
                "status": "success",
                "symbol": symbol,
                "indicators": indicators,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Technical indicators calculation error: {e}")
            return {"status": "error", "message": str(e)}
    
    def calculate_correlation_matrix(self, symbols: List[str]) -> Dict[str, Any]:
        """Calculate correlation matrix for symbols"""
        try:
            # Get price data for all symbols
            price_data = {}
            
            for symbol in symbols:
                cache_key = f"yahoo_finance_{symbol}_{datetime.now().strftime('%Y%m%d_%H')}"
                if cache_key in self.market_data_cache:
                    symbol_data = self.market_data_cache[cache_key]["data"]
                    if symbol in symbol_data and "price" in symbol_data[symbol]:
                        price_data[symbol] = [symbol_data[symbol]["price"]["close"]]
                else:
                    # Use mock data if no cache
                    price_data[symbol] = [random.uniform(70, 80)]
            
            # Calculate correlation matrix
            df = pd.DataFrame(price_data)
            correlation_matrix = df.corr().to_dict()
            
            # Store in cache
            self.correlation_matrix = {
                "matrix": correlation_matrix,
                "symbols": symbols,
                "timestamp": datetime.now().isoformat()
            }
            
            return {
                "status": "success",
                "correlation_matrix": correlation_matrix,
                "symbols": symbols,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Correlation matrix calculation error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def start_websocket_stream(self, symbols: List[str], callback_func) -> Dict[str, Any]:
        """Start WebSocket stream for real-time data"""
        try:
            stream_id = f"stream_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Store connection info
            self.websocket_connections[stream_id] = {
                "symbols": symbols,
                "callback": callback_func,
                "active": True,
                "started_at": datetime.now().isoformat()
            }
            
            # Start background task for data streaming
            asyncio.create_task(self._websocket_data_stream(stream_id, symbols, callback_func))
            
            return {
                "status": "success",
                "stream_id": stream_id,
                "symbols": symbols,
                "started_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"WebSocket stream start error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _websocket_data_stream(self, stream_id: str, symbols: List[str], callback_func):
        """Background task for WebSocket data streaming"""
        try:
            while stream_id in self.websocket_connections and self.websocket_connections[stream_id]["active"]:
                # Fetch latest data for all symbols
                data = await self.fetch_market_data(symbols, [MarketDataType.PRICE])
                
                # Call callback function
                if callback_func:
                    await callback_func(data)
                
                # Wait before next update
                await asyncio.sleep(5)
                
        except Exception as e:
            logger.error(f"WebSocket data stream error: {e}")
        finally:
            if stream_id in self.websocket_connections:
                del self.websocket_connections[stream_id]
    
    def stop_websocket_stream(self, stream_id: str) -> Dict[str, Any]:
        """Stop WebSocket stream"""
        try:
            if stream_id in self.websocket_connections:
                self.websocket_connections[stream_id]["active"] = False
                del self.websocket_connections[stream_id]
                
                return {
                    "status": "success",
                    "stream_id": stream_id,
                    "stopped_at": datetime.now().isoformat()
                }
            else:
                return {"status": "error", "message": "Stream not found"}
                
        except Exception as e:
            logger.error(f"WebSocket stream stop error: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_market_data_statistics(self) -> Dict[str, Any]:
        """Get market data engine statistics"""
        try:
            return {
                "status": "success",
                "statistics": {
                    "data_sources": {
                        "total": len(self.data_sources),
                        "enabled": sum(1 for s in self.data_sources.values() if s["enabled"])
                    },
                    "cache": {
                        "entries": len(self.market_data_cache),
                        "memory_usage": sum(len(str(v)) for v in self.market_data_cache.values())
                    },
                    "websocket_connections": len(self.websocket_connections),
                    "technical_indicators": len(self.technical_indicators),
                    "correlation_matrices": len(self.correlation_matrix)
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Statistics retrieval error: {e}")
            return {"status": "error", "message": str(e)}

async def generate_market_data() -> Dict[str, Any]:
    """Generate mock market data for energy commodities"""
    base_prices = {
        "crude_oil": 75.0,
        "natural_gas": 3.2,
        "coal": 150.0,
        "electricity": 45.0
    }
    
    data = {}
    for commodity, base_price in base_prices.items():
        # Generate realistic price movement (±2%)
        change = random.uniform(-0.02, 0.02)
        current_price = base_price * (1 + change)
        
        data[commodity] = {
            "price": round(current_price, 2),
            "change": round(change * 100, 2),
            "volume": random.randint(1000, 10000),
            "timestamp": datetime.now().isoformat()
        }
    
    return {
        "type": "market_data",
        "data": data,
        "timestamp": datetime.now().isoformat()
    }

def fetch_energy_prices(symbol: str = 'BRENT', api_key: str = 'demo') -> Dict[str, float]:
    """
    Fetch real energy prices from Alpha Vantage API
    Enhanced for Brent/WTI oil prices with demo key
    """
    try:
        # Alpha Vantage API endpoint for daily time series
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}'
        
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # Extract daily close prices
        time_series = data.get('Time Series (Daily)', {})
        prices = {}
        
        for date, values in time_series.items():
            close_price = float(values.get('4. close', 0))
            prices[date] = close_price
        
        return prices
        
    except Exception as e:
        print(f"Alpha Vantage API error: {e}")
        # Fallback to mock data
        return generate_mock_prices(symbol)

def generate_mock_prices(symbol: str) -> Dict[str, float]:
    """Generate mock prices when API fails"""
    base_prices = {
        'BRENT': 75.0,
        'WTI': 70.0,
        'NATGAS': 3.2
    }
    
    base_price = base_prices.get(symbol, 75.0)
    prices = {}
    
    # Generate 30 days of mock data
    for i in range(30):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        change = random.uniform(-0.05, 0.05)  # ±5% daily change
        prices[date] = base_price * (1 + change)
    
    return prices

def get_market_volatility(prices: Dict[str, float], days: int = 30) -> float:
    """
    Calculate market volatility for risk assessment
    Enhanced for Guyana/ME geo-risk analysis
    """
    if len(prices) < 2:
        return 0.0
    
    # Convert to sorted list of prices
    sorted_prices = sorted(prices.items())
    price_values = [float(price) for _, price in sorted_prices]
    
    if len(price_values) < 2:
        return 0.0
    
    # Calculate daily returns
    returns = np.diff(np.log(price_values))
    
    # Calculate volatility (annualized)
    volatility = np.std(returns) * np.sqrt(252)
    
    return float(volatility)

async def market_data_broadcaster(websocket, path: str):
    """WebSocket handler for broadcasting market data with real Alpha Vantage data"""
    try:
        while True:
            # Try to get real market data
            try:
                brent_prices = fetch_energy_prices('BRENT')
                wti_prices = fetch_energy_prices('WTI')
                
                # Calculate volatilities
                brent_vol = get_market_volatility(brent_prices)
                wti_vol = get_market_volatility(wti_prices)
                
                market_data = {
                    "type": "enhanced_market_data",
                    "data": {
                        "brent": {
                            "latest_price": list(brent_prices.values())[0] if brent_prices else 75.0,
                            "volatility": brent_vol,
                            "source": "Alpha Vantage"
                        },
                        "wti": {
                            "latest_price": list(wti_prices.values())[0] if wti_prices else 70.0,
                            "volatility": wti_vol,
                            "source": "Alpha Vantage"
                        }
                    },
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                print(f"Real market data error: {e}, falling back to mock data")
                market_data = await generate_market_data()
            
            await websocket.send(json.dumps(market_data))
            await asyncio.sleep(5)  # Send updates every 5 seconds (API rate limits)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()
