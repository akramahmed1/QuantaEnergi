#!/usr/bin/env python3
"""
Quality Assurance Script for EnergyOpti-Pro

This script performs comprehensive quality checks on the codebase.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

class QualityChecker:
    """Comprehensive quality checker for EnergyOpti-Pro."""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "overall_status": "PENDING"
        }
    
    def check_file_structure(self):
        """Check if all required files and directories exist."""
        print("🔍 Checking file structure...")
        
        required_files = [
            "src/energyopti_pro/__init__.py",
            "src/energyopti_pro/main.py",
            "src/energyopti_pro/core/config.py",
            "src/energyopti_pro/services/market_data/base_service.py",
            "src/energyopti_pro/services/islamic_finance/base_service.py",
            "docs/QUALITY_METRICS_DASHBOARD.md",
            "docs/7_DAY_ACTION_PLAN.md",
            ".github/workflows/ci.yml"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            self.results["checks"]["file_structure"] = {
                "status": "FAILED",
                "missing_files": missing_files
            }
            print(f"❌ Missing files: {missing_files}")
        else:
            self.results["checks"]["file_structure"] = {
                "status": "PASSED",
                "message": "All required files present"
            }
            print("✅ File structure check passed")
    
    def check_imports(self):
        """Check if all modules can be imported successfully."""
        print("🔍 Checking imports...")
        
        try:
            # Test core imports
            sys.path.insert(0, "src")
            import energyopti_pro
            from energyopti_pro.core.config import settings
            from energyopti_pro.services.market_data.base_service import BaseMarketDataService
            from energyopti_pro.services.islamic_finance.base_service import BaseIslamicFinanceService
            
            self.results["checks"]["imports"] = {
                "status": "PASSED",
                "message": "All core modules import successfully"
            }
            print("✅ Import check passed")
            
        except ImportError as e:
            self.results["checks"]["imports"] = {
                "status": "FAILED",
                "error": str(e)
            }
            print(f"❌ Import check failed: {e}")
    
    def check_duplication_analysis(self):
        """Analyze code duplication using jscpd output."""
        print("🔍 Analyzing duplication...")
        
        try:
            import subprocess
            result = subprocess.run(
                ["npx", "jscpd", "./src", "--format", "python", "--min-lines", "5", "--min-tokens", "30"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                # Parse the output to extract duplication percentage
                output = result.stdout
                if "Duplicated lines" in output:
                    # Extract percentage from output
                    lines = output.split('\n')
                    for line in lines:
                        if "Duplicated lines" in line and "%" in line:
                            percentage = line.split('%')[0].split()[-1]
                            duplication_rate = float(percentage)
                            
                            self.results["checks"]["duplication"] = {
                                "status": "PASSED" if duplication_rate < 3.0 else "WARNING",
                                "duplication_rate": duplication_rate,
                                "target": "< 3.0%"
                            }
                            print(f"✅ Duplication analysis: {duplication_rate}%")
                            break
                else:
                    self.results["checks"]["duplication"] = {
                        "status": "PASSED",
                        "message": "No significant duplication found"
                    }
                    print("✅ Duplication analysis passed")
            else:
                self.results["checks"]["duplication"] = {
                    "status": "FAILED",
                    "error": "jscpd command failed"
                }
                print("❌ Duplication analysis failed")
                
        except Exception as e:
            self.results["checks"]["duplication"] = {
                "status": "ERROR",
                "error": str(e)
            }
            print(f"💥 Duplication analysis error: {e}")
    
    def check_documentation(self):
        """Check if all required documentation is present."""
        print("🔍 Checking documentation...")
        
        required_docs = [
            "docs/QUALITY_METRICS_DASHBOARD.md",
            "docs/7_DAY_ACTION_PLAN.md",
            "docs/architecture/SERVICE_TEMPLATE.md",
            "docs/architecture/REFACTORING_PATTERNS.md",
            "README.md"
        ]
        
        missing_docs = []
        for doc_path in required_docs:
            if not Path(doc_path).exists():
                missing_docs.append(doc_path)
        
        if missing_docs:
            self.results["checks"]["documentation"] = {
                "status": "FAILED",
                "missing_docs": missing_docs
            }
            print(f"❌ Missing documentation: {missing_docs}")
        else:
            self.results["checks"]["documentation"] = {
                "status": "PASSED",
                "message": "All required documentation present"
            }
            print("✅ Documentation check passed")
    
    def check_ci_cd(self):
        """Check if CI/CD configuration is properly set up."""
        print("🔍 Checking CI/CD configuration...")
        
        ci_file = Path(".github/workflows/ci.yml")
        if ci_file.exists():
            content = ci_file.read_text()
            if "jscpd" in content and "duplication" in content:
                self.results["checks"]["ci_cd"] = {
                    "status": "PASSED",
                    "message": "CI/CD with duplication guard configured"
                }
                print("✅ CI/CD check passed")
            else:
                self.results["checks"]["ci_cd"] = {
                    "status": "FAILED",
                    "message": "CI/CD missing duplication guard"
                }
                print("❌ CI/CD missing duplication guard")
        else:
            self.results["checks"]["ci_cd"] = {
                "status": "FAILED",
                "message": "CI/CD file not found"
            }
            print("❌ CI/CD file not found")
    
    def generate_report(self):
        """Generate comprehensive quality report."""
        print("\n" + "=" * 60)
        print("📊 QUALITY ASSURANCE REPORT")
        print("=" * 60)
        
        passed = 0
        failed = 0
        warnings = 0
        
        for check_name, check_result in self.results["checks"].items():
            status = check_result["status"]
            print(f"{check_name.upper()}: {status}")
            
            if status == "PASSED":
                passed += 1
                print(f"  ✅ {check_result.get('message', 'Check passed')}")
            elif status == "WARNING":
                warnings += 1
                print(f"  ⚠️  {check_result.get('message', 'Check warning')}")
            else:
                failed += 1
                print(f"  ❌ {check_result.get('error', check_result.get('message', 'Check failed'))}")
        
        print("\n" + "=" * 60)
        print(f"SUMMARY: {passed} passed, {warnings} warnings, {failed} failed")
        
        if failed == 0 and warnings == 0:
            self.results["overall_status"] = "EXCELLENT"
            print("🏆 OVERALL STATUS: EXCELLENT - All checks passed!")
        elif failed == 0:
            self.results["overall_status"] = "GOOD"
            print("✅ OVERALL STATUS: GOOD - Some warnings, no failures")
        else:
            self.results["overall_status"] = "NEEDS_ATTENTION"
            print("⚠️  OVERALL STATUS: NEEDS ATTENTION - Some checks failed")
        
        # Save report to file
        report_file = Path("quality_report.json")
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
    
    def run_all_checks(self):
        """Run all quality checks."""
        print("🚀 Starting comprehensive quality assurance...")
        print("=" * 60)
        
        self.check_file_structure()
        self.check_imports()
        self.check_duplication_analysis()
        self.check_documentation()
        self.check_ci_cd()
        
        self.generate_report()

def main():
    """Main execution function."""
    checker = QualityChecker()
    checker.run_all_checks()

if __name__ == "__main__":
    main() 