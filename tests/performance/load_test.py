"""
Load Testing for EnergyOpti-Pro.

Comprehensive load testing using Locust to validate:
- 10,000 concurrent WebSocket connections
- Sub-200ms response times under load
- Database connection pooling under peak load
- Memory leak detection
"""

import asyncio
import time
import json
import statistics
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import psutil
import aiohttp
import websockets
import asyncio
from dataclasses import dataclass
from locust import HttpUser, task, between, events
from locust.runners import MasterRunner, WorkerRunner
import structlog

logger = structlog.get_logger()

@dataclass
class PerformanceMetrics:
    """Performance metrics container."""
    response_time_avg: float
    response_time_p95: float
    response_time_p99: float
    throughput_rps: float
    error_rate: float
    concurrent_users: int
    memory_usage_mb: float
    cpu_usage_percent: float
    database_connections: int
    websocket_connections: int
    timestamp: datetime

class EnergyOptiProLoadTest(HttpUser):
    """Load test user for EnergyOpti-Pro."""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Initialize user session."""
        self.session_id = f"user_{self.client.environment.runner.user_count}"
        self.websocket_connection = None
        self.auth_token = None
        
        # Authenticate user
        self.authenticate()
    
    def authenticate(self):
        """Authenticate user and get JWT token."""
        try:
            response = self.client.post("/api/v1/auth/login", json={
                "username": f"testuser_{self.session_id}",
                "password": "testpassword123"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                logger.info(f"User {self.session_id} authenticated successfully")
            else:
                logger.warning(f"Authentication failed for user {self.session_id}")
                
        except Exception as e:
            logger.error(f"Authentication error for user {self.session_id}: {e}")
    
    @task(3)
    def get_market_data(self):
        """Get real-time market data."""
        headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
        
        response = self.client.get("/api/v1/market-data", headers=headers)
        
        if response.status_code != 200:
            logger.error(f"Market data request failed: {response.status_code}")
    
    @task(2)
    def get_portfolio(self):
        """Get user portfolio."""
        headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
        
        response = self.client.get("/api/v1/portfolio", headers=headers)
        
        if response.status_code != 200:
            logger.error(f"Portfolio request failed: {response.status_code}")
    
    @task(1)
    def place_order(self):
        """Place a trading order."""
        headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
        
        order_data = {
            "symbol": "OIL_USD",
            "side": "buy",
            "type": "market",
            "quantity": 100,
            "time_in_force": "GTC"
        }
        
        response = self.client.post("/api/v1/orders", json=order_data, headers=headers)
        
        if response.status_code not in [200, 201]:
            logger.error(f"Order placement failed: {response.status_code}")
    
    @task(2)
    def get_risk_metrics(self):
        """Get risk management metrics."""
        headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
        
        response = self.client.get("/api/v1/risk/metrics", headers=headers)
        
        if response.status_code != 200:
            logger.error(f"Risk metrics request failed: {response.status_code}")
    
    @task(1)
    def get_ai_forecast(self):
        """Get AI-powered market forecast."""
        headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
        
        response = self.client.get("/api/v1/ai/forecast?symbol=OIL_USD&horizon=30", headers=headers)
        
        if response.status_code != 200:
            logger.error(f"AI forecast request failed: {response.status_code}")

class WebSocketLoadTest:
    """WebSocket load testing for real-time connections."""
    
    def __init__(self, base_url: str, max_connections: int = 10000):
        self.base_url = base_url.replace("http", "ws")
        self.max_connections = max_connections
        self.connections: List[websockets.WebSocketServerProtocol] = []
        self.metrics: List[Dict[str, Any]] = []
        self.running = False
    
    async def start_load_test(self, duration_seconds: int = 300):
        """Start WebSocket load test."""
        logger.info(f"Starting WebSocket load test: {self.max_connections} connections for {duration_seconds}s")
        
        self.running = True
        start_time = time.time()
        
        # Create connections gradually
        connection_batch_size = 100
        for i in range(0, self.max_connections, connection_batch_size):
            if not self.running:
                break
                
            batch_size = min(connection_batch_size, self.max_connections - i)
            await self.create_connection_batch(batch_size)
            
            # Wait between batches
            await asyncio.sleep(1)
        
        # Monitor connections
        await self.monitor_connections(duration_seconds)
        
        # Cleanup
        await self.cleanup_connections()
        
        # Generate report
        self.generate_report()
    
    async def create_connection_batch(self, batch_size: int):
        """Create a batch of WebSocket connections."""
        tasks = []
        
        for i in range(batch_size):
            task = asyncio.create_task(self.create_websocket_connection())
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def create_websocket_connection(self):
        """Create a single WebSocket connection."""
        try:
            websocket_url = f"{self.base_url}/ws"
            connection = await websockets.connect(websocket_url)
            
            # Subscribe to market data
            subscribe_message = {
                "type": "subscribe",
                "data": {
                    "topic": "market_data:OIL_USD"
                }
            }
            
            await connection.send(json.dumps(subscribe_message))
            
            # Store connection
            self.connections.append(connection)
            
            # Start message handler
            asyncio.create_task(self.handle_messages(connection))
            
        except Exception as e:
            logger.error(f"Failed to create WebSocket connection: {e}")
    
    async def handle_messages(self, connection):
        """Handle incoming WebSocket messages."""
        try:
            async for message in connection:
                # Process message
                data = json.loads(message)
                
                # Record metrics
                self.metrics.append({
                    "timestamp": datetime.now(timezone.utc),
                    "message_type": data.get("type"),
                    "connection_count": len(self.connections)
                })
                
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
    
    async def monitor_connections(self, duration_seconds: int):
        """Monitor WebSocket connections."""
        start_time = time.time()
        
        while time.time() - start_time < duration_seconds and self.running:
            # Record metrics
            metrics = {
                "timestamp": datetime.now(timezone.utc),
                "active_connections": len(self.connections),
                "memory_usage_mb": psutil.Process().memory_info().rss / 1024 / 1024,
                "cpu_usage_percent": psutil.Process().cpu_percent()
            }
            
            self.metrics.append(metrics)
            
            # Log status every 30 seconds
            if int(time.time() - start_time) % 30 == 0:
                logger.info(f"WebSocket Load Test Status: {metrics['active_connections']} connections, "
                          f"{metrics['memory_usage_mb']:.1f}MB RAM, {metrics['cpu_usage_percent']:.1f}% CPU")
            
            await asyncio.sleep(5)
    
    async def cleanup_connections(self):
        """Clean up WebSocket connections."""
        logger.info(f"Cleaning up {len(self.connections)} WebSocket connections")
        
        for connection in self.connections:
            try:
                await connection.close()
            except Exception as e:
                logger.error(f"Error closing WebSocket connection: {e}")
        
        self.connections.clear()
    
    def generate_report(self):
        """Generate WebSocket load test report."""
        if not self.metrics:
            logger.warning("No metrics collected for WebSocket load test")
            return
        
        # Calculate statistics
        connection_counts = [m.get("active_connections", 0) for m in self.metrics if "active_connections" in m]
        memory_usage = [m.get("memory_usage_mb", 0) for m in self.metrics if "memory_usage_mb" in m]
        cpu_usage = [m.get("cpu_usage_percent", 0) for m in self.metrics if "cpu_usage_percent" in m]
        
        report = {
            "test_type": "websocket_load_test",
            "max_connections": self.max_connections,
            "peak_connections": max(connection_counts) if connection_counts else 0,
            "avg_connections": statistics.mean(connection_counts) if connection_counts else 0,
            "peak_memory_mb": max(memory_usage) if memory_usage else 0,
            "avg_memory_mb": statistics.mean(memory_usage) if memory_usage else 0,
            "peak_cpu_percent": max(cpu_usage) if cpu_usage else 0,
            "avg_cpu_percent": statistics.mean(cpu_usage) if cpu_usage else 0,
            "total_messages": len([m for m in self.metrics if "message_type" in m]),
            "test_duration_seconds": len(self.metrics) * 5,  # Assuming 5-second intervals
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info("WebSocket Load Test Report", **report)
        
        # Save report to file
        with open("websocket_load_test_report.json", "w") as f:
            json.dump(report, f, indent=2, default=str)

class DatabaseLoadTest:
    """Database load testing for connection pooling."""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.connections = []
        self.metrics = []
    
    async def run_connection_pool_test(self, max_connections: int = 100, duration_seconds: int = 60):
        """Test database connection pooling under load."""
        logger.info(f"Starting database connection pool test: {max_connections} connections for {duration_seconds}s")
        
        # Create connections
        for i in range(max_connections):
            try:
                import asyncpg
                connection = await asyncpg.connect(self.database_url)
                self.connections.append(connection)
            except Exception as e:
                logger.error(f"Failed to create database connection {i}: {e}")
                break
        
        logger.info(f"Created {len(self.connections)} database connections")
        
        # Run queries under load
        start_time = time.time()
        while time.time() - start_time < duration_seconds:
            await self.run_concurrent_queries()
            await asyncio.sleep(1)
        
        # Cleanup
        await self.cleanup_connections()
        
        # Generate report
        self.generate_report()
    
    async def run_concurrent_queries(self):
        """Run concurrent database queries."""
        if not self.connections:
            return
        
        # Create random queries
        queries = [
            "SELECT COUNT(*) FROM users",
            "SELECT COUNT(*) FROM orders",
            "SELECT COUNT(*) FROM positions",
            "SELECT AVG(price) FROM market_data WHERE symbol = 'OIL_USD'",
            "SELECT COUNT(*) FROM audit_logs WHERE created_at > NOW() - INTERVAL '1 hour'"
        ]
        
        tasks = []
        for connection in self.connections:
            query = queries[len(tasks) % len(queries)]
            task = asyncio.create_task(self.execute_query(connection, query))
            tasks.append(task)
        
        # Wait for all queries to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Record metrics
        successful_queries = len([r for r in results if not isinstance(r, Exception)])
        failed_queries = len(results) - successful_queries
        
        self.metrics.append({
            "timestamp": datetime.now(timezone.utc),
            "total_queries": len(results),
            "successful_queries": successful_queries,
            "failed_queries": failed_queries,
            "active_connections": len(self.connections)
        })
    
    async def execute_query(self, connection, query: str):
        """Execute a single database query."""
        try:
            start_time = time.time()
            result = await connection.fetchval(query)
            execution_time = time.time() - start_time
            
            return {
                "query": query,
                "result": result,
                "execution_time": execution_time,
                "success": True
            }
        except Exception as e:
            return {
                "query": query,
                "error": str(e),
                "success": False
            }
    
    async def cleanup_connections(self):
        """Clean up database connections."""
        logger.info(f"Cleaning up {len(self.connections)} database connections")
        
        for connection in self.connections:
            try:
                await connection.close()
            except Exception as e:
                logger.error(f"Error closing database connection: {e}")
        
        self.connections.clear()
    
    def generate_report(self):
        """Generate database load test report."""
        if not self.metrics:
            logger.warning("No metrics collected for database load test")
            return
        
        # Calculate statistics
        total_queries = sum(m["total_queries"] for m in self.metrics)
        successful_queries = sum(m["successful_queries"] for m in self.metrics)
        failed_queries = sum(m["failed_queries"] for m in self.metrics)
        
        report = {
            "test_type": "database_load_test",
            "total_queries": total_queries,
            "successful_queries": successful_queries,
            "failed_queries": failed_queries,
            "success_rate": (successful_queries / total_queries * 100) if total_queries > 0 else 0,
            "peak_connections": max(m["active_connections"] for m in self.metrics),
            "avg_connections": statistics.mean(m["active_connections"] for m in self.metrics),
            "test_duration_seconds": len(self.metrics),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info("Database Load Test Report", **report)
        
        # Save report to file
        with open("database_load_test_report.json", "w") as f:
            json.dump(report, f, indent=2, default=str)

class MemoryLeakTest:
    """Memory leak detection test."""
    
    def __init__(self):
        self.initial_memory = None
        self.memory_samples = []
        self.running = False
    
    async def run_memory_leak_test(self, duration_seconds: int = 600):
        """Run memory leak detection test."""
        logger.info(f"Starting memory leak test for {duration_seconds}s")
        
        self.running = True
        self.initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        start_time = time.time()
        
        while time.time() - start_time < duration_seconds and self.running:
            # Sample memory usage
            current_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            self.memory_samples.append({
                "timestamp": datetime.now(timezone.utc),
                "memory_mb": current_memory,
                "elapsed_seconds": time.time() - start_time
            })
            
            # Log every minute
            if int(time.time() - start_time) % 60 == 0:
                logger.info(f"Memory Leak Test: {current_memory:.1f}MB RAM "
                          f"({current_memory - self.initial_memory:+.1f}MB from start)")
            
            await asyncio.sleep(10)
        
        # Analyze results
        self.analyze_memory_usage()
    
    def analyze_memory_usage(self):
        """Analyze memory usage for potential leaks."""
        if not self.memory_samples:
            logger.warning("No memory samples collected")
            return
        
        memory_values = [s["memory_mb"] for s in self.memory_samples]
        
        # Calculate statistics
        initial_memory = memory_values[0]
        final_memory = memory_values[-1]
        memory_increase = final_memory - initial_memory
        memory_increase_percent = (memory_increase / initial_memory * 100) if initial_memory > 0 else 0
        
        # Check for memory leak (more than 10% increase over 10 minutes)
        test_duration_hours = (self.memory_samples[-1]["elapsed_seconds"] / 3600)
        memory_increase_per_hour = memory_increase / test_duration_hours if test_duration_hours > 0 else 0
        
        leak_detected = memory_increase_per_hour > 50  # 50MB per hour threshold
        
        report = {
            "test_type": "memory_leak_test",
            "initial_memory_mb": initial_memory,
            "final_memory_mb": final_memory,
            "memory_increase_mb": memory_increase,
            "memory_increase_percent": memory_increase_percent,
            "memory_increase_per_hour_mb": memory_increase_per_hour,
            "test_duration_hours": test_duration_hours,
            "leak_detected": leak_detected,
            "peak_memory_mb": max(memory_values),
            "avg_memory_mb": statistics.mean(memory_values),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info("Memory Leak Test Report", **report)
        
        if leak_detected:
            logger.warning("POTENTIAL MEMORY LEAK DETECTED!")
        else:
            logger.info("No memory leak detected")
        
        # Save report to file
        with open("memory_leak_test_report.json", "w") as f:
            json.dump(report, f, indent=2, default=str)

# Performance test runner
async def run_performance_tests(base_url: str, database_url: str):
    """Run all performance tests."""
    logger.info("Starting comprehensive performance testing")
    
    # 1. WebSocket Load Test
    websocket_test = WebSocketLoadTest(base_url, max_connections=10000)
    await websocket_test.start_load_test(duration_seconds=300)
    
    # 2. Database Load Test
    database_test = DatabaseLoadTest(database_url)
    await database_test.run_connection_pool_test(max_connections=100, duration_seconds=60)
    
    # 3. Memory Leak Test
    memory_test = MemoryLeakTest()
    await memory_test.run_memory_leak_test(duration_seconds=600)
    
    logger.info("Performance testing completed")

# Locust event handlers
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when a test is starting."""
    logger.info("Performance test starting")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when a test is ending."""
    logger.info("Performance test completed")

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, response, context, exception, start_time, url, **kwargs):
    """Called for every request."""
    if exception:
        logger.error(f"Request failed: {name} - {exception}")
    elif response_time > 200:  # Log slow requests
        logger.warning(f"Slow request: {name} - {response_time}ms")

if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python load_test.py <base_url> <database_url>")
        sys.exit(1)
    
    base_url = sys.argv[1]
    database_url = sys.argv[2]
    
    # Run performance tests
    asyncio.run(run_performance_tests(base_url, database_url))
