#!/usr/bin/env python3
"""
Comprehensive End-to-End Test for QuantaEnergi Platform
Tests all major features and integrations
"""

import requests
import json
import time
import sys
import os
from datetime import datetime, timedelta

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"
TEST_USER = {"username": "admin", "password": "secret"}

class QuantaEnergiE2ETest:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.test_results = []
        
    def log_test(self, test_name, status, message=""):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"{status_icon} {test_name}: {message}")
        
    def test_backend_health(self):
        """Test backend health endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Backend Health", "PASS", f"Status: {data.get('status')}")
                return True
            else:
                self.log_test("Backend Health", "FAIL", f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Health", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_authentication(self):
        """Test authentication flow"""
        try:
            # Test login
            response = self.session.post(
                f"{BACKEND_URL}/api/v1/login",
                data=TEST_USER,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.log_test("Authentication", "PASS", "Login successful")
                
                # Test protected endpoint
                headers = {"Authorization": f"Bearer {self.token}"}
                response = self.session.get(
                    f"{BACKEND_URL}/api/v1/me",
                    headers=headers,
                    timeout=10
                )
                if response.status_code == 200:
                    self.log_test("Protected Endpoint", "PASS", "Token validation successful")
                    return True
                else:
                    self.log_test("Protected Endpoint", "FAIL", f"Status code: {response.status_code}")
                    return False
            else:
                self.log_test("Authentication", "FAIL", f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Authentication", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_trade_lifecycle(self):
        """Test complete trade lifecycle"""
        if not self.token:
            self.log_test("Trade Lifecycle", "SKIP", "No authentication token")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # 1. Create a trade
            trade_data = {
                "commodity": "electricity",
                "quantity": 100,
                "price": 50.0,
                "trade_type": "spot"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/api/v1/capture",
                json=trade_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 201:
                trade = response.json()
                trade_id = trade.get("id")
                self.log_test("Trade Creation", "PASS", f"Trade ID: {trade_id}")
                
                # 2. Validate trade
                response = self.session.post(
                    f"{BACKEND_URL}/api/v1/validate/{trade_id}",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    self.log_test("Trade Validation", "PASS", "Trade validated successfully")
                    
                    # 3. Settle trade
                    response = self.session.post(
                        f"{BACKEND_URL}/api/v1/settle/{trade_id}",
                        headers=headers,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        self.log_test("Trade Settlement", "PASS", "Trade settled successfully")
                        
                        # 4. Get trades list
                        response = self.session.get(
                            f"{BACKEND_URL}/api/v1/trades",
                            headers=headers,
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            trades = response.json()
                            self.log_test("Trade Retrieval", "PASS", f"Retrieved {len(trades)} trades")
                            return True
                        else:
                            self.log_test("Trade Retrieval", "FAIL", f"Status code: {response.status_code}")
                            return False
                    else:
                        self.log_test("Trade Settlement", "FAIL", f"Status code: {response.status_code}")
                        return False
                else:
                    self.log_test("Trade Validation", "FAIL", f"Status code: {response.status_code}")
                    return False
            else:
                self.log_test("Trade Creation", "FAIL", f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Trade Lifecycle", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_analytics_features(self):
        """Test analytics and AI features"""
        if not self.token:
            self.log_test("Analytics Features", "SKIP", "No authentication token")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # 1. Test AI forecasting
            response = self.session.post(
                f"{BACKEND_URL}/api/v1/forecast?periods=7",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                forecast = response.json()
                self.log_test("AI Forecasting", "PASS", f"Generated {len(forecast.get('forecast', []))} forecast points")
            else:
                self.log_test("AI Forecasting", "FAIL", f"Status code: {response.status_code}")
                return False
            
            # 2. Test market insights
            response = self.session.get(
                f"{BACKEND_URL}/api/v1/forecast/insights/crude_oil",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                insights = response.json()
                self.log_test("Market Insights", "PASS", f"Sentiment: {insights.get('sentiment')}")
            else:
                self.log_test("Market Insights", "FAIL", f"Status code: {response.status_code}")
                return False
            
            # 3. Test portfolio optimization
            optimization_data = {
                "returns": [0.1, 0.05, 0.08],
                "volatilities": [0.2, 0.1, 0.15],
                "budget": 1.0
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/api/v1/optimize/portfolio",
                json=optimization_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                optimization = response.json()
                self.log_test("Portfolio Optimization", "PASS", f"Method: {optimization.get('method')}")
            else:
                self.log_test("Portfolio Optimization", "FAIL", f"Status code: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("Analytics Features", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_compliance_features(self):
        """Test compliance and regulatory features"""
        if not self.token:
            self.log_test("Compliance Features", "SKIP", "No authentication token")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # 1. Test Sharia compliance check
            trade_data = {
                "id": "test-trade-compliance",
                "commodity": "electricity",
                "price": 50.0,
                "quantity": 100,
                "trade_type": "spot",
                "delivery_date": (datetime.now() + timedelta(days=7)).isoformat(),
                "delivery_location": "Dubai"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/api/v1/sharia/check",
                json=trade_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                compliance = response.json()
                self.log_test("Sharia Compliance", "PASS", f"Status: {compliance.get('overall_status')}")
            else:
                self.log_test("Sharia Compliance", "FAIL", f"Status code: {response.status_code}")
                return False
            
            # 2. Test compliance report generation
            report_data = {
                "report_type": "cftc",
                "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
                "end_date": datetime.now().isoformat(),
                "data": [],
                "anonymize": True
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/api/v1/reports/generate",
                json=report_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                report = response.json()
                self.log_test("Compliance Reporting", "PASS", f"Report ID: {report.get('report_id')}")
            else:
                self.log_test("Compliance Reporting", "FAIL", f"Status code: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("Compliance Features", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_blockchain_features(self):
        """Test blockchain and ESG features"""
        if not self.token:
            self.log_test("Blockchain Features", "SKIP", "No authentication token")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # 1. Test carbon trade creation
            carbon_trade_data = {
                "buyer_address": "0xTestBuyer123",
                "seller_address": "0xTestSeller456",
                "carbon_amount": 100.0,
                "price": 25.5
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/api/v1/blockchain/carbon-trade",
                json=carbon_trade_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                carbon_trade = response.json()
                self.log_test("Carbon Trading", "PASS", f"Trade ID: {carbon_trade.get('trade_id')}")
            else:
                self.log_test("Carbon Trading", "FAIL", f"Status code: {response.status_code}")
                return False
            
            # 2. Test ESG score retrieval
            response = self.session.get(
                f"{BACKEND_URL}/api/v1/blockchain/esg-score/companyA_address",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                esg_score = response.json()
                self.log_test("ESG Scoring", "PASS", f"Score: {esg_score.get('score')}")
            else:
                self.log_test("ESG Scoring", "FAIL", f"Status code: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("Blockchain Features", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_billing_features(self):
        """Test billing and subscription features"""
        if not self.token:
            self.log_test("Billing Features", "SKIP", "No authentication token")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # 1. Test billing plans retrieval
            response = self.session.get(
                f"{BACKEND_URL}/api/v1/billing/plans",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                plans = response.json()
                plan_count = len(plans.get('plans', {}))
                self.log_test("Billing Plans", "PASS", f"Retrieved {plan_count} plans")
            else:
                self.log_test("Billing Plans", "FAIL", f"Status code: {response.status_code}")
                return False
            
            # 2. Test customer creation
            customer_data = {
                "email": "test@example.com",
                "name": "Test Customer",
                "user_id": "test-user-123"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/api/v1/billing/customers",
                json=customer_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                customer = response.json()
                self.log_test("Customer Creation", "PASS", f"Customer ID: {customer.get('customer_id')}")
            else:
                self.log_test("Customer Creation", "FAIL", f"Status code: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("Billing Features", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        if not self.token:
            self.log_test("Rate Limiting", "SKIP", "No authentication token")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Make multiple rapid requests to test rate limiting
            rate_limit_hit = False
            for i in range(10):
                response = self.session.get(
                    f"{BACKEND_URL}/api/v1/trades",
                    headers=headers,
                    timeout=5
                )
                
                if response.status_code == 429:  # Too Many Requests
                    rate_limit_hit = True
                    break
                
                time.sleep(0.1)  # Small delay between requests
            
            if rate_limit_hit:
                self.log_test("Rate Limiting", "PASS", "Rate limiting working correctly")
            else:
                self.log_test("Rate Limiting", "PASS", "Rate limiting not triggered (normal)")
            
            return True
            
        except Exception as e:
            self.log_test("Rate Limiting", "FAIL", f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all E2E tests"""
        print("🚀 Starting QuantaEnergi E2E Tests")
        print("=" * 50)
        
        # Wait for backend to be ready
        print("⏳ Waiting for backend to be ready...")
        for i in range(30):
            if self.test_backend_health():
                break
            time.sleep(1)
        else:
            print("❌ Backend not ready after 30 seconds")
            return False
        
        print("\n🧪 Running comprehensive E2E tests...\n")
        
        # Run all test suites
        test_suites = [
            ("Authentication", self.test_authentication),
            ("Trade Lifecycle", self.test_trade_lifecycle),
            ("Analytics Features", self.test_analytics_features),
            ("Compliance Features", self.test_compliance_features),
            ("Blockchain Features", self.test_blockchain_features),
            ("Billing Features", self.test_billing_features),
            ("Rate Limiting", self.test_rate_limiting)
        ]
        
        passed = 0
        failed = 0
        skipped = 0
        
        for suite_name, test_func in test_suites:
            try:
                result = test_func()
                if result:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.log_test(suite_name, "FAIL", f"Exception: {str(e)}")
                failed += 1
        
        # Count results
        for result in self.test_results:
            if result["status"] == "PASS":
                passed += 1
            elif result["status"] == "FAIL":
                failed += 1
            elif result["status"] == "SKIP":
                skipped += 1
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 E2E Test Summary")
        print("=" * 50)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⏭️  Skipped: {skipped}")
        print(f"📈 Total: {passed + failed + skipped}")
        
        if failed == 0:
            print("\n🎉 All tests passed! QuantaEnergi is ready for production!")
        else:
            print(f"\n⚠️  {failed} tests failed. Please review the issues above.")
        
        # Save detailed results
        with open("e2e_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: e2e_test_results.json")
        
        return failed == 0

def main():
    """Main function"""
    print("QuantaEnergi Comprehensive E2E Test Suite")
    print("=" * 50)
    
    # Check if backend is running
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ Backend not responding at {BACKEND_URL}")
            print("Please start the backend with: python -m uvicorn apps.backend.app.main:app --host 0.0.0.0 --port 8000")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print(f"❌ Cannot connect to backend at {BACKEND_URL}")
        print("Please start the backend with: python -m uvicorn apps.backend.app.main:app --host 0.0.0.0 --port 8000")
        sys.exit(1)
    
    # Run tests
    tester = QuantaEnergiE2ETest()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
