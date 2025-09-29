#!/usr/bin/env python3
"""
Debug script to test imports and identify issues
"""

import sys
import os
import traceback

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_import(module_name, description):
    """Test importing a specific module"""
    try:
        __import__(module_name)
        print(f"✅ {description}: {module_name}")
        return True
    except Exception as e:
        print(f"❌ {description}: {module_name} - {e}")
        traceback.print_exc()
        return False

def main():
    """Main debug function"""
    print("🔍 Debugging QuantaEnergi Project Imports")
    print("=" * 50)
    
    # Test core imports
    print("\n📦 Testing Core Imports...")
    core_imports = [
        ("app.core.config", "Core Config"),
        ("app.core.database_manager", "Database Manager"),
        ("app.core.trade_engine", "Trade Engine"),
        ("app.core.risk_calculator", "Risk Calculator"),
    ]
    
    core_success = 0
    for module, desc in core_imports:
        if test_import(module, desc):
            core_success += 1
    
    # Test service imports
    print("\n🔧 Testing Service Imports...")
    service_imports = [
        ("app.services.advanced_etrm_features", "Advanced ETRM Features"),
        ("app.services.advanced_risk_management", "Advanced Risk Management"),
        ("app.services.advanced_trading_engine", "Advanced Trading Engine"),
        ("app.services.comprehensive_compliance", "Comprehensive Compliance"),
        ("app.services.trade_service", "Trade Service"),
        ("app.services.risk_service", "Risk Service"),
        ("app.services.ai_service", "AI Service"),
    ]
    
    service_success = 0
    for module, desc in service_imports:
        if test_import(module, desc):
            service_success += 1
    
    # Test API imports
    print("\n🌐 Testing API Imports...")
    api_imports = [
        ("app.api.v1.advanced_etrm", "Advanced ETRM API"),
        ("app.api.v1.regulatory_compliance", "Regulatory Compliance API"),
        ("app.api.v1.blockchain_carbon", "Blockchain Carbon API"),
    ]
    
    api_success = 0
    for module, desc in api_imports:
        if test_import(module, desc):
            api_success += 1
    
    # Test schema imports
    print("\n📋 Testing Schema Imports...")
    schema_imports = [
        ("app.schemas.trade", "Trade Schemas"),
        ("app.schemas.base", "Base Schemas"),
        ("app.schemas.risk", "Risk Schemas"),
    ]
    
    schema_success = 0
    for module, desc in schema_imports:
        if test_import(module, desc):
            schema_success += 1
    
    # Test model imports
    print("\n🗄️ Testing Model Imports...")
    model_imports = [
        ("app.models.trade", "Trade Models"),
        ("app.models.user", "User Models"),
        ("app.models.esg", "ESG Models"),
    ]
    
    model_success = 0
    for module, desc in model_imports:
        if test_import(module, desc):
            model_success += 1
    
    # Summary
    print("\n📊 Import Test Summary")
    print("=" * 50)
    total_tests = len(core_imports) + len(service_imports) + len(api_imports) + len(schema_imports) + len(model_imports)
    total_success = core_success + service_success + api_success + schema_success + model_success
    
    print(f"Core Imports: {core_success}/{len(core_imports)}")
    print(f"Service Imports: {service_success}/{len(service_imports)}")
    print(f"API Imports: {api_success}/{len(api_imports)}")
    print(f"Schema Imports: {schema_success}/{len(schema_imports)}")
    print(f"Model Imports: {model_success}/{len(model_imports)}")
    print(f"Total: {total_success}/{total_tests}")
    
    if total_success == total_tests:
        print("🎉 All imports successful!")
        return True
    else:
        print(f"⚠️ {total_tests - total_success} imports failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
