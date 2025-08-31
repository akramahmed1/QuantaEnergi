#!/usr/bin/env python3
"""
QuantaEnergi Deployment Verification Script
This script verifies that all deployment components are ready
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

class DeploymentVerifier:
    """Verify QuantaEnergi deployment readiness"""
    
    def __init__(self):
        self.project_root = project_root
        self.verification_results = {
            "docker_setup": False,
            "kubernetes_setup": False,
            "monitoring_setup": False,
            "testing_setup": False,
            "documentation": False
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
    
    def verify_docker_setup(self):
        """Verify Docker production setup"""
        self.print_status("Verifying Docker production setup...")
        
        try:
            # Check Docker Compose production file
            docker_compose_prod = self.project_root / "docker-compose.prod.yml"
            if not docker_compose_prod.exists():
                self.print_status("docker-compose.prod.yml not found", "ERROR")
                return False
            
            # Check production Dockerfiles
            dockerfiles = [
                "backend/Dockerfile.prod",
                "frontend/Dockerfile.prod"
            ]
            
            for dockerfile in dockerfiles:
                file_path = self.project_root / dockerfile
                if not file_path.exists():
                    self.print_status(f"{dockerfile} not found", "ERROR")
                    return False
            
            # Check Docker Compose content
            with open(docker_compose_prod, 'r') as f:
                content = f.read()
            
            required_services = [
                "redis-node-1", "postgres", "backend", "frontend", 
                "prometheus", "grafana", "nginx"
            ]
            
            missing_services = [service for service in required_services if service not in content]
            if missing_services:
                self.print_status(f"Missing services: {missing_services}", "ERROR")
                return False
            
            self.print_status("Docker production setup verified", "SUCCESS")
            self.verification_results["docker_setup"] = True
            return True
            
        except Exception as e:
            self.print_status(f"Docker verification failed: {e}", "ERROR")
            return False
    
    def verify_kubernetes_setup(self):
        """Verify Kubernetes deployment setup"""
        self.print_status("Verifying Kubernetes deployment setup...")
        
        try:
            # Check Kubernetes directory
            k8s_dir = self.project_root / "kubernetes"
            if not k8s_dir.exists():
                self.print_status("Kubernetes directory not found", "ERROR")
                return False
            
            # Check deployment manifests
            deployment_file = k8s_dir / "deployment.yaml"
            if not deployment_file.exists():
                self.print_status("deployment.yaml not found", "ERROR")
                return False
            
            # Check deployment content
            with open(deployment_file, 'r') as f:
                content = f.read()
            
            required_k8s_resources = [
                "Deployment", "Service", "StatefulSet", "Ingress", "HorizontalPodAutoscaler"
            ]
            
            missing_resources = [resource for resource in required_k8s_resources if resource not in content]
            if missing_resources:
                self.print_status(f"Missing K8s resources: {missing_resources}", "WARNING")
            
            self.print_status("Kubernetes deployment setup verified", "SUCCESS")
            self.verification_results["kubernetes_setup"] = True
            return True
            
        except Exception as e:
            self.print_status(f"Kubernetes verification failed: {e}", "ERROR")
            return False
    
    def verify_monitoring_setup(self):
        """Verify monitoring and observability setup"""
        self.print_status("Verifying monitoring and observability setup...")
        
        try:
            # Check monitoring directory
            monitoring_dir = self.project_root / "monitoring"
            if not monitoring_dir.exists():
                self.print_status("Monitoring directory not found", "ERROR")
                return False
            
            # Check Prometheus configuration
            prometheus_config = monitoring_dir / "prometheus" / "prometheus.yml"
            if not prometheus_config.exists():
                self.print_status("Prometheus configuration not found", "ERROR")
                return False
            
            # Check Grafana dashboards
            grafana_dir = monitoring_dir / "grafana"
            if not grafana_dir.exists():
                self.print_status("Grafana directory not found", "ERROR")
                return False
            
            # Check dashboard files
            dashboard_files = list(grafana_dir.rglob("*.json"))
            if not dashboard_files:
                self.print_status("No Grafana dashboards found", "WARNING")
            
            self.print_status("Monitoring setup verified", "SUCCESS")
            self.verification_results["monitoring_setup"] = True
            return True
            
        except Exception as e:
            self.print_status(f"Monitoring verification failed: {e}", "ERROR")
            return False
    
    def verify_testing_setup(self):
        """Verify testing framework setup"""
        self.print_status("Verifying testing framework setup...")
        
        try:
            # Check test scripts
            test_scripts = [
                "scripts/test-all.sh",
                "scripts/test-e2e.sh",
                "scripts/test-pr5.py",
                "scripts/test-all-prs.py"
            ]
            
            for script in test_scripts:
                script_path = self.project_root / script
                if not script_path.exists():
                    self.print_status(f"{script} not found", "ERROR")
                    return False
            
            # Check Cypress setup
            cypress_config = self.project_root / "frontend" / "cypress.config.js"
            if not cypress_config.exists():
                self.print_status("Cypress configuration not found", "ERROR")
                return False
            
            # Check E2E test files
            e2e_tests = [
                "frontend/cypress/e2e/authentication.cy.js",
                "frontend/cypress/e2e/trading-dashboard.cy.js",
                "frontend/cypress/e2e/api-integration.cy.js"
            ]
            
            for test_file in e2e_tests:
                file_path = self.project_root / test_file
                if not file_path.exists():
                    self.print_status(f"{test_file} not found", "ERROR")
                    return False
            
            self.print_status("Testing framework verified", "SUCCESS")
            self.verification_results["testing_setup"] = True
            return True
            
        except Exception as e:
            self.print_status(f"Testing verification failed: {e}", "ERROR")
            return False
    
    def verify_documentation(self):
        """Verify documentation completeness"""
        self.print_status("Verifying documentation completeness...")
        
        try:
            # Check README
            readme_file = self.project_root / "README.md"
            if not readme_file.exists():
                self.print_status("README.md not found", "ERROR")
                return False
            
            # Check final status document
            final_status = self.project_root / "FINAL_STATUS.md"
            if not final_status.exists():
                self.print_status("FINAL_STATUS.md not found", "ERROR")
                return False
            
            # Check PR plan documents
            pr_plans = [
                "temp_pr1.md", "temp_pr2.md", "temp_pr3.md", 
                "temp_pr4.md", "temp_pr5.md"
            ]
            
            existing_plans = 0
            for plan in pr_plans:
                plan_path = self.project_root / plan
                if plan_path.exists():
                    existing_plans += 1
            
            if existing_plans >= 3:
                self.print_status(f"PR plan documents found: {existing_plans}/5", "SUCCESS")
            else:
                self.print_status(f"Insufficient PR plan documents: {existing_plans}/5", "WARNING")
            
            self.print_status("Documentation verified", "SUCCESS")
            self.verification_results["documentation"] = True
            return True
            
        except Exception as e:
            self.print_status(f"Documentation verification failed: {e}", "ERROR")
            return False
    
    def run_verification(self):
        """Run all verification checks"""
        self.print_status("🔍 Starting QuantaEnergi Deployment Verification...", "INFO")
        print("=" * 70)
        
        verifications = [
            ("Docker Production Setup", self.verify_docker_setup),
            ("Kubernetes Deployment", self.verify_kubernetes_setup),
            ("Monitoring & Observability", self.verify_monitoring_setup),
            ("Testing Framework", self.verify_testing_setup),
            ("Documentation", self.verify_documentation)
        ]
        
        for verification_name, verification_func in verifications:
            print(f"\n🔍 Verifying: {verification_name}")
            print("-" * 50)
            try:
                result = verification_func()
                status = "✅ VERIFIED" if result else "❌ FAILED"
                self.print_status(f"{verification_name}: {status}", "SUCCESS" if result else "ERROR")
            except Exception as e:
                self.print_status(f"{verification_name}: ERROR - {e}", "ERROR")
        
        return self.verification_results
    
    def generate_verification_report(self):
        """Generate verification report"""
        print("\n" + "=" * 70)
        self.print_status("📊 QuantaEnergi Deployment Verification Report", "INFO")
        print("=" * 70)
        
        total_checks = len(self.verification_results)
        passed_checks = sum(self.verification_results.values())
        success_rate = (passed_checks / total_checks) * 100
        
        print(f"\n📈 Verification Results:")
        print(f"   Total Checks: {total_checks}")
        print(f"   Passed: {passed_checks}")
        print(f"   Failed: {total_checks - passed_checks}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        print(f"\n🔍 Detailed Results:")
        check_names = {
            "docker_setup": "Docker Production Setup",
            "kubernetes_setup": "Kubernetes Deployment",
            "monitoring_setup": "Monitoring & Observability",
            "testing_setup": "Testing Framework",
            "documentation": "Documentation"
        }
        
        for check_key, check_name in check_names.items():
            result = self.verification_results[check_key]
            status = "✅ VERIFIED" if result else "❌ FAILED"
            print(f"   {check_name}: {status}")
        
        if success_rate == 100:
            print(f"\n🎉 DEPLOYMENT VERIFICATION COMPLETE!")
            print(f"   QuantaEnergi is ready for production deployment!")
            print(f"   🚀 All systems verified and operational!")
        elif success_rate >= 80:
            print(f"\n⚠️  Most verifications passed. Review failed checks.")
        else:
            print(f"\n❌ Multiple verifications failed. Fix issues before deployment.")
        
        return success_rate == 100

def main():
    """Main verification execution"""
    print("🔍 QuantaEnergi Deployment Verification Suite")
    print("=" * 70)
    
    verifier = DeploymentVerifier()
    
    try:
        # Run all verifications
        results = verifier.run_verification()
        
        # Generate report
        success = verifier.generate_verification_report()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Verification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
