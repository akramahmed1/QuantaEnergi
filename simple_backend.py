#!/usr/bin/env python3
"""
Simple Working Backend - No Import Issues
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import uuid
from datetime import datetime

# Simple models
class Trade(BaseModel):
    id: Optional[str] = None
    commodity: str
    quantity: float
    price: float
    trade_type: str
    status: str = "captured"
    timestamp: Optional[datetime] = None

class User(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Create FastAPI app
app = FastAPI(
    title="QuantaEnergi API",
    version="1.0.0",
    description="AI-Powered Energy Trading Platform API"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
trades_db = {}
users_db = {
    "admin": {"username": "admin", "password": "secret"},
    "trader": {"username": "trader", "password": "secret"}
}

# Routes
@app.get("/")
async def root():
    return {"message": "QuantaEnergi API v1.0", "status": "operational"}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "QuantaEnergi API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/login", response_model=Token)
async def login(user: User):
    if user.username in users_db and users_db[user.username]["password"] == user.password:
        return {"access_token": f"token_{user.username}_{uuid.uuid4()}", "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/api/v1/capture", response_model=Trade)
async def capture_trade(trade: Trade):
    trade.id = str(uuid.uuid4())
    trade.timestamp = datetime.now()
    trades_db[trade.id] = trade
    return trade

@app.get("/api/v1/trades", response_model=List[Trade])
async def get_trades():
    return list(trades_db.values())

@app.post("/api/v1/forecast")
async def create_forecast():
    return {
        "forecast": [
            {"date": "2024-01-01", "price": 50.0},
            {"date": "2024-01-02", "price": 52.0},
            {"date": "2024-01-03", "price": 48.0}
        ],
        "method": "AI Prophet",
        "confidence": 0.85
    }

@app.post("/api/v1/optimize/portfolio")
async def optimize_portfolio():
    return {
        "optimized_weights": [0.4, 0.3, 0.3],
        "expected_return": 0.08,
        "method": "Quantum QAOA"
    }

@app.post("/api/v1/blockchain/carbon-trade")
async def create_carbon_trade():
    return {
        "trade_id": str(uuid.uuid4()),
        "carbon_amount": 100.0,
        "price": 25.5,
        "status": "pending"
    }

if __name__ == "__main__":
    print("🚀 Starting QuantaEnergi Backend...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
