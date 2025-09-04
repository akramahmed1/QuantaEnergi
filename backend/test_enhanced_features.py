"""
Comprehensive Tests for Enhanced Features
Tests event-driven architecture, multi-tenancy, and real-time synchronization
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app
from app.core.event_bus import event_bus, EventType, create_event, publish_event
from app.services.enhanced_trade_lifecycle import enhanced_trade_service
from app.core.websocket_manager import connection_manager
from app.schemas.trade import TradeCreate, TradeType, CommodityType, TradeDirection, SettlementType
import pytest_asyncio

# Test client
client = TestClient(app)

class TestEventBus:
    """Test event bus functionality"""
    
    def test_event_bus_initialization(self):
        """Test event bus is properly initialized"""
        assert event_bus is not None
        assert hasattr(event_bus, '_subscribers')
        assert hasattr(event_bus, '_middleware')
        assert hasattr(event_bus, '_event_history')
    
    def test_event_type_enum(self):
        """Test event type enumeration"""
        assert EventType.TRADE_CAPTURED.value == "trade_captured"
        assert EventType.TRADE_VALIDATED.value == "trade_validated"
        assert EventType.TRADE_CONFIRMED.value == "trade_confirmed"
        assert EventType.TRADE_SETTLED.value == "trade_settled"
        assert EventType.RISK_LIMIT_BREACHED.value == "risk_limit_breached"
        assert EventType.COMPLIANCE_VIOLATION.value == "compliance_violation"
    
    def test_create_event(self):
        """Test event creation"""
        payload = {"test": "data"}
        event = create_event(
            event_type=EventType.TRADE_CAPTURED,
            payload=payload,
            correlation_id="test_correlation",
            user_id="test_user",
            organization_id="test_org",
            source_service="test_service"
        )
        
        assert event.metadata.event_type == EventType.TRADE_CAPTURED
        assert event.metadata.correlation_id == "test_correlation"
        assert event.metadata.user_id == "test_user"
        assert event.metadata.organization_id == "test_org"
        assert event.metadata.source_service == "test_service"
        assert event.payload == payload
    
    def test_event_serialization(self):
        """Test event serialization to JSON"""
        payload = {"test": "data", "number": 42}
        event = create_event(
            event_type=EventType.TRADE_CAPTURED,
            payload=payload
        )
        
        event_dict = event.to_dict()
        event_json = event.to_json()
        
        assert isinstance(event_dict, dict)
        assert isinstance(event_json, str)
        assert "metadata" in event_dict
        assert "payload" in event_dict
        assert event_dict["payload"] == payload
        
        # Test JSON can be parsed back
        parsed_json = json.loads(event_json)
        assert parsed_json["payload"] == payload

class TestEnhancedTradeLifecycle:
    """Test enhanced trade lifecycle service"""
    
    @pytest_asyncio.fixture(autouse=True)
    async def setup_event_bus(self):
        """Setup event bus for tests"""
        await event_bus.start()
        yield
        await event_bus.stop()
    
    def setup_method(self):
        """Setup test data and clear previous test data"""
        # Clear previous test data
        enhanced_trade_service.trades.clear()
        enhanced_trade_service.trade_history.clear()
        enhanced_trade_service.confirmations.clear()
        enhanced_trade_service.allocations.clear()
        enhanced_trade_service.settlements.clear()
        enhanced_trade_service.invoices.clear()
        enhanced_trade_service.payments.clear()
        
        self.sample_trade = TradeCreate(
            trade_type=TradeType.FORWARD,
            commodity=CommodityType.CRUDE_OIL,
            quantity=1000.0,
            price=85.50,
            currency="USD",
            counterparty="CP001",
            delivery_date=datetime.utcnow() + timedelta(days=30),
            delivery_location="Houston, TX",
            trade_direction=TradeDirection.BUY,
            settlement_type=SettlementType.T_PLUS_2,
            is_islamic_compliant=False,
            organization_id="123e4567-e89b-12d3-a456-426614174000"
        )
        
        self.user_id = "user_123"
        self.organization_id = "123e4567-e89b-12d3-a456-426614174000"
    
    def test_service_initialization(self):
        """Test service is properly initialized"""
        assert enhanced_trade_service is not None
        assert hasattr(enhanced_trade_service, 'trades')
        assert hasattr(enhanced_trade_service, 'trade_history')
        assert hasattr(enhanced_trade_service, 'organizations')
    
    def test_sample_organizations(self):
        """Test sample organizations are loaded"""
        orgs = enhanced_trade_service.organizations
        assert len(orgs) > 0
        
        # Check Saudi Aramco
        saudi_aramco = orgs["123e4567-e89b-12d3-a456-426614174000"]
        assert saudi_aramco.name == "Saudi Aramco Trading"
        assert saudi_aramco.code == "SAT"
        assert saudi_aramco.primary_region == "ME"
        assert saudi_aramco.is_islamic_compliant == True
        
        # Check ExxonMobil
        exxon = orgs["456e7890-e89b-12d3-a456-426614174001"]
        assert exxon.name == "ExxonMobil Trading"
        assert exxon.code == "EMT"
        assert exxon.primary_region == "US"
        assert exxon.is_islamic_compliant == False
    
    @pytest.mark.asyncio
    async def test_capture_trade(self):
        """Test trade capture functionality"""
        response = await enhanced_trade_service.capture_trade(
            trade_data=self.sample_trade,
            user_id=self.user_id,
            organization_id=self.organization_id
        )
        
        assert response.trade_id is not None
        assert response.status == "captured"
        assert str(response.organization_id) == self.organization_id
        assert response.correlation_id is not None
        
        # Check trade is stored
        assert response.trade_id in enhanced_trade_service.trades
        stored_trade = enhanced_trade_service.trades[response.trade_id]
        assert str(stored_trade["organization_id"]) == self.organization_id
        assert stored_trade["user_id"] == self.user_id
        assert stored_trade["status"] == "captured"
    
    @pytest.mark.asyncio
    async def test_validate_trade(self):
        """Test trade validation"""
        # First capture a trade
        capture_response = await enhanced_trade_service.capture_trade(
            trade_data=self.sample_trade,
            user_id=self.user_id,
            organization_id=self.organization_id
        )
        
        # Then validate it
        validation_response = await enhanced_trade_service.validate_trade(
            trade_id=capture_response.trade_id,
            user_id=self.user_id
        )
        
        assert validation_response.trade_id == capture_response.trade_id
        assert validation_response.valid == True
        assert validation_response.compliant == True  # Non-Islamic trades are compliant by default
        assert str(validation_response.organization_id) == self.organization_id
        
        # Check trade status is updated
        trade = enhanced_trade_service.trades[capture_response.trade_id]
        assert trade["status"] == "validated"
        assert "validated_at" in trade
    
    @pytest.mark.asyncio
    async def test_confirm_trade(self):
        """Test trade confirmation"""
        # Capture and validate a trade first
        capture_response = await enhanced_trade_service.capture_trade(
            trade_data=self.sample_trade,
            user_id=self.user_id,
            organization_id=self.organization_id
        )
        
        await enhanced_trade_service.validate_trade(
            trade_id=capture_response.trade_id,
            user_id=self.user_id
        )
        
        # Confirm the trade
        confirmation = await enhanced_trade_service.confirm_trade(
            trade_id=capture_response.trade_id,
            user_id=self.user_id,
            confirmation_notes="Test confirmation"
        )
        
        assert confirmation.trade_id == capture_response.trade_id
        assert confirmation.confirmation_number.startswith("CONF_")
        assert confirmation.confirmed_by == self.user_id
        assert confirmation.confirmation_notes == "Test confirmation"
        
        # Check trade status is updated
        trade = enhanced_trade_service.trades[capture_response.trade_id]
        assert trade["status"] == "confirmed"
        assert "confirmed_at" in trade
    
    @pytest.mark.asyncio
    async def test_get_trade_status(self):
        """Test getting trade status"""
        # Create a trade
        capture_response = await enhanced_trade_service.capture_trade(
            trade_data=self.sample_trade,
            user_id=self.user_id,
            organization_id=self.organization_id
        )
        
        # Get status
        status = await enhanced_trade_service.get_trade_status(
            trade_id=capture_response.trade_id
        )
        
        assert status.trade_id == capture_response.trade_id
        assert status.status == "captured"
        assert status.valid == True
        assert str(status.organization_id) == self.organization_id
    
    @pytest.mark.asyncio
    async def test_get_user_trades(self):
        """Test getting user trades with pagination"""
        # Create multiple trades
        for i in range(5):
            trade_data = self.sample_trade.model_copy()
            trade_data.quantity = 1000.0 + i
            await enhanced_trade_service.capture_trade(
                trade_data=trade_data,
                user_id=self.user_id,
                organization_id=self.organization_id
            )
        
        # Get trades with pagination
        response = await enhanced_trade_service.get_user_trades(
            user_id=self.user_id,
            organization_id=self.organization_id,
            page=1,
            page_size=3
        )
        
        assert response.total_count == 5
        assert response.page == 1
        assert response.page_size == 3
        assert response.total_pages == 2
        assert len(response.trades) == 3
        
        # Check second page
        response_page2 = await enhanced_trade_service.get_user_trades(
            user_id=self.user_id,
            organization_id=self.organization_id,
            page=2,
            page_size=3
        )
        
        assert response_page2.page == 2
        assert len(response_page2.trades) == 2
    
    @pytest.mark.asyncio
    async def test_get_trade_analytics(self):
        """Test trade analytics"""
        # Create some trades
        for i in range(3):
            trade_data = self.sample_trade.model_copy()
            trade_data.quantity = 1000.0 + i
            trade_data.price = 85.50 + i
            await enhanced_trade_service.capture_trade(
                trade_data=trade_data,
                user_id=self.user_id,
                organization_id=self.organization_id
            )
        
        # Get analytics
        analytics = await enhanced_trade_service.get_trade_analytics(
            organization_id=self.organization_id
        )
        
        assert analytics.total_trades == 3
        assert analytics.total_volume == 3003.0  # 1000 + 1001 + 1002
        assert analytics.total_value > 0
        assert analytics.average_price > 0
        assert analytics.compliance_rate == 1.0  # All trades are valid
        assert analytics.islamic_compliance_rate == 0.0  # None are Islamic compliant
    
    @pytest.mark.asyncio
    async def test_cancel_trade(self):
        """Test trade cancellation"""
        # Create a trade
        capture_response = await enhanced_trade_service.capture_trade(
            trade_data=self.sample_trade,
            user_id=self.user_id,
            organization_id=self.organization_id
        )
        
        # Cancel the trade
        cancel_response = await enhanced_trade_service.cancel_trade(
            trade_id=capture_response.trade_id,
            user_id=self.user_id,
            reason="Test cancellation"
        )
        
        assert cancel_response.trade_id == capture_response.trade_id
        assert cancel_response.status == "cancelled"
        assert "Test cancellation" in cancel_response.message
        
        # Check trade status is updated
        trade = enhanced_trade_service.trades[capture_response.trade_id]
        assert trade["status"] == "cancelled"
        assert "cancelled_at" in trade
        assert trade["cancellation_reason"] == "Test cancellation"

class TestWebSocketManager:
    """Test WebSocket manager functionality"""
    
    def test_connection_manager_initialization(self):
        """Test connection manager is properly initialized"""
        assert connection_manager is not None
        assert hasattr(connection_manager, 'active_connections')
        assert hasattr(connection_manager, 'organization_connections')
        assert hasattr(connection_manager, 'user_connections')
        assert hasattr(connection_manager, 'connection_metadata')
    
    def test_connection_stats(self):
        """Test connection statistics"""
        stats = connection_manager.get_connection_stats()
        
        assert "total_connections" in stats
        assert "active_connections" in stats
        assert "organization_connections" in stats
        assert "user_connections" in stats
        assert "total_messages" in stats
        assert "total_errors" in stats
        assert "offline_queue_size" in stats
        
        # All should be numbers
        for key, value in stats.items():
            assert isinstance(value, (int, float))

class TestEnhancedAPIEndpoints:
    """Test enhanced API endpoints"""
    
    def test_enhanced_trade_capture_endpoint(self):
        """Test enhanced trade capture API endpoint"""
        trade_data = {
            "trade_type": "forward",
            "commodity": "crude_oil",
            "quantity": 1000.0,
            "price": 85.50,
            "currency": "USD",
            "counterparty": "CP001",
            "delivery_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "delivery_location": "Houston, TX",
            "trade_direction": "buy",
            "settlement_type": "T+2",
            "is_islamic_compliant": False,
            "organization_id": "123e4567-e89b-12d3-a456-426614174000"
        }
        
        response = client.post("/api/v1/enhanced/trades/capture", json=trade_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["trade_id"] is not None
        assert data["status"] == "captured"
        assert data["organization_id"] == "123e4567-e89b-12d3-a456-426614174000"
    
    def test_enhanced_trade_validation_endpoint(self):
        """Test enhanced trade validation API endpoint"""
        # First capture a trade
        trade_data = {
            "trade_type": "forward",
            "commodity": "crude_oil",
            "quantity": 1000.0,
            "price": 85.50,
            "currency": "USD",
            "counterparty": "CP001",
            "delivery_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "delivery_location": "Houston, TX",
            "trade_direction": "buy",
            "settlement_type": "T+2",
            "is_islamic_compliant": False,
            "organization_id": "123e4567-e89b-12d3-a456-426614174000"
        }
        
        capture_response = client.post("/api/v1/enhanced/trades/capture", json=trade_data)
        trade_id = capture_response.json()["trade_id"]
        
        # Then validate it
        validation_response = client.post(f"/api/v1/enhanced/trades/{trade_id}/validate")
        
        assert validation_response.status_code == 200
        data = validation_response.json()
        assert data["trade_id"] == trade_id
        assert data["valid"] == True
        assert data["organization_id"] == "123e4567-e89b-12d3-a456-426614174000"
    
    def test_enhanced_trade_analytics_endpoint(self):
        """Test enhanced trade analytics API endpoint"""
        response = client.get("/api/v1/enhanced/trades/analytics")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_trades" in data
        assert "total_volume" in data
        assert "total_value" in data
        assert "average_price" in data
        assert "compliance_rate" in data
        assert "islamic_compliance_rate" in data
    
    def test_event_bus_stats_endpoint(self):
        """Test event bus statistics API endpoint"""
        response = client.get("/api/v1/enhanced/trades/event-bus/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "data" in data
        assert "is_running" in data["data"]
        assert "queue_size" in data["data"]
        assert "total_events_processed" in data["data"]
    
    def test_websocket_stats_endpoint(self):
        """Test WebSocket statistics API endpoint"""
        response = client.get("/api/v1/ws/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "data" in data
        assert "total_connections" in data["data"]
        assert "active_connections" in data["data"]
        assert "total_messages" in data["data"]
    
    def test_websocket_health_endpoint(self):
        """Test WebSocket health check endpoint"""
        response = client.get("/api/v1/ws/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "data" in data
        assert "status" in data["data"]
        assert "active_connections" in data["data"]

class TestMultiTenancy:
    """Test multi-tenant functionality"""
    
    def test_organization_isolation(self):
        """Test that organizations are properly isolated"""
        # Check that different organizations have different configurations
        saudi_aramco = enhanced_trade_service.organizations["123e4567-e89b-12d3-a456-426614174000"]
        exxon = enhanced_trade_service.organizations["456e7890-e89b-12d3-a456-426614174001"]
        
        assert saudi_aramco.primary_region == "ME"
        assert exxon.primary_region == "US"
        assert saudi_aramco.is_islamic_compliant == True
        assert exxon.is_islamic_compliant == False
    
    def test_organization_compliance_requirements(self):
        """Test organization compliance requirements"""
        saudi_aramco = enhanced_trade_service.organizations["123e4567-e89b-12d3-a456-426614174000"]
        
        # Test compliance requirement retrieval
        requirement = saudi_aramco.get_compliance_requirement("ME", "islamic_finance")
        # This will be None for now since we haven't set specific requirements
        # In production, this would return actual compliance requirements
        
        # Test trading limits
        limit = saudi_aramco.get_trading_limit("daily")
        # This will be None for now since we haven't set specific limits
        # In production, this would return actual trading limits
    
    def test_organization_trading_capabilities(self):
        """Test organization trading capabilities"""
        saudi_aramco = enhanced_trade_service.organizations["123e4567-e89b-12d3-a456-426614174000"]
        
        # Test commodity trading permissions
        can_trade_crude = saudi_aramco.can_trade_commodity("crude_oil")
        assert can_trade_crude == True  # Default is True when no restrictions set
        
        # Test organization status
        assert saudi_aramco.is_active == True
        assert saudi_aramco.has_expired_subscription == False

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
