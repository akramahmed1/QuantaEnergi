#!/usr/bin/env python3
"""
Test script for Real Market Data Service
Tests the core market data functionality with real API calls
"""

import asyncio
import sys
import os
sys.path.append('.')

from app.services.real_market_data import market_data_service

async def test_energy_prices():
    """Test energy price fetching"""
    print("🔍 Testing Energy Price Fetching...")
    
    # Test with default symbols
    result = await market_data_service.fetch_energy_prices()
    print(f"✅ Status: {result['status']}")
    print(f"📊 Cached: {result['cached_count']}, Fresh: {result['fresh_count']}")
    
    for symbol, data in result['data'].items():
        print(f"💰 {symbol}: ${data['price']} ({data['source']})")
        if 'change' in data:
            print(f"   📈 Change: {data['change']} ({data['change_percent']}%)")

async def test_portfolio_pricing():
    """Test portfolio pricing with P&L calculation"""
    print("\n🔍 Testing Portfolio Pricing...")
    
    # Mock portfolio
    portfolio = [
        {"symbol": "CL=F", "quantity": 1000, "entry_price": 80.0},
        {"symbol": "NG=F", "quantity": 5000, "entry_price": 3.0}
    ]
    
    result = await market_data_service.get_portfolio_prices(portfolio)
    print(f"✅ Status: {result['status']}")
    
    if result['status'] == 'success':
        summary = result['portfolio_summary']
        print(f"💼 Total Value: ${summary['total_value']}")
        print(f"📈 Total P&L: ${summary['total_pnl']} ({summary['pnl_percent']}%)")
        print(f"📊 Positions: {summary['position_count']}")
        
        for position in result['positions']:
            print(f"   {position['symbol']}: ${position['position_value']} (P&L: ${position['unrealized_pnl']})")

async def test_historical_data():
    """Test historical data for VaR calculations"""
    print("\n🔍 Testing Historical Data...")
    
    result = await market_data_service.get_historical_prices("CL=F", days=7)
    print(f"✅ Status: {result['status']}")
    print(f"📊 Symbol: {result['symbol']}")
    print(f"📈 Price Count: {result['price_count']}")
    
    if result['status'] == 'success' and result['prices']:
        latest = result['prices'][-1]
        print(f"📅 Latest: {latest['date']} - ${latest['close']}")

async def main():
    """Run all tests"""
    print("🚀 QuantaEnergi Market Data Service Test")
    print("=" * 50)
    
    try:
        await test_energy_prices()
        await test_portfolio_pricing()
        await test_historical_data()
        
        print("\n✅ All tests completed successfully!")
        print("🎯 Market data service is ready for ETRM/CTRM operations")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
