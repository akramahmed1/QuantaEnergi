#!/usr/bin/env python3
"""
QuantaEnergi End-to-End Test Script
Tests all components: Backend, Frontend, Weather API, Database
"""

import requests
import time
import json

def test_backend_health():
    """Test backend health endpoint"""
    print("🔍 Testing Backend Health...")
    try:
        response = requests.get("http://localhost:8001/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend Health: {data}")
            return True
        else:
            print(f"❌ Backend Health Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend Health Error: {e}")
        return False

def test_weather_current():
    """Test current weather endpoint"""
    print("\n🌤️ Testing Current Weather...")
    try:
        response = requests.get("http://localhost:8001/api/weather/current?lat=33.44&lon=-94.04", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Current Weather: {data['temp']}°C, {data['description']}")
            return True
        else:
            print(f"❌ Weather API Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Weather API Error: {e}")
        return False

def test_weather_forecast():
    """Test weather forecast endpoint"""
    print("\n📅 Testing Weather Forecast...")
    try:
        response = requests.get("http://localhost:8001/api/weather/forecast?lat=33.44&lon=-94.04", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Weather Forecast: {len(data['forecasts'])} forecasts loaded")
            return True
        else:
            print(f"❌ Forecast API Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Forecast API Error: {e}")
        return False

def test_market_prices():
    """Test market prices endpoint"""
    print("\n📊 Testing Market Prices...")
    try:
        response = requests.get("http://localhost:8001/api/market/prices", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Market Prices: {len(data)} commodities loaded")
            return True
        else:
            print(f"❌ Market Prices Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Market Prices Error: {e}")
        return False

def test_frontend():
    """Test frontend accessibility"""
    print("\n🌐 Testing Frontend...")
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend accessible")
            return True
        else:
            print(f"❌ Frontend Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend Error: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("\n🗄️ Testing Database Connection...")
    try:
        # Test if PostgreSQL is listening
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 5432))
        sock.close()
        
        if result == 0:
            print("✅ PostgreSQL is running on port 5432")
            return True
        else:
            print("❌ PostgreSQL not accessible on port 5432")
            return False
    except Exception as e:
        print(f"❌ Database Test Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 QuantaEnergi End-to-End Testing")
    print("=" * 50)
    
    tests = [
        ("Backend Health", test_backend_health),
        ("Current Weather", test_weather_current),
        ("Weather Forecast", test_weather_forecast),
        ("Market Prices", test_market_prices),
        ("Frontend", test_frontend),
        ("Database", test_database_connection)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} Test Exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! QuantaEnergi is fully operational!")
        print("\n🌐 Access your application:")
        print("   Frontend: http://localhost:3000")
        print("   Backend API: http://localhost:8001")
        print("   API Docs: http://localhost:8001/docs")
    else:
        print("⚠️ Some tests failed. Check the logs above.")
    
    return passed == total

if __name__ == "__main__":
    main()
