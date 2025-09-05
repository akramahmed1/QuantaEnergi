"""
Market Data Integration Service
ETRM/CTRM Real-time Market Feeds, Price Discovery, Market Depth
"""

from fastapi import HTTPException
from typing import Dict, List, Optional, Any
import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib
import random

logger = logging.getLogger(__name__)

class MarketFeed(Enum):
    """Market feed enumeration"""
    BLOOMBERG = "bloomberg"
    REUTERS = "reuters"
    ICE = "ice"
    CME = "cme"
    EEX = "eex"
    REGIONAL = "regional"

class CommodityType(Enum):
    """Commodity type enumeration"""
    CRUDE_OIL = "crude_oil"
    NATURAL_GAS = "natural_gas"
    ELECTRICITY = "electricity"
    CARBON_CREDIT = "carbon_credit"
    COAL = "coal"
    RENEWABLE_ENERGY = "renewable_energy"

class MarketDataObserver:
    """Observer pattern for real-time market data updates"""
    
    def __init__(self):
        self.subscribers = []
    
    def subscribe(self, callback):
        """Subscribe to market data updates"""
        self.subscribers.append(callback)
    
    def notify(self, market_data: Dict):
        """Notify all subscribers of market data updates"""
        for callback in self.subscribers:
            try:
                callback(market_data)
            except Exception as e:
                logger.error(f"Market data notification failed: {e}")

class MarketDataIntegration:
    """Market data integration with real-time feeds and price discovery"""
    
    def __init__(self):
        self.observer = MarketDataObserver()
        self.market_data = {}
        self.price_history = {}
        self.feed_status = {}
        self.subscriptions = {}
    
    async def fetch_real_time_feed(self, commodity: str, exchange: str, feed_type: str = "bloomberg") -> Dict:
        """Fetch real-time market data from specified feed"""
        try:
            # Validate commodity and exchange
            if not commodity or not exchange:
                raise ValueError("Commodity and exchange are required")
            
            # Simulate real-time data fetch (integrate with actual APIs in production)
            base_price = self._get_base_price(commodity)
            price_variation = random.uniform(-0.02, 0.02)  # ±2% variation
            current_price = base_price * (1 + price_variation)
            
            # Generate market depth data
            market_depth = self._generate_market_depth(current_price)
            
            # Create market data record
            market_data = {
                "commodity": commodity,
                "exchange": exchange,
                "feed_type": feed_type,
                "price": round(current_price, 2),
                "currency": "USD",
                "market_depth": market_depth,
                "volume": random.randint(1000, 10000),
                "timestamp": datetime.utcnow().isoformat(),
                "bid_ask_spread": round(market_depth["asks"][0]["price"] - market_depth["bids"][0]["price"], 2),
                "last_trade_time": datetime.utcnow().isoformat(),
                "change_percent": round(price_variation * 100, 2),
                "high_24h": round(current_price * 1.05, 2),
                "low_24h": round(current_price * 0.95, 2)
            }
            
            # Store market data
            key = f"{commodity}_{exchange}_{feed_type}"
            self.market_data[key] = market_data
            
            # Update price history
            if commodity not in self.price_history:
                self.price_history[commodity] = []
            self.price_history[commodity].append({
                "price": current_price,
                "timestamp": datetime.utcnow().isoformat(),
                "exchange": exchange
            })
            
            # Keep only last 1000 price points
            if len(self.price_history[commodity]) > 1000:
                self.price_history[commodity] = self.price_history[commodity][-1000:]
            
            # Notify subscribers
            self.observer.notify(market_data)
            
            # Update feed status
            self.feed_status[key] = {
                "status": "active",
                "last_update": datetime.utcnow().isoformat(),
                "latency_ms": random.randint(10, 50)
            }
            
            logger.info(f"Real-time feed fetched for {commodity} on {exchange}")
            return market_data
            
        except ValueError as e:
            logger.error(f"Market data validation error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Real-time feed fetch failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Real-time feed fetch failed: {str(e)}")
    
    def _get_base_price(self, commodity: str) -> float:
        """Get base price for commodity"""
        base_prices = {
            "crude_oil": 85.0,
            "natural_gas": 3.5,
            "electricity": 0.08,
            "carbon_credit": 25.0,
            "coal": 120.0,
            "renewable_energy": 0.12
        }
        return base_prices.get(commodity, 50.0)
    
    def _generate_market_depth(self, current_price: float) -> Dict:
        """Generate market depth data"""
        spread = current_price * 0.001  # 0.1% spread
        bid_price = current_price - spread/2
        ask_price = current_price + spread/2
        
        # Generate bid levels
        bids = []
        for i in range(5):
            price = bid_price - (i * spread * 0.5)
            volume = random.randint(100, 1000)
            bids.append({"price": round(price, 2), "volume": volume})
        
        # Generate ask levels
        asks = []
        for i in range(5):
            price = ask_price + (i * spread * 0.5)
            volume = random.randint(100, 1000)
            asks.append({"price": round(price, 2), "volume": volume})
        
        return {
            "bids": bids,
            "asks": asks,
            "best_bid": round(bid_price, 2),
            "best_ask": round(ask_price, 2)
        }
    
    async def discover_price(self, commodity: str, discovery_method: str = "weighted_average") -> Dict:
        """Discover price using various methods"""
        try:
            if commodity not in self.price_history:
                raise ValueError(f"No price history available for {commodity}")
            
            recent_prices = self.price_history[commodity][-100:]  # Last 100 prices
            
            if not recent_prices:
                raise ValueError(f"Insufficient price data for {commodity}")
            
            if discovery_method == "weighted_average":
                # Weighted average with more recent prices having higher weight
                total_weight = 0
                weighted_sum = 0
                
                for i, price_point in enumerate(recent_prices):
                    weight = i + 1  # More recent = higher weight
                    weighted_sum += price_point["price"] * weight
                    total_weight += weight
                
                discovered_price = weighted_sum / total_weight
                
            elif discovery_method == "median":
                prices = [p["price"] for p in recent_prices]
                prices.sort()
                discovered_price = prices[len(prices) // 2]
                
            elif discovery_method == "volume_weighted":
                # Simulate volume-weighted average
                total_volume = 0
                volume_weighted_sum = 0
                
                for price_point in recent_prices:
                    volume = random.randint(100, 1000)  # Simulate volume
                    volume_weighted_sum += price_point["price"] * volume
                    total_volume += volume
                
                discovered_price = volume_weighted_sum / total_volume
                
            else:
                raise ValueError(f"Unsupported discovery method: {discovery_method}")
            
            price_discovery = {
                "commodity": commodity,
                "discovered_price": round(discovered_price, 2),
                "discovery_method": discovery_method,
                "data_points": len(recent_prices),
                "price_range": {
                    "min": round(min(p["price"] for p in recent_prices), 2),
                    "max": round(max(p["price"] for p in recent_prices), 2)
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Price discovery completed for {commodity} using {discovery_method}")
            return price_discovery
            
        except ValueError as e:
            logger.error(f"Price discovery validation error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Price discovery failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Price discovery failed: {str(e)}")
    
    async def get_market_depth(self, commodity: str, exchange: str) -> Dict:
        """Get market depth for commodity and exchange"""
        try:
            key = f"{commodity}_{exchange}_bloomberg"  # Default to Bloomberg
            
            if key not in self.market_data:
                # Fetch fresh data if not available
                await self.fetch_real_time_feed(commodity, exchange)
            
            market_data = self.market_data[key]
            
            depth_analysis = {
                "commodity": commodity,
                "exchange": exchange,
                "market_depth": market_data["market_depth"],
                "bid_ask_spread": market_data["bid_ask_spread"],
                "total_bid_volume": sum(level["volume"] for level in market_data["market_depth"]["bids"]),
                "total_ask_volume": sum(level["volume"] for level in market_data["market_depth"]["asks"]),
                "volume_imbalance": self._calculate_volume_imbalance(market_data["market_depth"]),
                "timestamp": market_data["timestamp"]
            }
            
            logger.info(f"Market depth retrieved for {commodity} on {exchange}")
            return depth_analysis
            
        except Exception as e:
            logger.error(f"Market depth retrieval failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Market depth retrieval failed: {str(e)}")
    
    def _calculate_volume_imbalance(self, market_depth: Dict) -> float:
        """Calculate volume imbalance between bids and asks"""
        total_bid_volume = sum(level["volume"] for level in market_depth["bids"])
        total_ask_volume = sum(level["volume"] for level in market_depth["asks"])
        
        if total_bid_volume + total_ask_volume == 0:
            return 0.0
        
        return (total_bid_volume - total_ask_volume) / (total_bid_volume + total_ask_volume)
    
    async def subscribe_to_feed(self, commodity: str, exchange: str, callback) -> str:
        """Subscribe to real-time market data feed"""
        try:
            subscription_id = str(hash(f"{commodity}_{exchange}_{datetime.utcnow()}"))
            
            self.subscriptions[subscription_id] = {
                "commodity": commodity,
                "exchange": exchange,
                "callback": callback,
                "created_at": datetime.utcnow().isoformat(),
                "active": True
            }
            
            # Subscribe to observer
            self.observer.subscribe(callback)
            
            logger.info(f"Subscription {subscription_id} created for {commodity} on {exchange}")
            return subscription_id
            
        except Exception as e:
            logger.error(f"Feed subscription failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Feed subscription failed: {str(e)}")
    
    async def get_market_analytics(self, commodity: str) -> Dict:
        """Get market analytics for commodity"""
        try:
            if commodity not in self.price_history:
                raise ValueError(f"No price history available for {commodity}")
            
            prices = [p["price"] for p in self.price_history[commodity]]
            
            if len(prices) < 2:
                raise ValueError(f"Insufficient price data for analytics")
            
            # Calculate analytics
            current_price = prices[-1]
            price_change = current_price - prices[0]
            price_change_percent = (price_change / prices[0]) * 100
            
            # Calculate volatility (standard deviation)
            mean_price = sum(prices) / len(prices)
            variance = sum((p - mean_price) ** 2 for p in prices) / len(prices)
            volatility = variance ** 0.5
            
            # Calculate moving averages
            ma_20 = sum(prices[-20:]) / min(20, len(prices)) if len(prices) >= 20 else mean_price
            ma_50 = sum(prices[-50:]) / min(50, len(prices)) if len(prices) >= 50 else mean_price
            
            analytics = {
                "commodity": commodity,
                "current_price": round(current_price, 2),
                "price_change": round(price_change, 2),
                "price_change_percent": round(price_change_percent, 2),
                "volatility": round(volatility, 4),
                "moving_average_20": round(ma_20, 2),
                "moving_average_50": round(ma_50, 2),
                "data_points": len(prices),
                "price_range": {
                    "min": round(min(prices), 2),
                    "max": round(max(prices), 2)
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Market analytics generated for {commodity}")
            return analytics
            
        except ValueError as e:
            logger.error(f"Market analytics validation error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Market analytics generation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Market analytics generation failed: {str(e)}")
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            logger.info("Market data integration cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")
