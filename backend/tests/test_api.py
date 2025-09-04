import requests

def test_api_endpoints():
    urls = [
        "http://localhost:8000/api/prices",
        "http://localhost:8000/api/models/v1/prices",
        "http://localhost:8000/api/secure",
        "http://localhost:8000/api/secure/transparency",
        "http://localhost:8000/api/oilfield",
        "http://localhost:8000/api/tariff_impact",
        "http://localhost:8000/api/renewables",
        "http://localhost:8000/api/retention",
        "http://localhost:8000/api/onboarding?user_type=trader",
        "http://localhost:8000/api/health"
    ]
    for url in urls:
        method = "GET"
        headers = {"Authorization": "Bearer token0"} if "secure" in url else {}
        response = requests.request(method, url, headers=headers, params={"region": "middle_east", "ramadan_mode": "true"} if "prices" in url else {})
        assert response.status_code in [200, 401, 403], f"Failed: {url} ({method}) - {response.text}"
    # Test POST endpoints
    body = {"test": "audit"}
    response = requests.post("http://localhost:8000/api/audit", headers={"Authorization": "Bearer token0"}, json=body)
    assert response.status_code == 200, f"Failed: /api/audit (POST) - {response.text}"
    response = requests.post("http://localhost:8000/api/gamify", json={"action": "feedback"})
    assert response.status_code == 200, f"Failed: /api/gamify (POST) - {response.text}"
    print("All API tests passed!")

if __name__ == "__main__":
    test_api_endpoints()
