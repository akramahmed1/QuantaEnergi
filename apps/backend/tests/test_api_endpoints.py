"""
Test suite for API endpoints
Tests all API routes and their responses
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from app.main import app

client = TestClient(app)

class TestHealthEndpoint:
    """Test cases for health check endpoint"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert data["status"] == "healthy"

class TestAuthEndpoints:
    """Test cases for authentication endpoints"""
    
    def test_login_success(self):
        """Test successful login"""
        response = client.post(
            "/api/v1/login",
            data={"username": "admin", "password": "secret"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = client.post(
            "/api/v1/login",
            data={"username": "invalid", "password": "wrong"}
        )
        assert response.status_code == 401
    
    def test_login_missing_credentials(self):
        """Test login with missing credentials"""
        response = client.post("/api/v1/login", data={})
        assert response.status_code == 422  # Validation error
    
    def test_get_current_user(self):
        """Test getting current user information"""
        # First login to get token
        login_response = client.post(
            "/api/v1/login",
            data={"username": "admin", "password": "secret"}
        )
        token = login_response.json()["access_token"]
        
        # Then get current user
        response = client.get(
            "/api/v1/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "username" in data
        assert data["username"] == "admin"

class TestTradeLifecycleEndpoints:
    """Test cases for trade lifecycle endpoints"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Login to get token
        login_response = client.post(
            "/api/v1/login",
            data={"username": "admin", "password": "secret"}
        )
        self.token = login_response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_capture_trade(self):
        """Test trade capture"""
        trade_data = {
            "commodity": "electricity",
            "quantity": 100,
            "price": 50.0,
            "trade_type": "spot"
        }
        
        response = client.post(
            "/api/v1/capture",
            json=trade_data,
            headers=self.headers
        )
        assert response.status_code == 201
        
        data = response.json()
        assert "id" in data
        assert "commodity" in data
        assert "quantity" in data
        assert "price" in data
        assert "trade_type" in data
        assert "status" in data
        assert "timestamp" in data
        assert "user_id" in data
        
        assert data["commodity"] == trade_data["commodity"]
        assert data["quantity"] == trade_data["quantity"]
        assert data["price"] == trade_data["price"]
        assert data["trade_type"] == trade_data["trade_type"]
        assert data["status"] == "captured"
        assert data["user_id"] == "admin"
    
    def test_capture_trade_unauthorized(self):
        """Test trade capture without authentication"""
        trade_data = {
            "commodity": "electricity",
            "quantity": 100,
            "price": 50.0,
            "trade_type": "spot"
        }
        
        response = client.post("/api/v1/capture", json=trade_data)
        assert response.status_code == 401
    
    def test_validate_trade(self):
        """Test trade validation"""
        # First capture a trade
        trade_data = {
            "commodity": "electricity",
            "quantity": 100,
            "price": 50.0,
            "trade_type": "spot"
        }
        
        capture_response = client.post(
            "/api/v1/capture",
            json=trade_data,
            headers=self.headers
        )
        trade_id = capture_response.json()["id"]
        
        # Then validate it
        response = client.post(
            f"/api/v1/validate/{trade_id}",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "validated"
        assert data["id"] == trade_id
    
    def test_validate_nonexistent_trade(self):
        """Test validation of non-existent trade"""
        response = client.post(
            "/api/v1/validate/nonexistent-trade-id",
            headers=self.headers
        )
        assert response.status_code == 404
    
    def test_settle_trade(self):
        """Test trade settlement"""
        # First capture and validate a trade
        trade_data = {
            "commodity": "electricity",
            "quantity": 100,
            "price": 50.0,
            "trade_type": "spot"
        }
        
        capture_response = client.post(
            "/api/v1/capture",
            json=trade_data,
            headers=self.headers
        )
        trade_id = capture_response.json()["id"]
        
        # Then settle it
        response = client.post(
            f"/api/v1/settle/{trade_id}",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "settled"
        assert data["id"] == trade_id
    
    def test_get_trades(self):
        """Test getting user trades"""
        # First create some trades
        trade_data = {
            "commodity": "electricity",
            "quantity": 100,
            "price": 50.0,
            "trade_type": "spot"
        }
        
        client.post(
            "/api/v1/capture",
            json=trade_data,
            headers=self.headers
        )
        
        # Then get all trades
        response = client.get("/api/v1/trades", headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        trade = data[0]
        assert "id" in trade
        assert "commodity" in trade
        assert "quantity" in trade
        assert "price" in trade
        assert "status" in trade
    
    def test_get_trade_by_id(self):
        """Test getting specific trade by ID"""
        # First capture a trade
        trade_data = {
            "commodity": "electricity",
            "quantity": 100,
            "price": 50.0,
            "trade_type": "spot"
        }
        
        capture_response = client.post(
            "/api/v1/capture",
            json=trade_data,
            headers=self.headers
        )
        trade_id = capture_response.json()["id"]
        
        # Then get it by ID
        response = client.get(
            f"/api/v1/trades/{trade_id}",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == trade_id
        assert data["commodity"] == trade_data["commodity"]

class TestAnalyticsEndpoints:
    """Test cases for analytics endpoints"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Login to get token
        login_response = client.post(
            "/api/v1/login",
            data={"username": "admin", "password": "secret"}
        )
        self.token = login_response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_generate_forecast(self):
        """Test AI price forecast generation"""
        response = client.post(
            "/api/v1/forecast?periods=30",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "forecast" in data
        assert "periods" in data
        assert "unit" in data
        
        assert data["periods"] == 30
        assert data["unit"] == "USD/MWh"
        assert len(data["forecast"]) == 30
    
    def test_get_market_insights(self):
        """Test market insights generation"""
        response = client.get(
            "/api/v1/forecast/insights/crude_oil",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "sentiment" in data
        assert "risk_level" in data
        assert "recommendation" in data
        assert "price_change_percentage" in data
    
    def test_optimize_portfolio(self):
        """Test portfolio optimization"""
        optimization_data = {
            "returns": [0.1, 0.05, 0.08],
            "volatilities": [0.2, 0.1, 0.15],
            "budget": 1.0
        }
        
        response = client.post(
            "/api/v1/optimize/portfolio",
            json=optimization_data,
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "optimized_weights" in data
        assert "expected_return" in data
        assert "expected_volatility" in data
        assert "method" in data
    
    def test_optimize_strategy(self):
        """Test trading strategy optimization"""
        strategy_data = [
            {"price": 50.0, "volume": 1000, "timestamp": "2024-01-01"},
            {"price": 55.0, "volume": 1200, "timestamp": "2024-01-02"}
        ]
        
        response = client.post(
            "/api/v1/optimize/strategy",
            json=strategy_data,
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "optimized_strategy_parameters" in data
        assert "performance_metrics" in data
        assert "method" in data
    
    def test_create_carbon_trade(self):
        """Test carbon credit trade creation"""
        carbon_trade_data = {
            "buyer_address": "0xBuyer123",
            "seller_address": "0xSeller456",
            "carbon_amount": 100.0,
            "price": 25.5
        }
        
        response = client.post(
            "/api/v1/blockchain/carbon-trade",
            json=carbon_trade_data,
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "trade_id" in data
        assert "buyer_address" in data
        assert "seller_address" in data
        assert "carbon_amount" in data
        assert "price" in data
        assert "status" in data
    
    def test_get_esg_score(self):
        """Test ESG score retrieval"""
        response = client.get(
            "/api/v1/blockchain/esg-score/companyA_address",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "score" in data
        assert "last_updated" in data
        assert "details" in data

class TestComplianceEndpoints:
    """Test cases for compliance endpoints"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Login to get token
        login_response = client.post(
            "/api/v1/login",
            data={"username": "admin", "password": "secret"}
        )
        self.token = login_response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_sharia_compliance_check(self):
        """Test Sharia compliance checking"""
        trade_data = {
            "id": "test-trade-123",
            "commodity": "electricity",
            "price": 50.0,
            "quantity": 100,
            "trade_type": "spot",
            "delivery_date": "2024-02-01",
            "delivery_location": "New York"
        }
        
        response = client.post(
            "/api/v1/sharia/check",
            json=trade_data,
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "trade_id" in data
        assert "overall_status" in data
        assert "compliance_checks" in data
        assert "recommendations" in data
        assert "compliance_score" in data
    
    def test_generate_compliance_report(self):
        """Test compliance report generation"""
        report_data = {
            "report_type": "cftc",
            "start_date": "2024-01-01T00:00:00Z",
            "end_date": "2024-01-31T23:59:59Z",
            "data": [],
            "anonymize": True
        }
        
        response = client.post(
            "/api/v1/reports/generate",
            json=report_data,
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "report_id" in data
        assert "report_type" in data
        assert "report_name" in data
        assert "generated_at" in data
        assert "data_summary" in data
        assert "compliance_status" in data
    
    def test_get_billing_plans(self):
        """Test billing plans retrieval"""
        response = client.get(
            "/api/v1/billing/plans",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "plans" in data
        assert "generated_at" in data
        
        plans = data["plans"]
        assert "basic" in plans
        assert "professional" in plans
        assert "enterprise" in plans

class TestErrorHandling:
    """Test cases for error handling"""
    
    def test_404_endpoint(self):
        """Test 404 for non-existent endpoint"""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    def test_unauthorized_access(self):
        """Test unauthorized access to protected endpoints"""
        response = client.get("/api/v1/trades")
        assert response.status_code == 401
    
    def test_invalid_json(self):
        """Test invalid JSON in request body"""
        response = client.post(
            "/api/v1/capture",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

if __name__ == '__main__':
    pytest.main([__file__])
