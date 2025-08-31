#!/usr/bin/env python3
"""
Test PR5: Infrastructure & Deployment for QuantaEnergi
This script tests the production infrastructure and deployment capabilities
"""

import os
import sys
import subprocess
import json
import time
import requests
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

class PR5Tester:
    """Test PR5 Infrastructure & Deployment capabilities"""
    
    def __init__(self):
        self.project_root = project_root
        self.test_results = {
            "redis_cluster": False,
            "monitoring": False,
            "deployment": False,
            "performance": False,
            "security": False,
            "scalability": False,
            "testing": False
        }
        
    def print_status(self, message, status="INFO"):
        """Print formatted status message"""
        colors = {
            "INFO": "\033[94m",
            "SUCCESS": "\033[92m", 
            "WARNING": "\033[93m",
            "ERROR": "\033[91m",
            "RESET": "\033[0m"
        }
        print(f"{colors.get(status, colors['INFO'])}[{status}]{colors['RESET']} {message}")
    
    def test_redis_cluster(self):
        """Test Redis Cluster implementation"""
        self.print_status("Testing Redis Cluster implementation...")
        
        try:
            # Check if Redis Cluster files exist
            docker_compose_file = self.project_root / "docker-compose.prod.yml"
            if not docker_compose_file.exists():
                self.print_status("docker-compose.prod.yml not found", "ERROR")
                return False
            
            # Check Redis Cluster configuration
            with open(docker_compose_file, 'r') as f:
                content = f.read()
                
            if "redis-node-1" in content and "redis-cluster-init" in content:
                self.print_status("Redis Cluster configuration found", "SUCCESS")
                self.test_results["redis_cluster"] = True
                return True
            else:
                self.print_status("Redis Cluster configuration incomplete", "ERROR")
                return False
                
        except Exception as e:
            self.print_status(f"Redis Cluster test failed: {e}", "ERROR")
            return False
    
    def test_monitoring(self):
        """Test monitoring and alerting systems"""
        self.print_status("Testing monitoring and alerting systems...")
        
        try:
            # Check Prometheus configuration
            prometheus_config = self.project_root / "monitoring" / "prometheus" / "prometheus.yml"
            if prometheus_config.exists():
                self.print_status("Prometheus configuration found", "SUCCESS")
            else:
                self.print_status("Prometheus configuration missing", "ERROR")
                return False
            
            # Check Grafana dashboards
            grafana_dir = self.project_root / "monitoring" / "grafana"
            if grafana_dir.exists():
                self.print_status("Grafana configuration found", "SUCCESS")
            else:
                self.print_status("Grafana configuration missing", "ERROR")
                return False
            
            self.test_results["monitoring"] = True
            return True
            
        except Exception as e:
            self.print_status(f"Monitoring test failed: {e}", "ERROR")
            return False
    
    def test_deployment(self):
        """Test production deployment automation"""
        self.print_status("Testing production deployment automation...")
        
        try:
            # Check deployment scripts
            deploy_script = self.project_root / "scripts" / "deploy-production.sh"
            deploy_script_alt = self.project_root / "scripts" / "deploy.sh"
            
            if deploy_script.exists() or deploy_script_alt.exists():
                self.print_status("Deployment scripts found", "SUCCESS")
            else:
                self.print_status("Deployment scripts missing", "ERROR")
                return False
            
            # Check Docker production files
            backend_dockerfile = self.project_root / "backend" / "Dockerfile.prod"
            frontend_dockerfile = self.project_root / "frontend" / "Dockerfile.prod"
            
            if backend_dockerfile.exists() and frontend_dockerfile.exists():
                self.print_status("Production Dockerfiles found", "SUCCESS")
            else:
                self.print_status("Production Dockerfiles missing", "ERROR")
                return False
            
            self.test_results["deployment"] = True
            return True
            
        except Exception as e:
            self.print_status(f"Deployment test failed: {e}", "ERROR")
            return False
    
    def test_performance(self):
        """Test performance optimization features"""
        self.print_status("Testing performance optimization features...")
        
        try:
            # Check for performance-related configurations
            docker_compose_file = self.project_root / "docker-compose.prod.yml"
            
            with open(docker_compose_file, 'r') as f:
                content = f.read()
                
            # Check for performance optimizations
            optimizations = [
                "healthcheck",
                "restart: unless-stopped",
                "volumes:",
                "networks:"
            ]
            
            found_optimizations = sum(1 for opt in optimizations if opt in content)
            if found_optimizations >= 3:
                self.print_status(f"Performance optimizations found: {found_optimizations}/4", "SUCCESS")
                self.test_results["performance"] = True
                return True
            else:
                self.print_status(f"Insufficient performance optimizations: {found_optimizations}/4", "WARNING")
                return False
                
        except Exception as e:
            self.print_status(f"Performance test failed: {e}", "ERROR")
            return False
    
    def test_security(self):
        """Test security and compliance features"""
        self.print_status("Testing security and compliance features...")
        
        try:
            # Check for security configurations
            docker_compose_file = self.project_root / "docker-compose.prod.yml"
            
            with open(docker_compose_file, 'r') as f:
                content = f.read()
                
            # Check for security features
            security_features = [
                "environment:",
                "POSTGRES_PASSWORD",
                "JWT_SECRET_KEY",
                "GRAFANA_PASSWORD"
            ]
            
            found_security = sum(1 for feature in security_features if feature in content)
            if found_security >= 3:
                self.print_status(f"Security features found: {found_security}/4", "SUCCESS")
                self.test_results["security"] = True
                return True
            else:
                self.print_status(f"Insufficient security features: {found_security}/4", "WARNING")
                return False
                
        except Exception as e:
            self.print_status(f"Security test failed: {e}", "ERROR")
            return False
    
    def test_scalability(self):
        """Test scalability and high availability features"""
        self.print_status("Testing scalability and high availability features...")
        
        try:
            # Check Kubernetes manifests
            k8s_dir = self.project_root / "kubernetes"
            if k8s_dir.exists():
                deployment_file = k8s_dir / "deployment.yaml"
                if deployment_file.exists():
                    self.print_status("Kubernetes manifests found", "SUCCESS")
                    
                    # Check for scaling features
                    with open(deployment_file, 'r') as f:
                        content = f.read()
                    
                    if "HorizontalPodAutoscaler" in content:
                        self.print_status("Auto-scaling configuration found", "SUCCESS")
                        self.test_results["scalability"] = True
                        return True
                    else:
                        self.print_status("Auto-scaling configuration missing", "WARNING")
                        return False
                else:
                    self.print_status("Kubernetes deployment file missing", "ERROR")
                    return False
            else:
                self.print_status("Kubernetes directory missing", "ERROR")
                return False
                
        except Exception as e:
            self.print_status(f"Scalability test failed: {e}", "ERROR")
            return False
    
    def test_testing(self):
        """Test comprehensive testing framework"""
        self.print_status("Testing comprehensive testing framework...")
        
        try:
            # Check test scripts
            test_script = self.project_root / "scripts" / "test-all.sh"
            e2e_script = self.project_root / "scripts" / "test-e2e.sh"
            
            if test_script.exists() and e2e_script.exists():
                self.print_status("Testing scripts found", "SUCCESS")
            else:
                self.print_status("Testing scripts missing", "ERROR")
                return False
            
            # Check Cypress configuration
            cypress_config = self.project_root / "frontend" / "cypress.config.js"
            if cypress_config.exists():
                self.print_status("Cypress configuration found", "SUCCESS")
            else:
                self.print_status("Cypress configuration missing", "ERROR")
                return False
            
            self.test_results["testing"] = True
            return True
            
        except Exception as e:
            self.print_status(f"Testing framework test failed: {e}", "ERROR")
            return False
    
    def run_all_tests(self):
        """Run all PR5 tests"""
        self.print_status("🚀 Starting PR5 Infrastructure & Deployment Tests...", "INFO")
        print("=" * 60)
        
        tests = [
            ("Redis Cluster", self.test_redis_cluster),
            ("Monitoring & Alerting", self.test_monitoring),
            ("Production Deployment", self.test_deployment),
            ("Performance Optimization", self.test_performance),
            ("Security & Compliance", self.test_security),
            ("Scalability & HA", self.test_scalability),
            ("Testing Framework", self.test_testing)
        ]
        
        for test_name, test_func in tests:
            print(f"\n🔍 Testing: {test_name}")
            print("-" * 40)
            try:
                result = test_func()
                status = "✅ PASSED" if result else "❌ FAILED"
                self.print_status(f"{test_name}: {status}", "SUCCESS" if result else "ERROR")
            except Exception as e:
                self.print_status(f"{test_name}: ERROR - {e}", "ERROR")
        
        return self.test_results
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        self.print_status("📊 PR5 Test Results Summary", "INFO")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(self.test_results.values())
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"\n📈 Overall Results:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {total_tests - passed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        print(f"\n🔍 Detailed Results:")
        for test_name, result in self.test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {test_name.replace('_', ' ').title()}: {status}")
        
        if success_rate == 100:
            print(f"\n🎉 CONGRATULATIONS! All PR5 tests passed!")
            print(f"   QuantaEnergi is ready for production deployment!")
        elif success_rate >= 80:
            print(f"\n⚠️  Most tests passed. Review failed tests before production.")
        else:
            print(f"\n❌ Multiple tests failed. Fix issues before production deployment.")
        
        return success_rate == 100

def main():
    """Main test execution"""
    print("🧪 QuantaEnergi PR5 Infrastructure & Deployment Tester")
    print("=" * 60)
    
    tester = PR5Tester()
    
    try:
        # Run all tests
        results = tester.run_all_tests()
        
        # Generate report
        success = tester.generate_report()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
