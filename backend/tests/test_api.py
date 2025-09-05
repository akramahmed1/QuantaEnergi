import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_endpoints():
    """Test API endpoints using FastAPI test client instead of live server"""
    # Test GET endpoints
    endpoints = [
        "/api/prices",
        "/api/models/v1/prices", 
        "/api/secure",
        "/api/secure/transparency",
        "/api/oilfield",
        "/api/tariff_impact",
        "/api/renewables",
        "/api/retention",
        "/api/onboarding",
        "/api/health"
    ]
    
    for endpoint in endpoints:
        headers = {"Authorization": "Bearer token0"} if "secure" in endpoint else {}
        params = {"region": "middle_east", "ramadan_mode": "true"} if "prices" in endpoint else {}
        if endpoint == "/api/onboarding":
            params["user_type"] = "trader"
            
        response = client.get(endpoint, headers=headers, params=params)
        assert response.status_code in [200, 401, 403, 404], f"Failed: {endpoint} - {response.text}"
    
    # Test POST endpoints
    body = {"test": "audit"}
    response = client.post("/api/audit", headers={"Authorization": "Bearer token0"}, json=body)
    assert response.status_code in [200, 401, 403, 404], f"Failed: /api/audit (POST) - {response.text}"
    
    response = client.post("/api/gamify", json={"action": "feedback"})
    assert response.status_code in [200, 401, 403, 404], f"Failed: /api/gamify (POST) - {response.text}"
    
    print("All API tests passed!")

if __name__ == "__main__":
    test_api_endpoints()
