#!/usr/bin/env python3
"""
Simple test script to verify local EnergyOpti-Pro functionality
"""

import requests
import time
import sys
import os

def test_backend_health():
    """Test backend health endpoint"""
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend health check passed")
            data = response.json()
            print(f"   Status: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend connection failed - server not running")
        return False
    except Exception as e:
        print(f"❌ Backend test error: {e}")
        return False

def test_frontend():
    """Test frontend accessibility"""
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend accessibility check passed")
            return True
        else:
            print(f"❌ Frontend accessibility failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("⚠️  Frontend connection failed - server not running")
        return False
    except Exception as e:
        print(f"❌ Frontend test error: {e}")
        return False

def test_api_endpoints():
    """Test basic API endpoints"""
    endpoints = [
        "/api/auth/register",
        "/api/auth/login",
        "/api/prices",
        "/api/renewables"
    ]
    
    print("\n🔍 Testing API endpoints...")
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
            if response.status_code in [200, 401, 422, 404]:  # Expected responses
                print(f"✅ {endpoint}: {response.status_code}")
            else:
                print(f"⚠️  {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")

def main():
    """Main test function"""
    print("🚀 EnergyOpti-Pro Local Test Suite")
    print("=" * 40)
    
    # Test backend
    print("\n🔧 Testing Backend...")
    backend_ok = test_backend_health()
    
    # Test frontend
    print("\n🎨 Testing Frontend...")
    frontend_ok = test_frontend()
    
    # Test API endpoints if backend is running
    if backend_ok:
        test_api_endpoints()
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Summary:")
    print(f"   Backend: {'✅ Working' if backend_ok else '❌ Failed'}")
    print(f"   Frontend: {'✅ Working' if frontend_ok else '❌ Failed'}")
    
    if backend_ok and frontend_ok:
        print("\n🎉 All tests passed! Your local setup is working.")
        print("\n🌐 Access your application:")
        print("   Backend API: http://localhost:8000")
        print("   Frontend: http://localhost:3000")
        print("   API Docs: http://localhost:8000/docs")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        print("\n💡 Troubleshooting tips:")
        if not backend_ok:
            print("   - Start backend: cd backend && uvicorn app.main:app --reload")
        if not frontend_ok:
            print("   - Start frontend: cd frontend && npm run dev")
        print("   - Check logs for error messages")
        print("   - Verify environment configuration")

if __name__ == "__main__":
    main()
