#!/usr/bin/env python3
"""
Comprehensive Test Runner for QuantaEnergi
Runs all tests: Unit, Integration, E2E, and Local Validation
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    print(f"Running: {command}")
    print()
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ SUCCESS")
            if result.stdout:
                print("Output:")
                print(result.stdout)
        else:
            print("❌ FAILED")
            if result.stderr:
                print("Error:")
                print(result.stderr)
            if result.stdout:
                print("Output:")
                print(result.stdout)
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False
    
    return True

def main():
    """Run comprehensive test suite"""
    print("🚀 QuantaEnergi Comprehensive Test Suite")
    print("=" * 60)
    print("Testing all phases: VaR, Geo-Risk, Quantum, REMIT")
    print("=" * 60)
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Local Validation (All Phases)
    tests_total += 1
    if run_command("python test_local_validation.py", "Local Validation - All Phases"):
        tests_passed += 1
    
    # Test 2: Unit Tests (if available)
    tests_total += 1
    if run_command("poetry run pytest tests/ -v --tb=short", "Unit Tests"):
        tests_passed += 1
    
    # Test 3: E2E Tests (if available)
    tests_total += 1
    if run_command("poetry run pytest tests/test_comprehensive_e2e_phases.py -v", "E2E Tests"):
        tests_passed += 1
    
    # Test 4: API Health Check (if server is running)
    tests_total += 1
    if run_command("curl -f http://localhost:8000/health", "API Health Check"):
        tests_passed += 1
    
    # Test 5: Code Quality (if available)
    tests_total += 1
    if run_command("poetry run ruff check app/", "Code Quality Check"):
        tests_passed += 1
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests Passed: {tests_passed}/{tests_total}")
    print(f"Success Rate: {(tests_passed/tests_total)*100:.1f}%")
    
    if tests_passed == tests_total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ QuantaEnergi is ready for deployment")
        return 0
    else:
        print(f"\n⚠️ {tests_total - tests_passed} tests failed")
        print("❌ Some issues need to be resolved")
        return 1

if __name__ == "__main__":
    sys.exit(main())
