"""
Test script for Phase 2: Advanced ETRM Features & Market Expansion
Tests all stub services for options, structured products, algorithmic trading, quantum optimization, advanced risk, and supply chain
"""

import sys
import os
from datetime import datetime, timedelta

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.options import OptionsEngine, IslamicOptionsValidator
from app.services.structured_products import StructuredProductsEngine, IslamicStructuredValidator
from app.services.algo_trading import AlgorithmicTradingEngine, IslamicAlgoValidator
from app.services.quantum_optimizer import QuantumPortfolioOptimizer, QuantumComplianceValidator
from app.services.advanced_risk import AdvancedRiskAnalytics, IslamicRiskValidator
from app.services.supply_chain import SupplyChainManager, IslamicSupplyChainValidator


def test_options_engine():
    """Test OptionsEngine functionality"""
    print("🔧 Testing OptionsEngine...")
    
    try:
        engine = OptionsEngine()
        
        # Test option pricing
        option_spec = {
            "underlying": "crude_oil",
            "strike": 80.0,
            "expiry": "2025-06-01",
            "type": "call"
        }
        result = engine.price_option(option_spec)
        assert result["status"] == "priced"
        assert result["islamic_compliant"] == True
        print("  ✅ Option pricing works")
        
        # Test arbun premium calculation
        arbun_result = engine.calculate_arbun_premium(85.0, 80.0, 0.5, 0.25)
        assert arbun_result["islamic_compliant"] == True
        assert "arbun_premium" in arbun_result
        print("  ✅ Arbun premium calculation works")
        
        # Test Islamic structure validation
        validation_result = engine.validate_islamic_structure(option_spec)
        assert validation_result["islamic_compliant"] == True
        print("  ✅ Islamic structure validation works")
        
        # Test option execution
        execution_result = engine.execute_option_trade("OPT_001", {"quantity": 1000})
        assert execution_result["status"] == "executed"
        print("  ✅ Option execution works")
        
        # Test portfolio retrieval
        portfolio_result = engine.get_option_portfolio("user123")
        assert "total_options" in portfolio_result
        print("  ✅ Portfolio retrieval works")
        
        print("  🎯 OptionsEngine tests passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ OptionsEngine tests failed: {str(e)}")
        return False


def test_structured_products_engine():
    """Test StructuredProductsEngine functionality"""
    print("🔧 Testing StructuredProductsEngine...")
    
    try:
        engine = StructuredProductsEngine()
        
        # Test product creation
        product_spec = {
            "type": "murabaha_plus",
            "commodity": "crude_oil",
            "notional": 1000000.0,
            "tenor": "12M"
        }
        result = engine.create_structured_product(product_spec)
        assert result["status"] == "created"
        assert result["islamic_compliant"] == True
        print("  ✅ Product creation works")
        
        # Test product pricing
        pricing_result = engine.price_structured_product("SP_001", {"market_price": 85.0})
        assert "current_price" in pricing_result
        print("  ✅ Product pricing works")
        
        # Test payoff profile calculation
        scenarios = [{"name": "Base Case"}, {"name": "Upside"}, {"name": "Downside"}]
        payoff_result = engine.calculate_payoff_profile("SP_001", scenarios)
        assert "payoff_profile" in payoff_result
        print("  ✅ Payoff profile calculation works")
        
        # Test Islamic compliance validation
        compliance_result = engine.validate_islamic_compliance(product_spec)
        assert compliance_result["islamic_compliant"] == True
        print("  ✅ Islamic compliance validation works")
        
        # Test trade execution
        execution_result = engine.execute_structured_trade("SP_001", {"counterparty": "Bank_ABC"})
        assert execution_result["status"] == "executed"
        print("  ✅ Trade execution works")
        
        # Test portfolio retrieval
        portfolio_result = engine.get_product_portfolio("user123")
        assert "total_products" in portfolio_result
        print("  ✅ Portfolio retrieval works")
        
        print("  🎯 StructuredProductsEngine tests passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ StructuredProductsEngine tests failed: {str(e)}")
        return False


def test_algo_trading_engine():
    """Test AlgorithmicTradingEngine functionality"""
    print("🔧 Testing AlgorithmicTradingEngine...")
    
    try:
        engine = AlgorithmicTradingEngine()
        
        # Test algorithm execution
        algo_spec = {
            "strategy": "twap",
            "commodity": "crude_oil",
            "quantity": 1000000.0,
            "duration": 60
        }
        result = engine.execute_algorithm(algo_spec)
        assert result["status"] == "executed"
        assert result["islamic_compliant"] == True
        print("  ✅ Algorithm execution works")
        
        # Test VWAP calculation
        orders = [{"volume": 100000, "price": 85.0}, {"volume": 200000, "price": 85.5}]
        vwap_result = engine.calculate_vwap(orders)
        assert "vwap" in vwap_result
        print("  ✅ VWAP calculation works")
        
        # Test TWAP strategy execution
        twap_params = {
            "total_quantity": 1000000.0,
            "duration_minutes": 60,
            "slice_interval": 5
        }
        twap_result = engine.execute_twap_strategy(twap_params)
        assert twap_result["status"] == "executing"
        print("  ✅ TWAP strategy execution works")
        
        # Test order sizing optimization
        market_data = {"volatility": 0.02, "liquidity": "high"}
        risk_params = {"max_impact": 0.001}
        sizing_result = engine.optimize_order_sizing(market_data, 1000000.0, risk_params)
        assert "optimal_slice_size" in sizing_result
        print("  ✅ Order sizing optimization works")
        
        # Test execution quality monitoring
        quality_result = engine.monitor_execution_quality("ALGO_001")
        assert "quality_score" in quality_result
        print("  ✅ Execution quality monitoring works")
        
        # Test strategy performance
        performance_result = engine.get_strategy_performance("twap")
        assert "total_trades" in performance_result
        print("  ✅ Strategy performance retrieval works")
        
        print("  🎯 AlgorithmicTradingEngine tests passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ AlgorithmicTradingEngine tests failed: {str(e)}")
        return False


def test_quantum_optimizer():
    """Test QuantumPortfolioOptimizer functionality"""
    print("🔧 Testing QuantumPortfolioOptimizer...")
    
    try:
        optimizer = QuantumPortfolioOptimizer()
        
        # Test portfolio optimization
        portfolio_data = {"assets": ["crude_oil", "natural_gas"], "weights": [0.6, 0.4]}
        optimization_params = {"method": "quantum_annealing", "risk_tolerance": "moderate"}
        result = optimizer.optimize_portfolio(portfolio_data, optimization_params)
        assert result["constraints_satisfied"] == True
        assert result["islamic_compliant"] == True
        print("  ✅ Portfolio optimization works")
        
        # Test quantum annealing
        problem_data = {"variables": [1, 0, 1, 0, 1]}
        annealing_result = optimizer.quantum_anneal_optimization(problem_data)
        assert annealing_result["quantum_advantage"] == True
        print("  ✅ Quantum annealing works")
        
        # Test quantum advantage calculation
        classical_result = {"execution_time_ms": 1000, "solution_quality": 0.8}
        quantum_result = {"execution_time_ms": 150, "solution_quality": 0.95}
        advantage_result = optimizer.calculate_quantum_advantage(classical_result, quantum_result)
        assert advantage_result["quantum_advantage"] == True
        print("  ✅ Quantum advantage calculation works")
        
        # Test risk parity optimization
        assets = [{"id": "asset1"}, {"id": "asset2"}]
        risk_parity_result = optimizer.optimize_risk_parity(assets, 0.1)
        assert risk_parity_result["islamic_compliant"] == True
        print("  ✅ Risk parity optimization works")
        
        # Test multi-objective optimization
        objectives = ["return", "risk", "liquidity"]
        constraints = {"max_risk": 0.15}
        multi_obj_result = optimizer.multi_objective_optimization(objectives, constraints)
        assert multi_obj_result["constraints_satisfied"] == True
        print("  ✅ Multi-objective optimization works")
        
        # Test portfolio rebalancing
        current_portfolio = {"crude_oil": 0.6, "natural_gas": 0.4}
        target_allocation = {"crude_oil": 0.5, "natural_gas": 0.5}
        rebalancing_result = optimizer.quantum_portfolio_rebalancing(current_portfolio, target_allocation)
        assert rebalancing_result["islamic_compliant"] == True
        print("  ✅ Portfolio rebalancing works")
        
        # Test performance retrieval
        performance_result = optimizer.get_optimization_performance()
        assert "total_optimizations" in performance_result
        print("  ✅ Performance retrieval works")
        
        print("  🎯 QuantumPortfolioOptimizer tests passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ QuantumPortfolioOptimizer tests failed: {str(e)}")
        return False


def test_advanced_risk_analytics():
    """Test AdvancedRiskAnalytics functionality"""
    print("🔧 Testing AdvancedRiskAnalytics...")
    
    try:
        analytics = AdvancedRiskAnalytics()
        
        # Test Monte Carlo VaR
        portfolio_data = {"positions": [{"asset": "crude_oil", "value": 1000000}]}
        var_result = analytics.monte_carlo_var(portfolio_data, 1000, 0.95)
        assert var_result["method"] == "monte_carlo"
        assert "var_results" in var_result
        print("  ✅ Monte Carlo VaR works")
        
        # Test stress testing
        scenarios = [{"name": "Market Crash"}, {"name": "Oil Shock"}]
        stress_result = analytics.stress_test_portfolio(portfolio_data, scenarios)
        assert "num_scenarios" in stress_result
        print("  ✅ Stress testing works")
        
        # Test correlation matrix calculation
        assets = ["crude_oil", "natural_gas", "refined_products"]
        correlation_result = analytics.calculate_correlation_matrix(assets)
        assert "correlation_matrix" in correlation_result
        print("  ✅ Correlation matrix calculation works")
        
        # Test portfolio volatility calculation
        volatility_result = analytics.calculate_portfolio_volatility(portfolio_data)
        assert "portfolio_volatility" in volatility_result
        print("  ✅ Portfolio volatility calculation works")
        
        # Test credit risk metrics
        counterparties = [{"id": "cp1"}, {"id": "cp2"}]
        exposures = {"cp1": 500000, "cp2": 300000}
        credit_result = analytics.calculate_credit_risk_metrics(counterparties, exposures)
        assert "total_exposure" in credit_result
        print("  ✅ Credit risk metrics calculation works")
        
        # Test liquidity risk calculation
        market_conditions = {"volatility": 0.02, "liquidity": "high"}
        liquidity_result = analytics.calculate_liquidity_risk(portfolio_data, market_conditions)
        assert "portfolio_liquidity_score" in liquidity_result
        print("  ✅ Liquidity risk calculation works")
        
        # Test risk report generation
        risk_metrics = {"var_95": 125000, "volatility": 0.15, "sharpe_ratio": 1.2}
        report_result = analytics.generate_risk_report(portfolio_data, risk_metrics)
        assert "report_type" in report_result
        print("  ✅ Risk report generation works")
        
        print("  🎯 AdvancedRiskAnalytics tests passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ AdvancedRiskAnalytics tests failed: {str(e)}")
        return False


def test_supply_chain_manager():
    """Test SupplyChainManager functionality"""
    print("🔧 Testing SupplyChainManager...")
    
    try:
        manager = SupplyChainManager()
        
        # Test supply chain optimization
        supply_chain_data = {
            "nodes": ["saudi_arabia", "rotterdam"],
            "commodities": ["crude_oil"],
            "volumes": [1000000.0]
        }
        optimization_result = manager.optimize_supply_chain(supply_chain_data)
        assert "optimization_id" in optimization_result
        print("  ✅ Supply chain optimization works")
        
        # Test blending optimization
        crude_specs = [
            {"id": "crude1", "price": 80.0, "sulfur": 2.5, "api_gravity": 35.0},
            {"id": "crude2", "price": 82.0, "sulfur": 1.8, "api_gravity": 38.0}
        ]
        target_specs = {"sulfur": 2.0, "api_gravity": 36.0}
        blending_result = manager.optimize_blending_operations(crude_specs, target_specs)
        assert "blending_id" in blending_result
        print("  ✅ Blending optimization works")
        
        # Test inventory placement optimization
        demand_forecast = {"regions": [{"name": "europe", "demand": 1000000}]}
        supply_sources = [{"id": "source1", "capacity": 2000000}]
        inventory_result = manager.optimize_inventory_placement(demand_forecast, supply_sources)
        assert "placement_id" in inventory_result
        print("  ✅ Inventory placement optimization works")
        
        # Test transport optimization
        transport_result = manager.calculate_transport_optimization(
            "saudi_arabia", "rotterdam", "crude_oil", 1000000.0
        )
        assert "transport_id" in transport_result
        print("  ✅ Transport optimization works")
        
        # Test storage allocation optimization
        storage_facilities = [{"id": "facility1", "capacity": 1000000, "cost_per_unit": 0.05}]
        inventory_requirements = {"crude_oil": {"quantity": 500000}}
        storage_result = manager.optimize_storage_allocation(storage_facilities, inventory_requirements)
        assert "allocation_id" in storage_result
        print("  ✅ Storage allocation optimization works")
        
        # Test carbon footprint calculation
        carbon_result = manager.calculate_carbon_footprint(supply_chain_data)
        assert "emissions_intensity" in carbon_result
        print("  ✅ Carbon footprint calculation works")
        
        # Test report generation
        report_result = manager.generate_supply_chain_report(supply_chain_data)
        assert "report_type" in report_result
        print("  ✅ Report generation works")
        
        print("  🎯 SupplyChainManager tests passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ SupplyChainManager tests failed: {str(e)}")
        return False


def test_islamic_validators():
    """Test Islamic compliance validators"""
    print("🔧 Testing Islamic Compliance Validators...")
    
    try:
        # Test Islamic Options Validator
        options_validator = IslamicOptionsValidator()
        arbun_result = options_validator.validate_arbun_structure({"type": "arbun"})
        assert arbun_result["valid"] == True
        print("  ✅ Islamic Options Validator works")
        
        # Test Islamic Structured Validator
        structured_validator = IslamicStructuredValidator()
        murabaha_result = structured_validator.validate_murabaha_structure({"type": "murabaha"})
        assert murabaha_result["valid"] == True
        print("  ✅ Islamic Structured Validator works")
        
        # Test Islamic Algo Validator
        algo_validator = IslamicAlgoValidator()
        strategy_result = algo_validator.validate_algo_strategy({"strategy": "twap"})
        assert strategy_result["islamic_compliant"] == True
        print("  ✅ Islamic Algo Validator works")
        
        # Test Quantum Compliance Validator
        quantum_validator = QuantumComplianceValidator()
        solution_result = quantum_validator.validate_quantum_solution({"method": "quantum_annealing"})
        assert solution_result["islamic_compliant"] == True
        print("  ✅ Quantum Compliance Validator works")
        
        # Test Islamic Risk Validator
        risk_validator = IslamicRiskValidator()
        compliance_result = risk_validator.validate_risk_compliance({"var_95": 100000})
        assert compliance_result["islamic_compliant"] == True
        print("  ✅ Islamic Risk Validator works")
        
        # Test Islamic Supply Chain Validator
        supply_chain_validator = IslamicSupplyChainValidator()
        supply_chain_compliance = supply_chain_validator.validate_supply_chain_compliance({"type": "logistics"})
        assert supply_chain_compliance["islamic_compliant"] == True
        print("  ✅ Islamic Supply Chain Validator works")
        
        print("  🎯 Islamic Compliance Validators tests passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ Islamic Compliance Validators tests failed: {str(e)}")
        return False


def main():
    """Run all Phase 2 tests"""
    print("🚀 Starting Phase 2: Advanced ETRM Features & Market Expansion Tests")
    print("=" * 80)
    
    test_results = []
    
    # Run all tests
    test_results.append(("OptionsEngine", test_options_engine()))
    test_results.append(("StructuredProductsEngine", test_structured_products_engine()))
    test_results.append(("AlgorithmicTradingEngine", test_algo_trading_engine()))
    test_results.append(("QuantumPortfolioOptimizer", test_quantum_optimizer()))
    test_results.append(("AdvancedRiskAnalytics", test_advanced_risk_analytics()))
    test_results.append(("SupplyChainManager", test_supply_chain_manager()))
    test_results.append(("Islamic Compliance Validators", test_islamic_validators()))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 PHASE 2 TEST RESULTS SUMMARY")
    print("=" * 80)
    
    passed = 0
    total = len(test_results)
    
    for service_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{service_name:<30} {status}")
        if result:
            passed += 1
    
    print("-" * 80)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL PHASE 2 TESTS PASSED! 🎉")
        print("Phase 2: Advanced ETRM Features & Market Expansion is ready!")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please review and fix issues.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
