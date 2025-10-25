"""
Advanced Trading Engine for Enterprise ETRM/CTRM
Implements real-time trading, order management, and execution
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from pydantic import BaseModel, Field
import asyncio
import json
import uuid
from decimal import Decimal
import numpy as np
from dataclasses import dataclass

# Trading Enums
class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    ICEBERG = "iceberg"
    TWAP = "twap"
    VWAP = "vwap"

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"

class TradeStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SETTLED = "settled"
    FAILED = "failed"

class AssetType(Enum):
    ELECTRICITY = "electricity"
    NATURAL_GAS = "natural_gas"
    OIL = "oil"
    COAL = "coal"
    RENEWABLE_CREDITS = "renewable_credits"
    CARBON_CREDITS = "carbon_credits"
    WEATHER_DERIVATIVES = "weather_derivatives"

# Pydantic Models
class Asset(BaseModel):
    symbol: str
    name: str
    asset_type: AssetType
    exchange: str
    currency: str
    tick_size: float
    lot_size: int
    is_active: bool = True

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    asset_symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: Decimal
    price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    time_in_force: str = "GTC"  # Good Till Cancelled
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: Decimal = Decimal('0')
    average_price: Optional[Decimal] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    parent_order_id: Optional[str] = None
    strategy_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Trade(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order_id: str
    asset_symbol: str
    side: OrderSide
    quantity: Decimal
    price: Decimal
    status: TradeStatus = TradeStatus.PENDING
    counterparty: Optional[str] = None
    venue: str
    execution_time: datetime = Field(default_factory=datetime.now)
    settlement_date: Optional[datetime] = None
    commission: Decimal = Decimal('0')
    fees: Decimal = Decimal('0')
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Position(BaseModel):
    asset_symbol: str
    quantity: Decimal
    average_price: Decimal
    unrealized_pnl: Decimal
    realized_pnl: Decimal
    market_value: Decimal
    last_updated: datetime = Field(default_factory=datetime.now)

class Portfolio(BaseModel):
    user_id: str
    positions: Dict[str, Position] = Field(default_factory=dict)
    total_value: Decimal = Decimal('0')
    total_pnl: Decimal = Decimal('0')
    last_updated: datetime = Field(default_factory=datetime.now)

class MarketData(BaseModel):
    symbol: str
    bid_price: Decimal
    ask_price: Decimal
    last_price: Decimal
    volume: int
    timestamp: datetime = Field(default_factory=datetime.now)

class TradingStrategy(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)

# Advanced Trading Engine
class AdvancedTradingEngine:
    def __init__(self):
        self.orders: Dict[str, Order] = {}
        self.trades: Dict[str, Trade] = {}
        self.positions: Dict[str, Dict[str, Position]] = {}  # user_id -> asset -> position
        self.market_data: Dict[str, MarketData] = {}
        self.strategies: Dict[str, TradingStrategy] = {}
        self.order_book: Dict[str, List[Order]] = {}  # asset -> orders
        self.running = False
        
    async def start(self):
        """Start the trading engine"""
        self.running = True
        # Start background tasks
        asyncio.create_task(self._market_data_updater())
        asyncio.create_task(self._order_processor())
        asyncio.create_task(self._position_updater())
        
    async def stop(self):
        """Stop the trading engine"""
        self.running = False
        
    async def _market_data_updater(self):
        """Update market data in real-time"""
        while self.running:
            try:
                # Simulate market data updates
                for symbol in ["ELEC_SPOT", "NG_HENRY", "BRENT_CRUDE", "COAL_API2"]:
                    self.market_data[symbol] = MarketData(
                        symbol=symbol,
                        bid_price=Decimal(str(np.random.uniform(50, 150))),
                        ask_price=Decimal(str(np.random.uniform(50, 150))),
                        last_price=Decimal(str(np.random.uniform(50, 150))),
                        volume=np.random.randint(1000, 10000)
                    )
                await asyncio.sleep(1)  # Update every second
            except Exception as e:
                print(f"Market data update error: {e}")
                await asyncio.sleep(5)
    
    async def _order_processor(self):
        """Process orders in the order book"""
        while self.running:
            try:
                for asset, orders in self.order_book.items():
                    for order in orders[:]:  # Copy to avoid modification during iteration
                        if order.status == OrderStatus.PENDING:
                            await self._process_order(order)
                await asyncio.sleep(0.1)  # Process every 100ms
            except Exception as e:
                print(f"Order processing error: {e}")
                await asyncio.sleep(1)
    
    async def _position_updater(self):
        """Update positions based on trades"""
        while self.running:
            try:
                for user_id, user_positions in self.positions.items():
                    for asset, position in user_positions.items():
                        # Update position based on latest market data
                        if asset in self.market_data:
                            market_price = self.market_data[asset].last_price
                            position.market_value = position.quantity * market_price
                            position.unrealized_pnl = position.quantity * (market_price - position.average_price)
                            position.last_updated = datetime.now()
                await asyncio.sleep(5)  # Update every 5 seconds
            except Exception as e:
                print(f"Position update error: {e}")
                await asyncio.sleep(10)
    
    async def _process_order(self, order: Order):
        """Process a single order"""
        try:
            # Check if order is valid
            if not self._validate_order(order):
                order.status = OrderStatus.REJECTED
                return
            
            # Check market data availability
            if order.asset_symbol not in self.market_data:
                order.status = OrderStatus.REJECTED
                return
            
            market_data = self.market_data[order.asset_symbol]
            
            # Process based on order type
            if order.order_type == OrderType.MARKET:
                await self._execute_market_order(order, market_data)
            elif order.order_type == OrderType.LIMIT:
                await self._execute_limit_order(order, market_data)
            elif order.order_type == OrderType.STOP:
                await self._execute_stop_order(order, market_data)
            else:
                # Add to order book for other order types
                order.status = OrderStatus.SUBMITTED
                if order.asset_symbol not in self.order_book:
                    self.order_book[order.asset_symbol] = []
                self.order_book[order.asset_symbol].append(order)
                
        except Exception as e:
            print(f"Order processing error: {e}")
            order.status = OrderStatus.REJECTED
    
    def _validate_order(self, order: Order) -> bool:
        """Validate order parameters"""
        if order.quantity <= 0:
            return False
        if order.order_type in [OrderType.LIMIT, OrderType.STOP_LIMIT] and not order.price:
            return False
        if order.order_type in [OrderType.STOP, OrderType.STOP_LIMIT] and not order.stop_price:
            return False
        return True
    
    async def _execute_market_order(self, order: Order, market_data: MarketData):
        """Execute market order immediately"""
        execution_price = market_data.ask_price if order.side == OrderSide.BUY else market_data.bid_price
        
        # Create trade
        trade = Trade(
            order_id=order.id,
            asset_symbol=order.asset_symbol,
            side=order.side,
            quantity=order.quantity,
            price=execution_price,
            status=TradeStatus.CONFIRMED,
            venue="INTERNAL",
            execution_time=datetime.now()
        )
        
        self.trades[trade.id] = trade
        
        # Update order
        order.status = OrderStatus.FILLED
        order.filled_quantity = order.quantity
        order.average_price = execution_price
        order.updated_at = datetime.now()
        
        # Update position
        await self._update_position(order.user_id, order.asset_symbol, order.side, order.quantity, execution_price)
    
    async def _execute_limit_order(self, order: Order, market_data: MarketData):
        """Execute limit order if price is favorable"""
        if order.side == OrderSide.BUY and order.price >= market_data.ask_price:
            await self._execute_market_order(order, market_data)
        elif order.side == OrderSide.SELL and order.price <= market_data.bid_price:
            await self._execute_market_order(order, market_data)
        else:
            # Add to order book
            order.status = OrderStatus.SUBMITTED
            if order.asset_symbol not in self.order_book:
                self.order_book[order.asset_symbol] = []
            self.order_book[order.asset_symbol].append(order)
    
    async def _execute_stop_order(self, order: Order, market_data: MarketData):
        """Execute stop order if stop price is hit"""
        if order.side == OrderSide.BUY and market_data.last_price >= order.stop_price:
            await self._execute_market_order(order, market_data)
        elif order.side == OrderSide.SELL and market_data.last_price <= order.stop_price:
            await self._execute_market_order(order, market_data)
        else:
            # Keep in order book
            order.status = OrderStatus.SUBMITTED
            if order.asset_symbol not in self.order_book:
                self.order_book[order.asset_symbol] = []
            self.order_book[order.asset_symbol].append(order)
    
    async def _update_position(self, user_id: str, asset_symbol: str, side: OrderSide, quantity: Decimal, price: Decimal):
        """Update user position after trade"""
        if user_id not in self.positions:
            self.positions[user_id] = {}
        
        if asset_symbol not in self.positions[user_id]:
            self.positions[user_id][asset_symbol] = Position(
                asset_symbol=asset_symbol,
                quantity=Decimal('0'),
                average_price=Decimal('0'),
                unrealized_pnl=Decimal('0'),
                realized_pnl=Decimal('0'),
                market_value=Decimal('0')
            )
        
        position = self.positions[user_id][asset_symbol]
        
        if side == OrderSide.BUY:
            # Add to position
            total_quantity = position.quantity + quantity
            total_value = (position.quantity * position.average_price) + (quantity * price)
            position.average_price = total_value / total_quantity if total_quantity > 0 else Decimal('0')
            position.quantity = total_quantity
        else:
            # Reduce position
            position.quantity -= quantity
            if position.quantity < 0:
                # Short position
                position.quantity = abs(position.quantity)
                position.average_price = price
        
        position.last_updated = datetime.now()
    
    # Public API methods
    async def create_order(self, order: Order) -> Order:
        """Create a new order"""
        self.orders[order.id] = order
        
        # Add to order book for processing
        if order.asset_symbol not in self.order_book:
            self.order_book[order.asset_symbol] = []
        self.order_book[order.asset_symbol].append(order)
        
        return order
    
    async def cancel_order(self, order_id: str, user_id: str) -> bool:
        """Cancel an order"""
        if order_id not in self.orders:
            return False
        
        order = self.orders[order_id]
        if order.user_id != user_id:
            return False
        
        if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED]:
            return False
        
        order.status = OrderStatus.CANCELLED
        order.updated_at = datetime.now()
        
        # Remove from order book
        if order.asset_symbol in self.order_book:
            self.order_book[order.asset_symbol] = [
                o for o in self.order_book[order.asset_symbol] if o.id != order_id
            ]
        
        return True
    
    async def get_orders(self, user_id: str, status: Optional[OrderStatus] = None) -> List[Order]:
        """Get user orders"""
        orders = [order for order in self.orders.values() if order.user_id == user_id]
        if status:
            orders = [order for order in orders if order.status == status]
        return sorted(orders, key=lambda x: x.created_at, reverse=True)
    
    async def get_trades(self, user_id: str) -> List[Trade]:
        """Get user trades"""
        user_orders = [order.id for order in self.orders.values() if order.user_id == user_id]
        trades = [trade for trade in self.trades.values() if trade.order_id in user_orders]
        return sorted(trades, key=lambda x: x.execution_time, reverse=True)
    
    async def get_positions(self, user_id: str) -> Dict[str, Position]:
        """Get user positions"""
        return self.positions.get(user_id, {})
    
    async def get_market_data(self, symbol: str) -> Optional[MarketData]:
        """Get market data for symbol"""
        return self.market_data.get(symbol)
    
    async def get_all_market_data(self) -> Dict[str, MarketData]:
        """Get all market data"""
        return self.market_data
    
    async def create_strategy(self, strategy: TradingStrategy) -> TradingStrategy:
        """Create a trading strategy"""
        self.strategies[strategy.id] = strategy
        return strategy
    
    async def get_strategies(self, user_id: str) -> List[TradingStrategy]:
        """Get user strategies"""
        return [strategy for strategy in self.strategies.values() if strategy.is_active]

# Global trading engine instance
trading_engine = AdvancedTradingEngine()
