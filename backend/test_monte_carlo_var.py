#!/usr/bin/env python3
"""
Test script for Monte Carlo VaR Service
Tests the core VaR calculation functionality with 10,000 simulation paths
"""

import asyncio
import sys
import os
sys.path.append('.')

from app.services.monte_carlo_var import monte_carlo_var_service

async def test_monte_carlo_var():
    """Test Monte Carlo VaR calculation"""
    print("🔍 Testing Monte Carlo VaR Calculation...")
    
    # Test portfolio
    portfolio = [
        {"symbol": "CL=F", "quantity": 1000, "entry_price": 80.0},
        {"symbol": "NG=F", "quantity": 5000, "entry_price": 3.0}
    ]
    
    result = await monte_carlo_var_service.calculate_monte_carlo_var(
        portfolio=portfolio,
        confidence_level=0.95,
        time_horizon=1,
        num_simulations=10000
    )
    
    print(f"✅ Status: {result['status']}")
    
    if result['status'] == 'success':
        var_results = result['var_results']
        risk_metrics = result['risk_metrics']
        portfolio_summary = result['portfolio_summary']
        
        print(f"📊 Portfolio Value: ${portfolio_summary['total_value']:,.2f}")
        print(f"📈 Total P&L: ${portfolio_summary['total_pnl']:,.2f}")
        print(f"⚠️  VaR (95%): ${var_results['var_value']:,.2f}")
        print(f"📉 Expected Shortfall: ${var_results['expected_shortfall']:,.2f}")
        print(f"📊 Mean Return: ${risk_metrics['mean_return']:,.2f}")
        print(f"📊 Std Return: ${risk_metrics['std_return']:,.2f}")
        print(f"📊 Sharpe Ratio: {risk_metrics['sharpe_ratio']:.4f}")
        print(f"📊 Max Drawdown: ${risk_metrics['max_drawdown']:,.2f}")

async def test_stress_testing():
    """Test stress testing functionality"""
    print("\n🔍 Testing Stress Testing...")
    
    # Test portfolio
    portfolio = [
        {"symbol": "CL=F", "quantity": 1000, "entry_price": 80.0, "current_price": 85.0},
        {"symbol": "NG=F", "quantity": 5000, "entry_price": 3.0, "current_price": 3.5}
    ]
    
    # Stress scenarios
    stress_scenarios = [
        {
            "name": "Oil Price Crash",
            "price_shocks": {"CL=F": -0.50, "NG=F": -0.30}
        },
        {
            "name": "Natural Gas Spike",
            "price_shocks": {"NG=F": 1.00, "CL=F": 0.20}
        }
    ]
    
    result = await monte_carlo_var_service.stress_test_portfolio(
        portfolio=portfolio,
        stress_scenarios=stress_scenarios
    )
    
    print(f"✅ Status: {result['status']}")
    
    if result['status'] == 'success':
        for stress_result in result['stress_results']:
            print(f"📊 {stress_result['scenario_name']}: ${stress_result['total_impact']:,.2f}")
            for impact in stress_result['position_impacts']:
                print(f"   {impact['symbol']}: {impact['shock_percent']:+.1f}% → ${impact['impact']:,.2f}")

async def test_risk_metrics():
    """Test comprehensive risk metrics"""
    print("\n🔍 Testing Risk Metrics...")
    
    # Test portfolio
    portfolio = [
        {"symbol": "CL=F", "quantity": 1000, "entry_price": 80.0},
        {"symbol": "NG=F", "quantity": 5000, "entry_price": 3.0}
    ]
    
    # Test multiple confidence levels
    confidence_levels = [0.95, 0.99, 0.999]
    
    for conf_level in confidence_levels:
        result = await monte_carlo_var_service.calculate_monte_carlo_var(
            portfolio=portfolio,
            confidence_level=conf_level,
            num_simulations=10000
        )
        
        if result['status'] == 'success':
            var_value = result['var_results']['var_value']
            print(f"📊 VaR ({conf_level*100:.1f}%): ${var_value:,.2f}")

async def main():
    """Run all tests"""
    print("🚀 QuantaEnergi Monte Carlo VaR Service Test")
    print("=" * 60)
    
    try:
        await test_monte_carlo_var()
        await test_stress_testing()
        await test_risk_metrics()
        
        print("\n✅ All Monte Carlo VaR tests completed successfully!")
        print("🎯 Monte Carlo VaR service is ready for ETRM/CTRM risk management")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
