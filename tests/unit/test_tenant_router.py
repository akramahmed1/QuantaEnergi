"""
Unit tests for Tenant Router
Tests schema-per-tenant routing functionality
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.tenant_router import TenantRouter, get_tenant_router, tenant_required
from app.core.config import settings


class TestTenantRouter:
    """Test cases for TenantRouter class"""
    
    @pytest.fixture
    def tenant_router(self):
        """Create a TenantRouter instance for testing"""
        with patch('app.core.tenant_router.create_engine') as mock_engine:
            mock_engine.return_value = Mock()
            router = TenantRouter()
            return router
    
    def test_init(self, tenant_router):
        """Test TenantRouter initialization"""
        assert tenant_router.engines == {}
        assert tenant_router.sessions == {}
        assert tenant_router.tenant_schemas == {}
        assert tenant_router.connection_pools == {}
    
    def test_get_tenant_schema_name(self, tenant_router):
        """Test schema name generation"""
        # Test normal tenant ID
        schema_name = tenant_router._get_tenant_schema_name("tenant-123")
        assert schema_name == "tenant_tenant_123"
        assert tenant_router.tenant_schemas["tenant-123"] == "tenant_tenant_123"
        
        # Test tenant ID with dots
        schema_name = tenant_router._get_tenant_schema_name("tenant.123")
        assert schema_name == "tenant_tenant_123"
        
        # Test tenant ID with mixed case
        schema_name = tenant_router._get_tenant_schema_name("Tenant-123")
        assert schema_name == "tenant_tenant_123"
    
    @pytest.mark.asyncio
    async def test_create_tenant_schema_success(self, tenant_router):
        """Test successful tenant schema creation"""
        tenant_id = "test-tenant"
        
        with patch.object(tenant_router, '_create_tenant_tables') as mock_create_tables:
            with patch.object(tenant_router.default_engine, 'connect') as mock_connect:
                mock_conn = Mock()
                mock_connect.return_value.__enter__.return_value = mock_conn
                
                # Mock schema exists check
                mock_result = Mock()
                mock_result.fetchone.return_value = None  # Schema doesn't exist
                mock_conn.execute.return_value = mock_result
                
                result = await tenant_router.create_tenant_schema(tenant_id)
                
                assert result is True
                assert tenant_id in tenant_router.tenant_schemas
                mock_conn.execute.assert_called()
                mock_conn.commit.assert_called()
                mock_create_tables.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_tenant_schema_already_exists(self, tenant_router):
        """Test tenant schema creation when schema already exists"""
        tenant_id = "existing-tenant"
        
        with patch.object(tenant_router, '_create_tenant_tables') as mock_create_tables:
            with patch.object(tenant_router.default_engine, 'connect') as mock_connect:
                mock_conn = Mock()
                mock_connect.return_value.__enter__.return_value = mock_conn
                
                # Mock schema exists check
                mock_result = Mock()
                mock_result.fetchone.return_value = ["tenant_existing_tenant"]  # Schema exists
                mock_conn.execute.return_value = mock_result
                
                result = await tenant_router.create_tenant_schema(tenant_id)
                
                assert result is True
                mock_create_tables.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_create_tenant_schema_failure(self, tenant_router):
        """Test tenant schema creation failure"""
        tenant_id = "failing-tenant"
        
        with patch.object(tenant_router.default_engine, 'connect') as mock_connect:
            mock_connect.side_effect = SQLAlchemyError("Database connection failed")
            
            result = await tenant_router.create_tenant_schema(tenant_id)
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_create_tenant_tables(self, tenant_router):
        """Test tenant table creation"""
        tenant_id = "test-tenant"
        schema_name = "tenant_test_tenant"
        
        with patch.object(tenant_router.default_engine, 'connect') as mock_connect:
            mock_conn = Mock()
            mock_connect.return_value.__enter__.return_value = mock_conn
            
            await tenant_router._create_tenant_tables(tenant_id, schema_name)
            
            # Verify table creation calls
            assert mock_conn.execute.call_count >= 4  # At least 4 tables created
            mock_conn.commit.assert_called()
    
    def test_get_tenant_engine(self, tenant_router):
        """Test getting tenant-specific engine"""
        tenant_id = "test-tenant"
        
        with patch('app.core.tenant_router.create_engine') as mock_create_engine:
            with patch('app.core.tenant_router.sessionmaker') as mock_sessionmaker:
                mock_engine = Mock()
                mock_create_engine.return_value = mock_engine
                mock_session_factory = Mock()
                mock_sessionmaker.return_value = mock_session_factory
                
                engine = tenant_router.get_tenant_engine(tenant_id)
                
                assert engine == mock_engine
                assert tenant_id in tenant_router.engines
                assert tenant_id in tenant_router.sessions
                mock_create_engine.assert_called_once()
                mock_sessionmaker.assert_called_once()
    
    def test_get_tenant_session(self, tenant_router):
        """Test getting tenant-specific session"""
        tenant_id = "test-tenant"
        
        with patch.object(tenant_router, 'get_tenant_engine') as mock_get_engine:
            mock_session_factory = Mock()
            mock_session = Mock()
            mock_session_factory.return_value = mock_session
            tenant_router.sessions[tenant_id] = mock_session_factory
            
            session = tenant_router.get_tenant_session(tenant_id)
            
            assert session == mock_session
            mock_session_factory.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_tenant_session_async(self, tenant_router):
        """Test getting async tenant session"""
        tenant_id = "test-tenant"
        
        with patch('app.core.tenant_router.create_async_engine') as mock_create_async_engine:
            with patch('app.core.tenant_router.sessionmaker') as mock_sessionmaker:
                mock_async_engine = Mock()
                mock_create_async_engine.return_value = mock_async_engine
                mock_async_session_factory = Mock()
                mock_sessionmaker.return_value = mock_async_session_factory
                
                mock_session = Mock()
                mock_async_session_factory.return_value.__aenter__.return_value = mock_session
                
                async with tenant_router.get_tenant_session_async(tenant_id) as session:
                    assert session == mock_session
                
                mock_create_async_engine.assert_called_once()
                mock_async_engine.dispose.assert_called_once()
    
    def test_delete_tenant_schema(self, tenant_router):
        """Test tenant schema deletion"""
        tenant_id = "test-tenant"
        tenant_router.tenant_schemas[tenant_id] = "tenant_test_tenant"
        tenant_router.engines[tenant_id] = Mock()
        tenant_router.sessions[tenant_id] = Mock()
        
        with patch.object(tenant_router.default_engine, 'connect') as mock_connect:
            mock_conn = Mock()
            mock_connect.return_value.__enter__.return_value = mock_conn
            
            result = tenant_router.delete_tenant_schema(tenant_id)
            
            assert result is True
            mock_conn.execute.assert_called()
            mock_conn.commit.assert_called()
            assert tenant_id not in tenant_router.engines
            assert tenant_id not in tenant_router.sessions
            assert tenant_id not in tenant_router.tenant_schemas
    
    def test_list_tenant_schemas(self, tenant_router):
        """Test listing tenant schemas"""
        with patch.object(tenant_router.default_engine, 'connect') as mock_connect:
            mock_conn = Mock()
            mock_connect.return_value.__enter__.return_value = mock_conn
            
            mock_result = Mock()
            mock_result.fetchall.return_value = [
                ["tenant_tenant1"],
                ["tenant_tenant2"],
                ["tenant_tenant3"]
            ]
            mock_conn.execute.return_value = mock_result
            
            schemas = tenant_router.list_tenant_schemas()
            
            assert schemas == ["tenant_tenant1", "tenant_tenant2", "tenant_tenant3"]
    
    def test_get_tenant_stats(self, tenant_router):
        """Test getting tenant statistics"""
        tenant_id = "test-tenant"
        tenant_router.tenant_schemas[tenant_id] = "tenant_test_tenant"
        
        with patch.object(tenant_router.default_engine, 'connect') as mock_connect:
            mock_conn = Mock()
            mock_connect.return_value.__enter__.return_value = mock_conn
            
            mock_result = Mock()
            mock_result.fetchall.return_value = [
                {"tablename": "trades", "size": "1MB"},
                {"tablename": "portfolios", "size": "512KB"}
            ]
            mock_conn.execute.return_value = mock_result
            
            stats = tenant_router.get_tenant_stats(tenant_id)
            
            assert stats["tenant_id"] == tenant_id
            assert stats["schema_name"] == "tenant_test_tenant"
            assert "table_sizes" in stats
            assert "row_counts" in stats


class TestTenantRouterDecorator:
    """Test cases for tenant_required decorator"""
    
    @pytest.mark.asyncio
    async def test_tenant_required_success(self):
        """Test successful tenant_required decorator usage"""
        @tenant_required
        async def test_function(tenant_id, tenant_router=None):
            return f"Success for {tenant_id}"
        
        with patch('app.core.tenant_router.TenantRouter') as mock_router_class:
            mock_router = Mock()
            mock_router_class.return_value = mock_router
            mock_router.tenant_schemas = {}
            mock_router.create_tenant_schema = Mock(return_value=True)
            
            result = await test_function("test-tenant")
            
            assert result == "Success for test-tenant"
            mock_router.create_tenant_schema.assert_called_once_with("test-tenant")
    
    @pytest.mark.asyncio
    async def test_tenant_required_missing_tenant_id(self):
        """Test tenant_required decorator with missing tenant ID"""
        @tenant_required
        async def test_function(tenant_router=None):
            return "Success"
        
        with pytest.raises(ValueError, match="Tenant ID is required"):
            await test_function()


class TestTenantRouterGlobal:
    """Test cases for global tenant router functions"""
    
    def test_get_tenant_router(self):
        """Test getting tenant router instance"""
        with patch('app.core.tenant_router.TenantRouter') as mock_router_class:
            router = get_tenant_router()
            assert router is not None
            mock_router_class.assert_called_once()
    
    def test_get_global_tenant_router(self):
        """Test getting global tenant router instance"""
        with patch('app.core.tenant_router.TenantRouter') as mock_router_class:
            router = get_tenant_router()
            assert router is not None
            mock_router_class.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
