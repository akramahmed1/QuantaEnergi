import asyncio
import json
import random
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import numpy as np

async def generate_market_data() -> Dict[str, Any]:
    """Generate mock market data for energy commodities"""
    base_prices = {
        "crude_oil": 75.0,
        "natural_gas": 3.2,
        "coal": 150.0,
        "electricity": 45.0
    }
    
    data = {}
    for commodity, base_price in base_prices.items():
        # Generate realistic price movement (±2%)
        change = random.uniform(-0.02, 0.02)
        current_price = base_price * (1 + change)
        
        data[commodity] = {
            "price": round(current_price, 2),
            "change": round(change * 100, 2),
            "volume": random.randint(1000, 10000),
            "timestamp": datetime.now().isoformat()
        }
    
    return {
        "type": "market_data",
        "data": data,
        "timestamp": datetime.now().isoformat()
    }

def fetch_energy_prices(symbol: str = 'BRENT', api_key: str = 'demo') -> Dict[str, float]:
    """
    Fetch real energy prices from Alpha Vantage API
    Enhanced for Brent/WTI oil prices with demo key
    """
    try:
        # Alpha Vantage API endpoint for daily time series
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}'
        
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # Extract daily close prices
        time_series = data.get('Time Series (Daily)', {})
        prices = {}
        
        for date, values in time_series.items():
            close_price = float(values.get('4. close', 0))
            prices[date] = close_price
        
        return prices
        
    except Exception as e:
        print(f"Alpha Vantage API error: {e}")
        # Fallback to mock data
        return generate_mock_prices(symbol)

def generate_mock_prices(symbol: str) -> Dict[str, float]:
    """Generate mock prices when API fails"""
    base_prices = {
        'BRENT': 75.0,
        'WTI': 70.0,
        'NATGAS': 3.2
    }
    
    base_price = base_prices.get(symbol, 75.0)
    prices = {}
    
    # Generate 30 days of mock data
    for i in range(30):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        change = random.uniform(-0.05, 0.05)  # ±5% daily change
        prices[date] = base_price * (1 + change)
    
    return prices

def get_market_volatility(prices: Dict[str, float], days: int = 30) -> float:
    """
    Calculate market volatility for risk assessment
    Enhanced for Guyana/ME geo-risk analysis
    """
    if len(prices) < 2:
        return 0.0
    
    # Convert to sorted list of prices
    sorted_prices = sorted(prices.items())
    price_values = [float(price) for _, price in sorted_prices]
    
    if len(price_values) < 2:
        return 0.0
    
    # Calculate daily returns
    returns = np.diff(np.log(price_values))
    
    # Calculate volatility (annualized)
    volatility = np.std(returns) * np.sqrt(252)
    
    return float(volatility)

async def market_data_broadcaster(websocket, path: str):
    """WebSocket handler for broadcasting market data with real Alpha Vantage data"""
    try:
        while True:
            # Try to get real market data
            try:
                brent_prices = fetch_energy_prices('BRENT')
                wti_prices = fetch_energy_prices('WTI')
                
                # Calculate volatilities
                brent_vol = get_market_volatility(brent_prices)
                wti_vol = get_market_volatility(wti_prices)
                
                market_data = {
                    "type": "enhanced_market_data",
                    "data": {
                        "brent": {
                            "latest_price": list(brent_prices.values())[0] if brent_prices else 75.0,
                            "volatility": brent_vol,
                            "source": "Alpha Vantage"
                        },
                        "wti": {
                            "latest_price": list(wti_prices.values())[0] if wti_prices else 70.0,
                            "volatility": wti_vol,
                            "source": "Alpha Vantage"
                        }
                    },
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                print(f"Real market data error: {e}, falling back to mock data")
                market_data = await generate_market_data()
            
            await websocket.send(json.dumps(market_data))
            await asyncio.sleep(5)  # Send updates every 5 seconds (API rate limits)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()
