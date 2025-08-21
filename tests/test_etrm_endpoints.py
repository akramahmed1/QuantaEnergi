"""
Comprehensive tests for ETRM/CTRM endpoints.

This module tests all ETRM functionality including contracts, trading,
risk management, compliance, and market data endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from decimal import Decimal
import json

from src.energyopti_pro.main import app

client = TestClient(app)

# Test data
test_contract = {
    "contract_type": "PPA",
    "counterparty_id": 1,
    "commodity": "power",
    "delivery_location": "Dubai",
    "delivery_period_start": (datetime.now() + timedelta(days=30)).isoformat(),
    "delivery_period_end": (datetime.now() + timedelta(days=60)).isoformat(),
    "quantity": 100.0,
    "unit": "MWh",
    "price": 75.50,
    "currency": "USD",
    "region": "ME",
    "compliance_flags": {"sharia_compliant": True}
}

test_trade = {
    "contract_id": "test-contract-id",
    "trader_id": 1,
    "side": "buy",
    "quantity": 50.0,
    "price": 75.50,
    "trade_date": datetime.now().isoformat(),
    "region": "ME"
}

class TestETRMEndpoints:
    """Test suite for ETRM endpoints."""
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_create_contract(self):
        """Test contract creation endpoint."""
        response = client.post("/api/v1/etrm/contracts/", json=test_contract)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "created"
        assert "contract_id" in data
        assert "contract_number" in data
    
    def test_get_contracts(self):
        """Test contract retrieval endpoint."""
        response = client.get("/api/v1/etrm/contracts/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_contracts_with_filters(self):
        """Test contract retrieval with filters."""
        response = client.get("/api/v1/etrm/contracts/?region=ME&commodity=power")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_execute_trade(self):
        """Test trade execution endpoint."""
        response = client.post("/api/v1/etrm/trades/", json=test_trade)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "executed"
        assert "trade_id" in data
    
    def test_get_trades(self):
        """Test trade retrieval endpoint."""
        response = client.get("/api/v1/etrm/trades/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_positions(self):
        """Test position retrieval endpoint."""
        response = client.get("/api/v1/etrm/positions/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_calculate_var(self):
        """Test VaR calculation endpoint."""
        response = client.get("/api/v1/etrm/risk/var?region=ME&confidence_level=0.95")
        assert response.status_code == 200
        data = response.json()
        assert "var" in data
        assert "confidence_level" in data
        assert "region" in data
    
    def test_get_risk_limits(self):
        """Test risk limits endpoint."""
        response = client.get("/api/v1/etrm/risk/limits?region=ME")
        assert response.status_code == 200
        data = response.json()
        assert "region" in data
        assert "risk_limits" in data
    
    def test_get_compliance_status(self):
        """Test compliance status endpoint."""
        response = client.get("/api/v1/etrm/compliance/status")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_submit_compliance_report(self):
        """Test compliance report submission."""
        report = {
            "regulation_name": "ADNOC",
            "report_period": "Q1-2024",
            "data": {"emissions": 1000, "compliance_score": 95},
            "region": "ME"
        }
        response = client.post("/api/v1/etrm/compliance/report", json=report)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "submitted"
    
    def test_get_market_prices(self):
        """Test market prices endpoint."""
        response = client.get("/api/v1/etrm/market/prices")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_settlements(self):
        """Test settlements endpoint."""
        response = client.get("/api/v1/etrm/settlements/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_regional_compliance_rules(self):
        """Test regional compliance rules endpoint."""
        response = client.get("/api/v1/etrm/compliance/rules/ME")
        assert response.status_code == 200
        data = response.json()
        assert "region" in data
        assert "compliance_rules" in data
    
    def test_invalid_region_compliance_rules(self):
        """Test compliance rules with invalid region."""
        response = client.get("/api/v1/etrm/compliance/rules/INVALID")
        assert response.status_code == 404
    
    def test_contract_validation(self):
        """Test contract validation."""
        invalid_contract = test_contract.copy()
        invalid_contract["delivery_period_end"] = (datetime.now() - timedelta(days=1)).isoformat()
        
        response = client.post("/api/v1/etrm/contracts/", json=invalid_contract)
        assert response.status_code == 400
        assert "Delivery end must be after start" in response.json()["detail"]
    
    def test_trade_validation(self):
        """Test trade validation."""
        invalid_trade = test_trade.copy()
        invalid_trade["side"] = "invalid"
        
        response = client.post("/api/v1/etrm/trades/", json=invalid_trade)
        assert response.status_code == 400
        assert "Side must be buy or sell" in response.json()["detail"]


class TestRBACSystem:
    """Test suite for RBAC functionality."""
    
    def test_role_hierarchy(self):
        """Test role hierarchy structure."""
        from src.energyopti_pro.core.rbac import get_role_hierarchy
        
        hierarchy = get_role_hierarchy()
        assert "super_admin" in hierarchy
        assert "trader" in hierarchy
        assert "viewer" in hierarchy
        
        # Check role levels
        assert hierarchy["super_admin"]["level"] > hierarchy["trader"]["level"]
        assert hierarchy["trader"]["level"] > hierarchy["viewer"]["level"]
    
    def test_feature_permissions(self):
        """Test feature permissions mapping."""
        from src.energyopti_pro.core.rbac import get_feature_permissions
        
        permissions = get_feature_permissions()
        assert "trading" in permissions
        assert "risk_management" in permissions
        assert "compliance" in permissions
    
    def test_user_permissions(self):
        """Test user permission retrieval."""
        from src.energyopti_pro.core.rbac import get_user_permissions
        
        trader_permissions = get_user_permissions("trader")
        assert "trading" in trader_permissions
        assert "position_management" in trader_permissions
        
        admin_permissions = get_user_permissions("super_admin")
        assert "*" in admin_permissions  # All permissions


class TestDatabaseModels:
    """Test suite for database models."""
    
    def test_user_model(self):
        """Test User model structure."""
        from src.energyopti_pro.db.models import User
        
        user = User(
            username="test_user",
            email="test@example.com",
            hashed_password="hashed_password",
            role="trader",
            region="ME"
        )
        
        assert user.username == "test_user"
        assert user.role == "trader"
        assert user.region == "ME"
    
    def test_contract_model(self):
        """Test Contract model structure."""
        from src.energyopti_pro.db.models import Contract
        
        contract = Contract(
            contract_number="CTR-TEST-001",
            contract_type="PPA",
            counterparty_id=1,
            commodity="power",
            delivery_location="Dubai",
            delivery_period_start=datetime.now(),
            delivery_period_end=datetime.now() + timedelta(days=30),
            quantity=100.0,
            unit="MWh",
            price=Decimal("75.50"),
            currency="USD",
            region="ME"
        )
        
        assert contract.contract_number == "CTR-TEST-001"
        assert contract.commodity == "power"
        assert contract.region == "ME"


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 