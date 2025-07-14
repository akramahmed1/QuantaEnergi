"""Comprehensive test suite for EnergyOpti-Pro API endpoints."""
import pytest
from fastapi.testclient import TestClient
from main import app
from pyjwt import encode
import json

client = TestClient(app)

@pytest.fixture
def valid_token():
    """Generate a mock valid token for authentication."""
    return encode({"sub": "testuser", "exp": 253402300799}, "secret", algorithm="HS256")

def test_predict_valid_input(valid_token):
    response = client.post("/predict", json={"capacity_kwh": 100, "current_soc": 0.5, "electricity_price": 50, "frequency_need": 0.7}, headers={"Authorization": f"Bearer {valid_token}"})
    assert response.status_code == 200
    data = response.json()
    assert "optimal_soc" in data
    assert "recommended_action" in data

def test_predict_invalid_input(valid_token):
    response = client.post("/predict", json={"capacity_kwh": -100, "current_soc": 0.5, "electricity_price": 50, "frequency_need": 0.7}, headers={"Authorization": f"Bearer {valid_token}"})
    assert response.status_code == 400

def test_quantum_valid_input(valid_token):
    response = client.post("/quantum", json={"market": "oil", "portfolio_size": 1000}, headers={"Authorization": f"Bearer {valid_token}"})
    assert response.status_code == 200
    data = response.json()
    assert "optimal_allocation" in data

def test_forecast_valid_input(valid_token):
    response = client.post("/forecast", json={"location": "US", "date_range": ["2025-07-12", "2025-07-13"]}, headers={"Authorization": f"Bearer {valid_token}"})
    assert response.status_code == 200
    data = response.json()
    assert "hourly_price_forecast" in data

def test_carbon_valid_input(valid_token):
    response = client.post("/carbon", json={"facility_id": "F1", "fuel_types": ["natural gas"]}, headers={"Authorization": f"Bearer {valid_token}"})
    assert response.status_code == 200
    data = response.json()
    assert "carbon_intensity" in data

def test_iot_valid_input(valid_token):
    response = client.post("/iot", json={"grid_id": "G1", "battery_capacities": [100, 200]}, headers={"Authorization": f"Bearer {valid_token}"})
    assert response.status_code == 200
    data = response.json()
    assert "vpp_capacity" in data

def test_metrics_valid_input(valid_token):
    response = client.get("/metrics", headers={"Authorization": f"Bearer {valid_token}"})
    assert response.status_code == 200
    data = response.json()
    assert "pipeline_logs" in data

def test_logs_valid_input(valid_token):
    response = client.get("/logs", headers={"Authorization": f"Bearer {valid_token}"})
    assert response.status_code == 200
    data = response.json()
    assert "logs" in data

def test_token_valid_input():
    response = client.post("/token", data=json.dumps({"username": "testuser", "password": "testpass"}), headers={"Content-Type": "application/json"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_token_invalid_input():
    response = client.post("/token", data=json.dumps({"username": "testuser", "password": "wrong"}), headers={"Content-Type": "application/json"})
    assert response.status_code == 401

def test_webhook_valid_input(valid_token):
    response = client.post("/webhook", json={"event": "test"}, headers={"Authorization": f"Bearer {valid_token}"})
    assert response.status_code == 200
    assert response.json() == {"status": "received"}