"""
Risk Schema - Isolated from test_risk_schema.py
"""

from pydantic import BaseModel
from typing import List

class VarRequest(BaseModel):
    positions: List[float]
    confidence: float = 0.95
