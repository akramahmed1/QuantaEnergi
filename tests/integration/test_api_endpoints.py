"""
Integration tests for API endpoints
Tests API endpoints with real HTTP requests
"""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
import json

from app.main import app
from app.core.config import settings


class TestHealthEndpoints:
    """Test cases for health and status endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "QuantaEnergi API v2.0"
        assert data["status"] == "operational"
        assert data["version"] == "2.0.0"
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "QuantaEnergi API"
        assert data["version"] == "2.0.0"
    
    def test_api_status_endpoint(self):
        """Test API status endpoint"""
        client = TestClient(app)
        response = client.get("/api/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["api_status"] == "operational"
        assert "features" in data
        assert "rate_limit" in data


class TestTenantManagementAPI:
    """Test cases for tenant management API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_auth_user(self):
        """Mock authenticated user"""
        return {
            "user_id": "test-user",
            "email": "test@example.com",
            "tenant_id": "test-tenant",
            "is_admin": True,
            "roles": ["admin"]
        }
    
    def test_create_tenant_success(self, client, mock_auth_user):
        """Test successful tenant creation"""
        tenant_data = {
            "tenant_id": "new-tenant",
            "name": "New Tenant",
            "region": "us",
            "subscription_tier": "basic",
            "max_users": 10,
            "max_trades_per_day": 1000,
            "features": ["trading", "analytics"]
        }
        
        with patch('app.api.tenant_management.get_current_user', return_value=mock_auth_user):
            with patch('app.api.tenant_management.get_tenant_service') as mock_service:
                mock_tenant_service = Mock()
                mock_tenant_service.create_tenant.return_value = True
                mock_tenant_service.get_tenant_info.return_value = Mock(
                    tenant_id="new-tenant",
                    name="New Tenant",
                    region="us",
                    subscription_tier="basic",
                    max_users=10,
                    max_trades_per_day=1000,
                    features=["trading", "analytics"],
                    created_at="2024-01-01T00:00:00Z",
                    updated_at="2024-01-01T00:00:00Z",
                    is_active=True
                )
                mock_service.return_value = mock_tenant_service
                
                response = client.post("/api/v1/tenant-management/tenants", json=tenant_data)
                
                assert response.status_code == 201
                data = response.json()
                assert data["tenant_id"] == "new-tenant"
                assert data["name"] == "New Tenant"
    
    def test_create_tenant_insufficient_permissions(self, client):
        """Test tenant creation with insufficient permissions"""
        mock_user = {
            "user_id": "test-user",
            "email": "test@example.com",
            "tenant_id": "test-tenant",
            "is_admin": False,
            "roles": ["user"]
        }
        
        tenant_data = {
            "tenant_id": "new-tenant",
            "name": "New Tenant"
        }
        
        with patch('app.api.tenant_management.get_current_user', return_value=mock_user):
            response = client.post("/api/v1/tenant-management/tenants", json=tenant_data)
            
            assert response.status_code == 403
            data = response.json()
            assert "Insufficient permissions" in data["detail"]
    
    def test_get_tenant_success(self, client, mock_auth_user):
        """Test successful tenant retrieval"""
        with patch('app.api.tenant_management.get_current_user', return_value=mock_auth_user):
            with patch('app.api.tenant_management.get_tenant_service') as mock_service:
                mock_tenant_service = Mock()
                mock_tenant_service.get_tenant_info.return_value = Mock(
                    tenant_id="test-tenant",
                    name="Test Tenant",
                    region="us",
                    subscription_tier="basic",
                    max_users=10,
                    max_trades_per_day=1000,
                    features=["trading"],
                    created_at="2024-01-01T00:00:00Z",
                    updated_at="2024-01-01T00:00:00Z",
                    is_active=True
                )
                mock_service.return_value = mock_tenant_service
                
                response = client.get("/api/v1/tenant-management/tenants/test-tenant")
                
                assert response.status_code == 200
                data = response.json()
                assert data["tenant_id"] == "test-tenant"
                assert data["name"] == "Test Tenant"
    
    def test_get_tenant_not_found(self, client, mock_auth_user):
        """Test tenant retrieval when tenant doesn't exist"""
        with patch('app.api.tenant_management.get_current_user', return_value=mock_auth_user):
            with patch('app.api.tenant_management.get_tenant_service') as mock_service:
                mock_tenant_service = Mock()
                mock_tenant_service.get_tenant_info.return_value = None
                mock_service.return_value = mock_tenant_service
                
                response = client.get("/api/v1/tenant-management/tenants/nonexistent-tenant")
                
                assert response.status_code == 404
                data = response.json()
                assert "Tenant not found" in data["detail"]
    
    def test_update_tenant_success(self, client, mock_auth_user):
        """Test successful tenant update"""
        update_data = {
            "name": "Updated Tenant",
            "max_users": 20
        }
        
        with patch('app.api.tenant_management.get_current_user', return_value=mock_auth_user):
            with patch('app.api.tenant_management.get_tenant_service') as mock_service:
                mock_tenant_service = Mock()
                mock_tenant_service.get_tenant_info.return_value = Mock(
                    tenant_id="test-tenant",
                    name="Original Tenant"
                )
                mock_tenant_service.update_tenant.return_value = True
                mock_tenant_service.get_tenant_info.return_value = Mock(
                    tenant_id="test-tenant",
                    name="Updated Tenant",
                    region="us",
                    subscription_tier="basic",
                    max_users=20,
                    max_trades_per_day=1000,
                    features=["trading"],
                    created_at="2024-01-01T00:00:00Z",
                    updated_at="2024-01-01T00:00:00Z",
                    is_active=True
                )
                mock_service.return_value = mock_tenant_service
                
                response = client.put(
                    "/api/v1/tenant-management/tenants/test-tenant",
                    json=update_data
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["name"] == "Updated Tenant"
                assert data["max_users"] == 20
    
    def test_delete_tenant_success(self, client, mock_auth_user):
        """Test successful tenant deletion"""
        with patch('app.api.tenant_management.get_current_user', return_value=mock_auth_user):
            with patch('app.api.tenant_management.get_tenant_service') as mock_service:
                mock_tenant_service = Mock()
                mock_tenant_service.get_tenant_info.return_value = Mock(
                    tenant_id="test-tenant"
                )
                mock_tenant_service.delete_tenant.return_value = True
                mock_service.return_value = mock_tenant_service
                
                response = client.delete("/api/v1/tenant-management/tenants/test-tenant")
                
                assert response.status_code == 204
    
    def test_list_tenants_success(self, client, mock_auth_user):
        """Test successful tenant listing"""
        with patch('app.api.tenant_management.get_current_user', return_value=mock_auth_user):
            with patch('app.api.tenant_management.get_tenant_service') as mock_service:
                mock_tenant_service = Mock()
                mock_tenant_service.list_tenants.return_value = [
                    Mock(
                        tenant_id="tenant1",
                        name="Tenant 1",
                        region="us",
                        subscription_tier="basic",
                        max_users=10,
                        max_trades_per_day=1000,
                        features=["trading"],
                        created_at="2024-01-01T00:00:00Z",
                        updated_at="2024-01-01T00:00:00Z",
                        is_active=True
                    ),
                    Mock(
                        tenant_id="tenant2",
                        name="Tenant 2",
                        region="eu",
                        subscription_tier="premium",
                        max_users=50,
                        max_trades_per_day=5000,
                        features=["trading", "analytics"],
                        created_at="2024-01-01T00:00:00Z",
                        updated_at="2024-01-01T00:00:00Z",
                        is_active=True
                    )
                ]
                mock_service.return_value = mock_tenant_service
                
                response = client.get("/api/v1/tenant-management/tenants")
                
                assert response.status_code == 200
                data = response.json()
                assert data["total_count"] == 2
                assert len(data["tenants"]) == 2
                assert data["page"] == 1
                assert data["page_size"] == 20
    
    def test_get_tenant_stats_success(self, client, mock_auth_user):
        """Test successful tenant statistics retrieval"""
        with patch('app.api.tenant_management.get_current_user', return_value=mock_auth_user):
            with patch('app.api.tenant_management.get_tenant_service') as mock_service:
                mock_tenant_service = Mock()
                mock_tenant_service.get_tenant_stats.return_value = {
                    "tenant_id": "test-tenant",
                    "trade_count": 100,
                    "portfolio_count": 5,
                    "position_count": 25,
                    "total_trade_value": 100000.0,
                    "database_stats": {"size": "1MB"},
                    "timestamp": "2024-01-01T00:00:00Z"
                }
                mock_service.return_value = mock_tenant_service
                
                response = client.get("/api/v1/tenant-management/tenants/test-tenant/stats")
                
                assert response.status_code == 200
                data = response.json()
                assert data["tenant_id"] == "test-tenant"
                assert data["trade_count"] == 100
                assert data["portfolio_count"] == 5
                assert data["position_count"] == 25
                assert data["total_trade_value"] == 100000.0
    
    def test_get_tenant_features_success(self, client, mock_auth_user):
        """Test successful tenant features retrieval"""
        with patch('app.api.tenant_management.get_current_user', return_value=mock_auth_user):
            with patch('app.api.tenant_management.get_tenant_service') as mock_service:
                mock_tenant_service = Mock()
                mock_tenant_service.get_tenant_features.return_value = ["trading", "analytics", "compliance"]
                mock_service.return_value = mock_tenant_service
                
                response = client.get("/api/v1/tenant-management/tenants/test-tenant/features")
                
                assert response.status_code == 200
                data = response.json()
                assert data["features"] == ["trading", "analytics", "compliance"]
    
    def test_check_tenant_feature_success(self, client, mock_auth_user):
        """Test successful tenant feature check"""
        with patch('app.api.tenant_management.get_current_user', return_value=mock_auth_user):
            with patch('app.api.tenant_management.get_tenant_service') as mock_service:
                mock_tenant_service = Mock()
                mock_tenant_service.is_feature_enabled.return_value = True
                mock_service.return_value = mock_tenant_service
                
                response = client.get("/api/v1/tenant-management/tenants/test-tenant/features/trading")
                
                assert response.status_code == 200
                data = response.json()
                assert data["feature"] == "trading"
                assert data["enabled"] is True


class TestGraphQLEndpoints:
    """Test cases for GraphQL endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_graphql_hello_query(self, client):
        """Test GraphQL hello query"""
        query = """
        query {
            hello
        }
        """
        
        response = client.post("/api/graphql", json={"query": query})
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["hello"] == "Hello from QuantaEnergi GraphQL!"
    
    def test_graphql_get_trades_query(self, client):
        """Test GraphQL get trades query"""
        query = """
        query {
            getTrades(limit: 5) {
                id
                commodity
                type
                quantity
                price
                totalValue
                status
            }
        }
        """
        
        response = client.post("/api/graphql", json={"query": query})
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "getTrades" in data["data"]
        assert len(data["data"]["getTrades"]) == 5
        
        trade = data["data"]["getTrades"][0]
        assert "id" in trade
        assert "commodity" in trade
        assert "type" in trade
        assert "quantity" in trade
        assert "price" in trade
        assert "totalValue" in trade
        assert "status" in trade
    
    def test_graphql_get_market_data_query(self, client):
        """Test GraphQL get market data query"""
        query = """
        query {
            getMarketData {
                crudeOil {
                    price
                    change
                    volume
                    source
                }
                naturalGas {
                    price
                    change
                    volume
                    source
                }
                electricity {
                    price
                    change
                    volume
                    source
                }
                carbonCredits {
                    price
                    change
                    volume
                    source
                }
            }
        }
        """
        
        response = client.post("/api/graphql", json={"query": query})
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "getMarketData" in data["data"]
        
        market_data = data["data"]["getMarketData"]
        assert "crudeOil" in market_data
        assert "naturalGas" in market_data
        assert "electricity" in market_data
        assert "carbonCredits" in market_data
        
        # Check crude oil data
        crude_oil = market_data["crudeOil"]
        assert "price" in crude_oil
        assert "change" in crude_oil
        assert "volume" in crude_oil
        assert "source" in crude_oil
    
    def test_graphql_invalid_query(self, client):
        """Test GraphQL with invalid query"""
        query = """
        query {
            invalidField
        }
        """
        
        response = client.post("/api/graphql", json={"query": query})
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data


class TestErrorHandling:
    """Test cases for error handling"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_404_error(self, client):
        """Test 404 error handling"""
        response = client.get("/nonexistent-endpoint")
        
        assert response.status_code == 404
    
    def test_422_validation_error(self, client):
        """Test 422 validation error handling"""
        invalid_data = {
            "invalid_field": "value"
        }
        
        response = client.post("/api/v1/tenant-management/tenants", json=invalid_data)
        
        assert response.status_code == 422
    
    def test_500_internal_server_error(self, client):
        """Test 500 internal server error handling"""
        with patch('app.api.tenant_management.get_tenant_service') as mock_service:
            mock_tenant_service = Mock()
            mock_tenant_service.create_tenant.side_effect = Exception("Database error")
            mock_service.return_value = mock_tenant_service
            
            tenant_data = {
                "tenant_id": "error-tenant",
                "name": "Error Tenant"
            }
            
            mock_auth_user = {
                "user_id": "test-user",
                "is_admin": True
            }
            
            with patch('app.api.tenant_management.get_current_user', return_value=mock_auth_user):
                response = client.post("/api/v1/tenant-management/tenants", json=tenant_data)
                
                assert response.status_code == 500
                data = response.json()
                assert "Internal server error" in data["detail"]


class TestCORS:
    """Test cases for CORS functionality"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_cors_headers(self, client):
        """Test CORS headers are present"""
        response = client.options("/", headers={"Origin": "https://example.com"})
        
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers


if __name__ == "__main__":
    pytest.main([__file__])
