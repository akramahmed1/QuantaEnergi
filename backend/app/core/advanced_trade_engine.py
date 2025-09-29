"""
Advanced Trade Engine for ETRM/CTRM Enterprise Application
Implements comprehensive trading functionality including order management, execution, and settlement
"""
import asyncio
import uuid
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Tuple, Any, Union
from enum import Enum
import logging
from dataclasses import dataclass, field
from sqlalchemy.orm import Session
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import norm
import json

logger = logging.getLogger(__name__)

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    ICEBERG = "iceberg"
    TWAP = "twap"
    VWAP = "vwap"
    PEG = "peg"

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(Enum):
    NEW = "new"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"

class ExecutionAlgorithm(Enum):
    SIMPLE = "simple"
    TWAP = "twap"
    VWAP = "vwap"
    ICEBERG = "iceberg"
    PEG = "peg"
    ADAPTIVE = "adaptive"

@dataclass
class Order:
    """Order representation with full enterprise features"""
    order_id: str
    client_order_id: str
    instrument: str
    side: OrderSide
    order_type: OrderType
    quantity: Decimal
    price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    time_in_force: str = "GTC"  # GTC, IOC, FOK, DAY
    status: OrderStatus = OrderStatus.NEW
    filled_quantity: Decimal = Decimal('0')
    average_price: Optional[Decimal] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    execution_algorithm: ExecutionAlgorithm = ExecutionAlgorithm.SIMPLE
    algorithm_params: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.expires_at is None and self.time_in_force == "DAY":
            self.expires_at = datetime.utcnow().replace(hour=16, minute=0, second=0, microsecond=0)
            if self.expires_at <= datetime.utcnow():
                self.expires_at += timedelta(days=1)

@dataclass
class Execution:
    """Trade execution with detailed information"""
    execution_id: str
    order_id: str
    instrument: str
    side: OrderSide
    quantity: Decimal
    price: Decimal
    execution_time: datetime
    venue: str
    commission: Decimal = Decimal('0')
    fees: Dict[str, Decimal] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Position:
    """Position with real-time P&L and risk metrics"""
    instrument: str
    quantity: Decimal
    average_price: Decimal
    current_price: Decimal
    unrealized_pnl: Decimal
    realized_pnl: Decimal = Decimal('0')
    market_value: Decimal = Decimal('0')
    cost_basis: Decimal = Decimal('0')
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def update_price(self, new_price: Decimal):
        """Update position with new market price"""
        self.current_price = new_price
        self.market_value = self.quantity * new_price
        self.unrealized_pnl = self.quantity * (new_price - self.average_price)
        self.last_updated = datetime.utcnow()

class AdvancedTradeEngine:
    """Enterprise-grade trade engine with advanced order management"""
    
    def __init__(self, db: Session, risk_engine=None, market_data_engine=None):
        self.db = db
        self.risk_engine = risk_engine
        self.market_data_engine = market_data_engine
        self.orders: Dict[str, Order] = {}
        self.executions: List[Execution] = []
        self.positions: Dict[str, Position] = {}
        self.order_book: Dict[str, List[Order]] = {}
        self.running = False
        
    async def start(self):
        """Start the trade engine"""
        self.running = True
        logger.info("Advanced Trade Engine started")
        
    async def stop(self):
        """Stop the trade engine"""
        self.running = False
        logger.info("Advanced Trade Engine stopped")
    
    def create_order(self, 
                    client_order_id: str,
                    instrument: str,
                    side: OrderSide,
                    order_type: OrderType,
                    quantity: Decimal,
                    price: Optional[Decimal] = None,
                    stop_price: Optional[Decimal] = None,
                    time_in_force: str = "GTC",
                    execution_algorithm: ExecutionAlgorithm = ExecutionAlgorithm.SIMPLE,
                    algorithm_params: Dict[str, Any] = None,
                    metadata: Dict[str, Any] = None) -> Order:
        """Create a new order with comprehensive validation"""
        
        # Generate unique order ID
        order_id = f"ORD_{uuid.uuid4().hex[:12].upper()}"
        
        # Validate order parameters
        if quantity <= 0:
            raise ValueError("Order quantity must be positive")
        
        if order_type in [OrderType.LIMIT, OrderType.STOP_LIMIT] and price is None:
            raise ValueError("Price required for limit orders")
        
        if order_type in [OrderType.STOP, OrderType.STOP_LIMIT] and stop_price is None:
            raise ValueError("Stop price required for stop orders")
        
        # Create order
        order = Order(
            order_id=order_id,
            client_order_id=client_order_id,
            instrument=instrument,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
            time_in_force=time_in_force,
            execution_algorithm=execution_algorithm,
            algorithm_params=algorithm_params or {},
            metadata=metadata or {}
        )
        
        # Risk checks
        if self.risk_engine:
            risk_result = self.risk_engine.validate_order(order)
            if not risk_result.get('approved', False):
                order.status = OrderStatus.REJECTED
                order.metadata['rejection_reason'] = risk_result.get('reason', 'Risk check failed')
                return order
        
        # Add to order book
        if instrument not in self.order_book:
            self.order_book[instrument] = []
        self.order_book[instrument].append(order)
        self.orders[order_id] = order
        
        logger.info(f"Order created: {order_id} for {instrument} {side.value} {quantity} @ {price}")
        return order
    
    async def execute_order(self, order_id: str, market_price: Decimal) -> List[Execution]:
        """Execute an order with sophisticated algorithms"""
        
        if order_id not in self.orders:
            raise ValueError(f"Order {order_id} not found")
        
        order = self.orders[order_id]
        if order.status != OrderStatus.NEW:
            return []
        
        executions = []
        
        # Execute based on algorithm
        if order.execution_algorithm == ExecutionAlgorithm.SIMPLE:
            executions = await self._execute_simple(order, market_price)
        elif order.execution_algorithm == ExecutionAlgorithm.TWAP:
            executions = await self._execute_twap(order, market_price)
        elif order.execution_algorithm == ExecutionAlgorithm.VWAP:
            executions = await self._execute_vwap(order, market_price)
        elif order.execution_algorithm == ExecutionAlgorithm.ICEBERG:
            executions = await self._execute_iceberg(order, market_price)
        elif order.execution_algorithm == ExecutionAlgorithm.PEG:
            executions = await self._execute_peg(order, market_price)
        elif order.execution_algorithm == ExecutionAlgorithm.ADAPTIVE:
            executions = await self._execute_adaptive(order, market_price)
        
        # Update order status
        total_filled = sum(exec.quantity for exec in executions)
        if total_filled >= order.quantity:
            order.status = OrderStatus.FILLED
        elif total_filled > 0:
            order.status = OrderStatus.PARTIALLY_FILLED
        
        order.filled_quantity = total_filled
        if executions:
            order.average_price = sum(exec.price * exec.quantity for exec in executions) / total_filled
        
        # Update positions
        for execution in executions:
            await self._update_position(execution)
        
        return executions
    
    async def _execute_simple(self, order: Order, market_price: Decimal) -> List[Execution]:
        """Simple execution algorithm"""
        executions = []
        
        if order.order_type == OrderType.MARKET:
            # Market order - execute at market price
            execution = Execution(
                execution_id=f"EXEC_{uuid.uuid4().hex[:12].upper()}",
                order_id=order.order_id,
                instrument=order.instrument,
                side=order.side,
                quantity=order.quantity,
                price=market_price,
                execution_time=datetime.utcnow(),
                venue="INTERNAL"
            )
            executions.append(execution)
            
        elif order.order_type == OrderType.LIMIT:
            # Limit order - execute if price is favorable
            if order.side == OrderSide.BUY and market_price <= order.price:
                execution = Execution(
                    execution_id=f"EXEC_{uuid.uuid4().hex[:12].upper()}",
                    order_id=order.order_id,
                    instrument=order.instrument,
                    side=order.side,
                    quantity=order.quantity,
                    price=order.price,
                    execution_time=datetime.utcnow(),
                    venue="INTERNAL"
                )
                executions.append(execution)
            elif order.side == OrderSide.SELL and market_price >= order.price:
                execution = Execution(
                    execution_id=f"EXEC_{uuid.uuid4().hex[:12].upper()}",
                    order_id=order.order_id,
                    instrument=order.instrument,
                    side=order.side,
                    quantity=order.quantity,
                    price=order.price,
                    execution_time=datetime.utcnow(),
                    venue="INTERNAL"
                )
                executions.append(execution)
        
        return executions
    
    async def _execute_twap(self, order: Order, market_price: Decimal) -> List[Execution]:
        """Time-Weighted Average Price execution"""
        executions = []
        
        # Get TWAP parameters
        duration_minutes = order.algorithm_params.get('duration_minutes', 60)
        slice_size = order.algorithm_params.get('slice_size', 0.1)  # 10% of order per slice
        
        # Calculate number of slices
        num_slices = max(1, int(duration_minutes / 5))  # 5-minute intervals
        slice_quantity = order.quantity / num_slices
        
        # Execute slices over time
        for i in range(num_slices):
            await asyncio.sleep(5)  # 5-second delay between slices
            
            execution = Execution(
                execution_id=f"EXEC_{uuid.uuid4().hex[:12].upper()}",
                order_id=order.order_id,
                instrument=order.instrument,
                side=order.side,
                quantity=slice_quantity,
                price=market_price,
                execution_time=datetime.utcnow(),
                venue="INTERNAL"
            )
            executions.append(execution)
        
        return executions
    
    async def _execute_vwap(self, order: Order, market_price: Decimal) -> List[Execution]:
        """Volume-Weighted Average Price execution"""
        executions = []
        
        # Get historical volume data for VWAP calculation
        if self.market_data_engine:
            vwap_price = await self.market_data_engine.get_vwap(order.instrument, period_minutes=60)
        else:
            vwap_price = market_price
        
        # Execute at VWAP price
        execution = Execution(
            execution_id=f"EXEC_{uuid.uuid4().hex[:12].upper()}",
            order_id=order.order_id,
            instrument=order.instrument,
            side=order.side,
            quantity=order.quantity,
            price=vwap_price,
            execution_time=datetime.utcnow(),
            venue="INTERNAL"
        )
        executions.append(execution)
        
        return executions
    
    async def _execute_iceberg(self, order: Order, market_price: Decimal) -> List[Execution]:
        """Iceberg execution - hide large orders"""
        executions = []
        
        # Get iceberg parameters
        visible_size = order.algorithm_params.get('visible_size', order.quantity * Decimal('0.1'))
        refresh_rate = order.algorithm_params.get('refresh_rate_seconds', 30)
        
        remaining_quantity = order.quantity
        
        while remaining_quantity > 0:
            # Execute visible size
            exec_quantity = min(visible_size, remaining_quantity)
            
            execution = Execution(
                execution_id=f"EXEC_{uuid.uuid4().hex[:12].upper()}",
                order_id=order.order_id,
                instrument=order.instrument,
                side=order.side,
                quantity=exec_quantity,
                price=market_price,
                execution_time=datetime.utcnow(),
                venue="INTERNAL"
            )
            executions.append(execution)
            
            remaining_quantity -= exec_quantity
            
            if remaining_quantity > 0:
                await asyncio.sleep(refresh_rate)
        
        return executions
    
    async def _execute_peg(self, order: Order, market_price: Decimal) -> List[Execution]:
        """Peg execution - follow market with offset"""
        executions = []
        
        # Get peg parameters
        offset = order.algorithm_params.get('offset', Decimal('0.01'))  # 1 cent offset
        min_price = order.algorithm_params.get('min_price', Decimal('0.01'))
        max_price = order.algorithm_params.get('max_price', Decimal('1000.00'))
        
        # Calculate peg price
        if order.side == OrderSide.BUY:
            peg_price = market_price - offset
        else:
            peg_price = market_price + offset
        
        # Ensure price is within bounds
        peg_price = max(min_price, min(max_price, peg_price))
        
        execution = Execution(
            execution_id=f"EXEC_{uuid.uuid4().hex[:12].upper()}",
            order_id=order.order_id,
            instrument=order.instrument,
            side=order.side,
            quantity=order.quantity,
            price=peg_price,
            execution_time=datetime.utcnow(),
            venue="INTERNAL"
        )
        executions.append(execution)
        
        return executions
    
    async def _execute_adaptive(self, order: Order, market_price: Decimal) -> List[Execution]:
        """Adaptive execution - ML-based order splitting"""
        executions = []
        
        # Get market conditions
        volatility = order.algorithm_params.get('volatility', 0.02)
        liquidity = order.algorithm_params.get('liquidity', 1.0)
        
        # Calculate optimal execution strategy
        if volatility > 0.05:  # High volatility
            # Use TWAP with smaller slices
            return await self._execute_twap(order, market_price)
        elif liquidity < 0.5:  # Low liquidity
            # Use iceberg execution
            return await self._execute_iceberg(order, market_price)
        else:
            # Use simple execution
            return await self._execute_simple(order, market_price)
    
    async def _update_position(self, execution: Execution):
        """Update position after execution"""
        instrument = execution.instrument
        
        if instrument not in self.positions:
            self.positions[instrument] = Position(
                instrument=instrument,
                quantity=Decimal('0'),
                average_price=Decimal('0'),
                current_price=execution.price,
                unrealized_pnl=Decimal('0'),
                realized_pnl=Decimal('0')
            )
        
        position = self.positions[instrument]
        
        if execution.side == OrderSide.BUY:
            # Buying - increase position
            if position.quantity == 0:
                position.quantity = execution.quantity
                position.average_price = execution.price
                position.cost_basis = execution.quantity * execution.price
            else:
                # Calculate new average price
                total_cost = position.cost_basis + (execution.quantity * execution.price)
                total_quantity = position.quantity + execution.quantity
                position.average_price = total_cost / total_quantity
                position.quantity = total_quantity
                position.cost_basis = total_cost
        else:
            # Selling - decrease position
            if position.quantity >= execution.quantity:
                # Calculate realized P&L
                realized_pnl = execution.quantity * (execution.price - position.average_price)
                position.realized_pnl += realized_pnl
                position.quantity -= execution.quantity
                position.cost_basis -= execution.quantity * position.average_price
            else:
                # Short position
                if position.quantity > 0:
                    # Close long position first
                    realized_pnl = position.quantity * (execution.price - position.average_price)
                    position.realized_pnl += realized_pnl
                    remaining_quantity = execution.quantity - position.quantity
                    position.quantity = -remaining_quantity
                    position.average_price = execution.price
                    position.cost_basis = -remaining_quantity * execution.price
                else:
                    # Increase short position
                    total_cost = position.cost_basis + (execution.quantity * execution.price)
                    total_quantity = abs(position.quantity) + execution.quantity
                    position.average_price = total_cost / total_quantity
                    position.quantity = -total_quantity
                    position.cost_basis = -total_quantity * position.average_price
        
        # Update current price and P&L
        position.update_price(execution.price)
    
    def get_positions(self) -> Dict[str, Position]:
        """Get all positions"""
        return self.positions.copy()
    
    def get_position(self, instrument: str) -> Optional[Position]:
        """Get position for specific instrument"""
        return self.positions.get(instrument)
    
    def get_orders(self, status: Optional[OrderStatus] = None) -> List[Order]:
        """Get orders with optional status filter"""
        if status is None:
            return list(self.orders.values())
        return [order for order in self.orders.values() if order.status == status]
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        if order_id not in self.orders:
            return False
        
        order = self.orders[order_id]
        if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED]:
            return False
        
        order.status = OrderStatus.CANCELLED
        order.updated_at = datetime.utcnow()
        
        # Remove from order book
        if order.instrument in self.order_book:
            self.order_book[order.instrument] = [
                o for o in self.order_book[order.instrument] if o.order_id != order_id
            ]
        
        logger.info(f"Order cancelled: {order_id}")
        return True
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get comprehensive portfolio summary"""
        total_market_value = sum(pos.market_value for pos in self.positions.values())
        total_unrealized_pnl = sum(pos.unrealized_pnl for pos in self.positions.values())
        total_realized_pnl = sum(pos.realized_pnl for pos in self.positions.values())
        total_pnl = total_unrealized_pnl + total_realized_pnl
        
        return {
            "total_positions": len(self.positions),
            "total_market_value": float(total_market_value),
            "total_unrealized_pnl": float(total_unrealized_pnl),
            "total_realized_pnl": float(total_realized_pnl),
            "total_pnl": float(total_pnl),
            "pnl_percentage": float((total_pnl / total_market_value * 100) if total_market_value > 0 else 0),
            "positions": [
                {
                    "instrument": pos.instrument,
                    "quantity": float(pos.quantity),
                    "average_price": float(pos.average_price),
                    "current_price": float(pos.current_price),
                    "market_value": float(pos.market_value),
                    "unrealized_pnl": float(pos.unrealized_pnl),
                    "realized_pnl": float(pos.realized_pnl)
                }
                for pos in self.positions.values()
            ]
        }
