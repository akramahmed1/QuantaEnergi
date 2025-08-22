"""
Trading Service for EnergyOpti-Pro.

Handles order management, position tracking, and real-time trading operations.
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
import structlog
from dataclasses import dataclass
from uuid import uuid4

logger = structlog.get_logger()

class OrderStatus(Enum):
    """Order status enumeration."""
    PENDING = "pending"
    SUBMITTED = "submitted"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"

class OrderType(Enum):
    """Order type enumeration."""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    FILL_OR_KILL = "fill_or_kill"
    IMMEDIATE_OR_CANCEL = "immediate_or_cancel"
    GOOD_TILL_CANCELLED = "good_till_cancelled"

class OrderSide(Enum):
    """Order side enumeration."""
    BUY = "buy"
    SELL = "sell"

@dataclass
class Order:
    """Trading order with full metadata."""
    id: str
    user_id: str
    commodity: str
    exchange: str
    side: OrderSide
    order_type: OrderType
    quantity: Decimal
    price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: Decimal = Decimal("0")
    average_fill_price: Optional[Decimal] = None
    created_at: datetime = None
    updated_at: datetime = None
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = datetime.now(timezone.utc)
        if self.metadata is None:
            self.metadata = {}

@dataclass
class Position:
    """Trading position with P&L tracking."""
    id: str
    user_id: str
    commodity: str
    exchange: str
    quantity: Decimal
    average_price: Decimal
    current_price: Decimal
    unrealized_pnl: Decimal
    realized_pnl: Decimal = Decimal("0")
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = datetime.now(timezone.utc)

class TradingService:
    """Real-time trading service with order management and position tracking."""
    
    def __init__(self):
        self.orders: Dict[str, Order] = {}
        self.positions: Dict[str, Position] = {}
        self.order_counter = 0
        self.position_counter = 0
        
    async def create_order(
        self,
        user_id: str,
        commodity: str,
        exchange: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: Decimal,
        price: Optional[Decimal] = None,
        stop_price: Optional[Decimal] = None,
        expires_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Order:
        """Create a new trading order."""
        try:
            # Validate order parameters
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
            
            if order_type in [OrderType.LIMIT, OrderType.STOP_LIMIT] and price is None:
                raise ValueError("Price is required for limit orders")
            
            if order_type in [OrderType.STOP, OrderType.STOP_LIMIT] and stop_price is None:
                raise ValueError("Stop price is required for stop orders")
            
            # Generate unique order ID
            order_id = f"order_{uuid4().hex[:8]}"
            
            # Create order
            order = Order(
                id=order_id,
                user_id=user_id,
                commodity=commodity,
                exchange=exchange,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price,
                stop_price=stop_price,
                expires_at=expires_at,
                metadata=metadata or {}
            )
            
            # Store order
            self.orders[order_id] = order
            
            logger.info(f"Created order {order_id}", 
                       user_id=user_id, commodity=commodity, side=side.value)
            
            return order
            
        except Exception as e:
            logger.error(f"Failed to create order: {e}")
            raise
    
    async def submit_order(self, order_id: str) -> Order:
        """Submit an order for execution."""
        try:
            if order_id not in self.orders:
                raise ValueError(f"Order {order_id} not found")
            
            order = self.orders[order_id]
            
            if order.status != OrderStatus.PENDING:
                raise ValueError(f"Order {order_id} is not in pending status")
            
            # Update order status
            order.status = OrderStatus.SUBMITTED
            order.updated_at = datetime.now(timezone.utc)
            
            logger.info(f"Submitted order {order_id}")
            
            # Simulate order execution (in real implementation, this would connect to exchange)
            await self._simulate_order_execution(order)
            
            return order
            
        except Exception as e:
            logger.error(f"Failed to submit order {order_id}: {e}")
            raise
    
    async def cancel_order(self, order_id: str, user_id: str) -> Order:
        """Cancel an existing order."""
        try:
            if order_id not in self.orders:
                raise ValueError(f"Order {order_id} not found")
            
            order = self.orders[order_id]
            
            if order.user_id != user_id:
                raise ValueError("Unauthorized to cancel this order")
            
            if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED]:
                raise ValueError(f"Order {order_id} cannot be cancelled")
            
            # Update order status
            order.status = OrderStatus.CANCELLED
            order.updated_at = datetime.now(timezone.utc)
            
            logger.info(f"Cancelled order {order_id}")
            
            return order
            
        except Exception as e:
            logger.error(f"Failed to cancel order {order_id}: {e}")
            raise
    
    async def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID."""
        return self.orders.get(order_id)
    
    async def get_user_orders(self, user_id: str, status: Optional[OrderStatus] = None) -> List[Order]:
        """Get all orders for a user, optionally filtered by status."""
        user_orders = [order for order in self.orders.values() if order.user_id == user_id]
        
        if status:
            user_orders = [order for order in user_orders if order.status == status]
        
        return sorted(user_orders, key=lambda x: x.created_at, reverse=True)
    
    async def get_position(self, position_id: str) -> Optional[Position]:
        """Get position by ID."""
        return self.positions.get(position_id)
    
    async def get_user_positions(self, user_id: str) -> List[Position]:
        """Get all positions for a user."""
        user_positions = [pos for pos in self.positions.values() if pos.user_id == user_id]
        return sorted(user_positions, key=lambda x: x.updated_at, reverse=True)
    
    async def update_position_price(self, position_id: str, current_price: Decimal) -> Position:
        """Update position with current market price and recalculate P&L."""
        try:
            if position_id not in self.positions:
                raise ValueError(f"Position {position_id} not found")
            
            position = self.positions[position_id]
            
            # Update current price
            position.current_price = current_price
            position.updated_at = datetime.now(timezone.utc)
            
            # Calculate unrealized P&L
            if position.side == OrderSide.BUY:
                position.unrealized_pnl = (current_price - position.average_price) * position.quantity
            else:
                position.unrealized_pnl = (position.average_price - current_price) * position.quantity
            
            logger.debug(f"Updated position {position_id} price to {current_price}")
            
            return position
            
        except Exception as e:
            logger.error(f"Failed to update position {position_id} price: {e}")
            raise
    
    async def _simulate_order_execution(self, order: Order):
        """Simulate order execution for demonstration purposes."""
        try:
            # Simulate market conditions
            await asyncio.sleep(0.1)  # Simulate processing time
            
            # Random fill simulation
            import random
            fill_probability = 0.7  # 70% chance of immediate fill
            
            if random.random() < fill_probability:
                # Order gets filled
                order.status = OrderStatus.FILLED
                order.filled_quantity = order.quantity
                order.average_fill_price = order.price or Decimal("75.50")  # Mock price
                order.updated_at = datetime.now(timezone.utc)
                
                # Create or update position
                await self._update_position_from_fill(order)
                
                logger.info(f"Order {order.id} filled completely")
            else:
                # Order partially filled
                order.status = OrderStatus.PARTIALLY_FILLED
                order.filled_quantity = order.quantity * Decimal("0.6")  # 60% fill
                order.average_fill_price = order.price or Decimal("75.50")
                order.updated_at = datetime.now(timezone.utc)
                
                # Create or update position
                await self._update_position_from_fill(order)
                
                logger.info(f"Order {order.id} partially filled")
                
        except Exception as e:
            logger.error(f"Failed to simulate order execution: {e}")
            order.status = OrderStatus.REJECTED
            order.updated_at = datetime.now(timezone.utc)
    
    async def _update_position_from_fill(self, order: Order):
        """Update or create position based on order fill."""
        try:
            # Find existing position for this user/commodity/exchange combination
            position_key = f"{order.user_id}_{order.commodity}_{order.exchange}"
            
            if position_key in self.positions:
                # Update existing position
                position = self.positions[position_key]
                
                # Calculate new average price
                total_cost = (position.quantity * position.average_price + 
                            order.filled_quantity * order.average_fill_price)
                total_quantity = position.quantity + order.filled_quantity
                new_average_price = total_cost / total_quantity
                
                # Update position
                position.quantity = total_quantity
                position.average_price = new_average_price
                position.updated_at = datetime.now(timezone.utc)
                
                logger.info(f"Updated existing position {position.id}")
                
            else:
                # Create new position
                position_id = f"pos_{uuid4().hex[:8]}"
                
                position = Position(
                    id=position_id,
                    user_id=order.user_id,
                    commodity=order.commodity,
                    exchange=order.exchange,
                    quantity=order.filled_quantity,
                    average_price=order.average_fill_price,
                    current_price=order.average_fill_price,
                    unrealized_pnl=Decimal("0")
                )
                
                self.positions[position_key] = position
                
                logger.info(f"Created new position {position_id}")
                
        except Exception as e:
            logger.error(f"Failed to update position from fill: {e}")
    
    async def get_trading_summary(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive trading summary for a user."""
        try:
            # Get user orders and positions
            orders = await self.get_user_orders(user_id)
            positions = await self.get_user_positions(user_id)
            
            # Calculate summary statistics
            total_orders = len(orders)
            active_orders = len([o for o in orders if o.status in [OrderStatus.PENDING, OrderStatus.SUBMITTED]])
            filled_orders = len([o for o in orders if o.status == OrderStatus.FILLED])
            
            total_positions = len(positions)
            total_unrealized_pnl = sum(pos.unrealized_pnl for pos in positions)
            total_realized_pnl = sum(pos.realized_pnl for pos in positions)
            
            # Calculate total portfolio value
            total_portfolio_value = sum(pos.quantity * pos.current_price for pos in positions)
            
            return {
                "user_id": user_id,
                "orders_summary": {
                    "total": total_orders,
                    "active": active_orders,
                    "filled": filled_orders
                },
                "positions_summary": {
                    "total": total_positions,
                    "total_value": total_portfolio_value
                },
                "pnl_summary": {
                    "unrealized": total_unrealized_pnl,
                    "realized": total_realized_pnl,
                    "total": total_unrealized_pnl + total_realized_pnl
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get trading summary for user {user_id}: {e}")
            raise 