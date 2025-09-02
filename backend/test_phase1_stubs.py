#!/usr/bin/env python3
"""
Test script for Phase 1 ETRM/CTRM stubs
Tests all core services and validates stub functionality
"""

import sys
import os
from datetime import datetime, timedelta

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_sharia_engine():
    """Test Sharia compliance engine"""
    print("Testing Sharia Engine...")
    
    try:
        from app.services.sharia import ShariaScreeningEngine, IslamicTradingValidator
        
        # Test commodity screening
        engine = ShariaScreeningEngine()
        result = engine.screen_commodity({"type": "crude_oil"})
        assert result["compliant"] == True, "Crude oil should be compliant"
        
        result = engine.screen_commodity({"type": "alcohol"})
        assert result["compliant"] == False, "Alcohol should not be compliant"
        
        # Test trading structure validation
        result = engine.validate_trading_structure({"interest_rate": 0, "asset_backing_ratio": 1.0})
        assert result["compliant"] == True, "Islamic structure should be compliant"
        
        result = engine.validate_trading_structure({"interest_rate": 0.05, "asset_backing_ratio": 1.0})
        assert result["compliant"] == False, "Interest-based structure should not be compliant"
        
        # Test Zakat calculation
        result = engine.calculate_zakat_obligation(200000)
        assert result["zakat_obligation"] > 0, "Zakat should be calculated for wealth above nisab"
        
        print("✅ Sharia Engine tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Sharia Engine tests failed: {e}")
        return False

def test_deal_capture():
    """Test deal capture service"""
    print("Testing Deal Capture Service...")
    
    try:
        from app.services.deal_capture import DealCaptureService, DealValidationService
        
        # Test deal validation
        validator = DealValidationService()
        
        # Use a future delivery date
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        deal_data = {
            "parties": ["trader1", "counterparty1"],
            "commodity": "crude_oil",
            "quantity": 1000,
            "price": 85.50,
            "delivery_date": future_date
        }
        
        result = validator.validate_deal_data(deal_data)
        assert result["valid"] == True, "Valid deal should pass validation"
        
        # Test invalid deal
        invalid_deal = {"parties": ["trader1"]}  # Missing required fields
        result = validator.validate_deal_data(invalid_deal)
        assert result["valid"] == False, "Invalid deal should fail validation"
        
        # Test deal capture
        service = DealCaptureService()
        result = service.capture_deal(deal_data)
        assert result["success"] == True, "Deal should be captured successfully"
        assert "deal_id" in result, "Deal ID should be returned"
        
        print("✅ Deal Capture Service tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Deal Capture Service tests failed: {e}")
        return False

def test_position_manager():
    """Test position manager service"""
    print("Testing Position Manager...")
    
    try:
        from app.services.position_manager import PositionManager
        
        service = PositionManager()
        
        # Test position creation
        deal_data = {
            "commodity": "crude_oil",
            "quantity": 1000,
            "price": 85.50,
            "currency": "USD",
            "trade_type": "spot",
            "direction": "long",
            "sharia_compliant": True
        }
        
        result = service.create_position(deal_data)
        assert result["success"] == True, "Position should be created successfully"
        assert "position_id" in result, "Position ID should be returned"
        
        position_id = result["position_id"]
        
        # Test P&L calculation
        pnl_result = service.calculate_pnl(position_id, 90.00)
        assert pnl_result["success"] == True, "P&L should be calculated successfully"
        assert pnl_result["unrealized_pnl"] > 0, "P&L should be positive for price increase"
        
        # Test portfolio summary
        summary = service.get_portfolio_summary()
        assert "total_positions" in summary, "Portfolio summary should contain total positions"
        
        print("✅ Position Manager tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Position Manager tests failed: {e}")
        return False

def test_market_risk_engine():
    """Test market risk engine"""
    print("Testing Market Risk Engine...")
    
    try:
        from app.services.market_risk_engine import MarketRiskEngine
        
        engine = MarketRiskEngine()
        
        # Test VaR calculation
        positions = [
            {"notional_value": 1000000},
            {"notional_value": 2000000}
        ]
        
        var_result = engine.calculate_var(positions, 0.95, 1)
        assert "var" in var_result, "VaR result should contain var value"
        assert var_result["var"] > 0, "VaR should be positive"
        
        # Test Expected Shortfall
        es_result = engine.calculate_expected_shortfall(positions, 0.95)
        assert "expected_shortfall" in es_result, "ES result should contain expected shortfall"
        
        # Test stress testing
        scenarios = [
            {"name": "Oil Price Crash", "price_shock": -0.20},
            {"name": "Gas Price Spike", "price_shock": 0.30}
        ]
        
        stress_result = engine.perform_stress_test(positions, scenarios)
        assert "stress_test_results" in stress_result, "Stress test should return results"
        assert len(stress_result["stress_test_results"]) == 2, "Should have 2 scenario results"
        
        print("✅ Market Risk Engine tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Market Risk Engine tests failed: {e}")
        return False

def test_logistics_manager():
    """Test logistics manager"""
    print("Testing Logistics Manager...")
    
    try:
        from app.services.logistics_manager import LogisticsManager
        
        service = LogisticsManager()
        
        # Test route optimization
        result = service.optimize_transport_route("usa", "europe", "crude_oil", 1000000)
        assert "routes" in result, "Route optimization should return routes"
        assert "optimal_route" in result, "Should return optimal route"
        
        # Test storage planning
        storage_result = service.plan_storage_allocation("crude_oil", 1000000, "rotterdam", 30)
        assert "storage_options" in storage_result, "Storage planning should return options"
        assert "total_storage_cost" in storage_result, "Should calculate storage costs"
        
        # Test carbon footprint
        carbon_result = service.calculate_carbon_footprint({
            "distance": 5000,
            "transport_mode": "ship",
            "quantity": 1000000
        })
        assert "total_emissions_kg" in carbon_result, "Should calculate emissions"
        
        print("✅ Logistics Manager tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Logistics Manager tests failed: {e}")
        return False

def test_inventory_manager():
    """Test inventory manager"""
    print("Testing Inventory Manager...")
    
    try:
        from app.services.inventory_manager import InventoryManager
        
        service = InventoryManager()
        
        # Test adding inventory
        result = service.add_inventory("crude_oil", 1000000, "rotterdam")
        assert result["success"] == True, "Inventory should be added successfully"
        
        # Test inventory status
        status = service.get_inventory_status("crude_oil", "rotterdam")
        assert len(status) > 0, "Should return inventory status"
        
        # Test storage optimization
        opt_result = service.optimize_storage_allocation(["crude_oil", "natural_gas"], 5000000)
        assert "allocations" in opt_result, "Should return storage allocations"
        
        print("✅ Inventory Manager tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Inventory Manager tests failed: {e}")
        return False

def test_regional_pricing():
    """Test regional pricing engine"""
    print("Testing Regional Pricing Engine...")
    
    try:
        from app.services.regional_pricing_engine import RegionalPricingEngine
        
        engine = RegionalPricingEngine()
        
        # Test regional pricing
        result = engine.calculate_regional_price("crude_oil", "middle_east")
        assert result["success"] == True, "Regional pricing should succeed"
        assert "final_price" in result, "Should return final price"
        
        # Test basis differential
        basis_result = engine.calculate_basis_differential("crude_oil", "usa", "europe")
        assert basis_result["success"] == True, "Basis calculation should succeed"
        assert "basis_differential" in basis_result, "Should return basis differential"
        
        # Test market summary
        summary = engine.get_market_summary("crude_oil")
        assert summary["success"] == True, "Market summary should succeed"
        assert "statistics" in summary, "Should return market statistics"
        
        print("✅ Regional Pricing Engine tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Regional Pricing Engine tests failed: {e}")
        return False

def test_compliance_engine():
    """Test compliance engine"""
    print("Testing Compliance Engine...")
    
    try:
        from app.services.compliance_engine import ComplianceEngine
        
        engine = ComplianceEngine()
        
        # Test position compliance
        positions = [
            {"notional_value": 5000000},  # $5M position
            {"notional_value": 3000000}   # $3M position
        ]
        
        result = engine.check_position_compliance(positions, 8000000)
        assert "compliant" in result, "Should return compliance status"
        
        # Test audit logging
        log_result = engine.log_audit_event("test_event", {"test": "data"})
        assert log_result["success"] == True, "Audit event should be logged"
        
        # Test regulatory updates
        updates = engine.check_regulatory_updates("usa")
        assert "updates" in updates, "Should return regulatory updates"
        
        print("✅ Compliance Engine tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Compliance Engine tests failed: {e}")
        return False

def main():
    """Run all Phase 1 stub tests"""
    print("🚀 Testing Phase 1 ETRM/CTRM Stubs")
    print("=" * 50)
    
    tests = [
        test_sharia_engine,
        test_deal_capture,
        test_position_manager,
        test_market_risk_engine,
        test_logistics_manager,
        test_inventory_manager,
        test_regional_pricing,
        test_compliance_engine
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Phase 1 stubs are working correctly!")
        return True
    else:
        print("⚠️  Some stubs need attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
