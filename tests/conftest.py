"""
Pytest configuration and fixtures for EnergyOpti-Pro.

This file contains shared fixtures and configuration for all tests.
"""

import pytest
import asyncio
from typing import Dict, Any, Generator
from unittest.mock import Mock, AsyncMock
import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from energyopti_pro.services.market_data_service import MarketDataService
from energyopti_pro.services.trading_service import TradingService
from energyopti_pro.services.risk_management_service import RiskManagementService
from energyopti_pro.services.compliance_service import ComplianceService, ComplianceRegion
from energyopti_pro.services.ai_ml_service import AIMLService


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_market_data():
    """Mock market data for testing."""
    return {
        "crude_oil": {
            "price": 75.50,
            "historical_prices": [74.00, 74.50, 75.00, 75.25, 75.50],
            "volume": 1000000,
            "exchange": "CME",
            "timestamp": "2024-01-15T10:00:00Z"
        },
        "natural_gas": {
            "price": 3.25,
            "historical_prices": [3.20, 3.22, 3.24, 3.23, 3.25],
            "volume": 500000,
            "exchange": "NYMEX",
            "timestamp": "2024-01-15T10:00:00Z"
        },
        "brent_crude": {
            "price": 78.25,
            "historical_prices": [77.50, 77.75, 78.00, 78.10, 78.25],
            "volume": 800000,
            "exchange": "ICE",
            "timestamp": "2024-01-15T10:00:00Z"
        }
    }


@pytest.fixture
def mock_user_profile():
    """Mock user profile for testing."""
    return {
        "user_id": "test_user_123",
        "username": "testuser",
        "email": "test@example.com",
        "islamic_finance_enabled": True,
        "risk_tolerance": 0.5,
        "enable_portfolio_optimization": True,
        "positions": [
            {
                "commodity": "crude_oil",
                "quantity": 1000,
                "current_price": 75.50,
                "weight": 0.4
            },
            {
                "commodity": "natural_gas",
                "quantity": 5000,
                "current_price": 3.25,
                "weight": 0.3
            },
            {
                "commodity": "brent_crude",
                "quantity": 800,
                "current_price": 78.25,
                "weight": 0.3
            }
        ]
    }


@pytest.fixture
def mock_transaction_data():
    """Mock transaction data for compliance testing."""
    return {
        "transaction_id": "tx_123",
        "commodity": "crude_oil",
        "quantity": 1000,
        "price": 75.50,
        "exchange": "CME",
        "user_id": "test_user_123",
        "timestamp": "2024-01-15T10:00:00Z",
        "adnoc_certification": True,
        "data_consent": True,
        "market_manipulation_risk": 0.3,
        "uncertainty_level": 0.2,
        "speculation_level": 0.4,
        "investment_type": "energy",
        "zakat_calculated": True
    }


@pytest.fixture
def mock_positions():
    """Mock trading positions for testing."""
    return [
        {
            "id": "pos_1",
            "user_id": "test_user_123",
            "commodity": "crude_oil",
            "exchange": "CME",
            "quantity": 1000,
            "current_price": 75.50,
            "weight": 0.4
        },
        {
            "id": "pos_2",
            "user_id": "test_user_123",
            "commodity": "natural_gas",
            "exchange": "NYMEX",
            "quantity": 5000,
            "current_price": 3.25,
            "weight": 0.3
        },
        {
            "id": "pos_3",
            "user_id": "test_user_123",
            "commodity": "brent_crude",
            "exchange": "ICE",
            "quantity": 800,
            "current_price": 78.25,
            "weight": 0.3
        }
    ]


@pytest.fixture
async def market_data_service():
    """Create a MarketDataService instance for testing."""
    service = MarketDataService()
    yield service
    await service.close()


@pytest.fixture
def trading_service():
    """Create a TradingService instance for testing."""
    return TradingService()


@pytest.fixture
def risk_management_service():
    """Create a RiskManagementService instance for testing."""
    return RiskManagementService()


@pytest.fixture
def compliance_service():
    """Create a ComplianceService instance for testing."""
    return ComplianceService()


@pytest.fixture
def ai_ml_service():
    """Create an AIMLService instance for testing."""
    return AIMLService()


@pytest.fixture
def mock_api_responses():
    """Mock API responses for external services."""
    return {
        "cme": {
            "status": 200,
            "data": {
                "last": 75.50,
                "bid": 75.45,
                "ask": 75.55,
                "volume": 1000000
            }
        },
        "ice": {
            "status": 200,
            "data": {
                "last": 78.25,
                "bid": 78.20,
                "ask": 78.30,
                "volume": 800000
            }
        },
        "nymex": {
            "status": 200,
            "data": {
                "last": 3.25,
                "bid": 3.24,
                "ask": 3.26,
                "volume": 500000
            }
        },
        "openweathermap": {
            "status": 200,
            "data": {
                "main": {
                    "temp": 25.0,
                    "humidity": 65
                },
                "weather": [
                    {"description": "Partly cloudy"}
                ]
            }
        }
    }


@pytest.fixture
def mock_stress_scenarios():
    """Mock stress test scenarios for risk management testing."""
    return [
        {
            "name": "market_crash",
            "price_shock": -0.20,
            "volatility_shock": 2.0
        },
        {
            "name": "moderate_decline",
            "price_shock": -0.10,
            "volatility_shock": 1.5
        },
        {
            "name": "volatility_spike",
            "price_shock": 0.0,
            "volatility_shock": 2.5
        }
    ]


@pytest.fixture
def mock_compliance_region():
    """Mock compliance region for testing."""
    return ComplianceRegion.MIDDLE_EAST


@pytest.fixture
def mock_environment_variables():
    """Mock environment variables for testing."""
    return {
        "CME_API_KEY": "test_cme_key",
        "ICE_API_KEY": "test_ice_key",
        "NYMEX_API_KEY": "test_nymex_key",
        "OPENWEATHER_API_KEY": "test_weather_key",
        "DATABASE_URL": "postgresql://test:test@localhost:5432/test_db",
        "REDIS_URL": "redis://localhost:6379/0",
        "JWT_SECRET_KEY": "test_jwt_secret_key",
        "ENVIRONMENT": "testing"
    }


@pytest.fixture(autouse=True)
def setup_test_environment(mock_environment_variables):
    """Set up test environment variables."""
    for key, value in mock_environment_variables.items():
        os.environ[key] = value
    
    yield
    
    # Clean up environment variables
    for key in mock_environment_variables.keys():
        if key in os.environ:
            del os.environ[key]


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    return Mock()


@pytest.fixture
def mock_http_session():
    """Mock HTTP session for testing."""
    session = AsyncMock()
    session.get = AsyncMock()
    session.post = AsyncMock()
    session.put = AsyncMock()
    session.delete = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def mock_database_connection():
    """Mock database connection for testing."""
    connection = Mock()
    connection.execute = Mock()
    connection.commit = Mock()
    connection.rollback = Mock()
    connection.close = Mock()
    return connection


@pytest.fixture
def mock_redis_client():
    """Mock Redis client for testing."""
    client = Mock()
    client.get = Mock()
    client.set = Mock()
    client.delete = Mock()
    client.exists = Mock()
    client.expire = Mock()
    return client


# Test markers
pytest_plugins = []


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )
    config.addinivalue_line(
        "markers", "api: marks tests as API tests"
    )
    config.addinivalue_line(
        "markers", "database: marks tests as database tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add unit test marker for test files
        if "test_" in item.nodeid and "test_" in item.nodeid.split("::")[0]:
            item.add_marker(pytest.mark.unit)
        
        # Add integration test marker for integration test files
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Add API test marker for API test files
        if "api" in item.nodeid:
            item.add_marker(pytest.mark.api)
        
        # Add database test marker for database test files
        if "database" in item.nodeid:
            item.add_marker(pytest.mark.database)
