"""
Trade Capture Schema
Pydantic model for trade capture validation
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

class AssetType(str, Enum):
    OIL = "oil"
    GAS = "gas"

class RegionType(str, Enum):
    ME = "me"
    GUYANA = "guyana"
    US = "us"
    UK = "uk"
    EU = "eu"

class TradeCapture(BaseModel):
    asset: AssetType = Field(..., description="Asset type (oil/gas)")
    volume: float = Field(..., gt=0, description="Trade volume")
    price: float = Field(..., gt=0, description="Trade price per unit")
    region: RegionType = Field(..., description="Trading region")
    amendments: Optional[List[Dict[str, Any]]] = Field(default=None, description="Optional trade amendments")