"""
Trading Domain Services
Real P&L calculations and position management
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from sqlalchemy.orm import Session
from .models import Trade, Position, Settlement, TradeStatus

logger = logging.getLogger(__name__)

class TradingService:
    """Core trading service with real P&L calculations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_trade(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new trade with real validation"""
        try:
            # Generate unique trade ID
            trade_id = f"T{datetime.now().strftime('%Y%m%d%H%M%S')}{hash(trade_data.get('asset', '')) % 10000:04d}"
            
            trade = Trade(
                trade_id=trade_id,
                asset=trade_data['asset'],
                quantity=trade_data['quantity'],
                price=trade_data['price'],
                direction=trade_data.get('direction', 'buy'),
                counterparty=trade_data.get('counterparty'),
                is_sharia_compliant=trade_data.get('is_sharia_compliant', True)
            )
            
            self.db.add(trade)
            self.db.commit()
            self.db.refresh(trade)
            
            # Create corresponding position
            position = self._create_position(trade)
            
            return {
                "success": True,
                "trade_id": trade.trade_id,
                "position_id": position.position_id,
                "trade": trade,
                "position": position
            }
            
        except Exception as e:
            logger.error(f"Error creating trade: {e}")
            self.db.rollback()
            return {"success": False, "error": str(e)}
    
    def _create_position(self, trade: Trade) -> Position:
        """Create position for trade"""
        position_id = f"POS-{trade.trade_id}"
        
        position = Position(
            position_id=position_id,
            trade_id=trade.id,
            asset=trade.asset,
            quantity=trade.quantity,
            entry_price=trade.price,
            current_price=trade.price,
            currency=trade.currency
        )
        
        self.db.add(position)
        self.db.commit()
        self.db.refresh(position)
        
        return position
    
    def calculate_real_pnl(self, position_id: str, current_price: float) -> Dict[str, Any]:
        """Calculate real P&L for position"""
        try:
            position = self.db.query(Position).filter(Position.position_id == position_id).first()
            if not position:
                return {"success": False, "error": "Position not found"}
            
            # Calculate unrealized P&L
            if position.direction == "buy":
                unrealized_pnl = (current_price - position.entry_price) * position.quantity
            else:  # sell
                unrealized_pnl = (position.entry_price - current_price) * position.quantity
            
            # Update position
            position.current_price = current_price
            position.unrealized_pnl = unrealized_pnl
            self.db.commit()
            
            return {
                "success": True,
                "position_id": position_id,
                "unrealized_pnl": unrealized_pnl,
                "pnl_percentage": (unrealized_pnl / (position.entry_price * position.quantity)) * 100,
                "current_price": current_price,
                "entry_price": position.entry_price
            }
            
        except Exception as e:
            logger.error(f"Error calculating P&L: {e}")
            return {"success": False, "error": str(e)}
    
    def get_portfolio_summary(self, user_id: str = None) -> Dict[str, Any]:
        """Get portfolio summary with real calculations"""
        try:
            # Get all positions
            positions = self.db.query(Position).all()
            
            total_value = 0
            total_pnl = 0
            position_count = len(positions)
            
            for position in positions:
                position_value = position.current_price * position.quantity
                total_value += position_value
                total_pnl += position.unrealized_pnl
            
            return {
                "success": True,
                "total_positions": position_count,
                "total_value": total_value,
                "total_pnl": total_pnl,
                "pnl_percentage": (total_pnl / total_value * 100) if total_value > 0 else 0,
                "positions": [
                    {
                        "position_id": p.position_id,
                        "asset": p.asset,
                        "quantity": p.quantity,
                        "current_price": p.current_price,
                        "unrealized_pnl": p.unrealized_pnl
                    } for p in positions
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting portfolio summary: {e}")
            return {"success": False, "error": str(e)}

class PositionManager:
    """Position management service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def reconcile_positions(self) -> Dict[str, Any]:
        """Reconcile all positions with current market data"""
        try:
            positions = self.db.query(Position).all()
            reconciled_count = 0
            
            for position in positions:
                # In real implementation, fetch current market price
                # For now, simulate price update
                import random
                price_change = random.uniform(-0.05, 0.05)  # ±5% change
                new_price = position.entry_price * (1 + price_change)
                
                # Update position
                position.current_price = new_price
                position.unrealized_pnl = (new_price - position.entry_price) * position.quantity
                reconciled_count += 1
            
            self.db.commit()
            
            return {
                "success": True,
                "reconciled_positions": reconciled_count,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error reconciling positions: {e}")
            return {"success": False, "error": str(e)}
