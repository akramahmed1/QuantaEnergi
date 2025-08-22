"""
Unit tests for enhanced services (PR2).

Tests enhanced AI/ML, caching, WebSocket, and security services.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone, timedelta
import json

from src.energyopti_pro.services.enhanced_ai_ml_service import (
    EnhancedAIMLService,
    EnhancedForecastResult,
    RLTrainingResult,
    QuantumOptimizationResult,
    ESGModelResult
)
from src.energyopti_pro.services.cache_service import CacheService
from src.energyopti_pro.services.websocket_service import (
    WebSocketService,
    WebSocketMessage,
    MessageType
)
from src.energyopti_pro.services.enhanced_security_service import (
    EnhancedSecurityService,
    Permission,
    Role,
    User
)

@pytest.fixture
def enhanced_ai_ml_service():
    """Create enhanced AI/ML service instance."""
    return EnhancedAIMLService()

@pytest.fixture
def cache_service():
    """Create cache service instance."""
    return CacheService("redis://localhost:6379/0")

@pytest.fixture
def websocket_service():
    """Create WebSocket service instance."""
    return WebSocketService()

@pytest.fixture
def security_service():
    """Create security service instance."""
    return EnhancedSecurityService("test-secret-key")

class TestEnhancedAIMLService:
    """Test enhanced AI/ML service."""
    
    @pytest.mark.asyncio
    async def test_initialization(self, enhanced_ai_ml_service):
        """Test service initialization."""
        assert enhanced_ai_ml_service.forecast_models is not None
        assert enhanced_ai_ml_service.rl_agents is not None
        assert enhanced_ai_ml_service.quantum_circuits is not None
        assert enhanced_ai_ml_service.esg_models is not None
    
    @pytest.mark.asyncio
    async def test_forecast_energy_prices(self, enhanced_ai_ml_service):
        """Test energy price forecasting."""
        forecast = await enhanced_ai_ml_service.forecast_energy_prices("crude_oil", 7)
        
        assert len(forecast) == 7
        assert all(isinstance(f, EnhancedForecastResult) for f in forecast)
        assert all(f.commodity == "crude_oil" for f in forecast)
    
    @pytest.mark.asyncio
    async def test_rl_agent_training(self, enhanced_ai_ml_service):
        """Test RL agent training."""
        training_data = {"episodes": 1000, "environment": "trading"}
        hyperparameters = {"learning_rate": 0.001, "total_timesteps": 10000}
        
        result = await enhanced_ai_ml_service.train_rl_agent(
            "portfolio_optimization", training_data, hyperparameters
        )
        
        assert isinstance(result, RLTrainingResult)
        assert result.agent_type == "portfolio_optimization"
        assert result.training_episodes > 0
    
    @pytest.mark.asyncio
    async def test_quantum_optimization(self, enhanced_ai_ml_service):
        """Test quantum optimization."""
        parameters = {"shots": 1000}
        
        result = await enhanced_ai_ml_service.run_quantum_optimization(
            "portfolio_optimization", parameters
        )
        
        assert isinstance(result, QuantumOptimizationResult)
        assert result.optimization_type == "portfolio_optimization"
        assert result.shots == 1000
    
    @pytest.mark.asyncio
    async def test_esg_analysis(self, enhanced_ai_ml_service):
        """Test ESG analysis."""
        company_data = {
            "company_name": "Test Corp",
            "carbon_emissions": 0.5,
            "energy_efficiency": 0.8,
            "renewable_energy_usage": 0.3
        }
        
        result = await enhanced_ai_ml_service.analyze_esg(company_data)
        
        assert isinstance(result, ESGModelResult)
        assert 0 <= result.esg_score <= 1
        assert 0 <= result.environmental_score <= 1
        assert 0 <= result.social_score <= 1
        assert 0 <= result.governance_score <= 1
    
    @pytest.mark.asyncio
    async def test_comprehensive_ai_insights(self, enhanced_ai_ml_service):
        """Test comprehensive AI insights."""
        market_data = {"crude_oil": {"price": 75.50}}
        user_profile = {"enable_portfolio_optimization": True, "positions": []}
        
        insights = await enhanced_ai_ml_service.get_comprehensive_ai_insights(
            market_data, user_profile
        )
        
        assert "market_analysis" in insights
        assert "trading_recommendations" in insights
        assert "risk_assessment" in insights
        assert "ai_model_status" in insights

class TestCacheService:
    """Test cache service."""
    
    @pytest.mark.asyncio
    async def test_initialization(self, cache_service):
        """Test cache service initialization."""
        assert cache_service.redis_url == "redis://localhost:6379/0"
        assert cache_service.default_ttl == 300
        assert cache_service.max_ttl == 86400
    
    def test_generate_key(self, cache_service):
        """Test cache key generation."""
        key = cache_service._generate_key("test", "arg1", kwarg1="value1")
        assert key.startswith("test:")
        assert "arg1" in key
        assert "kwarg1:value1" in key
    
    @pytest.mark.asyncio
    async def test_set_and_get(self, cache_service):
        """Test cache set and get operations."""
        # Mock Redis client
        cache_service.client = Mock()
        cache_service.client.set = AsyncMock(return_value=True)
        cache_service.client.get = AsyncMock(return_value=json.dumps({"test": "data"}))
        
        # Test set
        success = await cache_service.set("test_key", {"test": "data"}, ttl=60)
        assert success is True
        
        # Test get
        value = await cache_service.get("test_key")
        assert value == {"test": "data"}
    
    @pytest.mark.asyncio
    async def test_delete(self, cache_service):
        """Test cache delete operation."""
        cache_service.client = Mock()
        cache_service.client.delete = AsyncMock(return_value=1)
        
        success = await cache_service.delete("test_key")
        assert success is True
    
    @pytest.mark.asyncio
    async def test_get_or_set(self, cache_service):
        """Test get or set functionality."""
        cache_service.client = Mock()
        cache_service.client.get = AsyncMock(return_value=None)
        cache_service.client.set = AsyncMock(return_value=True)
        
        def default_func():
            return "default_value"
        
        value = await cache_service.get_or_set("test_key", default_func, ttl=60)
        assert value == "default_value"
    
    @pytest.mark.asyncio
    async def test_health_check(self, cache_service):
        """Test cache health check."""
        cache_service.client = Mock()
        cache_service.client.set = AsyncMock(return_value=True)
        cache_service.client.get = AsyncMock(return_value=json.dumps({"test": True}))
        cache_service.client.delete = AsyncMock(return_value=1)
        
        health = await cache_service.health_check()
        assert health["status"] == "healthy"

class TestWebSocketService:
    """Test WebSocket service."""
    
    def test_initialization(self, websocket_service):
        """Test WebSocket service initialization."""
        assert websocket_service.connection_manager is not None
        assert websocket_service.message_handlers is not None
    
    @pytest.mark.asyncio
    async def test_start_and_stop(self, websocket_service):
        """Test service start and stop."""
        await websocket_service.start()
        assert websocket_service.heartbeat_task is not None
        
        await websocket_service.stop()
        assert websocket_service.heartbeat_task is None
    
    def test_message_creation(self):
        """Test WebSocket message creation."""
        message = WebSocketMessage(
            type=MessageType.MARKET_DATA,
            data={"price": 75.50},
            timestamp=datetime.now(timezone.utc),
            user_id="user123"
        )
        
        message_dict = message.to_dict()
        assert message_dict["type"] == "market_data"
        assert message_dict["data"]["price"] == 75.50
        assert "user_id" in message_dict
    
    @pytest.mark.asyncio
    async def test_broadcast_market_data(self, websocket_service):
        """Test market data broadcasting."""
        market_data = {"crude_oil": {"price": 75.50}}
        
        # Mock connection manager
        websocket_service.connection_manager.broadcast = AsyncMock()
        
        await websocket_service.broadcast_market_data(market_data)
        
        websocket_service.connection_manager.broadcast.assert_called_once()
        call_args = websocket_service.connection_manager.broadcast.call_args
        assert call_args[0][0].type == MessageType.MARKET_DATA
        assert call_args[0][0].data == market_data
    
    @pytest.mark.asyncio
    async def test_broadcast_order_update(self, websocket_service):
        """Test order update broadcasting."""
        order_data = {"order_id": "123", "status": "filled"}
        user_id = "user123"
        
        # Mock connection manager
        websocket_service.connection_manager.send_to_user = AsyncMock()
        
        await websocket_service.broadcast_order_update(order_data, user_id)
        
        websocket_service.connection_manager.send_to_user.assert_called_once()
        call_args = websocket_service.connection_manager.send_to_user.call_args
        assert call_args[0][0] == user_id
        assert call_args[0][1].type == MessageType.ORDER_UPDATE
        assert call_args[0][1].data == order_data

class TestEnhancedSecurityService:
    """Test enhanced security service."""
    
    def test_initialization(self, security_service):
        """Test security service initialization."""
        assert security_service.secret_key == "test-secret-key"
        assert security_service.algorithm == "HS256"
        assert security_service.post_quantum_crypto is not None
        assert len(security_service.users) > 0
    
    def test_user_creation(self, security_service):
        """Test user creation."""
        user = security_service.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
            role=Role.TRADER
        )
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == Role.TRADER
        assert user.is_active is True
        assert user.id in security_service.users
    
    def test_user_authentication(self, security_service):
        """Test user authentication."""
        # Create user first
        user = security_service.create_user(
            username="authuser",
            email="auth@example.com",
            password="password123",
            role=Role.ANALYST
        )
        
        # Test authentication
        token = security_service.authenticate_user("authuser", "password123", "127.0.0.1")
        assert token is not None
        
        # Verify token
        user_info = security_service.verify_token(token)
        assert user_info is not None
        assert user_info["username"] == "authuser"
        assert user_info["role"] == Role.ANALYST.value
    
    def test_permission_checking(self, security_service):
        """Test permission checking."""
        # Create user with specific permissions
        user = security_service.create_user(
            username="permuser",
            email="perm@example.com",
            password="password123",
            role=Role.TRADER
        )
        
        # Authenticate user
        token = security_service.authenticate_user("permuser", "password123", "127.0.0.1")
        
        # Check permissions
        assert security_service.check_permission(token, Permission.READ_MARKET_DATA) is True
        assert security_service.check_permission(token, Permission.WRITE_TRADING_DATA) is True
        assert security_service.check_permission(token, Permission.ADMIN) is False
    
    def test_rate_limiting(self, security_service):
        """Test rate limiting."""
        identifier = "test_ip_127.0.0.1"
        
        # Check rate limit
        for i in range(100):
            allowed = security_service.check_rate_limit(identifier, "api")
            if i < 99:
                assert allowed is True
            else:
                assert allowed is False
        
        # Check remaining
        remaining = security_service.rate_limiters["api"].get_remaining(identifier)
        assert remaining == 0
    
    def test_post_quantum_encryption(self, security_service):
        """Test post-quantum encryption."""
        plaintext = "sensitive_data"
        
        # Encrypt
        encrypted = security_service.encrypt_sensitive_data(plaintext)
        assert "ciphertext" in encrypted
        assert "encrypted_data" in encrypted
        assert "algorithm" in encrypted
        
        # Decrypt
        decrypted = security_service.decrypt_sensitive_data(
            encrypted["ciphertext"],
            encrypted["encrypted_data"]
        )
        assert decrypted == plaintext
    
    def test_audit_logging(self, security_service):
        """Test audit logging."""
        initial_count = len(security_service.audit_logs)
        
        # Log an event
        security_service._log_audit_event(
            user_id="testuser",
            action="test_action",
            resource="test_resource",
            details={"test": "data"},
            ip_address="127.0.0.1",
            user_agent="test_agent",
            success=True
        )
        
        assert len(security_service.audit_logs) == initial_count + 1
        
        # Check log entry
        latest_log = security_service.audit_logs[-1]
        assert latest_log.user_id == "testuser"
        assert latest_log.action == "test_action"
        assert latest_log.success is True
    
    def test_security_events(self, security_service):
        """Test security event logging."""
        initial_count = len(security_service.security_events)
        
        # Log security event
        security_service._log_security_event(
            event_type="test_event",
            severity="medium",
            description="Test security event",
            user_id="testuser",
            ip_address="127.0.0.1"
        )
        
        assert len(security_service.security_events) == initial_count + 1
        
        # Check event
        latest_event = security_service.security_events[-1]
        assert latest_event.event_type == "test_event"
        assert latest_event.severity == "medium"
        assert latest_event.user_id == "testuser"
    
    def test_get_audit_logs(self, security_service):
        """Test audit log retrieval."""
        # Create some test logs
        for i in range(5):
            security_service._log_audit_event(
                user_id=f"user{i}",
                action="test_action",
                resource="test_resource",
                details={"index": i},
                ip_address="127.0.0.1",
                user_agent="test_agent",
                success=True
            )
        
        # Test filtering
        user_logs = security_service.get_audit_logs(user_id="user0")
        assert len(user_logs) == 1
        assert user_logs[0].user_id == "user0"
        
        # Test limiting
        limited_logs = security_service.get_audit_logs(limit=3)
        assert len(limited_logs) == 3
    
    def test_get_security_status(self, security_service):
        """Test security status retrieval."""
        status = security_service.get_security_status()
        
        assert status["status"] == "active"
        assert "total_users" in status
        assert "active_tokens" in status
        assert "total_audit_logs" in status
        assert "total_security_events" in status

@pytest.mark.asyncio
async def test_service_integration():
    """Test integration between enhanced services."""
    # Create services
    ai_ml_service = EnhancedAIMLService()
    cache_service = CacheService("redis://localhost:6379/0")
    security_service = EnhancedSecurityService("test-secret")
    
    # Test AI/ML with caching
    cache_key = "forecast:crude_oil:7"
    await cache_service.set(cache_key, {"cached": True}, ttl=300)
    
    cached_value = await cache_service.get(cache_key)
    assert cached_value["cached"] is True
    
    # Test security with AI/ML
    user = security_service.create_user(
        username="integration_user",
        email="integration@example.com",
        password="password123",
        role=Role.ANALYST
    )
    
    token = security_service.authenticate_user("integration_user", "password123", "127.0.0.1")
    assert token is not None
    
    # Test permission for AI/ML access
    assert security_service.check_permission(token, Permission.READ_AI_ML_DATA) is True
    
    # Test AI/ML insights
    market_data = {"crude_oil": {"price": 75.50}}
    user_profile = {"enable_portfolio_optimization": True, "positions": []}
    
    insights = await ai_ml_service.get_comprehensive_ai_insights(market_data, user_profile)
    assert "market_analysis" in insights
    assert "ai_model_status" in insights

if __name__ == "__main__":
    pytest.main([__file__])
