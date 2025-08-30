import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app

class TestWebSocket:
    """Test WebSocket endpoints and real-time functionality"""
    
    def test_websocket_market_endpoint_exists(self):
        """Test that WebSocket market endpoint is available"""
        client = TestClient(app)
        
        # Check if the endpoint exists in the app routes
        websocket_routes = [route for route in app.routes if hasattr(route, 'path') and 'ws' in route.path]
        assert len(websocket_routes) > 0
        
        # Check for specific WebSocket endpoints
        ws_paths = [route.path for route in websocket_routes]
        assert "/ws/market" in ws_paths
        assert "/ws/trades/{user_id}" in ws_paths
    
    def test_websocket_market_route_configuration(self):
        """Test WebSocket market route configuration"""
        # Find the market WebSocket route
        market_ws_route = None
        for route in app.routes:
            if hasattr(route, 'path') and route.path == "/ws/market":
                market_ws_route = route
                break
        
        assert market_ws_route is not None
        assert hasattr(market_ws_route, 'endpoint')
    
    def test_websocket_trades_route_configuration(self):
        """Test WebSocket trades route configuration"""
        # Find the trades WebSocket route
        trades_ws_route = None
        for route in app.routes:
            if hasattr(route, 'path') and "/ws/trades/" in route.path:
                trades_ws_route = route
                break
        
        assert trades_ws_route is not None
        assert hasattr(trades_ws_route, 'endpoint')
    
    def test_websocket_endpoint_names(self):
        """Test WebSocket endpoint function names"""
        # Check that the WebSocket functions exist
        assert hasattr(app, 'websocket_market_endpoint')
        assert hasattr(app, 'websocket_trades_endpoint')
    
    def test_websocket_async_functions(self):
        """Test that WebSocket functions are async"""
        import inspect
        
        # Check if the WebSocket functions are async
        market_func = getattr(app, 'websocket_market_endpoint', None)
        trades_func = getattr(app, 'websocket_trades_endpoint', None)
        
        if market_func:
            assert inspect.iscoroutinefunction(market_func)
        if trades_func:
            assert inspect.iscoroutinefunction(trades_func)

class TestWebSocketIntegration:
    """Test WebSocket integration with the application"""
    
    def test_websocket_in_app_routes(self):
        """Test that WebSocket routes are properly included in the app"""
        # Get all routes
        all_routes = [route for route in app.routes if hasattr(route, 'path')]
        
        # Check for WebSocket routes
        ws_routes = [route for route in all_routes if 'ws' in route.path]
        assert len(ws_routes) >= 2  # At least market and trades endpoints
        
        # Verify route types
        for route in ws_routes:
            assert hasattr(route, 'endpoint')
    
    def test_websocket_route_methods(self):
        """Test WebSocket route HTTP methods"""
        # WebSocket routes should not have HTTP methods
        for route in app.routes:
            if hasattr(route, 'path') and 'ws' in route.path:
                # WebSocket routes are handled differently than HTTP routes
                assert hasattr(route, 'endpoint')
    
    def test_websocket_app_integration(self):
        """Test that WebSocket endpoints are properly integrated with the FastAPI app"""
        # Check app metadata
        assert app.title == "EnergyOpti-Pro: Disruptive Energy Trading Platform"
        
        # Check that WebSocket routes are accessible
        ws_routes = [route for route in app.routes if hasattr(route, 'path') and 'ws' in route.path]
        assert len(ws_routes) > 0
        
        # Verify each WebSocket route has proper configuration
        for route in ws_routes:
            assert hasattr(route, 'endpoint')
            assert callable(route.endpoint)
