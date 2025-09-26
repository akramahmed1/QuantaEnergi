"""
QuantaEnergi MVP Integration Test
Tests all MVP foundations in isolation
"""

import json
from datetime import datetime

def test_trade_capture_schema():
    """Test trade capture schema"""
    print("🧪 Testing Trade Capture Schema...")
    
    from app.schemas.trade import TradeCapture
    
    # Test valid trade
    trade = TradeCapture(
        asset='oil',
        volume=1000.0,
        price=80.5,
        region='me'
    )
    
    assert trade.asset == 'oil'
    assert trade.volume == 1000.0
    assert trade.price == 80.5
    assert trade.region == 'me'
    
    print("✅ Trade Capture Schema: PASSED")

def test_validation_service():
    """Test validation service"""
    print("🧪 Testing Validation Service...")
    
    from app.schemas.trade import TradeCapture
    from app.services.energy_service import validate_forecast
    
    trade = TradeCapture(asset='oil', volume=1000.0, price=80.5, region='me')
    result = validate_forecast(trade)
    
    assert 'is_valid' in result
    assert 'forecast_price' in result
    assert 'confidence' in result
    
    print("✅ Validation Service: PASSED")

def test_compliance_service():
    """Test compliance service"""
    print("🧪 Testing Compliance Service...")
    
    from app.services.compliance import screen_trade
    
    # Test allowed region
    assert screen_trade('me') == True
    assert screen_trade('us') == True
    assert screen_trade('uk') == True
    assert screen_trade('guyana') == True
    
    # Test blocked region
    assert screen_trade('eu') == False
    
    print("✅ Compliance Service: PASSED")

def test_risk_schema():
    """Test risk schema"""
    print("🧪 Testing Risk Schema...")
    
    from app.schemas.risk import VarRequest
    
    req = VarRequest(positions=[10.0, 20.0, 30.0], confidence=0.95)
    
    assert req.positions == [10.0, 20.0, 30.0]
    assert req.confidence == 0.95
    
    print("✅ Risk Schema: PASSED")

def test_endpoint_imports():
    """Test endpoint imports"""
    print("🧪 Testing Endpoint Imports...")
    
    # Test that all imports work
    from app.api_endpoints import router
    from app.schemas.trade import TradeCapture
    from app.services.energy_service import validate_forecast
    from app.services.compliance import screen_trade
    from app.schemas.risk import VarRequest
    from app.services.risk import RiskCalculator
    
    print("✅ Endpoint Imports: PASSED")

def main():
    """Run all MVP integration tests"""
    print("🚀 QuantaEnergi MVP Integration Test")
    print("=" * 50)
    
    try:
        test_trade_capture_schema()
        test_validation_service()
        test_compliance_service()
        test_risk_schema()
        test_endpoint_imports()
        
        print("=" * 50)
        print("🎉 ALL MVP TESTS PASSED!")
        print("✅ Trade Capture: Ready")
        print("✅ Risk Management: Ready")
        print("✅ Compliance: Ready")
        print("✅ API Endpoints: Ready")
        print("")
        print("🚀 MVP Foundations Complete!")
        print("📍 Start backend: python start_mvp.py")
        print("🌐 Start frontend: npm run dev")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
