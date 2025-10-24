"""
Enterprise Exchange Connectors for QuantaEnergi ETRM/CTRM Platform
Implements comprehensive market data connectors for major exchanges and clearing houses
"""

import asyncio
import aiohttp
import websockets
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
import ssl
import certifi
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
import threading
import time

logger = logging.getLogger(__name__)

class ExchangeType(Enum):
    """Exchange types"""
    ENERGY = "energy"
    COMMODITY = "commodity"
    FINANCIAL = "financial"
    CRYPTO = "crypto"
    DERIVATIVES = "derivatives"

class DataFormat(Enum):
    """Data format standards"""
    FIX = "fix"
    FIXML = "fixml"
    JSON = "json"
    XML = "xml"
    CSV = "csv"
    BINARY = "binary"

@dataclass
class ExchangeConfig:
    """Exchange configuration"""
    name: str
    exchange_type: ExchangeType
    base_url: str
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    websocket_url: Optional[str] = None
    data_format: DataFormat = DataFormat.JSON
    rate_limit: int = 1000  # requests per minute
    timeout: int = 30
    ssl_verify: bool = True
    custom_headers: Dict[str, str] = field(default_factory=dict)
    supported_instruments: List[str] = field(default_factory=list)
    trading_hours: Dict[str, str] = field(default_factory=dict)

@dataclass
class MarketDataMessage:
    """Standardized market data message"""
    symbol: str
    exchange: str
    price: float
    volume: float
    timestamp: datetime
    bid: Optional[float] = None
    ask: Optional[float] = None
    bid_size: Optional[float] = None
    ask_size: Optional[float] = None
    message_type: str = "tick"
    metadata: Dict[str, Any] = field(default_factory=dict)

class ExchangeConnector(ABC):
    """Abstract base class for exchange connectors"""
    
    def __init__(self, config: ExchangeConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.is_connected = False
        self.subscriptions: Dict[str, Callable] = {}
        self.rate_limiter = RateLimiter(config.rate_limit)
        
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to exchange"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from exchange"""
        pass
    
    @abstractmethod
    async def subscribe_to_market_data(self, symbols: List[str], callback: Callable) -> bool:
        """Subscribe to market data for symbols"""
        pass
    
    @abstractmethod
    async def get_historical_data(self, symbol: str, start_date: datetime, end_date: datetime) -> List[MarketDataMessage]:
        """Get historical market data"""
        pass
    
    @abstractmethod
    async def get_order_book(self, symbol: str) -> Dict[str, Any]:
        """Get current order book"""
        pass

class RateLimiter:
    """Rate limiter for API calls"""
    
    def __init__(self, max_requests: int, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
        self.lock = threading.Lock()
    
    async def acquire(self):
        """Acquire rate limit permission"""
        with self.lock:
            now = time.time()
            # Remove old requests outside time window
            self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]
            
            if len(self.requests) >= self.max_requests:
                sleep_time = self.time_window - (now - self.requests[0])
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
            
            self.requests.append(now)

class ICEConnector(ExchangeConnector):
    """ICE (Intercontinental Exchange) connector for energy commodities"""
    
    def __init__(self, config: ExchangeConfig):
        super().__init__(config)
        self.fix_session = None
        
    async def connect(self) -> bool:
        """Connect to ICE using FIX protocol"""
        try:
            # Initialize FIX session for ICE
            self.fix_session = await self._initialize_fix_session()
            self.is_connected = True
            logger.info(f"Connected to ICE exchange: {self.config.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to ICE: {e}")
            return False
    
    async def _initialize_fix_session(self):
        """Initialize FIX session for ICE"""
        # This would implement actual FIX session initialization
        # For demo purposes, return mock session
        return {"session_id": "ICE_FIX_SESSION", "status": "connected"}
    
    async def disconnect(self) -> bool:
        """Disconnect from ICE"""
        try:
            if self.fix_session:
                # Close FIX session
                self.fix_session = None
            self.is_connected = False
            logger.info("Disconnected from ICE")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from ICE: {e}")
            return False
    
    async def subscribe_to_market_data(self, symbols: List[str], callback: Callable) -> bool:
        """Subscribe to ICE market data"""
        try:
            for symbol in symbols:
                # Subscribe to ICE market data feed
                subscription_id = f"ICE_{symbol}_{int(time.time())}"
                self.subscriptions[subscription_id] = callback
                
                # Start data collection for symbol
                asyncio.create_task(self._collect_ice_data(symbol, callback))
            
            return True
        except Exception as e:
            logger.error(f"Failed to subscribe to ICE data: {e}")
            return False
    
    async def _collect_ice_data(self, symbol: str, callback: Callable):
        """Collect data from ICE for symbol"""
        while symbol in [sub.split('_')[1] for sub in self.subscriptions.keys()]:
            try:
                # Simulate ICE data collection
                data = await self._fetch_ice_tick_data(symbol)
                if data:
                    await callback(data)
                await asyncio.sleep(1)  # 1 second update frequency
            except Exception as e:
                logger.error(f"Error collecting ICE data for {symbol}: {e}")
                await asyncio.sleep(5)
    
    async def _fetch_ice_tick_data(self, symbol: str) -> Optional[MarketDataMessage]:
        """Fetch tick data from ICE"""
        try:
            # Simulate ICE tick data
            base_prices = {
                "BRENT": 75.0,
                "WTI": 70.0,
                "NATGAS": 3.2,
                "COAL": 150.0
            }
            
            base_price = base_prices.get(symbol, 75.0)
            price_change = np.random.normal(0, 0.01)  # 1% volatility
            current_price = base_price * (1 + price_change)
            
            return MarketDataMessage(
                symbol=symbol,
                exchange="ICE",
                price=round(current_price, 2),
                volume=np.random.uniform(1000, 10000),
                timestamp=datetime.utcnow(),
                bid=current_price - 0.01,
                ask=current_price + 0.01,
                bid_size=np.random.uniform(100, 500),
                ask_size=np.random.uniform(100, 500),
                message_type="tick",
                metadata={"source": "ICE", "feed": "real_time"}
            )
        except Exception as e:
            logger.error(f"Error fetching ICE tick data: {e}")
            return None
    
    async def get_historical_data(self, symbol: str, start_date: datetime, end_date: datetime) -> List[MarketDataMessage]:
        """Get historical data from ICE"""
        try:
            # Simulate historical data
            data_points = []
            current_date = start_date
            
            while current_date <= end_date:
                base_prices = {"BRENT": 75.0, "WTI": 70.0, "NATGAS": 3.2, "COAL": 150.0}
                base_price = base_prices.get(symbol, 75.0)
                price_change = np.random.normal(0, 0.02)
                price = base_price * (1 + price_change)
                
                data_points.append(MarketDataMessage(
                    symbol=symbol,
                    exchange="ICE",
                    price=round(price, 2),
                    volume=np.random.uniform(1000, 10000),
                    timestamp=current_date,
                    message_type="historical"
                ))
                
                current_date += timedelta(days=1)
            
            return data_points
        except Exception as e:
            logger.error(f"Error getting ICE historical data: {e}")
            return []
    
    async def get_order_book(self, symbol: str) -> Dict[str, Any]:
        """Get ICE order book"""
        try:
            # Simulate ICE order book
            base_prices = {"BRENT": 75.0, "WTI": 70.0, "NATGAS": 3.2, "COAL": 150.0}
            base_price = base_prices.get(symbol, 75.0)
            
            bids = [(base_price - i * 0.01, np.random.uniform(100, 1000)) for i in range(1, 11)]
            asks = [(base_price + i * 0.01, np.random.uniform(100, 1000)) for i in range(1, 11)]
            
            return {
                "symbol": symbol,
                "exchange": "ICE",
                "bids": bids,
                "asks": asks,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting ICE order book: {e}")
            return {}

class CMEConnector(ExchangeConnector):
    """CME (Chicago Mercantile Exchange) connector for energy futures"""
    
    async def connect(self) -> bool:
        """Connect to CME"""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout),
                connector=aiohttp.TCPConnector(ssl=self.config.ssl_verify)
            )
            self.is_connected = True
            logger.info(f"Connected to CME exchange: {self.config.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to CME: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from CME"""
        try:
            if self.session:
                await self.session.close()
            self.is_connected = False
            logger.info("Disconnected from CME")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from CME: {e}")
            return False
    
    async def subscribe_to_market_data(self, symbols: List[str], callback: Callable) -> bool:
        """Subscribe to CME market data"""
        try:
            for symbol in symbols:
                subscription_id = f"CME_{symbol}_{int(time.time())}"
                self.subscriptions[subscription_id] = callback
                
                # Start data collection for symbol
                asyncio.create_task(self._collect_cme_data(symbol, callback))
            
            return True
        except Exception as e:
            logger.error(f"Failed to subscribe to CME data: {e}")
            return False
    
    async def _collect_cme_data(self, symbol: str, callback: Callable):
        """Collect data from CME for symbol"""
        while symbol in [sub.split('_')[1] for sub in self.subscriptions.keys()]:
            try:
                data = await self._fetch_cme_tick_data(symbol)
                if data:
                    await callback(data)
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error collecting CME data for {symbol}: {e}")
                await asyncio.sleep(5)
    
    async def _fetch_cme_tick_data(self, symbol: str) -> Optional[MarketDataMessage]:
        """Fetch tick data from CME"""
        try:
            # Simulate CME tick data
            base_prices = {
                "CL": 70.0,  # Crude Oil
                "NG": 3.2,   # Natural Gas
                "HO": 2.5,   # Heating Oil
                "RB": 2.3    # RBOB Gasoline
            }
            
            base_price = base_prices.get(symbol, 70.0)
            price_change = np.random.normal(0, 0.015)  # 1.5% volatility
            current_price = base_price * (1 + price_change)
            
            return MarketDataMessage(
                symbol=symbol,
                exchange="CME",
                price=round(current_price, 2),
                volume=np.random.uniform(1000, 10000),
                timestamp=datetime.utcnow(),
                bid=current_price - 0.01,
                ask=current_price + 0.01,
                bid_size=np.random.uniform(100, 500),
                ask_size=np.random.uniform(100, 500),
                message_type="tick",
                metadata={"source": "CME", "feed": "real_time"}
            )
        except Exception as e:
            logger.error(f"Error fetching CME tick data: {e}")
            return None
    
    async def get_historical_data(self, symbol: str, start_date: datetime, end_date: datetime) -> List[MarketDataMessage]:
        """Get historical data from CME"""
        try:
            data_points = []
            current_date = start_date
            
            while current_date <= end_date:
                base_prices = {"CL": 70.0, "NG": 3.2, "HO": 2.5, "RB": 2.3}
                base_price = base_prices.get(symbol, 70.0)
                price_change = np.random.normal(0, 0.02)
                price = base_price * (1 + price_change)
                
                data_points.append(MarketDataMessage(
                    symbol=symbol,
                    exchange="CME",
                    price=round(price, 2),
                    volume=np.random.uniform(1000, 10000),
                    timestamp=current_date,
                    message_type="historical"
                ))
                
                current_date += timedelta(days=1)
            
            return data_points
        except Exception as e:
            logger.error(f"Error getting CME historical data: {e}")
            return []
    
    async def get_order_book(self, symbol: str) -> Dict[str, Any]:
        """Get CME order book"""
        try:
            base_prices = {"CL": 70.0, "NG": 3.2, "HO": 2.5, "RB": 2.3}
            base_price = base_prices.get(symbol, 70.0)
            
            bids = [(base_price - i * 0.01, np.random.uniform(100, 1000)) for i in range(1, 11)]
            asks = [(base_price + i * 0.01, np.random.uniform(100, 1000)) for i in range(1, 11)]
            
            return {
                "symbol": symbol,
                "exchange": "CME",
                "bids": bids,
                "asks": asks,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting CME order book: {e}")
            return {}

class NYMEXConnector(ExchangeConnector):
    """NYMEX (New York Mercantile Exchange) connector"""
    
    async def connect(self) -> bool:
        """Connect to NYMEX"""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout),
                connector=aiohttp.TCPConnector(ssl=self.config.ssl_verify)
            )
            self.is_connected = True
            logger.info(f"Connected to NYMEX exchange: {self.config.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to NYMEX: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from NYMEX"""
        try:
            if self.session:
                await self.session.close()
            self.is_connected = False
            logger.info("Disconnected from NYMEX")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from NYMEX: {e}")
            return False
    
    async def subscribe_to_market_data(self, symbols: List[str], callback: Callable) -> bool:
        """Subscribe to NYMEX market data"""
        try:
            for symbol in symbols:
                subscription_id = f"NYMEX_{symbol}_{int(time.time())}"
                self.subscriptions[subscription_id] = callback
                
                asyncio.create_task(self._collect_nymex_data(symbol, callback))
            
            return True
        except Exception as e:
            logger.error(f"Failed to subscribe to NYMEX data: {e}")
            return False
    
    async def _collect_nymex_data(self, symbol: str, callback: Callable):
        """Collect data from NYMEX for symbol"""
        while symbol in [sub.split('_')[1] for sub in self.subscriptions.keys()]:
            try:
                data = await self._fetch_nymex_tick_data(symbol)
                if data:
                    await callback(data)
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error collecting NYMEX data for {symbol}: {e}")
                await asyncio.sleep(5)
    
    async def _fetch_nymex_tick_data(self, symbol: str) -> Optional[MarketDataMessage]:
        """Fetch tick data from NYMEX"""
        try:
            base_prices = {
                "CL": 70.0,  # Crude Oil
                "NG": 3.2,   # Natural Gas
                "HO": 2.5,   # Heating Oil
                "RB": 2.3    # RBOB Gasoline
            }
            
            base_price = base_prices.get(symbol, 70.0)
            price_change = np.random.normal(0, 0.012)  # 1.2% volatility
            current_price = base_price * (1 + price_change)
            
            return MarketDataMessage(
                symbol=symbol,
                exchange="NYMEX",
                price=round(current_price, 2),
                volume=np.random.uniform(1000, 10000),
                timestamp=datetime.utcnow(),
                bid=current_price - 0.01,
                ask=current_price + 0.01,
                bid_size=np.random.uniform(100, 500),
                ask_size=np.random.uniform(100, 500),
                message_type="tick",
                metadata={"source": "NYMEX", "feed": "real_time"}
            )
        except Exception as e:
            logger.error(f"Error fetching NYMEX tick data: {e}")
            return None
    
    async def get_historical_data(self, symbol: str, start_date: datetime, end_date: datetime) -> List[MarketDataMessage]:
        """Get historical data from NYMEX"""
        try:
            data_points = []
            current_date = start_date
            
            while current_date <= end_date:
                base_prices = {"CL": 70.0, "NG": 3.2, "HO": 2.5, "RB": 2.3}
                base_price = base_prices.get(symbol, 70.0)
                price_change = np.random.normal(0, 0.02)
                price = base_price * (1 + price_change)
                
                data_points.append(MarketDataMessage(
                    symbol=symbol,
                    exchange="NYMEX",
                    price=round(price, 2),
                    volume=np.random.uniform(1000, 10000),
                    timestamp=current_date,
                    message_type="historical"
                ))
                
                current_date += timedelta(days=1)
            
            return data_points
        except Exception as e:
            logger.error(f"Error getting NYMEX historical data: {e}")
            return []
    
    async def get_order_book(self, symbol: str) -> Dict[str, Any]:
        """Get NYMEX order book"""
        try:
            base_prices = {"CL": 70.0, "NG": 3.2, "HO": 2.5, "RB": 2.3}
            base_price = base_prices.get(symbol, 70.0)
            
            bids = [(base_price - i * 0.01, np.random.uniform(100, 1000)) for i in range(1, 11)]
            asks = [(base_price + i * 0.01, np.random.uniform(100, 1000)) for i in range(1, 11)]
            
            return {
                "symbol": symbol,
                "exchange": "NYMEX",
                "bids": bids,
                "asks": asks,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting NYMEX order book: {e}")
            return {}

class ExchangeConnectorManager:
    """Manager for all exchange connectors"""
    
    def __init__(self):
        self.connectors: Dict[str, ExchangeConnector] = {}
        self.data_aggregator = MarketDataAggregator()
        self.is_running = False
        
    async def initialize_connectors(self) -> bool:
        """Initialize all exchange connectors"""
        try:
            # ICE Connector
            ice_config = ExchangeConfig(
                name="ICE",
                exchange_type=ExchangeType.ENERGY,
                base_url="https://api.theice.com",
                websocket_url="wss://api.theice.com/ws",
                data_format=DataFormat.FIX,
                rate_limit=1000,
                supported_instruments=["BRENT", "WTI", "NATGAS", "COAL"],
                trading_hours={"start": "06:00", "end": "17:00"}
            )
            self.connectors["ICE"] = ICEConnector(ice_config)
            
            # CME Connector
            cme_config = ExchangeConfig(
                name="CME",
                exchange_type=ExchangeType.ENERGY,
                base_url="https://api.cmegroup.com",
                websocket_url="wss://api.cmegroup.com/ws",
                data_format=DataFormat.JSON,
                rate_limit=1000,
                supported_instruments=["CL", "NG", "HO", "RB"],
                trading_hours={"start": "06:00", "end": "17:00"}
            )
            self.connectors["CME"] = CMEConnector(cme_config)
            
            # NYMEX Connector
            nymex_config = ExchangeConfig(
                name="NYMEX",
                exchange_type=ExchangeType.ENERGY,
                base_url="https://api.nymex.com",
                websocket_url="wss://api.nymex.com/ws",
                data_format=DataFormat.JSON,
                rate_limit=1000,
                supported_instruments=["CL", "NG", "HO", "RB"],
                trading_hours={"start": "06:00", "end": "17:00"}
            )
            self.connectors["NYMEX"] = NYMEXConnector(nymex_config)
            
            logger.info("Exchange connectors initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize exchange connectors: {e}")
            return False
    
    async def start_all_connectors(self) -> bool:
        """Start all exchange connectors"""
        try:
            for name, connector in self.connectors.items():
                success = await connector.connect()
                if not success:
                    logger.warning(f"Failed to connect to {name}")
            
            self.is_running = True
            logger.info("All exchange connectors started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start exchange connectors: {e}")
            return False
    
    async def stop_all_connectors(self) -> bool:
        """Stop all exchange connectors"""
        try:
            for name, connector in self.connectors.items():
                await connector.disconnect()
            
            self.is_running = False
            logger.info("All exchange connectors stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop exchange connectors: {e}")
            return False
    
    async def subscribe_to_symbols(self, symbols: List[str], callback: Callable) -> Dict[str, bool]:
        """Subscribe to symbols across all exchanges"""
        results = {}
        
        for exchange_name, connector in self.connectors.items():
            try:
                # Filter symbols supported by this exchange
                supported_symbols = [s for s in symbols if s in connector.config.supported_instruments]
                
                if supported_symbols:
                    success = await connector.subscribe_to_market_data(supported_symbols, callback)
                    results[exchange_name] = success
                else:
                    results[exchange_name] = False
                    
            except Exception as e:
                logger.error(f"Error subscribing to {exchange_name}: {e}")
                results[exchange_name] = False
        
        return results
    
    async def get_historical_data(self, symbol: str, start_date: datetime, end_date: datetime) -> Dict[str, List[MarketDataMessage]]:
        """Get historical data from all exchanges for symbol"""
        results = {}
        
        for exchange_name, connector in self.connectors.items():
            try:
                if symbol in connector.config.supported_instruments:
                    data = await connector.get_historical_data(symbol, start_date, end_date)
                    results[exchange_name] = data
            except Exception as e:
                logger.error(f"Error getting historical data from {exchange_name}: {e}")
                results[exchange_name] = []
        
        return results
    
    def get_connector_status(self) -> Dict[str, Any]:
        """Get status of all connectors"""
        status = {}
        
        for name, connector in self.connectors.items():
            status[name] = {
                "connected": connector.is_connected,
                "subscriptions": len(connector.subscriptions),
                "supported_instruments": connector.config.supported_instruments,
                "rate_limit": connector.config.rate_limit
            }
        
        return status

class MarketDataAggregator:
    """Aggregates market data from multiple exchanges"""
    
    def __init__(self):
        self.data_cache: Dict[str, List[MarketDataMessage]] = {}
        self.price_aggregator = PriceAggregator()
        self.volume_aggregator = VolumeAggregator()
        
    async def process_market_data(self, message: MarketDataMessage):
        """Process incoming market data message"""
        try:
            symbol = message.symbol
            
            # Add to cache
            if symbol not in self.data_cache:
                self.data_cache[symbol] = []
            
            self.data_cache[symbol].append(message)
            
            # Keep only last 1000 messages per symbol
            if len(self.data_cache[symbol]) > 1000:
                self.data_cache[symbol] = self.data_cache[symbol][-1000:]
            
            # Aggregate data
            await self.price_aggregator.aggregate_prices(symbol, message)
            await self.volume_aggregator.aggregate_volumes(symbol, message)
            
        except Exception as e:
            logger.error(f"Error processing market data: {e}")
    
    def get_aggregated_data(self, symbol: str) -> Dict[str, Any]:
        """Get aggregated data for symbol"""
        if symbol not in self.data_cache:
            return {}
        
        messages = self.data_cache[symbol]
        if not messages:
            return {}
        
        # Calculate aggregated metrics
        prices = [msg.price for msg in messages]
        volumes = [msg.volume for msg in messages]
        
        return {
            "symbol": symbol,
            "latest_price": prices[-1] if prices else 0,
            "average_price": np.mean(prices) if prices else 0,
            "price_volatility": np.std(prices) if len(prices) > 1 else 0,
            "total_volume": sum(volumes),
            "average_volume": np.mean(volumes) if volumes else 0,
            "message_count": len(messages),
            "last_update": messages[-1].timestamp.isoformat() if messages else None
        }

class PriceAggregator:
    """Aggregates price data across exchanges"""
    
    def __init__(self):
        self.price_data: Dict[str, List[float]] = {}
    
    async def aggregate_prices(self, symbol: str, message: MarketDataMessage):
        """Aggregate price data for symbol"""
        if symbol not in self.price_data:
            self.price_data[symbol] = []
        
        self.price_data[symbol].append(message.price)
        
        # Keep only last 100 prices
        if len(self.price_data[symbol]) > 100:
            self.price_data[symbol] = self.price_data[symbol][-100:]

class VolumeAggregator:
    """Aggregates volume data across exchanges"""
    
    def __init__(self):
        self.volume_data: Dict[str, List[float]] = {}
    
    async def aggregate_volumes(self, symbol: str, message: MarketDataMessage):
        """Aggregate volume data for symbol"""
        if symbol not in self.volume_data:
            self.volume_data[symbol] = []
        
        self.volume_data[symbol].append(message.volume)
        
        # Keep only last 100 volumes
        if len(self.volume_data[symbol]) > 100:
            self.volume_data[symbol] = self.volume_data[symbol][-100:]

# Global connector manager instance
connector_manager = ExchangeConnectorManager()

async def initialize_exchange_connectors() -> bool:
    """Initialize all exchange connectors"""
    return await connector_manager.initialize_connectors()

async def start_exchange_connectors() -> bool:
    """Start all exchange connectors"""
    return await connector_manager.start_all_connectors()

async def stop_exchange_connectors() -> bool:
    """Stop all exchange connectors"""
    return await connector_manager.stop_all_connectors()

async def subscribe_to_market_data(symbols: List[str], callback: Callable) -> Dict[str, bool]:
    """Subscribe to market data for symbols across all exchanges"""
    return await connector_manager.subscribe_to_symbols(symbols, callback)

async def get_historical_data(symbol: str, start_date: datetime, end_date: datetime) -> Dict[str, List[MarketDataMessage]]:
    """Get historical data for symbol from all exchanges"""
    return await connector_manager.get_historical_data(symbol, start_date, end_date)

def get_connector_status() -> Dict[str, Any]:
    """Get status of all connectors"""
    return connector_manager.get_connector_status()
