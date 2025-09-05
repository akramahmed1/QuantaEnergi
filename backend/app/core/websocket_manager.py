"""
WebSocket Manager for Real-Time Frontend-Backend Synchronization
Provides real-time updates and offline-first capabilities
"""

import asyncio
import json
import logging
from typing import Dict, List, Set, Optional, Any, Callable
from datetime import datetime
from uuid import uuid4
import weakref

from fastapi import WebSocket, WebSocketDisconnect
from .event_bus import EventType, BaseEvent

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections and provides real-time updates"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.organization_connections: Dict[str, Set[str]] = {}
        self.user_connections: Dict[str, Set[str]] = {}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        self.message_handlers: Dict[str, Callable] = {}
        self.offline_queue: Dict[str, List[Dict[str, Any]]] = {}
        
        # Performance metrics
        self.connection_count = 0
        self.message_count = 0
        self.error_count = 0
        
        # Register default message handlers
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register default message handlers"""
        self.register_handler("ping", self._handle_ping)
        self.register_handler("subscribe", self._handle_subscribe)
        self.register_handler("unsubscribe", self._handle_unsubscribe)
        self.register_handler("sync_request", self._handle_sync_request)
        self.register_handler("offline_data", self._handle_offline_data)
    
    async def connect(self, websocket: WebSocket, user_id: str, organization_id: str) -> str:
        """Accept a new WebSocket connection"""
        try:
            await websocket.accept()
            
            # Generate connection ID
            connection_id = str(uuid4())
            
            # Store connection
            self.active_connections[connection_id] = websocket
            self.connection_metadata[connection_id] = {
                "user_id": user_id,
                "organization_id": organization_id,
                "connected_at": datetime.utcnow(),
                "last_activity": datetime.utcnow(),
                "subscriptions": set(),
                "is_online": True
            }
            
            # Add to organization and user mappings
            if organization_id not in self.organization_connections:
                self.organization_connections[organization_id] = set()
            self.organization_connections[organization_id].add(connection_id)
            
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(connection_id)
            
            self.connection_count += 1
            
            # Send welcome message
            await self.send_personal_message(connection_id, {
                "type": "connection_established",
                "connection_id": connection_id,
                "timestamp": datetime.utcnow().isoformat(),
                "message": "WebSocket connection established successfully"
            })
            
            logger.info(f"WebSocket connection {connection_id} established for user {user_id} in organization {organization_id}")
            return connection_id
            
        except Exception as e:
            logger.error(f"Error establishing WebSocket connection: {e}")
            raise
    
    async def disconnect(self, connection_id: str):
        """Disconnect a WebSocket connection"""
        try:
            if connection_id in self.active_connections:
                websocket = self.active_connections[connection_id]
                metadata = self.connection_metadata.get(connection_id, {})
                
                # Remove from mappings
                user_id = metadata.get("user_id")
                organization_id = metadata.get("organization_id")
                
                if user_id and user_id in self.user_connections:
                    self.user_connections[user_id].discard(connection_id)
                    if not self.user_connections[user_id]:
                        del self.user_connections[user_id]
                
                if organization_id and organization_id in self.organization_connections:
                    self.organization_connections[organization_id].discard(connection_id)
                    if not self.organization_connections[organization_id]:
                        del self.organization_connections[organization_id]
                
                # Close websocket
                await websocket.close()
                
                # Clean up
                del self.active_connections[connection_id]
                del self.connection_metadata[connection_id]
                
                self.connection_count -= 1
                
                logger.info(f"WebSocket connection {connection_id} disconnected")
                
        except Exception as e:
            logger.error(f"Error disconnecting WebSocket connection {connection_id}: {e}")
    
    async def send_personal_message(self, connection_id: str, message: Dict[str, Any]):
        """Send a message to a specific connection"""
        try:
            if connection_id in self.active_connections:
                websocket = self.active_connections[connection_id]
                message_json = json.dumps(message)
                await websocket.send_text(message_json)
                
                # Update last activity
                if connection_id in self.connection_metadata:
                    self.connection_metadata[connection_id]["last_activity"] = datetime.utcnow()
                
                self.message_count += 1
                
        except Exception as e:
            logger.error(f"Error sending personal message to {connection_id}: {e}")
            self.error_count += 1
    
    async def broadcast_to_organization(self, organization_id: str, message: Dict[str, Any]):
        """Broadcast a message to all connections in an organization"""
        try:
            if organization_id in self.organization_connections:
                connection_ids = self.organization_connections[organization_id].copy()
                for connection_id in connection_ids:
                    await self.send_personal_message(connection_id, message)
                
                logger.debug(f"Broadcasted message to {len(connection_ids)} connections in organization {organization_id}")
                
        except Exception as e:
            logger.error(f"Error broadcasting to organization {organization_id}: {e}")
            self.error_count += 1
    
    async def broadcast_to_user(self, user_id: str, message: Dict[str, Any]):
        """Broadcast a message to all connections of a specific user"""
        try:
            if user_id in self.user_connections:
                connection_ids = self.user_connections[user_id].copy()
                for connection_id in connection_ids:
                    await self.send_personal_message(connection_id, message)
                
                logger.debug(f"Broadcasted message to {len(connection_ids)} connections for user {user_id}")
                
        except Exception as e:
            logger.error(f"Error broadcasting to user {user_id}: {e}")
            self.error_count += 1
    
    async def broadcast_to_all(self, message: Dict[str, Any]):
        """Broadcast a message to all active connections"""
        try:
            connection_ids = list(self.active_connections.keys())
            for connection_id in connection_ids:
                await self.send_personal_message(connection_id, message)
            
            logger.debug(f"Broadcasted message to {len(connection_ids)} connections")
            
        except Exception as e:
            logger.error(f"Error broadcasting to all connections: {e}")
            self.error_count += 1
    
    async def handle_message(self, connection_id: str, message: str):
        """Handle incoming WebSocket messages"""
        try:
            if connection_id not in self.active_connections:
                return
            
            # Parse message
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                await self.send_personal_message(connection_id, {
                    "type": "error",
                    "message": "Invalid JSON format",
                    "timestamp": datetime.utcnow().isoformat()
                })
                return
            
            message_type = data.get("type")
            if not message_type:
                await self.send_personal_message(connection_id, {
                    "type": "error",
                    "message": "Message type is required",
                    "timestamp": datetime.utcnow().isoformat()
                })
                return
            
            # Update last activity
            if connection_id in self.connection_metadata:
                self.connection_metadata[connection_id]["last_activity"] = datetime.utcnow()
            
            # Handle message
            if message_type in self.message_handlers:
                await self.message_handlers[message_type](connection_id, data)
            else:
                await self.send_personal_message(connection_id, {
                    "type": "error",
                    "message": f"Unknown message type: {message_type}",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
        except Exception as e:
            logger.error(f"Error handling message from {connection_id}: {e}")
            self.error_count += 1
    
    def register_handler(self, message_type: str, handler: Callable):
        """Register a message handler for a specific message type"""
        self.message_handlers[message_type] = handler
        logger.debug(f"Registered handler for message type: {message_type}")
    
    async def _handle_ping(self, connection_id: str, data: Dict[str, Any]):
        """Handle ping messages"""
        await self.send_personal_message(connection_id, {
            "type": "pong",
            "timestamp": datetime.utcnow().isoformat(),
            "connection_id": connection_id
        })
    
    async def _handle_subscribe(self, connection_id: str, data: Dict[str, Any]):
        """Handle subscription requests"""
        try:
            subscription_type = data.get("subscription_type")
            subscription_id = data.get("subscription_id")
            
            if not subscription_type or not subscription_id:
                await self.send_personal_message(connection_id, {
                    "type": "subscription_error",
                    "message": "subscription_type and subscription_id are required",
                    "timestamp": datetime.utcnow().isoformat()
                })
                return
            
            # Add subscription
            if connection_id in self.connection_metadata:
                self.connection_metadata[connection_id]["subscriptions"].add(
                    f"{subscription_type}:{subscription_id}"
                )
            
            await self.send_personal_message(connection_id, {
                "type": "subscription_confirmed",
                "subscription_type": subscription_type,
                "subscription_id": subscription_id,
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error handling subscription request: {e}")
            await self.send_personal_message(connection_id, {
                "type": "subscription_error",
                "message": "Internal server error",
                "timestamp": datetime.utcnow().isoformat()
            })
    
    async def _handle_unsubscribe(self, connection_id: str, data: Dict[str, Any]):
        """Handle unsubscription requests"""
        try:
            subscription_type = data.get("subscription_type")
            subscription_id = data.get("subscription_id")
            
            if not subscription_type or not subscription_id:
                await self.send_personal_message(connection_id, {
                    "type": "unsubscription_error",
                    "message": "subscription_type and subscription_id are required",
                    "timestamp": datetime.utcnow().isoformat()
                })
                return
            
            # Remove subscription
            if connection_id in self.connection_metadata:
                subscription_key = f"{subscription_type}:{subscription_id}"
                self.connection_metadata[connection_id]["subscriptions"].discard(subscription_key)
            
            await self.send_personal_message(connection_id, {
                "type": "unsubscription_confirmed",
                "subscription_type": subscription_type,
                "subscription_id": subscription_id,
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error handling unsubscription request: {e}")
            await self.send_personal_message(connection_id, {
                "type": "unsubscription_error",
                "message": "Internal server error",
                "timestamp": datetime.utcnow().isoformat()
            })
    
    async def _handle_sync_request(self, connection_id: str, data: Dict[str, Any]):
        """Handle synchronization requests"""
        try:
            sync_type = data.get("sync_type")
            last_sync = data.get("last_sync")
            
            # For now, send a simple sync response
            # In production, implement proper data synchronization
            await self.send_personal_message(connection_id, {
                "type": "sync_response",
                "sync_type": sync_type,
                "last_sync": last_sync,
                "current_sync": datetime.utcnow().isoformat(),
                "data": {},
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error handling sync request: {e}")
            await self.send_personal_message(connection_id, {
                "type": "sync_error",
                "message": "Internal server error",
                "timestamp": datetime.utcnow().isoformat()
            })
    
    async def _handle_offline_data(self, connection_id: str, data: Dict[str, Any]):
        """Handle offline data from clients"""
        try:
            user_id = self.connection_metadata.get(connection_id, {}).get("user_id")
            if not user_id:
                return
            
            # Store offline data
            if user_id not in self.offline_queue:
                self.offline_queue[user_id] = []
            
            offline_item = {
                "id": str(uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "data": data,
                "processed": False
            }
            
            self.offline_queue[user_id].append(offline_item)
            
            # Acknowledge receipt
            await self.send_personal_message(connection_id, {
                "type": "offline_data_received",
                "offline_id": offline_item["id"],
                "timestamp": datetime.utcnow().isoformat()
            })
            
            logger.info(f"Received offline data from user {user_id}: {offline_item['id']}")
            
        except Exception as e:
            logger.error(f"Error handling offline data: {e}")
    
    async def process_offline_queue(self, user_id: str):
        """Process offline queue for a specific user"""
        try:
            if user_id not in self.offline_queue:
                return
            
            offline_items = self.offline_queue[user_id]
            processed_items = []
            
            for item in offline_items:
                if not item["processed"]:
                    try:
                        # Process offline data
                        # In production, implement proper offline data processing
                        item["processed"] = True
                        item["processed_at"] = datetime.utcnow().isoformat()
                        processed_items.append(item)
                        
                        logger.info(f"Processed offline data {item['id']} for user {user_id}")
                        
                    except Exception as e:
                        logger.error(f"Error processing offline data {item['id']}: {e}")
                        item["error"] = str(e)
            
            # Remove processed items
            for item in processed_items:
                offline_items.remove(item)
            
            # Notify user if online
            if user_id in self.user_connections:
                for connection_id in self.user_connections[user_id]:
                    await self.send_personal_message(connection_id, {
                        "type": "offline_data_processed",
                        "processed_count": len(processed_items),
                        "timestamp": datetime.utcnow().isoformat()
                    })
            
        except Exception as e:
            logger.error(f"Error processing offline queue for user {user_id}: {e}")
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        return {
            "total_connections": self.connection_count,
            "active_connections": len(self.active_connections),
            "organization_connections": len(self.organization_connections),
            "user_connections": len(self.user_connections),
            "total_messages": self.message_count,
            "total_errors": self.error_count,
            "offline_queue_size": sum(len(queue) for queue in self.offline_queue.values())
        }
    
    def get_connection_info(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific connection"""
        if connection_id in self.connection_metadata:
            metadata = self.connection_metadata[connection_id].copy()
            metadata["subscriptions"] = list(metadata["subscriptions"])
            return metadata
        return None
    
    async def cleanup_inactive_connections(self, max_inactive_minutes: int = 30):
        """Clean up inactive connections"""
        try:
            current_time = datetime.utcnow()
            inactive_connections = []
            
            for connection_id, metadata in self.connection_metadata.items():
                last_activity = metadata.get("last_activity")
                if last_activity:
                    inactive_minutes = (current_time - last_activity).total_seconds() / 60
                    if inactive_minutes > max_inactive_minutes:
                        inactive_connections.append(connection_id)
            
            for connection_id in inactive_connections:
                await self.disconnect(connection_id)
                logger.info(f"Cleaned up inactive connection {connection_id}")
            
            if inactive_connections:
                logger.info(f"Cleaned up {len(inactive_connections)} inactive connections")
                
        except Exception as e:
            logger.error(f"Error cleaning up inactive connections: {e}")

# Global connection manager instance
connection_manager = ConnectionManager()

class WebSocketEndpoint:
    """WebSocket endpoint for handling connections"""
    
    def __init__(self, manager: ConnectionManager = None):
        self.manager = manager or connection_manager
    
    async def handle_websocket(self, websocket: WebSocket, user_id: str, organization_id: str):
        """Handle WebSocket connection lifecycle"""
        connection_id = None
        
        try:
            # Accept connection
            connection_id = await self.manager.connect(websocket, user_id, organization_id)
            
            # Handle messages
            while True:
                try:
                    message = await websocket.receive_text()
                    await self.manager.handle_message(connection_id, message)
                    
                except WebSocketDisconnect:
                    logger.info(f"WebSocket {connection_id} disconnected by client")
                    break
                    
        except Exception as e:
            logger.error(f"Error in WebSocket connection {connection_id}: {e}")
            
        finally:
            # Clean up connection
            if connection_id:
                await self.manager.disconnect(connection_id)

# Event bus integration
async def broadcast_event_to_organization(event: BaseEvent, organization_id: str):
    """Broadcast an event to all connections in an organization"""
    try:
        message = {
            "type": "event",
            "event_type": event.metadata.event_type.value,
            "event_id": event.metadata.event_id,
            "correlation_id": event.metadata.correlation_id,
            "timestamp": event.metadata.timestamp.isoformat(),
            "payload": event.payload
        }
        
        await connection_manager.broadcast_to_organization(organization_id, message)
        
    except Exception as e:
        logger.error(f"Error broadcasting event to organization {organization_id}: {e}")

async def broadcast_event_to_user(event: BaseEvent, user_id: str):
    """Broadcast an event to all connections of a specific user"""
    try:
        message = {
            "type": "event",
            "event_type": event.metadata.event_type.value,
            "event_id": event.metadata.event_id,
            "correlation_id": event.metadata.correlation_id,
            "timestamp": event.metadata.timestamp.isoformat(),
            "payload": event.payload
        }
        
        await connection_manager.broadcast_to_user(user_id, message)
        
    except Exception as e:
        logger.error(f"Error broadcasting event to user {user_id}: {e}")
