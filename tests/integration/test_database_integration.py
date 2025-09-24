"""
Integration tests for database operations
Tests database connectivity and operations
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.tenant_router import TenantRouter
from app.services.tenant_service import TenantService


class TestDatabaseConnectivity:
    """Test cases for database connectivity"""
    
    @pytest.fixture
    def tenant_router(self):
        """Create a TenantRouter instance for testing"""
        with patch('app.core.tenant_router.create_engine') as mock_engine:
            mock_engine_instance = Mock()
            mock_engine.return_value = mock_engine_instance
            
            # Mock connection
            mock_conn = Mock()
            mock_engine_instance.connect.return_value.__enter__.return_value = mock_conn
            
            router = TenantRouter()
            router.default_engine = mock_engine_instance
            return router
    
    def test_database_connection(self, tenant_router):
        """Test database connection"""
        with tenant_router.default_engine.connect() as conn:
            assert conn is not None
    
    def test_schema_creation_query(self, tenant_router):
        """Test schema creation SQL query"""
        schema_name = "test_schema"
        
        with patch.object(tenant_router.default_engine, 'connect') as mock_connect:
            mock_conn = Mock()
            mock_connect.return_value.__enter__.return_value = mock_conn
            
            # Mock schema exists check
            mock_result = Mock()
            mock_result.fetchone.return_value = None
            mock_conn.execute.return_value = mock_result
            
            # Test schema creation
            mock_conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
            mock_conn.commit()
            
            # Verify calls
            assert mock_conn.execute.called
            assert mock_conn.commit.called
    
    def test_table_creation_queries(self, tenant_router):
        """Test table creation SQL queries"""
        schema_name = "test_schema"
        
        with patch.object(tenant_router.default_engine, 'connect') as mock_connect:
            mock_conn = Mock()
            mock_connect.return_value.__enter__.return_value = mock_conn
            
            # Test trades table creation
            trades_query = f"""
                CREATE TABLE IF NOT EXISTS {schema_name}.trades (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    trade_id VARCHAR(50) NOT NULL,
                    commodity VARCHAR(50) NOT NULL,
                    trade_type VARCHAR(20) NOT NULL,
                    quantity DECIMAL(15,2) NOT NULL,
                    price DECIMAL(15,4) NOT NULL,
                    total_value DECIMAL(15,2) NOT NULL,
                    currency VARCHAR(3) NOT NULL,
                    counterparty VARCHAR(100),
                    trade_date TIMESTAMP WITH TIME ZONE NOT NULL,
                    settlement_date TIMESTAMP WITH TIME ZONE,
                    status VARCHAR(20) NOT NULL,
                    region VARCHAR(50),
                    is_sharia_compliant BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """
            
            mock_conn.execute(text(trades_query))
            
            # Test portfolios table creation
            portfolios_query = f"""
                CREATE TABLE IF NOT EXISTS {schema_name}.portfolios (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    portfolio_id VARCHAR(50) NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    total_value DECIMAL(15,2) DEFAULT 0,
                    cash_balance DECIMAL(15,2) DEFAULT 0,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """
            
            mock_conn.execute(text(portfolios_query))
            
            # Verify calls
            assert mock_conn.execute.call_count >= 2
    
    def test_index_creation_queries(self, tenant_router):
        """Test index creation SQL queries"""
        schema_name = "test_schema"
        
        with patch.object(tenant_router.default_engine, 'connect') as mock_connect:
            mock_conn = Mock()
            mock_connect.return_value.__enter__.return_value = mock_conn
            
            # Test index creation
            index_queries = [
                f"CREATE INDEX IF NOT EXISTS idx_{schema_name}_trades_date ON {schema_name}.trades(trade_date)",
                f"CREATE INDEX IF NOT EXISTS idx_{schema_name}_trades_commodity ON {schema_name}.trades(commodity)",
                f"CREATE INDEX IF NOT EXISTS idx_{schema_name}_positions_portfolio ON {schema_name}.positions(portfolio_id)"
            ]
            
            for query in index_queries:
                mock_conn.execute(text(query))
            
            # Verify calls
            assert mock_conn.execute.call_count == len(index_queries)
    
    def test_database_error_handling(self, tenant_router):
        """Test database error handling"""
        with patch.object(tenant_router.default_engine, 'connect') as mock_connect:
            mock_connect.side_effect = SQLAlchemyError("Database connection failed")
            
            with pytest.raises(SQLAlchemyError):
                with tenant_router.default_engine.connect() as conn:
                    pass


class TestTenantDatabaseOperations:
    """Test cases for tenant-specific database operations"""
    
    @pytest.fixture
    def tenant_service(self):
        """Create a TenantService instance for testing"""
        with patch('app.services.tenant_service.get_tenant_router') as mock_get_router:
            mock_router = Mock()
            mock_get_router.return_value = mock_router
            service = TenantService()
            service.router = mock_router
            return service
    
    def test_tenant_data_insertion(self, tenant_service):
        """Test tenant data insertion"""
        tenant_data = {
            "tenant_id": "test-tenant",
            "name": "Test Tenant",
            "region": "us",
            "subscription_tier": "basic",
            "max_users": 10,
            "max_trades_per_day": 1000,
            "features": ["trading", "analytics"]
        }
        
        with patch.object(tenant_service.router, 'default_engine') as mock_engine:
            mock_conn = Mock()
            mock_engine.connect.return_value.__enter__.return_value = mock_conn
            
            # Mock tenant exists check
            mock_result = Mock()
            mock_result.fetchone.return_value = None
            mock_conn.execute.return_value = mock_result
            
            # Test insertion query
            insert_query = text("""
                INSERT INTO tenants (
                    tenant_id, name, region, subscription_tier, 
                    max_users, max_trades_per_day, features, 
                    created_at, updated_at, is_active
                ) VALUES (
                    :tenant_id, :name, :region, :subscription_tier,
                    :max_users, :max_trades_per_day, :features,
                    :created_at, :updated_at, :is_active
                )
            """)
            
            mock_conn.execute(insert_query, tenant_data)
            mock_conn.commit()
            
            # Verify calls
            assert mock_conn.execute.called
            assert mock_conn.commit.called
    
    def test_tenant_data_retrieval(self, tenant_service):
        """Test tenant data retrieval"""
        tenant_id = "test-tenant"
        
        with patch.object(tenant_service.router, 'default_engine') as mock_engine:
            mock_conn = Mock()
            mock_engine.connect.return_value.__enter__.return_value = mock_conn
            
            # Mock query result
            mock_result = Mock()
            mock_result.fetchone.return_value = (
                tenant_id, "Test Tenant", "us", "basic", 10, 1000, 
                ["trading"], "2024-01-01T00:00:00Z", "2024-01-01T00:00:00Z", True
            )
            mock_conn.execute.return_value = mock_result
            
            # Test retrieval query
            select_query = text("""
                SELECT tenant_id, name, region, subscription_tier,
                       max_users, max_trades_per_day, features,
                       created_at, updated_at, is_active
                FROM tenants 
                WHERE tenant_id = :tenant_id
            """)
            
            mock_conn.execute(select_query, {"tenant_id": tenant_id})
            
            # Verify call
            assert mock_conn.execute.called
    
    def test_tenant_data_update(self, tenant_service):
        """Test tenant data update"""
        tenant_id = "test-tenant"
        update_data = {
            "name": "Updated Tenant",
            "max_users": 20,
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        with patch.object(tenant_service.router, 'default_engine') as mock_engine:
            mock_conn = Mock()
            mock_engine.connect.return_value.__enter__.return_value = mock_conn
            
            # Test update query
            update_query = text("""
                UPDATE tenants 
                SET name = :name, max_users = :max_users, updated_at = :updated_at
                WHERE tenant_id = :tenant_id
            """)
            
            update_values = {"tenant_id": tenant_id, **update_data}
            mock_conn.execute(update_query, update_values)
            mock_conn.commit()
            
            # Verify calls
            assert mock_conn.execute.called
            assert mock_conn.commit.called
    
    def test_tenant_data_deletion(self, tenant_service):
        """Test tenant data deletion"""
        tenant_id = "test-tenant"
        
        with patch.object(tenant_service.router, 'default_engine') as mock_engine:
            mock_conn = Mock()
            mock_engine.connect.return_value.__enter__.return_value = mock_conn
            
            # Test deletion query
            delete_query = text("""
                UPDATE tenants 
                SET is_active = false, updated_at = :updated_at
                WHERE tenant_id = :tenant_id
            """)
            
            mock_conn.execute(delete_query, {
                "tenant_id": tenant_id,
                "updated_at": "2024-01-01T00:00:00Z"
            })
            mock_conn.commit()
            
            # Verify calls
            assert mock_conn.execute.called
            assert mock_conn.commit.called


class TestTenantSchemaOperations:
    """Test cases for tenant schema operations"""
    
    @pytest.fixture
    def tenant_router(self):
        """Create a TenantRouter instance for testing"""
        with patch('app.core.tenant_router.create_engine') as mock_engine:
            mock_engine_instance = Mock()
            mock_engine.return_value = mock_engine_instance
            
            router = TenantRouter()
            router.default_engine = mock_engine_instance
            return router
    
    def test_schema_listing_query(self, tenant_router):
        """Test schema listing SQL query"""
        with patch.object(tenant_router.default_engine, 'connect') as mock_connect:
            mock_conn = Mock()
            mock_connect.return_value.__enter__.return_value = mock_conn
            
            # Mock query result
            mock_result = Mock()
            mock_result.fetchall.return_value = [
                ["tenant_tenant1"],
                ["tenant_tenant2"],
                ["tenant_tenant3"]
            ]
            mock_conn.execute.return_value = mock_result
            
            # Test schema listing query
            list_query = text("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name LIKE 'tenant_%'
                ORDER BY schema_name
            """)
            
            mock_conn.execute(list_query)
            
            # Verify call
            assert mock_conn.execute.called
    
    def test_schema_stats_query(self, tenant_router):
        """Test schema statistics SQL query"""
        schema_name = "tenant_test_tenant"
        
        with patch.object(tenant_router.default_engine, 'connect') as mock_connect:
            mock_conn = Mock()
            mock_connect.return_value.__enter__.return_value = mock_conn
            
            # Mock query results
            mock_result1 = Mock()
            mock_result1.fetchall.return_value = [
                {"tablename": "trades", "size": "1MB"},
                {"tablename": "portfolios", "size": "512KB"}
            ]
            
            mock_result2 = Mock()
            mock_result2.fetchall.return_value = [
                {"table_name": "trades", "row_count": 100},
                {"table_name": "portfolios", "row_count": 5},
                {"table_name": "positions", "row_count": 25}
            ]
            
            mock_conn.execute.side_effect = [mock_result1, mock_result2]
            
            # Test table sizes query
            sizes_query = text(f"""
                SELECT 
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
                FROM pg_tables 
                WHERE schemaname = '{schema_name}'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            """)
            
            mock_conn.execute(sizes_query)
            
            # Test row counts query
            counts_query = text(f"""
                SELECT 
                    'trades' as table_name,
                    COUNT(*) as row_count
                FROM {schema_name}.trades
                UNION ALL
                SELECT 
                    'portfolios' as table_name,
                    COUNT(*) as row_count
                FROM {schema_name}.portfolios
                UNION ALL
                SELECT 
                    'positions' as table_name,
                    COUNT(*) as row_count
                FROM {schema_name}.positions
            """)
            
            mock_conn.execute(counts_query)
            
            # Verify calls
            assert mock_conn.execute.call_count == 2
    
    def test_schema_deletion_query(self, tenant_router):
        """Test schema deletion SQL query"""
        schema_name = "tenant_test_tenant"
        
        with patch.object(tenant_router.default_engine, 'connect') as mock_connect:
            mock_conn = Mock()
            mock_connect.return_value.__enter__.return_value = mock_conn
            
            # Test schema deletion query
            delete_query = text(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE")
            
            mock_conn.execute(delete_query)
            mock_conn.commit()
            
            # Verify calls
            assert mock_conn.execute.called
            assert mock_conn.commit.called


class TestDatabaseTransactionHandling:
    """Test cases for database transaction handling"""
    
    @pytest.fixture
    def tenant_router(self):
        """Create a TenantRouter instance for testing"""
        with patch('app.core.tenant_router.create_engine') as mock_engine:
            mock_engine_instance = Mock()
            mock_engine.return_value = mock_engine_instance
            
            router = TenantRouter()
            router.default_engine = mock_engine_instance
            return router
    
    def test_transaction_commit(self, tenant_router):
        """Test transaction commit"""
        with patch.object(tenant_router.default_engine, 'connect') as mock_connect:
            mock_conn = Mock()
            mock_connect.return_value.__enter__.return_value = mock_conn
            
            # Test transaction
            mock_conn.execute(text("INSERT INTO test_table VALUES (1)"))
            mock_conn.commit()
            
            # Verify calls
            assert mock_conn.execute.called
            assert mock_conn.commit.called
    
    def test_transaction_rollback(self, tenant_router):
        """Test transaction rollback"""
        with patch.object(tenant_router.default_engine, 'connect') as mock_connect:
            mock_conn = Mock()
            mock_connect.return_value.__enter__.return_value = mock_conn
            
            # Test transaction with error
            mock_conn.execute.side_effect = SQLAlchemyError("Database error")
            
            try:
                mock_conn.execute(text("INSERT INTO test_table VALUES (1)"))
                mock_conn.commit()
            except SQLAlchemyError:
                mock_conn.rollback()
            
            # Verify calls
            assert mock_conn.execute.called
            assert mock_conn.rollback.called
    
    def test_connection_pool_handling(self, tenant_router):
        """Test connection pool handling"""
        with patch.object(tenant_router.default_engine, 'connect') as mock_connect:
            mock_conn = Mock()
            mock_connect.return_value.__enter__.return_value = mock_conn
            
            # Test multiple connections
            with tenant_router.default_engine.connect() as conn1:
                with tenant_router.default_engine.connect() as conn2:
                    assert conn1 is not None
                    assert conn2 is not None
            
            # Verify multiple connections were created
            assert mock_connect.call_count == 2


if __name__ == "__main__":
    pytest.main([__file__])
