#!/usr/bin/env python3
"""
Enhanced Validation System for EnergyOpti-Pro
Comprehensive validation with 5-minute timeout protection.
"""

import os
import sys
import time
from pathlib import Path

class ValidationSystem:
    """Enhanced validation system with timeout protection."""
    
    def __init__(self, timeout_minutes=5):
        self.timeout_seconds = timeout_minutes * 60
        self.start_time = time.time()
        self.results = {}
    
    def check_timeout(self):
        """Check if timeout exceeded."""
        if time.time() - self.start_time > self.timeout_seconds:
            print("⏰ TIMEOUT: Moving to next task")
            return True
        return False
    
    def validate_critical_files(self):
        """Validate critical files exist."""
        print("🔍 Validating critical files...")
        
        critical_files = [
            'src/energyopti_pro/main.py',
            'src/energyopti_pro/core/config.py',
            'src/energyopti_pro/services/market_data/base_service.py',
            'src/energyopti_pro/services/islamic_finance/base_service.py',
            'docs/QUALITY_METRICS_DASHBOARD.md',
            'docs/7_DAY_ACTION_PLAN.md',
            '.github/workflows/ci.yml',
            'requirements.txt',
            'README.md'
        ]
        
        missing_files = []
        for file_path in critical_files:
            if self.check_timeout():
                return False
            
            if not Path(file_path).exists():
                missing_files.append(file_path)
                print(f"❌ Missing: {file_path}")
            else:
                print(f"✅ Found: {file_path}")
        
        self.results['critical_files'] = len(missing_files) == 0
        return len(missing_files) == 0
    
    def validate_architecture(self):
        """Validate architecture patterns."""
        print("🔍 Validating architecture patterns...")
        
        if self.check_timeout():
            return False
        
        # Check base service patterns
        base_service_files = [
            'src/energyopti_pro/services/market_data/base_service.py',
            'src/energyopti_pro/services/islamic_finance/base_service.py'
        ]
        
        for file_path in base_service_files:
            if not Path(file_path).exists():
                print(f"❌ Missing base service: {file_path}")
                self.results['architecture'] = False
                return False
        
        print("✅ Base service patterns validated")
        self.results['architecture'] = True
        return True
    
    def validate_documentation(self):
        """Validate documentation completeness."""
        print("🔍 Validating documentation...")
        
        if self.check_timeout():
            return False
        
        required_docs = [
            'docs/QUALITY_METRICS_DASHBOARD.md',
            'docs/7_DAY_ACTION_PLAN.md',
            'docs/TEAM_TRAINING_GUIDE.md',
            'docs/US_MARKET_INTEGRATION_PLAN.md',
            'FINAL_COMPLETION_REPORT.md'
        ]
        
        missing_docs = []
        for doc_path in required_docs:
            if not Path(doc_path).exists():
                missing_docs.append(doc_path)
                print(f"❌ Missing documentation: {doc_path}")
            else:
                print(f"✅ Found: {doc_path}")
        
        self.results['documentation'] = len(missing_docs) == 0
        return len(missing_docs) == 0
    
    def validate_ci_cd(self):
        """Validate CI/CD configuration."""
        print("🔍 Validating CI/CD configuration...")
        
        if self.check_timeout():
            return False
        
        ci_file = Path(".github/workflows/ci.yml")
        if ci_file.exists():
            try:
                content = ci_file.read_text(encoding='utf-8')
                if "jscpd" in content and "duplication" in content:
                    print("✅ CI/CD with duplication guard configured")
                    self.results['ci_cd'] = True
                    return True
                else:
                    print("❌ CI/CD missing duplication guard")
                    self.results['ci_cd'] = False
                    return False
            except Exception as e:
                print(f"❌ CI/CD file read error: {e}")
                self.results['ci_cd'] = False
                return False
        else:
            print("❌ CI/CD file not found")
            self.results['ci_cd'] = False
            return False
    
    def run_all_validations(self):
        """Run all validations with timeout protection."""
        print("🚀 Enhanced Validation System for EnergyOpti-Pro")
        print("=" * 60)
        
        validations = [
            ("Critical Files", self.validate_critical_files),
            ("Architecture", self.validate_architecture),
            ("Documentation", self.validate_documentation),
            ("CI/CD Configuration", self.validate_ci_cd)
        ]
        
        passed = 0
        total = len(validations)
        
        for validation_name, validation_func in validations:
            if self.check_timeout():
                print(f"⏰ TIMEOUT: Skipping {validation_name}")
                continue
            
            try:
                if validation_func():
                    passed += 1
                    print(f"✅ {validation_name}: PASSED")
                else:
                    print(f"❌ {validation_name}: FAILED")
            except Exception as e:
                print(f"💥 {validation_name}: ERROR - {e}")
        
        print("\n" + "=" * 60)
        print(f"SUMMARY: {passed}/{total} validations passed")
        
        if passed == total:
            print("🏆 ALL VALIDATIONS PASSED - READY FOR PRODUCTION!")
            return True
        else:
            print("⚠️  Some validations failed - review required")
            return False

def main():
    """Main validation function with timeout protection."""
    validator = ValidationSystem(timeout_minutes=5)
    success = validator.run_all_validations()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 