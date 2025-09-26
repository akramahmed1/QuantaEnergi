"""
Unit tests for Trade Capture endpoint
Tests the POST /v1/trade/capture endpoint functionality
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import json

# Import the main app
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from main import app

client = TestClient(app)

class TestTradeCapture:
    """Test cases for trade capture endpoint"""
    
    def test_capture_oil_trade_success(self):
        """Test successful oil trade capture"""
        trade_data = {
            "asset": "oil",
            "volume": 1000.0,
            "price": 85.50,
            "region": "me",
            "amendments": None
        }
        
        response = client.post("/api/v1/trade/capture", json=trade_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "trade_id" in data
        assert data["status"] in ["captured", "pending_review"]
        assert "message" in data
        assert "timestamp" in data
        assert "forecast_validation" in data
        
        # Validate trade ID format
        assert data["trade_id"].startswith("T")
        assert len(data["trade_id"]) == 17  # T + 14 digits + 4 random
        
    def test_capture_gas_trade_success(self):
        """Test successful gas trade capture"""
        trade_data = {
            "asset": "gas",
            "volume": 500.0,
            "price": 3.25,
            "region": "us",
            "amendments": [{"type": "quality_adjustment", "value": 0.02}]
        }
        
        response = client.post("/api/v1/trade/capture", json=trade_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] in ["captured", "pending_review"]
        assert "forecast_validation" in data
        
    def test_capture_trade_invalid_asset(self):
        """Test trade capture with invalid asset"""
        trade_data = {
            "asset": "invalid_asset",
            "volume": 1000.0,
            "price": 85.50,
            "region": "me"
        }
        
        response = client.post("/api/v1/trade/capture", json=trade_data)
        
        assert response.status_code == 422  # Validation error
        
    def test_capture_trade_invalid_region(self):
        """Test trade capture with invalid region"""
        trade_data = {
            "asset": "oil",
            "volume": 1000.0,
            "price": 85.50,
            "region": "invalid_region"
        }
        
        response = client.post("/api/v1/trade/capture", json=trade_data)
        
        assert response.status_code == 422  # Validation error
        
    def test_capture_trade_negative_volume(self):
        """Test trade capture with negative volume"""
        trade_data = {
            "asset": "oil",
            "volume": -1000.0,
            "price": 85.50,
            "region": "me"
        }
        
        response = client.post("/api/v1/trade/capture", json=trade_data)
        
        assert response.status_code == 422  # Validation error
        
    def test_capture_trade_negative_price(self):
        """Test trade capture with negative price"""
        trade_data = {
            "asset": "oil",
            "volume": 1000.0,
            "price": -85.50,
            "region": "me"
        }
        
        response = client.post("/api/v1/trade/capture", json=trade_data)
        
        assert response.status_code == 422  # Validation error
        
    def test_capture_trade_missing_required_fields(self):
        """Test trade capture with missing required fields"""
        trade_data = {
            "asset": "oil",
            "volume": 1000.0
            # Missing price and region
        }
        
        response = client.post("/api/v1/trade/capture", json=trade_data)
        
        assert response.status_code == 422  # Validation error
        
    def test_capture_trade_with_amendments(self):
        """Test trade capture with amendments"""
        trade_data = {
            "asset": "oil",
            "volume": 1000.0,
            "price": 85.50,
            "region": "guyana",
            "amendments": [
                {"type": "quality_adjustment", "value": 0.05},
                {"type": "transport_cost", "value": 2.50}
            ]
        }
        
        response = client.post("/api/v1/trade/capture", json=trade_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] in ["captured", "pending_review"]
        assert "forecast_validation" in data
        
    def test_capture_trade_all_regions(self):
        """Test trade capture for all supported regions"""
        regions = ["me", "guyana", "us", "uk", "eu"]
        
        for region in regions:
            trade_data = {
                "asset": "oil",
                "volume": 100.0,
                "price": 80.0,
                "region": region
            }
            
            response = client.post("/api/v1/trade/capture", json=trade_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] in ["captured", "pending_review"]
            
    def test_forecast_validation_structure(self):
        """Test that forecast validation returns expected structure"""
        trade_data = {
            "asset": "oil",
            "volume": 1000.0,
            "price": 85.50,
            "region": "me"
        }
        
        response = client.post("/api/v1/trade/capture", json=trade_data)
        
        assert response.status_code == 200
        data = response.json()
        
        forecast_validation = data["forecast_validation"]
        assert "forecast_price" in forecast_validation
        assert "trade_price" in forecast_validation
        assert "deviation_percent" in forecast_validation
        assert "is_valid" in forecast_validation
        assert "confidence" in forecast_validation
        assert "forecast_data" in forecast_validation
        
        # Validate data types
        assert isinstance(forecast_validation["forecast_price"], (int, float))
        assert isinstance(forecast_validation["trade_price"], (int, float))
        assert isinstance(forecast_validation["deviation_percent"], (int, float))
        assert isinstance(forecast_validation["is_valid"], bool)
        assert isinstance(forecast_validation["confidence"], (int, float))
        assert isinstance(forecast_validation["forecast_data"], list)

if __name__ == "__main__":
    pytest.main([__file__])
