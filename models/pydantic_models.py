from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

class TokenRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class PredictionInput(BaseModel):
    temperature_celsius: float = Field(..., example=25.0)
    # (Add other fields as per PRD)

class PredictionOutput(BaseModel):
    prediction: float = Field(..., example=100.0)

# (Similar for other schemas: QuantumOptimizationRequest/Response, IoTData, CarbonFootprintInput/Output, ForecastInput/Output, etc.)