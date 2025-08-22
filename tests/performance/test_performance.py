"""
Performance tests for enhanced services (PR2).

Tests sub-200ms response times and high throughput for AI/ML, caching, and WebSocket services.
"""

import asyncio
import time
import statistics
from typing import List, Dict, Any
import structlog
from concurrent.futures import ThreadPoolExecutor
import threading

from src.energyopti_pro.services.enhanced_ai_ml_service import EnhancedAIMLService
from src.energyopti_pro.services.cache_service import CacheService
from src.energyopti_pro.services.websocket_service import WebSocketService
from src.energyopti_pro.services.enhanced_security_service import EnhancedSecurityService

logger = structlog.get_logger()

class PerformanceTester:
    """Performance testing for enhanced services."""
    
    def __init__(self):
        self.ai_ml_service = EnhancedAIMLService()
        self.cache_service = CacheService("redis://localhost:6379/0")
        self.websocket_service = WebSocketService()
        self.security_service = EnhancedSecurityService("test-secret")
        
        # Performance metrics
        self.results: Dict[str, List[float]] = {}
        self.throughput_results: Dict[str, List[int]] = {}
    
    async def test_ai_ml_performance(self, iterations: int = 100) -> Dict[str, Any]:
        """Test AI/ML service performance."""
        logger.info(f"Testing AI/ML service performance with {iterations} iterations")
        
        # Test forecasting performance
        forecast_times = []
        for i in range(iterations):
            start_time = time.time()
            await self.ai_ml_service.forecast_energy_prices("crude_oil", 7)
            end_time = time.time()
            forecast_times.append((end_time - start_time) * 1000)  # Convert to ms
        
        # Test RL training performance
        rl_times = []
        for i in range(iterations // 10):  # Fewer iterations for RL (slower)
            start_time = time.time()
            await self.ai_ml_service.train_rl_agent(
                "portfolio_optimization",
                {"episodes": 100},
                {"total_timesteps": 1000}
            )
            end_time = time.time()
            rl_times.append((end_time - start_time) * 1000)
        
        # Test quantum optimization performance
        quantum_times = []
        for i in range(iterations):
            start_time = time.time()
            await self.ai_ml_service.run_quantum_optimization(
                "portfolio_optimization",
                {"shots": 100}
            )
            end_time = time.time()
            quantum_times.append((end_time - start_time) * 1000)
        
        # Test ESG analysis performance
        esg_times = []
        company_data = {
            "company_name": f"Test Corp {i}",
            "carbon_emissions": 0.5,
            "energy_efficiency": 0.8
        }
        for i in range(iterations):
            start_time = time.time()
            await self.ai_ml_service.analyze_esg(company_data)
            end_time = time.time()
            esg_times.append((end_time - start_time) * 1000)
        
        # Store results
        self.results["forecasting"] = forecast_times
        self.results["rl_training"] = rl_times
        self.results["quantum_optimization"] = quantum_times
        self.results["esg_analysis"] = esg_times
        
        return {
            "forecasting": self._calculate_metrics(forecast_times),
            "rl_training": self._calculate_metrics(rl_times),
            "quantum_optimization": self._calculate_metrics(quantum_times),
            "esg_analysis": self._calculate_metrics(esg_times)
        }
    
    async def test_cache_performance(self, iterations: int = 1000) -> Dict[str, Any]:
        """Test cache service performance."""
        logger.info(f"Testing cache service performance with {iterations} iterations")
        
        # Initialize cache service
        await self.cache_service.initialize()
        
        # Test set performance
        set_times = []
        for i in range(iterations):
            start_time = time.time()
            await self.cache_service.set(f"test_key_{i}", {"data": f"value_{i}"}, ttl=60)
            end_time = time.time()
            set_times.append((end_time - start_time) * 1000)
        
        # Test get performance
        get_times = []
        for i in range(iterations):
            start_time = time.time()
            await self.cache_service.get(f"test_key_{i}")
            end_time = time.time()
            get_times.append((end_time - start_time) * 1000)
        
        # Test delete performance
        delete_times = []
        for i in range(iterations):
            start_time = time.time()
            await self.cache_service.delete(f"test_key_{i}")
            end_time = time.time()
            delete_times.append((end_time - start_time) * 1000)
        
        # Store results
        self.results["cache_set"] = set_times
        self.results["cache_get"] = get_times
        self.results["cache_delete"] = delete_times
        
        # Clean up
        await self.cache_service.close()
        
        return {
            "cache_set": self._calculate_metrics(set_times),
            "cache_get": self._calculate_metrics(get_times),
            "cache_delete": self._calculate_metrics(delete_times)
        }
    
    async def test_websocket_performance(self, iterations: int = 100) -> Dict[str, Any]:
        """Test WebSocket service performance."""
        logger.info(f"Testing WebSocket service performance with {iterations} iterations")
        
        # Start WebSocket service
        await self.websocket_service.start()
        
        # Test message creation performance
        message_times = []
        for i in range(iterations):
            start_time = time.time()
            message = self.websocket_service.connection_manager.create_message(
                "market_data",
                {"price": 75.50 + i},
                "user123"
            )
            end_time = time.time()
            message_times.append((end_time - start_time) * 1000)
        
        # Test broadcasting performance (simulated)
        broadcast_times = []
        for i in range(iterations):
            start_time = time.time()
            # Simulate broadcast without actual connections
            await self.websocket_service.broadcast_market_data({"price": 75.50 + i})
            end_time = time.time()
            broadcast_times.append((end_time - start_time) * 1000)
        
        # Store results
        self.results["websocket_message_creation"] = message_times
        self.results["websocket_broadcast"] = broadcast_times
        
        # Stop WebSocket service
        await self.websocket_service.stop()
        
        return {
            "websocket_message_creation": self._calculate_metrics(message_times),
            "websocket_broadcast": self._calculate_metrics(broadcast_times)
        }
    
    async def test_security_performance(self, iterations: int = 100) -> Dict[str, Any]:
        """Test security service performance."""
        logger.info(f"Testing security service performance with {iterations} iterations")
        
        # Test user creation performance
        creation_times = []
        for i in range(iterations):
            start_time = time.time()
            self.security_service.create_user(
                f"user{i}",
                f"user{i}@example.com",
                "password123",
                "trader"
            )
            end_time = time.time()
            creation_times.append((end_time - start_time) * 1000)
        
        # Test authentication performance
        auth_times = []
        for i in range(iterations):
            start_time = time.time()
            self.security_service.authenticate_user(f"user{i}", "password123", "127.0.0.1")
            end_time = time.time()
            auth_times.append((end_time - start_time) * 1000)
        
        # Test permission checking performance
        permission_times = []
        # Create a user and get token first
        user = self.security_service.create_user("permuser", "perm@example.com", "password123", "trader")
        token = self.security_service.authenticate_user("permuser", "password123", "127.0.0.1")
        
        for i in range(iterations):
            start_time = time.time()
            self.security_service.check_permission(token, "read_market_data")
            end_time = time.time()
            permission_times.append((end_time - start_time) * 1000)
        
        # Test encryption performance
        encryption_times = []
        for i in range(iterations):
            start_time = time.time()
            self.security_service.encrypt_sensitive_data(f"sensitive_data_{i}")
            end_time = time.time()
            encryption_times.append((end_time - start_time) * 1000)
        
        # Store results
        self.results["user_creation"] = creation_times
        self.results["authentication"] = auth_times
        self.results["permission_checking"] = permission_times
        self.results["encryption"] = encryption_times
        
        return {
            "user_creation": self._calculate_metrics(creation_times),
            "authentication": self._calculate_metrics(auth_times),
            "permission_checking": self._calculate_metrics(permission_times),
            "encryption": self._calculate_metrics(encryption_times)
        }
    
    async def test_concurrent_performance(self, concurrent_users: int = 100, requests_per_user: int = 10) -> Dict[str, Any]:
        """Test concurrent performance."""
        logger.info(f"Testing concurrent performance with {concurrent_users} users, {requests_per_user} requests each")
        
        # Test concurrent AI/ML requests
        ai_ml_concurrent_times = []
        ai_ml_throughput = []
        
        async def concurrent_ai_ml_request():
            start_time = time.time()
            await self.ai_ml_service.forecast_energy_prices("crude_oil", 7)
            end_time = time.time()
            return (end_time - start_time) * 1000
        
        # Run concurrent requests
        for batch in range(0, concurrent_users, 10):  # Process in batches of 10
            batch_size = min(10, concurrent_users - batch)
            tasks = [concurrent_ai_ml_request() for _ in range(batch_size)]
            
            batch_start = time.time()
            results = await asyncio.gather(*tasks)
            batch_end = time.time()
            
            ai_ml_concurrent_times.extend(results)
            ai_ml_throughput.append(int(batch_size / (batch_end - batch_start)))
        
        # Test concurrent cache requests
        cache_concurrent_times = []
        cache_throughput = []
        
        async def concurrent_cache_request():
            start_time = time.time()
            await self.cache_service.set("concurrent_key", "value", ttl=60)
            end_time = time.time()
            return (end_time - start_time) * 1000
        
        # Initialize cache for concurrent test
        await self.cache_service.initialize()
        
        for batch in range(0, concurrent_users, 10):
            batch_size = min(10, concurrent_users - batch)
            tasks = [concurrent_cache_request() for _ in range(batch_size)]
            
            batch_start = time.time()
            results = await asyncio.gather(*tasks)
            batch_end = time.time()
            
            cache_concurrent_times.extend(results)
            cache_throughput.append(int(batch_size / (batch_end - batch_start)))
        
        await self.cache_service.close()
        
        # Store results
        self.results["concurrent_ai_ml"] = ai_ml_concurrent_times
        self.results["concurrent_cache"] = cache_concurrent_times
        self.throughput_results["concurrent_ai_ml"] = ai_ml_throughput
        self.throughput_results["concurrent_cache"] = cache_throughput
        
        return {
            "concurrent_ai_ml": self._calculate_metrics(ai_ml_concurrent_times),
            "concurrent_cache": self._calculate_metrics(cache_concurrent_times),
            "ai_ml_throughput": self._calculate_throughput_metrics(ai_ml_throughput),
            "cache_throughput": self._calculate_throughput_metrics(cache_throughput)
        }
    
    def _calculate_metrics(self, times: List[float]) -> Dict[str, Any]:
        """Calculate performance metrics."""
        if not times:
            return {}
        
        return {
            "count": len(times),
            "mean_ms": statistics.mean(times),
            "median_ms": statistics.median(times),
            "min_ms": min(times),
            "max_ms": max(times),
            "std_dev_ms": statistics.stdev(times) if len(times) > 1 else 0,
            "p95_ms": sorted(times)[int(len(times) * 0.95)],
            "p99_ms": sorted(times)[int(len(times) * 0.99)],
            "under_200ms": sum(1 for t in times if t < 200),
            "under_200ms_pct": (sum(1 for t in times if t < 200) / len(times)) * 100
        }
    
    def _calculate_throughput_metrics(self, throughput: List[int]) -> Dict[str, Any]:
        """Calculate throughput metrics."""
        if not throughput:
            return {}
        
        return {
            "count": len(throughput),
            "mean_rps": statistics.mean(throughput),
            "median_rps": statistics.median(throughput),
            "min_rps": min(throughput),
            "max_rps": max(throughput),
            "std_dev_rps": statistics.stdev(throughput) if len(throughput) > 1 else 0
        }
    
    def generate_performance_report(self) -> str:
        """Generate comprehensive performance report."""
        report = []
        report.append("=" * 80)
        report.append("ENERGYOPTI-PRO PERFORMANCE TEST REPORT (PR2)")
        report.append("=" * 80)
        report.append("")
        
        # Overall summary
        total_tests = len(self.results)
        total_under_200ms = 0
        total_requests = 0
        
        for test_name, times in self.results.items():
            if times:
                under_200ms = sum(1 for t in times if t < 200)
                total_under_200ms += under_200ms
                total_requests += len(times)
        
        overall_percentage = (total_under_200ms / total_requests * 100) if total_requests > 0 else 0
        
        report.append(f"OVERALL PERFORMANCE SUMMARY:")
        report.append(f"  Total Tests: {total_tests}")
        report.append(f"  Total Requests: {total_requests}")
        report.append(f"  Requests Under 200ms: {total_under_200ms}")
        report.append(f"  Percentage Under 200ms: {overall_percentage:.2f}%")
        report.append("")
        
        # Individual test results
        for test_name, times in self.results.items():
            if times:
                metrics = self._calculate_metrics(times)
                report.append(f"{test_name.upper()}:")
                report.append(f"  Count: {metrics['count']}")
                report.append(f"  Mean: {metrics['mean_ms']:.2f}ms")
                report.append(f"  Median: {metrics['median_ms']:.2f}ms")
                report.append(f"  P95: {metrics['p95_ms']:.2f}ms")
                report.append(f"  P99: {metrics['p99_ms']:.2f}ms")
                report.append(f"  Under 200ms: {metrics['under_200ms']}/{metrics['count']} ({metrics['under_200ms_pct']:.2f}%)")
                report.append("")
        
        # Throughput results
        if self.throughput_results:
            report.append("THROUGHPUT RESULTS:")
            for test_name, throughput in self.throughput_results.items():
                if throughput:
                    metrics = self._calculate_throughput_metrics(throughput)
                    report.append(f"  {test_name}:")
                    report.append(f"    Mean: {metrics['mean_rps']:.2f} requests/second")
                    report.append(f"    Max: {metrics['max_rps']} requests/second")
                    report.append("")
        
        # Performance recommendations
        report.append("PERFORMANCE RECOMMENDATIONS:")
        
        # Check for tests that don't meet 200ms target
        slow_tests = []
        for test_name, times in self.results.items():
            if times:
                metrics = self._calculate_metrics(times)
                if metrics['under_200ms_pct'] < 95:  # Less than 95% under 200ms
                    slow_tests.append((test_name, metrics['under_200ms_pct']))
        
        if slow_tests:
            report.append("  ⚠️  Tests that need optimization:")
            for test_name, percentage in slow_tests:
                report.append(f"    - {test_name}: {percentage:.2f}% under 200ms")
        else:
            report.append("  ✅ All tests meet performance targets!")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)

async def main():
    """Run performance tests."""
    logger.info("Starting EnergyOpti-Pro performance tests (PR2)")
    
    tester = PerformanceTester()
    
    try:
        # Run all performance tests
        logger.info("Running AI/ML performance tests...")
        ai_ml_results = await tester.test_ai_ml_performance(100)
        
        logger.info("Running cache performance tests...")
        cache_results = await tester.test_cache_performance(1000)
        
        logger.info("Running WebSocket performance tests...")
        websocket_results = await tester.test_websocket_performance(100)
        
        logger.info("Running security performance tests...")
        security_results = await tester.test_security_performance(100)
        
        logger.info("Running concurrent performance tests...")
        concurrent_results = await tester.test_concurrent_performance(100, 10)
        
        # Generate and display report
        report = tester.generate_performance_report()
        print(report)
        
        # Save report to file
        with open("performance_report_pr2.txt", "w") as f:
            f.write(report)
        
        logger.info("Performance tests completed. Report saved to performance_report_pr2.txt")
        
    except Exception as e:
        logger.error(f"Performance tests failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
