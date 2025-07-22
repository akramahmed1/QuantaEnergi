import pytest
from httpx import AsyncClient
from main import app
from app.core.security import create_access_token
from datetime import timedelta

@pytest.fixture(scope="module")
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture(scope="module")
async def authenticated_client(async_client: AsyncClient):
    token = create_access_token({"sub": "trader_ahmed@eop"}, timedelta(minutes=30))
    async_client.headers["Authorization"] = f"Bearer {token}"
    return async_client

@pytest.mark.asyncio
async def test_quantum_simulation_e2e(authenticated_client: AsyncClient):
    response = await authenticated_client.post(
        "/api/v1/quantum/simulate",
        json={"market_data": {"brent_price": 90.5}, "strategy": "aggressive"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

@pytest.mark.asyncio
async def test_esg_footprint_e2e(authenticated_client: AsyncClient):
    response = await authenticated_client.post(
        "/api/v1/esg/footprint",
        json={"energy_consumption_kwh": 1000, "country_code": "US"}
    )
    assert response.status_code == 200
    assert response.json()["carbon_emissions_kgCO2e"] == 430.0

# Add more tests for other endpoints