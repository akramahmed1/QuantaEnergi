"""
Comprehensive End-to-End Testing for QuantaEnergi
Covers authentication, API endpoints, security, and data flow.
"""

import pytest
import time
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.backend.main import app
from src.backend.db.session import get_db, create_tables
from src.backend.models.base import Base

TEST_DATABASE_URL = "sqlite:///./test_energyopti_pro.db"
TEST_USER_EMAIL = f"test_{int(time.time())}@energyopti-pro.com"
TEST_USER_PASSWORD = "TestPassword123!"
TEST_USER_ROLE = "trader"

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment with test database."""
    engine = create_engine(TEST_DATABASE_URL)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Patch the database dependency to use test database
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app, headers={"Host": "localhost"})
    yield client

    app.dependency_overrides.clear()
    engine.dispose()
    import os
    if os.path.exists("./test_energyopti_pro.db"):
        os.remove("./test_energyopti_pro.db")

def test_health_check_endpoint(setup_test_environment):
    client = setup_test_environment
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data and data["status"] == "healthy"

def test_authentication_workflow(setup_test_environment):
    client = setup_test_environment
    # Create user
    create_response = client.post(
        "/api/auth/register",
        json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "role": TEST_USER_ROLE,
            "company_name": "Test Energy Corp"
        }
    )
    assert create_response.status_code == 201
    user_data = create_response.json()
    assert "user_id" in user_data
    assert "password" not in user_data

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
    )
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "access_token" in login_data
    assert login_data["token_type"] == "bearer"
    token = login_data["access_token"]
    assert len(token) > 50
    assert token.count('.') == 2
