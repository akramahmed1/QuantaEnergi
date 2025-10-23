"""
Real Market Data API endpoints for ETRM/CTRM operations
Handles live energy commodity prices with Redis caching
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from ...services.real_market_data import market_data_service
from ...core.auth import get_current_user_mock as get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/market-data", tags=["market_data"])

@router.get("/prices/energy")
async def get_energy_prices(
    symbols: Optional[List[str]] = Query(None, description="Energy symbols (CL=F, NG=F, BZ=F, etc.)"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get real-time energy commodity prices
    
    Args:
        symbols: List of symbols to fetch (default: CL=F, NG=F)
        
    Returns:
        Real-time price data with caching
    """
    try:
        if symbols is None:
            symbols = ["CL=F", "NG=F"]  # Default to Brent and Natural Gas
        
        result = await market_data_service.fetch_energy_prices(symbols)
        
        logger.info(f"Energy prices fetched for {len(symbols)} symbols")
        return result
        
    except Exception as e:
        logger.error(f"Energy prices fetch failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch energy prices: {str(e)}")

@router.post("/prices/portfolio")
async def get_portfolio_prices(
    portfolio: List[Dict[str, Any]],
    current_user: Dict = Depends(get_current_user)
):
    """
    Get current prices for trading portfolio with P&L calculation
    
    Args:
        portfolio: List of positions with symbol, quantity, entry_price
        
    Returns:
        Portfolio pricing with unrealized P&L
    """
    try:
        result = await market_data_service.get_portfolio_prices(portfolio)
        
        logger.info(f"Portfolio prices calculated for {len(portfolio)} positions")
        return result
        
    except Exception as e:
        logger.error(f"Portfolio pricing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Portfolio pricing failed: {str(e)}")

@router.get("/prices/historical/{symbol}")
async def get_historical_prices(
    symbol: str,
    days: int = Query(30, ge=1, le=365, description="Number of days of history"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get historical price data for risk calculations
    
    Args:
        symbol: Energy symbol (CL=F, NG=F, etc.)
        days: Number of days of history (1-365)
        
    Returns:
        Historical price data for VaR calculations
    """
    try:
        result = await market_data_service.get_historical_prices(symbol, days)
        
        logger.info(f"Historical prices fetched for {symbol} ({days} days)")
        return result
        
    except Exception as e:
        logger.error(f"Historical prices fetch failed for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Historical prices fetch failed: {str(e)}")

@router.get("/prices/brent")
async def get_brent_price(current_user: Dict = Depends(get_current_user)):
    """
    Get current Brent crude oil price (CL=F)
    
    Returns:
        Current Brent price with change metrics
    """
    try:
        result = await market_data_service.fetch_energy_prices(["CL=F"])
        
        if "CL=F" in result.get("data", {}):
            brent_data = result["data"]["CL=F"]
            return {
                "symbol": "CL=F",
                "commodity": "Brent Crude Oil",
                "price": brent_data["price"],
                "change": brent_data["change"],
                "change_percent": brent_data["change_percent"],
                "volume": brent_data["volume"],
                "timestamp": brent_data["timestamp"],
                "source": brent_data["source"]
            }
        else:
            raise HTTPException(status_code=404, detail="Brent price data not available")
            
    except Exception as e:
        logger.error(f"Brent price fetch failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Brent price fetch failed: {str(e)}")

@router.get("/prices/natural-gas")
async def get_natural_gas_price(current_user: Dict = Depends(get_current_user)):
    """
    Get current Natural Gas price (NG=F)
    
    Returns:
        Current Natural Gas price with change metrics
    """
    try:
        result = await market_data_service.fetch_energy_prices(["NG=F"])
        
        if "NG=F" in result.get("data", {}):
            ng_data = result["data"]["NG=F"]
            return {
                "symbol": "NG=F",
                "commodity": "Natural Gas",
                "price": ng_data["price"],
                "change": ng_data["change"],
                "change_percent": ng_data["change_percent"],
                "volume": ng_data["volume"],
                "timestamp": ng_data["timestamp"],
                "source": ng_data["source"]
            }
        else:
            raise HTTPException(status_code=404, detail="Natural Gas price data not available")
            
    except Exception as e:
        logger.error(f"Natural Gas price fetch failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Natural Gas price fetch failed: {str(e)}")

@router.get("/cache/status")
async def get_cache_status(current_user: Dict = Depends(get_current_user)):
    """
    Get market data cache status and statistics
    
    Returns:
        Cache status and performance metrics
    """
    try:
        # Get cache statistics
        cache_stats = {
            "redis_available": market_data_service.redis_client is not None,
            "cache_ttl_seconds": market_data_service.cache_ttl,
            "memory_cache_size": len(market_data_service.memory_cache),
            "supported_symbols": list(market_data_service.energy_symbols.keys()),
            "service_version": market_data_service.service_version
        }
        
        return {
            "status": "success",
            "cache_stats": cache_stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Cache status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cache status check failed: {str(e)}")
