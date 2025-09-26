"""
Trade Schema - Isolated from test_schema.py
"""

from pydantic import BaseModel

class TradeCapture(BaseModel):
    asset: str
    volume: float
    price: float
    region: str