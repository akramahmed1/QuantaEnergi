"""
Real P&L Calculation API endpoints for ETRM/CTRM operations
Handles qty*(exit-entry)*FX formula with position reconciliation
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from ...services.real_pnl_calculator import real_pnl_calculator
from ...core.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/real-pnl", tags=["real_pnl"])

@router.post("/calculate/trade")
async def calculate_trade_pnl(
    trade_data: Dict[str, Any] = Body(..., description="Trade data for P&L calculation"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Calculate P&L for a single trade using qty*(exit-entry)*FX formula
    
    Args:
        trade_data: Trade data with quantity, entry_price, exit_price, currency, direction
        
    Returns:
        Trade P&L calculation results
    """
    try:
        result = await real_pnl_calculator.calculate_trade_pnl(trade_data)
        
        logger.info(f"Trade P&L calculated for trade {trade_data.get('trade_id', 'unknown')}")
        return result
        
    except Exception as e:
        logger.error(f"Trade P&L calculation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Trade P&L calculation failed: {str(e)}")

@router.post("/calculate/portfolio")
async def calculate_portfolio_pnl(
    portfolio: List[Dict[str, Any]] = Body(..., description="Portfolio positions"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Calculate P&L for entire portfolio with position reconciliation
    
    Args:
        portfolio: List of positions with trade data
        
    Returns:
        Portfolio P&L results with reconciliation
    """
    try:
        result = await real_pnl_calculator.calculate_portfolio_pnl(portfolio)
        
        logger.info(f"Portfolio P&L calculated for {len(portfolio)} positions")
        return result
        
    except Exception as e:
        logger.error(f"Portfolio P&L calculation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Portfolio P&L calculation failed: {str(e)}")

@router.post("/mark-to-market")
async def calculate_mark_to_market_pnl(
    positions: List[Dict[str, Any]] = Body(..., description="Open positions"),
    current_prices: Dict[str, float] = Body(..., description="Current market prices by symbol"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Calculate mark-to-market P&L using current market prices
    
    Args:
        positions: List of open positions
        current_prices: Dict of current market prices by symbol
        
    Returns:
        Mark-to-market P&L results
    """
    try:
        result = await real_pnl_calculator.calculate_mark_to_market_pnl(positions, current_prices)
        
        logger.info(f"Mark-to-market P&L calculated for {len(positions)} positions")
        return result
        
    except Exception as e:
        logger.error(f"Mark-to-market P&L calculation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Mark-to-market P&L calculation failed: {str(e)}")

@router.post("/realized-unrealized")
async def calculate_realized_vs_unrealized_pnl(
    portfolio: List[Dict[str, Any]] = Body(..., description="Portfolio positions"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Calculate realized vs unrealized P&L breakdown
    
    Args:
        portfolio: List of positions
        
    Returns:
        Realized/unrealized P&L breakdown
    """
    try:
        result = await real_pnl_calculator.calculate_realized_vs_unrealized_pnl(portfolio)
        
        logger.info(f"Realized/unrealized P&L calculated for {len(portfolio)} positions")
        return result
        
    except Exception as e:
        logger.error(f"Realized/unrealized P&L calculation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Realized/unrealized P&L calculation failed: {str(e)}")

@router.get("/fx-rates")
async def get_fx_rates(current_user: Dict = Depends(get_current_user)):
    """
    Get current FX rates for P&L calculations
    
    Returns:
        Dict of FX rates
    """
    try:
        return {
            "status": "success",
            "fx_rates": real_pnl_calculator.fx_rates,
            "base_currency": "USD",
            "supported_currencies": list(real_pnl_calculator.fx_rates.keys()),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"FX rates fetch failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"FX rates fetch failed: {str(e)}")

@router.post("/validate-formula")
async def validate_pnl_formula(
    test_data: Dict[str, Any] = Body(..., description="Test data for formula validation"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Validate P&L calculation formula with test data
    
    Args:
        test_data: Test data with known expected results
        
    Returns:
        Formula validation results
    """
    try:
        # Test the formula: qty*(exit-entry)*FX
        quantity = test_data.get('quantity', 1000)
        entry_price = test_data.get('entry_price', 80.0)
        exit_price = test_data.get('exit_price', 85.0)
        currency = test_data.get('currency', 'USD')
        direction = test_data.get('direction', 'long')
        
        # Calculate using our service
        trade_data = {
            'quantity': quantity,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'currency': currency,
            'direction': direction
        }
        
        result = await real_pnl_calculator.calculate_trade_pnl(trade_data)
        
        if result['status'] == 'success':
            calculated_pnl = result['pnl_calculation']['pnl']
            
            # Manual calculation for validation
            fx_rate = real_pnl_calculator._get_fx_rate(currency)
            price_diff = exit_price - entry_price
            if direction == 'short':
                price_diff = -price_diff
            expected_pnl = quantity * price_diff * fx_rate
            
            # Validate formula
            formula_correct = abs(calculated_pnl - expected_pnl) < 0.01
            
            return {
                "status": "success",
                "formula_validation": {
                    "formula": "qty*(exit-entry)*FX",
                    "test_data": test_data,
                    "calculated_pnl": calculated_pnl,
                    "expected_pnl": expected_pnl,
                    "formula_correct": formula_correct,
                    "difference": abs(calculated_pnl - expected_pnl)
                },
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "error",
                "error": "P&L calculation failed",
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Formula validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Formula validation failed: {str(e)}")

@router.get("/formula/examples")
async def get_pnl_formula_examples(current_user: Dict = Depends(get_current_user)):
    """
    Get examples of P&L calculation formula usage
    
    Returns:
        Examples of P&L calculations
    """
    try:
        examples = [
            {
                "name": "Long Crude Oil Position",
                "description": "Buy 1000 barrels at $80, sell at $85",
                "formula": "qty*(exit-entry)*FX",
                "calculation": "1000 * (85 - 80) * 1.0 = $5,000",
                "test_data": {
                    "quantity": 1000,
                    "entry_price": 80.0,
                    "exit_price": 85.0,
                    "currency": "USD",
                    "direction": "long"
                }
            },
            {
                "name": "Short Natural Gas Position",
                "description": "Sell 5000 MMBtu at $3.50, buy back at $3.00",
                "formula": "qty*(exit-entry)*FX",
                "calculation": "5000 * (3.00 - 3.50) * 1.0 = -$2,500 (profit for short)",
                "test_data": {
                    "quantity": 5000,
                    "entry_price": 3.50,
                    "exit_price": 3.00,
                    "currency": "USD",
                    "direction": "short"
                }
            },
            {
                "name": "EUR Currency Position",
                "description": "Buy 1000 barrels at €70, sell at €75 (EUR base)",
                "formula": "qty*(exit-entry)*FX",
                "calculation": "1000 * (75 - 70) * 1.1 = $5,500",
                "test_data": {
                    "quantity": 1000,
                    "entry_price": 70.0,
                    "exit_price": 75.0,
                    "currency": "EUR",
                    "direction": "long"
                }
            }
        ]
        
        return {
            "status": "success",
            "formula": "qty*(exit-entry)*FX",
            "examples": examples,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Formula examples fetch failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Formula examples fetch failed: {str(e)}")
