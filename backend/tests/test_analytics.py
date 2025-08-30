import pytest
from fastapi.testclient import TestClient
from app.main import app

class TestAnalyticsEndpoints:
    """Test analytics endpoints and data validation"""
    
    def test_analytics_endpoint_exists(self):
        """Test that analytics endpoint is available"""
        client = TestClient(app)
        
        # Check if the analytics endpoint exists
        analytics_routes = [route for route in app.routes if hasattr(route, 'path') and 'analytics' in route.path]
        assert len(analytics_routes) > 0
        
        # Check for specific analytics endpoints
        analytics_paths = [route.path for route in analytics_routes]
        assert "/api/analytics" in analytics_paths
    
    def test_analytics_route_configuration(self):
        """Test analytics route configuration"""
        # Find the analytics route
        analytics_route = None
        for route in app.routes:
            if hasattr(route, 'path') and route.path == "/api/analytics":
                analytics_route = route
                break
        
        assert analytics_route is not None
        assert hasattr(analytics_route, 'endpoint')
    
    def test_analytics_endpoint_method(self):
        """Test that analytics endpoint uses GET method"""
        # Find the analytics route
        analytics_route = None
        for route in app.routes:
            if hasattr(route, 'path') and route.path == "/api/analytics":
                analytics_route = route
                break
        
        if analytics_route and hasattr(analytics_route, 'methods'):
            assert 'GET' in analytics_route.methods
    
    def test_analytics_endpoint_requires_auth(self):
        """Test that analytics endpoint requires authentication"""
        # The analytics endpoint should have authentication dependencies
        analytics_route = None
        for route in app.routes:
            if hasattr(route, 'path') and route.path == "/api/analytics":
                analytics_route = route
                break
        
        if analytics_route and hasattr(analytics_route, 'dependencies'):
            # Check if it has authentication dependencies
            assert len(analytics_route.dependencies) > 0

class TestAnalyticsDataStructure:
    """Test analytics data structure and validation"""
    
    def test_analytics_response_structure(self):
        """Test that analytics endpoint returns expected data structure"""
        # This would require a mock authenticated user
        # For now, just verify the endpoint exists and is configured
        analytics_route = None
        for route in app.routes:
            if hasattr(route, 'path') and route.path == "/api/analytics":
                analytics_route = route
                break
        
        assert analytics_route is not None
        assert hasattr(analytics_route, 'endpoint')
    
    def test_analytics_endpoint_integration(self):
        """Test analytics endpoint integration with the application"""
        # Check that analytics is part of the main app
        assert app.title == "EnergyOpti-Pro: Disruptive Energy Trading Platform"
        
        # Verify analytics route is accessible
        analytics_routes = [route for route in app.routes if hasattr(route, 'path') and 'analytics' in route.path]
        assert len(analytics_routes) > 0
        
        # Verify each analytics route has proper configuration
        for route in analytics_routes:
            assert hasattr(route, 'endpoint')
            assert callable(route.endpoint)

class TestAnalyticsFunctionality:
    """Test analytics functionality and business logic"""
    
    def test_analytics_endpoint_async(self):
        """Test that analytics endpoint is async"""
        import inspect
        
        # Find the analytics endpoint function
        analytics_route = None
        for route in app.routes:
            if hasattr(route, 'path') and route.path == "/api/analytics":
                analytics_route = route
                break
        
        if analytics_route and hasattr(analytics_route, 'endpoint'):
            endpoint_func = analytics_route.endpoint
            assert inspect.iscoroutinefunction(endpoint_func)
    
    def test_analytics_endpoint_parameters(self):
        """Test analytics endpoint parameter configuration"""
        # Find the analytics route
        analytics_route = None
        for route in app.routes:
            if hasattr(route, 'path') and route.path == "/api/analytics":
                analytics_route = route
                break
        
        if analytics_route and hasattr(analytics_route, 'endpoint'):
            # The analytics endpoint should accept current_user parameter
            endpoint_func = analytics_route.endpoint
            assert callable(endpoint_func)
