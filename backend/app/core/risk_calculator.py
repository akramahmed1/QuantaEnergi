"""
Risk Calculator - SOLID Design Pattern Implementation
Centralized risk calculations with single responsibility principle
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class RiskMethod(ABC):
    """Abstract base class for risk calculation methods"""
    
    @abstractmethod
    def calculate(self, positions: List[Dict[str, Any]], 
                  confidence_level: float = 0.95) -> Dict[str, Any]:
        pass

class HistoricalVaR(RiskMethod):
    """Historical Value at Risk calculation"""
    
    def calculate(self, positions: List[Dict[str, Any]], 
                  confidence_level: float = 0.95) -> Dict[str, Any]:
        """Calculate VaR using historical simulation"""
        if not positions:
            return {'var': 0.0, 'method': 'historical', 'confidence': confidence_level}
        
        # Extract price changes
        price_changes = []
        for position in positions:
            if 'price_history' in position:
                prices = position['price_history']
                if len(prices) > 1:
                    changes = np.diff(prices) / prices[:-1]
                    price_changes.extend(changes)
        
        if not price_changes:
            return {'var': 0.0, 'method': 'historical', 'confidence': confidence_level}
        
        # Calculate VaR
        var_percentile = (1 - confidence_level) * 100
        var_value = np.percentile(price_changes, var_percentile)
        
        return {
            'var': float(var_value),
            'method': 'historical',
            'confidence': confidence_level,
            'calculated_at': datetime.now().isoformat()
        }

class MonteCarloVaR(RiskMethod):
    """Monte Carlo Value at Risk calculation"""
    
    def calculate(self, positions: List[Dict[str, Any]], 
                  confidence_level: float = 0.95,
                  num_simulations: int = 10000) -> Dict[str, Any]:
        """Calculate VaR using Monte Carlo simulation"""
        if not positions:
            return {'var': 0.0, 'method': 'monte_carlo', 'confidence': confidence_level}
        
        # Extract position data
        total_value = sum(pos.get('notional_value', 0) for pos in positions)
        if total_value == 0:
            return {'var': 0.0, 'method': 'monte_carlo', 'confidence': confidence_level}
        
        # Generate random returns (normal distribution)
        np.random.seed(42)  # For reproducibility
        returns = np.random.normal(0, 0.02, num_simulations)  # 2% daily volatility
        
        # Calculate portfolio values
        portfolio_values = total_value * (1 + returns)
        
        # Calculate VaR
        var_percentile = (1 - confidence_level) * 100
        var_value = np.percentile(portfolio_values, var_percentile)
        var_amount = total_value - var_value
        
        return {
            'var': float(var_amount),
            'var_percentage': float(var_amount / total_value * 100),
            'method': 'monte_carlo',
            'confidence': confidence_level,
            'simulations': num_simulations,
            'calculated_at': datetime.now().isoformat()
        }

class RiskCalculator:
    """
    SOLID Risk Calculator - Single Responsibility for risk calculations
    """
    
    def __init__(self):
        self.methods = {
            'historical': HistoricalVaR(),
            'monte_carlo': MonteCarloVaR()
        }
    
    def calculate_var(self, positions: List[Dict[str, Any]], 
                     method: str = 'monte_carlo',
                     confidence_level: float = 0.95,
                     **kwargs) -> Dict[str, Any]:
        """
        Calculate Value at Risk using specified method
        
        Args:
            positions: List of trading positions
            method: VaR calculation method (historical/monte_carlo)
            confidence_level: VaR confidence level
            **kwargs: Additional method-specific parameters
            
        Returns:
            VaR calculation result
        """
        try:
            risk_method = self.methods.get(method)
            if not risk_method:
                return {
                    'success': False,
                    'error': f'Unknown risk method: {method}'
                }
            
            result = risk_method.calculate(positions, confidence_level, **kwargs)
            result['success'] = True
            
            logger.info(f"VaR calculated using {method} method: {result.get('var', 0)}")
            
            return result
            
        except Exception as e:
            logger.error(f"VaR calculation failed: {str(e)}")
            return {
                'success': False,
                'error': f'VaR calculation failed: {str(e)}'
            }
    
    def calculate_portfolio_risk(self, positions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate comprehensive portfolio risk metrics"""
        try:
            if not positions:
                return {
                    'success': True,
                    'total_value': 0,
                    'risk_metrics': {}
                }
            
            total_value = sum(pos.get('notional_value', 0) for pos in positions)
            
            # Calculate various risk metrics
            risk_metrics = {
                'total_value': total_value,
                'position_count': len(positions),
                'concentration_risk': self._calculate_concentration_risk(positions),
                'liquidity_risk': self._calculate_liquidity_risk(positions)
            }
            
            return {
                'success': True,
                'total_value': total_value,
                'risk_metrics': risk_metrics,
                'calculated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Portfolio risk calculation failed: {str(e)}")
            return {
                'success': False,
                'error': f'Portfolio risk calculation failed: {str(e)}'
            }
    
    def _calculate_concentration_risk(self, positions: List[Dict[str, Any]]) -> float:
        """Calculate concentration risk (Herfindahl index)"""
        if not positions:
            return 0.0
        
        values = [pos.get('notional_value', 0) for pos in positions]
        total = sum(values)
        if total == 0:
            return 0.0
        
        # Calculate Herfindahl index
        weights = [v / total for v in values]
        herfindahl = sum(w**2 for w in weights)
        
        return float(herfindahl)
    
    def _calculate_liquidity_risk(self, positions: List[Dict[str, Any]]) -> float:
        """Calculate liquidity risk based on position sizes"""
        if not positions:
            return 0.0
        
        # Simple liquidity risk based on position size distribution
        values = [pos.get('notional_value', 0) for pos in positions]
        if not values:
            return 0.0
        
        # Calculate coefficient of variation as liquidity risk proxy
        mean_value = np.mean(values)
        std_value = np.std(values)
        
        if mean_value == 0:
            return 0.0
        
        return float(std_value / mean_value)
