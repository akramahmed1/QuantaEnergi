import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import json

class TradingService:
    """Comprehensive trading service for ETRM/CTRM"""
    
    def __init__(self):
        # Supported exchanges by region
        self.exchanges = {
            "ME": {
                "ADX": "Abu Dhabi Securities Exchange",
                "DFM": "Dubai Financial Market",
                "Tadawul": "Saudi Stock Exchange",
                "QSE": "Qatar Stock Exchange"
            },
            "US": {
                "CME": "Chicago Mercantile Exchange",
                "ICE": "Intercontinental Exchange",
                "NYMEX": "New York Mercantile Exchange",
                "PJM": "PJM Interconnection"
            },
            "UK": {
                "LSE": "London Stock Exchange",
                "ICE_UK": "ICE UK Energy",
                "N2EX": "N2EX Power Exchange"
            },
            "EU": {
                "EEX": "European Energy Exchange",
                "EPEX": "EPEX SPOT",
                "Nord_Pool": "Nord Pool",
                "OMIE": "OMIE (Spain)"
            },
            "GUYANA": {
                "Local_OTC": "Local Over-the-Counter Market",
                "Regional_Exchange": "Caribbean Energy Exchange"
            }
        }
        
        # Commodity types and units
        self.commodities = {
            "power": {
                "unit": "MWh",
                "contract_sizes": [1, 5, 10, 25, 50, 100],
                "delivery_periods": ["hourly", "daily", "weekly", "monthly", "quarterly", "yearly"]
            },
            "gas": {
                "unit": "MMBtu",
                "contract_sizes": [1000, 5000, 10000, 50000, 100000],
                "delivery_periods": ["daily", "weekly", "monthly", "quarterly"]
            },
            "oil": {
                "unit": "barrel",
                "contract_sizes": [1000, 5000, 10000, 50000, 100000],
                "delivery_periods": ["monthly", "quarterly", "yearly"]
            },
            "carbon": {
                "unit": "ton CO2e",
                "contract_sizes": [1000, 5000, 10000, 50000, 100000],
                "delivery_periods": ["monthly", "quarterly", "yearly"]
            }
        }
        
        # Order types
        self.order_types = [
            "market", "limit", "stop", "stop_limit", "fill_or_kill", 
            "immediate_or_cancel", "good_till_cancelled", "day_order"
        ]
    
    async def place_order(
        self,
        trader_id: int,
        contract_id: str,
        order_type: str,
        side: str,  # buy or sell
        quantity: float,
        price: Optional[Decimal] = None,
        exchange: str = "OTC",
        region: str = "US",
        time_in_force: str = "day",
        stop_price: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """Place a new trading order"""
        
        # Validate order parameters
        validation = await self._validate_order(
            order_type, side, quantity, price, stop_price, time_in_force
        )
        
        if not validation["valid"]:
            return {
                "status": "rejected",
                "order_id": None,
                "errors": validation["errors"]
            }
        
        # Generate order ID
        order_id = f"ORD-{region}-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
        
        # Create order object
        order = {
            "order_id": order_id,
            "trader_id": trader_id,
            "contract_id": contract_id,
            "order_type": order_type,
            "side": side,
            "quantity": quantity,
            "price": float(price) if price else None,
            "stop_price": float(stop_price) if stop_price else None,
            "exchange": exchange,
            "region": region,
            "time_in_force": time_in_force,
            "status": "pending",
            "placed_at": datetime.now(),
            "filled_quantity": 0,
            "remaining_quantity": quantity,
            "average_fill_price": None,
            "fills": []
        }
        
        # Route order to appropriate exchange
        routing_result = await self._route_order(order)
        
        if routing_result["success"]:
            order["status"] = "accepted"
            order["exchange_order_id"] = routing_result["exchange_order_id"]
        else:
            order["status"] = "rejected"
            order["rejection_reason"] = routing_result["reason"]
        
        return {
            "status": order["status"],
            "order_id": order_id,
            "exchange_order_id": order.get("exchange_order_id"),
            "rejection_reason": order.get("rejection_reason"),
            "order_details": order
        }
    
    async def cancel_order(
        self,
        order_id: str,
        trader_id: int
    ) -> Dict[str, Any]:
        """Cancel an existing order"""
        
        # Mock order cancellation - in production, integrate with exchange APIs
        await asyncio.sleep(0.1)  # Simulate processing time
        
        return {
            "status": "cancelled",
            "order_id": order_id,
            "cancelled_at": datetime.now(),
            "message": "Order cancelled successfully"
        }
    
    async def modify_order(
        self,
        order_id: str,
        trader_id: int,
        new_quantity: Optional[float] = None,
        new_price: Optional[Decimal] = None,
        new_stop_price: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """Modify an existing order"""
        
        # Mock order modification - in production, integrate with exchange APIs
        await asyncio.sleep(0.1)  # Simulate processing time
        
        modifications = {}
        if new_quantity is not None:
            modifications["quantity"] = new_quantity
        if new_price is not None:
            modifications["price"] = float(new_price)
        if new_stop_price is not None:
            modifications["stop_price"] = float(new_stop_price)
        
        return {
            "status": "modified",
            "order_id": order_id,
            "modifications": modifications,
            "modified_at": datetime.now(),
            "message": "Order modified successfully"
        }
    
    async def get_order_status(
        self,
        order_id: str,
        trader_id: int
    ) -> Dict[str, Any]:
        """Get current status of an order"""
        
        # Mock order status - in production, query exchange or database
        await asyncio.sleep(0.05)  # Simulate API call
        
        # Simulate different order statuses
        statuses = ["pending", "partially_filled", "filled", "cancelled", "rejected"]
        current_status = statuses[hash(order_id) % len(statuses)]
        
        order_status = {
            "order_id": order_id,
            "status": current_status,
            "placed_at": datetime.now() - timedelta(hours=2),
            "last_updated": datetime.now(),
            "filled_quantity": 0.7 if current_status == "partially_filled" else 1.0 if current_status == "filled" else 0,
            "remaining_quantity": 0.3 if current_status == "partially_filled" else 0,
            "average_fill_price": 75.50 if current_status in ["partially_filled", "filled"] else None
        }
        
        return order_status
    
    async def get_trading_history(
        self,
        trader_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        region: Optional[str] = None,
        commodity: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get trading history for a trader"""
        
        # Mock trading history - in production, query database
        await asyncio.sleep(0.1)
        
        # Generate mock trades
        mock_trades = []
        base_date = start_date or (datetime.now() - timedelta(days=30))
        end_date = end_date or datetime.now()
        
        for i in range(20):
            trade_date = base_date + timedelta(days=i)
            if trade_date <= end_date:
                mock_trades.append({
                    "trade_id": f"TRD-{i:06d}",
                    "contract_id": f"CTR-{i:06d}",
                    "side": "buy" if i % 2 == 0 else "sell",
                    "quantity": 100 + (i * 50),
                    "price": 70.0 + (i * 0.5),
                    "trade_date": trade_date,
                    "commodity": commodity or ["power", "gas", "oil", "carbon"][i % 4],
                    "region": region or ["ME", "US", "UK", "EU", "GUYANA"][i % 5],
                    "exchange": "OTC"
                })
        
        return {
            "trader_id": trader_id,
            "trades": mock_trades,
            "total_trades": len(mock_trades),
            "period": {
                "start_date": base_date,
                "end_date": end_date
            },
            "summary": {
                "total_volume": sum(t["quantity"] for t in mock_trades),
                "total_value": sum(t["quantity"] * t["price"] for t in mock_trades),
                "buy_volume": sum(t["quantity"] for t in mock_trades if t["side"] == "buy"),
                "sell_volume": sum(t["quantity"] for t in mock_trades if t["side"] == "sell")
            }
        }
    
    async def calculate_execution_analytics(
        self,
        trader_id: int,
        start_date: datetime,
        end_date: datetime,
        region: Optional[str] = None
    ) -> Dict[str, Any]:
        """Calculate execution analytics for trading performance"""
        
        # Get trading history
        history = await self.get_trading_history(trader_id, start_date, end_date, region)
        trades = history["trades"]
        
        if not trades:
            return {
                "trader_id": trader_id,
                "period": {"start_date": start_date, "end_date": end_date},
                "analytics": "No trades found for the specified period"
            }
        
        # Calculate execution metrics
        total_trades = len(trades)
        filled_trades = len([t for t in trades if t["status"] != "cancelled"])
        fill_rate = filled_trades / total_trades if total_trades > 0 else 0
        
        # Calculate slippage (mock data)
        slippage = sum([0.1 + (i * 0.01) for i in range(len(trades))])
        avg_slippage = slippage / len(trades) if trades else 0
        
        # Calculate market impact
        large_trades = [t for t in trades if t["quantity"] > 500]
        market_impact = len(large_trades) * 0.05  # Mock impact calculation
        
        # Calculate execution costs
        execution_costs = {
            "commission": sum(t["quantity"] * t["price"] * 0.001 for t in trades),  # 0.1% commission
            "slippage": slippage,
            "market_impact": market_impact,
            "total": sum(t["quantity"] * t["price"] * 0.001 for t in trades) + slippage + market_impact
        }
        
        # Performance metrics
        buy_trades = [t for t in trades if t["side"] == "buy"]
        sell_trades = [t for t in trades if t["side"] == "sell"]
        
        avg_buy_price = sum(t["price"] for t in buy_trades) / len(buy_trades) if buy_trades else 0
        avg_sell_price = sum(t["price"] for t in sell_trades) / len(sell_trades) if sell_trades else 0
        
        return {
            "trader_id": trader_id,
            "period": {"start_date": start_date, "end_date": end_date},
            "execution_metrics": {
                "total_trades": total_trades,
                "filled_trades": filled_trades,
                "fill_rate": fill_rate,
                "average_slippage": avg_slippage,
                "market_impact": market_impact
            },
            "cost_analysis": execution_costs,
            "performance_metrics": {
                "average_buy_price": avg_buy_price,
                "average_sell_price": avg_sell_price,
                "price_spread": avg_sell_price - avg_buy_price if avg_buy_price > 0 and avg_sell_price > 0 else 0
            },
            "regional_breakdown": self._calculate_regional_breakdown(trades),
            "commodity_breakdown": self._calculate_commodity_breakdown(trades)
        }
    
    async def get_market_depth(
        self,
        commodity: str,
        location: str,
        region: str,
        exchange: str = "OTC"
    ) -> Dict[str, Any]:
        """Get market depth for a specific commodity and location"""
        
        # Mock market depth - in production, integrate with exchange APIs
        await asyncio.sleep(0.05)
        
        # Generate mock order book
        base_price = 75.0
        spread = 0.50
        
        bids = []
        asks = []
        
        # Generate bid orders (buy orders)
        for i in range(5):
            price = base_price - (i * 0.10) - (spread / 2)
            quantity = 100 + (i * 50)
            bids.append({
                "price": round(price, 2),
                "quantity": quantity,
                "orders": 2 + i
            })
        
        # Generate ask orders (sell orders)
        for i in range(5):
            price = base_price + (i * 0.10) + (spread / 2)
            quantity = 100 + (i * 50)
            asks.append({
                "price": round(price, 2),
                "quantity": quantity,
                "orders": 2 + i
            })
        
        return {
            "commodity": commodity,
            "location": location,
            "region": region,
            "exchange": exchange,
            "timestamp": datetime.now(),
            "bids": bids,
            "asks": asks,
            "spread": spread,
            "mid_price": base_price,
            "total_bid_volume": sum(b["quantity"] for b in bids),
            "total_ask_volume": sum(a["quantity"] for a in asks)
        }
    
    async def _validate_order(
        self,
        order_type: str,
        side: str,
        quantity: float,
        price: Optional[Decimal],
        stop_price: Optional[Decimal],
        time_in_force: str
    ) -> Dict[str, Any]:
        """Validate order parameters"""
        
        errors = []
        
        # Validate order type
        if order_type not in self.order_types:
            errors.append(f"Invalid order type: {order_type}")
        
        # Validate side
        if side not in ["buy", "sell"]:
            errors.append(f"Invalid side: {side}")
        
        # Validate quantity
        if quantity <= 0:
            errors.append("Quantity must be positive")
        
        # Validate price for limit orders
        if order_type in ["limit", "stop_limit"] and price is None:
            errors.append("Price is required for limit orders")
        
        # Validate stop price for stop orders
        if order_type in ["stop", "stop_limit"] and stop_price is None:
            errors.append("Stop price is required for stop orders")
        
        # Validate time in force
        valid_tif = ["day", "good_till_cancelled", "immediate_or_cancel", "fill_or_kill"]
        if time_in_force not in valid_tif:
            errors.append(f"Invalid time in force: {time_in_force}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    async def _route_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Route order to appropriate exchange"""
        
        # Mock order routing - in production, integrate with exchange APIs
        await asyncio.sleep(0.1)
        
        # Simulate exchange acceptance
        if order["exchange"] == "OTC":
            return {
                "success": True,
                "exchange_order_id": f"OTC-{uuid.uuid4().hex[:8]}",
                "exchange": "OTC"
            }
        else:
            # Simulate exchange-specific routing
            return {
                "success": True,
                "exchange_order_id": f"{order['exchange']}-{uuid.uuid4().hex[:8]}",
                "exchange": order["exchange"]
            }
    
    def _calculate_regional_breakdown(self, trades: List[Dict]) -> Dict[str, Any]:
        """Calculate regional breakdown of trades"""
        
        regional_data = {}
        for trade in trades:
            region = trade.get("region", "unknown")
            if region not in regional_data:
                regional_data[region] = {
                    "trade_count": 0,
                    "total_volume": 0,
                    "total_value": 0
                }
            
            regional_data[region]["trade_count"] += 1
            regional_data[region]["total_volume"] += trade["quantity"]
            regional_data[region]["total_value"] += trade["quantity"] * trade["price"]
        
        return regional_data
    
    def _calculate_commodity_breakdown(self, trades: List[Dict]) -> Dict[str, Any]:
        """Calculate commodity breakdown of trades"""
        
        commodity_data = {}
        for trade in trades:
            commodity = trade.get("commodity", "unknown")
            if commodity not in commodity_data:
                commodity_data[commodity] = {
                    "trade_count": 0,
                    "total_volume": 0,
                    "total_value": 0
                }
            
            commodity_data[commodity]["trade_count"] += 1
            commodity_data[commodity]["total_volume"] += trade["quantity"]
            commodity_data[commodity]["total_value"] += trade["quantity"] * trade["price"]
        
        return commodity_data 