#!/usr/bin/env python3
"""
Simple Backend Test Script
"""

import requests
import time
import sys

def test_backend():
    """Test if backend is running"""
    print("🔍 Testing QuantaEnergi Backend...")
    
    # Wait a moment for backend to start
    time.sleep(2)
    
    try:
        # Test health endpoint
        response = requests.get('http://localhost:8000/health', timeout=10)
        if response.status_code == 200:
            print("✅ Backend is running!")
            print(f"   Status: {response.json()}")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running or not accessible")
        return False
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
        return False

def test_auth():
    """Test authentication"""
    print("\n🔐 Testing Authentication...")
    
    try:
        # Test login
        login_data = {
            'username': 'admin',
            'password': 'secret'
        }
        
        response = requests.post(
            'http://localhost:8000/api/v1/login',
            data=login_data,
            timeout=10
        )
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Authentication working!")
            print(f"   Token type: {token_data.get('token_type')}")
            return token_data.get('access_token')
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def test_trade_creation(token):
    """Test trade creation"""
    if not token:
        print("\n⏭️  Skipping trade test - no token")
        return False
        
    print("\n📊 Testing Trade Creation...")
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        trade_data = {
            'commodity': 'electricity',
            'quantity': 100,
            'price': 50.0,
            'trade_type': 'spot'
        }
        
        response = requests.post(
            'http://localhost:8000/api/v1/capture',
            json=trade_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 201:
            trade = response.json()
            print("✅ Trade creation working!")
            print(f"   Trade ID: {trade.get('id')}")
            return True
        else:
            print(f"❌ Trade creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Trade creation error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 QuantaEnergi Backend Test Suite")
    print("=" * 40)
    
    # Test backend health
    if not test_backend():
        print("\n❌ Backend is not running. Please start it with:")
        print("   python -m uvicorn apps.backend.app.main:app --host 0.0.0.0 --port 8000")
        sys.exit(1)
    
    # Test authentication
    token = test_auth()
    
    # Test trade creation
    test_trade_creation(token)
    
    print("\n🎉 Backend test completed!")
    print("\n📋 Next steps:")
    print("   1. Start frontend: cd apps/frontend && npm run dev")
    print("   2. Open browser: http://localhost:5173")
    print("   3. Run E2E tests: python test_e2e_comprehensive.py")

if __name__ == "__main__":
    main()
