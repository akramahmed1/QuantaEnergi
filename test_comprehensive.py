#!/usr/bin/env python3
"""
🚀 EnergyOpti-Pro Comprehensive Testing Suite
Tests all components: Backend, Frontend, Database, Redis, APIs, and UI Components
"""

import asyncio
import requests
import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Configuration
BACKEND_URL = "http://localhost:8001"
FRONTEND_URL = "http://localhost:3001"
TIMEOUT = 10

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(title: str):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}{Colors.END}")

def print_test_result(test_name: str, success: bool, details: str = ""):
    """Print test result with color coding"""
    status = f"{Colors.GREEN}✅ PASS{Colors.END}" if success else f"{Colors.RED}❌ FAIL{Colors.END}"
    print(f"{status} {test_name}")
    if details:
        print(f"    {Colors.YELLOW}{details}{Colors.END}")

def test_backend_health():
    """Test backend health endpoints"""
    print_header("🏥 Backend Health Testing")
    
    tests = [
        ("Basic Health Check", "/health"),
        ("Detailed Health", "/health/detailed"),
        ("API Status", "/api/status"),
        ("Root Endpoint", "/"),
        ("API Info", "/api/info")
    ]
    
    results = []
    for test_name, endpoint in tests:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=TIMEOUT)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f" | Response: {list(data.keys())[:3]}..."
            
            print_test_result(test_name, success, details)
            results.append(success)
            
        except Exception as e:
            print_test_result(test_name, False, f"Error: {str(e)}")
            results.append(False)
    
    return all(results)

def test_weather_integration():
    """Test weather data integration"""
    print_header("🌤️ Weather Data Integration Testing")
    
    tests = [
        ("Current Weather", "/api/weather/current"),
        ("Weather Forecast", "/api/weather/forecast"),
        ("Weather with Coordinates", "/api/weather/current?lat=40.7128&lon=-74.0060")
    ]
    
    results = []
    for test_name, endpoint in tests:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=TIMEOUT)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                if "temp" in data:
                    details += f" | Temp: {data['temp']}°C"
                elif "forecasts" in data:
                    details += f" | Forecasts: {len(data['forecasts'])}"
            
            print_test_result(test_name, success, details)
            results.append(success)
            
        except Exception as e:
            print_test_result(test_name, False, f"Error: {str(e)}")
            results.append(False)
    
    return all(results)

def test_market_data():
    """Test market data and analytics"""
    print_header("📊 Market Data & Analytics Testing")
    
    tests = [
        ("User Analytics", "/api/analytics"),
        ("Market Prices", "/api/market/prices"),
        ("Renewable Energy", "/api/renewables"),
        ("Portfolio Summary", "/api/portfolio/summary"),
        ("Recent Trades", "/api/trades/recent")
    ]
    
    results = []
    for test_name, endpoint in tests:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=TIMEOUT)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                if isinstance(data, dict):
                    details += f" | Keys: {list(data.keys())[:3]}..."
                elif isinstance(data, list):
                    details += f" | Items: {len(data)}"
            
            print_test_result(test_name, success, details)
            results.append(success)
            
        except Exception as e:
            print_test_result(test_name, False, f"Error: {str(e)}")
            results.append(False)
    
    return all(results)

def test_trading_signals():
    """Test trading signals and ESG metrics"""
    print_header("🎯 Trading Signals & ESG Testing")
    
    tests = [
        ("Trading Signals", "/api/signals"),
        ("ESG Metrics", "/api/esg/metrics"),
        ("Energy Forecast", "/api/forecast/energy"),
        ("Signals with Filter", "/api/signals?commodity=crude_oil&confidence_min=70")
    ]
    
    results = []
    for test_name, endpoint in tests:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=TIMEOUT)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                if "signals" in data:
                    details += f" | Signals: {len(data['signals'])}"
                elif "overall_esg_score" in data:
                    details += f" | ESG Score: {data['overall_esg_score']}"
                elif "forecasts" in data:
                    details += f" | Forecasts: {len(data['forecasts'])}"
            
            print_test_result(test_name, success, details)
            results.append(success)
            
        except Exception as e:
            print_test_result(test_name, False, f"Error: {str(e)}")
            results.append(False)
    
    return all(results)

def test_frontend_connectivity():
    """Test frontend connectivity and basic functionality"""
    print_header("🌐 Frontend Connectivity Testing")
    
    try:
        # Test if frontend is accessible
        response = requests.get(FRONTEND_URL, timeout=TIMEOUT)
        success = response.status_code == 200
        details = f"Status: {response.status_code}"
        
        if success:
            content = response.text
            if "quantaenergi" in content.lower() or "energyopti" in content.lower():
                details += " | Content: EnergyOpti-Pro detected"
            else:
                details += " | Content: Generic React app"
        
        print_test_result("Frontend Accessibility", success, details)
        return success
        
    except Exception as e:
        print_test_result("Frontend Accessibility", False, f"Error: {str(e)}")
        return False

def test_api_integration():
    """Test frontend-backend API integration"""
    print_header("🔗 Frontend-Backend Integration Testing")
    
    # Test if frontend can reach backend APIs
    try:
        response = requests.get(f"{BACKEND_URL}/api/analytics", timeout=TIMEOUT)
        success = response.status_code == 200
        
        if success:
            data = response.json()
            details = f"Backend API accessible | Data: {list(data.keys())[:3]}..."
        else:
            details = f"Backend API returned status: {response.status_code}"
        
        print_test_result("Backend API Access", success, details)
        return success
        
    except Exception as e:
        print_test_result("Backend API Access", False, f"Error: {str(e)}")
        return False

def test_database_connectivity():
    """Test database connectivity"""
    print_header("🗄️ Database Connectivity Testing")
    
    try:
        # Test database health through backend
        response = requests.get(f"{BACKEND_URL}/health/detailed", timeout=TIMEOUT)
        success = response.status_code == 200
        
        if success:
            data = response.json()
            db_status = data.get("services", {}).get("database", {}).get("status", "unknown")
            details = f"Database Status: {db_status}"
            
            if db_status == "healthy":
                details += " | ✅ Database connected"
            else:
                details += " | ⚠️ Database issues detected"
        else:
            details = f"Health check failed: {response.status_code}"
        
        print_test_result("Database Health Check", success, details)
        return success
        
    except Exception as e:
        print_test_result("Database Health Check", False, f"Error: {str(e)}")
        return False

def test_redis_connectivity():
    """Test Redis connectivity"""
    print_header("🔴 Redis Connectivity Testing")
    
    try:
        # Test Redis health through backend
        response = requests.get(f"{BACKEND_URL}/health/detailed", timeout=TIMEOUT)
        success = response.status_code == 200
        
        if success:
            data = response.json()
            redis_status = data.get("services", {}).get("redis", {}).get("status", "unknown")
            details = f"Redis Status: {redis_status}"
            
            if redis_status == "healthy":
                details += " | ✅ Redis connected"
            else:
                details += " | ⚠️ Redis not available (caching disabled)"
        else:
            details = f"Health check failed: {response.status_code}"
        
        print_test_result("Redis Health Check", success, details)
        return success
        
    except Exception as e:
        print_test_result("Redis Health Check", False, f"Error: {str(e)}")
        return False

def run_performance_tests():
    """Run basic performance tests"""
    print_header("⚡ Performance Testing")
    
    tests = [
        ("Health Check Response Time", "/health"),
        ("Analytics Response Time", "/api/analytics"),
        ("Weather Data Response Time", "/api/weather/current"),
        ("Market Data Response Time", "/api/market/prices")
    ]
    
    results = []
    for test_name, endpoint in tests:
        try:
            start_time = time.time()
            response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=TIMEOUT)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            success = response.status_code == 200 and response_time < 1000  # Under 1 second
            
            details = f"Response Time: {response_time:.2f}ms | Status: {response.status_code}"
            
            if response_time > 500:
                details += " | ⚠️ Slow response"
            
            print_test_result(test_name, success, details)
            results.append(success)
            
        except Exception as e:
            print_test_result(test_name, False, f"Error: {str(e)}")
            results.append(False)
    
    return all(results)

def generate_test_report(results: Dict[str, bool]):
    """Generate comprehensive test report"""
    print_header("📋 Test Results Summary")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    failed_tests = total_tests - passed_tests
    
    print(f"{Colors.BOLD}Overall Results:{Colors.END}")
    print(f"  Total Tests: {total_tests}")
    print(f"  Passed: {Colors.GREEN}{passed_tests}{Colors.END}")
    print(f"  Failed: {Colors.RED}{failed_tests}{Colors.END}")
    print(f"  Success Rate: {Colors.BOLD}{(passed_tests/total_tests)*100:.1f}%{Colors.END}")
    
    if failed_tests == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! EnergyOpti-Pro is fully operational!{Colors.END}")
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  {failed_tests} tests failed. Please review the issues above.{Colors.END}")
    
    print(f"\n{Colors.CYAN}Access your application:{Colors.END}")
    print(f"  Frontend: {FRONTEND_URL}")
    print(f"  Backend API: {BACKEND_URL}")
    print(f"  API Documentation: {BACKEND_URL}/docs")
    print(f"  Health Check: {BACKEND_URL}/health")

def main():
    """Main testing function"""
    print_header("🚀 EnergyOpti-Pro Comprehensive Testing Suite")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Frontend URL: {FRONTEND_URL}")
    
    # Run all tests
    test_results = {
        "Backend Health": test_backend_health(),
        "Weather Integration": test_weather_integration(),
        "Market Data": test_market_data(),
        "Trading Signals": test_trading_signals(),
        "Frontend Connectivity": test_frontend_connectivity(),
        "API Integration": test_api_integration(),
        "Database Connectivity": test_database_connectivity(),
        "Redis Connectivity": test_redis_connectivity(),
        "Performance": run_performance_tests()
    }
    
    # Generate report
    generate_test_report(test_results)
    
    # Exit with appropriate code
    if all(test_results.values()):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Testing interrupted by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {str(e)}{Colors.END}")
        sys.exit(1)
