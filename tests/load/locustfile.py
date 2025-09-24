"""
Locust Load Testing for QuantaEnergi Platform
Simulates realistic trading workload with 1000+ concurrent users
"""

import json
import random
import time
from datetime import datetime, timezone
from typing import Dict, Any

from locust import HttpUser, task, between, events
from locust.exception import RescheduleTask


class QuantaEnergiUser(HttpUser):
    """Simulates a realistic trading user"""
    
    wait_time = between(1, 5)  # Wait 1-5 seconds between tasks
    
    def on_start(self):
        """Called when a user starts"""
        self.tenant_id = f"tenant_{random.randint(1, 100)}"
        self.user_id = f"user_{random.randint(1, 1000)}"
        self.access_token = None
        self.trade_counter = 0
        
        # Login to get access token
        self.login()
    
    def login(self):
        """Simulate user login"""
        login_data = {
            "username": f"trader_{self.user_id}",
            "password": "test_password_123",
            "tenant_id": self.tenant_id
        }
        
        with self.client.post("/api/auth/login", json=login_data, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                response.success()
            else:
                response.failure(f"Login failed: {response.status_code}")
                raise RescheduleTask()
    
    @task(10)
    def get_market_prices(self):
        """Get current market prices - most frequent operation"""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Tenant-ID": self.tenant_id
        }
        
        region = random.choice(["us", "eu", "middle_east", "guyana"])
        ramadan_mode = random.choice([True, False])
        
        with self.client.get(
            f"/api/market/prices?region={region}&ramadan_mode={ramadan_mode}",
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                # Validate response structure
                if "crude_oil" in data and "natural_gas" in data:
                    response.success()
                else:
                    response.failure("Invalid market data structure")
            else:
                response.failure(f"Market prices failed: {response.status_code}")
    
    @task(8)
    def get_trading_signals(self):
        """Get trading signals"""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Tenant-ID": self.tenant_id
        }
        
        commodity = random.choice(["crude_oil", "natural_gas", "electricity", "carbon_credits"])
        confidence_min = random.uniform(50.0, 95.0)
        
        with self.client.get(
            f"/api/signals?commodity={commodity}&confidence_min={confidence_min}",
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "signals" in data and len(data["signals"]) > 0:
                    response.success()
                else:
                    response.failure("No trading signals returned")
            else:
                response.failure(f"Trading signals failed: {response.status_code}")
    
    @task(6)
    def get_portfolio_summary(self):
        """Get portfolio summary"""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Tenant-ID": self.tenant_id
        }
        
        with self.client.get(
            "/api/portfolio/summary",
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "total_value" in data and "positions" in data:
                    response.success()
                else:
                    response.failure("Invalid portfolio structure")
            else:
                response.failure(f"Portfolio summary failed: {response.status_code}")
    
    @task(5)
    def get_recent_trades(self):
        """Get recent trading history"""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Tenant-ID": self.tenant_id
        }
        
        limit = random.randint(5, 50)
        
        with self.client.get(
            f"/api/trades/recent?limit={limit}",
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "trades" in data:
                    response.success()
                else:
                    response.failure("No trades returned")
            else:
                response.failure(f"Recent trades failed: {response.status_code}")
    
    @task(4)
    def create_trade(self):
        """Create a new trade"""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Tenant-ID": self.tenant_id,
            "Content-Type": "application/json"
        }
        
        trade_data = {
            "trade_type": random.choice(["spot", "forward", "futures"]),
            "commodity_type": random.choice(["crude_oil", "natural_gas", "electricity"]),
            "quantity": random.randint(100, 10000),
            "price": round(random.uniform(20, 100), 2),
            "currency": random.choice(["USD", "EUR", "GBP"]),
            "counterparty": f"counterparty_{random.randint(1, 100)}",
            "trade_date": datetime.now(timezone.utc).isoformat(),
            "settlement_date": datetime.now(timezone.utc).isoformat(),
            "region": random.choice(["us", "eu", "middle_east"]),
            "is_sharia_compliant": random.choice([True, False])
        }
        
        with self.client.post(
            "/api/v1/trade-lifecycle/capture",
            json=trade_data,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code in [200, 201]:
                self.trade_counter += 1
                response.success()
            else:
                response.failure(f"Trade creation failed: {response.status_code}")
    
    @task(3)
    def calculate_var(self):
        """Calculate Value at Risk"""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Tenant-ID": self.tenant_id,
            "Content-Type": "application/json"
        }
        
        var_data = {
            "portfolio_id": f"portfolio_{self.user_id}",
            "confidence_level": random.choice([0.95, 0.99]),
            "time_horizon": random.choice([1, 5, 10]),
            "calculation_method": random.choice(["monte_carlo", "parametric", "historical"])
        }
        
        with self.client.post(
            "/api/v1/risk-analytics/var/monte-carlo",
            json=var_data,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "var_value" in data:
                    response.success()
                else:
                    response.failure("Invalid VaR response")
            else:
                response.failure(f"VaR calculation failed: {response.status_code}")
    
    @task(2)
    def get_esg_metrics(self):
        """Get ESG metrics"""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Tenant-ID": self.tenant_id
        }
        
        with self.client.get(
            "/api/esg/metrics",
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "overall_esg_score" in data:
                    response.success()
                else:
                    response.failure("Invalid ESG metrics")
            else:
                response.failure(f"ESG metrics failed: {response.status_code}")
    
    @task(2)
    def get_weather_data(self):
        """Get weather data for trading analysis"""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Tenant-ID": self.tenant_id
        }
        
        lat = random.uniform(20, 60)  # Random latitude
        lon = random.uniform(-120, 120)  # Random longitude
        
        with self.client.get(
            f"/api/weather/current?lat={lat}&lon={lon}",
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "temp" in data and "humidity" in data:
                    response.success()
                else:
                    response.failure("Invalid weather data")
            else:
                response.failure(f"Weather data failed: {response.status_code}")
    
    @task(1)
    def get_energy_forecast(self):
        """Get energy price forecast"""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Tenant-ID": self.tenant_id
        }
        
        commodity = random.choice(["crude_oil", "natural_gas", "electricity"])
        days = random.randint(7, 30)
        
        with self.client.get(
            f"/api/forecast/energy?commodity={commodity}&days={days}",
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "forecasts" in data and "summary" in data:
                    response.success()
                else:
                    response.failure("Invalid forecast data")
            else:
                response.failure(f"Energy forecast failed: {response.status_code}")
    
    @task(1)
    def stress_test_scenario(self):
        """Run stress test scenario"""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Tenant-ID": self.tenant_id,
            "Content-Type": "application/json"
        }
        
        stress_data = {
            "portfolio_id": f"portfolio_{self.user_id}",
            "scenario_name": f"stress_{random.randint(1, 10)}",
            "market_shocks": {
                "crude_oil": random.uniform(-0.3, 0.3),
                "natural_gas": random.uniform(-0.2, 0.2),
                "electricity": random.uniform(-0.4, 0.4)
            }
        }
        
        with self.client.post(
            "/api/v1/risk-analytics/stress-test",
            json=stress_data,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "loss_amount" in data:
                    response.success()
                else:
                    response.failure("Invalid stress test response")
            else:
                response.failure(f"Stress test failed: {response.status_code}")


class HighFrequencyTrader(HttpUser):
    """Simulates high-frequency trading behavior"""
    
    wait_time = between(0.1, 0.5)  # Very fast trading
    
    def on_start(self):
        """Called when a user starts"""
        self.tenant_id = f"hft_tenant_{random.randint(1, 10)}"
        self.user_id = f"hft_user_{random.randint(1, 100)}"
        self.access_token = None
        self.login()
    
    def login(self):
        """Quick login for HFT user"""
        login_data = {
            "username": f"hft_trader_{self.user_id}",
            "password": "hft_password_123",
            "tenant_id": self.tenant_id
        }
        
        with self.client.post("/api/auth/login", json=login_data, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                response.success()
            else:
                response.failure(f"HFT login failed: {response.status_code}")
                raise RescheduleTask()
    
    @task(20)
    def rapid_market_data_updates(self):
        """Rapid market data updates for HFT"""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Tenant-ID": self.tenant_id
        }
        
        with self.client.get(
            "/api/market/prices?region=global",
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HFT market data failed: {response.status_code}")
    
    @task(15)
    def rapid_trade_execution(self):
        """Rapid trade execution"""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Tenant-ID": self.tenant_id,
            "Content-Type": "application/json"
        }
        
        trade_data = {
            "trade_type": "spot",
            "commodity_type": random.choice(["crude_oil", "natural_gas"]),
            "quantity": random.randint(1000, 5000),
            "price": round(random.uniform(80, 90), 2),
            "currency": "USD",
            "counterparty": f"hft_counterparty_{random.randint(1, 20)}",
            "trade_date": datetime.now(timezone.utc).isoformat(),
            "settlement_date": datetime.now(timezone.utc).isoformat(),
            "region": "us"
        }
        
        with self.client.post(
            "/api/v1/trade-lifecycle/capture",
            json=trade_data,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(f"HFT trade failed: {response.status_code}")
    
    @task(10)
    def rapid_risk_calculations(self):
        """Rapid risk calculations for HFT"""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Tenant-ID": self.tenant_id,
            "Content-Type": "application/json"
        }
        
        var_data = {
            "portfolio_id": f"hft_portfolio_{self.user_id}",
            "confidence_level": 0.99,
            "time_horizon": 1,
            "calculation_method": "monte_carlo"
        }
        
        with self.client.post(
            "/api/v1/risk-analytics/var/monte-carlo",
            json=var_data,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HFT risk calculation failed: {response.status_code}")


class ComplianceOfficer(HttpUser):
    """Simulates compliance officer workload"""
    
    wait_time = between(5, 15)  # Slower, more thoughtful operations
    
    def on_start(self):
        """Called when a compliance officer starts"""
        self.tenant_id = f"compliance_tenant_{random.randint(1, 20)}"
        self.user_id = f"compliance_officer_{random.randint(1, 50)}"
        self.access_token = None
        self.login()
    
    def login(self):
        """Login for compliance officer"""
        login_data = {
            "username": f"compliance_{self.user_id}",
            "password": "compliance_password_123",
            "tenant_id": self.tenant_id
        }
        
        with self.client.post("/api/auth/login", json=login_data, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                response.success()
            else:
                response.failure(f"Compliance login failed: {response.status_code}")
                raise RescheduleTask()
    
    @task(8)
    def generate_compliance_report(self):
        """Generate compliance reports"""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Tenant-ID": self.tenant_id,
            "Content-Type": "application/json"
        }
        
        report_data = {
            "report_type": random.choice(["cftc", "emir", "gdpr", "dfsa"]),
            "region": random.choice(["us", "eu", "middle_east"]),
            "period_start": "2024-01-01T00:00:00Z",
            "period_end": "2024-01-31T23:59:59Z"
        }
        
        with self.client.post(
            "/api/v1/compliance/report",
            json=report_data,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Compliance report failed: {response.status_code}")
    
    @task(6)
    def check_compliance_status(self):
        """Check compliance status"""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Tenant-ID": self.tenant_id
        }
        
        with self.client.get(
            "/api/v1/compliance/status",
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Compliance status failed: {response.status_code}")
    
    @task(4)
    def get_compliance_history(self):
        """Get compliance history"""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Tenant-ID": self.tenant_id
        }
        
        with self.client.get(
            "/api/v1/compliance/history",
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Compliance history failed: {response.status_code}")


# Event handlers for custom metrics
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Track custom metrics for requests"""
    if exception:
        print(f"Request failed: {name} - {exception}")
    else:
        print(f"Request succeeded: {name} - {response_time}ms")


@events.user_error.add_listener
def on_user_error(user_instance, exception, tb, **kwargs):
    """Track user errors"""
    print(f"User error: {exception}")


# Load test configuration
class LoadTestConfig:
    """Configuration for load testing"""
    
    # User weights (percentage of total users)
    USER_WEIGHTS = {
        "QuantaEnergiUser": 70,      # 70% regular traders
        "HighFrequencyTrader": 20,   # 20% HFT traders
        "ComplianceOfficer": 10      # 10% compliance officers
    }
    
    # Target scenarios
    SCENARIOS = {
        "normal_load": {
            "users": 100,
            "spawn_rate": 10,
            "duration": "10m"
        },
        "high_load": {
            "users": 500,
            "spawn_rate": 50,
            "duration": "5m"
        },
        "peak_load": {
            "users": 1000,
            "spawn_rate": 100,
            "duration": "3m"
        },
        "stress_test": {
            "users": 2000,
            "spawn_rate": 200,
            "duration": "2m"
        }
    }


# Example usage:
# locust -f locustfile.py --host=http://localhost:8000 --users=1000 --spawn-rate=100 --run-time=10m
# locust -f locustfile.py --host=http://localhost:8000 --users=500 --spawn-rate=50 --headless --run-time=5m
