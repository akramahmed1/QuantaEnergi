"""
Real Market Data Service for ETRM/CTRM Trading
Production-ready implementation with Yahoo Finance + Redis caching
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import numpy as np

# Market data imports
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("Warning: yfinance not available, using fallback market data")

# Redis imports
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("Warning: redis not available, using in-memory cache")

logger = logging.getLogger(__name__)

class RealMarketDataService:
    """
    Production-ready market data service with real Yahoo Finance integration
    and Redis caching for ETRM/CTRM trading operations
    """
    
    def __init__(self):
        self.service_version = "1.0.0"
        self.cache_ttl = 300  # 5 minutes TTL
        self.redis_client = None
        self.memory_cache = {}  # Fallback cache
        
        # Initialize Redis connection
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.Redis(
                    host='localhost', 
                    port=6379, 
                    db=0, 
                    decode_responses=True
                )
                # Test connection
                self.redis_client.ping()
                logger.info("Redis connection established")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}. Using memory cache.")
                self.redis_client = None
        
        # Energy commodity symbols
        self.energy_symbols = {
            "CL=F": "Crude Oil WTI",
            "NG=F": "Natural Gas",
            "BZ=F": "Brent Crude Oil",
            "RB=F": "RBOB Gasoline",
            "HO=F": "Heating Oil"
        }
        
        logger.info(f"RealMarketDataService initialized - yfinance: {YFINANCE_AVAILABLE}, redis: {REDIS_AVAILABLE}")
    
    def _get_cache_key(self, symbol: str, data_type: str = "price") -> str:
        """Generate cache key for symbol and data type"""
        return f"market_data:{symbol}:{data_type}"
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get data from cache (Redis or memory)"""
        try:
            if self.redis_client:
                cached_data = self.redis_client.get(cache_key)
                if cached_data:
                    return json.loads(cached_data)
            else:
                # Memory cache fallback
                if cache_key in self.memory_cache:
                    cached_item = self.memory_cache[cache_key]
                    if datetime.now() < cached_item['expires_at']:
                        return cached_item['data']
                    else:
                        del self.memory_cache[cache_key]
        except Exception as e:
            logger.warning(f"Cache retrieval error: {e}")
        
        return None
    
    def _set_cache(self, cache_key: str, data: Dict[str, Any]) -> None:
        """Set data in cache (Redis or memory)"""
        try:
            if self.redis_client:
                self.redis_client.setex(
                    cache_key, 
                    self.cache_ttl, 
                    json.dumps(data, default=str)
                )
            else:
                # Memory cache fallback
                self.memory_cache[cache_key] = {
                    'data': data,
                    'expires_at': datetime.now() + timedelta(seconds=self.cache_ttl)
                }
        except Exception as e:
            logger.warning(f"Cache storage error: {e}")
    
    async def fetch_energy_prices(self, symbols: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Fetch real energy commodity prices with caching
        
        Args:
            symbols: List of symbols to fetch (default: CL=F, NG=F)
            
        Returns:
            Dict with price data for each symbol
        """
        if symbols is None:
            symbols = ["CL=F", "NG=F"]  # Default to Brent and Natural Gas
        
        results = {}
        
        for symbol in symbols:
            cache_key = self._get_cache_key(symbol, "price")
            
            # Check cache first
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                results[symbol] = cached_data
                logger.info(f"Retrieved {symbol} from cache")
                continue
            
            # Fetch fresh data
            try:
                if YFINANCE_AVAILABLE:
                    price_data = await self._fetch_yahoo_price(symbol)
                else:
                    price_data = self._generate_fallback_price(symbol)
                
                # Cache the result
                self._set_cache(cache_key, price_data)
                results[symbol] = price_data
                
                logger.info(f"Fetched fresh {symbol} data: ${price_data['price']:.2f}")
                
            except Exception as e:
                logger.error(f"Error fetching {symbol}: {e}")
                results[symbol] = {
                    "symbol": symbol,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        return {
            "status": "success",
            "data": results,
            "cached_count": sum(1 for r in results.values() if r.get('cached', False)),
            "fresh_count": len(results) - sum(1 for r in results.values() if r.get('cached', False)),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _fetch_yahoo_price(self, symbol: str) -> Dict[str, Any]:
        """Fetch price data from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get current info
            info = ticker.info
            
            # Get recent historical data for more accurate pricing
            hist = ticker.history(period="1d", interval="1m")
            
            # Use latest close price if available, otherwise use info
            if not hist.empty:
                current_price = float(hist['Close'].iloc[-1])
                volume = int(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns else info.get('volume', 0)
            else:
                current_price = info.get('regularMarketPrice', 0)
                volume = info.get('volume', 0)
            
            # Calculate price change
            prev_close = info.get('regularMarketPreviousClose', current_price)
            change = current_price - prev_close
            change_percent = (change / prev_close * 100) if prev_close > 0 else 0
            
            return {
                "symbol": symbol,
                "price": round(current_price, 2),
                "volume": volume,
                "change": round(change, 2),
                "change_percent": round(change_percent, 2),
                "high": info.get('dayHigh', current_price),
                "low": info.get('dayLow', current_price),
                "open": info.get('regularMarketOpen', current_price),
                "previous_close": prev_close,
                "timestamp": datetime.now().isoformat(),
                "source": "yfinance",
                "cached": False
            }
            
        except Exception as e:
            logger.error(f"Yahoo Finance fetch error for {symbol}: {e}")
            raise
    
    def _generate_fallback_price(self, symbol: str) -> Dict[str, Any]:
        """Generate fallback price data when Yahoo Finance is unavailable"""
        base_prices = {
            "CL=F": 85.0,  # WTI Crude
            "NG=F": 3.5,   # Natural Gas
            "BZ=F": 87.0,  # Brent Crude
            "RB=F": 2.8,   # Gasoline
            "HO=F": 2.9    # Heating Oil
        }
        
        base_price = base_prices.get(symbol, 50.0)
        
        # Add some realistic variation
        variation = np.random.normal(0, 0.02)  # 2% standard deviation
        current_price = base_price * (1 + variation)
        
        return {
            "symbol": symbol,
            "price": round(current_price, 2),
            "volume": np.random.randint(1000, 10000),
            "change": round(np.random.normal(0, 1), 2),
            "change_percent": round(np.random.normal(0, 1), 2),
            "high": round(current_price * 1.02, 2),
            "low": round(current_price * 0.98, 2),
            "open": round(current_price * 0.99, 2),
            "previous_close": round(current_price * 0.99, 2),
            "timestamp": datetime.now().isoformat(),
            "source": "fallback",
            "cached": False
        }
    
    async def get_portfolio_prices(self, portfolio: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get current prices for a trading portfolio
        
        Args:
            portfolio: List of portfolio positions with symbols
            
        Returns:
            Dict with portfolio pricing data
        """
        try:
            # Extract unique symbols from portfolio
            symbols = list(set([pos.get('symbol', 'CL=F') for pos in portfolio]))
            
            # Fetch prices for all symbols
            price_data = await self.fetch_energy_prices(symbols)
            
            # Calculate portfolio metrics
            total_value = 0
            total_pnl = 0
            positions = []
            
            for position in portfolio:
                symbol = position.get('symbol', 'CL=F')
                quantity = position.get('quantity', 0)
                entry_price = position.get('entry_price', 0)
                
                if symbol in price_data['data']:
                    current_price = price_data['data'][symbol]['price']
                    position_value = quantity * current_price
                    position_pnl = quantity * (current_price - entry_price)
                    
                    total_value += position_value
                    total_pnl += position_pnl
                    
                    positions.append({
                        "symbol": symbol,
                        "quantity": quantity,
                        "entry_price": entry_price,
                        "current_price": current_price,
                        "position_value": round(position_value, 2),
                        "unrealized_pnl": round(position_pnl, 2),
                        "pnl_percent": round((position_pnl / (quantity * entry_price) * 100) if entry_price > 0 else 0, 2)
                    })
            
            return {
                "status": "success",
                "portfolio_summary": {
                    "total_value": round(total_value, 2),
                    "total_pnl": round(total_pnl, 2),
                    "pnl_percent": round((total_pnl / (total_value - total_pnl) * 100) if (total_value - total_pnl) > 0 else 0, 2),
                    "position_count": len(positions)
                },
                "positions": positions,
                "price_data": price_data,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Portfolio pricing error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_historical_prices(self, symbol: str, days: int = 30) -> Dict[str, Any]:
        """
        Get historical price data for risk calculations
        
        Args:
            symbol: Symbol to fetch history for
            days: Number of days of history
            
        Returns:
            Dict with historical price data
        """
        try:
            if YFINANCE_AVAILABLE:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=f"{days}d")
                
                if hist.empty:
                    return {
                        "status": "error",
                        "error": "No historical data available",
                        "symbol": symbol
                    }
                
                # Convert to list format
                prices = []
                for date, row in hist.iterrows():
                    prices.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "open": float(row['Open']),
                        "high": float(row['High']),
                        "low": float(row['Low']),
                        "close": float(row['Close']),
                        "volume": int(row['Volume'])
                    })
                
                return {
                    "status": "success",
                    "symbol": symbol,
                    "period_days": days,
                    "prices": prices,
                    "price_count": len(prices),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # Generate fallback historical data
                return self._generate_fallback_history(symbol, days)
                
        except Exception as e:
            logger.error(f"Historical data error for {symbol}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "symbol": symbol
            }
    
    def _generate_fallback_history(self, symbol: str, days: int) -> Dict[str, Any]:
        """Generate fallback historical data"""
        base_price = 85.0 if symbol == "CL=F" else 3.5
        
        prices = []
        current_price = base_price
        
        for i in range(days):
            # Random walk with slight upward bias
            change = np.random.normal(0.001, 0.02)  # 0.1% daily return, 2% volatility
            current_price *= (1 + change)
            
            prices.append({
                "date": (datetime.now() - timedelta(days=days-i)).strftime("%Y-%m-%d"),
                "open": round(current_price * 0.99, 2),
                "high": round(current_price * 1.01, 2),
                "low": round(current_price * 0.98, 2),
                "close": round(current_price, 2),
                "volume": np.random.randint(1000, 10000)
            })
        
        return {
            "status": "success",
            "symbol": symbol,
            "period_days": days,
            "prices": prices,
            "price_count": len(prices),
            "source": "fallback",
            "timestamp": datetime.now().isoformat()
        }

# Global instance
market_data_service = RealMarketDataService()
