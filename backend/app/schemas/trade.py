"""
Pydantic schemas for trade operations and lifecycle management
"""

from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enum import Enum

# Enums
class TradeType(str, Enum):
    SPOT = "spot"
    FORWARD = "forward"
    FUTURES = "futures"
    OPTIONS = "options"
    SWAP = "swap"
    MURABAHA = "murabaha"  # Islamic finance
    SUKUK = "sukuk"        # Islamic bonds

class TradeStatus(str, Enum):
    CAPTURED = "captured"
    VALIDATED = "validated"
    CONFIRMED = "confirmed"
    ALLOCATED = "allocated"
    SETTLED = "settled"
    INVOICED = "invoiced"
    PAID = "paid"
    CANCELLED = "cancelled"
    FAILED = "failed"
    UNKNOWN = "unknown"

class CommodityType(str, Enum):
    CRUDE_OIL = "crude_oil"
    NATURAL_GAS = "natural_gas"
    ELECTRICITY = "electricity"
    RENEWABLES = "renewables"
    CARBON_CREDITS = "carbon_credits"
    LNG = "lng"
    LPG = "lpg"

class SettlementType(str, Enum):
    T_PLUS_1 = "T+1"
    T_PLUS_2 = "T+2"
    T_PLUS_3 = "T+3"
    SPOT = "spot"
    FORWARD = "forward"

# Base Models
class TradeBase(BaseModel):
    trade_type: TradeType
    commodity: CommodityType
    quantity: float = Field(..., gt=0, description="Trade quantity")
    price: float = Field(..., gt=0, description="Trade price per unit")
    currency: str = Field(default="USD", description="Trade currency")
    counterparty: str = Field(..., description="Counterparty identifier")
    delivery_date: datetime = Field(..., description="Expected delivery date")
    delivery_location: str = Field(..., description="Delivery location")
    
    @field_validator('delivery_date')
    @classmethod
    def delivery_date_must_be_future(cls, v):
        if v <= datetime.now():
            raise ValueError('Delivery date must be in the future')
        return v

class TradeCreate(TradeBase):
    user_id: Optional[str] = Field(None, description="User ID (auto-filled)")
    capture_timestamp: Optional[datetime] = Field(None, description="Capture timestamp (auto-filled)")
    additional_terms: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional trade terms")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "trade_type": "forward",
                "commodity": "crude_oil",
                "quantity": 1000.0,
                "price": 85.50,
                "currency": "USD",
                "counterparty": "CP001",
                "delivery_date": "2024-12-31T23:59:59",
                "delivery_location": "Houston, TX",
                "additional_terms": {
                    "quality_specs": "Brent Crude",
                    "incoterms": "FOB"
                }
            }
        }
    }

class TradeUpdate(BaseModel):
    quantity: Optional[float] = Field(None, gt=0)
    price: Optional[float] = Field(None, gt=0)
    delivery_date: Optional[datetime] = None
    delivery_location: Optional[str] = None
    additional_terms: Optional[Dict[str, Any]] = None

# Response Models
class TradeResponse(BaseModel):
    trade_id: str
    status: TradeStatus
    message: str
    timestamp: datetime
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "trade_id": "trade_123",
                "status": "captured",
                "message": "Trade captured successfully",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
    }

class TradeStatusResponse(BaseModel):
    trade_id: str
    status: TradeStatus
    details: Dict[str, Any]
    timestamp: datetime
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "trade_id": "trade_123",
                "status": "validated",
                "details": {
                    "sharia_compliant": True,
                    "credit_approved": True
                },
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
    }

class ConfirmationResponse(BaseModel):
    trade_id: str
    confirmation_id: str
    status: str
    timestamp: datetime

class AllocationResponse(BaseModel):
    trade_id: str
    allocation_id: str
    status: str
    details: Dict[str, Any]
    timestamp: datetime

class SettlementResponse(BaseModel):
    trade_id: str
    settlement_id: str
    status: str
    details: Dict[str, Any]
    timestamp: datetime

class InvoiceResponse(BaseModel):
    trade_id: str
    invoice_id: str
    status: str
    details: Dict[str, Any]
    timestamp: datetime

class PaymentResponse(BaseModel):
    trade_id: str
    payment_id: str
    status: str
    details: Dict[str, Any]
    timestamp: datetime

# Credit Management Schemas
class CreditLimit(BaseModel):
    counterparty_id: str
    limit_amount: float = Field(..., gt=0)
    currency: str = Field(default="USD")
    risk_rating: str = Field(..., description="Risk rating (A, B, C, D)")
    expiry_date: datetime
    terms: Optional[Dict[str, Any]] = None

class CreditExposure(BaseModel):
    counterparty_id: str
    current_exposure: float
    available_credit: float
    utilization_percentage: float
    risk_level: str
    last_updated: datetime

class CreditReport(BaseModel):
    counterparty_id: str
    credit_limit: CreditLimit
    current_exposure: CreditExposure
    risk_assessment: Dict[str, Any]
    recommendations: List[str]
    generated_at: datetime

# Regulatory Compliance Schemas
class ComplianceCheck(BaseModel):
    region: str
    regulation_type: str
    compliance_status: bool
    requirements_met: List[str]
    requirements_missing: List[str]
    risk_level: str
    last_check: datetime

class RegulatoryReport(BaseModel):
    report_id: str
    region: str
    regulation_type: str
    report_data: Dict[str, Any]
    submission_date: datetime
    status: str
    compliance_score: float

# Sharia Compliance Schemas
class ShariaValidation(BaseModel):
    trade_id: str
    compliant: bool
    validation_details: Dict[str, Any]
    sharia_board_approval: Optional[str] = None
    validation_timestamp: datetime

# Position Management Schemas
class Position(BaseModel):
    commodity: CommodityType
    long_quantity: float = Field(default=0, ge=0)
    short_quantity: float = Field(default=0, ge=0)
    net_quantity: float
    average_price: float
    market_value: float
    unrealized_pnl: float
    last_updated: datetime

class PositionResponse(BaseModel):
    user_id: str
    positions: List[Position]
    total_market_value: float
    total_unrealized_pnl: float
    risk_metrics: Dict[str, Any]
    last_updated: datetime

# Risk Analytics Schemas
class RiskMetrics(BaseModel):
    var_95: float
    var_99: float
    expected_shortfall: float
    stress_test_results: Dict[str, Any]
    correlation_matrix: Dict[str, Any]
    calculated_at: datetime

# Supply Chain Schemas
class SupplyChain(BaseModel):
    chain_id: str
    origin: str
    destination: str
    commodity: CommodityType
    quantity: float
    status: str
    estimated_cost: float
    risk_assessment: Dict[str, Any]
    created_at: datetime

# IoT Integration Schemas
class IoTDevice(BaseModel):
    device_id: str
    device_type: str
    location: str
    status: str
    last_data: Dict[str, Any]
    last_updated: datetime

# Mobile App Schemas
class MobileDevice(BaseModel):
    device_id: str
    user_id: str
    platform: str
    push_token: Optional[str] = None
    preferences: Dict[str, Any]
    last_active: datetime

# Admin Dashboard Schemas
class SystemMetrics(BaseModel):
    total_users: int
    active_trades: int
    system_health: str
    performance_metrics: Dict[str, Any]
    alerts: List[Dict[str, Any]]
    last_updated: datetime

class UserManagement(BaseModel):
    user_id: str
    username: str
    email: str
    role: str
    status: str
    permissions: List[str]
    last_login: datetime
    created_at: datetime

# API Response Schemas
class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class IslamicComplianceResponse(BaseModel):
    compliant: bool
    sharia_score: float
    validation_details: Dict[str, Any]
    recommendations: List[str]
    timestamp: datetime

# Options Trading Schemas
class OptionCreate(BaseModel):
    option_type: str = Field(..., description="Type of option (call/put)")
    underlying: CommodityType
    strike_price: float = Field(..., gt=0)
    expiry_date: datetime
    quantity: float = Field(..., gt=0)
    premium: Optional[float] = None
    volatility: Optional[float] = None
    risk_free_rate: Optional[float] = None
    islamic_compliant: bool = True

class OptionResponse(BaseModel):
    option_id: str
    option_type: str
    underlying: CommodityType
    strike_price: float
    expiry_date: datetime
    quantity: float
    premium: float
    greeks: Dict[str, float]
    islamic_compliant: bool
    created_at: datetime

# Structured Products Schemas
class StructuredProductCreate(BaseModel):
    product_type: str = Field(..., description="Type of structured product")
    underlying: CommodityType
    notional_amount: float = Field(..., gt=0)
    maturity_date: datetime
    payoff_structure: Dict[str, Any]
    islamic_compliant: bool = True
    risk_parameters: Dict[str, Any]

class StructuredProductResponse(BaseModel):
    product_id: str
    product_type: str
    underlying: CommodityType
    notional_amount: float
    maturity_date: datetime
    payoff_structure: Dict[str, Any]
    current_value: float
    islamic_compliant: bool
    created_at: datetime

# Algorithmic Trading Schemas
class AlgoStrategyCreate(BaseModel):
    strategy_name: str
    strategy_type: str = Field(..., description="Type of algo strategy")
    parameters: Dict[str, Any]
    risk_limits: Dict[str, float]
    islamic_compliant: bool = True
    execution_mode: str = "passive"

class AlgoStrategyResponse(BaseModel):
    strategy_id: str
    strategy_name: str
    strategy_type: str
    parameters: Dict[str, Any]
    risk_limits: Dict[str, float]
    islamic_compliant: bool
    execution_mode: str
    status: str
    created_at: datetime

# Quantum Optimization Schemas
class QuantumOptimizationRequest(BaseModel):
    portfolio_data: Dict[str, Any]
    optimization_method: str = "quantum_annealing"
    constraints: Dict[str, Any]
    risk_tolerance: str = "moderate"
    target_return: Optional[float] = None

class QuantumOptimizationResponse(BaseModel):
    optimization_id: str
    optimal_weights: List[float]
    expected_return: float
    expected_risk: float
    improvement_over_classical: float
    quantum_advantage: bool
    execution_time: float
    created_at: datetime
