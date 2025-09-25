"""
Market Data Normalizer Service for ETRM/CTRM Trading
Handles live feeds, normalization utils, and WebSocket integration
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
import asyncio
import json
import websockets
import threading
import time
from enum import Enum
from fastapi import HTTPException
import uuid

logger = logging.getLogger(__name__)

class MarketDataType(Enum):
    """Market data type enumeration"""
    PRICE = "price"
    VOLUME = "volume"
    VOLATILITY = "volatility"
    FUNDAMENTAL = "fundamental"
    TECHNICAL = "technical"
    NEWS = "news"
    SENTIMENT = "sentiment"

class DataSource(Enum):
    """Data source enumeration"""
    YAHOO_FINANCE = "yahoo_finance"
    BLOOMBERG = "bloomberg"
    REFINITIV = "refinitiv"
    INTERNAL = "internal"
    MOCK = "mock"

class MarketDataNormalizer:
    """
    Service for normalizing market data from various sources
    Includes live feeds, WebSocket integration, and data processing
    """
    
    def __init__(self):
        # Data storage
        self.market_data = {}
        self.normalized_data = {}
        self.data_feeds = {}
        self.websocket_clients = {}
        
        # Data processing
        self.data_schemas = {}
        self.normalization_rules = {}
        
        # WebSocket configuration
        self.websocket_servers = {}
        self.websocket_port = 8765
        
        # Initialize data schemas and normalization rules
        self._initialize_data_schemas()
        self._initialize_normalization_rules()
        
        # Start WebSocket server
        self._start_websocket_server()
    
    def _initialize_data_schemas(self):
        """Initialize data schemas for different market data types"""
        
        self.data_schemas = {
            MarketDataType.PRICE.value: {
                "symbol": str,
                "price": float,
                "currency": str,
                "timestamp": str,
                "source": str,
                "bid": Optional[float],
                "ask": Optional[float],
                "spread": Optional[float],
                "volume": Optional[int]
            },
            MarketDataType.VOLUME.value: {
                "symbol": str,
                "volume": int,
                "timestamp": str,
                "source": str,
                "volume_type": str,  # "traded", "outstanding", "available"
                "price_range": Optional[Dict[str, float]]
            },
            MarketDataType.VOLATILITY.value: {
                "symbol": str,
                "volatility": float,
                "volatility_type": str,  # "historical", "implied", "realized"
                "timeframe": str,  # "1d", "1w", "1m", "1y"
                "timestamp": str,
                "source": str
            },
            MarketDataType.FUNDAMENTAL.value: {
                "symbol": str,
                "metric_name": str,
                "metric_value": float,
                "metric_unit": str,
                "timestamp": str,
                "source": str,
                "period": str  # "quarterly", "annual", "trailing"
            },
            MarketDataType.TECHNICAL.value: {
                "symbol": str,
                "indicator_name": str,
                "indicator_value": float,
                "indicator_type": str,  # "trend", "momentum", "oscillator", "volume"
                "timestamp": str,
                "source": str,
                "parameters": Optional[Dict[str, Any]]
            }
        }
    
    def _initialize_normalization_rules(self):
        """Initialize normalization rules for different data sources"""
        
        self.normalization_rules = {
            DataSource.YAHOO_FINANCE.value: {
                "price_mapping": {
                    "regularMarketPrice": "price",
                    "currency": "currency",
                    "regularMarketTime": "timestamp",
                    "bid": "bid",
                    "ask": "ask",
                    "regularMarketVolume": "volume"
                },
                "transformations": {
                    "timestamp": lambda x: datetime.fromtimestamp(x).isoformat(),
                    "currency": lambda x: x.upper() if x else "USD"
                }
            },
            DataSource.BLOOMBERG.value: {
                "price_mapping": {
                    "PX_LAST": "price",
                    "CRNCY": "currency",
                    "TIMESTAMP": "timestamp",
                    "BID": "bid",
                    "ASK": "ask",
                    "VOLUME": "volume"
                },
                "transformations": {
                    "timestamp": lambda x: x.isoformat() if hasattr(x, 'isoformat') else str(x)
                }
            },
            DataSource.REFINITIV.value: {
                "price_mapping": {
                    "TRDPRC_1": "price",
                    "CRNCY_ADJ_MKT_CAP": "currency",
                    "TIMESTAMP_1": "timestamp",
                    "BID": "bid",
                    "ASK": "ask",
                    "VOLUME_1": "volume"
                },
                "transformations": {
                    "timestamp": lambda x: x.isoformat() if hasattr(x, 'isoformat') else str(x)
                }
            },
            DataSource.MOCK.value: {
                "price_mapping": {
                    "price": "price",
                    "currency": "currency",
                    "timestamp": "timestamp",
                    "bid": "bid",
                    "ask": "ask",
                    "volume": "volume"
                },
                "transformations": {
                    "timestamp": lambda x: datetime.now().isoformat()
                }
            }
        }
    
    async def normalize_market_data(
        self, 
        raw_data: Dict[str, Any], 
        data_type: str, 
        source: str
    ) -> Dict[str, Any]:
        """
        Normalize market data from various sources
        
        Args:
            raw_data: Raw market data from source
            data_type: Type of market data (price, volume, volatility, etc.)
            source: Data source (yahoo_finance, bloomberg, etc.)
            
        Returns:
            Dict with normalized market data
        """
        try:
            logger.info(f"Normalizing {data_type} data from {source}")
            
            # Get normalization rules for source
            rules = self.normalization_rules.get(source, {})
            if not rules:
                raise HTTPException(status_code=400, detail=f"No normalization rules for source: {source}")
            
            # Get data schema for type
            schema = self.data_schemas.get(data_type, {})
            if not schema:
                raise HTTPException(status_code=400, detail=f"No schema for data type: {data_type}")
            
            # Apply field mapping
            field_mapping = rules.get(f"{data_type}_mapping", rules.get("price_mapping", {}))
            transformations = rules.get("transformations", {})
            
            normalized_data = {}
            
            # Map and transform fields
            for source_field, target_field in field_mapping.items():
                if source_field in raw_data:
                    value = raw_data[source_field]
                    
                    # Apply transformation if available
                    if target_field in transformations:
                        try:
                            value = transformations[target_field](value)
                        except Exception as e:
                            logger.warning(f"Transformation failed for {target_field}: {e}")
                            continue
                    
                    normalized_data[target_field] = value
            
            # Add metadata
            normalized_data.update({
                "normalized_at": datetime.now().isoformat(),
                "source": source,
                "data_type": data_type,
                "normalization_version": "1.0"
            })
            
            # Validate against schema
            validated_data = self._validate_data_schema(normalized_data, schema)
            
            # Store normalized data
            symbol = normalized_data.get("symbol", "unknown")
            if symbol not in self.normalized_data:
                self.normalized_data[symbol] = {}
            
            self.normalized_data[symbol][data_type] = validated_data
            
            # Broadcast via WebSocket
            await self._broadcast_market_data(symbol, data_type, validated_data)
            
            logger.info(f"Successfully normalized {data_type} data for {symbol}")
            
            return {
                "success": True,
                "normalized_data": validated_data,
                "symbol": symbol,
                "data_type": data_type,
                "source": source
            }
            
        except Exception as e:
            logger.error(f"Market data normalization failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def _validate_data_schema(self, data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data against schema"""
        
        validated_data = {}
        
        for field, expected_type in schema.items():
            if field in data:
                value = data[field]
                
                # Type validation
                if expected_type == Optional[float] and value is not None:
                    try:
                        validated_data[field] = float(value)
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid float value for {field}: {value}")
                        continue
                elif expected_type == Optional[int] and value is not None:
                    try:
                        validated_data[field] = int(value)
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid int value for {field}: {value}")
                        continue
                elif expected_type == float:
                    try:
                        validated_data[field] = float(value)
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid float value for {field}: {value}")
                        continue
                elif expected_type == int:
                    try:
                        validated_data[field] = int(value)
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid int value for {field}: {value}")
                        continue
                else:
                    validated_data[field] = value
            else:
                # Add default value for optional fields
                if expected_type == Optional[float] or expected_type == Optional[int]:
                    validated_data[field] = None
                elif expected_type == str:
                    validated_data[field] = ""
                elif expected_type == float:
                    validated_data[field] = 0.0
                elif expected_type == int:
                    validated_data[field] = 0
        
        return validated_data
    
    async def _broadcast_market_data(self, symbol: str, data_type: str, data: Dict[str, Any]):
        """Broadcast normalized market data via WebSocket"""
        
        try:
            broadcast_data = {
                "type": "market_data",
                "symbol": symbol,
                "data_type": data_type,
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
            
            # Send to all connected WebSocket clients
            if self.websocket_clients:
                message = json.dumps(broadcast_data)
                disconnected_clients = []
                
                for client_id, websocket in self.websocket_clients.items():
                    try:
                        await websocket.send(message)
                    except websockets.exceptions.ConnectionClosed:
                        disconnected_clients.append(client_id)
                
                # Remove disconnected clients
                for client_id in disconnected_clients:
                    del self.websocket_clients[client_id]
                    logger.info(f"Removed disconnected WebSocket client: {client_id}")
            
        except Exception as e:
            logger.error(f"Failed to broadcast market data: {e}")
    
    def _start_websocket_server(self):
        """Start WebSocket server for real-time market data"""
        
        async def websocket_handler(websocket, path):
            client_id = str(uuid.uuid4())
            self.websocket_clients[client_id] = websocket
            logger.info(f"New WebSocket client connected: {client_id}")
            
            try:
                # Send welcome message
                welcome_message = {
                    "type": "connection",
                    "status": "connected",
                    "client_id": client_id,
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send(json.dumps(welcome_message))
                
                # Keep connection alive
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        await self._handle_websocket_message(client_id, data)
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON from client {client_id}: {message}")
                    except Exception as e:
                        logger.error(f"Error handling message from client {client_id}: {e}")
                        
            except websockets.exceptions.ConnectionClosed:
                logger.info(f"WebSocket client disconnected: {client_id}")
            finally:
                if client_id in self.websocket_clients:
                    del self.websocket_clients[client_id]
        
        async def start_server():
            server = await websockets.serve(websocket_handler, "localhost", self.websocket_port)
            self.websocket_servers["main"] = server
            logger.info(f"WebSocket server started on port {self.websocket_port}")
            
            # Keep server running
            await server.wait_closed()
        
        # Start server in background thread
        def run_server():
            asyncio.new_event_loop().run_until_complete(start_server())
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
    
    async def _handle_websocket_message(self, client_id: str, message: Dict[str, Any]):
        """Handle incoming WebSocket messages"""
        
        message_type = message.get("type")
        
        if message_type == "subscribe":
            # Handle subscription requests
            symbols = message.get("symbols", [])
            data_types = message.get("data_types", [])
            
            # Send current data for subscribed symbols/types
            for symbol in symbols:
                if symbol in self.normalized_data:
                    for data_type in data_types:
                        if data_type in self.normalized_data[symbol]:
                            response = {
                                "type": "market_data",
                                "symbol": symbol,
                                "data_type": data_type,
                                "data": self.normalized_data[symbol][data_type],
                                "timestamp": datetime.now().isoformat()
                            }
                            await self.websocket_clients[client_id].send(json.dumps(response))
        
        elif message_type == "ping":
            # Handle ping/pong
            pong_response = {
                "type": "pong",
                "timestamp": datetime.now().isoformat()
            }
            await self.websocket_clients[client_id].send(json.dumps(pong_response))
    
    async def get_market_data(
        self, 
        symbol: str, 
        data_type: str, 
        source: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get market data for a symbol
        
        Args:
            symbol: Market symbol (e.g., CL=F for crude oil futures)
            data_type: Type of data to retrieve
            source: Optional source filter
            
        Returns:
            Dict with market data
        """
        try:
            if symbol not in self.normalized_data:
                raise HTTPException(status_code=404, detail=f"No data available for symbol: {symbol}")
            
            symbol_data = self.normalized_data[symbol]
            
            if data_type not in symbol_data:
                raise HTTPException(status_code=404, detail=f"No {data_type} data available for symbol: {symbol}")
            
            data = symbol_data[data_type]
            
            # Apply source filter if provided
            if source and data.get("source") != source:
                raise HTTPException(status_code=404, detail=f"No data from source {source} for symbol: {symbol}")
            
            return {
                "success": True,
                "symbol": symbol,
                "data_type": data_type,
                "data": data,
                "retrieved_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get market data: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_market_data_feed(
        self, 
        symbols: List[str], 
        data_types: List[str], 
        sources: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get market data feed for multiple symbols
        
        Args:
            symbols: List of market symbols
            data_types: List of data types to retrieve
            sources: Optional list of sources to filter by
            
        Returns:
            Dict with market data feed
        """
        try:
            feed_data = {}
            
            for symbol in symbols:
                if symbol in self.normalized_data:
                    symbol_data = {}
                    
                    for data_type in data_types:
                        if data_type in self.normalized_data[symbol]:
                            data = self.normalized_data[symbol][data_type]
                            
                            # Apply source filter if provided
                            if sources and data.get("source") not in sources:
                                continue
                            
                            symbol_data[data_type] = data
                    
                    if symbol_data:
                        feed_data[symbol] = symbol_data
            
            return {
                "success": True,
                "feed_data": feed_data,
                "symbols_requested": symbols,
                "symbols_available": list(feed_data.keys()),
                "data_types_requested": data_types,
                "sources_filtered": sources,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get market data feed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def start_data_feed(
        self, 
        symbol: str, 
        data_type: str, 
        source: str, 
        frequency: int = 60
    ) -> Dict[str, Any]:
        """
        Start a real-time data feed for a symbol
        
        Args:
            symbol: Market symbol
            data_type: Type of data to feed
            source: Data source
            frequency: Update frequency in seconds
            
        Returns:
            Dict with feed configuration
        """
        try:
            feed_id = f"{symbol}_{data_type}_{source}_{int(time.time())}"
            
            # Create feed configuration
            feed_config = {
                "feed_id": feed_id,
                "symbol": symbol,
                "data_type": data_type,
                "source": source,
                "frequency": frequency,
                "status": "active",
                "started_at": datetime.now().isoformat(),
                "last_update": None,
                "update_count": 0
            }
            
            # Store feed configuration
            self.data_feeds[feed_id] = feed_config
            
            # Start feed in background
            asyncio.create_task(self._run_data_feed(feed_id))
            
            logger.info(f"Started data feed: {feed_id}")
            
            return {
                "success": True,
                "feed_config": feed_config,
                "websocket_endpoint": f"ws://localhost:{self.websocket_port}"
            }
            
        except Exception as e:
            logger.error(f"Failed to start data feed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _run_data_feed(self, feed_id: str):
        """Run a data feed in the background"""
        
        try:
            feed_config = self.data_feeds[feed_id]
            
            while feed_config["status"] == "active":
                try:
                    # Generate mock data (in production, fetch from real source)
                    mock_data = self._generate_mock_data(
                        feed_config["symbol"],
                        feed_config["data_type"],
                        feed_config["source"]
                    )
                    
                    # Normalize the data
                    await self.normalize_market_data(
                        mock_data,
                        feed_config["data_type"],
                        feed_config["source"]
                    )
                    
                    # Update feed statistics
                    feed_config["last_update"] = datetime.now().isoformat()
                    feed_config["update_count"] += 1
                    
                    # Wait for next update
                    await asyncio.sleep(feed_config["frequency"])
                    
                except Exception as e:
                    logger.error(f"Error in data feed {feed_id}: {e}")
                    await asyncio.sleep(feed_config["frequency"])
            
        except Exception as e:
            logger.error(f"Data feed {feed_id} failed: {e}")
            self.data_feeds[feed_id]["status"] = "failed"
    
    def _generate_mock_data(
        self, 
        symbol: str, 
        data_type: str, 
        source: str
    ) -> Dict[str, Any]:
        """Generate mock market data for testing"""
        
        import random
        import time
        
        base_prices = {
            "CL=F": 75.50,  # Crude oil
            "NG=F": 3.25,   # Natural gas
            "HO=F": 2.85,   # Heating oil
            "RB=F": 2.45,   # Gasoline
            "BZ=F": 78.25,  # Brent crude
        }
        
        base_price = base_prices.get(symbol, 50.0)
        
        # Add some randomness
        price_variation = random.uniform(-0.05, 0.05)  # ±5% variation
        current_price = base_price * (1 + price_variation)
        
        mock_data = {
            "symbol": symbol,
            "price": round(current_price, 2),
            "currency": "USD",
            "timestamp": int(time.time()),
            "source": source,
            "bid": round(current_price * 0.999, 2),
            "ask": round(current_price * 1.001, 2),
            "volume": random.randint(1000, 10000)
        }
        
        # Add data type specific fields
        if data_type == MarketDataType.VOLATILITY.value:
            mock_data.update({
                "volatility": round(random.uniform(15.0, 35.0), 2),
                "volatility_type": "implied",
                "timeframe": "1m"
            })
        elif data_type == MarketDataType.VOLUME.value:
            mock_data.update({
                "volume": random.randint(50000, 500000),
                "volume_type": "traded",
                "price_range": {
                    "high": round(current_price * 1.02, 2),
                    "low": round(current_price * 0.98, 2)
                }
            })
        
        return mock_data
    
    async def stop_data_feed(self, feed_id: str) -> Dict[str, Any]:
        """Stop a data feed"""
        
        try:
            if feed_id not in self.data_feeds:
                raise HTTPException(status_code=404, detail="Feed not found")
            
            self.data_feeds[feed_id]["status"] = "stopped"
            self.data_feeds[feed_id]["stopped_at"] = datetime.now().isoformat()
            
            logger.info(f"Stopped data feed: {feed_id}")
            
            return {
                "success": True,
                "feed_id": feed_id,
                "status": "stopped"
            }
            
        except Exception as e:
            logger.error(f"Failed to stop data feed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_active_feeds(self) -> Dict[str, Any]:
        """Get list of active data feeds"""
        
        active_feeds = [
            feed for feed in self.data_feeds.values() 
            if feed["status"] == "active"
        ]
        
        return {
            "success": True,
            "active_feeds": active_feeds,
            "total_feeds": len(self.data_feeds),
            "generated_at": datetime.now().isoformat()
        }


# Global service instance
market_data_normalizer = MarketDataNormalizer()
