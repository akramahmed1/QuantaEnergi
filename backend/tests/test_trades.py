import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

# Mock the database connection during import
with patch('app.db.session.engine'):
    from app.main import app

client = TestClient(app)

def test_health_endpoint():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_login_endpoint():
    """Test login endpoint"""
    # Valid credentials
    response = client.post("/auth/login", json={"username": "admin", "password": "password"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()
    
    # Invalid credentials
    response = client.post("/auth/login", json={"username": "wrong", "password": "wrong"})
    assert response.status_code == 200
    assert "error" in response.json()

def test_create_trade_without_auth():
    """Test creating a trade without authentication (should fail)"""
    response = client.post("/trades", json={"asset": "oil", "quantity": 100, "price": 80})
    assert response.status_code == 200  # FastAPI returns 200 with error message
    assert "error" in response.json()

def test_create_trade_with_auth():
    """Test creating a trade with valid authentication"""
    # First, get a JWT token
    login_response = client.post("/auth/login", json={"username": "admin", "password": "password"})
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # Then create a trade with the token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/trades", json={"asset": "oil", "quantity": 100, "price": 80}, headers=headers)
    assert response.status_code == 200
    assert "id" in response.json()
    assert "trade" in response.json()
    assert "user" in response.json()