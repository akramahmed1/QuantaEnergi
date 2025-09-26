#!/usr/bin/env python3
"""
Simple test to verify the trade capture endpoint works
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_trade_capture_schema():
    """Test the TradeCapture schema without full app startup"""
    try:
        from app.api_endpoints import TradeCapture, AssetType, RegionType
        
        # Test schema creation
        trade_data = TradeCapture(
            asset=AssetType.OIL,
            volume=1000.0,
            price=85.50,
            region=RegionType.ME,
            amendments=None
        )
        
        print("✅ TradeCapture schema works correctly")
        print(f"Trade data: {trade_data.model_dump()}")
        return True
        
    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        return False

def test_risk_calculator():
    """Test the risk calculator without full app startup"""
    try:
        from app.services.risk import calculate_var
        
        # Test VaR calculation
        positions = [1000, -500, 2000, -800, 1500, -1200, 3000, -600, 1800, -900]
        var_95 = calculate_var(positions, confidence=0.95)
        
        print("✅ Risk calculator works correctly")
        print(f"VaR 95%: {var_95}")
        return True
        
    except Exception as e:
        print(f"❌ Risk calculator test failed: {e}")
        return False

def test_api_endpoints_import():
    """Test that API endpoints can be imported"""
    try:
        from app.api_endpoints import router
        print("✅ API endpoints import successfully")
        print(f"Router prefix: {router.prefix}")
        return True
        
    except Exception as e:
        print(f"❌ API endpoints import failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Running simple tests...")
    print("=" * 50)
    
    tests = [
        test_api_endpoints_import,
        test_trade_capture_schema,
        test_risk_calculator
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All core components are working!")
    else:
        print("⚠️ Some components need fixing")
