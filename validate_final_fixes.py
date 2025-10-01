#!/usr/bin/env python3
"""
Final validation script for PR #4 remaining fixes
Tests all critical components and fixes
"""

import sys
import os
import json

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'backend'))

def test_trade_lifecycle_service():
    """Test TradeLifecycleService methods"""
    print("🔍 Testing TradeLifecycleService...")
    
    try:
        from backend.app.services.advanced_etrm_features import TradeLifecycleService
        
        service = TradeLifecycleService()
        
        # Test create_trade
        trade_data = {
            "trade_id": "TEST_001",
            "commodity": "crude_oil",
            "quantity": 1000,
            "price": 75.50
        }
        
        result = service.create_trade(trade_data)
        assert result["success"] is True
        assert result["status"] == "CREATED"
        trade_id = result["trade_id"]
        
        # Test confirm_trade
        confirm_result = service.confirm_trade(trade_id)
        assert confirm_result["status"] == "CONFIRMED"
        
        # Test settle_trade
        settle_result = service.settle_trade(trade_id)
        assert settle_result["status"] == "SETTLED"
        
        # Test calculate_pnl
        pnl_data = {
            "trade_id": "TEST_001",
            "commodity": "crude_oil",
            "quantity": 1000,
            "entry_price": 75.00,
            "current_price": 78.50,
            "position_type": "long"
        }
        
        pnl_result = service.calculate_pnl(pnl_data)
        assert pnl_result["success"] is True
        assert "unrealized_pnl" in pnl_result
        assert "var_95" in pnl_result
        
        print("✅ TradeLifecycleService working correctly")
        return True
    except Exception as e:
        print(f"❌ TradeLifecycleService failed: {e}")
        return False

def test_sharia_compliance_service():
    """Test ShariaComplianceService methods"""
    print("🔍 Testing ShariaComplianceService...")
    
    try:
        from backend.app.services.sharia_compliance import ShariaComplianceService
        
        service = ShariaComplianceService()
        
        # Test islamic_structures attribute
        assert hasattr(service, 'islamic_structures')
        assert 'murabaha' in service.islamic_structures
        assert service.islamic_structures['murabaha']['type'] == 'Cost-plus financing'
        
        # Test calculate_zakat method
        wealth_data = {
            "total_wealth": 150000,
            "zakat_rate": 0.025,
            "nisab_threshold": 100000
        }
        
        zakat_result = service.calculate_zakat(wealth_data)
        assert zakat_result["zakat_required"] is True
        assert zakat_result["zakat_amount"] == 3750  # 2.5% of 150K
        assert zakat_result["wealth_above_nisab"] == 50000  # 150K - 100K
        
        # Test calculate_islamic_pnl
        trade_data = {
            "principal": 1000000,
            "profit_rate": 0.05,
            "period_months": 12
        }
        
        pnl_result = service.calculate_islamic_pnl(trade_data, "murabaha")
        assert pnl_result["sharia_compliant"] is True
        assert "islamic_pnl" in pnl_result
        
        print("✅ ShariaComplianceService working correctly")
        return True
    except Exception as e:
        print(f"❌ ShariaComplianceService failed: {e}")
        return False

def test_guyana_production_data():
    """Test Guyana production data"""
    print("🔍 Testing Guyana production data...")
    
    try:
        from backend.app.services.geo_risk_service import GeoRiskService
        
        service = GeoRiskService()
        guyana_data = service.guyana_basin_data
        
        # Check production data
        assert guyana_data['liza_field']['production'] == 300000
        assert guyana_data['payara_field']['production'] == 250000
        assert guyana_data['yellowtail_field']['production'] == 150000
        
        total_production = sum([
            guyana_data['liza_field']['production'],
            guyana_data['payara_field']['production'],
            guyana_data['yellowtail_field']['production']
        ])
        
        assert 650000 <= total_production <= 800000
        assert total_production == 700000
        
        print("✅ Guyana production data correct (700K bpd)")
        return True
    except Exception as e:
        print(f"❌ Guyana production test failed: {e}")
        return False

def test_vercel_config():
    """Test Vercel configuration"""
    print("🔍 Testing Vercel configuration...")
    
    try:
        with open('frontend/vercel.json', 'r') as f:
            vercel_config = json.load(f)
        
        # Check that builds property exists and functions property is removed
        assert 'builds' in vercel_config
        assert 'functions' not in vercel_config
        assert vercel_config['builds'][0]['use'] == '@vercel/static-build'
        
        print("✅ Vercel configuration is correct")
        return True
    except Exception as e:
        print(f"❌ Vercel config test failed: {e}")
        return False

def test_trade_schema_validation():
    """Test TradeRequest schema validation"""
    print("🔍 Testing TradeRequest schema validation...")
    
    try:
        from backend.app.schemas.trade import TradeRequest, OrderType
        from datetime import datetime
        
        # Test valid MARKET order (no price required)
        valid_market_trade = TradeRequest(
            commodity="crude_oil",
            asset="WTI",
            volume=1000,
            order_type=OrderType.MARKET,
            price=None,  # Should be valid for market orders
            region="US",
            counterparty="Test Counterparty",
            trade_date=datetime.now()
        )
        assert valid_market_trade.order_type == OrderType.MARKET
        
        # Test valid LIMIT order (price required)
        valid_limit_trade = TradeRequest(
            commodity="crude_oil",
            asset="WTI",
            volume=1000,
            order_type=OrderType.LIMIT,
            price=75.50,  # Required for limit orders
            region="US",
            counterparty="Test Counterparty",
            trade_date=datetime.now()
        )
        assert valid_limit_trade.price == 75.50
        
        print("✅ TradeRequest schema validation working correctly")
        return True
    except Exception as e:
        print(f"❌ TradeRequest schema test failed: {e}")
        return False

def main():
    """Run all validation tests"""
    print("🚀 Validating PR #4 final fixes...")
    print("=" * 50)
    
    tests = [
        test_trade_lifecycle_service,
        test_sharia_compliance_service,
        test_guyana_production_data,
        test_vercel_config,
        test_trade_schema_validation
    ]
    
    passed = 0
    for test in tests:
        print()
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Validation Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All validation tests passed! PR #4 is ready for merge.")
        print("\n📋 Next steps:")
        print("1. git add [modified files]")
        print("2. git commit -m 'Resolve PR #4 remaining test failures: fix TradeLifecycleService confirm_trade, ShariaComplianceService attributes, Vercel/CodeRabbit updates'")
        print("3. git push origin feature/ui-and-db-updates")
        print("4. Merge PR #4 to main branch")
        return 0
    else:
        print("⚠️ Some validation tests failed. Please review and fix issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
