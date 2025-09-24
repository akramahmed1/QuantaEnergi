"""
Load testing suite using Locust
Tests API performance under various load conditions
"""

from locust import HttpUser, task, between
import random
import json
from datetime import datetime, timedelta

class QuantaEnergiUser(HttpUser):
    """Locust user class for QuantaEnergi API load testing"""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Called when a user starts"""
        self.login()
    
    def login(self):
        """Login and store token"""
        response = self.client.post(
            "/api/v1/login",
            data={"username": "admin", "password": "secret"}
        )
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}
    
    @task(3)
    def get_health(self):
        """Test health check endpoint"""
        self.client.get("/health")
    
    @task(5)
    def get_trades(self):
        """Test getting trades"""
        if self.token:
            self.client.get("/api/v1/trades", headers=self.headers)
    
    @task(2)
    def create_trade(self):
        """Test creating a trade"""
        if self.token:
            trade_data = {
                "commodity": random.choice(["electricity", "solar_energy", "wind_energy", "natural_gas"]),
                "quantity": random.randint(10, 1000),
                "price": round(random.uniform(20.0, 100.0), 2),
                "trade_type": random.choice(["spot", "forward", "futures"])
            }
            self.client.post(
                "/api/v1/capture",
                json=trade_data,
                headers=self.headers
            )
    
    @task(1)
    def get_forecast(self):
        """Test AI forecasting"""
        if self.token:
            periods = random.randint(7, 90)
            self.client.post(
                f"/api/v1/forecast?periods={periods}",
                headers=self.headers
            )
    
    @task(1)
    def get_market_insights(self):
        """Test market insights"""
        if self.token:
            commodity = random.choice(["crude_oil", "natural_gas", "electricity"])
            self.client.get(
                f"/api/v1/forecast/insights/{commodity}",
                headers=self.headers
            )
    
    @task(1)
    def optimize_portfolio(self):
        """Test portfolio optimization"""
        if self.token:
            # Generate random portfolio data
            num_assets = random.randint(2, 5)
            returns = [round(random.uniform(0.01, 0.15), 3) for _ in range(num_assets)]
            volatilities = [round(random.uniform(0.05, 0.25), 3) for _ in range(num_assets)]
            
            optimization_data = {
                "returns": returns,
                "volatilities": volatilities,
                "budget": 1.0
            }
            self.client.post(
                "/api/v1/optimize/portfolio",
                json=optimization_data,
                headers=self.headers
            )
    
    @task(1)
    def create_carbon_trade(self):
        """Test carbon credit trading"""
        if self.token:
            carbon_trade_data = {
                "buyer_address": f"0xBuyer{random.randint(1000, 9999)}",
                "seller_address": f"0xSeller{random.randint(1000, 9999)}",
                "carbon_amount": random.randint(50, 500),
                "price": round(random.uniform(10.0, 50.0), 2)
            }
            self.client.post(
                "/api/v1/blockchain/carbon-trade",
                json=carbon_trade_data,
                headers=self.headers
            )
    
    @task(1)
    def get_esg_score(self):
        """Test ESG score retrieval"""
        if self.token:
            company_addresses = ["companyA_address", "companyB_address", "companyC_address"]
            company = random.choice(company_addresses)
            self.client.get(
                f"/api/v1/blockchain/esg-score/{company}",
                headers=self.headers
            )
    
    @task(1)
    def check_sharia_compliance(self):
        """Test Sharia compliance checking"""
        if self.token:
            trade_data = {
                "id": f"trade-{random.randint(1000, 9999)}",
                "commodity": random.choice(["electricity", "solar_energy", "wind_energy"]),
                "price": round(random.uniform(30.0, 80.0), 2),
                "quantity": random.randint(50, 500),
                "trade_type": random.choice(["spot", "forward"]),
                "delivery_date": (datetime.now() + timedelta(days=random.randint(1, 30))).isoformat(),
                "delivery_location": random.choice(["New York", "London", "Dubai", "Singapore"])
            }
            self.client.post(
                "/api/v1/sharia/check",
                json=trade_data,
                headers=self.headers
            )
    
    @task(1)
    def generate_compliance_report(self):
        """Test compliance report generation"""
        if self.token:
            report_types = ["cftc", "emir", "gdpr", "guyana"]
            report_type = random.choice(report_types)
            
            start_date = (datetime.now() - timedelta(days=30)).isoformat()
            end_date = datetime.now().isoformat()
            
            report_data = {
                "report_type": report_type,
                "start_date": start_date,
                "end_date": end_date,
                "data": [],
                "anonymize": True
            }
            self.client.post(
                "/api/v1/reports/generate",
                json=report_data,
                headers=self.headers
            )
    
    @task(1)
    def get_billing_plans(self):
        """Test billing plans retrieval"""
        if self.token:
            self.client.get("/api/v1/billing/plans", headers=self.headers)
    
    @task(1)
    def create_customer(self):
        """Test customer creation"""
        if self.token:
            customer_data = {
                "email": f"test{random.randint(1000, 9999)}@example.com",
                "name": f"Test User {random.randint(1000, 9999)}",
                "user_id": f"user-{random.randint(1000, 9999)}"
            }
            self.client.post(
                "/api/v1/billing/customers",
                json=customer_data,
                headers=self.headers
            )

class HighFrequencyTrader(QuantaEnergiUser):
    """High frequency trading simulation"""
    
    wait_time = between(0.1, 0.5)  # Much faster execution
    
    @task(10)
    def rapid_trade_creation(self):
        """Rapid trade creation for high frequency testing"""
        if self.token:
            trade_data = {
                "commodity": random.choice(["electricity", "solar_energy"]),
                "quantity": random.randint(100, 1000),
                "price": round(random.uniform(40.0, 60.0), 2),
                "trade_type": "spot"
            }
            self.client.post(
                "/api/v1/capture",
                json=trade_data,
                headers=self.headers
            )
    
    @task(5)
    def rapid_forecast_requests(self):
        """Rapid forecasting requests"""
        if self.token:
            periods = random.randint(1, 7)
            self.client.post(
                f"/api/v1/forecast?periods={periods}",
                headers=self.headers
            )

class ComplianceOfficer(QuantaEnergiUser):
    """Compliance officer simulation - focuses on compliance tasks"""
    
    wait_time = between(2, 5)
    
    @task(5)
    def generate_reports(self):
        """Generate various compliance reports"""
        if self.token:
            report_types = ["cftc", "emir", "gdpr", "guyana"]
            for report_type in report_types:
                report_data = {
                    "report_type": report_type,
                    "start_date": (datetime.now() - timedelta(days=7)).isoformat(),
                    "end_date": datetime.now().isoformat(),
                    "data": [],
                    "anonymize": True
                }
                self.client.post(
                    "/api/v1/reports/generate",
                    json=report_data,
                    headers=self.headers
                )
    
    @task(3)
    def check_sharia_compliance(self):
        """Check Sharia compliance for trades"""
        if self.token:
            trade_data = {
                "id": f"compliance-check-{random.randint(1000, 9999)}",
                "commodity": "electricity",
                "price": round(random.uniform(30.0, 80.0), 2),
                "quantity": random.randint(50, 500),
                "trade_type": "spot",
                "delivery_date": (datetime.now() + timedelta(days=random.randint(1, 30))).isoformat(),
                "delivery_location": "Dubai"
            }
            self.client.post(
                "/api/v1/sharia/check",
                json=trade_data,
                headers=self.headers
            )
    
    @task(2)
    def get_consolidated_reports(self):
        """Get consolidated compliance reports"""
        if self.token:
            report_data = {
                "report_types": ["cftc", "emir", "gdpr"],
                "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
                "end_date": datetime.now().isoformat(),
                "data": []
            }
            self.client.post(
                "/api/v1/reports/consolidated",
                json=report_data,
                headers=self.headers
            )

class AnalyticsUser(QuantaEnergiUser):
    """Analytics user simulation - focuses on AI and quantum features"""
    
    wait_time = between(1, 3)
    
    @task(4)
    def get_forecasts(self):
        """Get various forecasts"""
        if self.token:
            periods = random.randint(7, 90)
            self.client.post(
                f"/api/v1/forecast?periods={periods}",
                headers=self.headers
            )
    
    @task(3)
    def optimize_portfolios(self):
        """Optimize various portfolios"""
        if self.token:
            num_assets = random.randint(2, 8)
            returns = [round(random.uniform(0.01, 0.20), 3) for _ in range(num_assets)]
            volatilities = [round(random.uniform(0.05, 0.30), 3) for _ in range(num_assets)]
            
            optimization_data = {
                "returns": returns,
                "volatilities": volatilities,
                "budget": 1.0
            }
            self.client.post(
                "/api/v1/optimize/portfolio",
                json=optimization_data,
                headers=self.headers
            )
    
    @task(2)
    def get_market_insights(self):
        """Get market insights for different commodities"""
        if self.token:
            commodities = ["crude_oil", "natural_gas", "electricity", "solar_energy"]
            commodity = random.choice(commodities)
            self.client.get(
                f"/api/v1/forecast/insights/{commodity}",
                headers=self.headers
            )
    
    @task(1)
    def optimize_strategies(self):
        """Optimize trading strategies"""
        if self.token:
            historical_data = [
                {
                    "price": round(random.uniform(40.0, 60.0), 2),
                    "volume": random.randint(1000, 5000),
                    "timestamp": (datetime.now() - timedelta(days=i)).isoformat()
                }
                for i in range(30)
            ]
            self.client.post(
                "/api/v1/optimize/strategy",
                json=historical_data,
                headers=self.headers
            )

# Configuration for different test scenarios
class LoadTestConfig:
    """Configuration for load tests"""
    
    @staticmethod
    def get_normal_load_config():
        """Normal load configuration"""
        return {
            "QuantaEnergiUser": 10,  # 10 normal users
            "ComplianceOfficer": 2,  # 2 compliance officers
            "AnalyticsUser": 3,      # 3 analytics users
        }
    
    @staticmethod
    def get_high_load_config():
        """High load configuration"""
        return {
            "QuantaEnergiUser": 50,  # 50 normal users
            "ComplianceOfficer": 5,  # 5 compliance officers
            "AnalyticsUser": 10,     # 10 analytics users
        }
    
    @staticmethod
    def get_stress_test_config():
        """Stress test configuration"""
        return {
            "QuantaEnergiUser": 100,  # 100 normal users
            "HighFrequencyTrader": 20, # 20 high frequency traders
            "ComplianceOfficer": 10,  # 10 compliance officers
            "AnalyticsUser": 20,      # 20 analytics users
        }

if __name__ == "__main__":
    # This file can be run with: locust -f load_tests.py --host=http://localhost:8000
    print("Load testing suite for QuantaEnergi API")
    print("Run with: locust -f load_tests.py --host=http://localhost:8000")
    print("\nAvailable user types:")
    print("- QuantaEnergiUser: General API usage")
    print("- HighFrequencyTrader: High frequency trading simulation")
    print("- ComplianceOfficer: Compliance-focused usage")
    print("- AnalyticsUser: AI and analytics-focused usage")
