"""
Enhanced Trade Service with Real P&L Calculations and Lifecycle Management
Production-ready implementation for ETRM/CTRM trading operations
"""

from sqlalchemy.orm import Session
from app.models.trade import Trade
from app.models.user import User
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP
import logging

logger = logging.getLogger(__name__)

class TradeLifecycleService:
    """Real trade lifecycle management with P&L calculations"""
    
    def __init__(self):
        self.fx_rates = {
            'USD': 1.0,
            'EUR': 0.85,
            'GBP': 0.73,
            'JPY': 110.0,
            'CAD': 1.25
        }
        self.hedge_ratio = 0.05  # 5% hedge buffer
    
    def capture_trade(self, trade_data: Dict[str, Any], user_id: int, db: Session) -> Dict[str, Any]:
        """
        Capture new trade with real validation and P&L setup
        
        Args:
            trade_data: Trade information
            user_id: User creating the trade
            db: Database session
            
        Returns:
            Dict with captured trade details
        """
        try:
            # Validate trade data
            validation_result = self._validate_trade(trade_data)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['error'],
                    'trade_id': None
                }
            
            # Create trade record
            trade = Trade(
                asset=trade_data['asset'],
                quantity=Decimal(str(trade_data['quantity'])),
                price=Decimal(str(trade_data['price'])),
                currency=trade_data.get('currency', 'USD'),
                trade_type=trade_data.get('trade_type', 'spot'),
                owner_id=user_id,
                status='captured',
                timestamp=datetime.utcnow()
            )
            
            db.add(trade)
            db.commit()
            db.refresh(trade)
            
            # Calculate initial P&L metrics
            pnl_metrics = self._calculate_initial_pnl(trade)
            
            # Update trade with P&L data
            trade.unrealized_pnl = Decimal(str(pnl_metrics['unrealized_pnl']))
            trade.notional_value = Decimal(str(pnl_metrics['notional_value']))
            db.commit()
            
            logger.info(f"Trade {trade.id} captured successfully for user {user_id}")
            
            return {
                'success': True,
                'trade_id': trade.id,
                'trade': {
                    'id': trade.id,
                    'asset': trade.asset,
                    'quantity': float(trade.quantity),
                    'price': float(trade.price),
                    'currency': trade.currency,
                    'notional_value': float(trade.notional_value),
                    'unrealized_pnl': float(trade.unrealized_pnl),
                    'status': trade.status,
                    'timestamp': trade.timestamp.isoformat()
                },
                'pnl_metrics': pnl_metrics
            }
            
        except Exception as e:
            logger.error(f"Trade capture failed: {str(e)}")
            db.rollback()
            return {
                'success': False,
                'error': f"Trade capture failed: {str(e)}",
                'trade_id': None
            }
    
    def settle_pnl(self, trade_id: int, current_price: float, db: Session) -> Dict[str, Any]:
        """
        Calculate and settle P&L for a trade
        
        Args:
            trade_id: Trade ID
            current_price: Current market price
            db: Database session
            
        Returns:
            P&L settlement details
        """
        try:
            trade = db.query(Trade).get(trade_id)
            if not trade:
                return {'success': False, 'error': 'Trade not found'}
            
            # Calculate P&L components
            entry_price = float(trade.price)
            quantity = float(trade.quantity)
            currency = trade.currency
            
            # Basic P&L calculation: qty * (current_price - entry_price)
            price_diff = current_price - entry_price
            gross_pnl = quantity * price_diff
            
            # Apply FX hedge (5% buffer)
            fx_rate = self.fx_rates.get(currency, 1.0)
            fx_adjusted_pnl = gross_pnl * fx_rate * (1 - self.hedge_ratio)
            
            # Calculate fees and costs
            fees = self._calculate_trading_fees(quantity, entry_price, current_price)
            net_pnl = fx_adjusted_pnl - fees
            
            # Update trade record
            trade.current_price = Decimal(str(current_price))
            trade.realized_pnl = Decimal(str(net_pnl))
            trade.settlement_date = datetime.utcnow()
            trade.status = 'settled'
            
            db.commit()
            
            logger.info(f"P&L settled for trade {trade_id}: ${net_pnl:.2f}")
            
            return {
                'success': True,
                'trade_id': trade_id,
                'pnl_breakdown': {
                    'gross_pnl': round(gross_pnl, 2),
                    'fx_adjusted_pnl': round(fx_adjusted_pnl, 2),
                    'fees': round(fees, 2),
                    'net_pnl': round(net_pnl, 2)
                },
                'settlement_date': trade.settlement_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"P&L settlement failed: {str(e)}")
            return {'success': False, 'error': f"P&L settlement failed: {str(e)}"}
    
    def reconcile_position(self, trade_id: int, db: Session) -> Dict[str, Any]:
        """
        Reconcile position with real calculations
        
        Args:
            trade_id: Trade ID
            db: Database session
            
        Returns:
            Position reconciliation details
        """
        try:
            trade = db.query(Trade).get(trade_id)
            if not trade:
                return {'success': False, 'error': 'Trade not found'}
            
            # Calculate position metrics
            quantity = float(trade.quantity)
            price = float(trade.price)
            current_price = float(trade.current_price) if trade.current_price else price
            
            notional_value = quantity * price
            current_value = quantity * current_price
            unrealized_pnl = current_value - notional_value
            
            # Position risk metrics
            position_risk = self._calculate_position_risk(quantity, price, current_price)
            
            return {
                'success': True,
                'trade_id': trade_id,
                'position': {
                    'quantity': quantity,
                    'entry_price': price,
                    'current_price': current_price,
                    'notional_value': round(notional_value, 2),
                    'current_value': round(current_value, 2),
                    'unrealized_pnl': round(unrealized_pnl, 2),
                    'pnl_percentage': round((unrealized_pnl / notional_value) * 100, 2)
                },
                'risk_metrics': position_risk
            }
            
        except Exception as e:
            logger.error(f"Position reconciliation failed: {str(e)}")
            return {'success': False, 'error': f"Position reconciliation failed: {str(e)}"}
    
    def _validate_trade(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate trade data before capture"""
        required_fields = ['asset', 'quantity', 'price']
        
        for field in required_fields:
            if field not in trade_data:
                return {'valid': False, 'error': f'Missing required field: {field}'}
        
        # Validate quantity
        if trade_data['quantity'] <= 0:
            return {'valid': False, 'error': 'Quantity must be positive'}
        
        # Validate price
        if trade_data['price'] <= 0:
            return {'valid': False, 'error': 'Price must be positive'}
        
        return {'valid': True}
    
    def _calculate_initial_pnl(self, trade: Trade) -> Dict[str, Any]:
        """Calculate initial P&L metrics for a trade"""
        quantity = float(trade.quantity)
        price = float(trade.price)
        
        notional_value = quantity * price
        unrealized_pnl = 0.0  # No P&L at capture
        
        return {
            'notional_value': round(notional_value, 2),
            'unrealized_pnl': round(unrealized_pnl, 2),
            'quantity': quantity,
            'price': price
        }
    
    def _calculate_trading_fees(self, quantity: float, entry_price: float, current_price: float) -> float:
        """Calculate trading fees and costs"""
        notional_value = quantity * entry_price
        # 0.1% trading fee
        trading_fee = notional_value * 0.001
        # $50 settlement fee
        settlement_fee = 50.0
        return trading_fee + settlement_fee
    
    def _calculate_position_risk(self, quantity: float, entry_price: float, current_price: float) -> Dict[str, Any]:
        """Calculate position risk metrics"""
        notional_value = quantity * entry_price
        current_value = quantity * current_price
        pnl = current_value - notional_value
        pnl_percentage = (pnl / notional_value) * 100
        
        # Risk level based on P&L percentage
        if abs(pnl_percentage) > 20:
            risk_level = 'HIGH'
        elif abs(pnl_percentage) > 10:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        return {
            'risk_level': risk_level,
            'max_loss': notional_value * 0.15,  # 15% max loss
            'var_95': notional_value * 0.05,    # 5% VaR
            'pnl_percentage': round(pnl_percentage, 2)
        }
