from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from ...services.market_data_normalizer import market_data_normalizer, MarketDataType, DataSource
from ...core.security import get_current_active_user
from ...models.user import User

router = APIRouter()

class NormalizeMarketDataRequest(BaseModel):
    raw_data: Dict[str, Any] = Field(..., example={"price": 75.50, "currency": "USD", "timestamp": 1640995200})
    data_type: str = Field(..., example="price", description="Type of market data (price, volume, volatility, fundamental, technical)")
    source: str = Field(..., example="yahoo_finance", description="Data source (yahoo_finance, bloomberg, refinitiv, mock)")

class GetMarketDataRequest(BaseModel):
    symbol: str = Field(..., example="CL=F", description="Market symbol (e.g., CL=F for crude oil futures)")
    data_type: str = Field(..., example="price", description="Type of data to retrieve")
    source: Optional[str] = Field(None, example="yahoo_finance", description="Optional source filter")

class GetMarketDataFeedRequest(BaseModel):
    symbols: List[str] = Field(..., example=["CL=F", "NG=F", "HO=F"], description="List of market symbols")
    data_types: List[str] = Field(..., example=["price", "volume"], description="List of data types to retrieve")
    sources: Optional[List[str]] = Field(None, example=["yahoo_finance", "bloomberg"], description="Optional list of sources to filter by")

class StartDataFeedRequest(BaseModel):
    symbol: str = Field(..., example="CL=F", description="Market symbol")
    data_type: str = Field(..., example="price", description="Type of data to feed")
    source: str = Field(..., example="yahoo_finance", description="Data source")
    frequency: int = Field(default=60, ge=10, le=3600, example=60, description="Update frequency in seconds (10-3600)")

@router.post("/market/feed", summary="Normalize market data from various sources")
async def normalize_market_data_endpoint(
    request: NormalizeMarketDataRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Normalizes market data from various sources (Yahoo Finance, Bloomberg, Refinitiv, etc.).
    Requires 'market_data:write' permission.
    """
    # TODO: Add permission check for current_user
    try:
        result = await market_data_normalizer.normalize_market_data(
            request.raw_data,
            request.data_type,
            request.source
        )
        return {"message": "Market data normalized successfully", "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/market/data/{symbol}", summary="Get market data for a specific symbol")
async def get_market_data_endpoint(
    symbol: str,
    data_type: str,
    source: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieves market data for a specific symbol and data type.
    Requires 'market_data:read' permission.
    """
    # TODO: Add permission check for current_user
    try:
        result = await market_data_normalizer.get_market_data(symbol, data_type, source)
        return {"message": "Market data retrieved successfully", "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/market/feed/batch", summary="Get market data feed for multiple symbols")
async def get_market_data_feed_endpoint(
    request: GetMarketDataFeedRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieves market data feed for multiple symbols and data types.
    Requires 'market_data:read' permission.
    """
    # TODO: Add permission check for current_user
    try:
        result = await market_data_normalizer.get_market_data_feed(
            request.symbols,
            request.data_types,
            request.sources
        )
        return {"message": "Market data feed retrieved successfully", "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/market/feed/start", summary="Start a real-time data feed")
async def start_data_feed_endpoint(
    request: StartDataFeedRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Starts a real-time data feed for a specific symbol and data type.
    Requires 'market_data:admin' permission.
    """
    # TODO: Add permission check for current_user
    try:
        result = await market_data_normalizer.start_data_feed(
            request.symbol,
            request.data_type,
            request.source,
            request.frequency
        )
        return {"message": "Data feed started successfully", "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/market/feed/stop/{feed_id}", summary="Stop a data feed")
async def stop_data_feed_endpoint(
    feed_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Stops a running data feed.
    Requires 'market_data:admin' permission.
    """
    # TODO: Add permission check for current_user
    try:
        result = await market_data_normalizer.stop_data_feed(feed_id)
        return {"message": "Data feed stopped successfully", "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/market/feeds/active", summary="Get list of active data feeds")
async def get_active_feeds_endpoint(
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieves list of currently active data feeds.
    Requires 'market_data:read' permission.
    """
    # TODO: Add permission check for current_user
    try:
        result = await market_data_normalizer.get_active_feeds()
        return {"message": "Active feeds retrieved successfully", "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/market/websocket/info", summary="Get WebSocket connection information")
async def get_websocket_info_endpoint(
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieves WebSocket connection information for real-time market data.
    Requires 'market_data:read' permission.
    """
    # TODO: Add permission check for current_user
    try:
        websocket_info = {
            "websocket_url": f"ws://localhost:{market_data_normalizer.websocket_port}",
            "connection_protocol": "JSON",
            "message_types": ["market_data", "connection", "ping", "pong", "subscribe"],
            "subscription_format": {
                "type": "subscribe",
                "symbols": ["CL=F", "NG=F"],
                "data_types": ["price", "volume"]
            },
            "ping_format": {
                "type": "ping"
            }
        }
        
        return {"message": "WebSocket information retrieved", "data": websocket_info}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
