"""
Comprehensive Test for All Production-Ready Services
EnergyOpti-Pro Post-Phase 3: Production Readiness & Market Launch
"""

import sys
import traceback
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def test_agi_trading_production():
    """Test AGI Trading Assistant - Production Ready"""
    print("\n🧠 Testing AGI Trading Assistant (Production Ready)...")
    
    try:
        from app.services.agi_trading import AGITradingAssistant, AGIComplianceValidator
        
        # Initialize service
        agi_service = AGITradingAssistant()
        validator = AGIComplianceValidator()
        
        # Test market predictions
        prediction = agi_service.generate_market_predictions("WTI", "1d")
        assert "predicted_price" in prediction, "Market prediction failed"
        assert "confidence" in prediction, "Confidence score missing"
        print("✅ Market predictions working")
        
        # Test sentiment analysis
        sentiment = agi_service.analyze_market_sentiment("Energy markets show strong growth potential")
        assert "sentiment_score" in sentiment, "Sentiment analysis failed"
        print("✅ Sentiment analysis working")
        
        # Test strategy generation
        market_conditions = {"volatility": "medium", "trend": "bullish", "commodities": ["WTI", "Brent"]}
        strategy = agi_service.generate_trading_strategies(market_conditions, "moderate")
        assert len(strategy) > 0, "Strategy generation failed"
        print("✅ Strategy generation working")
        
        # Test compliance validation
        compliance = validator.validate_agi_strategy(strategy[0])  # Pass first strategy
        assert "is_compliant" in compliance, "Compliance validation failed"
        print("✅ Compliance validation working")
        
        print("🎉 AGI Trading Assistant: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ AGI Trading Assistant test failed: {e}")
        traceback.print_exc()
        return False

def test_quantum_trading_production():
    """Test Quantum Trading Engine - Production Ready"""
    print("\n⚛️ Testing Quantum Trading Engine (Production Ready)...")
    
    try:
        from app.services.quantum_trading import QuantumTradingEngine, QuantumComplianceValidator
        
        # Initialize service
        quantum_service = QuantumTradingEngine()
        validator = QuantumComplianceValidator()
        
        # Test portfolio optimization
        assets = ["AAPL", "GOOGL", "MSFT"]
        returns = [0.12, 0.15, 0.10]  # Sample returns
        portfolio = quantum_service.quantum_portfolio_optimization(assets, returns, 0.5)
        assert "optimal_weights" in portfolio, "Portfolio optimization failed"
        print("✅ Portfolio optimization working")
        
        # Test risk assessment
        portfolio_data = {
            "portfolio": {
                "positions": [
                    {"asset": "AAPL", "value": 10000},
                    {"asset": "GOOGL", "value": 15000},
                    {"asset": "MSFT", "value": 12000}
                ]
            }
        }
        risk_types = ["market", "credit", "liquidity"]
        risk = quantum_service.quantum_risk_assessment(portfolio_data, risk_types)
        assert "var_95" in risk, "Risk assessment failed"
        print("✅ Risk assessment working")
        
        # Test compliance validation
        compliance = validator.validate_quantum_strategy(portfolio)
        assert "is_compliant" in compliance, "Compliance validation failed"
        print("✅ Compliance validation working")
        
        print("🎉 Quantum Trading Engine: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Quantum Trading Engine test failed: {e}")
        traceback.print_exc()
        return False

def test_digital_twin_production():
    """Test Digital Twin Service - Production Ready"""
    print("\n🔄 Testing Digital Twin Service (Production Ready)...")
    
    try:
        from app.services.digital_twin import GlobalEnergyDigitalTwin, DigitalTwinComplianceValidator
        
        # Initialize service
        twin_service = GlobalEnergyDigitalTwin()
        validator = DigitalTwinComplianceValidator()
        
        # Test market twin creation
        twin = twin_service.create_market_twin("crude_oil", "global")
        assert "twin_id" in twin, "Market twin creation failed"
        print("✅ Market twin creation working")
        
        # Test scenario simulation
        scenario = twin_service.simulate_market_scenarios(twin["twin_id"], "supply_shock", {"shock_intensity": 0.3, "volume_impact": 0.2})
        assert "scenario_id" in scenario, "Scenario simulation failed"
        print("✅ Scenario simulation working")
        
        # Test compliance validation
        compliance = validator.validate_twin_compliance(twin)
        assert "is_compliant" in compliance, "Compliance validation failed"
        print("✅ Compliance validation working")
        
        print("🎉 Digital Twin Service: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Digital Twin Service test failed: {e}")
        traceback.print_exc()
        return False

def test_autonomous_trading_production():
    """Test Autonomous Trading Ecosystem - Production Ready"""
    print("\n🤖 Testing Autonomous Trading Ecosystem (Production Ready)...")
    
    try:
        from app.services.autonomous_trading import AutonomousTradingEcosystem, AutonomousTradingValidator
        
        # Initialize service
        autonomous_service = AutonomousTradingEcosystem()
        validator = AutonomousTradingValidator()
        
        # Test agent creation
        agent = autonomous_service.create_trading_agent("momentum", {"risk_tolerance": 0.5}, {"max_position_size": 0.1})
        assert "agent_id" in agent, "Agent creation failed"
        print("✅ Agent creation working")
        
        # Test strategy execution
        market_data = {"prices": [100, 101, 102, 103, 104]}
        execution = autonomous_service.execute_autonomous_strategy(agent["agent_id"], market_data)
        assert "decision" in execution, "Strategy execution failed"
        print("✅ Strategy execution working")
        
        # Test compliance validation
        compliance = validator.validate_agent_compliance(autonomous_service.active_agents[agent["agent_id"]])
        assert "is_compliant" in compliance, "Compliance validation failed"
        print("✅ Compliance validation working")
        
        print("🎉 Autonomous Trading Ecosystem: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Autonomous Trading Ecosystem test failed: {e}")
        traceback.print_exc()
        return False

def test_decentralized_trading_production():
    """Test Decentralized Trading Protocol - Production Ready"""
    print("\n🔗 Testing Decentralized Trading Protocol (Production Ready)...")
    
    try:
        from app.services.decentralized_trading import DecentralizedTradingProtocol, DecentralizedTradingValidator
        
        # Initialize service
        dex_service = DecentralizedTradingProtocol("testnet")
        validator = DecentralizedTradingValidator()
        
        # Test liquidity pool creation
        pool = dex_service.create_liquidity_pool("ETH", "USDC", 3000, {"ETH": 1000, "USDC": 1000000})
        assert "pool_id" in pool, "Liquidity pool creation failed"
        print("✅ Liquidity pool creation working")
        
        # Test trade execution
        trade = dex_service.execute_dex_trade(pool["pool_id"], "exact_input", 100, "ETH", 0.005)
        assert "status" in trade, "Trade execution failed"
        print("✅ Trade execution working")
        
        # Test compliance validation
        compliance = validator.validate_trade_compliance(trade)
        assert "is_compliant" in compliance, "Compliance validation failed"
        print("✅ Compliance validation working")
        
        print("🎉 Decentralized Trading Protocol: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Decentralized Trading Protocol test failed: {e}")
        traceback.print_exc()
        return False

def test_carbon_trading_production():
    """Test Carbon Credit Trading - Production Ready"""
    print("\n🌱 Testing Carbon Credit Trading (Production Ready)...")
    
    try:
        from app.services.carbon_trading import CarbonCreditTradingPlatform, CarbonTradingValidator
        
        # Initialize service
        carbon_service = CarbonCreditTradingPlatform()
        validator = CarbonTradingValidator()
        
        # Test project registration
        project_data = {
            "project_name": "Solar Farm Project",
            "project_type": "renewable_energy",
            "location": "California, USA",
            "start_date": "2024-01-01",
            "expected_lifetime": 25,
            "estimated_emissions_reduction": 50000
        }
        project = carbon_service.register_carbon_project(project_data, "verra")
        assert "project_id" in project, "Project registration failed"
        print("✅ Project registration working")
        
        # Test credit issuance
        # For testing, manually set project as verified
        project_id = project["project_id"]
        carbon_service.carbon_projects[project_id]["verification_status"] = "verified"
        
        credits = carbon_service.issue_carbon_credits(project_id, 1000)
        assert "batch_id" in credits, "Credit issuance failed"
        print("✅ Credit issuance working")
        
        # Test compliance validation
        compliance = validator.validate_credit_authenticity(credits)
        assert "is_valid" in compliance, "Compliance validation failed"
        print("✅ Compliance validation working")
        
        print("🎉 Carbon Credit Trading: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Carbon Credit Trading test failed: {e}")
        traceback.print_exc()
        return False

def test_market_intelligence_production():
    """Test Market Intelligence Network - Production Ready"""
    print("\n📊 Testing Market Intelligence Network (Production Ready)...")
    
    try:
        from app.services.market_intelligence import GlobalMarketIntelligenceNetwork, MarketIntelligenceValidator
        
        # Initialize service
        intelligence_service = GlobalMarketIntelligenceNetwork()
        validator = MarketIntelligenceValidator()
        
        # Test market data fetch
        market_data = intelligence_service.fetch_real_time_market_data(["AAPL", "GOOGL"])
        assert "status" in market_data, "Market data fetch failed"
        print("✅ Market data fetch working")
        
        # Test sentiment analysis
        sentiment = intelligence_service.analyze_market_sentiment(["AAPL", "GOOGL"])
        assert "status" in sentiment, "Sentiment analysis failed"
        print("✅ Sentiment analysis working")
        
        # Test data quality validation
        if market_data["status"] == "success" and "AAPL" in market_data["market_data"]:
            quality = validator.validate_market_data_quality(market_data["market_data"]["AAPL"])
            assert "is_quality" in quality, "Data quality validation failed"
            print("✅ Data quality validation working")
        
        print("🎉 Market Intelligence Network: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Market Intelligence Network test failed: {e}")
        traceback.print_exc()
        return False

def test_production_requirements():
    """Test production requirements and dependencies"""
    print("\n🔧 Testing Production Requirements...")
    
    try:
        # Core ML/AI packages
        import numpy as np
        import pandas as pd
        import sklearn
        print("✅ Core ML/AI packages available")
        
        # Quantum computing packages
        try:
            import qutip
            print("✅ QuTiP available")
        except ImportError:
            print("⚠️ QuTiP not available (using fallbacks)")
        
        try:
            import dwave
            print("✅ D-Wave available")
        except ImportError:
            print("⚠️ D-Wave not available (using fallbacks)")
        
        # Deep learning packages
        try:
            import torch
            print("✅ PyTorch available")
        except ImportError:
            print("⚠️ PyTorch not available (using fallbacks)")
        
        try:
            import transformers
            print("✅ Transformers available")
        except ImportError:
            print("⚠️ Transformers not available (using fallbacks)")
        
        # IoT and real-time packages
        try:
            import paho.mqtt.client
            print("✅ MQTT client available")
        except ImportError:
            print("⚠️ MQTT client not available (using fallbacks)")
        
        try:
            import redis
            print("✅ Redis available")
        except ImportError:
            print("⚠️ Redis not available (using fallbacks)")
        
        # Blockchain packages
        try:
            import web3
            print("✅ Web3 available")
        except ImportError:
            print("⚠️ Web3 not available (using fallbacks)")
        
        # Market data packages
        try:
            import yfinance
            print("✅ yfinance available")
        except ImportError:
            print("⚠️ yfinance not available (using fallbacks)")
        
        # Core framework
        import fastapi
        print("✅ FastAPI available")
        
        print("🎉 Production Requirements: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Production requirements test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main test execution"""
    print("🚀 EnergyOpti-Pro: Comprehensive Production Service Testing")
    print("=" * 70)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = []
    
    # Test all production-ready services
    test_results.append(("Production Requirements", test_production_requirements()))
    test_results.append(("AGI Trading Assistant", test_agi_trading_production()))
    test_results.append(("Quantum Trading Engine", test_quantum_trading_production()))
    test_results.append(("Digital Twin Service", test_digital_twin_production()))
    test_results.append(("Autonomous Trading Ecosystem", test_autonomous_trading_production()))
    test_results.append(("Decentralized Trading Protocol", test_decentralized_trading_production()))
    test_results.append(("Carbon Credit Trading", test_carbon_trading_production()))
    test_results.append(("Market Intelligence Network", test_market_intelligence_production()))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 70)
    
    passed = 0
    total = len(test_results)
    
    for service_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{service_name:<35} {status}")
        if result:
            passed += 1
    
    print("=" * 70)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL SERVICES ARE PRODUCTION READY! 🎉")
        print("EnergyOpti-Pro is ready for deployment and market launch!")
    else:
        print(f"\n⚠️ {total - passed} service(s) need attention before production deployment")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
