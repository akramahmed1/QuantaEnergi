"""
WebSocket Service for EnergyOpti-Pro.

Provides real-time streaming for market data, order updates, and live trading information.
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, List, Set, Callable
from datetime import datetime, timezone
import structlog
from dataclasses import dataclass, asdict
from enum import Enum
import websockets
from websockets.server import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosed

logger = structlog.get_logger()

class MessageType(Enum):
    """WebSocket message types."""
    MARKET_DATA = "market_data"
    ORDER_UPDATE = "order_update"
    POSITION_UPDATE = "position_update"
    TRADING_SIGNAL = "trading_signal"
    RISK_ALERT = "risk_alert"
    SYSTEM_STATUS = "system_status"
    HEARTBEAT = "heartbeat"
    ERROR = "error"

@dataclass
class WebSocketMessage:
    """WebSocket message structure."""
    type: MessageType
    data: Dict[str, Any]
    timestamp: datetime
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        message_dict = asdict(self)
        message_dict["type"] = self.type.value
        message_dict["timestamp"] = self.timestamp.isoformat()
        return message_dict

class ConnectionManager:
    """Manages WebSocket connections and subscriptions."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocketServerProtocol] = {}
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> set of connection_ids
        self.subscriptions: Dict[str, Set[str]] = {}  # connection_id -> set of topics
        self.topic_subscribers: Dict[str, Set[str]] = {}  # topic -> set of connection_ids
        
        # Connection metadata
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Heartbeat tracking
        self.last_heartbeat: Dict[str, float] = {}
        self.heartbeat_interval = 30  # seconds
        
        # Performance metrics
        self.metrics = {
            "total_connections": 0,
            "active_connections": 0,
            "messages_sent": 0,
            "messages_received": 0,
            "errors": 0
        }
    
    async def connect(self, websocket: WebSocketServerProtocol, user_id: Optional[str] = None) -> str:
        """Register a new WebSocket connection."""
        connection_id = str(id(websocket))
        
        # Store connection
        self.active_connections[connection_id] = websocket
        self.connection_metadata[connection_id] = {
            "user_id": user_id,
            "connected_at": time.time(),
            "last_activity": time.time(),
            "ip_address": websocket.remote_address[0] if websocket.remote_address else "unknown",
            "user_agent": websocket.request_headers.get("User-Agent", "unknown")
        }
        
        # Update user connections
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(connection_id)
        
        # Initialize subscriptions
        self.subscriptions[connection_id] = set()
        
        # Update metrics
        self.metrics["total_connections"] += 1
        self.metrics["active_connections"] += 1
        
        logger.info(f"WebSocket connected: {connection_id} (user: {user_id})")
        return connection_id
    
    async def disconnect(self, connection_id: str):
        """Remove a WebSocket connection."""
        if connection_id not in self.active_connections:
            return
        
        # Get user_id for cleanup
        user_id = self.connection_metadata.get(connection_id, {}).get("user_id")
        
        # Remove from active connections
        websocket = self.active_connections.pop(connection_id, None)
        if websocket:
            try:
                await websocket.close()
            except Exception as e:
                logger.warning(f"Error closing websocket {connection_id}: {e}")
        
        # Clean up subscriptions
        subscribed_topics = self.subscriptions.pop(connection_id, set())
        for topic in subscribed_topics:
            if topic in self.topic_subscribers:
                self.topic_subscribers[topic].discard(connection_id)
                if not self.topic_subscribers[topic]:
                    del self.topic_subscribers[topic]
        
        # Clean up user connections
        if user_id and user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        # Clean up metadata
        self.connection_metadata.pop(connection_id, None)
        self.last_heartbeat.pop(connection_id, None)
        
        # Update metrics
        self.metrics["active_connections"] = max(0, self.metrics["active_connections"] - 1)
        
        logger.info(f"WebSocket disconnected: {connection_id}")
    
    async def subscribe(self, connection_id: str, topic: str) -> bool:
        """Subscribe a connection to a topic."""
        if connection_id not in self.active_connections:
            return False
        
        # Add to subscriptions
        if connection_id not in self.subscriptions:
            self.subscriptions[connection_id] = set()
        self.subscriptions[connection_id].add(topic)
        
        # Add to topic subscribers
        if topic not in self.topic_subscribers:
            self.topic_subscribers[topic] = set()
        self.topic_subscribers[topic].add(connection_id)
        
        logger.debug(f"Connection {connection_id} subscribed to {topic}")
        return True
    
    async def unsubscribe(self, connection_id: str, topic: str) -> bool:
        """Unsubscribe a connection from a topic."""
        if connection_id not in self.subscriptions:
            return False
        
        # Remove from subscriptions
        if topic in self.subscriptions[connection_id]:
            self.subscriptions[connection_id].discard(topic)
        
        # Remove from topic subscribers
        if topic in self.topic_subscribers:
            self.topic_subscribers[topic].discard(connection_id)
            if not self.topic_subscribers[topic]:
                del self.topic_subscribers[topic]
        
        logger.debug(f"Connection {connection_id} unsubscribed from {topic}")
        return True
    
    async def broadcast(self, message: WebSocketMessage, topic: Optional[str] = None):
        """Broadcast message to all connections or topic subscribers."""
        connections_to_notify = set()
        
        if topic:
            # Send to topic subscribers
            if topic in self.topic_subscribers:
                connections_to_notify.update(self.topic_subscribers[topic])
        else:
            # Send to all connections
            connections_to_notify.update(self.active_connections.keys())
        
        # Send message to each connection
        failed_connections = []
        for connection_id in connections_to_notify:
            if connection_id in self.active_connections:
                try:
                    websocket = self.active_connections[connection_id]
                    await websocket.send(json.dumps(message.to_dict()))
                    self.metrics["messages_sent"] += 1
                    
                    # Update last activity
                    if connection_id in self.connection_metadata:
                        self.connection_metadata[connection_id]["last_activity"] = time.time()
                        
                except Exception as e:
                    logger.error(f"Failed to send message to {connection_id}: {e}")
                    failed_connections.append(connection_id)
                    self.metrics["errors"] += 1
        
        # Clean up failed connections
        for connection_id in failed_connections:
            await self.disconnect(connection_id)
    
    async def send_to_user(self, user_id: str, message: WebSocketMessage):
        """Send message to all connections of a specific user."""
        if user_id not in self.user_connections:
            return
        
        failed_connections = []
        for connection_id in self.user_connections[user_id]:
            if connection_id in self.active_connections:
                try:
                    websocket = self.active_connections[connection_id]
                    await websocket.send(json.dumps(message.to_dict()))
                    self.metrics["messages_sent"] += 1
                    
                    # Update last activity
                    if connection_id in self.connection_metadata:
                        self.connection_metadata[connection_id]["last_activity"] = time.time()
                        
                except Exception as e:
                    logger.error(f"Failed to send message to user {user_id} connection {connection_id}: {e}")
                    failed_connections.append(connection_id)
                    self.metrics["errors"] += 1
        
        # Clean up failed connections
        for connection_id in failed_connections:
            await self.disconnect(connection_id)
    
    async def send_to_connection(self, connection_id: str, message: WebSocketMessage) -> bool:
        """Send message to a specific connection."""
        if connection_id not in self.active_connections:
            return False
        
        try:
            websocket = self.active_connections[connection_id]
            await websocket.send(json.dumps(message.to_dict()))
            self.metrics["messages_sent"] += 1
            
            # Update last activity
            if connection_id in self.connection_metadata:
                self.connection_metadata[connection_id]["last_activity"] = time.time()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message to {connection_id}: {e}")
            self.metrics["errors"] += 1
            return False
    
    async def update_heartbeat(self, connection_id: str):
        """Update heartbeat for a connection."""
        self.last_heartbeat[connection_id] = time.time()
    
    async def check_heartbeats(self):
        """Check and remove stale connections."""
        current_time = time.time()
        stale_connections = []
        
        for connection_id, last_heartbeat in self.last_heartbeat.items():
            if current_time - last_heartbeat > self.heartbeat_interval * 2:
                stale_connections.append(connection_id)
        
        for connection_id in stale_connections:
            logger.warning(f"Removing stale connection: {connection_id}")
            await self.disconnect(connection_id)
    
    def get_connection_info(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific connection."""
        if connection_id not in self.connection_metadata:
            return None
        
        info = self.connection_metadata[connection_id].copy()
        info["subscriptions"] = list(self.subscriptions.get(connection_id, set()))
        info["is_active"] = connection_id in self.active_connections
        
        return info
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get connection manager metrics."""
        metrics = self.metrics.copy()
        metrics["topics"] = list(self.topic_subscribers.keys())
        metrics["total_subscriptions"] = sum(len(subscribers) for subscribers in self.topic_subscribers.values())
        
        return metrics

class WebSocketService:
    """Main WebSocket service for real-time communication."""
    
    def __init__(self):
        self.connection_manager = ConnectionManager()
        self.message_handlers: Dict[str, Callable] = {}
        self.heartbeat_task: Optional[asyncio.Task] = None
        
        # Register default message handlers
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register default message handlers."""
        self.message_handlers = {
            "subscribe": self._handle_subscribe,
            "unsubscribe": self._handle_unsubscribe,
            "heartbeat": self._handle_heartbeat,
            "ping": self._handle_ping,
            "get_status": self._handle_get_status
        }
    
    async def start(self):
        """Start the WebSocket service."""
        # Start heartbeat monitoring
        self.heartbeat_task = asyncio.create_task(self._heartbeat_monitor())
        logger.info("WebSocket service started")
    
    async def stop(self):
        """Stop the WebSocket service."""
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass
        
        # Close all connections
        for connection_id in list(self.connection_manager.active_connections.keys()):
            await self.connection_manager.disconnect(connection_id)
        
        logger.info("WebSocket service stopped")
    
    async def handle_connection(self, websocket: WebSocketServerProtocol, path: str):
        """Handle a new WebSocket connection."""
        connection_id = None
        
        try:
            # Extract user_id from query parameters or headers
            user_id = self._extract_user_id(websocket, path)
            
            # Register connection
            connection_id = await self.connection_manager.connect(websocket, user_id)
            
            # Send welcome message
            welcome_message = WebSocketMessage(
                type=MessageType.SYSTEM_STATUS,
                data={
                    "status": "connected",
                    "connection_id": connection_id,
                    "user_id": user_id,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                timestamp=datetime.now(timezone.utc),
                user_id=user_id,
                session_id=connection_id
            )
            
            await self.connection_manager.send_to_connection(connection_id, welcome_message)
            
            # Handle incoming messages
            async for message in websocket:
                await self._handle_message(connection_id, message)
                
        except ConnectionClosed:
            logger.info(f"WebSocket connection closed: {connection_id}")
        except Exception as e:
            logger.error(f"WebSocket error for {connection_id}: {e}")
        finally:
            if connection_id:
                await self.connection_manager.disconnect(connection_id)
    
    def _extract_user_id(self, websocket: WebSocketServerProtocol, path: str) -> Optional[str]:
        """Extract user ID from connection."""
        # Try to get from query parameters
        if "?" in path:
            query_params = path.split("?")[1]
            for param in query_params.split("&"):
                if param.startswith("user_id="):
                    return param.split("=")[1]
        
        # Try to get from headers
        auth_header = websocket.request_headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # In real implementation, decode JWT token to get user_id
            token = auth_header.split(" ")[1]
            # For now, return a mock user_id
            return f"user_{hash(token) % 1000}"
        
        return None
    
    async def _handle_message(self, connection_id: str, message: str):
        """Handle incoming WebSocket message."""
        try:
            data = json.loads(message)
            self.connection_manager.metrics["messages_received"] += 1
            
            message_type = data.get("type")
            if message_type in self.message_handlers:
                await self.message_handlers[message_type](connection_id, data)
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON message from {connection_id}")
        except Exception as e:
            logger.error(f"Error handling message from {connection_id}: {e}")
    
    async def _handle_subscribe(self, connection_id: str, data: Dict[str, Any]):
        """Handle subscription request."""
        topic = data.get("topic")
        if topic:
            await self.connection_manager.subscribe(connection_id, topic)
            
            # Send confirmation
            confirmation = WebSocketMessage(
                type=MessageType.SYSTEM_STATUS,
                data={"status": "subscribed", "topic": topic},
                timestamp=datetime.now(timezone.utc),
                session_id=connection_id
            )
            await self.connection_manager.send_to_connection(connection_id, confirmation)
    
    async def _handle_unsubscribe(self, connection_id: str, data: Dict[str, Any]):
        """Handle unsubscription request."""
        topic = data.get("topic")
        if topic:
            await self.connection_manager.unsubscribe(connection_id, topic)
            
            # Send confirmation
            confirmation = WebSocketMessage(
                type=MessageType.SYSTEM_STATUS,
                data={"status": "unsubscribed", "topic": topic},
                timestamp=datetime.now(timezone.utc),
                session_id=connection_id
            )
            await self.connection_manager.send_to_connection(connection_id, confirmation)
    
    async def _handle_heartbeat(self, connection_id: str, data: Dict[str, Any]):
        """Handle heartbeat message."""
        await self.connection_manager.update_heartbeat(connection_id)
        
        # Send heartbeat response
        response = WebSocketMessage(
            type=MessageType.HEARTBEAT,
            data={"timestamp": datetime.now(timezone.utc).isoformat()},
            timestamp=datetime.now(timezone.utc),
            session_id=connection_id
        )
        await self.connection_manager.send_to_connection(connection_id, response)
    
    async def _handle_ping(self, connection_id: str, data: Dict[str, Any]):
        """Handle ping message."""
        # Send pong response
        response = WebSocketMessage(
            type=MessageType.HEARTBEAT,
            data={"type": "pong", "timestamp": datetime.now(timezone.utc).isoformat()},
            timestamp=datetime.now(timezone.utc),
            session_id=connection_id
        )
        await self.connection_manager.send_to_connection(connection_id, response)
    
    async def _handle_get_status(self, connection_id: str, data: Dict[str, Any]):
        """Handle status request."""
        status = WebSocketMessage(
            type=MessageType.SYSTEM_STATUS,
            data={
                "connection_info": self.connection_manager.get_connection_info(connection_id),
                "service_metrics": self.connection_manager.get_metrics(),
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            timestamp=datetime.now(timezone.utc),
            session_id=connection_id
        )
        await self.connection_manager.send_to_connection(connection_id, status)
    
    async def _heartbeat_monitor(self):
        """Monitor connections and remove stale ones."""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                await self.connection_manager.check_heartbeats()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat monitor error: {e}")
    
    # Public methods for other services to use
    
    async def broadcast_market_data(self, market_data: Dict[str, Any]):
        """Broadcast market data to all subscribers."""
        message = WebSocketMessage(
            type=MessageType.MARKET_DATA,
            data=market_data,
            timestamp=datetime.now(timezone.utc)
        )
        await self.connection_manager.broadcast(message, "market_data")
    
    async def broadcast_order_update(self, order_data: Dict[str, Any], user_id: str):
        """Broadcast order update to specific user."""
        message = WebSocketMessage(
            type=MessageType.ORDER_UPDATE,
            data=order_data,
            timestamp=datetime.now(timezone.utc),
            user_id=user_id
        )
        await self.connection_manager.send_to_user(user_id, message)
    
    async def broadcast_position_update(self, position_data: Dict[str, Any], user_id: str):
        """Broadcast position update to specific user."""
        message = WebSocketMessage(
            type=MessageType.POSITION_UPDATE,
            data=position_data,
            timestamp=datetime.now(timezone.utc),
            user_id=user_id
        )
        await self.connection_manager.send_to_user(user_id, message)
    
    async def broadcast_trading_signal(self, signal_data: Dict[str, Any]):
        """Broadcast trading signal to all subscribers."""
        message = WebSocketMessage(
            type=MessageType.TRADING_SIGNAL,
            data=signal_data,
            timestamp=datetime.now(timezone.utc)
        )
        await self.connection_manager.broadcast(message, "trading_signals")
    
    async def broadcast_risk_alert(self, alert_data: Dict[str, Any], user_id: str):
        """Broadcast risk alert to specific user."""
        message = WebSocketMessage(
            type=MessageType.RISK_ALERT,
            data=alert_data,
            timestamp=datetime.now(timezone.utc),
            user_id=user_id
        )
        await self.connection_manager.send_to_user(user_id, message)
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get WebSocket service status."""
        return {
            "status": "running",
            "connection_manager": self.connection_manager.get_metrics(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# Global WebSocket service instance
_websocket_service: Optional[WebSocketService] = None

async def get_websocket_service() -> WebSocketService:
    """Get global WebSocket service instance."""
    global _websocket_service
    if _websocket_service is None:
        _websocket_service = WebSocketService()
        await _websocket_service.start()
    return _websocket_service

async def close_websocket_service():
    """Close global WebSocket service."""
    global _websocket_service
    if _websocket_service:
        await _websocket_service.stop()
        _websocket_service = None
