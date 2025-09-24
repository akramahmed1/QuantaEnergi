#!/usr/bin/env python3
"""
Load Testing Runner for QuantaEnergi Platform
Automates running different load test scenarios
"""

import os
import sys
import time
import subprocess
import json
from datetime import datetime
from typing import Dict, List, Optional
import argparse

import requests
from dataclasses import dataclass


@dataclass
class LoadTestResult:
    """Result of a load test"""
    scenario: str
    duration: str
    users: int
    success_rate: float
    avg_response_time: float
    max_response_time: float
    requests_per_second: float
    errors: int
    timestamp: datetime


class LoadTestRunner:
    """Load testing runner for QuantaEnergi"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize load test runner
        
        Args:
            base_url: Base URL of the application
        """
        self.base_url = base_url
        self.results: List[LoadTestResult] = []
        
    def check_application_health(self) -> bool:
        """
        Check if the application is healthy before running tests
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            return response.status_code == 200
        except requests.RequestException as e:
            print(f"Health check failed: {e}")
            return False
    
    def run_locust_test(self, users: int, spawn_rate: int, duration: str, 
                       scenario_name: str) -> LoadTestResult:
        """
        Run Locust load test
        
        Args:
            users: Number of concurrent users
            spawn_rate: User spawn rate per second
            duration: Test duration (e.g., "10m", "5m")
            scenario_name: Name of the test scenario
            
        Returns:
            Load test result
        """
        print(f"Running Locust test: {scenario_name}")
        print(f"Users: {users}, Spawn rate: {spawn_rate}, Duration: {duration}")
        
        # Run Locust in headless mode
        cmd = [
            "locust",
            "-f", "tests/load/locustfile.py",
            "--host", self.base_url,
            "--users", str(users),
            "--spawn-rate", str(spawn_rate),
            "--headless",
            "--run-time", duration,
            "--html", f"reports/locust_{scenario_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
            
            if result.returncode == 0:
                # Parse Locust output for metrics
                metrics = self._parse_locust_output(result.stdout)
                
                return LoadTestResult(
                    scenario=scenario_name,
                    duration=duration,
                    users=users,
                    success_rate=metrics.get("success_rate", 0.0),
                    avg_response_time=metrics.get("avg_response_time", 0.0),
                    max_response_time=metrics.get("max_response_time", 0.0),
                    requests_per_second=metrics.get("requests_per_second", 0.0),
                    errors=metrics.get("errors", 0),
                    timestamp=datetime.now()
                )
            else:
                print(f"Locust test failed: {result.stderr}")
                return self._create_failed_result(scenario_name, duration, users)
                
        except subprocess.TimeoutExpired:
            print(f"Locust test timed out for scenario: {scenario_name}")
            return self._create_failed_result(scenario_name, duration, users)
        except Exception as e:
            print(f"Error running Locust test: {e}")
            return self._create_failed_result(scenario_name, duration, users)
    
    def run_artillery_test(self, config_file: str, scenario_name: str) -> LoadTestResult:
        """
        Run Artillery load test
        
        Args:
            config_file: Artillery configuration file
            scenario_name: Name of the test scenario
            
        Returns:
            Load test result
        """
        print(f"Running Artillery test: {scenario_name}")
        
        cmd = [
            "artillery", "run",
            "--output", f"reports/artillery_{scenario_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            config_file
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
            
            if result.returncode == 0:
                # Parse Artillery output for metrics
                metrics = self._parse_artillery_output(result.stdout)
                
                return LoadTestResult(
                    scenario=scenario_name,
                    duration="artillery_duration",
                    users=metrics.get("users", 0),
                    success_rate=metrics.get("success_rate", 0.0),
                    avg_response_time=metrics.get("avg_response_time", 0.0),
                    max_response_time=metrics.get("max_response_time", 0.0),
                    requests_per_second=metrics.get("requests_per_second", 0.0),
                    errors=metrics.get("errors", 0),
                    timestamp=datetime.now()
                )
            else:
                print(f"Artillery test failed: {result.stderr}")
                return self._create_failed_result(scenario_name, "artillery_duration", 0)
                
        except subprocess.TimeoutExpired:
            print(f"Artillery test timed out for scenario: {scenario_name}")
            return self._create_failed_result(scenario_name, "artillery_duration", 0)
        except Exception as e:
            print(f"Error running Artillery test: {e}")
            return self._create_failed_result(scenario_name, "artillery_duration", 0)
    
    def _parse_locust_output(self, output: str) -> Dict:
        """Parse Locust output to extract metrics"""
        metrics = {}
        
        lines = output.split('\n')
        for line in lines:
            if 'requests/sec' in line:
                try:
                    rps = float(line.split('requests/sec')[0].split()[-1])
                    metrics['requests_per_second'] = rps
                except:
                    pass
            elif 'Average response time' in line:
                try:
                    avg_time = float(line.split('Average response time')[1].split()[0])
                    metrics['avg_response_time'] = avg_time
                except:
                    pass
            elif 'Max response time' in line:
                try:
                    max_time = float(line.split('Max response time')[1].split()[0])
                    metrics['max_response_time'] = max_time
                except:
                    pass
            elif 'Failure rate' in line:
                try:
                    failure_rate = float(line.split('Failure rate')[1].split()[0].replace('%', ''))
                    metrics['success_rate'] = 100.0 - failure_rate
                except:
                    pass
        
        return metrics
    
    def _parse_artillery_output(self, output: str) -> Dict:
        """Parse Artillery output to extract metrics"""
        metrics = {}
        
        lines = output.split('\n')
        for line in lines:
            if 'Summary report' in line:
                # Artillery output parsing would go here
                pass
        
        return metrics
    
    def _create_failed_result(self, scenario: str, duration: str, users: int) -> LoadTestResult:
        """Create a failed test result"""
        return LoadTestResult(
            scenario=scenario,
            duration=duration,
            users=users,
            success_rate=0.0,
            avg_response_time=0.0,
            max_response_time=0.0,
            requests_per_second=0.0,
            errors=999,
            timestamp=datetime.now()
        )
    
    def run_comprehensive_load_tests(self):
        """Run comprehensive load test suite"""
        print("Starting comprehensive load test suite...")
        
        # Ensure reports directory exists
        os.makedirs("reports", exist_ok=True)
        
        # Check application health
        if not self.check_application_health():
            print("Application health check failed. Aborting load tests.")
            return
        
        print("Application is healthy. Starting load tests...")
        
        # Define test scenarios
        scenarios = [
            {"name": "warm_up", "users": 50, "spawn_rate": 5, "duration": "2m"},
            {"name": "normal_load", "users": 200, "spawn_rate": 20, "duration": "5m"},
            {"name": "high_load", "users": 500, "spawn_rate": 50, "duration": "3m"},
            {"name": "peak_load", "users": 1000, "spawn_rate": 100, "duration": "2m"},
            {"name": "stress_test", "users": 2000, "spawn_rate": 200, "duration": "1m"}
        ]
        
        # Run Locust tests
        for scenario in scenarios:
            result = self.run_locust_test(
                users=scenario["users"],
                spawn_rate=scenario["spawn_rate"],
                duration=scenario["duration"],
                scenario_name=scenario["name"]
            )
            self.results.append(result)
            
            # Wait between tests
            print(f"Waiting 30 seconds before next test...")
            time.sleep(30)
        
        # Run Artillery test
        artillery_result = self.run_artillery_test(
            config_file="tests/load/artillery-config.yml",
            scenario_name="artillery_comprehensive"
        )
        self.results.append(artillery_result)
        
        # Generate summary report
        self.generate_summary_report()
    
    def generate_summary_report(self):
        """Generate summary report of all load tests"""
        print("\n" + "="*80)
        print("LOAD TEST SUMMARY REPORT")
        print("="*80)
        
        for result in self.results:
            print(f"\nScenario: {result.scenario}")
            print(f"  Duration: {result.duration}")
            print(f"  Users: {result.users}")
            print(f"  Success Rate: {result.success_rate:.2f}%")
            print(f"  Avg Response Time: {result.avg_response_time:.2f}ms")
            print(f"  Max Response Time: {result.max_response_time:.2f}ms")
            print(f"  Requests/sec: {result.requests_per_second:.2f}")
            print(f"  Errors: {result.errors}")
        
        # Save results to JSON
        results_data = []
        for result in self.results:
            results_data.append({
                "scenario": result.scenario,
                "duration": result.duration,
                "users": result.users,
                "success_rate": result.success_rate,
                "avg_response_time": result.avg_response_time,
                "max_response_time": result.max_response_time,
                "requests_per_second": result.requests_per_second,
                "errors": result.errors,
                "timestamp": result.timestamp.isoformat()
            })
        
        with open(f"reports/load_test_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
            json.dump(results_data, f, indent=2)
        
        print(f"\nDetailed results saved to reports/ directory")
        print("="*80)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="QuantaEnergi Load Test Runner")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of the application")
    parser.add_argument("--scenario", help="Specific scenario to run")
    parser.add_argument("--users", type=int, help="Number of users for specific scenario")
    parser.add_argument("--spawn-rate", type=int, help="Spawn rate for specific scenario")
    parser.add_argument("--duration", help="Duration for specific scenario")
    
    args = parser.parse_args()
    
    runner = LoadTestRunner(base_url=args.url)
    
    if args.scenario and args.users and args.spawn_rate and args.duration:
        # Run specific scenario
        result = runner.run_locust_test(
            users=args.users,
            spawn_rate=args.spawn_rate,
            duration=args.duration,
            scenario_name=args.scenario
        )
        runner.results.append(result)
        runner.generate_summary_report()
    else:
        # Run comprehensive test suite
        runner.run_comprehensive_load_tests()


if __name__ == "__main__":
    main()
