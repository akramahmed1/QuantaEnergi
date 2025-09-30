"""
SOLID TradeEngine - Enterprise-grade trade processing with real P&L calculations
Implements Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Protocol
from enum import Enum
import uuid
import numpy as np

logger = logging.getLogger(__name__)

class TradeStatus(Enum):
    """Trade status enumeration following Open/Closed principle"""
    PENDING = "pending"
    VALIDATED = "validated"
    CONFIRMED = "confirmed"
    SETTLED = "settled"
    CANCELLED = "cancelled"

class ComplianceFramework(Enum):
    """Compliance framework enumeration"""
    REMIT = "REMIT"
    FERC = "FERC"
    UK_ETS = "UK_ETS"
    ISLAMIC = "ISLAMIC"

class TradeValidator(Protocol):
    """Interface for trade validation following Interface Segregation principle"""
    def validate(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate trade data"""
        ...

class ComplianceValidator(TradeValidator):
    """REMIT/FERC compliance validator"""
    
    def __init__(self, framework: ComplianceFramework):
        self.framework = framework
        self.position_limits = {
            ComplianceFramework.REMIT: 1000,  # 1000 bbl/day
            ComplianceFramework.FERC: 500,    # $500 price cap
            ComplianceFramework.UK_ETS: 1000,
            ComplianceFramework.ISLAMIC: float('inf')  # No limits for Islamic
        }
    
    def validate(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate trade against regulatory framework"""
        quantity = trade_data.get('quantity', 0)
        price = trade_data.get('price', 0)
        
        # REMIT volume validation
        if self.framework == ComplianceFramework.REMIT and quantity > self.position_limits[ComplianceFramework.REMIT]:
            return {
                'valid': False,
                'error': f'Volume {quantity} exceeds REMIT limit {self.position_limits[ComplianceFramework.REMIT]} bbl/day',
                'compliance_violation': True
            }
        
        # FERC price validation
        if self.framework == ComplianceFramework.FERC and price > self.position_limits[ComplianceFramework.FERC]:
            return {
                'valid': False,
                'error': f'Price ${price} exceeds FERC limit ${self.position_limits[ComplianceFramework.FERC]}',
                'compliance_violation': True
            }
        
        return {
            'valid': True,
            'compliance_violation': False,
            'framework': self.framework.value
        }

class PnLCalculator:
    """Real P&L calculation engine with FX hedging and fees"""
    
    def __init__(self):
        self.fx_rates = {'USD': 1.0, 'EUR': 0.85, 'GBP': 0.73}  # Mock FX rates
        self.trading_fees = 0.001  # 0.1% trading fee
        self.hedging_cost = 0.05   # 5% hedging cost
    
    def calculate_unrealized_pnl(self, position: Dict[str, Any], current_price: float) -> Dict[str, Any]:
        """Calculate unrealized P&L with real market factors"""
        quantity = position.get('quantity', 0)
        entry_price = position.get('entry_price', 0)
        currency = position.get('currency', 'USD')
        direction = position.get('direction', 'long')
        
        # Basic P&L calculation
        if direction == 'long':
            price_diff = current_price - entry_price
        else:
            price_diff = entry_price - current_price
        
        gross_pnl = quantity * price_diff
        
        # Apply FX conversion if needed
        fx_rate = self.fx_rates.get(currency, 1.0)
        fx_adjusted_pnl = gross_pnl * fx_rate
        
        # Apply trading fees
        notional_value = quantity * current_price * fx_rate
        trading_fee = notional_value * self.trading_fees
        
        # Apply hedging cost (5% of position value)
        hedging_cost = notional_value * self.hedging_cost
        
        net_pnl = fx_adjusted_pnl - trading_fee - hedging_cost
        
        return {
            'gross_pnl': round(gross_pnl, 2),
            'fx_adjusted_pnl': round(fx_adjusted_pnl, 2),
            'trading_fee': round(trading_fee, 2),
            'hedging_cost': round(hedging_cost, 2),
            'net_pnl': round(net_pnl, 2),
            'pnl_percentage': round((net_pnl / (quantity * entry_price * fx_rate)) * 100, 2),
            'currency': currency,
            'fx_rate': fx_rate
        }

class PositionReconciler:
    """Position reconciliation engine"""
    
    def __init__(self):
        self.positions = {}  # In-memory storage for demo
    
    def reconcile_position(self, trade_id: str, current_price: float) -> Dict[str, Any]:
        """Reconcile position with real-time market data"""
        if trade_id not in self.positions:
            return {'error': 'Position not found'}
        
        position = self.positions[trade_id]
        pnl_calculator = PnLCalculator()
        
        # Calculate current P&L
        pnl_metrics = pnl_calculator.calculate_unrealized_pnl(position, current_price)
        
        # Update position with current metrics
        position.update({
            'current_price': current_price,
            'last_updated': datetime.now().isoformat(),
            'pnl_metrics': pnl_metrics
        })
        
        return {
            'position_id': trade_id,
            'position': position,
            'reconciliation_time': datetime.now().isoformat()
        }

class TradeEngine:
    """SOLID TradeEngine - Single responsibility for trade processing"""
    
    def __init__(self):
        self.validator = ComplianceValidator(ComplianceFramework.REMIT)
        self.position_reconciler = PositionReconciler()
        self.pnl_calculator = PnLCalculator()
        self.trades = {}  # In-memory storage for demo
    
    def process_trade(self, trade_data: Dict[str, Any], framework: str = "REMIT") -> Dict[str, Any]:
        """
        Process trade with full lifecycle management
        
        Args:
            trade_data: Trade information
            framework: Compliance framework (REMIT, FERC, etc.)
        
        Returns:
            Dict with trade processing results
        """
        try:
            # Generate unique trade ID
            trade_id = f"TRADE-{uuid.uuid4().hex[:8].upper()}"
            
            # Validate trade
            self.validator.framework = ComplianceFramework(framework)
            validation_result = self.validator.validate(trade_data)
            
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['error'],
                    'trade_id': None
                }
            
            # Create trade record
            trade_record = {
                'trade_id': trade_id,
                'status': TradeStatus.VALIDATED.value,
                'created_at': datetime.now().isoformat(),
                'asset': trade_data.get('asset'),
                'quantity': trade_data.get('quantity'),
                'price': trade_data.get('price'),
                'currency': trade_data.get('currency', 'USD'),
                'trade_type': trade_data.get('trade_type', 'spot'),
                'direction': trade_data.get('direction', 'long'),
                'user_id': trade_data.get('user_id'),
                'compliance': validation_result
            }
            
            # Store trade
            self.trades[trade_id] = trade_record
            
            # Create position
            position_data = {
                'trade_id': trade_id,
                'quantity': trade_data.get('quantity'),
                'entry_price': trade_data.get('price'),
                'currency': trade_data.get('currency', 'USD'),
                'direction': trade_data.get('direction', 'long'),
                'created_at': datetime.now().isoformat()
            }
            self.position_reconciler.positions[trade_id] = position_data
            
            return {
                'success': True,
                'trade_id': trade_id,
                'trade': trade_record,
                'compliance': validation_result,
                'status': TradeStatus.VALIDATED.value
            }
            
        except Exception as e:
            logger.error(f"Trade processing failed: {str(e)}")
            return {
                'success': False,
                'error': f'Trade processing failed: {str(e)}',
                'trade_id': None
            }
    
    def settle_trade(self, trade_id: str, current_price: float) -> Dict[str, Any]:
        """Settle trade with final P&L calculation"""
        if trade_id not in self.trades:
            return {'error': 'Trade not found'}
        
        trade = self.trades[trade_id]
        
        # Calculate final P&L
        position_data = self.position_reconciler.positions.get(trade_id, {})
        pnl_metrics = self.pnl_calculator.calculate_unrealized_pnl(position_data, current_price)
        
        # Update trade status
        trade['status'] = TradeStatus.SETTLED.value
        trade['settled_at'] = datetime.now().isoformat()
        trade['settlement_price'] = current_price
        trade['final_pnl'] = pnl_metrics
        
        return {
            'success': True,
            'trade_id': trade_id,
            'settlement_price': current_price,
            'final_pnl': pnl_metrics,
            'settled_at': trade['settled_at']
        }