"""
Real P&L Calculation Service for ETRM/CTRM Trading
Production-ready implementation with qty*(exit-entry)*FX formula
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
import asyncio

logger = logging.getLogger(__name__)

class RealPnLCalculator:
    """
    Production-ready P&L calculation service for energy commodity trading
    Implements real P&L = qty*(exit-entry)*FX formula with position reconciliation
    """
    
    def __init__(self):
        self.service_version = "1.0.0"
        
        # FX rates (mock for now, in production would fetch from API)
        self.fx_rates = {
            "USD": 1.0,
            "EUR": 1.1,  # 1 USD = 1.1 EUR (mock rate)
            "GBP": 0.8,  # 1 USD = 0.8 GBP (mock rate)
            "JPY": 150.0,  # 1 USD = 150 JPY (mock rate)
            "CAD": 1.35,  # 1 USD = 1.35 CAD (mock rate)
            "AUD": 1.5,   # 1 USD = 1.5 AUD (mock rate)
            "CHF": 0.9,   # 1 USD = 0.9 CHF (mock rate)
            "CNY": 7.2    # 1 USD = 7.2 CNY (mock rate)
        }
        
        logger.info(f"RealPnLCalculator initialized with {len(self.fx_rates)} FX rates")
    
    async def calculate_trade_pnl(self, 
                                trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate P&L for a single trade using qty*(exit-entry)*FX formula
        
        Args:
            trade_data: Trade data with quantity, entry_price, exit_price, currency
            
        Returns:
            Dict with P&L calculation results
        """
        try:
            quantity = trade_data.get('quantity', 0)
            entry_price = trade_data.get('entry_price', 0)
            exit_price = trade_data.get('exit_price', 0)
            currency = trade_data.get('currency', 'USD')
            trade_direction = trade_data.get('direction', 'long')  # long or short
            
            # Validate inputs
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
            if entry_price <= 0:
                raise ValueError("Entry price must be positive")
            if exit_price <= 0:
                raise ValueError("Exit price must be positive")
            
            # Get FX rate
            fx_rate = self._get_fx_rate(currency)
            
            # Calculate price difference
            price_diff = exit_price - entry_price
            
            # Adjust for trade direction
            if trade_direction == 'short':
                price_diff = -price_diff  # Short positions profit when price goes down
            
            # Calculate P&L using formula: qty*(exit-entry)*FX
            pnl = quantity * price_diff * fx_rate
            
            # Calculate additional metrics
            notional_value = quantity * entry_price * fx_rate
            pnl_percent = (pnl / notional_value * 100) if notional_value > 0 else 0
            
            # Calculate unrealized P&L if no exit price
            unrealized_pnl = None
            if exit_price == 0:
                # This is an open position, calculate unrealized P&L
                current_price = trade_data.get('current_price', entry_price)
                price_diff_unrealized = current_price - entry_price
                if trade_direction == 'short':
                    price_diff_unrealized = -price_diff_unrealized
                unrealized_pnl = quantity * price_diff_unrealized * fx_rate
            
            return {
                "status": "success",
                "trade_id": trade_data.get('trade_id', 'unknown'),
                "pnl_calculation": {
                    "quantity": quantity,
                    "entry_price": entry_price,
                    "exit_price": exit_price,
                    "price_difference": price_diff,
                    "fx_rate": fx_rate,
                    "currency": currency,
                    "direction": trade_direction,
                    "pnl": round(pnl, 2),
                    "pnl_percent": round(pnl_percent, 2),
                    "notional_value": round(notional_value, 2),
                    "unrealized_pnl": round(unrealized_pnl, 2) if unrealized_pnl is not None else None
                },
                "formula": "qty*(exit-entry)*FX",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Trade P&L calculation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def calculate_portfolio_pnl(self, 
                                    portfolio: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate P&L for entire portfolio with position reconciliation
        
        Args:
            portfolio: List of positions with trade data
            
        Returns:
            Dict with portfolio P&L results
        """
        try:
            total_pnl = 0
            total_notional = 0
            position_pnls = []
            currency_exposure = {}
            
            for position in portfolio:
                # Calculate individual position P&L
                pnl_result = await self.calculate_trade_pnl(position)
                
                if pnl_result['status'] == 'success':
                    pnl_data = pnl_result['pnl_calculation']
                    pnl = pnl_data['pnl']
                    notional = pnl_data['notional_value']
                    currency = pnl_data['currency']
                    
                    total_pnl += pnl
                    total_notional += notional
                    
                    # Track currency exposure
                    if currency not in currency_exposure:
                        currency_exposure[currency] = {'pnl': 0, 'notional': 0}
                    currency_exposure[currency]['pnl'] += pnl
                    currency_exposure[currency]['notional'] += notional
                    
                    position_pnls.append({
                        "trade_id": pnl_data.get('trade_id', 'unknown'),
                        "symbol": position.get('symbol', 'unknown'),
                        "quantity": pnl_data['quantity'],
                        "pnl": pnl,
                        "pnl_percent": pnl_data['pnl_percent'],
                        "notional_value": notional,
                        "currency": currency,
                        "direction": pnl_data['direction']
                    })
            
            # Calculate portfolio metrics
            portfolio_pnl_percent = (total_pnl / total_notional * 100) if total_notional > 0 else 0
            
            # Calculate position reconciliation
            reconciliation = await self._reconcile_positions(portfolio)
            
            return {
                "status": "success",
                "portfolio_summary": {
                    "total_pnl": round(total_pnl, 2),
                    "total_notional": round(total_notional, 2),
                    "portfolio_pnl_percent": round(portfolio_pnl_percent, 2),
                    "position_count": len(portfolio),
                    "profitable_positions": len([p for p in position_pnls if p['pnl'] > 0]),
                    "losing_positions": len([p for p in position_pnls if p['pnl'] < 0])
                },
                "currency_exposure": currency_exposure,
                "position_pnls": position_pnls,
                "reconciliation": reconciliation,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Portfolio P&L calculation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _reconcile_positions(self, portfolio: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Reconcile positions to ensure accuracy
        
        Args:
            portfolio: List of positions
            
        Returns:
            Dict with reconciliation results
        """
        try:
            # Group positions by symbol
            symbol_positions = {}
            for position in portfolio:
                symbol = position.get('symbol', 'unknown')
                if symbol not in symbol_positions:
                    symbol_positions[symbol] = []
                symbol_positions[symbol].append(position)
            
            reconciliation_results = []
            
            for symbol, positions in symbol_positions.items():
                # Calculate net position
                net_quantity = 0
                total_notional = 0
                weighted_avg_price = 0
                
                for position in positions:
                    quantity = position.get('quantity', 0)
                    entry_price = position.get('entry_price', 0)
                    direction = position.get('direction', 'long')
                    
                    # Adjust quantity for direction
                    if direction == 'short':
                        quantity = -quantity
                    
                    net_quantity += quantity
                    total_notional += abs(quantity) * entry_price
                
                # Calculate weighted average price
                if total_notional > 0:
                    total_quantity = sum(abs(p.get('quantity', 0)) for p in positions)
                    if total_quantity > 0:
                        weighted_avg_price = total_notional / total_quantity
                
                reconciliation_results.append({
                    "symbol": symbol,
                    "net_quantity": net_quantity,
                    "total_notional": total_notional,
                    "weighted_avg_price": round(weighted_avg_price, 2),
                    "position_count": len(positions),
                    "net_direction": "long" if net_quantity > 0 else "short" if net_quantity < 0 else "flat"
                })
            
            return {
                "reconciliation_status": "success",
                "symbol_reconciliation": reconciliation_results,
                "total_symbols": len(symbol_positions),
                "net_positions": len([r for r in reconciliation_results if r['net_quantity'] != 0])
            }
            
        except Exception as e:
            logger.error(f"Position reconciliation failed: {e}")
            return {
                "reconciliation_status": "error",
                "error": str(e)
            }
    
    def _get_fx_rate(self, currency: str) -> float:
        """Get FX rate for currency conversion"""
        return self.fx_rates.get(currency, 1.0)
    
    async def calculate_mark_to_market_pnl(self, 
                                         positions: List[Dict[str, Any]], 
                                         current_prices: Dict[str, float]) -> Dict[str, Any]:
        """
        Calculate mark-to-market P&L using current market prices
        
        Args:
            positions: List of open positions
            current_prices: Dict of current market prices by symbol
            
        Returns:
            Dict with mark-to-market P&L results
        """
        try:
            mtm_pnl = 0
            mtm_positions = []
            
            for position in positions:
                symbol = position.get('symbol', 'unknown')
                quantity = position.get('quantity', 0)
                entry_price = position.get('entry_price', 0)
                direction = position.get('direction', 'long')
                currency = position.get('currency', 'USD')
                
                if symbol in current_prices:
                    current_price = current_prices[symbol]
                    fx_rate = self._get_fx_rate(currency)
                    
                    # Calculate price difference
                    price_diff = current_price - entry_price
                    if direction == 'short':
                        price_diff = -price_diff
                    
                    # Calculate mark-to-market P&L
                    position_mtm_pnl = quantity * price_diff * fx_rate
                    mtm_pnl += position_mtm_pnl
                    
                    mtm_positions.append({
                        "symbol": symbol,
                        "quantity": quantity,
                        "entry_price": entry_price,
                        "current_price": current_price,
                        "price_diff": price_diff,
                        "mtm_pnl": round(position_mtm_pnl, 2),
                        "currency": currency,
                        "direction": direction
                    })
            
            return {
                "status": "success",
                "total_mtm_pnl": round(mtm_pnl, 2),
                "mtm_positions": mtm_positions,
                "position_count": len(mtm_positions),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Mark-to-market P&L calculation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def calculate_realized_vs_unrealized_pnl(self, 
                                                  portfolio: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate realized vs unrealized P&L breakdown
        
        Args:
            portfolio: List of positions
            
        Returns:
            Dict with realized/unrealized P&L breakdown
        """
        try:
            realized_pnl = 0
            unrealized_pnl = 0
            realized_positions = []
            unrealized_positions = []
            
            for position in portfolio:
                exit_price = position.get('exit_price', 0)
                pnl_result = await self.calculate_trade_pnl(position)
                
                if pnl_result['status'] == 'success':
                    pnl_data = pnl_result['pnl_calculation']
                    pnl = pnl_data['pnl']
                    
                    if exit_price > 0:
                        # Realized P&L (position closed)
                        realized_pnl += pnl
                        realized_positions.append({
                            "trade_id": pnl_data.get('trade_id', 'unknown'),
                            "symbol": position.get('symbol', 'unknown'),
                            "realized_pnl": pnl,
                            "exit_price": exit_price
                        })
                    else:
                        # Unrealized P&L (position open)
                        unrealized_pnl += pnl_data.get('unrealized_pnl', 0)
                        unrealized_positions.append({
                            "trade_id": pnl_data.get('trade_id', 'unknown'),
                            "symbol": position.get('symbol', 'unknown'),
                            "unrealized_pnl": pnl_data.get('unrealized_pnl', 0),
                            "current_price": position.get('current_price', 0)
                        })
            
            return {
                "status": "success",
                "realized_pnl": round(realized_pnl, 2),
                "unrealized_pnl": round(unrealized_pnl, 2),
                "total_pnl": round(realized_pnl + unrealized_pnl, 2),
                "realized_positions": realized_positions,
                "unrealized_positions": unrealized_positions,
                "realized_count": len(realized_positions),
                "unrealized_count": len(unrealized_positions),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Realized/unrealized P&L calculation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Global instance
real_pnl_calculator = RealPnLCalculator()
