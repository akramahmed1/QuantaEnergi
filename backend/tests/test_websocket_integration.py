"""
Test WebSocket Integration for Real-Time ETRM/CTRM Operations
Tests real-time data sync, observer pattern, and connection management
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from fastapi.testclient import TestClient
from fastapi import FastAPI, WebSocket

from app.core.websocket_enhanced import (
    EnhancedWebSocketManager, 
    WebSocketObserver, 
    MessageType, 
    WebSocketMessage
)

class TestWebSocketObserver:
    """Test WebSocket Observer Pattern"""
    
    @pytest.fixture
    def observer(self):
        """Create observer instance"""
        return WebSocketObserver()
    
    @pytest.fixture
    def mock_websocket(self):
        """Create mock websocket"""
        websocket = AsyncMock(spec=WebSocket)
        websocket.send_text = AsyncMock()
        return websocket
    
    @pytest.mark.asyncio
    async def test_subscribe_websocket(self, observer, mock_websocket):
        """Test websocket subscription to topic"""
        topic = "market_data"
        
        observer.subscribe(mock_websocket, topic)
        
        assert topic in observer.subscribers
        assert mock_websocket in observer.subscribers[topic]
        assert topic in observer.connection_subscriptions[mock_websocket]
    
    @pytest.mark.asyncio
    async def test_unsubscribe_websocket(self, observer, mock_websocket):
        """Test websocket unsubscription from topic"""
        topic = "market_data"
        
        # Subscribe first
        observer.subscribe(mock_websocket, topic)
        assert mock_websocket in observer.subscribers[topic]
        
        # Unsubscribe
        observer.unsubscribe(mock_websocket, topic)
        assert mock_websocket not in observer.subscribers[topic]
        assert topic not in observer.connection_subscriptions[mock_websocket]
    
    @pytest.mark.asyncio
    async def test_notify_subscribers(self, observer, mock_websocket):
        """Test notifying subscribers"""
        topic = "market_data"
        observer.subscribe(mock_websocket, topic)
        
        message = WebSocketMessage(
            type=MessageType.MARKET_DATA,
            data={"price": 85.50, "commodity": "crude_oil"},
            timestamp=datetime.utcnow(),
            message_id="test-123"
        )
        
        await observer.notify(topic, message)
        
        # Verify message was sent
        mock_websocket.send_text.assert_called_once()
        call_args = mock_websocket.send_text.call_args[0][0]
        message_data = json.loads(call_args)
        
        assert message_data["type"] == "market_data"
        assert message_data["data"]["price"] == 85.50
        assert message_data["topic"] == topic
    
    @pytest.mark.asyncio
    async def test_handle_ping_message(self, observer, mock_websocket):
        """Test handling ping message"""
        ping_data = {"type": "ping", "data": {}}
        
        await observer.handle_message(mock_websocket, json.dumps(ping_data))
        
        # Should send pong response
        mock_websocket.send_text.assert_called_once()
        call_args = mock_websocket.send_text.call_args[0][0]
        response_data = json.loads(call_args)
        
        assert response_data["type"] == "pong"
    
    @pytest.mark.asyncio
    async def test_handle_subscribe_message(self, observer, mock_websocket):
        """Test handling subscribe message"""
        subscribe_data = {"type": "subscribe", "topic": "trades"}
        
        await observer.handle_message(mock_websocket, json.dumps(subscribe_data))
        
        # Should be subscribed to trades topic
        assert "trades" in observer.connection_subscriptions[mock_websocket]
        assert mock_websocket in observer.subscribers["trades"]
        
        # Should send success response
        mock_websocket.send_text.assert_called()
        call_args = mock_websocket.send_text.call_args[0][0]
        response_data = json.loads(call_args)
        
        assert response_data["type"] == "data_update"
        assert "Subscribed to trades" in response_data["data"]["message"]

class TestEnhancedWebSocketManager:
    """Test Enhanced WebSocket Manager"""
    
    @pytest.fixture
    def manager(self):
        """Create manager instance"""
        return EnhancedWebSocketManager()
    
    @pytest.fixture
    def mock_websocket(self):
        """Create mock websocket"""
        websocket = AsyncMock(spec=WebSocket)
        websocket.accept = AsyncMock()
        websocket.send_text = AsyncMock()
        return websocket
    
    @pytest.mark.asyncio
    async def test_connect_websocket(self, manager, mock_websocket):
        """Test websocket connection"""
        user_id = "test_user"
        organization_id = "test_org"
        
        connection_id = await manager.connect(mock_websocket, user_id, organization_id)
        
        assert connection_id is not None
        assert connection_id in manager.active_connections
        assert connection_id in manager.organization_connections[organization_id]
        assert connection_id in manager.user_connections[user_id]
        
        # Verify welcome message was sent
        mock_websocket.send_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_disconnect_websocket(self, manager, mock_websocket):
        """Test websocket disconnection"""
        user_id = "test_user"
        organization_id = "test_org"
        
        # Connect first
        connection_id = await manager.connect(mock_websocket, user_id, organization_id)
        
        # Disconnect
        await manager.disconnect(connection_id)
        
        assert connection_id not in manager.active_connections
        assert connection_id not in manager.organization_connections[organization_id]
        assert connection_id not in manager.user_connections[user_id]
    
    @pytest.mark.asyncio
    async def test_broadcast_to_organization(self, manager, mock_websocket):
        """Test broadcasting to organization"""
        user_id = "test_user"
        organization_id = "test_org"
        
        # Connect websocket
        connection_id = await manager.connect(mock_websocket, user_id, organization_id)
        
        # Create message
        message = WebSocketMessage(
            type=MessageType.DATA_UPDATE,
            data={"message": "Test broadcast"},
            timestamp=datetime.utcnow(),
            message_id="test-123"
        )
        
        # Broadcast to organization
        await manager.broadcast_to_organization(organization_id, message)
        
        # Verify message was sent
        assert mock_websocket.send_text.call_count >= 2  # Welcome + broadcast
    
    @pytest.mark.asyncio
    async def test_broadcast_to_topic(self, manager, mock_websocket):
        """Test broadcasting to topic"""
        user_id = "test_user"
        organization_id = "test_org"
        topic = "market_data"
        
        # Connect websocket
        connection_id = await manager.connect(mock_websocket, user_id, organization_id)
        
        # Subscribe to topic
        subscribe_data = {"type": "subscribe", "topic": topic}
        await manager.handle_message(connection_id, json.dumps(subscribe_data))
        
        # Create message
        message = WebSocketMessage(
            type=MessageType.MARKET_DATA,
            data={"price": 85.50},
            timestamp=datetime.utcnow(),
            message_id="test-123"
        )
        
        # Broadcast to topic
        await manager.broadcast_to_topic(topic, message)
        
        # Verify message was sent
        assert mock_websocket.send_text.call_count >= 3  # Welcome + subscribe + broadcast
    
    def test_get_connection_stats(self, manager):
        """Test getting connection statistics"""
        stats = manager.get_connection_stats()
        
        assert "active_connections" in stats
        assert "total_messages" in stats
        assert "total_errors" in stats
        assert "organizations" in stats
        assert "users" in stats
        assert "background_tasks" in stats

@pytest.mark.asyncio
async def test_integration_10_realtime_updates():
    """Integration test with 10 real-time updates as specified in PRD"""
    manager = EnhancedWebSocketManager()
    mock_websocket = AsyncMock(spec=WebSocket)
    mock_websocket.accept = AsyncMock()
    mock_websocket.send_text = AsyncMock()
    
    user_id = "integration_test_user"
    organization_id = "integration_test_org"
    
    try:
        # Update 1: Connect websocket
        connection_id = await manager.connect(mock_websocket, user_id, organization_id)
        assert connection_id is not None
        
        # Update 2: Subscribe to market data
        subscribe_data = {"type": "subscribe", "topic": "market_data"}
        await manager.handle_message(connection_id, json.dumps(subscribe_data))
        
        # Update 3: Subscribe to trades
        subscribe_data = {"type": "subscribe", "topic": "trades"}
        await manager.handle_message(connection_id, json.dumps(subscribe_data))
        
        # Update 4: Subscribe to risk alerts
        subscribe_data = {"type": "subscribe", "topic": "risk_alerts"}
        await manager.handle_message(connection_id, json.dumps(subscribe_data))
        
        # Update 5: Send ping
        ping_data = {"type": "ping", "data": {}}
        await manager.handle_message(connection_id, json.dumps(ping_data))
        
        # Update 6: Broadcast market data
        market_message = WebSocketMessage(
            type=MessageType.MARKET_DATA,
            data={"crude_oil": {"price": 85.50, "change": 0.25}},
            timestamp=datetime.utcnow(),
            message_id="test-1"
        )
        await manager.broadcast_to_topic("market_data", market_message)
        
        # Update 7: Broadcast trade update
        trade_message = WebSocketMessage(
            type=MessageType.TRADE_UPDATE,
            data={"trade_id": "TRD-001", "status": "confirmed"},
            timestamp=datetime.utcnow(),
            message_id="test-2"
        )
        await manager.broadcast_to_topic("trades", trade_message)
        
        # Update 8: Broadcast risk alert
        risk_message = WebSocketMessage(
            type=MessageType.RISK_ALERT,
            data={"alert_type": "position_limit", "severity": "medium"},
            timestamp=datetime.utcnow(),
            message_id="test-3"
        )
        await manager.broadcast_to_topic("risk_alerts", risk_message)
        
        # Update 9: Broadcast to organization
        org_message = WebSocketMessage(
            type=MessageType.DATA_UPDATE,
            data={"message": "Organization update"},
            timestamp=datetime.utcnow(),
            message_id="test-4"
        )
        await manager.broadcast_to_organization(organization_id, org_message)
        
        # Update 10: Get connection stats
        stats = manager.get_connection_stats()
        assert stats["active_connections"] >= 1
        assert stats["total_messages"] >= 0
        
        # Cleanup
        await manager.disconnect(connection_id)
        
        print("✅ Integration test with 10 real-time updates completed successfully")
        
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        raise

if __name__ == "__main__":
    # Run the integration test
    asyncio.run(test_integration_10_realtime_updates())
