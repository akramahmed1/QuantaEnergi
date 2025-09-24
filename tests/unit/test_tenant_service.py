"""
Unit tests for Tenant Service
Tests tenant lifecycle management functionality
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
from sqlalchemy.exc import SQLAlchemyError

from app.services.tenant_service import TenantService, TenantInfo, get_tenant_service


class TestTenantInfo:
    """Test cases for TenantInfo dataclass"""
    
    def test_tenant_info_creation(self):
        """Test TenantInfo object creation"""
        tenant_info = TenantInfo(
            tenant_id="test-tenant",
            name="Test Tenant",
            region="us",
            subscription_tier="basic",
            max_users=10,
            max_trades_per_day=1000,
            features=["trading", "analytics"],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_active=True
        )
        
        assert tenant_info.tenant_id == "test-tenant"
        assert tenant_info.name == "Test Tenant"
        assert tenant_info.region == "us"
        assert tenant_info.subscription_tier == "basic"
        assert tenant_info.max_users == 10
        assert tenant_info.max_trades_per_day == 1000
        assert tenant_info.features == ["trading", "analytics"]
        assert tenant_info.is_active is True


class TestTenantService:
    """Test cases for TenantService class"""
    
    @pytest.fixture
    def tenant_service(self):
        """Create a TenantService instance for testing"""
        with patch('app.services.tenant_service.get_tenant_router') as mock_get_router:
            mock_router = Mock()
            mock_get_router.return_value = mock_router
            service = TenantService()
            return service
    
    @pytest.mark.asyncio
    async def test_create_tenant_success(self, tenant_service):
        """Test successful tenant creation"""
        tenant_data = {
            "tenant_id": "test-tenant",
            "name": "Test Tenant",
            "region": "us",
            "subscription_tier": "basic",
            "max_users": 10,
            "max_trades_per_day": 1000,
            "features": ["trading", "analytics"]
        }
        
        # Mock router methods
        tenant_service.router.create_tenant_schema = Mock(return_value=True)
        tenant_service.router.default_engine = Mock()
        
        with patch.object(tenant_service.router.default_engine, 'connect') as mock_connect:
            mock_conn = Mock()
            mock_connect.return_value.__enter__.return_value = mock_conn
            
            # Mock tenant exists check
            mock_result = Mock()
            mock_result.fetchone.return_value = None  # Tenant doesn't exist
            mock_conn.execute.return_value = mock_result
            
            result = await tenant_service.create_tenant(tenant_data)
            
            assert result is True
            assert "test-tenant" in tenant_service.tenant_cache
            tenant_service.router.create_tenant_schema.assert_called_once_with("test-tenant")
            mock_conn.execute.assert_called()
            mock_conn.commit.assert_called()
    
    @pytest.mark.asyncio
    async def test_create_tenant_already_exists(self, tenant_service):
        """Test tenant creation when tenant already exists"""
        tenant_data = {
            "tenant_id": "existing-tenant",
            "name": "Existing Tenant"
        }
        
        tenant_service.router.create_tenant_schema = Mock(return_value=True)
        tenant_service.router.default_engine = Mock()
        
        with patch.object(tenant_service.router.default_engine, 'connect') as mock_connect:
            mock_conn = Mock()
            mock_connect.return_value.__enter__.return_value = mock_conn
            
            # Mock tenant exists check
            mock_result = Mock()
            mock_result.fetchone.return_value = ["existing-tenant"]  # Tenant exists
            mock_conn.execute.return_value = mock_result
            
            result = await tenant_service.create_tenant(tenant_data)
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_create_tenant_schema_failure(self, tenant_service):
        """Test tenant creation when schema creation fails"""
        tenant_data = {
            "tenant_id": "failing-tenant",
            "name": "Failing Tenant"
        }
        
        tenant_service.router.create_tenant_schema = Mock(return_value=False)
        
        result = await tenant_service.create_tenant(tenant_data)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_create_tenant_database_error(self, tenant_service):
        """Test tenant creation with database error"""
        tenant_data = {
            "tenant_id": "error-tenant",
            "name": "Error Tenant"
        }
        
        tenant_service.router.create_tenant_schema = Mock(return_value=True)
        tenant_service.router.default_engine = Mock()
        
        with patch.object(tenant_service.router.default_engine, 'connect') as mock_connect:
            mock_connect.side_effect = SQLAlchemyError("Database error")
            
            result = await tenant_service.create_tenant(tenant_data)
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_get_tenant_info_from_cache(self, tenant_service):
        """Test getting tenant info from cache"""
        tenant_id = "cached-tenant"
        tenant_info = TenantInfo(
            tenant_id=tenant_id,
            name="Cached Tenant",
            region="us",
            subscription_tier="basic",
            max_users=10,
            max_trades_per_day=1000,
            features=[],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_active=True
        )
        
        tenant_service.tenant_cache[tenant_id] = tenant_info
        
        result = await tenant_service.get_tenant_info(tenant_id)
        
        assert result == tenant_info
    
    @pytest.mark.asyncio
    async def test_get_tenant_info_from_database(self, tenant_service):
        """Test getting tenant info from database"""
        tenant_id = "db-tenant"
        tenant_service.router.default_engine = Mock()
        
        with patch.object(tenant_service.router.default_engine, 'connect') as mock_connect:
            mock_conn = Mock()
            mock_connect.return_value.__enter__.return_value = mock_conn
            
            # Mock database query result
            mock_result = Mock()
            mock_result.fetchone.return_value = (
                tenant_id, "DB Tenant", "us", "basic", 10, 1000, 
                ["trading"], datetime.now(timezone.utc), 
                datetime.now(timezone.utc), True
            )
            mock_conn.execute.return_value = mock_result
            
            result = await tenant_service.get_tenant_info(tenant_id)
            
            assert result is not None
            assert result.tenant_id == tenant_id
            assert result.name == "DB Tenant"
            assert tenant_id in tenant_service.tenant_cache
    
    @pytest.mark.asyncio
    async def test_get_tenant_info_not_found(self, tenant_service):
        """Test getting tenant info when tenant doesn't exist"""
        tenant_id = "nonexistent-tenant"
        tenant_service.router.default_engine = Mock()
        
        with patch.object(tenant_service.router.default_engine, 'connect') as mock_connect:
            mock_conn = Mock()
            mock_connect.return_value.__enter__.return_value = mock_conn
            
            # Mock database query result
            mock_result = Mock()
            mock_result.fetchone.return_value = None  # Tenant not found
            mock_conn.execute.return_value = mock_result
            
            result = await tenant_service.get_tenant_info(tenant_id)
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_update_tenant_success(self, tenant_service):
        """Test successful tenant update"""
        tenant_id = "update-tenant"
        update_data = {
            "name": "Updated Tenant",
            "max_users": 20,
            "is_active": False
        }
        
        # Add tenant to cache
        tenant_info = TenantInfo(
            tenant_id=tenant_id,
            name="Original Tenant",
            region="us",
            subscription_tier="basic",
            max_users=10,
            max_trades_per_day=1000,
            features=[],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_active=True
        )
        tenant_service.tenant_cache[tenant_id] = tenant_info
        
        tenant_service.router.default_engine = Mock()
        
        with patch.object(tenant_service.router.default_engine, 'connect') as mock_connect:
            mock_conn = Mock()
            mock_connect.return_value.__enter__.return_value = mock_conn
            
            result = await tenant_service.update_tenant(tenant_id, update_data)
            
            assert result is True
            mock_conn.execute.assert_called()
            mock_conn.commit.assert_called()
            
            # Check cache was updated
            cached_tenant = tenant_service.tenant_cache[tenant_id]
            assert cached_tenant.name == "Updated Tenant"
            assert cached_tenant.max_users == 20
            assert cached_tenant.is_active is False
    
    @pytest.mark.asyncio
    async def test_update_tenant_no_valid_fields(self, tenant_service):
        """Test tenant update with no valid fields"""
        tenant_id = "update-tenant"
        update_data = {
            "invalid_field": "value"
        }
        
        result = await tenant_service.update_tenant(tenant_id, update_data)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_delete_tenant_success(self, tenant_service):
        """Test successful tenant deletion"""
        tenant_id = "delete-tenant"
        
        # Add tenant to cache
        tenant_info = TenantInfo(
            tenant_id=tenant_id,
            name="Delete Tenant",
            region="us",
            subscription_tier="basic",
            max_users=10,
            max_trades_per_day=1000,
            features=[],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_active=True
        )
        tenant_service.tenant_cache[tenant_id] = tenant_info
        
        tenant_service.router.delete_tenant_schema = Mock(return_value=True)
        tenant_service.router.default_engine = Mock()
        
        with patch.object(tenant_service.router.default_engine, 'connect') as mock_connect:
            mock_conn = Mock()
            mock_connect.return_value.__enter__.return_value = mock_conn
            
            result = await tenant_service.delete_tenant(tenant_id)
            
            assert result is True
            tenant_service.router.delete_tenant_schema.assert_called_once_with(tenant_id)
            mock_conn.execute.assert_called()
            mock_conn.commit.assert_called()
            assert tenant_id not in tenant_service.tenant_cache
    
    @pytest.mark.asyncio
    async def test_delete_tenant_schema_failure(self, tenant_service):
        """Test tenant deletion when schema deletion fails"""
        tenant_id = "delete-tenant"
        
        tenant_service.router.delete_tenant_schema = Mock(return_value=False)
        
        result = await tenant_service.delete_tenant(tenant_id)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_list_tenants_active_only(self, tenant_service):
        """Test listing active tenants only"""
        tenant_service.router.default_engine = Mock()
        
        with patch.object(tenant_service.router.default_engine, 'connect') as mock_connect:
            mock_conn = Mock()
            mock_connect.return_value.__enter__.return_value = mock_conn
            
            # Mock database query result
            mock_result = Mock()
            mock_result.fetchall.return_value = [
                ("tenant1", "Tenant 1", "us", "basic", 10, 1000, [], 
                 datetime.now(timezone.utc), datetime.now(timezone.utc), True),
                ("tenant2", "Tenant 2", "eu", "premium", 50, 5000, ["trading", "analytics"], 
                 datetime.now(timezone.utc), datetime.now(timezone.utc), True)
            ]
            mock_conn.execute.return_value = mock_result
            
            tenants = await tenant_service.list_tenants(active_only=True)
            
            assert len(tenants) == 2
            assert all(tenant.is_active for tenant in tenants)
    
    @pytest.mark.asyncio
    async def test_list_tenants_all(self, tenant_service):
        """Test listing all tenants"""
        tenant_service.router.default_engine = Mock()
        
        with patch.object(tenant_service.router.default_engine, 'connect') as mock_connect:
            mock_conn = Mock()
            mock_connect.return_value.__enter__.return_value = mock_conn
            
            # Mock database query result
            mock_result = Mock()
            mock_result.fetchall.return_value = [
                ("tenant1", "Tenant 1", "us", "basic", 10, 1000, [], 
                 datetime.now(timezone.utc), datetime.now(timezone.utc), True),
                ("tenant2", "Tenant 2", "eu", "premium", 50, 5000, [], 
                 datetime.now(timezone.utc), datetime.now(timezone.utc), False)
            ]
            mock_conn.execute.return_value = mock_result
            
            tenants = await tenant_service.list_tenants(active_only=False)
            
            assert len(tenants) == 2
            assert tenants[0].is_active is True
            assert tenants[1].is_active is False
    
    @pytest.mark.asyncio
    async def test_get_tenant_stats_success(self, tenant_service):
        """Test getting tenant statistics"""
        tenant_id = "stats-tenant"
        
        # Mock tenant info
        tenant_info = TenantInfo(
            tenant_id=tenant_id,
            name="Stats Tenant",
            region="us",
            subscription_tier="basic",
            max_users=10,
            max_trades_per_day=1000,
            features=[],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_active=True
        )
        
        with patch.object(tenant_service, 'get_tenant_info', return_value=tenant_info):
            with patch.object(tenant_service.router, 'get_tenant_stats', return_value={"db_stats": "data"}):
                with patch.object(tenant_service.router, 'get_tenant_session') as mock_get_session:
                    mock_session = Mock()
                    mock_get_session.return_value = mock_session
                    
                    # Mock database queries
                    mock_session.execute.side_effect = [
                        Mock(scalar=Mock(return_value=100)),  # trade_count
                        Mock(scalar=Mock(return_value=5)),    # portfolio_count
                        Mock(scalar=Mock(return_value=25)),   # position_count
                        Mock(scalar=Mock(return_value=100000.0))  # total_trade_value
                    ]
                    
                    stats = await tenant_service.get_tenant_stats(tenant_id)
                    
                    assert stats["tenant_id"] == tenant_id
                    assert stats["trade_count"] == 100
                    assert stats["portfolio_count"] == 5
                    assert stats["position_count"] == 25
                    assert stats["total_trade_value"] == 100000.0
                    assert "database_stats" in stats
                    
                    mock_session.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_tenant_stats_not_found(self, tenant_service):
        """Test getting tenant stats when tenant doesn't exist"""
        tenant_id = "nonexistent-tenant"
        
        with patch.object(tenant_service, 'get_tenant_info', return_value=None):
            stats = await tenant_service.get_tenant_stats(tenant_id)
            
            assert stats == {}
    
    @pytest.mark.asyncio
    async def test_validate_tenant_limits_trade_success(self, tenant_service):
        """Test validating tenant limits for trade operation"""
        tenant_id = "limit-tenant"
        
        tenant_info = TenantInfo(
            tenant_id=tenant_id,
            name="Limit Tenant",
            region="us",
            subscription_tier="basic",
            max_users=10,
            max_trades_per_day=1000,
            features=[],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_active=True
        )
        
        with patch.object(tenant_service, 'get_tenant_info', return_value=tenant_info):
            with patch.object(tenant_service.router, 'get_tenant_session') as mock_get_session:
                mock_session = Mock()
                mock_get_session.return_value = mock_session
                
                # Mock daily trades query
                mock_result = Mock()
                mock_result.scalar.return_value = 500  # Under limit
                mock_session.execute.return_value = mock_result
                
                result = await tenant_service.validate_tenant_limits(tenant_id, "trade")
                
                assert result is True
                mock_session.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_validate_tenant_limits_trade_exceeded(self, tenant_service):
        """Test validating tenant limits when trade limit is exceeded"""
        tenant_id = "limit-tenant"
        
        tenant_info = TenantInfo(
            tenant_id=tenant_id,
            name="Limit Tenant",
            region="us",
            subscription_tier="basic",
            max_users=10,
            max_trades_per_day=1000,
            features=[],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_active=True
        )
        
        with patch.object(tenant_service, 'get_tenant_info', return_value=tenant_info):
            with patch.object(tenant_service.router, 'get_tenant_session') as mock_get_session:
                mock_session = Mock()
                mock_get_session.return_value = mock_session
                
                # Mock daily trades query
                mock_result = Mock()
                mock_result.scalar.return_value = 1000  # At limit
                mock_session.execute.return_value = mock_result
                
                result = await tenant_service.validate_tenant_limits(tenant_id, "trade")
                
                assert result is False
                mock_session.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_validate_tenant_limits_inactive_tenant(self, tenant_service):
        """Test validating tenant limits for inactive tenant"""
        tenant_id = "inactive-tenant"
        
        with patch.object(tenant_service, 'get_tenant_info', return_value=None):
            result = await tenant_service.validate_tenant_limits(tenant_id, "trade")
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_get_tenant_features_success(self, tenant_service):
        """Test getting tenant features"""
        tenant_id = "feature-tenant"
        
        tenant_info = TenantInfo(
            tenant_id=tenant_id,
            name="Feature Tenant",
            region="us",
            subscription_tier="premium",
            max_users=50,
            max_trades_per_day=5000,
            features=["trading", "analytics", "compliance"],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_active=True
        )
        
        with patch.object(tenant_service, 'get_tenant_info', return_value=tenant_info):
            features = await tenant_service.get_tenant_features(tenant_id)
            
            assert features == ["trading", "analytics", "compliance"]
    
    @pytest.mark.asyncio
    async def test_get_tenant_features_not_found(self, tenant_service):
        """Test getting tenant features when tenant doesn't exist"""
        tenant_id = "nonexistent-tenant"
        
        with patch.object(tenant_service, 'get_tenant_info', return_value=None):
            features = await tenant_service.get_tenant_features(tenant_id)
            
            assert features == []
    
    @pytest.mark.asyncio
    async def test_is_feature_enabled_success(self, tenant_service):
        """Test checking if feature is enabled"""
        tenant_id = "feature-tenant"
        
        with patch.object(tenant_service, 'get_tenant_features', return_value=["trading", "analytics"]):
            result = await tenant_service.is_feature_enabled(tenant_id, "trading")
            
            assert result is True
            
            result = await tenant_service.is_feature_enabled(tenant_id, "compliance")
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_is_feature_enabled_error(self, tenant_service):
        """Test checking feature when error occurs"""
        tenant_id = "error-tenant"
        
        with patch.object(tenant_service, 'get_tenant_features', side_effect=Exception("Database error")):
            result = await tenant_service.is_feature_enabled(tenant_id, "trading")
            
            assert result is False


class TestTenantServiceGlobal:
    """Test cases for global tenant service functions"""
    
    def test_get_tenant_service(self):
        """Test getting tenant service instance"""
        with patch('app.services.tenant_service.get_tenant_router'):
            service = get_tenant_service()
            assert service is not None
            assert isinstance(service, TenantService)


if __name__ == "__main__":
    pytest.main([__file__])
