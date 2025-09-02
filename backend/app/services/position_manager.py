"""
Position Manager Service for ETRM/CTRM Trading
Handles position tracking, P&L calculations, and risk management
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class PositionManager:
    """Service for managing trading positions and P&L"""
    
    def __init__(self):
        self.positions = {}  # In-memory storage for stubs
        self.position_counter = 1000
        
    def create_position(self, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new trading position from deal
        
        Args:
            deal_data: Deal information to create position from
            
        Returns:
            Dict with created position details
        """
        # TODO: Implement real position creation with database
        position_id = f"POS-{self.position_counter:06d}"
        self.position_counter += 1
        
        # Calculate position metrics
        quantity = deal_data.get("quantity", 0)
        price = deal_data.get("price", 0.0)
        notional_value = quantity * price
        
        position = {
            "position_id": position_id,
            "deal_id": deal_data.get("deal_id"),
            "commodity": deal_data.get("commodity"),
            "quantity": quantity,
            "entry_price": price,
            "notional_value": notional_value,
            "currency": deal_data.get("currency", "USD"),
            "trade_type": deal_data.get("trade_type", "spot"),
            "direction": deal_data.get("direction", "long"),
            "status": "open",
            "created_at": datetime.now().isoformat(),
            "sharia_compliant": deal_data.get("sharia_compliant", False),
            "risk_metrics": self._calculate_position_risk(quantity, price)
        }
        
        self.positions[position_id] = position
        
        return {
            "success": True,
            "position_id": position_id,
            "position": position
        }
    
    def get_position(self, position_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve position by ID
        
        Args:
            position_id: Unique position identifier
            
        Returns:
            Position record or None if not found
        """
        return self.positions.get(position_id)
    
    def update_position(self, position_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update existing position
        
        Args:
            position_id: Unique position identifier
            updates: Fields to update
            
        Returns:
            Dict with update status
        """
        if position_id not in self.positions:
            return {
                "success": False,
                "error": "Position not found"
            }
        
        # TODO: Implement proper update validation
        for key, value in updates.items():
            if key in ["position_id", "created_at"]:
                continue  # Protected fields
            self.positions[position_id][key] = value
        
        self.positions[position_id]["updated_at"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "position": self.positions[position_id]
        }
    
    def close_position(self, position_id: str, exit_price: float, exit_quantity: Optional[float] = None) -> Dict[str, Any]:
        """
        Close or partially close a position
        
        Args:
            position_id: Unique position identifier
            exit_price: Price at which position is closed
            exit_quantity: Quantity to close (None for full close)
            
        Returns:
            Dict with closure details and P&L
        """
        if position_id not in self.positions:
            return {
                "success": False,
                "error": "Position not found"
            }
        
        position = self.positions[position_id]
        current_quantity = position["quantity"]
        
        if exit_quantity is None:
            exit_quantity = current_quantity
        
        if exit_quantity > current_quantity:
            return {
                "success": False,
                "error": f"Exit quantity {exit_quantity} exceeds current quantity {current_quantity}"
            }
        
        # Calculate P&L
        entry_price = position["entry_price"]
        pnl = (exit_price - entry_price) * exit_quantity
        
        # Update position
        remaining_quantity = current_quantity - exit_quantity
        
        if remaining_quantity == 0:
            position["status"] = "closed"
            position["closed_at"] = datetime.now().isoformat()
        else:
            position["quantity"] = remaining_quantity
        
        position["last_exit_price"] = exit_price
        position["total_pnl"] = position.get("total_pnl", 0) + pnl
        
        return {
            "success": True,
            "pnl": pnl,
            "remaining_quantity": remaining_quantity,
            "position": position
        }
    
    def calculate_pnl(self, position_id: str, current_price: float) -> Dict[str, Any]:
        """
        Calculate unrealized P&L for position
        
        Args:
            position_id: Unique position identifier
            current_price: Current market price
            
        Returns:
            Dict with P&L calculations
        """
        if position_id not in self.positions:
            return {
                "success": False,
                "error": "Position not found"
            }
        
        position = self.positions[position_id]
        quantity = position["quantity"]
        entry_price = position["entry_price"]
        
        # TODO: Implement proper P&L calculations with fees, taxes, etc.
        unrealized_pnl = (current_price - entry_price) * quantity
        pnl_percentage = (unrealized_pnl / (entry_price * quantity)) * 100 if entry_price > 0 else 0
        
        return {
            "success": True,
            "unrealized_pnl": unrealized_pnl,
            "pnl_percentage": pnl_percentage,
            "current_price": current_price,
            "entry_price": entry_price,
            "quantity": quantity
        }
    
    def get_portfolio_summary(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get portfolio summary with aggregate metrics
        
        Args:
            filters: Optional filter criteria
            
        Returns:
            Dict with portfolio summary
        """
        # TODO: Implement proper portfolio aggregation
        open_positions = [p for p in self.positions.values() if p["status"] == "open"]
        
        total_notional = sum(p["notional_value"] for p in open_positions)
        total_pnl = sum(p.get("total_pnl", 0) for p in open_positions)
        
        # Group by commodity
        commodity_positions = {}
        for pos in open_positions:
            commodity = pos["commodity"]
            if commodity not in commodity_positions:
                commodity_positions[commodity] = []
            commodity_positions[commodity].append(pos)
        
        return {
            "total_positions": len(open_positions),
            "total_notional_value": total_notional,
            "total_realized_pnl": total_pnl,
            "commodity_breakdown": {
                commodity: len(positions) for commodity, positions in commodity_positions.items()
            },
            "risk_level": self._calculate_portfolio_risk(open_positions)
        }
    
    def _calculate_position_risk(self, quantity: float, price: float) -> Dict[str, Any]:
        """
        Calculate risk metrics for position
        
        Args:
            quantity: Position quantity
            price: Position price
            
        Returns:
            Dict with risk metrics
        """
        # TODO: Implement proper risk calculations
        notional_value = quantity * price
        
        return {
            "notional_value": notional_value,
            "max_loss": notional_value * 0.15,  # 15% max loss stub
            "var_95": notional_value * 0.05,    # 5% VaR stub
            "risk_level": "high" if notional_value > 5000000 else "medium" if notional_value > 1000000 else "low"
        }
    
    def _calculate_portfolio_risk(self, positions: List[Dict[str, Any]]) -> str:
        """
        Calculate overall portfolio risk level
        
        Args:
            positions: List of positions
            
        Returns:
            Risk level string
        """
        # TODO: Implement proper portfolio risk calculation
        total_notional = sum(p["notional_value"] for p in positions)
        
        if total_notional > 10000000:  # $10M
            return "high"
        elif total_notional > 5000000:  # $5M
            return "medium"
        else:
            return "low"
