#!/usr/bin/env python3
"""
Test Runner for EnergyOpti-Pro

This script runs the complete test suite and provides detailed reporting.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return the result."""
    print(f"🔍 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            return True, result.stdout
        else:
            print(f"❌ {description} - FAILED")
            print(f"Error: {result.stderr}")
            return False, result.stderr
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False, "Command timed out"
    except Exception as e:
        print(f"💥 {description} - ERROR: {e}")
        return False, str(e)

def main():
    """Main test execution function."""
    print("🚀 EnergyOpti-Pro Test Suite Execution")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("src/energyopti_pro").exists():
        print("❌ Error: Not in EnergyOpti-Pro root directory")
        sys.exit(1)
    
    # Test 1: Duplication Check
    success, output = run_command(
        "npx jscpd ./src --format python --min-lines 5 --min-tokens 30",
        "Code Duplication Analysis"
    )
    
    if success:
        print("📊 Duplication Analysis Results:")
        print(output)
    
    # Test 2: Linting Check
    success, output = run_command(
        "ruff check .",
        "Code Linting"
    )
    
    # Test 3: Format Check
    success, output = run_command(
        "ruff format --check .",
        "Code Formatting"
    )
    
    # Test 4: Import Check
    success, output = run_command(
        "python -c 'import src.energyopti_pro; print(\"✅ All imports successful\")'",
        "Import Validation"
    )
    
    # Test 5: Configuration Check
    success, output = run_command(
        "python -c 'from src.energyopti_pro.core.config import settings; print(f\"✅ Config loaded: {settings.app_name}\")'",
        "Configuration Loading"
    )
    
    print("\n" + "=" * 50)
    print("🎯 Test Suite Execution Complete")
    print("📋 Next Steps:")
    print("1. Review any failed tests above")
    print("2. Fix any issues identified")
    print("3. Re-run tests to verify fixes")
    print("4. Proceed with deployment")

if __name__ == "__main__":
    main() 