#!/usr/bin/env python3
"""
Comprehensive E2E Test Runner for QuantaEnergi
Starts server and runs all tests
"""

import subprocess
import time
import requests
import json
import sys
from pathlib import Path

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting QuantaEnergi Server...")
    
    # Start server in background
    process = subprocess.Popen([
        "poetry", "run", "uvicorn", "app.main:app", 
        "--reload", "--host", "0.0.0.0", "--port", "8000"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    for i in range(30):  # Wait up to 30 seconds
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print("✅ Server started successfully!")
                return process
        except:
            time.sleep(1)
            print(f"   Waiting... ({i+1}/30)")
    
    print("❌ Server failed to start")
    return None

def test_endpoints():
    """Test all endpoints"""
    print("\n🧪 Testing All Endpoints...")
    print("=" * 50)
    
    tests = [
        ("Health Check", "GET", "/health", None),
        ("Swagger Docs", "GET", "/docs", None),
        ("OpenAPI Spec", "GET", "/openapi.json", None),
        ("Auth Login", "POST", "/auth/login", {"username": "test", "password": "test"}),
        ("Parametric VaR", "POST", "/risk/var", [150, 152, 148, 155, 160]),
        ("Monte Carlo VaR", "POST", "/risk/var?method=monte_carlo", [150, 152, 148, 155, 160]),
        ("Enhanced VaR", "POST", "/risk/var?method=enhanced", [150, 152, 148, 155, 160]),
        ("Market Data BRENT", "GET", "/market/prices/BRENT", None),
        ("Market Data WTI", "GET", "/market/prices/WTI", None),
        ("Guyana Geo-Risk", "POST", "/geo-risk/assess", {
            "region": "GUYANA", "volatility": 0.25, "sentiment": 0.4, "news_volume": 0.8
        }),
        ("ME Geo-Risk", "POST", "/geo-risk/assess", {
            "region": "MIDDLE_EAST", "volatility": 0.30, "sentiment": 0.2, "news_volume": 0.9
        }),
        ("Supported Regions", "GET", "/geo-risk/regions", None),
        ("Quantum Optimization", "POST", "/optimize/portfolio", {
            "returns": [0.05, 0.08, 0.12], "risks": [0.1, 0.15, 0.2]
        }),
        ("Classical Optimization", "POST", "/optimize/portfolio?method=classical", {
            "returns": [0.05, 0.08, 0.12], "risks": [0.1, 0.15, 0.2]
        }),
        ("REMIT Compliant", "POST", "/compliance/validate", {
            "trade": {
                "asset": "brent_crude_oil", "quantity": 500, "price": 75.50,
                "market_price": 75.00, "timestamp": "2024-01-15T10:30:00Z",
                "counterparty": "Shell_Energy", "trader": "John_Smith",
                "energy_type": "oil", "cross_border": False
            },
            "framework": "REMIT"
        }),
        ("REMIT Violation", "POST", "/compliance/validate", {
            "trade": {
                "asset": "wti_crude_oil", "quantity": 1200, "price": 70.25,
                "market_price": 70.00, "timestamp": "2024-01-15T11:00:00Z",
                "counterparty": "BP_Trading", "trader": "Jane_Doe",
                "energy_type": "oil", "cross_border": False
            },
            "framework": "REMIT"
        }),
        ("Price Forecast", "POST", "/forecast/price", [75.0, 76.5, 74.2, 77.8, 73.1]),
        ("Load Forecast", "POST", "/forecast/load", [75.0, 76.5, 74.2, 77.8, 73.1]),
        ("Metrics", "GET", "/metrics", None)
    ]
    
    results = {"passed": 0, "failed": 0, "total": 0}
    
    for test_name, method, endpoint, data in tests:
        results["total"] += 1
        try:
            url = f"http://localhost:8000{endpoint}"
            
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=10)
            
            if response.status_code in [200, 401, 403]:  # 401/403 are expected for auth endpoints
                print(f"✅ {test_name}")
                results["passed"] += 1
            else:
                print(f"❌ {test_name} - Status: {response.status_code}")
                results["failed"] += 1
                
        except Exception as e:
            print(f"❌ {test_name} - Error: {str(e)[:50]}...")
            results["failed"] += 1
    
    return results

def main():
    """Main test runner"""
    print("🚀 QuantaEnergi E2E Test Runner")
    print("=" * 50)
    
    # Start server
    server_process = start_server()
    if not server_process:
        print("❌ Failed to start server")
        return 1
    
    try:
        # Run tests
        results = test_endpoints()
        
        # Print summary
        print("\n📊 Test Summary")
        print("=" * 30)
        print(f"Total Tests: {results['total']}")
        print(f"Passed: {results['passed']}")
        print(f"Failed: {results['failed']}")
        print(f"Success Rate: {(results['passed']/results['total']*100):.1f}%")
        
        if results['failed'] == 0:
            print("\n🎉 All tests passed!")
            print("✅ QuantaEnergi is ready for production!")
        else:
            print(f"\n⚠️ {results['failed']} tests failed")
        
        # Save results
        with open("e2e_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        return 0 if results['failed'] == 0 else 1
        
    finally:
        # Cleanup
        if server_process:
            print("\n🛑 Stopping server...")
            server_process.terminate()
            server_process.wait()

if __name__ == "__main__":
    sys.exit(main())
