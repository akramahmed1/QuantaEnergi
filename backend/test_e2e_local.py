#!/usr/bin/env python3
"""
Comprehensive E2E Local Testing for QuantaEnergi
Tests all endpoints, features, and integrations locally
"""

import requests
import json
import time
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"

class QuantaEnergiE2ETester:
    """Comprehensive E2E tester for QuantaEnergi"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.auth_token = None
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "total": 0,
            "details": []
        }
    
    def log_test(self, test_name, status, details=""):
        """Log test result"""
        self.test_results["total"] += 1
        if status == "PASS":
            self.test_results["passed"] += 1
            print(f"✅ {test_name}")
        else:
            self.test_results["failed"] += 1
            print(f"❌ {test_name}: {details}")
        
        self.test_results["details"].append({
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def test_health_endpoint(self):
        """Test health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_test("Health Check", "PASS")
                    return True
            self.log_test("Health Check", "FAIL", f"Status: {response.status_code}")
            return False
        except Exception as e:
            self.log_test("Health Check", "FAIL", str(e))
            return False
    
    def test_swagger_docs(self):
        """Test Swagger documentation"""
        try:
            response = requests.get(f"{self.base_url}/docs", timeout=5)
            if response.status_code == 200:
                self.log_test("Swagger Documentation", "PASS")
                return True
            self.log_test("Swagger Documentation", "FAIL", f"Status: {response.status_code}")
            return False
        except Exception as e:
            self.log_test("Swagger Documentation", "FAIL", str(e))
            return False
    
    def test_openapi_spec(self):
        """Test OpenAPI specification"""
        try:
            response = requests.get(f"{self.base_url}/openapi.json", timeout=5)
            if response.status_code == 200:
                spec = response.json()
                if "info" in spec and "paths" in spec:
                    self.log_test("OpenAPI Specification", "PASS")
                    return True
            self.log_test("OpenAPI Specification", "FAIL", f"Status: {response.status_code}")
            return False
        except Exception as e:
            self.log_test("OpenAPI Specification", "FAIL", str(e))
            return False
    
    def test_authentication(self):
        """Test authentication flow"""
        try:
            # Test login (this will fail without proper user setup, but we can test the endpoint)
            login_data = {"username": "testuser", "password": "testpass"}
            response = requests.post(f"{self.base_url}/auth/login", json=login_data, timeout=5)
            
            if response.status_code in [200, 401]:  # 200 for success, 401 for invalid credentials
                self.log_test("Authentication Endpoint", "PASS")
                return True
            self.log_test("Authentication Endpoint", "FAIL", f"Status: {response.status_code}")
            return False
        except Exception as e:
            self.log_test("Authentication Endpoint", "FAIL", str(e))
            return False
    
    def test_risk_endpoints(self):
        """Test VaR/Monte Carlo risk endpoints"""
        try:
            # Test parametric VaR
            prices = [150, 152, 148, 155, 160, 158, 162, 165, 163, 168]
            response = requests.post(f"{self.base_url}/risk/var", json=prices, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "param_var" in data:
                    self.log_test("Parametric VaR", "PASS")
                else:
                    self.log_test("Parametric VaR", "FAIL", "Missing param_var in response")
            else:
                self.log_test("Parametric VaR", "FAIL", f"Status: {response.status_code}")
            
            # Test Monte Carlo VaR
            response = requests.post(f"{self.base_url}/risk/var?method=monte_carlo", json=prices, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "mc_var" in data:
                    self.log_test("Monte Carlo VaR", "PASS")
                else:
                    self.log_test("Monte Carlo VaR", "FAIL", "Missing mc_var in response")
            else:
                self.log_test("Monte Carlo VaR", "FAIL", f"Status: {response.status_code}")
            
            # Test Enhanced VaR
            response = requests.post(f"{self.base_url}/risk/var?method=enhanced", json=prices, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "risk_assessment" in data:
                    self.log_test("Enhanced VaR", "PASS")
                else:
                    self.log_test("Enhanced VaR", "FAIL", "Missing risk_assessment in response")
            else:
                self.log_test("Enhanced VaR", "FAIL", f"Status: {response.status_code}")
            
            return True
        except Exception as e:
            self.log_test("Risk Endpoints", "FAIL", str(e))
            return False
    
    def test_market_data_endpoints(self):
        """Test market data endpoints"""
        try:
            # Test market prices endpoint
            response = requests.get(f"{self.base_url}/market/prices/BRENT", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "symbol" in data and "volatility" in data:
                    self.log_test("Market Data (BRENT)", "PASS")
                else:
                    self.log_test("Market Data (BRENT)", "FAIL", "Missing required fields")
            else:
                self.log_test("Market Data (BRENT)", "FAIL", f"Status: {response.status_code}")
            
            # Test WTI prices
            response = requests.get(f"{self.base_url}/market/prices/WTI", timeout=10)
            if response.status_code == 200:
                self.log_test("Market Data (WTI)", "PASS")
            else:
                self.log_test("Market Data (WTI)", "FAIL", f"Status: {response.status_code}")
            
            return True
        except Exception as e:
            self.log_test("Market Data Endpoints", "FAIL", str(e))
            return False
    
    def test_geo_risk_endpoints(self):
        """Test geo-risk assessment endpoints"""
        try:
            # Test geo-risk assessment for Guyana
            geo_data = {
                "region": "GUYANA",
                "volatility": 0.25,
                "sentiment": 0.4,
                "news_volume": 0.8
            }
            response = requests.post(f"{self.base_url}/geo-risk/assess", json=geo_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "risk_assessment" in data and "recommendations" in data:
                    self.log_test("Guyana Geo-Risk Assessment", "PASS")
                else:
                    self.log_test("Guyana Geo-Risk Assessment", "FAIL", "Missing required fields")
            else:
                self.log_test("Guyana Geo-Risk Assessment", "FAIL", f"Status: {response.status_code}")
            
            # Test Middle East geo-risk
            geo_data["region"] = "MIDDLE_EAST"
            response = requests.post(f"{self.base_url}/geo-risk/assess", json=geo_data, timeout=10)
            if response.status_code == 200:
                self.log_test("Middle East Geo-Risk Assessment", "PASS")
            else:
                self.log_test("Middle East Geo-Risk Assessment", "FAIL", f"Status: {response.status_code}")
            
            # Test supported regions
            response = requests.get(f"{self.base_url}/geo-risk/regions", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if "regions" in data and len(data["regions"]) >= 3:
                    self.log_test("Supported Regions", "PASS")
                else:
                    self.log_test("Supported Regions", "FAIL", "Insufficient regions")
            else:
                self.log_test("Supported Regions", "FAIL", f"Status: {response.status_code}")
            
            return True
        except Exception as e:
            self.log_test("Geo-Risk Endpoints", "FAIL", str(e))
            return False
    
    def test_quantum_optimization_endpoints(self):
        """Test quantum portfolio optimization endpoints"""
        try:
            # Test quantum optimization
            opt_data = {
                "returns": [0.05, 0.08, 0.12, 0.06, 0.09],
                "risks": [0.1, 0.15, 0.2, 0.12, 0.18]
            }
            response = requests.post(f"{self.base_url}/optimize/portfolio", json=opt_data, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if "weights" in data and "portfolio_return" in data:
                    self.log_test("Quantum Portfolio Optimization", "PASS")
                else:
                    self.log_test("Quantum Portfolio Optimization", "FAIL", "Missing required fields")
            else:
                self.log_test("Quantum Portfolio Optimization", "FAIL", f"Status: {response.status_code}")
            
            # Test classical optimization
            response = requests.post(f"{self.base_url}/optimize/portfolio?method=classical", json=opt_data, timeout=15)
            if response.status_code == 200:
                self.log_test("Classical Portfolio Optimization", "PASS")
            else:
                self.log_test("Classical Portfolio Optimization", "FAIL", f"Status: {response.status_code}")
            
            return True
        except Exception as e:
            self.log_test("Quantum Optimization Endpoints", "FAIL", str(e))
            return False
    
    def test_remit_compliance_endpoints(self):
        """Test REMIT compliance endpoints"""
        try:
            # Test compliant trade
            compliant_trade = {
                "trade": {
                    "asset": "brent_crude_oil",
                    "quantity": 500,
                    "price": 75.50,
                    "market_price": 75.00,
                    "timestamp": "2024-01-15T10:30:00Z",
                    "counterparty": "Shell_Energy",
                    "trader": "John_Smith",
                    "energy_type": "oil",
                    "cross_border": False
                },
                "framework": "REMIT"
            }
            response = requests.post(f"{self.base_url}/compliance/validate", json=compliant_trade, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "compliant" in data and "violations" in data:
                    self.log_test("REMIT Compliance (Compliant Trade)", "PASS")
                else:
                    self.log_test("REMIT Compliance (Compliant Trade)", "FAIL", "Missing required fields")
            else:
                self.log_test("REMIT Compliance (Compliant Trade)", "FAIL", f"Status: {response.status_code}")
            
            # Test position limit violation
            violation_trade = {
                "trade": {
                    "asset": "wti_crude_oil",
                    "quantity": 1200,  # Over 1000 bbl/day limit
                    "price": 70.25,
                    "market_price": 70.00,
                    "timestamp": "2024-01-15T11:00:00Z",
                    "counterparty": "BP_Trading",
                    "trader": "Jane_Doe",
                    "energy_type": "oil",
                    "cross_border": False
                },
                "framework": "REMIT"
            }
            response = requests.post(f"{self.base_url}/compliance/validate", json=violation_trade, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if not data.get("compliant", True) and len(data.get("violations", [])) > 0:
                    self.log_test("REMIT Compliance (Position Limit Violation)", "PASS")
                else:
                    self.log_test("REMIT Compliance (Position Limit Violation)", "FAIL", "Violation not detected")
            else:
                self.log_test("REMIT Compliance (Position Limit Violation)", "FAIL", f"Status: {response.status_code}")
            
            return True
        except Exception as e:
            self.log_test("REMIT Compliance Endpoints", "FAIL", str(e))
            return False
    
    def test_forecast_endpoints(self):
        """Test forecasting endpoints"""
        try:
            # Test price forecasting
            historical_data = [75.0, 76.5, 74.2, 77.8, 73.1, 79.2, 72.5, 81.3, 71.8, 83.7]
            response = requests.post(f"{self.base_url}/forecast/price", json=historical_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "prediction" in data and "accuracy" in data:
                    self.log_test("Price Forecasting", "PASS")
                else:
                    self.log_test("Price Forecasting", "FAIL", "Missing required fields")
            else:
                self.log_test("Price Forecasting", "FAIL", f"Status: {response.status_code}")
            
            # Test load forecasting
            response = requests.post(f"{self.base_url}/forecast/load", json=historical_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "predicted" in data:
                    self.log_test("Load Forecasting", "PASS")
                else:
                    self.log_test("Load Forecasting", "FAIL", "Missing predicted field")
            else:
                self.log_test("Load Forecasting", "FAIL", f"Status: {response.status_code}")
            
            return True
        except Exception as e:
            self.log_test("Forecast Endpoints", "FAIL", str(e))
            return False
    
    def test_metrics_endpoint(self):
        """Test metrics endpoint"""
        try:
            response = requests.get(f"{self.base_url}/metrics", timeout=5)
            if response.status_code == 200:
                self.log_test("Metrics Endpoint", "PASS")
                return True
            self.log_test("Metrics Endpoint", "FAIL", f"Status: {response.status_code}")
            return False
        except Exception as e:
            self.log_test("Metrics Endpoint", "FAIL", str(e))
            return False
    
    def run_all_tests(self):
        """Run all E2E tests"""
        print("🚀 QuantaEnergi E2E Local Testing")
        print("=" * 50)
        print()
        
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        time.sleep(3)
        
        # Test basic endpoints
        print("🔍 Testing Basic Endpoints...")
        self.test_health_endpoint()
        self.test_swagger_docs()
        self.test_openapi_spec()
        self.test_authentication()
        self.test_metrics_endpoint()
        print()
        
        # Test Phase 1: VaR/Monte Carlo Risk
        print("🔬 Testing Phase 1: VaR/Monte Carlo Risk...")
        self.test_risk_endpoints()
        print()
        
        # Test Phase 2: Alpha Vantage + Geo-Risk AI
        print("🌐 Testing Phase 2: Alpha Vantage + Geo-Risk AI...")
        self.test_market_data_endpoints()
        self.test_geo_risk_endpoints()
        print()
        
        # Test Phase 3: Quantum Optimization + REMIT Compliance
        print("🔬 Testing Phase 3: Quantum Optimization + REMIT Compliance...")
        self.test_quantum_optimization_endpoints()
        self.test_remit_compliance_endpoints()
        print()
        
        # Test additional endpoints
        print("📊 Testing Additional Endpoints...")
        self.test_forecast_endpoints()
        print()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("📊 E2E Test Summary")
        print("=" * 50)
        print(f"Total Tests: {self.test_results['total']}")
        print(f"Passed: {self.test_results['passed']}")
        print(f"Failed: {self.test_results['failed']}")
        print(f"Success Rate: {(self.test_results['passed']/self.test_results['total']*100):.1f}%")
        print()
        
        if self.test_results['failed'] > 0:
            print("❌ Failed Tests:")
            for test in self.test_results['details']:
                if test['status'] == 'FAIL':
                    print(f"  - {test['test']}: {test['details']}")
            print()
        
        if self.test_results['failed'] == 0:
            print("🎉 All E2E tests passed!")
            print("✅ QuantaEnergi is ready for production!")
        else:
            print(f"⚠️ {self.test_results['failed']} tests failed")
            print("❌ Some issues need to be resolved")
        
        return self.test_results['failed'] == 0

def main():
    """Run E2E tests"""
    tester = QuantaEnergiE2ETester()
    success = tester.run_all_tests()
    
    # Save test results
    with open("e2e_test_results.json", "w") as f:
        json.dump(tester.test_results, f, indent=2)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
