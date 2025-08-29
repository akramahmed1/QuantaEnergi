#!/usr/bin/env python3
"""
Comprehensive Test Runner for EnergyOpti-Pro
Runs all security, unit, integration, and E2E tests with detailed reporting.
"""

import os
import sys
import subprocess
import time
import json
from datetime import datetime
from pathlib import Path

class ComprehensiveTestRunner:
    """Runs comprehensive testing suite for EnergyOpti-Pro."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_categories": {},
            "security_scan_results": {},
            "performance_metrics": {},
            "recommendations": []
        }
        
    def run_command(self, command, description, capture_output=True):
        """Run a shell command and return results."""
        print(f"\n🔍 Running: {description}")
        print(f"Command: {' '.join(command)}")
        
        try:
            if capture_output:
                result = subprocess.run(
                    command, 
                    capture_output=True, 
                    text=True, 
                    cwd=self.project_root,
                    timeout=300  # 5 minute timeout
                )
            else:
                result = subprocess.run(
                    command, 
                    cwd=self.project_root,
                    timeout=300
                )
                return result.returncode == 0
            
            success = result.returncode == 0
            output = result.stdout if success else result.stderr
            
            if success:
                print(f"✅ {description} completed successfully")
                if output:
                    print(f"Output: {output[:500]}...")
            else:
                print(f"❌ {description} failed")
                if output:
                    print(f"Error: {output[:500]}...")
            
            return success, output
            
        except subprocess.TimeoutExpired:
            print(f"⏰ {description} timed out after 5 minutes")
            return False, "Timeout expired"
        except Exception as e:
            print(f"💥 {description} failed with exception: {e}")
            return False, str(e)
    
    def check_dependencies(self):
        """Check if all required dependencies are installed."""
        print("\n📦 Checking dependencies...")
        
        dependencies = [
            ("pytest", "pytest --version"),
            ("bandit", "bandit --version"),
            ("safety", "safety --version"),
            ("black", "black --version"),
            ("ruff", "ruff --version"),
            ("mypy", "mypy --version")
        ]
        
        missing_deps = []
        for dep_name, check_cmd in dependencies:
            success, _ = self.run_command(check_cmd.split(), f"Checking {dep_name}")
            if not success:
                missing_deps.append(dep_name)
        
        if missing_deps:
            print(f"\n⚠️  Missing dependencies: {', '.join(missing_deps)}")
            print("Install with: pip install " + " ".join(missing_deps))
            return False
        
        print("✅ All dependencies are available")
        return True
    
    def run_security_tests(self):
        """Run comprehensive security testing."""
        print("\n🛡️  Running Security Tests...")
        
        security_results = {
            "bandit_scan": False,
            "safety_check": False,
            "security_tests": False,
            "vulnerabilities_found": 0,
            "security_score": 0
        }
        
        # Run Bandit security scan
        success, output = self.run_command(
            ["python", "-m", "bandit", "-r", "app/", "-f", "json"],
            "Bandit security scan"
        )
        
        if success and output:
            try:
                bandit_results = json.loads(output)
                security_results["bandit_scan"] = True
                security_results["vulnerabilities_found"] = len(bandit_results.get("results", []))
                
                # Calculate security score (0-100)
                if security_results["vulnerabilities_found"] == 0:
                    security_results["security_score"] = 100
                elif security_results["vulnerabilities_found"] <= 5:
                    security_results["security_score"] = 80
                elif security_results["vulnerabilities_found"] <= 10:
                    security_results["security_score"] = 60
                else:
                    security_results["security_score"] = 40
                    
            except json.JSONDecodeError:
                print("⚠️  Could not parse Bandit results")
        
        # Run Safety check for vulnerable dependencies
        success, output = self.run_command(
            ["python", "-m", "safety", "check", "--json"],
            "Safety dependency vulnerability check"
        )
        
        if success:
            security_results["safety_check"] = True
            try:
                safety_results = json.loads(output)
                vuln_count = len(safety_results)
                security_results["vulnerabilities_found"] += vuln_count
                
                if vuln_count > 0:
                    print(f"⚠️  Found {vuln_count} vulnerable dependencies")
                    
            except json.JSONDecodeError:
                print("⚠️  Could not parse Safety results")
        
        # Run security unit tests
        success, _ = self.run_command(
            ["python", "-m", "pytest", "tests/test_security.py", "-v"],
            "Security unit tests"
        )
        
        security_results["security_tests"] = success
        
        self.test_results["security_scan_results"] = security_results
        return security_results
    
    def run_code_quality_tests(self):
        """Run code quality and formatting checks."""
        print("\n🎨 Running Code Quality Checks...")
        
        quality_results = {
            "black_format": False,
            "ruff_lint": False,
            "mypy_check": False,
            "import_sort": False
        }
        
        # Check Black formatting
        success, _ = self.run_command(
            ["python", "-m", "black", "--check", "app/", "tests/"],
            "Black code formatting check"
        )
        quality_results["black_format"] = success
        
        # Run Ruff linting
        success, _ = self.run_command(
            ["python", "-m", "ruff", "check", "app/", "tests/"],
            "Ruff linting check"
        )
        quality_results["ruff_lint"] = success
        
        # Run MyPy type checking
        success, _ = self.run_command(
            ["python", "-m", "mypy", "app/"],
            "MyPy type checking"
        )
        quality_results["mypy_check"] = success
        
        # Check import sorting
        success, _ = self.run_command(
            ["python", "-m", "isort", "--check-only", "app/", "tests/"],
            "Import sorting check"
        )
        quality_results["import_sort"] = success
        
        return quality_results
    
    def run_unit_tests(self):
        """Run all unit tests."""
        print("\n🧪 Running Unit Tests...")
        
        success, output = self.run_command(
            ["python", "-m", "pytest", "tests/", "-v", "--tb=short"],
            "Unit tests"
        )
        
        if success and output:
            # Parse test results
            lines = output.split('\n')
            for line in lines:
                if 'passed' in line and 'failed' in line:
                    # Extract test counts
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == 'passed':
                            try:
                                self.test_results["passed_tests"] = int(parts[i-1])
                            except (ValueError, IndexError):
                                pass
                        elif part == 'failed':
                            try:
                                self.test_results["failed_tests"] = int(parts[i-1])
                            except (ValueError, IndexError):
                                pass
            
            self.test_results["total_tests"] = (
                self.test_results["passed_tests"] + 
                self.test_results["failed_tests"]
            )
        
        return success
    
    def run_integration_tests(self):
        """Run integration tests."""
        print("\n🔗 Running Integration Tests...")
        
        success, _ = self.run_command(
            ["python", "-m", "pytest", "tests/test_e2e_comprehensive.py", "-v", "--tb=short"],
            "Integration and E2E tests"
        )
        
        return success
    
    def run_performance_tests(self):
        """Run basic performance tests."""
        print("\n⚡ Running Performance Tests...")
        
        performance_results = {
            "startup_time": 0,
            "api_response_time": 0,
            "memory_usage": 0
        }
        
        # Test startup time
        start_time = time.time()
        success, _ = self.run_command(
            ["python", "-c", "import app.main; print('Import successful')"],
            "Application startup test"
        )
        end_time = time.time()
        
        if success:
            performance_results["startup_time"] = round(end_time - start_time, 3)
            print(f"🚀 Startup time: {performance_results['startup_time']}s")
        
        # Test API response time (if server can start)
        try:
            import uvicorn
            from app.main import app
            from fastapi.testclient import TestClient
            
            client = TestClient(app)
            start_time = time.time()
            response = client.get("/api/health")
            end_time = time.time()
            
            if response.status_code == 200:
                performance_results["api_response_time"] = round((end_time - start_time) * 1000, 2)
                print(f"📡 API response time: {performance_results['api_response_time']}ms")
            
        except Exception as e:
            print(f"⚠️  Could not test API performance: {e}")
        
        self.test_results["performance_metrics"] = performance_results
        return True
    
    def generate_recommendations(self):
        """Generate recommendations based on test results."""
        recommendations = []
        
        # Security recommendations
        security_results = self.test_results.get("security_scan_results", {})
        if security_results.get("vulnerabilities_found", 0) > 0:
            recommendations.append(
                f"🔒 Address {security_results['vulnerabilities_found']} security vulnerabilities found by Bandit/Safety"
            )
        
        if security_results.get("security_score", 0) < 80:
            recommendations.append("🛡️  Improve security score - review and fix identified vulnerabilities")
        
        # Test coverage recommendations
        if self.test_results["total_tests"] < 50:
            recommendations.append("🧪 Increase test coverage - aim for at least 50 tests")
        
        if self.test_results["failed_tests"] > 0:
            recommendations.append(f"❌ Fix {self.test_results['failed_tests']} failing tests")
        
        # Performance recommendations
        performance = self.test_results.get("performance_metrics", {})
        if performance.get("startup_time", 0) > 2.0:
            recommendations.append("⏱️  Optimize application startup time - aim for under 2 seconds")
        
        if performance.get("api_response_time", 0) > 100:
            recommendations.append("📡 Optimize API response time - aim for under 100ms")
        
        # Code quality recommendations
        if not all([
            self.test_results.get("black_format", False),
            self.test_results.get("ruff_lint", False),
            self.test_results.get("mypy_check", False)
        ]):
            recommendations.append("🎨 Fix code formatting and linting issues")
        
        self.test_results["recommendations"] = recommendations
        return recommendations
    
    def print_summary(self):
        """Print comprehensive test summary."""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("="*80)
        
        # Test Results
        print(f"\n🧪 Test Results:")
        print(f"   Total Tests: {self.test_results['total_tests']}")
        print(f"   Passed: {self.test_results['passed_tests']}")
        print(f"   Failed: {self.test_results['failed_tests']}")
        
        if self.test_results["total_tests"] > 0:
            success_rate = (self.test_results["passed_tests"] / self.test_results["total_tests"]) * 100
            print(f"   Success Rate: {success_rate:.1f}%")
        
        # Security Results
        security = self.test_results.get("security_scan_results", {})
        print(f"\n🛡️  Security Results:")
        print(f"   Security Score: {security.get('security_score', 0)}/100")
        print(f"   Vulnerabilities Found: {security.get('vulnerabilities_found', 0)}")
        print(f"   Bandit Scan: {'✅' if security.get('bandit_scan') else '❌'}")
        print(f"   Safety Check: {'✅' if security.get('safety_check') else '❌'}")
        print(f"   Security Tests: {'✅' if security.get('security_tests') else '❌'}")
        
        # Performance Results
        performance = self.test_results.get("performance_metrics", {})
        print(f"\n⚡ Performance Results:")
        print(f"   Startup Time: {performance.get('startup_time', 0)}s")
        print(f"   API Response Time: {performance.get('api_response_time', 0)}ms")
        
        # Recommendations
        recommendations = self.test_results.get("recommendations", [])
        if recommendations:
            print(f"\n💡 Recommendations:")
            for rec in recommendations:
                print(f"   {rec}")
        else:
            print(f"\n🎉 All tests passed! No immediate issues found.")
        
        print("\n" + "="*80)
    
    def save_results(self):
        """Save test results to JSON file."""
        results_file = self.project_root / "test_results.json"
        
        try:
            with open(results_file, 'w') as f:
                json.dump(self.test_results, f, indent=2)
            print(f"\n💾 Test results saved to: {results_file}")
        except Exception as e:
            print(f"\n⚠️  Could not save test results: {e}")
    
    def run_all_tests(self):
        """Run the complete testing suite."""
        print("🚀 EnergyOpti-Pro Comprehensive Test Suite")
        print("=" * 50)
        
        start_time = time.time()
        
        # Check dependencies
        if not self.check_dependencies():
            print("\n❌ Dependencies check failed. Please install missing packages.")
            return False
        
        # Run all test categories
        test_categories = {
            "Security Tests": self.run_security_tests,
            "Code Quality": self.run_code_quality_tests,
            "Unit Tests": self.run_unit_tests,
            "Integration Tests": self.run_integration_tests,
            "Performance Tests": self.run_performance_tests
        }
        
        for category_name, test_function in test_categories.items():
            try:
                success = test_function()
                self.test_results["test_categories"][category_name] = success
            except Exception as e:
                print(f"💥 {category_name} failed with exception: {e}")
                self.test_results["test_categories"][category_name] = False
        
        # Generate recommendations
        self.generate_recommendations()
        
        # Calculate total execution time
        total_time = time.time() - start_time
        
        # Print summary
        self.print_summary()
        
        # Save results
        self.save_results()
        
        print(f"\n⏱️  Total execution time: {total_time:.2f} seconds")
        
        # Return overall success
        overall_success = all(self.test_results["test_categories"].values())
        return overall_success

def main():
    """Main entry point."""
    runner = ComprehensiveTestRunner()
    
    try:
        success = runner.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
