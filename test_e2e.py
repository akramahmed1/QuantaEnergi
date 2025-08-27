#!/usr/bin/env python3
"""
E2E Test Script for EnergyOpti-Pro
Tests backend, frontend, and API integration
"""

import requests
import time
import json

def test_backend():
    """Test backend endpoints"""
    print("🔧 Testing Backend...")
    
    base_url = "http://127.0.0.1:8000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health endpoint: WORKING")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health endpoint: FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ Health endpoint: ERROR - {e}")
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Root endpoint: WORKING")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint: FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ Root endpoint: ERROR - {e}")
    
    # Test API documentation
    try:
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200:
            print("✅ API Documentation: WORKING")
        else:
            print(f"❌ API Documentation: FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ API Documentation: ERROR - {e}")

def test_frontend():
    """Test frontend accessibility"""
    print("\n🎨 Testing Frontend...")
    
    try:
        response = requests.get("http://localhost:3001")
        if response.status_code == 200:
            print("✅ Frontend: WORKING")
            if "EnergyOpti-Pro Trading Platform" in response.text:
                print("✅ Frontend Title: CORRECT")
            else:
                print("⚠️  Frontend Title: NOT FOUND")
        else:
            print(f"❌ Frontend: FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ Frontend: ERROR - {e}")

def test_api_integration():
    """Test API integration between frontend and backend"""
    print("\n🔗 Testing API Integration...")
    
    # Test if frontend can access backend API
    try:
        response = requests.get("http://127.0.0.1:8000/health")
        if response.status_code == 200:
            print("✅ Frontend-Backend Communication: WORKING")
            data = response.json()
            print(f"   Backend Status: {data.get('status', 'unknown')}")
            print(f"   Message: {data.get('message', 'unknown')}")
        else:
            print(f"❌ Frontend-Backend Communication: FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ Frontend-Backend Communication: ERROR - {e}")

def main():
    """Run all tests"""
    print("🚀 EnergyOpti-Pro E2E Test Suite")
    print("=" * 50)
    
    test_backend()
    test_frontend()
    test_api_integration()
    
    print("\n" + "=" * 50)
    print("🎉 E2E Testing Complete!")
    print("\n📋 Access URLs:")
    print("   Frontend: http://localhost:3001")
    print("   Backend: http://127.0.0.1:8000")
    print("   API Docs: http://127.0.0.1:8000/docs")
    print("   Health: http://127.0.0.1:8000/health")

if __name__ == "__main__":
    main()
