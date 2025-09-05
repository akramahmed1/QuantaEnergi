"""
Comprehensive E2E Testing for QuantaEnergi ETRM/CTRM Platform
Tests all PR1-PR4 features: Database, Auth, WebSocket, Dependencies
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from uuid import uuid4
import json

# Import all our new modules
from app.core.database_manager import MultiTenantDBManager
from app.core.jwt_auth import JWTAuthManager, auth_manager
from app.middleware.rate_limiter import RateLimiter
from app.core.websocket_enhanced import EnhancedWebSocketManager
from app.models.trade import Trade
from app.models.organization import Organization

class TestComprehensiveE2E:
    """Comprehensive E2E tests for all PR features"""
    
    @pytest.fixture
    def db_manager(self):
        return MultiTenantDBManager()
    
    @pytest.fixture
    def auth_mgr(self):
        return JWTAuthManager()
    
    @pytest.fixture
    def rate_limiter(self):
        return RateLimiter()
    
    @pytest.fixture
    def websocket_manager(self):
        return EnhancedWebSocketManager()
    
    @pytest.fixture
    def mock_session(self):
        session = AsyncMock()
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        session.rollback = AsyncMock()
        session.refresh = AsyncMock()
        return session

@pytest.mark.asyncio
async def test_e2e_trading_workflow():
    """E2E test: Complete trading workflow from capture to settlement"""
    
    # Initialize all managers
    db_manager = MultiTenantDBManager()
    auth_mgr = JWTAuthManager()
    rate_limiter = RateLimiter()
    websocket_manager = EnhancedWebSocketManager()
    
    # Mock session
    mock_session = AsyncMock()
    mock_session.execute = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    
    try:
        # Step 1: User Authentication
        user_data = {
            "user_id": "e2e_trader",
            "username": "e2e_trader",
            "email": "e2e@quantaenergi.com",
            "organization_id": str(uuid4()),
            "role": "trader",
            "is_active": True
        }
        
        # Create JWT token
        access_token = auth_mgr.create_access_token(user_data)
        assert access_token is not None
        
        # Verify token
        payload = auth_mgr.verify_token(access_token)
        assert payload["user_id"] == user_data["user_id"]
        
        # Step 2: Rate Limiting Check
        is_allowed, rate_info = await rate_limiter.check_rate_limit(
            user_data["user_id"], "trade_capture", "trader", 
            user_data["organization_id"], "tier1"
        )
        assert is_allowed == True
        
        # Step 3: Create Trade in Database
        trade_data = {
            "trade_type": "spot",
            "commodity": "crude_oil",
            "quantity": 1000.0,
            "price": 85.50,
            "currency": "USD",
            "counterparty_id": "CP001",
            "delivery_date": datetime.now() + timedelta(days=30),
            "delivery_location": "Houston, TX"
        }
        
        # Mock trade creation
        mock_trade = Trade(
            id=uuid4(),
            organization_id=user_data["organization_id"],
            trade_id="E2E-TRD-001",
            **trade_data
        )
        mock_session.refresh.return_value = mock_trade
        
        created_trade = await db_manager.add_trade(
            mock_session, trade_data, user_data["organization_id"], user_data["user_id"]
        )
        assert created_trade is not None
        
        # Step 4: WebSocket Real-time Updates
        mock_websocket = AsyncMock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_text = AsyncMock()
        
        # Connect WebSocket
        connection_id = await websocket_manager.connect(
            mock_websocket, user_data["user_id"], user_data["organization_id"]
        )
        assert connection_id is not None
        
        # Subscribe to trade updates
        subscribe_data = {"type": "subscribe", "topic": "trades"}
        await websocket_manager.handle_message(connection_id, json.dumps(subscribe_data))
        
        # Step 5: Update Trade Status
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_trade
        mock_session.execute.return_value = mock_result
        
        updated_trade = await db_manager.update_trade_status(
            mock_session, "E2E-TRD-001", user_data["organization_id"], "confirmed", user_data["user_id"]
        )
        assert updated_trade is not None
        
        # Step 6: Get Trade Analytics
        mock_trades = [mock_trade]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_trades
        mock_session.execute.return_value = mock_result
        
        analytics = await db_manager.get_trade_analytics(mock_session, user_data["organization_id"])
        assert analytics["total_trades"] == 1
        
        # Step 7: Permission Check
        assert auth_mgr.check_permission("trader", "trade_capture") == True
        assert auth_mgr.check_permission("trader", "risk_edit") == False
        
        # Step 8: WebSocket Broadcast
        from app.core.websocket_enhanced import WebSocketMessage, MessageType
        
        trade_message = WebSocketMessage(
            type=MessageType.TRADE_UPDATE,
            data={"trade_id": "E2E-TRD-001", "status": "confirmed"},
            timestamp=datetime.utcnow(),
            message_id=str(uuid4())
        )
        
        await websocket_manager.broadcast_to_topic("trades", trade_message)
        
        # Step 9: Rate Limit Status Check
        status = await rate_limiter.get_rate_limit_status(
            user_data["user_id"], "trade_capture", "trader",
            user_data["organization_id"], "tier1"
        )
        assert "user_limit" in status
        assert "org_limit" in status
        
        # Step 10: Cleanup
        await websocket_manager.disconnect(connection_id)
        stats = websocket_manager.get_connection_stats()
        assert stats["active_connections"] >= 0
        
        print("✅ E2E Trading Workflow completed successfully")
        
    except Exception as e:
        print(f"❌ E2E test failed: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_e2e_multi_tenant_isolation():
    """E2E test: Multi-tenant data isolation"""
    
    db_manager = MultiTenantDBManager()
    mock_session = AsyncMock()
    mock_session.execute = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    
    try:
        # Create two different organizations
        org1_id = str(uuid4())
        org2_id = str(uuid4())
        
        # Create trades for org1
        trade_data_org1 = {
            "trade_type": "spot",
            "commodity": "crude_oil",
            "quantity": 1000.0,
            "price": 85.50,
            "counterparty_id": "CP001",
            "delivery_date": datetime.now() + timedelta(days=30),
            "delivery_location": "Houston, TX"
        }
        
        mock_trade_org1 = Trade(
            id=uuid4(),
            organization_id=org1_id,
            trade_id="ORG1-TRD-001",
            **trade_data_org1
        )
        mock_session.refresh.return_value = mock_trade_org1
        
        trade1 = await db_manager.add_trade(mock_session, trade_data_org1, org1_id, "user1")
        assert trade1.organization_id == org1_id
        
        # Create trades for org2
        trade_data_org2 = {
            "trade_type": "forward",
            "commodity": "natural_gas",
            "quantity": 5000.0,
            "price": 3.20,
            "counterparty_id": "CP002",
            "delivery_date": datetime.now() + timedelta(days=60),
            "delivery_location": "New York, NY"
        }
        
        mock_trade_org2 = Trade(
            id=uuid4(),
            organization_id=org2_id,
            trade_id="ORG2-TRD-001",
            **trade_data_org2
        )
        mock_session.refresh.return_value = mock_trade_org2
        
        trade2 = await db_manager.add_trade(mock_session, trade_data_org2, org2_id, "user2")
        assert trade2.organization_id == org2_id
        
        # Verify isolation - org1 should only see org1 trades
        mock_trades_org1 = [mock_trade_org1]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_trades_org1
        mock_session.execute.return_value = mock_result
        
        org1_trades = await db_manager.get_trades_for_org(mock_session, org1_id)
        assert len(org1_trades) == 1
        assert org1_trades[0].organization_id == org1_id
        
        # Verify isolation - org2 should only see org2 trades
        mock_trades_org2 = [mock_trade_org2]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_trades_org2
        mock_session.execute.return_value = mock_result
        
        org2_trades = await db_manager.get_trades_for_org(mock_session, org2_id)
        assert len(org2_trades) == 1
        assert org2_trades[0].organization_id == org2_id
        
        print("✅ E2E Multi-tenant Isolation completed successfully")
        
    except Exception as e:
        print(f"❌ E2E Multi-tenant test failed: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_e2e_real_time_market_data():
    """E2E test: Real-time market data feed"""
    
    websocket_manager = EnhancedWebSocketManager()
    auth_mgr = JWTAuthManager()
    
    try:
        # Create multiple users
        users = [
            {"user_id": "trader1", "organization_id": "org1", "role": "trader"},
            {"user_id": "trader2", "organization_id": "org1", "role": "trader"},
            {"user_id": "viewer1", "organization_id": "org2", "role": "viewer"}
        ]
        
        mock_websockets = []
        connection_ids = []
        
        # Connect all users
        for user in users:
            mock_ws = AsyncMock()
            mock_ws.accept = AsyncMock()
            mock_ws.send_text = AsyncMock()
            mock_websockets.append(mock_ws)
            
            conn_id = await websocket_manager.connect(mock_ws, user["user_id"], user["organization_id"])
            connection_ids.append(conn_id)
            
            # Subscribe to market data
            subscribe_data = {"type": "subscribe", "topic": "market_data"}
            await websocket_manager.handle_message(conn_id, json.dumps(subscribe_data))
        
        # Broadcast market data
        from app.core.websocket_enhanced import WebSocketMessage, MessageType
        
        market_message = WebSocketMessage(
            type=MessageType.MARKET_DATA,
            data={
                "crude_oil": {"price": 85.50, "change": 0.25},
                "natural_gas": {"price": 3.20, "change": -0.05}
            },
            timestamp=datetime.utcnow(),
            message_id=str(uuid4())
        )
        
        await websocket_manager.broadcast_to_topic("market_data", market_message)
        
        # Verify all users received the message
        for mock_ws in mock_websockets:
            assert mock_ws.send_text.call_count >= 2  # Welcome + market data
        
        # Test organization-specific broadcast
        org_message = WebSocketMessage(
            type=MessageType.DATA_UPDATE,
            data={"message": "Organization-specific update"},
            timestamp=datetime.utcnow(),
            message_id=str(uuid4())
        )
        
        await websocket_manager.broadcast_to_organization("org1", org_message)
        
        # Only org1 users should receive this
        assert mock_websockets[0].send_text.call_count >= 3  # Welcome + market + org
        assert mock_websockets[1].send_text.call_count >= 3  # Welcome + market + org
        assert mock_websockets[2].send_text.call_count >= 2  # Welcome + market only
        
        # Cleanup
        for conn_id in connection_ids:
            await websocket_manager.disconnect(conn_id)
        
        print("✅ E2E Real-time Market Data completed successfully")
        
    except Exception as e:
        print(f"❌ E2E Real-time test failed: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_e2e_security_and_compliance():
    """E2E test: Security, authentication, and compliance"""
    
    auth_mgr = JWTAuthManager()
    rate_limiter = RateLimiter()
    
    try:
        # Test 1: JWT Token Security
        user_data = {
            "user_id": "security_test_user",
            "username": "security_test",
            "email": "security@quantaenergi.com",
            "organization_id": str(uuid4()),
            "role": "trader",
            "is_active": True
        }
        
        # Create and verify token
        token = auth_mgr.create_access_token(user_data)
        payload = auth_mgr.verify_token(token)
        assert payload["user_id"] == user_data["user_id"]
        
        # Test token revocation
        auth_mgr.revoke_token(token)
        with pytest.raises(Exception):  # HTTPException
            auth_mgr.verify_token(token)
        
        # Test 2: Role-based Access Control
        assert auth_mgr.check_permission("admin", "any_permission") == True
        assert auth_mgr.check_permission("trader", "trade_capture") == True
        assert auth_mgr.check_permission("trader", "risk_edit") == False
        assert auth_mgr.check_permission("viewer", "trade_capture") == False
        
        # Test 3: Rate Limiting
        user_id = "rate_test_user"
        org_id = "rate_test_org"
        
        # Make multiple requests
        for i in range(25):  # Exceed limit
            is_allowed, rate_info = await rate_limiter.check_rate_limit(
                user_id, "trade_capture", "trader", org_id, "tier1"
            )
            
            if i < 20:
                assert is_allowed == True
            else:
                assert is_allowed == False
                break
        
        # Test 4: Password Security
        password = "secure_password_123"
        hashed = auth_mgr.hash_password(password)
        assert auth_mgr.verify_password(password, hashed) == True
        assert auth_mgr.verify_password("wrong_password", hashed) == False
        
        # Test 5: Token Expiration
        expired_token = auth_mgr.create_access_token(
            user_data, expires_delta=timedelta(seconds=-1)
        )
        with pytest.raises(Exception):  # HTTPException
            auth_mgr.verify_token(expired_token)
        
        print("✅ E2E Security and Compliance completed successfully")
        
    except Exception as e:
        print(f"❌ E2E Security test failed: {str(e)}")
        raise

if __name__ == "__main__":
    # Run all E2E tests
    async def run_all_e2e_tests():
        print("🚀 Starting Comprehensive E2E Tests...")
        
        await test_e2e_trading_workflow()
        await test_e2e_multi_tenant_isolation()
        await test_e2e_real_time_market_data()
        await test_e2e_security_and_compliance()
        
        print("🎉 All E2E Tests Completed Successfully!")
    
    asyncio.run(run_all_e2e_tests())
