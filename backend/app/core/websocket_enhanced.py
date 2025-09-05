"""
Enhanced WebSocket Manager for Real-Time ETRM/CTRM Operations
Implements observer pattern, real-time data sync, and connection management
"""

import asyncio
import json
import logging
from typing import Dict, List, Set, Optional, Any, Callable
from datetime import datetime
from uuid import uuid4
import weakref
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum

from fastapi import WebSocket, WebSocketDisconnect
from .event_bus import EventType, BaseEvent

logger = logging.getLogger(__name__)

class MessageType(Enum):
    """WebSocket message types"""
    PING = "ping"
    PONG = "pong"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    DATA_UPDATE = "data_update"
    TRADE_UPDATE = "trade_update"
    MARKET_DATA = "market_data"
    RISK_ALERT = "risk_alert"
    ERROR = "error"

@dataclass
class WebSocketMessage:
    """WebSocket message structure"""
    type: MessageType
    data: Dict[str, Any]
    timestamp: datetime
    message_id: str

class WebSocketObserver:
    """Observer pattern implementation for WebSocket updates"""
    
    def __init__(self):
        self.subscribers: Dict[str, Set[WebSocket]] = defaultdict(set)
        self.connection_subscriptions: Dict[WebSocket, Set[str]] = defaultdict(set)
        self.message_handlers: Dict[MessageType, Callable] = {}
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register default message handlers"""
        self.message_handlers[MessageType.PING] = self._handle_ping
        self.message_handlers[MessageType.SUBSCRIBE] = self._handle_subscribe
        self.message_handlers[MessageType.UNSUBSCRIBE] = self._handle_unsubscribe
    
    def subscribe(self, websocket: WebSocket, topic: str):
        """Subscribe websocket to topic"""
        self.subscribers[topic].add(websocket)
        self.connection_subscriptions[websocket].add(topic)
        logger.info(f"WebSocket subscribed to topic: {topic}")
    
    def unsubscribe(self, websocket: WebSocket, topic: str):
        """Unsubscribe websocket from topic"""
        self.subscribers[topic].discard(websocket)
        self.connection_subscriptions[websocket].discard(topic)
        logger.info(f"WebSocket unsubscribed from topic: {topic}")
    
    def unsubscribe_all(self, websocket: WebSocket):
        """Unsubscribe websocket from all topics"""
        topics = self.connection_subscriptions[websocket].copy()
        for topic in topics:
            self.unsubscribe(websocket, topic)
        del self.connection_subscriptions[websocket]
    
    async def notify(self, topic: str, message: WebSocketMessage):
        """Notify all subscribers of a topic"""
        if topic not in self.subscribers:
            return
        
        # Create message data
        message_data = {
            "type": message.type.value,
            "data": message.data,
            "timestamp": message.timestamp.isoformat(),
            "message_id": message.message_id,
            "topic": topic
        }
        
        # Send to all subscribers
        disconnected = set()
        for websocket in self.subscribers[topic]:
            try:
                await websocket.send_text(json.dumps(message_data))
            except Exception as e:
                logger.warning(f"Failed to send message to websocket: {e}")
                disconnected.add(websocket)
        
        # Remove disconnected websockets
        for websocket in disconnected:
            self.unsubscribe_all(websocket)
    
    async def handle_message(self, websocket: WebSocket, message: str):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            message_type = MessageType(data.get("type", "ping"))
            
            if message_type in self.message_handlers:
                await self.message_handlers[message_type](websocket, data)
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON message received")
            await self._send_error(websocket, "Invalid JSON format")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await self._send_error(websocket, "Message handling error")
    
    async def _handle_ping(self, websocket: WebSocket, data: Dict[str, Any]):
        """Handle ping message"""
        pong_message = WebSocketMessage(
            type=MessageType.PONG,
            data={"timestamp": datetime.utcnow().isoformat()},
            timestamp=datetime.utcnow(),
            message_id=str(uuid4())
        )
        await self._send_message(websocket, pong_message)
    
    async def _handle_subscribe(self, websocket: WebSocket, data: Dict[str, Any]):
        """Handle subscribe message"""
        topic = data.get("topic")
        if topic:
            self.subscribe(websocket, topic)
            await self._send_success(websocket, f"Subscribed to {topic}")
        else:
            await self._send_error(websocket, "Topic required for subscription")
    
    async def _handle_unsubscribe(self, websocket: WebSocket, data: Dict[str, Any]):
        """Handle unsubscribe message"""
        topic = data.get("topic")
        if topic:
            self.unsubscribe(websocket, topic)
            await self._send_success(websocket, f"Unsubscribed from {topic}")
        else:
            await self._send_error(websocket, "Topic required for unsubscription")
    
    async def _send_message(self, websocket: WebSocket, message: WebSocketMessage):
        """Send message to websocket"""
        try:
            message_data = {
                "type": message.type.value,
                "data": message.data,
                "timestamp": message.timestamp.isoformat(),
                "message_id": message.message_id
            }
            await websocket.send_text(json.dumps(message_data))
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
    
    async def _send_error(self, websocket: WebSocket, error_message: str):
        """Send error message to websocket"""
        error_msg = WebSocketMessage(
            type=MessageType.ERROR,
            data={"error": error_message},
            timestamp=datetime.utcnow(),
            message_id=str(uuid4())
        )
        await self._send_message(websocket, error_msg)
    
    async def _send_success(self, websocket: WebSocket, success_message: str):
        """Send success message to websocket"""
        success_msg = WebSocketMessage(
            type=MessageType.DATA_UPDATE,
            data={"message": success_message, "status": "success"},
            timestamp=datetime.utcnow(),
            message_id=str(uuid4())
        )
        await self._send_message(websocket, success_msg)

class EnhancedWebSocketManager:
    """Enhanced WebSocket Manager with real-time features"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.organization_connections: Dict[str, Set[str]] = defaultdict(set)
        self.user_connections: Dict[str, Set[str]] = defaultdict(set)
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        self.observer = WebSocketObserver()
        
        # Performance metrics
        self.connection_count = 0
        self.message_count = 0
        self.error_count = 0
        
        # Real-time data feeds
        self.market_data_feeds: Dict[str, Dict[str, Any]] = {}
        self.trade_feeds: Dict[str, Dict[str, Any]] = {}
        self.risk_feeds: Dict[str, Dict[str, Any]] = {}
        
        # Background tasks
        self.background_tasks: Set[asyncio.Task] = set()
        self._start_background_tasks()
    
    def _start_background_tasks(self):
        """Start background tasks for real-time data"""
        # Background tasks will be started when needed
        pass
    
    async def connect(self, websocket: WebSocket, user_id: str, organization_id: str) -> str:
        """Accept a new WebSocket connection"""
        try:
            await websocket.accept()
            connection_id = str(uuid4())
            
            # Store connection
            self.active_connections[connection_id] = websocket
            self.organization_connections[organization_id].add(connection_id)
            self.user_connections[user_id].add(connection_id)
            
            # Store metadata
            self.connection_metadata[connection_id] = {
                "user_id": user_id,
                "organization_id": organization_id,
                "connected_at": datetime.utcnow(),
                "last_activity": datetime.utcnow()
            }
            
            self.connection_count += 1
            
            # Send welcome message
            welcome_message = WebSocketMessage(
                type=MessageType.DATA_UPDATE,
                data={
                    "message": "Connected to QuantaEnergi Real-Time Feed",
                    "connection_id": connection_id,
                    "available_topics": ["market_data", "trades", "risk_alerts", "positions"]
                },
                timestamp=datetime.utcnow(),
                message_id=str(uuid4())
            )
            await self.observer._send_message(websocket, welcome_message)
            
            logger.info(f"WebSocket connected: {connection_id} for user {user_id}")
            return connection_id
            
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
            raise
    
    async def disconnect(self, connection_id: str):
        """Disconnect WebSocket"""
        try:
            if connection_id in self.active_connections:
                websocket = self.active_connections[connection_id]
                metadata = self.connection_metadata.get(connection_id, {})
                
                # Unsubscribe from all topics
                self.observer.unsubscribe_all(websocket)
                
                # Remove from tracking
                user_id = metadata.get("user_id")
                organization_id = metadata.get("organization_id")
                
                if user_id:
                    self.user_connections[user_id].discard(connection_id)
                if organization_id:
                    self.organization_connections[organization_id].discard(connection_id)
                
                del self.active_connections[connection_id]
                del self.connection_metadata[connection_id]
                
                self.connection_count -= 1
                logger.info(f"WebSocket disconnected: {connection_id}")
                
        except Exception as e:
            logger.error(f"WebSocket disconnection error: {e}")
    
    async def handle_message(self, connection_id: str, message: str):
        """Handle incoming WebSocket message"""
        try:
            if connection_id not in self.active_connections:
                return
            
            websocket = self.active_connections[connection_id]
            self.connection_metadata[connection_id]["last_activity"] = datetime.utcnow()
            
            # Handle message through observer
            await self.observer.handle_message(websocket, message)
            self.message_count += 1
            
        except WebSocketDisconnect:
            await self.disconnect(connection_id)
        except Exception as e:
            logger.error(f"Message handling error: {e}")
            self.error_count += 1
    
    async def broadcast_to_organization(self, organization_id: str, message: WebSocketMessage):
        """Broadcast message to all connections in organization"""
        if organization_id not in self.organization_connections:
            return
        
        for connection_id in self.organization_connections[organization_id]:
            if connection_id in self.active_connections:
                websocket = self.active_connections[connection_id]
                try:
                    await self.observer._send_message(websocket, message)
                except Exception as e:
                    logger.warning(f"Failed to send to connection {connection_id}: {e}")
    
    async def broadcast_to_user(self, user_id: str, message: WebSocketMessage):
        """Broadcast message to all connections for user"""
        if user_id not in self.user_connections:
            return
        
        for connection_id in self.user_connections[user_id]:
            if connection_id in self.active_connections:
                websocket = self.active_connections[connection_id]
                try:
                    await self.observer._send_message(websocket, message)
                except Exception as e:
                    logger.warning(f"Failed to send to connection {connection_id}: {e}")
    
    async def broadcast_to_topic(self, topic: str, message: WebSocketMessage):
        """Broadcast message to all subscribers of topic"""
        await self.observer.notify(topic, message)
    
    async def _market_data_feed(self):
        """Background task for market data feed"""
        while True:
            try:
                # Simulate market data updates
                market_data = {
                    "crude_oil": {
                        "price": 85.50 + (asyncio.get_event_loop().time() % 10),
                        "change": 0.25,
                        "volume": 1000000,
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    "natural_gas": {
                        "price": 3.20 + (asyncio.get_event_loop().time() % 5) * 0.1,
                        "change": -0.05,
                        "volume": 500000,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }
                
                message = WebSocketMessage(
                    type=MessageType.MARKET_DATA,
                    data=market_data,
                    timestamp=datetime.utcnow(),
                    message_id=str(uuid4())
                )
                
                await self.broadcast_to_topic("market_data", message)
                await asyncio.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                logger.error(f"Market data feed error: {e}")
                await asyncio.sleep(10)
    
    async def _trade_feed(self):
        """Background task for trade updates"""
        while True:
            try:
                # Simulate trade updates
                trade_data = {
                    "trade_id": f"TRD-{int(datetime.utcnow().timestamp())}",
                    "status": "confirmed",
                    "commodity": "crude_oil",
                    "quantity": 1000,
                    "price": 85.50,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                message = WebSocketMessage(
                    type=MessageType.TRADE_UPDATE,
                    data=trade_data,
                    timestamp=datetime.utcnow(),
                    message_id=str(uuid4())
                )
                
                await self.broadcast_to_topic("trades", message)
                await asyncio.sleep(10)  # Update every 10 seconds
                
            except Exception as e:
                logger.error(f"Trade feed error: {e}")
                await asyncio.sleep(15)
    
    async def _risk_monitoring_feed(self):
        """Background task for risk monitoring"""
        while True:
            try:
                # Simulate risk alerts
                risk_data = {
                    "alert_type": "position_limit",
                    "severity": "medium",
                    "message": "Position approaching limit",
                    "trade_id": f"TRD-{int(datetime.utcnow().timestamp())}",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                message = WebSocketMessage(
                    type=MessageType.RISK_ALERT,
                    data=risk_data,
                    timestamp=datetime.utcnow(),
                    message_id=str(uuid4())
                )
                
                await self.broadcast_to_topic("risk_alerts", message)
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                logger.error(f"Risk monitoring error: {e}")
                await asyncio.sleep(45)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        return {
            "active_connections": self.connection_count,
            "total_messages": self.message_count,
            "total_errors": self.error_count,
            "organizations": len(self.organization_connections),
            "users": len(self.user_connections),
            "background_tasks": len(self.background_tasks)
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Close all connections
        for connection_id in list(self.active_connections.keys()):
            await self.disconnect(connection_id)

# Global WebSocket manager instance
websocket_manager = EnhancedWebSocketManager()
