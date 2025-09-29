"""
Trade Engine - SOLID Design Pattern Implementation
Centralized trade processing with single responsibility principle
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class TradeValidator(ABC):
    """Abstract base class for trade validation"""
    
    @abstractmethod
    def validate(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

class REMITValidator(TradeValidator):
    """REMIT compliance validator"""
    
    def validate(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate trade against REMIT regulations"""
        volume = trade_data.get('quantity', 0)
        
        if volume > 1000:  # REMIT threshold
            return {
                'valid': False,
                'error': f'Volume {volume} exceeds REMIT threshold of 1000 bbl/day',
                'requires_acer_reporting': True
            }
        
        return {'valid': True, 'requires_acer_reporting': False}

class FERCValidator(TradeValidator):
    """FERC compliance validator"""
    
    def validate(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate trade against FERC regulations"""
        price = trade_data.get('price', 0)
        
        if price > 500:  # FERC price threshold
            return {
                'valid': False,
                'error': f'Price ${price} exceeds FERC threshold of $500',
                'requires_reporting': True
            }
        
        return {'valid': True, 'requires_reporting': False}

class TradeEngine:
    """
    SOLID Trade Engine - Single Responsibility for trade processing
    """
    
    def __init__(self):
        self.validators = {
            'REMIT': REMITValidator(),
            'FERC': FERCValidator()
        }
        self.trades = {}  # In-memory storage for demo
    
    def process_trade(self, trade_data: Dict[str, Any], 
                     compliance_framework: str = 'REMIT') -> Dict[str, Any]:
        """
        Process trade with compliance validation
        
        Args:
            trade_data: Trade information
            compliance_framework: Regulatory framework (REMIT/FERC)
            
        Returns:
            Processing result
        """
        try:
            # Validate trade
            validator = self.validators.get(compliance_framework)
            if not validator:
                return {
                    'success': False,
                    'error': f'Unknown compliance framework: {compliance_framework}'
                }
            
            validation_result = validator.validate(trade_data)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['error']
                }
            
            # Process trade
            trade_id = f"TRADE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            trade_data['trade_id'] = trade_id
            trade_data['status'] = 'captured'
            trade_data['timestamp'] = datetime.now().isoformat()
            
            self.trades[trade_id] = trade_data
            
            logger.info(f"Trade {trade_id} processed successfully")
            
            return {
                'success': True,
                'trade_id': trade_id,
                'trade': trade_data,
                'compliance': validation_result
            }
            
        except Exception as e:
            logger.error(f"Trade processing failed: {str(e)}")
            return {
                'success': False,
                'error': f'Processing failed: {str(e)}'
            }
    
    def get_trade(self, trade_id: str) -> Optional[Dict[str, Any]]:
        """Get trade by ID"""
        return self.trades.get(trade_id)
    
    def list_trades(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List trades with optional status filter"""
        trades = list(self.trades.values())
        if status:
            trades = [t for t in trades if t.get('status') == status]
        return trades
