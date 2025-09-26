"""
Unit tests for Risk Management endpoints
Tests the GET /v1/risk/var and /v1/risk/stress-test endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json

# Import the main app
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from main import app

client = TestClient(app)

class TestRiskEndpoints:
    """Test cases for risk management endpoints"""
    
    def test_get_var_calculation_success(self):
        """Test successful VaR calculation"""
        response = client.get("/api/v1/risk/var?portfolio_id=test_portfolio_001")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "portfolio_id" in data
        assert "confidence_level" in data
        assert "var_metrics" in data
        assert "portfolio_summary" in data
        assert "calculated_at" in data
        assert "method" in data
        
        # Check VaR metrics structure
        var_metrics = data["var_metrics"]
        assert "var_95" in var_metrics
        assert "var_99" in var_metrics
        assert "expected_shortfall_95" in var_metrics
        assert "expected_shortfall_99" in var_metrics
        assert "portfolio_risk_score" in var_metrics
        
        # Check portfolio summary structure
        portfolio_summary = data["portfolio_summary"]
        assert "total_value" in portfolio_summary
        assert "num_positions" in portfolio_summary
        assert "position_breakdown" in portfolio_summary
        
        # Validate data types
        assert isinstance(var_metrics["var_95"], (int, float))
        assert isinstance(var_metrics["var_99"], (int, float))
        assert isinstance(portfolio_summary["total_value"], (int, float))
        assert isinstance(portfolio_summary["num_positions"], int)
        
    def test_get_var_calculation_with_confidence(self):
        """Test VaR calculation with custom confidence level"""
        response = client.get("/api/v1/risk/var?portfolio_id=test_portfolio_002&confidence=0.99")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["confidence_level"] == 0.99
        assert "var_metrics" in data
        
    def test_get_var_calculation_with_stress_test(self):
        """Test VaR calculation with stress test included"""
        response = client.get("/api/v1/risk/var?portfolio_id=test_portfolio_003&include_stress_test=true")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "stress_test" in data
        stress_test = data["stress_test"]
        assert "stress_test_results" in stress_test
        assert "overall_stress_score" in stress_test
        
    def test_get_var_calculation_invalid_confidence(self):
        """Test VaR calculation with invalid confidence level"""
        response = client.get("/api/v1/risk/var?portfolio_id=test_portfolio_004&confidence=1.5")
        
        assert response.status_code == 422  # Validation error
        
    def test_get_var_calculation_missing_portfolio_id(self):
        """Test VaR calculation without portfolio ID"""
        response = client.get("/api/v1/risk/var")
        
        assert response.status_code == 422  # Validation error
        
    def test_get_stress_test_success(self):
        """Test successful stress testing"""
        response = client.get("/api/v1/risk/stress-test?portfolio_id=test_portfolio_005")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "portfolio_id" in data
        assert "scenarios_tested" in data
        assert "stress_test_results" in data
        assert "calculated_at" in data
        
        # Check scenarios
        assert isinstance(data["scenarios_tested"], list)
        assert len(data["scenarios_tested"]) > 0
        
        # Check stress test results structure
        stress_results = data["stress_test_results"]
        assert "stress_test_results" in stress_results
        assert "overall_stress_score" in stress_results
        
    def test_get_stress_test_with_custom_scenarios(self):
        """Test stress testing with custom scenarios"""
        scenarios = "market_crash,oil_price_shock,currency_crisis"
        response = client.get(f"/api/v1/risk/stress-test?portfolio_id=test_portfolio_006&scenarios={scenarios}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["scenarios_tested"] == ["market_crash", "oil_price_shock", "currency_crisis"]
        
    def test_get_stress_test_missing_portfolio_id(self):
        """Test stress testing without portfolio ID"""
        response = client.get("/api/v1/risk/stress-test")
        
        assert response.status_code == 422  # Validation error
        
    def test_var_calculation_error_handling(self):
        """Test VaR calculation error handling"""
        with patch('app.services.risk.calculate_portfolio_var') as mock_calculate:
            mock_calculate.side_effect = Exception("Calculation error")
            
            response = client.get("/api/v1/risk/var?portfolio_id=test_portfolio_007")
            
            assert response.status_code == 500
            data = response.json()
            assert "VaR calculation failed" in data["detail"]
            
    def test_stress_test_error_handling(self):
        """Test stress test error handling"""
        with patch('app.services.risk.stress_test_portfolio') as mock_stress:
            mock_stress.side_effect = Exception("Stress test error")
            
            response = client.get("/api/v1/risk/stress-test?portfolio_id=test_portfolio_008")
            
            assert response.status_code == 500
            data = response.json()
            assert "Stress test failed" in data["detail"]
            
    def test_var_calculation_response_structure(self):
        """Test detailed VaR calculation response structure"""
        response = client.get("/api/v1/risk/var?portfolio_id=test_portfolio_009")
        
        assert response.status_code == 200
        data = response.json()
        
        # Test var_metrics structure
        var_metrics = data["var_metrics"]
        required_var_fields = [
            "var_95", "var_99", "expected_shortfall_95", 
            "expected_shortfall_99", "portfolio_risk_score"
        ]
        
        for field in required_var_fields:
            assert field in var_metrics
            assert isinstance(var_metrics[field], (int, float))
        
        # Test portfolio_summary structure
        portfolio_summary = data["portfolio_summary"]
        required_summary_fields = ["total_value", "num_positions", "position_breakdown"]
        
        for field in required_summary_fields:
            assert field in portfolio_summary
            
        # Test position_breakdown structure
        position_breakdown = portfolio_summary["position_breakdown"]
        assert isinstance(position_breakdown, list)
        
        if position_breakdown:
            position = position_breakdown[0]
            required_position_fields = ["commodity", "value", "percentage"]
            
            for field in required_position_fields:
                assert field in position
                
    def test_stress_test_response_structure(self):
        """Test detailed stress test response structure"""
        response = client.get("/api/v1/risk/stress-test?portfolio_id=test_portfolio_010")
        
        assert response.status_code == 200
        data = response.json()
        
        # Test stress_test_results structure
        stress_results = data["stress_test_results"]
        assert "stress_test_results" in stress_results
        assert "overall_stress_score" in stress_results
        
        # Test individual scenario results
        scenario_results = stress_results["stress_test_results"]
        assert isinstance(scenario_results, dict)
        
        for scenario, result in scenario_results.items():
            if "error" not in result:
                required_fields = [
                    "scenario", "stress_factor", "original_value", 
                    "stressed_value", "loss_amount", "loss_percentage"
                ]
                
                for field in required_fields:
                    assert field in result
                    
    def test_var_calculation_with_ml_insights(self):
        """Test VaR calculation with ML insights"""
        response = client.get("/api/v1/risk/var?portfolio_id=test_portfolio_011")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check ML insights structure
        assert "ml_insights" in data
        ml_insights = data["ml_insights"]
        assert isinstance(ml_insights, dict)
        
        # ML insights should have availability flag
        if "ml_available" in ml_insights:
            assert isinstance(ml_insights["ml_available"], bool)
            
    def test_confidence_level_validation(self):
        """Test confidence level validation"""
        # Test valid confidence levels
        valid_confidences = [0.5, 0.95, 0.99, 0.9]
        
        for confidence in valid_confidences:
            response = client.get(f"/api/v1/risk/var?portfolio_id=test_portfolio_012&confidence={confidence}")
            assert response.status_code == 200
            
        # Test invalid confidence levels
        invalid_confidences = [0.4, 1.0, 1.1, -0.1]
        
        for confidence in invalid_confidences:
            response = client.get(f"/api/v1/risk/var?portfolio_id=test_portfolio_013&confidence={confidence}")
            assert response.status_code == 422

if __name__ == "__main__":
    pytest.main([__file__])
