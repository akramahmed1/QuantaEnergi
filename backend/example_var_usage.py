#!/usr/bin/env python3
"""
Example usage of VaR calculator for QuantaEnergi
Demonstrates how to use the risk.py service for VaR calculations
"""

import sys
import os
import numpy as np
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.risk import calculate_var, calculate_portfolio_var, stress_test_portfolio

def example_basic_var():
    """Example of basic VaR calculation"""
    print("🔍 Basic VaR Calculation Example")
    print("=" * 50)
    
    # Sample position returns (daily P&L)
    position_returns = [
        1000, -500, 2000, -800, 1500, -1200, 3000, -600, 1800, -900,
        2200, -400, 1600, -1100, 2500, -700, 1900, -500, 2100, -800
    ]
    
    # Calculate VaR at different confidence levels
    var_95 = calculate_var(position_returns, confidence=0.95)
    var_99 = calculate_var(position_returns, confidence=0.99)
    
    print(f"Position Returns: {len(position_returns)} data points")
    print(f"95% VaR: ${var_95:,.2f}")
    print(f"99% VaR: ${var_99:,.2f}")
    print(f"Mean Return: ${np.mean(position_returns):,.2f}")
    print(f"Std Dev: ${np.std(position_returns):,.2f}")
    print()

def example_portfolio_var():
    """Example of portfolio VaR calculation"""
    print("📊 Portfolio VaR Calculation Example")
    print("=" * 50)
    
    # Sample portfolio data
    portfolio_data = {
        'total_value': 10000000,  # $10M portfolio
        'positions': [
            {
                'commodity': 'crude_oil',
                'value': 4000000,  # $4M
                'volatility': 0.25,
                'quantity': 1000,
                'price': 80.0
            },
            {
                'commodity': 'natural_gas',
                'value': 3000000,  # $3M
                'volatility': 0.35,
                'quantity': 2000,
                'price': 3.0
            },
            {
                'commodity': 'electricity',
                'value': 2000000,  # $2M
                'volatility': 0.40,
                'quantity': 500,
                'price': 50.0
            },
            {
                'commodity': 'carbon_credits',
                'value': 1000000,  # $1M
                'volatility': 0.30,
                'quantity': 10000,
                'price': 25.0
            }
        ]
    }
    
    # Calculate portfolio VaR
    var_results = calculate_portfolio_var(portfolio_data, confidence=0.95)
    
    print(f"Portfolio Value: ${portfolio_data['total_value']:,}")
    print(f"Number of Positions: {len(portfolio_data['positions'])}")
    print()
    print("VaR Results:")
    print(f"  95% VaR: ${var_results['var_95']:,.2f}")
    print(f"  99% VaR: ${var_results['var_99']:,.2f}")
    print(f"  95% Expected Shortfall: ${var_results['expected_shortfall_95']:,.2f}")
    print(f"  99% Expected Shortfall: ${var_results['expected_shortfall_99']:,.2f}")
    print(f"  Portfolio Risk Score: {var_results['portfolio_risk_score']:.3f}")
    print()
    
    # ML insights
    if 'ml_insights' in var_results:
        ml_insights = var_results['ml_insights']
        print("ML Insights:")
        print(f"  ML Available: {ml_insights.get('ml_available', False)}")
        if ml_insights.get('ml_available'):
            print(f"  Predicted Risk: {ml_insights.get('predicted_risk', 0):.4f}")
            print(f"  Confidence: {ml_insights.get('confidence', 0):.2f}")
        print()

def example_stress_testing():
    """Example of stress testing"""
    print("⚡ Stress Testing Example")
    print("=" * 50)
    
    # Sample portfolio for stress testing
    portfolio_data = {
        'total_value': 50000000,  # $50M portfolio
        'positions': [
            {
                'commodity': 'crude_oil',
                'value': 25000000,  # $25M
                'volatility': 0.30
            },
            {
                'commodity': 'natural_gas',
                'value': 15000000,  # $15M
                'volatility': 0.40
            },
            {
                'commodity': 'electricity',
                'value': 10000000,  # $10M
                'volatility': 0.35
            }
        ]
    }
    
    # Define stress test scenarios
    scenarios = [
        'market_crash',
        'oil_price_shock',
        'interest_rate_spike',
        'currency_crisis',
        'liquidity_crisis'
    ]
    
    # Run stress tests
    stress_results = stress_test_portfolio(portfolio_data, scenarios)
    
    print(f"Portfolio Value: ${portfolio_data['total_value']:,}")
    print(f"Stress Test Scenarios: {len(scenarios)}")
    print()
    
    print("Stress Test Results:")
    for scenario, result in stress_results.get('stress_test_results', {}).items():
        if 'error' not in result:
            print(f"  {scenario.replace('_', ' ').title()}:")
            print(f"    Stress Factor: {result['stress_factor']:.1%}")
            print(f"    Original Value: ${result['original_value']:,}")
            print(f"    Stressed Value: ${result['stressed_value']:,}")
            print(f"    Loss Amount: ${result['loss_amount']:,}")
            print(f"    Loss Percentage: {result['loss_percentage']:.1f}%")
            print()
    
    print(f"Overall Stress Score: {stress_results.get('overall_stress_score', 0):.3f}")
    print()

def example_monte_carlo_simulation():
    """Example of Monte Carlo VaR simulation"""
    print("🎲 Monte Carlo VaR Simulation Example")
    print("=" * 50)
    
    # Generate synthetic portfolio returns using Monte Carlo
    np.random.seed(42)  # For reproducible results
    
    # Portfolio parameters
    portfolio_value = 10000000  # $10M
    expected_return = 0.08  # 8% annual return
    volatility = 0.20  # 20% annual volatility
    time_horizon = 1  # 1 day
    num_simulations = 10000
    
    # Generate random returns
    random_returns = np.random.normal(
        expected_return / 252,  # Daily expected return
        volatility / np.sqrt(252),  # Daily volatility
        num_simulations
    )
    
    # Calculate portfolio values
    portfolio_values = portfolio_value * (1 + random_returns)
    
    # Calculate VaR
    var_95 = calculate_var(portfolio_values.tolist(), confidence=0.95)
    var_99 = calculate_var(portfolio_values.tolist(), confidence=0.99)
    
    print(f"Portfolio Value: ${portfolio_value:,}")
    print(f"Expected Daily Return: {expected_return/252:.4f}")
    print(f"Daily Volatility: {volatility/np.sqrt(252):.4f}")
    print(f"Number of Simulations: {num_simulations:,}")
    print()
    print("Monte Carlo VaR Results:")
    print(f"  95% VaR: ${var_95:,.2f}")
    print(f"  99% VaR: ${var_99:,.2f}")
    print(f"  Worst Case (1%): ${np.percentile(portfolio_values, 1):,.2f}")
    print(f"  Best Case (99%): ${np.percentile(portfolio_values, 99):,.2f}")
    print()

def main():
    """Run all examples"""
    print("🚀 QuantaEnergi VaR Calculator Examples")
    print("=" * 60)
    print(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        example_basic_var()
        example_portfolio_var()
        example_stress_testing()
        example_monte_carlo_simulation()
        
        print("✅ All examples completed successfully!")
        print()
        print("📝 Usage Notes:")
        print("- VaR values are in the same units as input positions")
        print("- Confidence levels: 0.95 = 95% VaR, 0.99 = 99% VaR")
        print("- Negative VaR values indicate potential losses")
        print("- ML insights require the ensemble model to be available")
        print("- Stress testing uses predefined scenarios")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
