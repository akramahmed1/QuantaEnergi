"""
Security Validation Schemas
OWASP AI Top 25 Risk Mitigation - Input Validation and Sanitization
"""

import re
from typing import Any, Optional
from pydantic import BaseModel, Field, validator, constr
from enum import Enum


class CommodityType(str, Enum):
    """Allowed commodity types to prevent injection attacks"""
    CRUDE_OIL = "crude_oil"
    NATURAL_GAS = "natural_gas"
    COAL = "coal"
    RENEWABLES = "renewables"
    ELECTRICITY = "electricity"
    CARBON_CREDITS = "carbon_credits"


class ForecastMethod(str, Enum):
    """Allowed forecasting methods"""
    LSTM = "lstm"
    PROPHET = "prophet"
    ENSEMBLE = "ensemble"
    CLASSICAL = "classical"


class SecureInputValidator:
    """Input validation utilities for security"""
    
    # Regex patterns for validation
    ALPHANUMERIC_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')
    SAFE_STRING_PATTERN = re.compile(r'^[a-zA-Z0-9\s._-]+$')
    NO_INJECTION_PATTERN = re.compile(r'^[^<>&"\'\\/]+$')
    
    @staticmethod
    def sanitize_string(input_str: str, max_length: int = 100) -> str:
        """Sanitize string input to prevent injection attacks"""
        if not input_str:
            return ""
        
        # Remove potential injection patterns
        sanitized = re.sub(r'[<>"\'\\/&]', '', str(input_str))
        
        # Limit length
        sanitized = sanitized[:max_length].strip()
        
        return sanitized
    
    @staticmethod
    def validate_numeric_range(value: int, min_val: int = 1, max_val: int = 365) -> int:
        """Validate numeric input within safe range"""
        if not isinstance(value, int):
            raise ValueError("Value must be an integer")
        
        if value < min_val or value > max_val:
            raise ValueError(f"Value must be between {min_val} and {max_val}")
        
        return value


class SecureForecastRequest(BaseModel):
    """Secure forecast request with input validation"""
    
    commodity: CommodityType = Field(..., description="Energy commodity type")
    days: int = Field(7, ge=1, le=365, description="Number of days to forecast (1-365)")
    method: ForecastMethod = Field(ForecastMethod.ENSEMBLE, description="Prediction method")
    use_prophet: bool = Field(False, description="Use Prophet library")
    include_esg: bool = Field(True, description="Include ESG scoring")
    
    @validator('days')
    def validate_days(cls, v):
        return SecureInputValidator.validate_numeric_range(v, 1, 365)
    
    @validator('commodity')
    def validate_commodity(cls, v):
        if isinstance(v, str):
            # Additional sanitization for string inputs
            sanitized = SecureInputValidator.sanitize_string(v, 50)
            if sanitized != v:
                raise ValueError("Invalid commodity format detected")
        return v


class SecureAIForecastRequest(BaseModel):
    """Secure AI forecast request for /ai/forecast endpoint"""
    
    commodity: constr(
        regex=r'^[a-zA-Z0-9_-]+$',
        min_length=1,
        max_length=50,
        strip_whitespace=True
    ) = Field(..., description="Energy commodity (alphanumeric only)")
    
    days: int = Field(7, ge=1, le=30, description="Days to forecast (1-30)")
    use_prophet: bool = Field(False, description="Use Prophet library")
    
    @validator('commodity')
    def validate_commodity_safe(cls, v):
        """Validate commodity input against injection patterns"""
        # Check for common injection patterns
        injection_patterns = [
            r'<script', r'javascript:', r'vbscript:', r'onload=',
            r'onerror=', r'eval\(', r'exec\(', r'import\s+',
            r'__import__', r'getattr', r'setattr', r'delattr'
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError(f"Invalid input pattern detected: {pattern}")
        
        # Validate against allowed commodities
        allowed_commodities = [item.value for item in CommodityType]
        if v.lower() not in allowed_commodities:
            raise ValueError(f"Commodity must be one of: {allowed_commodities}")
        
        return v.lower()
    
    @validator('days')
    def validate_days_safe(cls, v):
        """Validate days parameter"""
        if not isinstance(v, int):
            raise ValueError("Days must be an integer")
        
        if v < 1 or v > 30:
            raise ValueError("Days must be between 1 and 30")
        
        return v


class SecureRiskCalculationRequest(BaseModel):
    """Secure risk calculation request"""
    
    portfolio_data: dict = Field(..., description="Portfolio data")
    confidence_level: float = Field(0.95, ge=0.01, le=0.99, description="Confidence level")
    num_simulations: int = Field(1000, ge=100, le=50000, description="Number of simulations")
    time_horizon: int = Field(1, ge=1, le=30, description="Time horizon in days")
    
    @validator('portfolio_data')
    def validate_portfolio_data(cls, v):
        """Validate portfolio data structure"""
        if not isinstance(v, dict):
            raise ValueError("Portfolio data must be a dictionary")
        
        # Check for required keys
        required_keys = ['positions', 'market_data']
        for key in required_keys:
            if key not in v:
                raise ValueError(f"Missing required key: {key}")
        
        return v
    
    @validator('num_simulations')
    def validate_simulations(cls, v):
        """Validate simulation count to prevent resource exhaustion"""
        if v > 50000:
            raise ValueError("Too many simulations - potential DoS risk")
        return v


class SecureQuantumRequest(BaseModel):
    """Secure quantum optimization request"""
    
    assets: list = Field(..., description="Portfolio assets")
    target_return: float = Field(0.1, ge=0.0, le=2.0, description="Target return")
    risk_tolerance: float = Field(0.5, ge=0.0, le=1.0, description="Risk tolerance")
    max_iterations: int = Field(100, ge=10, le=1000, description="Max iterations")
    
    @validator('assets')
    def validate_assets(cls, v):
        """Validate assets list"""
        if not isinstance(v, list):
            raise ValueError("Assets must be a list")
        
        if len(v) > 50:
            raise ValueError("Too many assets - potential resource exhaustion")
        
        return v
    
    @validator('max_iterations')
    def validate_iterations(cls, v):
        """Validate iteration count"""
        if v > 1000:
            raise ValueError("Too many iterations - potential DoS risk")
        return v


# Rate limiting schemas
class RateLimitConfig(BaseModel):
    """Rate limiting configuration"""
    requests_per_minute: int = Field(60, ge=1, le=1000)
    burst_limit: int = Field(10, ge=1, le=100)
    window_size: int = Field(60, ge=1, le=3600)  # seconds


# JWT Security schemas
class JWTSecurityConfig(BaseModel):
    """JWT security configuration"""
    algorithm: str = Field("HS256", regex=r'^(HS256|HS384|HS512|RS256|RS384|RS512)$')
    access_token_expire_minutes: int = Field(30, ge=5, le=1440)
    refresh_token_expire_days: int = Field(7, ge=1, le=30)
    require_issuer: bool = Field(True)
    require_audience: bool = Field(True)
