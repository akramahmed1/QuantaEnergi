"""
Comprehensive tests for all new API endpoints
Tests trade lifecycle, credit management, regulatory compliance, and risk analytics APIs
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
from datetime import datetime, timedelta

from app.main import app

client = TestClient(app)

# Mock data for testing
SAMPLE_TRADE_DATA = {
    "trade_type": "forward",
    "commodity": "crude_oil",
    "quantity": 1000.0,
    "price": 85.50,
    "currency": "USD",
    "counterparty": "CP001",
    "delivery_date": (datetime.now() + timedelta(days=30)).isoformat(),
    "delivery_location": "Houston, TX",
    "additional_terms": {
        "quality_specs": "Brent Crude",
        "incoterms": "FOB"
    }
}

SAMPLE_CREDIT_LIMIT = {
    "counterparty_id": "CP001",
    "limit_amount": 1000000.0,
    "currency": "USD",
    "risk_rating": "A",
    "expiry_date": (datetime.now() + timedelta(days=365)).isoformat(),
    "terms": {"collateral_required": True}
}

SAMPLE_PORTFOLIO_DATA = {
    "portfolio_id": "portfolio_001",
    "total_value": 1000000.0,
    "volatility": 0.15,
    "positions": [
        {"commodity": "crude_oil", "quantity": 1000, "price": 85.50},
        {"commodity": "natural_gas", "quantity": 500, "price": 3.20}
    ]
}

SAMPLE_STRESS_SCENARIOS = [
    {
        "name": "Oil Price Crash",
        "type": "market_shock",
        "shock_factor": 0.3
    },
    {
        "name": "Volatility Spike",
        "type": "volatility_spike",
        "spike_factor": 2.5
    }
]

class TestTradeLifecycleAPI:
    """Test trade lifecycle API endpoints"""
    
    @patch('app.api.v1.trade_lifecycle.get_current_user')
    def test_capture_trade(self, mock_get_user):
        """Test trade capture endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "trader@quantaenergi.com", "role": "trader"}
        
        response = client.post("/api/v1/trade-lifecycle/capture", json=SAMPLE_TRADE_DATA)
        
        assert response.status_code == 200
        data = response.json()
        assert "trade_id" in data
        assert data["status"] == "captured"
    
    @patch('app.api.v1.trade_lifecycle.get_current_user')
    def test_validate_trade(self, mock_get_user):
        """Test trade validation endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "trader@quantaenergi.com", "role": "trader"}
        
        # First create a trade
        create_response = client.post("/api/v1/trade-lifecycle/capture", json=SAMPLE_TRADE_DATA)
        assert create_response.status_code == 200
        trade_data = create_response.json()
        trade_id = trade_data["trade_id"]
        
        # Now validate the trade
        response = client.post(f"/api/v1/trade-lifecycle/{trade_id}/validate")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    @patch('app.api.v1.trade_lifecycle.get_current_user')
    def test_generate_confirmation(self, mock_get_user):
        """Test trade confirmation endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "trader@quantaenergi.com", "role": "trader"}
        
        # First create a trade
        create_response = client.post("/api/v1/trade-lifecycle/capture", json=SAMPLE_TRADE_DATA)
        assert create_response.status_code == 200
        trade_data = create_response.json()
        trade_id = trade_data["trade_id"]
        
        # Now generate confirmation
        response = client.post(f"/api/v1/trade-lifecycle/{trade_id}/confirm")
        
        assert response.status_code == 200
        data = response.json()
        assert "confirmation_id" in data
    
    @patch('app.api.v1.trade_lifecycle.get_current_user')
    def test_allocate_trade(self, mock_get_user):
        """Test trade allocation endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "trader@quantaenergi.com", "role": "trader"}
        
        # First create a trade
        create_response = client.post("/api/v1/trade-lifecycle/capture", json=SAMPLE_TRADE_DATA)
        assert create_response.status_code == 200
        trade_data = create_response.json()
        trade_id = trade_data["trade_id"]
        
        allocation_data = {"account": "ACC001", "portfolio": "PORT001"}
        response = client.post(f"/api/v1/trade-lifecycle/{trade_id}/allocate", json=allocation_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "allocation_id" in data
    
    @patch('app.api.v1.trade_lifecycle.get_current_user')
    def test_process_settlement(self, mock_get_user):
        """Test trade settlement endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "trader@quantaenergi.com", "role": "trader"}
        
        # First create a trade
        create_response = client.post("/api/v1/trade-lifecycle/capture", json=SAMPLE_TRADE_DATA)
        assert create_response.status_code == 200
        trade_data = create_response.json()
        trade_id = trade_data["trade_id"]
        
        settlement_data = {"settlement_method": "wire_transfer", "bank_details": "BANK001"}
        response = client.post(f"/api/v1/trade-lifecycle/{trade_id}/settle", json=settlement_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "settlement_id" in data
    
    @patch('app.api.v1.trade_lifecycle.get_current_user')
    def test_generate_invoice(self, mock_get_user):
        """Test invoice generation endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "trader@quantaenergi.com", "role": "trader"}
        
        # First create a trade
        create_response = client.post("/api/v1/trade-lifecycle/capture", json=SAMPLE_TRADE_DATA)
        assert create_response.status_code == 200
        trade_data = create_response.json()
        trade_id = trade_data["trade_id"]
        
        response = client.post(f"/api/v1/trade-lifecycle/{trade_id}/invoice")
        
        assert response.status_code == 200
        data = response.json()
        assert "invoice_id" in data
    
    @patch('app.api.v1.trade_lifecycle.get_current_user')
    def test_process_payment(self, mock_get_user):
        """Test payment processing endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "trader@quantaenergi.com", "role": "trader"}
        
        # First create a trade
        create_response = client.post("/api/v1/trade-lifecycle/capture", json=SAMPLE_TRADE_DATA)
        assert create_response.status_code == 200
        trade_data = create_response.json()
        trade_id = trade_data["trade_id"]
        
        payment_data = {"payment_method": "credit_card", "card_number": "****1234"}
        response = client.post(f"/api/v1/trade-lifecycle/{trade_id}/payment", json=payment_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "payment_id" in data
    
    @patch('app.api.v1.trade_lifecycle.get_current_user')
    def test_get_trade_status(self, mock_get_user):
        """Test trade status retrieval endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "trader@quantaenergi.com", "role": "trader"}
        
        # First create a trade
        create_response = client.post("/api/v1/trade-lifecycle/capture", json=SAMPLE_TRADE_DATA)
        assert create_response.status_code == 200
        trade_data = create_response.json()
        trade_id = trade_data["trade_id"]
        
        response = client.get(f"/api/v1/trade-lifecycle/{trade_id}/status")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    @patch('app.api.v1.trade_lifecycle.get_current_user')
    def test_get_user_trades(self, mock_get_user):
        """Test user trades retrieval endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "trader@quantaenergi.com", "role": "trader"}
        
        response = client.get("/api/v1/trade-lifecycle/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @patch('app.api.v1.trade_lifecycle.get_current_user')
    def test_cancel_trade(self, mock_get_user):
        """Test trade cancellation endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "trader@quantaenergi.com", "role": "trader"}
        
        # First create a trade
        create_response = client.post("/api/v1/trade-lifecycle/capture", json=SAMPLE_TRADE_DATA)
        assert create_response.status_code == 200
        trade_data = create_response.json()
        trade_id = trade_data["trade_id"]
        
        response = client.delete(f"/api/v1/trade-lifecycle/{trade_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

class TestCreditManagementAPI:
    """Test credit management API endpoints"""
    
    @patch('app.api.v1.credit_management.get_current_user')
    def test_set_credit_limit(self, mock_get_user):
        """Test credit limit setting endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "trader@quantaenergi.com", "role": "trader"}
        
        response = client.post("/api/v1/credit/limits", json=SAMPLE_CREDIT_LIMIT)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data
    
    @patch('app.api.v1.credit_management.get_current_user')
    def test_get_credit_limit(self, mock_get_user):
        """Test credit limit retrieval endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "trader@quantaenergi.com", "role": "trader"}
        
        response = client.get("/api/v1/credit/limits/CP001")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    @patch('app.api.v1.credit_management.get_current_user')
    def test_get_all_credit_limits(self, mock_get_user):
        """Test all credit limits retrieval endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "trader@quantaenergi.com", "role": "trader"}
        
        response = client.get("/api/v1/credit/limits")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
    
    @patch('app.api.v1.credit_management.get_current_user')
    def test_calculate_exposure(self, mock_get_user):
        """Test exposure calculation endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "trader@quantaenergi.com", "role": "trader"}
        
        positions = [{"commodity": "crude_oil", "quantity": 1000, "price": 85.50}]
        response = client.post("/api/v1/credit/exposure/calculate", 
                             params={"counterparty_id": "CP001"}, 
                             json=positions)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    @patch('app.api.v1.credit_management.get_current_user')
    def test_get_exposure(self, mock_get_user):
        """Test exposure retrieval endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "trader@quantaenergi.com", "role": "trader"}
        
        response = client.get("/api/v1/credit/exposure/CP001")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    @patch('app.api.v1.credit_management.get_current_user')
    def test_check_credit_availability(self, mock_get_user):
        """Test credit availability check endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "trader@quantaenergi.com", "role": "trader"}
        
        response = client.post("/api/v1/credit/availability/check", 
                             params={"counterparty_id": "CP001", "trade_amount": 100000.0})
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    @patch('app.api.v1.credit_management.get_current_user')
    def test_get_credit_availability(self, mock_get_user):
        """Test credit availability retrieval endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "trader@quantaenergi.com", "role": "trader"}
        
        response = client.get("/api/v1/credit/availability/CP001")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    @patch('app.api.v1.credit_management.get_current_user')
    def test_generate_credit_report(self, mock_get_user):
        """Test credit report generation endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "trader@quantaenergi.com", "role": "trader"}
        
        response = client.post("/api/v1/credit/reports/generate")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    @patch('app.api.v1.credit_management.get_current_user')
    def test_get_credit_dashboard(self, mock_get_user):
        """Test credit dashboard endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "trader@quantaenergi.com", "role": "trader"}
        
        response = client.get("/api/v1/credit/dashboard")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "total_counterparties" in data["data"]

class TestRegulatoryComplianceAPI:
    """Test regulatory compliance API endpoints"""
    
    @patch('app.api.v1.regulatory_compliance.get_current_user')
    def test_generate_compliance_report(self, mock_get_user):
        """Test compliance report generation endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "compliance@quantaenergi.com", "role": "compliance_officer"}
        
        response = client.post("/api/v1/compliance/reports/generate", 
                             params={"region": "us", "regulation_type": "CFTC"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data
    
    @patch('app.api.v1.regulatory_compliance.get_current_user')
    def test_generate_bulk_compliance_reports(self, mock_get_user):
        """Test bulk compliance report generation endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "compliance@quantaenergi.com", "role": "compliance_officer"}
        
        response = client.post("/api/v1/compliance/reports/bulk", 
                             params={"regions": ["us", "uk"]})
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data
    
    @patch('app.api.v1.regulatory_compliance.get_current_user')
    def test_anonymize_compliance_data(self, mock_get_user):
        """Test data anonymization endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "compliance@quantaenergi.com", "role": "compliance_officer"}
        
        test_data = {"user_id": "123", "trade_amount": 100000, "counterparty": "CP001"}
        response = client.post("/api/v1/compliance/data/anonymize", json=test_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    @patch('app.api.v1.regulatory_compliance.get_current_user')
    def test_get_compliance_regions(self, mock_get_user):
        """Test compliance regions endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "compliance@quantaenergi.com", "role": "compliance_officer"}
        
        response = client.get("/api/v1/compliance/regions")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "us" in data["data"]
        assert "europe" in data["data"]
    
    @patch('app.api.v1.regulatory_compliance.get_current_user')
    def test_get_compliance_status(self, mock_get_user):
        """Test compliance status endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "compliance@quantaenergi.com", "role": "compliance_officer"}
        
        response = client.get("/api/v1/compliance/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "us" in data["data"]
    
    @patch('app.api.v1.regulatory_compliance.get_current_user')
    def test_get_compliance_dashboard(self, mock_get_user):
        """Test compliance dashboard endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "compliance@quantaenergi.com", "role": "compliance_officer"}
        
        response = client.get("/api/v1/compliance/dashboard")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "total_regions" in data["data"]
    
    @patch('app.api.v1.regulatory_compliance.get_current_user')
    def test_validate_compliance_requirements(self, mock_get_user):
        """Test compliance validation endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "compliance@quantaenergi.com", "role": "compliance_officer"}
        
        response = client.post("/api/v1/compliance/validation/check", 
                             params={"region": "us", "regulation_type": "CFTC"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "compliant" in data["data"]
    
    @patch('app.api.v1.regulatory_compliance.get_current_user')
    def test_get_compliance_history(self, mock_get_user):
        """Test compliance history endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "compliance@quantaenergi.com", "role": "compliance_officer"}
        
        response = client.get("/api/v1/compliance/history")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)

class TestRiskAnalyticsAPI:
    """Test risk analytics API endpoints"""
    
    @patch('app.api.v1.risk_analytics.get_current_user')
    def test_calculate_var_monte_carlo(self, mock_get_user):
        """Test Monte Carlo VaR calculation endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "risk@quantaenergi.com", "role": "risk_analyst"}
        
        response = client.post("/api/v1/risk-analytics/var/monte-carlo", 
                             json=SAMPLE_PORTFOLIO_DATA,
                             params={"confidence_level": 0.95, "time_horizon": 1, "num_simulations": 10000})
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data
    
    @patch('app.api.v1.risk_analytics.get_current_user')
    def test_calculate_var_parametric(self, mock_get_user):
        """Test parametric VaR calculation endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "risk@quantaenergi.com", "role": "risk_analyst"}
        
        response = client.post("/api/v1/risk-analytics/var/parametric", 
                             json=SAMPLE_PORTFOLIO_DATA,
                             params={"confidence_level": 0.95, "time_horizon": 1})
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "var_value" in data["data"]
    
    @patch('app.api.v1.risk_analytics.get_current_user')
    def test_calculate_var_historical(self, mock_get_user):
        """Test historical VaR calculation endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "risk@quantaenergi.com", "role": "risk_analyst"}
        
        portfolio_with_returns = SAMPLE_PORTFOLIO_DATA.copy()
        portfolio_with_returns["historical_returns"] = [0.01, -0.02, 0.015, -0.01, 0.02]
        
        response = client.post("/api/v1/risk-analytics/var/historical", 
                             json=portfolio_with_returns,
                             params={"confidence_level": 0.95, "time_horizon": 1, "historical_period": 252})
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "var_value" in data["data"]
    
    @patch('app.api.v1.risk_analytics.get_current_user')
    def test_stress_test_portfolio(self, mock_get_user):
        """Test portfolio stress testing endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "risk@quantaenergi.com", "role": "risk_analyst"}
        
        response = client.post("/api/v1/risk-analytics/stress-test", 
                             json={"portfolio_data": SAMPLE_PORTFOLIO_DATA, "stress_scenarios": SAMPLE_STRESS_SCENARIOS})
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data
    
    @patch('app.api.v1.risk_analytics.get_current_user')
    def test_calculate_expected_shortfall(self, mock_get_user):
        """Test expected shortfall calculation endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "risk@quantaenergi.com", "role": "risk_analyst"}
        
        response = client.post("/api/v1/risk-analytics/expected-shortfall", 
                             json=SAMPLE_PORTFOLIO_DATA,
                             params={"confidence_level": 0.95, "time_horizon": 1})
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data
    
    @patch('app.api.v1.risk_analytics.get_current_user')
    def test_perform_scenario_analysis(self, mock_get_user):
        """Test scenario analysis endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "risk@quantaenergi.com", "role": "risk_analyst"}
        
        response = client.post("/api/v1/risk-analytics/scenario-analysis", 
                             json={"portfolio_data": SAMPLE_PORTFOLIO_DATA, "scenarios": SAMPLE_STRESS_SCENARIOS})
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "scenarios_analyzed" in data["data"]
    
    @patch('app.api.v1.risk_analytics.get_current_user')
    def test_generate_risk_report(self, mock_get_user):
        """Test risk report generation endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "risk@quantaenergi.com", "role": "risk_analyst"}
        
        response = client.post("/api/v1/risk-analytics/risk-report", 
                             json=SAMPLE_PORTFOLIO_DATA,
                             params={"report_type": "comprehensive", "include_scenarios": True})
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data
    
    @patch('app.api.v1.risk_analytics.get_current_user')
    def test_get_risk_metrics(self, mock_get_user):
        """Test risk metrics retrieval endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "risk@quantaenergi.com", "role": "risk_analyst"}
        
        response = client.get("/api/v1/risk-analytics/risk-metrics")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "var_95" in data["data"]
    
    @patch('app.api.v1.risk_analytics.get_current_user')
    def test_get_risk_dashboard(self, mock_get_user):
        """Test risk dashboard endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "risk@quantaenergi.com", "role": "risk_analyst"}
        
        response = client.get("/api/v1/risk-analytics/dashboard")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "total_portfolios" in data["data"]
    
    @patch('app.api.v1.risk_analytics.get_current_user')
    def test_run_monte_carlo_simulation(self, mock_get_user):
        """Test Monte Carlo simulation endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "risk@quantaenergi.com", "role": "risk_analyst"}
        
        simulation_params = {
            "positions": [
                {"commodity": "crude_oil", "notional_value": 100000, "expected_return": 0.05, "volatility": 0.2},
                {"commodity": "natural_gas", "notional_value": 50000, "expected_return": 0.03, "volatility": 0.15}
            ],
            "market_data": {},
            "correlations": {},
            "num_simulations": 10000, 
            "time_horizon": 1
        }
        response = client.post("/api/v1/risk-analytics/simulation/monte-carlo", json=simulation_params)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "simulation_id" in data["data"]
    
    @patch('app.api.v1.risk_analytics.get_current_user')
    def test_get_simulation_status(self, mock_get_user):
        """Test simulation status endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "risk@quantaenergi.com", "role": "risk_analyst"}
        
        response = client.get("/api/v1/risk-analytics/simulation/mc_sim_20240115_100000/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "status" in data["data"]
    
    @patch('app.api.v1.risk_analytics.get_current_user')
    def test_get_simulation_results(self, mock_get_user):
        """Test simulation results endpoint"""
        mock_get_user.return_value = {"id": "user123", "email": "risk@quantaenergi.com", "role": "risk_analyst"}
        
        response = client.get("/api/v1/risk-analytics/simulation/mc_sim_20240115_100000/results")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "var_95" in data["data"]

class TestAlgorithmicTradingAPI:
    """Test algorithmic trading API endpoints"""
    
    def test_execute_algorithm(self):
        """Test algorithm execution endpoint"""
        algo_spec = {
            "strategy_name": "TWAP Strategy",
            "strategy_type": "twap",
            "parameters": {
                "total_quantity": 1000000.0,
                "duration_minutes": 60,
                "slice_interval": 5,
                "commodity": "crude_oil",
                "execution_type": "buy"
            },
            "risk_limits": {
                "max_order_size": 1000000.0,
                "max_daily_volume": 10000000.0,
                "max_slippage": 0.02
            },
            "islamic_compliant": True,
            "execution_mode": "passive"
        }
        
        response = client.post("/api/v1/options/algo/execute", json=algo_spec)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "execution_id" in data["data"]
        assert data["data"]["strategy"] == "twap"
    
    def test_calculate_vwap(self):
        """Test VWAP calculation endpoint"""
        orders = [
            {"price": 85.50, "volume": 100000},
            {"price": 85.60, "volume": 150000},
            {"price": 85.45, "volume": 200000}
        ]
        
        response = client.post("/api/v1/options/algo/vwap", 
                             json=orders,
                             params={"time_period": "1D"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "vwap" in data["data"]
        assert "total_volume" in data["data"]
    
    def test_execute_twap_strategy(self):
        """Test TWAP strategy execution endpoint"""
        twap_params = {
            "total_quantity": 1000000.0,
            "duration_minutes": 60,
            "slice_interval": 5,
            "commodity": "crude_oil",
            "execution_type": "buy"
        }
        
        response = client.post("/api/v1/options/algo/twap", json=twap_params)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "strategy_id" in data["data"]
        assert data["data"]["strategy_type"] == "TWAP"
        assert "execution_slices" in data["data"]
    
    def test_optimize_order_sizing(self):
        """Test order sizing optimization endpoint"""
        market_data = {"volatility": 0.02, "liquidity": "high"}
        risk_params = {"max_position_size": 1000000, "risk_tolerance": 0.05}
        target_volume = 500000.0
        
        response = client.post("/api/v1/options/algo/optimize-sizing", 
                             json={"market_data": market_data, "risk_params": risk_params},
                             params={"target_volume": target_volume})
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "optimization_id" in data["data"]
        assert "optimal_slice_size" in data["data"]
    
    def test_monitor_execution_quality(self):
        """Test execution quality monitoring endpoint"""
        response = client.get("/api/v1/options/algo/execution-quality/EXE_20240115_100000")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "execution_id" in data["data"]
        assert "quality_score" in data["data"]
    
    def test_get_strategy_performance(self):
        """Test strategy performance endpoint"""
        response = client.get("/api/v1/options/algo/performance/twap", 
                             params={"time_period": "1M"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "strategy_type" in data["data"]
        assert "total_trades" in data["data"]
        assert "win_rate" in data["data"]
    
    def test_validate_algo_strategy(self):
        """Test algorithmic strategy validation endpoint"""
        strategy_data = {
            "strategy": "twap",
            "risk_controls": ["position_limits", "volatility_checks"],
            "execution_params": {"max_slippage": 0.01}
        }
        
        response = client.post("/api/v1/options/islamic/validate-algo", json=strategy_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "islamic_compliant" in data["data"]
        assert "compliance_score" in data["data"]
    
    def test_check_execution_ethics(self):
        """Test execution ethics checking endpoint"""
        execution_data = {
            "execution_id": "EXE_20240115_100000",
            "market_impact": 0.001,
            "execution_time": "2024-01-15T10:00:00"
        }
        
        response = client.post("/api/v1/options/islamic/check-execution-ethics", json=execution_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "ethical_execution" in data["data"]
        assert "fairness_score" in data["data"]

class TestAPIErrorHandling:
    """Test API error handling and edge cases"""
    
    def test_invalid_trade_data(self):
        """Test API with invalid trade data"""
        invalid_trade_data = {
            "trade_type": "invalid_type",
            "quantity": -1000,  # Negative quantity
            "price": 0  # Zero price
        }
        
        response = client.post("/api/v1/trade-lifecycle/capture", json=invalid_trade_data)
        
        # Should handle validation errors gracefully
        assert response.status_code in [400, 422, 500]
    
    def test_invalid_credit_limit(self):
        """Test API with invalid credit limit data"""
        invalid_credit_limit = {
            "counterparty_id": "",
            "limit_amount": -1000000,  # Negative amount
            "risk_rating": "Z"  # Invalid rating
        }
        
        response = client.post("/api/v1/credit/limits", json=invalid_credit_limit)
        
        # Should handle validation errors gracefully
        assert response.status_code in [400, 422, 500]
    
    def test_invalid_compliance_region(self):
        """Test API with invalid compliance region"""
        response = client.post("/api/v1/compliance/reports/generate", 
                             params={"region": "invalid_region", "regulation_type": "CFTC"})
        
        # Should return 400 for invalid region
        assert response.status_code == 400
    
    def test_invalid_risk_parameters(self):
        """Test API with invalid risk parameters"""
        response = client.post("/api/v1/risk-analytics/var/monte-carlo", 
                             json=SAMPLE_PORTFOLIO_DATA,
                             params={"confidence_level": 0.5, "time_horizon": -1, "num_simulations": 0})
        
        # Should handle invalid parameters gracefully
        assert response.status_code in [400, 422, 500]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
