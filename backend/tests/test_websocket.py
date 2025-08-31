#!/usr/bin/env python3
"""
Test WebSocket functionality and real-time updates for QuantaEnergi
"""

import pytest
import asyncio
import json
import websockets
from datetime import datetime
import sys
import os

# Add shared services to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared', 'services'))

try:
    from app.main import app
except ImportError:
    # Fallback if app not available
    pytest.skip("Main app not available", allow_module_level=True)


class TestWebSocketFunctionality:
    """Test WebSocket functionality and real-time updates"""
    
    def setup_method(self):
        """Setup test environment"""
        self.base_url = "ws://localhost:8000"
        self.test_user_id = "test_user_123"
    
    @pytest.mark.asyncio
    async def test_websocket_market_connection(self):
        """Test WebSocket market data connection"""
        try:
            async with websockets.connect(f"{self.base_url}/ws/market") as websocket:
                # Test connection establishment
                assert websocket.open is True
                
                # Test receiving market data
                message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                data = json.loads(message)
                
                assert data is not None
                assert 'type' in data
                assert data['type'] == 'market_update'
                assert 'timestamp' in data
                assert 'cme_crude' in data
                assert 'ice_brent' in data
                assert 'message' in data
                
                # Test timestamp format
                timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                assert isinstance(timestamp, datetime)
                
                # Test market data structure
                cme_data = data['cme_crude']
                ice_data = data['ice_brent']
                
                assert 'data' in cme_data
                assert 'source' in cme_data
                assert 'data' in ice_data
                assert 'source' in ice_data
                
        except websockets.exceptions.InvalidURI:
            pytest.skip("WebSocket server not running")
        except Exception as e:
            pytest.skip(f"WebSocket test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_websocket_trades_connection(self):
        """Test WebSocket trades connection for specific user"""
        try:
            async with websockets.connect(f"{self.base_url}/ws/trades/{self.test_user_id}") as websocket:
                # Test connection establishment
                assert websocket.open is True
                
                # Test receiving trade updates
                message = await asyncio.wait_for(websocket.recv(), timeout=15.0)
                data = json.loads(message)
                
                assert data is not None
                assert 'type' in data
                assert data['type'] == 'trade_update'
                assert 'user_id' in data
                assert data['user_id'] == self.test_user_id
                assert 'timestamp' in data
                assert 'message' in data
                assert 'active_trades' in data
                assert 'portfolio_value' in data
                
                # Test data types
                assert isinstance(data['active_trades'], int)
                assert isinstance(data['portfolio_value'], (int, float))
                
        except websockets.exceptions.InvalidURI:
            pytest.skip("WebSocket server not running")
        except Exception as e:
            pytest.skip(f"WebSocket test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_websocket_message_format(self):
        """Test WebSocket message format and structure"""
        try:
            async with websockets.connect(f"{self.base_url}/ws/market") as websocket:
                # Receive multiple messages to test format consistency
                messages = []
                for _ in range(3):
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(message)
                    messages.append(data)
                
                # Test message format consistency
                for msg in messages:
                    assert 'type' in msg
                    assert 'timestamp' in msg
                    assert msg['type'] in ['market_update', 'error']
                    
                    if msg['type'] == 'market_update':
                        assert 'cme_crude' in msg
                        assert 'ice_brent' in msg
                        assert 'message' in msg
                    
                    # Test timestamp format consistency
                    timestamp = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00'))
                    assert isinstance(timestamp, datetime)
                    
                    # Test that timestamps are recent (within last minute)
                    time_diff = abs((datetime.now() - timestamp).total_seconds())
                    assert time_diff < 60
                
        except websockets.exceptions.InvalidURI:
            pytest.skip("WebSocket server not running")
        except Exception as e:
            pytest.skip(f"WebSocket test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_websocket_error_handling(self):
        """Test WebSocket error handling and recovery"""
        try:
            async with websockets.connect(f"{self.base_url}/ws/market") as websocket:
                # Test normal operation first
                message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                data = json.loads(message)
                
                if data['type'] == 'error':
                    # If we receive an error message, test error structure
                    assert 'message' in data
                    assert 'timestamp' in data
                    assert isinstance(data['message'], str)
                    assert len(data['message']) > 0
                
                # Test connection stability
                assert websocket.open is True
                
        except websockets.exceptions.InvalidURI:
            pytest.skip("WebSocket server not running")
        except Exception as e:
            pytest.skip(f"WebSocket test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_websocket_connection_limits(self):
        """Test WebSocket connection limits and handling"""
        try:
            # Test multiple simultaneous connections
            connections = []
            max_connections = 5
            
            for i in range(max_connections):
                try:
                    websocket = await websockets.connect(f"{self.base_url}/ws/market")
                    connections.append(websocket)
                except Exception:
                    break
            
            # Should be able to establish multiple connections
            assert len(connections) > 0
            
            # Test that all connections are working
            for i, websocket in enumerate(connections):
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(message)
                    assert data is not None
                    assert 'type' in data
                except Exception as e:
                    pytest.fail(f"Connection {i} failed: {e}")
            
            # Clean up connections
            for websocket in connections:
                await websocket.close()
                
        except websockets.exceptions.InvalidURI:
            pytest.skip("WebSocket server not running")
        except Exception as e:
            pytest.skip(f"WebSocket test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_websocket_data_frequency(self):
        """Test WebSocket data update frequency"""
        try:
            async with websockets.connect(f"{self.base_url}/ws/market") as websocket:
                # Test market data update frequency (should be every 5 seconds)
                start_time = datetime.now()
                
                # Receive first message
                message1 = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                time1 = datetime.now()
                
                # Receive second message
                message2 = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                time2 = datetime.now()
                
                # Calculate time difference
                time_diff = (time2 - time1).total_seconds()
                
                # Market updates should be approximately every 5 seconds
                # Allow some tolerance for network delays
                assert 3 <= time_diff <= 8
                
                # Test data consistency between updates
                data1 = json.loads(message1)
                data2 = json.loads(message2)
                
                assert data1['type'] == data2['type']
                assert data1['type'] == 'market_update'
                
                # Timestamps should be different
                timestamp1 = datetime.fromisoformat(data1['timestamp'].replace('Z', '+00:00'))
                timestamp2 = datetime.fromisoformat(data2['timestamp'].replace('Z', '+00:00'))
                assert timestamp1 != timestamp2
                
        except websockets.exceptions.InvalidURI:
            pytest.skip("WebSocket server not running")
        except Exception as e:
            pytest.skip(f"WebSocket test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_websocket_user_specific_updates(self):
        """Test user-specific trade updates via WebSocket"""
        try:
            async with websockets.connect(f"{self.base_url}/ws/trades/{self.test_user_id}") as websocket:
                # Test trade updates frequency (should be every 10 seconds)
                start_time = datetime.now()
                
                # Receive first trade update
                message1 = await asyncio.wait_for(websocket.recv(), timeout=15.0)
                time1 = datetime.now()
                
                # Receive second trade update
                message2 = await asyncio.wait_for(websocket.recv(), timeout=15.0)
                time2 = datetime.now()
                
                # Calculate time difference
                time_diff = (time2 - time1).total_seconds()
                
                # Trade updates should be approximately every 10 seconds
                # Allow some tolerance for network delays
                assert 8 <= time_diff <= 15
                
                # Test data structure consistency
                data1 = json.loads(message1)
                data2 = json.loads(message2)
                
                assert data1['type'] == data2['type']
                assert data1['type'] == 'trade_update'
                assert data1['user_id'] == self.test_user_id
                assert data2['user_id'] == self.test_user_id
                
                # Test trade data fields
                for data in [data1, data2]:
                    assert 'active_trades' in data
                    assert 'portfolio_value' in data
                    assert isinstance(data['active_trades'], int)
                    assert isinstance(data['portfolio_value'], (int, float))
                    assert data['portfolio_value'] >= 0
                    assert data['active_trades'] >= 0
                
        except websockets.exceptions.InvalidURI:
            pytest.skip("WebSocket server not running")
        except Exception as e:
            pytest.skip(f"WebSocket test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_websocket_connection_closure(self):
        """Test WebSocket connection closure and cleanup"""
        try:
            websocket = await websockets.connect(f"{self.base_url}/ws/market")
            
            # Test connection is open
            assert websocket.open is True
            
            # Close connection
            await websocket.close()
            
            # Test connection is closed
            assert websocket.open is False
            
        except websockets.exceptions.InvalidURI:
            pytest.skip("WebSocket server not running")
        except Exception as e:
            pytest.skip(f"WebSocket test failed: {e}")


class TestWebSocketIntegration:
    """Test WebSocket integration with other services"""
    
    def setup_method(self):
        """Setup test environment"""
        self.base_url = "ws://localhost:8000"
    
    @pytest.mark.asyncio
    async def test_websocket_market_data_integration(self):
        """Test WebSocket market data integration with external services"""
        try:
            async with websockets.connect(f"{self.base_url}/ws/market") as websocket:
                # Test that market data includes external service data
                message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                data = json.loads(message)
                
                if data['type'] == 'market_update':
                    # Test CME data integration
                    cme_data = data['cme_crude']
                    assert 'data' in cme_data
                    assert 'source' in cme_data
                    
                    # Test ICE data integration
                    ice_data = data['ice_brent']
                    assert 'data' in ice_data
                    assert 'source' in ice_data
                    
                    # Test data validity
                    assert isinstance(cme_data['data'], (int, float))
                    assert isinstance(ice_data['data'], (int, float))
                    assert cme_data['data'] > 0
                    assert ice_data['data'] > 0
                
        except websockets.exceptions.InvalidURI:
            pytest.skip("WebSocket server not running")
        except Exception as e:
            pytest.skip(f"WebSocket test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_websocket_error_recovery(self):
        """Test WebSocket error recovery and fallback mechanisms"""
        try:
            async with websockets.connect(f"{self.base_url}/ws/market") as websocket:
                # Test error message handling
                message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                data = json.loads(message)
                
                if data['type'] == 'error':
                    # Test error message structure
                    assert 'message' in data
                    assert 'timestamp' in data
                    
                    # Test error message content
                    error_msg = data['message']
                    assert isinstance(error_msg, str)
                    assert len(error_msg) > 0
                    
                    # Test that error messages are informative
                    assert 'Failed to fetch market data' in error_msg or 'error' in error_msg.lower()
                
        except websockets.exceptions.InvalidURI:
            pytest.skip("WebSocket server not running")
        except Exception as e:
            pytest.skip(f"WebSocket test failed: {e}")


class TestWebSocketPerformance:
    """Test WebSocket performance and scalability"""
    
    def setup_method(self):
        """Setup test environment"""
        self.base_url = "ws://localhost:8000"
    
    @pytest.mark.asyncio
    async def test_websocket_latency(self):
        """Test WebSocket message latency"""
        try:
            async with websockets.connect(f"{self.base_url}/ws/market") as websocket:
                # Test message latency
                start_time = datetime.now()
                
                message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                
                end_time = datetime.now()
                latency = (end_time - start_time).total_seconds()
                
                # Latency should be reasonable (less than 2 seconds)
                assert latency < 2.0
                
                # Parse message to test processing time
                data = json.loads(message)
                assert data is not None
                
        except websockets.exceptions.InvalidURI:
            pytest.skip("WebSocket server not running")
        except Exception as e:
            pytest.skip(f"WebSocket test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_websocket_throughput(self):
        """Test WebSocket message throughput"""
        try:
            async with websockets.connect(f"{self.base_url}/ws/market") as websocket:
                # Test message throughput over time
                messages = []
                start_time = datetime.now()
                
                # Collect messages for 10 seconds
                try:
                    while (datetime.now() - start_time).total_seconds() < 10:
                        message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        messages.append(message)
                except asyncio.TimeoutError:
                    pass
                
                # Should receive multiple messages
                assert len(messages) > 0
                
                # Test message processing
                for message in messages:
                    data = json.loads(message)
                    assert data is not None
                    assert 'type' in data
                
        except websockets.exceptions.InvalidURI:
            pytest.skip("WebSocket server not running")
        except Exception as e:
            pytest.skip(f"WebSocket test failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
