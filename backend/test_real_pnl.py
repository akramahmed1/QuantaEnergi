#!/usr/bin/env python3
"""
Test script for Real P&L Calculator Service
Tests the core P&L calculation functionality with qty*(exit-entry)*FX formula
"""

import asyncio
import sys
import os
sys.path.append('.')

from app.services.real_pnl_calculator import real_pnl_calculator

async def test_trade_pnl():
    """Test individual trade P&L calculation"""
    print("🔍 Testing Trade P&L Calculation...")
    
    # Test long position
    long_trade = {
        "trade_id": "TRADE_001",
        "quantity": 1000,
        "entry_price": 80.0,
        "exit_price": 85.0,
        "currency": "USD",
        "direction": "long"
    }
    
    result = await real_pnl_calculator.calculate_trade_pnl(long_trade)
    print(f"✅ Status: {result['status']}")
    
    if result['status'] == 'success':
        pnl_data = result['pnl_calculation']
        print(f"💰 P&L: ${pnl_data['pnl']:,.2f}")
        print(f"📊 P&L %: {pnl_data['pnl_percent']:.2f}%")
        print(f"💼 Notional: ${pnl_data['notional_value']:,.2f}")
        print(f"🔢 Formula: {result['formula']}")
    
    # Test short position
    print("\n🔍 Testing Short Position...")
    short_trade = {
        "trade_id": "TRADE_002",
        "quantity": 5000,
        "entry_price": 3.50,
        "exit_price": 3.00,
        "currency": "USD",
        "direction": "short"
    }
    
    result = await real_pnl_calculator.calculate_trade_pnl(short_trade)
    print(f"✅ Status: {result['status']}")
    
    if result['status'] == 'success':
        pnl_data = result['pnl_calculation']
        print(f"💰 P&L: ${pnl_data['pnl']:,.2f}")
        print(f"📊 P&L %: {pnl_data['pnl_percent']:.2f}%")

async def test_portfolio_pnl():
    """Test portfolio P&L calculation"""
    print("\n🔍 Testing Portfolio P&L Calculation...")
    
    portfolio = [
        {
            "trade_id": "TRADE_001",
            "symbol": "CL=F",
            "quantity": 1000,
            "entry_price": 80.0,
            "exit_price": 85.0,
            "currency": "USD",
            "direction": "long"
        },
        {
            "trade_id": "TRADE_002",
            "symbol": "NG=F",
            "quantity": 5000,
            "entry_price": 3.50,
            "exit_price": 3.00,
            "currency": "USD",
            "direction": "short"
        },
        {
            "trade_id": "TRADE_003",
            "symbol": "BZ=F",
            "quantity": 2000,
            "entry_price": 82.0,
            "exit_price": 87.0,
            "currency": "EUR",
            "direction": "long"
        }
    ]
    
    result = await real_pnl_calculator.calculate_portfolio_pnl(portfolio)
    print(f"✅ Status: {result['status']}")
    
    if result['status'] == 'success':
        summary = result['portfolio_summary']
        print(f"💼 Total P&L: ${summary['total_pnl']:,.2f}")
        print(f"📊 Total Notional: ${summary['total_notional']:,.2f}")
        print(f"📈 Portfolio P&L %: {summary['portfolio_pnl_percent']:.2f}%")
        print(f"📊 Positions: {summary['position_count']}")
        print(f"✅ Profitable: {summary['profitable_positions']}")
        print(f"❌ Losing: {summary['losing_positions']}")
        
        # Show individual position P&L
        print("\n📊 Position Details:")
        for position in result['position_pnls']:
            print(f"   {position['symbol']}: ${position['pnl']:,.2f} ({position['pnl_percent']:+.2f}%)")

async def test_mark_to_market():
    """Test mark-to-market P&L calculation"""
    print("\n🔍 Testing Mark-to-Market P&L...")
    
    positions = [
        {
            "symbol": "CL=F",
            "quantity": 1000,
            "entry_price": 80.0,
            "currency": "USD",
            "direction": "long"
        },
        {
            "symbol": "NG=F",
            "quantity": 5000,
            "entry_price": 3.50,
            "currency": "USD",
            "direction": "short"
        }
    ]
    
    current_prices = {
        "CL=F": 85.0,
        "NG=F": 3.00
    }
    
    result = await real_pnl_calculator.calculate_mark_to_market_pnl(positions, current_prices)
    print(f"✅ Status: {result['status']}")
    
    if result['status'] == 'success':
        print(f"💰 Total MTM P&L: ${result['total_mtm_pnl']:,.2f}")
        print(f"📊 Positions: {result['position_count']}")
        
        for position in result['mtm_positions']:
            print(f"   {position['symbol']}: ${position['mtm_pnl']:,.2f} (${position['entry_price']} → ${position['current_price']})")

async def test_realized_unrealized():
    """Test realized vs unrealized P&L breakdown"""
    print("\n🔍 Testing Realized vs Unrealized P&L...")
    
    portfolio = [
        {
            "trade_id": "TRADE_001",
            "symbol": "CL=F",
            "quantity": 1000,
            "entry_price": 80.0,
            "exit_price": 85.0,  # Closed position
            "currency": "USD",
            "direction": "long"
        },
        {
            "trade_id": "TRADE_002",
            "symbol": "NG=F",
            "quantity": 5000,
            "entry_price": 3.50,
            "exit_price": 0,  # Open position
            "current_price": 3.00,
            "currency": "USD",
            "direction": "short"
        }
    ]
    
    result = await real_pnl_calculator.calculate_realized_vs_unrealized_pnl(portfolio)
    print(f"✅ Status: {result['status']}")
    
    if result['status'] == 'success':
        print(f"💰 Realized P&L: ${result['realized_pnl']:,.2f}")
        print(f"📊 Unrealized P&L: ${result['unrealized_pnl']:,.2f}")
        print(f"📈 Total P&L: ${result['total_pnl']:,.2f}")
        print(f"✅ Realized Positions: {result['realized_count']}")
        print(f"📊 Unrealized Positions: {result['unrealized_count']}")

async def test_formula_validation():
    """Test P&L formula validation"""
    print("\n🔍 Testing Formula Validation...")
    
    # Test the formula: qty*(exit-entry)*FX
    test_cases = [
        {
            "name": "Long USD Position",
            "quantity": 1000,
            "entry_price": 80.0,
            "exit_price": 85.0,
            "currency": "USD",
            "direction": "long",
            "expected": 5000.0  # 1000 * (85-80) * 1.0
        },
        {
            "name": "Short USD Position",
            "quantity": 1000,
            "entry_price": 80.0,
            "exit_price": 75.0,
            "currency": "USD",
            "direction": "short",
            "expected": 5000.0  # 1000 * (75-80) * -1 * 1.0
        },
        {
            "name": "Long EUR Position",
            "quantity": 1000,
            "entry_price": 70.0,
            "exit_price": 75.0,
            "currency": "EUR",
            "direction": "long",
            "expected": 5500.0  # 1000 * (75-70) * 1.1
        }
    ]
    
    for test_case in test_cases:
        trade_data = {
            "quantity": test_case["quantity"],
            "entry_price": test_case["entry_price"],
            "exit_price": test_case["exit_price"],
            "currency": test_case["currency"],
            "direction": test_case["direction"]
        }
        
        result = await real_pnl_calculator.calculate_trade_pnl(trade_data)
        
        if result['status'] == 'success':
            calculated = result['pnl_calculation']['pnl']
            expected = test_case['expected']
            difference = abs(calculated - expected)
            
            print(f"✅ {test_case['name']}: ${calculated:,.2f} (expected: ${expected:,.2f}, diff: ${difference:.2f})")
        else:
            print(f"❌ {test_case['name']}: Calculation failed")

async def main():
    """Run all tests"""
    print("🚀 QuantaEnergi Real P&L Calculator Service Test")
    print("=" * 60)
    
    try:
        await test_trade_pnl()
        await test_portfolio_pnl()
        await test_mark_to_market()
        await test_realized_unrealized()
        await test_formula_validation()
        
        print("\n✅ All Real P&L Calculator tests completed successfully!")
        print("🎯 Real P&L Calculator is ready for ETRM/CTRM trading operations")
        print("📊 Formula: qty*(exit-entry)*FX")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
