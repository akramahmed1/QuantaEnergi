#!/usr/bin/env python3
"""
PR5 Testing Script for EnergyOpti-Pro
Tests scalability, monitoring, and deployment features
"""

import asyncio
import time
import requests
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add shared services to path
sys.path.append(str(Path(__file__).parent.parent / "shared" / "services"))

class PR5Tester:
    def __init__(self):
        self.base_url = "http://localhost:8001"
        self.test_results = {}
        self.start_time = time.time()
        
    def print_header(self, title: str):
        print(f"\n{'='*60}")
        print(f"🧪 {title}")
        print(f"{'='*60}")
    
    def print_result(self, test_name: str, success: bool, details: str = ""):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        self.test_results[test_name] = success
    
    def test_redis_clustering(self) -> bool:
        """Test Redis clustering functionality"""
        self.print_header("Testing Redis Clustering")
        
        try:
            # Test Redis health endpoint
            response = requests.get(f"{self.base_url}/api/monitoring/cache/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.print_result("Redis Health Check", True, f"Status: {data.get('status', 'unknown')}")
                return True
            else:
                self.print_result("Redis Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.print_result("Redis Health Check", False, f"Error: {str(e)}")
            return False
    
    def test_horizontal_scaling(self) -> bool:
        """Test horizontal scaling features"""
        self.print_header("Testing Horizontal Scaling")
        
        try:
            # Test multiple backend instances
            backends = [8001, 8002, 8003]
            healthy_backends = 0
            
            for port in backends:
                try:
                    response = requests.get(f"http://localhost:{port}/api/health", timeout=5)
                    if response.status_code == 200:
                        healthy_backends += 1
                        self.print_result(f"Backend {port} Health", True)
                    else:
                        self.print_result(f"Backend {port} Health", False, f"Status: {response.status_code}")
                except Exception as e:
                    self.print_result(f"Backend {port} Health", False, f"Error: {str(e)}")
            
            # Test load balancer
            try:
                response = requests.get("http://localhost:80/api/health", timeout=5)
                if response.status_code == 200:
                    self.print_result("Load Balancer Health", True)
                else:
                    self.print_result("Load Balancer Health", False, f"Status: {response.status_code}")
            except Exception as e:
                self.print_result("Load Balancer Health", False, f"Error: {str(e)}")
            
            return healthy_backends >= 2  # At least 2 backends should be healthy
        except Exception as e:
            self.print_result("Horizontal Scaling", False, f"Error: {str(e)}")
            return False
    
    def test_monitoring_metrics(self) -> bool:
        """Test monitoring and metrics collection"""
        self.print_header("Testing Monitoring & Metrics")
        
        try:
            # Test Prometheus metrics endpoint
            response = requests.get(f"{self.base_url}/api/monitoring/metrics", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.print_result("Prometheus Metrics", True, f"Metrics collected: {len(data)}")
                
                # Check for specific metrics
                required_metrics = [
                    'http_requests_total',
                    'http_request_duration_seconds',
                    'cpu_usage_percent',
                    'memory_usage_bytes'
                ]
                
                for metric in required_metrics:
                    if metric in str(data):
                        self.print_result(f"Metric {metric}", True)
                    else:
                        self.print_result(f"Metric {metric}", False, "Metric not found")
                
                return True
            else:
                self.print_result("Promitoring Metrics", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.print_result("Promitoring Metrics", False, f"Error: {str(e)}")
            return False
    
    def test_cache_performance(self) -> bool:
        """Test Redis cache performance"""
        self.print_header("Testing Cache Performance")
        
        try:
            # Test forecasting with caching
            test_data = {
                "commodity": "crude_oil",
                "forecast_days": 7,
                "use_cache": True
            }
            
            # First request (cache miss)
            start_time = time.time()
            response1 = requests.post(f"{self.base_url}/api/forecast", json=test_data, timeout=30)
            first_request_time = time.time() - start_time
            
            if response1.status_code != 200:
                self.print_result("Cache Performance Test", False, f"First request failed: {response1.status_code}")
                return False
            
            # Second request (cache hit)
            start_time = time.time()
            response2 = requests.post(f"{self.base_url}/api/forecast", json=test_data, timeout=30)
            second_request_time = time.time() - start_time
            
            if response2.status_code != 200:
                self.print_result("Cache Performance Test", False, f"Second request failed: {response2.status_code}")
                return False
            
            # Check if second request was faster (cached)
            if second_request_time < first_request_time:
                self.print_result("Cache Hit Performance", True, 
                               f"Cache hit ({second_request_time:.2f}s) faster than miss ({first_request_time:.2f}s)")
            else:
                self.print_result("Cache Hit Performance", False, 
                               f"Cache hit ({second_request_time:.2f}s) not faster than miss ({first_request_time:.2f}s)")
            
            return True
        except Exception as e:
            self.print_result("Cache Performance Test", False, f"Error: {str(e)}")
            return False
    
    def test_websocket_scaling(self) -> bool:
        """Test WebSocket scaling capabilities"""
        self.print_header("Testing WebSocket Scaling")
        
        try:
            # Test WebSocket endpoint
            response = requests.get(f"{self.base_url}/api/websocket/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.print_result("WebSocket Status", True, f"Status: {data.get('status', 'unknown')}")
                return True
            else:
                self.print_result("WebSocket Status", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.print_result("WebSocket Status", False, f"Error: {str(e)}")
            return False
    
    def test_deployment_health(self) -> bool:
        """Test deployment health and readiness"""
        self.print_header("Testing Deployment Health")
        
        try:
            # Test detailed health endpoint
            response = requests.get(f"{self.base_url}/api/monitoring/health/detailed", timeout=15)
            if response.status_code == 200:
                data = response.json()
                self.print_result("Detailed Health Check", True, f"Overall status: {data.get('status', 'unknown')}")
                
                # Check individual services
                services = data.get('services', {})
                for service_name, service_status in services.items():
                    if service_status.get('status') == 'healthy':
                        self.print_result(f"Service {service_name}", True)
                    else:
                        self.print_result(f"Service {service_name}", False, 
                                       f"Status: {service_status.get('status', 'unknown')}")
                
                return True
            else:
                self.print_result("Detailed Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.print_result("Detailed Health Check", False, f"Error: {str(e)}")
            return False
    
    def test_load_balancing(self) -> bool:
        """Test load balancing functionality"""
        self.print_header("Testing Load Balancing")
        
        try:
            # Test load balancer with multiple requests
            responses = []
            for i in range(10):
                try:
                    response = requests.get("http://localhost:80/api/health", timeout=5)
                    if response.status_code == 200:
                        responses.append(response)
                except Exception as e:
                    print(f"   Request {i+1} failed: {str(e)}")
            
            if len(responses) >= 8:  # At least 80% success rate
                self.print_result("Load Balancer Requests", True, f"Success rate: {len(responses)}/10")
                return True
            else:
                self.print_result("Load Balancer Requests", False, f"Success rate: {len(responses)}/10")
                return False
        except Exception as e:
            self.print_result("Load Balancer Test", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all PR5 tests"""
        self.print_header("PR5 COMPREHENSIVE TESTING")
        
        tests = [
            ("Redis Clustering", self.test_redis_clustering),
            ("Horizontal Scaling", self.test_horizontal_scaling),
            ("Monitoring Metrics", self.test_monitoring_metrics),
            ("Cache Performance", self.test_cache_performance),
            ("WebSocket Scaling", self.test_websocket_scaling),
            ("Deployment Health", self.test_deployment_health),
            ("Load Balancing", self.test_load_balancing)
        ]
        
        for test_name, test_func in tests:
            try:
                success = test_func()
                self.test_results[test_name] = success
            except Exception as e:
                self.print_result(test_name, False, f"Test error: {str(e)}")
                self.test_results[test_name] = False
        
        return self.test_results
    
    def generate_report(self) -> str:
        """Generate test report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        report = f"""
{'='*60}
📊 PR5 TESTING REPORT
{'='*60}
Total Tests: {total_tests}
Passed: {passed_tests} ✅
Failed: {failed_tests} ❌
Success Rate: {success_rate:.1f}%

Test Results:
"""
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            report += f"{status} {test_name}\n"
        
        report += f"""
{'='*60}
Overall Status: {'🎉 ALL TESTS PASSED' if failed_tests == 0 else '⚠️  SOME TESTS FAILED'}
Execution Time: {time.time() - self.start_time:.2f} seconds
{'='*60}
"""
        
        return report

def main():
    """Main test execution"""
    print("🚀 Starting PR5 Testing for EnergyOpti-Pro...")
    
    tester = PR5Tester()
    results = tester.run_all_tests()
    
    # Generate and display report
    report = tester.generate_report()
    print(report)
    
    # Exit with appropriate code
    failed_tests = sum(1 for result in results.values() if not result)
    if failed_tests == 0:
        print("🎉 PR5 Testing completed successfully!")
        sys.exit(0)
    else:
        print(f"⚠️  PR5 Testing completed with {failed_tests} failures")
        sys.exit(1)

if __name__ == "__main__":
    main()
