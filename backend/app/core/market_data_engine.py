"""
Advanced Market Data Engine for ETRM/CTRM Enterprise Application
Implements real-time market data processing, tick data, and market microstructure
"""
import asyncio
import websockets
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import deque
import threading
import time
from sqlalchemy.orm import Session
import redis
import pickle

logger = logging.getLogger(__name__)

class MarketDataType(Enum):
    TICK = "tick"
    OHLCV = "ohlcv"
    ORDER_BOOK = "order_book"
    TRADE = "trade"
    QUOTE = "quote"
    VOLUME = "volume"
    VOLATILITY = "volatility"

class DataSource(Enum):
    ALPHA_VANTAGE = "alpha_vantage"
    YAHOO_FINANCE = "yahoo_finance"
    BLOOMBERG = "bloomberg"
    REUTERS = "reuters"
    INTERNAL = "internal"
    SIMULATED = "simulated"

@dataclass
class MarketTick:
    """Market tick data"""
    symbol: str
    price: float
    volume: float
    timestamp: datetime
    bid: Optional[float] = None
    ask: Optional[float] = None
    bid_size: Optional[float] = None
    ask_size: Optional[float] = None
    source: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class OHLCV:
    """OHLCV bar data"""
    symbol: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float
    timestamp: datetime
    timeframe: str = "1m"
    source: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class OrderBook:
    """Order book data"""
    symbol: str
    bids: List[Tuple[float, float]]  # [(price, size), ...]
    asks: List[Tuple[float, float]]  # [(price, size), ...]
    timestamp: datetime
    source: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MarketDataSubscription:
    """Market data subscription"""
    subscription_id: str
    symbol: str
    data_type: MarketDataType
    callback: Callable
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

class MarketDataEngine:
    """Advanced market data processing engine"""
    
    def __init__(self, db: Session, redis_client: redis.Redis = None):
        self.db = db
        self.redis_client = redis_client
        self.subscriptions: Dict[str, MarketDataSubscription] = {}
        self.data_cache: Dict[str, deque] = {}
        self.running = False
        self.websocket_connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.data_sources: Dict[str, DataSource] = {}
        self.market_data_processors: Dict[MarketDataType, Callable] = {}
        self.volatility_calculators: Dict[str, Callable] = {}
        self.correlation_calculators: Dict[Tuple[str, str], Callable] = {}
        
        # Initialize data processors
        self._initialize_data_processors()
        
        # Initialize volatility calculators
        self._initialize_volatility_calculators()
        
    def _initialize_data_processors(self):
        """Initialize market data processors"""
        self.market_data_processors = {
            MarketDataType.TICK: self._process_tick_data,
            MarketDataType.OHLCV: self._process_ohlcv_data,
            MarketDataType.ORDER_BOOK: self._process_order_book_data,
            MarketDataType.TRADE: self._process_trade_data,
            MarketDataType.QUOTE: self._process_quote_data,
            MarketDataType.VOLUME: self._process_volume_data,
            MarketDataType.VOLATILITY: self._process_volatility_data
        }
    
    def _initialize_volatility_calculators(self):
        """Initialize volatility calculators"""
        self.volatility_calculators = {
            'historical': self._calculate_historical_volatility,
            'garch': self._calculate_garch_volatility,
            'ewma': self._calculate_ewma_volatility,
            'realized': self._calculate_realized_volatility
        }
    
    async def start(self):
        """Start the market data engine"""
        self.running = True
        logger.info("Market Data Engine started")
        
        # Start data collection tasks
        asyncio.create_task(self._data_collection_loop())
        asyncio.create_task(self._data_processing_loop())
        asyncio.create_task(self._volatility_calculation_loop())
        asyncio.create_task(self._correlation_calculation_loop())
    
    async def stop(self):
        """Stop the market data engine"""
        self.running = False
        logger.info("Market Data Engine stopped")
    
    def subscribe_to_market_data(self, 
                               symbol: str,
                               data_type: MarketDataType,
                               callback: Callable,
                               source: DataSource = DataSource.SIMULATED) -> str:
        """Subscribe to market data for a symbol"""
        
        subscription_id = f"{symbol}_{data_type.value}_{int(time.time())}"
        
        subscription = MarketDataSubscription(
            subscription_id=subscription_id,
            symbol=symbol,
            data_type=data_type,
            callback=callback
        )
        
        self.subscriptions[subscription_id] = subscription
        self.data_sources[symbol] = source
        
        # Initialize data cache for symbol if not exists
        if symbol not in self.data_cache:
            self.data_cache[symbol] = deque(maxlen=10000)  # Keep last 10k ticks
        
        logger.info(f"Subscribed to {data_type.value} data for {symbol}")
        return subscription_id
    
    def unsubscribe_from_market_data(self, subscription_id: str) -> bool:
        """Unsubscribe from market data"""
        if subscription_id in self.subscriptions:
            del self.subscriptions[subscription_id]
            logger.info(f"Unsubscribed from {subscription_id}")
            return True
        return False
    
    async def _data_collection_loop(self):
        """Main data collection loop"""
        while self.running:
            try:
                # Collect data from all active subscriptions
                for subscription_id, subscription in self.subscriptions.items():
                    if subscription.is_active:
                        await self._collect_data_for_subscription(subscription)
                
                await asyncio.sleep(0.1)  # 100ms update frequency
            except Exception as e:
                logger.error(f"Error in data collection loop: {e}")
                await asyncio.sleep(1)
    
    async def _collect_data_for_subscription(self, subscription: MarketDataSubscription):
        """Collect data for a specific subscription"""
        
        symbol = subscription.symbol
        data_type = subscription.data_type
        source = self.data_sources.get(symbol, DataSource.SIMULATED)
        
        try:
            if source == DataSource.SIMULATED:
                data = await self._generate_simulated_data(symbol, data_type)
            elif source == DataSource.ALPHA_VANTAGE:
                data = await self._fetch_alpha_vantage_data(symbol, data_type)
            elif source == DataSource.YAHOO_FINANCE:
                data = await self._fetch_yahoo_finance_data(symbol, data_type)
            else:
                data = await self._generate_simulated_data(symbol, data_type)
            
            if data:
                # Store in cache
                self.data_cache[symbol].append(data)
                
                # Process data
                await self._process_market_data(data, subscription)
                
                # Call callback
                if subscription.callback:
                    await subscription.callback(data)
        
        except Exception as e:
            logger.error(f"Error collecting data for {symbol}: {e}")
    
    async def _generate_simulated_data(self, symbol: str, data_type: MarketDataType) -> Any:
        """Generate simulated market data"""
        
        base_price = 100.0  # Base price for simulation
        volatility = 0.02  # 2% volatility
        
        # Generate random price movement
        price_change = np.random.normal(0, volatility)
        current_price = base_price * (1 + price_change)
        
        if data_type == MarketDataType.TICK:
            return MarketTick(
                symbol=symbol,
                price=current_price,
                volume=np.random.uniform(100, 1000),
                timestamp=datetime.utcnow(),
                bid=current_price - 0.01,
                ask=current_price + 0.01,
                bid_size=np.random.uniform(100, 500),
                ask_size=np.random.uniform(100, 500),
                source="simulated"
            )
        
        elif data_type == MarketDataType.OHLCV:
            # Generate OHLCV data for the last minute
            high = current_price * (1 + np.random.uniform(0, 0.01))
            low = current_price * (1 - np.random.uniform(0, 0.01))
            open_price = current_price * (1 + np.random.uniform(-0.005, 0.005))
            
            return OHLCV(
                symbol=symbol,
                open_price=open_price,
                high_price=high,
                low_price=low,
                close_price=current_price,
                volume=np.random.uniform(1000, 10000),
                timestamp=datetime.utcnow(),
                timeframe="1m",
                source="simulated"
            )
        
        elif data_type == MarketDataType.ORDER_BOOK:
            # Generate order book data
            bids = [(current_price - i * 0.01, np.random.uniform(100, 1000)) for i in range(1, 11)]
            asks = [(current_price + i * 0.01, np.random.uniform(100, 1000)) for i in range(1, 11)]
            
            return OrderBook(
                symbol=symbol,
                bids=bids,
                asks=asks,
                timestamp=datetime.utcnow(),
                source="simulated"
            )
        
        return None
    
    async def _fetch_alpha_vantage_data(self, symbol: str, data_type: MarketDataType) -> Any:
        """Fetch data from Alpha Vantage API"""
        # This would implement actual Alpha Vantage API calls
        # For now, return simulated data
        return await self._generate_simulated_data(symbol, data_type)
    
    async def _fetch_yahoo_finance_data(self, symbol: str, data_type: MarketDataType) -> Any:
        """Fetch data from Yahoo Finance API"""
        # This would implement actual Yahoo Finance API calls
        # For now, return simulated data
        return await self._generate_simulated_data(symbol, data_type)
    
    async def _process_market_data(self, data: Any, subscription: MarketDataSubscription):
        """Process incoming market data"""
        
        data_type = subscription.data_type
        processor = self.market_data_processors.get(data_type)
        
        if processor:
            await processor(data, subscription)
    
    async def _process_tick_data(self, tick: MarketTick, subscription: MarketDataSubscription):
        """Process tick data"""
        # Calculate tick-based metrics
        symbol = tick.symbol
        
        # Update price statistics
        if self.redis_client:
            await self._update_redis_cache(symbol, tick)
        
        # Calculate real-time volatility
        await self._calculate_real_time_volatility(symbol, tick.price)
    
    async def _process_ohlcv_data(self, ohlcv: OHLCV, subscription: MarketDataSubscription):
        """Process OHLCV data"""
        symbol = ohlcv.symbol
        
        # Calculate technical indicators
        await self._calculate_technical_indicators(symbol, ohlcv)
        
        # Update volatility calculations
        await self._update_volatility_metrics(symbol, ohlcv)
    
    async def _process_order_book_data(self, order_book: OrderBook, subscription: MarketDataSubscription):
        """Process order book data"""
        symbol = order_book.symbol
        
        # Calculate market depth metrics
        await self._calculate_market_depth_metrics(symbol, order_book)
        
        # Update liquidity metrics
        await self._update_liquidity_metrics(symbol, order_book)
    
    async def _process_trade_data(self, trade: Any, subscription: MarketDataSubscription):
        """Process trade data"""
        pass
    
    async def _process_quote_data(self, quote: Any, subscription: MarketDataSubscription):
        """Process quote data"""
        pass
    
    async def _process_volume_data(self, volume: Any, subscription: MarketDataSubscription):
        """Process volume data"""
        pass
    
    async def _process_volatility_data(self, volatility: Any, subscription: MarketDataSubscription):
        """Process volatility data"""
        pass
    
    async def _data_processing_loop(self):
        """Data processing loop for advanced analytics"""
        while self.running:
            try:
                # Process all cached data
                for symbol, data_queue in self.data_cache.items():
                    if len(data_queue) > 0:
                        await self._process_cached_data(symbol, data_queue)
                
                await asyncio.sleep(1)  # Process every second
            except Exception as e:
                logger.error(f"Error in data processing loop: {e}")
                await asyncio.sleep(1)
    
    async def _process_cached_data(self, symbol: str, data_queue: deque):
        """Process cached data for a symbol"""
        
        # Calculate moving averages
        await self._calculate_moving_averages(symbol, data_queue)
        
        # Calculate correlation with other symbols
        await self._calculate_correlations(symbol, data_queue)
        
        # Calculate market microstructure metrics
        await self._calculate_microstructure_metrics(symbol, data_queue)
    
    async def _calculate_moving_averages(self, symbol: str, data_queue: deque):
        """Calculate moving averages for a symbol"""
        
        if len(data_queue) < 20:
            return
        
        # Get recent prices
        recent_prices = [tick.price for tick in list(data_queue)[-20:]]
        
        # Calculate simple moving averages
        sma_5 = np.mean(recent_prices[-5:])
        sma_10 = np.mean(recent_prices[-10:])
        sma_20 = np.mean(recent_prices[-20:])
        
        # Calculate exponential moving averages
        ema_5 = self._calculate_ema(recent_prices, 5)
        ema_10 = self._calculate_ema(recent_prices, 10)
        ema_20 = self._calculate_ema(recent_prices, 20)
        
        # Store in cache
        if self.redis_client:
            await self._store_moving_averages(symbol, {
                'sma_5': sma_5,
                'sma_10': sma_10,
                'sma_20': sma_20,
                'ema_5': ema_5,
                'ema_10': ema_10,
                'ema_20': ema_20
            })
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """Calculate exponential moving average"""
        if len(prices) < period:
            return np.mean(prices)
        
        alpha = 2.0 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = alpha * price + (1 - alpha) * ema
        
        return ema
    
    async def _calculate_correlations(self, symbol: str, data_queue: deque):
        """Calculate correlations with other symbols"""
        
        if len(data_queue) < 50:
            return
        
        # Get recent prices
        recent_prices = [tick.price for tick in list(data_queue)[-50:]]
        
        # Calculate correlation with other symbols
        for other_symbol, other_queue in self.data_cache.items():
            if other_symbol != symbol and len(other_queue) >= 50:
                other_prices = [tick.price for tick in list(other_queue)[-50:]]
                
                if len(recent_prices) == len(other_prices):
                    correlation = np.corrcoef(recent_prices, other_prices)[0, 1]
                    
                    # Store correlation
                    if self.redis_client:
                        await self._store_correlation(symbol, other_symbol, correlation)
    
    async def _calculate_microstructure_metrics(self, symbol: str, data_queue: deque):
        """Calculate market microstructure metrics"""
        
        if len(data_queue) < 100:
            return
        
        recent_ticks = list(data_queue)[-100:]
        
        # Calculate bid-ask spread
        spreads = []
        for tick in recent_ticks:
            if tick.bid and tick.ask:
                spread = tick.ask - tick.bid
                spreads.append(spread)
        
        if spreads:
            avg_spread = np.mean(spreads)
            spread_volatility = np.std(spreads)
            
            # Store microstructure metrics
            if self.redis_client:
                await self._store_microstructure_metrics(symbol, {
                    'avg_spread': avg_spread,
                    'spread_volatility': spread_volatility,
                    'tick_count': len(recent_ticks)
                })
    
    async def _volatility_calculation_loop(self):
        """Volatility calculation loop"""
        while self.running:
            try:
                for symbol in self.data_cache.keys():
                    await self._calculate_all_volatility_metrics(symbol)
                
                await asyncio.sleep(60)  # Calculate volatility every minute
            except Exception as e:
                logger.error(f"Error in volatility calculation loop: {e}")
                await asyncio.sleep(10)
    
    async def _calculate_all_volatility_metrics(self, symbol: str):
        """Calculate all volatility metrics for a symbol"""
        
        data_queue = self.data_cache.get(symbol)
        if not data_queue or len(data_queue) < 20:
            return
        
        recent_ticks = list(data_queue)[-100:]  # Last 100 ticks
        prices = [tick.price for tick in recent_ticks]
        
        # Calculate different types of volatility
        volatility_metrics = {}
        
        for vol_type, calculator in self.volatility_calculators.items():
            try:
                volatility = calculator(prices)
                volatility_metrics[vol_type] = volatility
            except Exception as e:
                logger.error(f"Error calculating {vol_type} volatility for {symbol}: {e}")
        
        # Store volatility metrics
        if self.redis_client:
            await self._store_volatility_metrics(symbol, volatility_metrics)
    
    def _calculate_historical_volatility(self, prices: List[float]) -> float:
        """Calculate historical volatility"""
        if len(prices) < 2:
            return 0.0
        
        returns = np.diff(np.log(prices))
        return np.std(returns) * np.sqrt(252)  # Annualized
    
    def _calculate_garch_volatility(self, prices: List[float]) -> float:
        """Calculate GARCH volatility (simplified)"""
        if len(prices) < 10:
            return 0.0
        
        returns = np.diff(np.log(prices))
        
        # Simplified GARCH(1,1) model
        alpha = 0.1
        beta = 0.85
        omega = 0.0001
        
        # Initialize variance
        variance = np.var(returns)
        
        # GARCH recursion
        for i in range(1, len(returns)):
            variance = omega + alpha * returns[i-1]**2 + beta * variance
        
        return np.sqrt(variance * 252)  # Annualized
    
    def _calculate_ewma_volatility(self, prices: List[float], lambda_param: float = 0.94) -> float:
        """Calculate EWMA volatility"""
        if len(prices) < 2:
            return 0.0
        
        returns = np.diff(np.log(prices))
        
        # EWMA variance
        variance = returns[0]**2
        
        for i in range(1, len(returns)):
            variance = lambda_param * variance + (1 - lambda_param) * returns[i]**2
        
        return np.sqrt(variance * 252)  # Annualized
    
    def _calculate_realized_volatility(self, prices: List[float]) -> float:
        """Calculate realized volatility"""
        if len(prices) < 2:
            return 0.0
        
        returns = np.diff(np.log(prices))
        return np.sqrt(np.sum(returns**2) * 252)  # Annualized
    
    async def _correlation_calculation_loop(self):
        """Correlation calculation loop"""
        while self.running:
            try:
                symbols = list(self.data_cache.keys())
                
                # Calculate pairwise correlations
                for i, symbol1 in enumerate(symbols):
                    for symbol2 in symbols[i+1:]:
                        await self._calculate_pairwise_correlation(symbol1, symbol2)
                
                await asyncio.sleep(300)  # Calculate correlations every 5 minutes
            except Exception as e:
                logger.error(f"Error in correlation calculation loop: {e}")
                await asyncio.sleep(30)
    
    async def _calculate_pairwise_correlation(self, symbol1: str, symbol2: str):
        """Calculate correlation between two symbols"""
        
        data1 = self.data_cache.get(symbol1)
        data2 = self.data_cache.get(symbol2)
        
        if not data1 or not data2 or len(data1) < 50 or len(data2) < 50:
            return
        
        # Get recent prices
        prices1 = [tick.price for tick in list(data1)[-50:]]
        prices2 = [tick.price for tick in list(data2)[-50:]]
        
        if len(prices1) == len(prices2):
            correlation = np.corrcoef(prices1, prices2)[0, 1]
            
            # Store correlation
            if self.redis_client:
                await self._store_correlation(symbol1, symbol2, correlation)
    
    async def _update_redis_cache(self, symbol: str, tick: MarketTick):
        """Update Redis cache with tick data"""
        try:
            key = f"market_data:{symbol}:latest"
            data = {
                'price': tick.price,
                'volume': tick.volume,
                'timestamp': tick.timestamp.isoformat(),
                'bid': tick.bid,
                'ask': tick.ask
            }
            await self.redis_client.setex(key, 300, json.dumps(data))  # 5 minute expiry
        except Exception as e:
            logger.error(f"Error updating Redis cache for {symbol}: {e}")
    
    async def _store_moving_averages(self, symbol: str, averages: Dict[str, float]):
        """Store moving averages in Redis"""
        try:
            key = f"market_data:{symbol}:moving_averages"
            await self.redis_client.setex(key, 600, json.dumps(averages))  # 10 minute expiry
        except Exception as e:
            logger.error(f"Error storing moving averages for {symbol}: {e}")
    
    async def _store_correlation(self, symbol1: str, symbol2: str, correlation: float):
        """Store correlation in Redis"""
        try:
            key = f"market_data:correlation:{symbol1}:{symbol2}"
            await self.redis_client.setex(key, 1800, json.dumps(correlation))  # 30 minute expiry
        except Exception as e:
            logger.error(f"Error storing correlation for {symbol1}-{symbol2}: {e}")
    
    async def _store_volatility_metrics(self, symbol: str, metrics: Dict[str, float]):
        """Store volatility metrics in Redis"""
        try:
            key = f"market_data:{symbol}:volatility"
            await self.redis_client.setex(key, 1800, json.dumps(metrics))  # 30 minute expiry
        except Exception as e:
            logger.error(f"Error storing volatility metrics for {symbol}: {e}")
    
    async def _store_microstructure_metrics(self, symbol: str, metrics: Dict[str, float]):
        """Store microstructure metrics in Redis"""
        try:
            key = f"market_data:{symbol}:microstructure"
            await self.redis_client.setex(key, 600, json.dumps(metrics))  # 10 minute expiry
        except Exception as e:
            logger.error(f"Error storing microstructure metrics for {symbol}: {e}")
    
    async def get_latest_price(self, symbol: str) -> Optional[float]:
        """Get latest price for a symbol"""
        data_queue = self.data_cache.get(symbol)
        if data_queue and len(data_queue) > 0:
            return data_queue[-1].price
        return None
    
    async def get_historical_data(self, symbol: str, start_time: datetime, end_time: datetime) -> List[MarketTick]:
        """Get historical data for a symbol"""
        data_queue = self.data_cache.get(symbol)
        if not data_queue:
            return []
        
        # Filter data by time range
        filtered_data = [
            tick for tick in data_queue
            if start_time <= tick.timestamp <= end_time
        ]
        
        return filtered_data
    
    async def get_volatility(self, symbol: str, vol_type: str = 'historical') -> Optional[float]:
        """Get volatility for a symbol"""
        if self.redis_client:
            try:
                key = f"market_data:{symbol}:volatility"
                data = await self.redis_client.get(key)
                if data:
                    metrics = json.loads(data)
                    return metrics.get(vol_type)
            except Exception as e:
                logger.error(f"Error getting volatility for {symbol}: {e}")
        return None
    
    async def get_correlation(self, symbol1: str, symbol2: str) -> Optional[float]:
        """Get correlation between two symbols"""
        if self.redis_client:
            try:
                key = f"market_data:correlation:{symbol1}:{symbol2}"
                data = await self.redis_client.get(key)
                if data:
                    return json.loads(data)
            except Exception as e:
                logger.error(f"Error getting correlation for {symbol1}-{symbol2}: {e}")
        return None
    
    def get_subscription_status(self) -> Dict[str, Any]:
        """Get status of all subscriptions"""
        return {
            "total_subscriptions": len(self.subscriptions),
            "active_subscriptions": len([s for s in self.subscriptions.values() if s.is_active]),
            "data_cache_size": {symbol: len(queue) for symbol, queue in self.data_cache.items()},
            "data_sources": {symbol: source.value for symbol, source in self.data_sources.items()}
        }
