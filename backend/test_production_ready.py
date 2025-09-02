"""
Comprehensive Test for Production-Ready Components
QuantaEnergi Post-Phase 3: Production Readiness & Market Launch
"""

import sys
import traceback
from datetime import datetime, timedelta
import warnings
import asyncio
import requests
import json
import time
warnings.filterwarnings('ignore')

def test_health_endpoints():
    """Test health check endpoints"""
    print("\n🏥 Testing Health Endpoints...")
    
    try:
        # Test basic health check
        response = requests.get("http://localhost:8000/v1/health/")
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        
        data = response.json()
        assert "status" in data, "Health status missing"
        assert "health_checks" in data, "Health checks missing"
        
        print("✅ Basic health check working")
        
        # Test readiness probe
        response = requests.get("http://localhost:8000/v1/health/ready")
        assert response.status_code == 200, f"Readiness check failed: {response.status_code}"
        
        data = response.json()
        assert data["status"] == "ready", "Readiness status incorrect"
        
        print("✅ Readiness probe working")
        
        # Test liveness probe
        response = requests.get("http://localhost:8000/v1/health/live")
        assert response.status_code == 200, f"Liveness check failed: {response.status_code}"
        
        data = response.json()
        assert data["status"] == "alive", "Liveness status incorrect"
        
        print("✅ Liveness probe working")
        
        # Test detailed health check
        response = requests.get("http://localhost:8000/v1/health/detailed")
        assert response.status_code == 200, f"Detailed health check failed: {response.status_code}"
        
        data = response.json()
        assert "health_score" in data, "Health score missing"
        assert "detailed_checks" in data, "Detailed checks missing"
        
        print("✅ Detailed health check working")
        
        # Test metrics endpoint
        response = requests.get("http://localhost:8000/v1/health/metrics")
        assert response.status_code == 200, f"Health metrics failed: {response.status_code}"
        
        data = response.json()
        assert "metrics" in data, "Health metrics missing"
        
        print("✅ Health metrics working")
        
        print("🎉 Health Endpoints: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Health endpoints test failed: {e}")
        traceback.print_exc()
        return False

def test_metrics_endpoints():
    """Test metrics endpoints"""
    print("\n📊 Testing Metrics Endpoints...")
    
    try:
        # Test Prometheus metrics
        response = requests.get("http://localhost:8000/v1/metrics/")
        assert response.status_code == 200, f"Prometheus metrics failed: {response.status_code}"
        
        content = response.text
        assert "quantaenergi_" in content, "Prometheus metrics not found"
        assert "HELP" in content, "Prometheus help text missing"
        
        print("✅ Prometheus metrics working")
        
        # Test metrics summary
        response = requests.get("http://localhost:8000/v1/metrics/summary")
        assert response.status_code == 200, f"Metrics summary failed: {response.status_code}"
        
        data = response.json()
        assert "metrics" in data, "Metrics data missing"
        assert "summary" in data, "Metrics summary missing"
        
        print("✅ Metrics summary working")
        
        # Test metrics health
        response = requests.get("http://localhost:8000/v1/metrics/health")
        assert response.status_code == 200, f"Metrics health failed: {response.status_code}"
        
        data = response.json()
        assert data["status"] == "healthy", "Metrics health status incorrect"
        
        print("✅ Metrics health working")
        
        # Test metrics update
        update_data = {
            "trading_volume": 1000000.0,
            "active_users": 25,
            "error": False
        }
        
        response = requests.post("http://localhost:8000/v1/metrics/update", json=update_data)
        assert response.status_code == 200, f"Metrics update failed: {response.status_code}"
        
        data = response.json()
        assert data["status"] == "success", "Metrics update status incorrect"
        
        print("✅ Metrics update working")
        
        print("🎉 Metrics Endpoints: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Metrics endpoints test failed: {e}")
        traceback.print_exc()
        return False

def test_authentication_endpoints():
    """Test authentication endpoints"""
    print("\n🔐 Testing Authentication Endpoints...")
    
    try:
        # Test user registration
        user_data = {
            "username": "testuser",
            "email": "test@quantaenergi.com",
            "password": "testpass123",
            "full_name": "Test User",
            "company": "Test Corp",
            "role": "trader"
        }
        
        response = requests.post("http://localhost:8000/v1/auth/register", json=user_data)
        assert response.status_code == 200, f"User registration failed: {response.status_code}"
        
        data = response.json()
        assert data["username"] == "testuser", "Username not set correctly"
        assert data["email"] == "test@quantaenergi.com", "Email not set correctly"
        
        print("✅ User registration working")
        
        # Test user login
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        response = requests.post("http://localhost:8000/v1/auth/login", json=login_data)
        assert response.status_code == 200, f"User login failed: {response.status_code}"
        
        data = response.json()
        assert "access_token" in data, "Access token missing"
        assert "refresh_token" in data, "Refresh token missing"
        assert "user" in data, "User data missing"
        
        access_token = data["access_token"]
        refresh_token = data["refresh_token"]
        
        print("✅ User login working")
        
        # Test get current user profile
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get("http://localhost:8000/v1/auth/me", headers=headers)
        assert response.status_code == 200, f"Get profile failed: {response.status_code}"
        
        data = response.json()
        assert data["username"] == "admin", "Profile username incorrect"
        
        print("✅ Get profile working")
        
        # Test update user profile
        profile_update = {
            "full_name": "Updated Admin Name",
            "company": "Updated Company"
        }
        
        response = requests.put("http://localhost:8000/v1/auth/me", json=profile_update, headers=headers)
        assert response.status_code == 200, f"Profile update failed: {response.status_code}"
        
        data = response.json()
        assert data["full_name"] == "Updated Admin Name", "Profile update not applied"
        
        print("✅ Profile update working")
        
        # Test change password
        password_data = {
            "current_password": "admin123",
            "new_password": "newadmin123"
        }
        
        response = requests.post("http://localhost:8000/v1/auth/change-password", json=password_data, headers=headers)
        assert response.status_code == 200, f"Password change failed: {response.status_code}"
        
        print("✅ Password change working")
        
        # Test refresh token
        refresh_data = {
            "refresh_token": refresh_token
        }
        
        response = requests.post("http://localhost:8000/v1/auth/refresh", json=refresh_data)
        assert response.status_code == 200, f"Token refresh failed: {response.status_code}"
        
        data = response.json()
        assert "access_token" in data, "New access token missing"
        
        print("✅ Token refresh working")
        
        # Test logout
        logout_data = {
            "token": access_token
        }
        
        response = requests.post("http://localhost:8000/v1/auth/logout", json=logout_data)
        assert response.status_code == 200, f"Logout failed: {response.status_code}"
        
        print("✅ Logout working")
        
        # Test authentication health
        response = requests.get("http://localhost:8000/v1/auth/health")
        assert response.status_code == 200, f"Auth health failed: {response.status_code}"
        
        data = response.json()
        assert data["status"] == "healthy", "Auth health status incorrect"
        
        print("✅ Authentication health working")
        
        print("🎉 Authentication Endpoints: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Authentication endpoints test failed: {e}")
        traceback.print_exc()
        return False

def test_production_configuration():
    """Test production configuration"""
    print("\n⚙️ Testing Production Configuration...")
    
    try:
        # Import production config
        from app.core.production_config import settings, get_config_summary, validate_settings
        
        # Test settings loading
        assert settings.APP_NAME == "QuantaEnergi", "App name incorrect"
        assert settings.APP_VERSION == "4.0.0", "App version incorrect"
        assert settings.APP_ENV == "production", "App environment incorrect"
        
        print("✅ Production settings loaded")
        
        # Test configuration validation
        validation = validate_settings()
        assert isinstance(validation, dict), "Validation result not a dict"
        
        print("✅ Configuration validation working")
        
        # Test configuration summary
        summary = get_config_summary()
        assert isinstance(summary, dict), "Config summary not a dict"
        assert "app_name" in summary, "App name missing from summary"
        assert "validation_score" in summary, "Validation score missing"
        
        print("✅ Configuration summary working")
        
        # Test environment-specific settings
        assert settings.DATABASE_URL.startswith("postgresql://"), "Database URL incorrect"
        assert settings.REDIS_URL.startswith("redis://"), "Redis URL incorrect"
        assert settings.SECRET_KEY, "Secret key not set"
        
        print("✅ Environment-specific settings correct")
        
        print("🎉 Production Configuration: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Production configuration test failed: {e}")
        traceback.print_exc()
        return False

def test_api_integration():
    """Test API integration"""
    print("\n🔗 Testing API Integration...")
    
    try:
        # Test main API health
        response = requests.get("http://localhost:8000/health")
        assert response.status_code == 200, f"Main API health failed: {response.status_code}"
        
        data = response.json()
        assert data["version"] == "4.0.0", "API version incorrect"
        assert "Post-Phase 3" in data["phase"], "API phase incorrect"
        
        print("✅ Main API health working")
        
        # Test API v1 health
        response = requests.get("http://localhost:8000/v1/health/")
        assert response.status_code == 200, f"API v1 health failed: {response.status_code}"
        
        data = response.json()
        assert "health_checks" in data, "Health checks missing"
        
        print("✅ API v1 health working")
        
        # Test metrics integration
        response = requests.get("http://localhost:8000/v1/metrics/")
        assert response.status_code == 200, f"Metrics integration failed: {response.status_code}"
        
        print("✅ Metrics integration working")
        
        # Test authentication integration
        response = requests.get("http://localhost:8000/v1/auth/health")
        assert response.status_code == 200, f"Auth integration failed: {response.status_code}"
        
        print("✅ Authentication integration working")
        
        print("🎉 API Integration: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ API integration test failed: {e}")
        traceback.print_exc()
        return False

def test_production_requirements():
    """Test production requirements"""
    print("\n🔧 Testing Production Requirements...")
    
    try:
        # Test required packages
        import fastapi
        import pydantic
        import psutil
        import jwt
        import asyncio
        
        print("✅ Core packages available")
        
        # Test optional packages
        try:
            import prometheus_client
            print("✅ Prometheus client available")
        except ImportError:
            print("⚠️ Prometheus client not available")
        
        try:
            import redis
            print("✅ Redis client available")
        except ImportError:
            print("⚠️ Redis client not available")
        
        try:
            import psycopg2
            print("✅ PostgreSQL client available")
        except ImportError:
            print("⚠️ PostgreSQL client not available")
        
        # Test configuration files
        import os
        assert os.path.exists("env.production.template"), "Production env template missing"
        assert os.path.exists("app/core/production_config.py"), "Production config missing"
        
        print("✅ Configuration files available")
        
        # Test API structure
        assert os.path.exists("app/api/v1/health.py"), "Health API missing"
        assert os.path.exists("app/api/v1/metrics.py"), "Metrics API missing"
        assert os.path.exists("app/api/v1/auth.py"), "Auth API missing"
        assert os.path.exists("app/middleware/auth.py"), "Auth middleware missing"
        
        print("✅ API structure correct")
        
        print("🎉 Production Requirements: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Production requirements test failed: {e}")
        traceback.print_exc()
        return False

def test_performance_metrics():
    """Test performance metrics"""
    print("\n⚡ Testing Performance Metrics...")
    
    try:
        # Test health check performance
        start_time = time.time()
        response = requests.get("http://localhost:8000/v1/health/")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        assert response_time < 1.0, f"Health check too slow: {response_time:.3f}s"
        
        print(f"✅ Health check performance: {response_time:.3f}s")
        
        # Test metrics performance
        start_time = time.time()
        response = requests.get("http://localhost:8000/v1/metrics/")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200, f"Metrics failed: {response.status_code}"
        assert response_time < 0.5, f"Metrics too slow: {response_time:.3f}s"
        
        print(f"✅ Metrics performance: {response_time:.3f}s")
        
        # Test authentication performance
        start_time = time.time()
        response = requests.get("http://localhost:8000/v1/auth/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200, f"Auth health failed: {response.status_code}"
        assert response_time < 0.3, f"Auth health too slow: {response_time:.3f}s"
        
        print(f"✅ Auth health performance: {response_time:.3f}s")
        
        print("🎉 Performance Metrics: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Performance metrics test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main test execution"""
    print("🚀 QuantaEnergi: Production-Ready Components Testing")
    print("=" * 70)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = []
    
    # Test all production-ready components
    test_results.append(("Production Requirements", test_production_requirements()))
    test_results.append(("Production Configuration", test_production_configuration()))
    test_results.append(("Health Endpoints", test_health_endpoints()))
    test_results.append(("Metrics Endpoints", test_metrics_endpoints()))
    test_results.append(("Authentication Endpoints", test_authentication_endpoints()))
    test_results.append(("API Integration", test_api_integration()))
    test_results.append(("Performance Metrics", test_performance_metrics()))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 70)
    
    passed = 0
    total = len(test_results)
    
    for component_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{component_name:<35} {status}")
        if result:
            passed += 1
    
    print("=" * 70)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL PRODUCTION COMPONENTS ARE READY! 🎉")
        print("QuantaEnergi is ready for production deployment and market launch!")
    else:
        print(f"\n⚠️ {total - passed} component(s) need attention before production deployment")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
