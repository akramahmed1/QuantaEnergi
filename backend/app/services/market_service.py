import asyncio
import json
import random
from datetime import datetime
from typing import Dict, Any

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

async def market_data_broadcaster(websocket, path: str):
    """WebSocket handler for broadcasting market data"""
    try:
        while True:
            market_data = await generate_market_data()
            await websocket.send(json.dumps(market_data))
            await asyncio.sleep(1)  # Send updates every second
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()
