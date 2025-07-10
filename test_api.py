from fastapi.testclient import TestClient
from main import app
import json
import pytest

client = TestClient(app)

@pytest.fixture
def test_token():
    # Get valid test token
    response = client.post(
        "/token",
        data={"username": "energyuser", "password": "energypass"}
    )
    return response.json()["access_token"]

def test_predict_endpoint(test_token):
    # Test valid prediction request
    valid_data = {
        "capacity_kwh": 100.5,
        "current_soc": 50.0,
        "electricity_price": 0.15,
        "demand_forecast": 500.0,
        "renewable_input": 200.0
    }
    
    response = client.post(
        "/predict",
        json=valid_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert 0 <= data["optimal_soc"] <= 100
    assert data["cost_savings"] > 0
    assert isinstance(data["recommended_action"], str)

def test_invalid_prediction_request(test_token):
    # Test invalid input data
    invalid_data = {
        "capacity_kwh": -100,  # Invalid negative value
        "current_soc": 150,     # Invalid SOC > 100
        "electricity_price": 0,
        "demand_forecast": -50,
        "renewable_input": -10
    }
    
    response = client.post(
        "/predict",
        json=invalid_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("greater than 0" in err["msg"] for err in errors)

def test_quantum_trading_valid(test_token):
    # Test valid quantum trading request
    valid_trade = {
        "market": "Nordpool",
        "portfolio_size": 1000000.0,
        "risk_tolerance": 0.5,
        "time_horizon": 4
    }
    
    response = client.post(
        "/quantum",
        json=valid_trade,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert sum(data["optimal_allocation"].values()) == pytest.approx(1.0)
    assert data["expected_return"] > 0
    assert 0 <= data["risk_assessment"] <= 1

def test_quantum_invalid_market(test_token):
    # Test invalid market parameter
    invalid_trade = {
        "market": "InvalidMarket",
        "portfolio_size": 1000000.0,
        "risk_tolerance": 0.5
    }
    
    response = client.post(
        "/quantum",
        json=invalid_trade,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("market" in err["loc"] for err in errors)

def test_unauthorized_access():
    # Test endpoints without authentication
    response = client.post("/predict", json={})
    assert response.status_code == 401
    
    response = client.post("/quantum", json={})
    assert response.status_code == 401
