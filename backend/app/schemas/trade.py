"""
Pydantic schemas for trade operations and lifecycle management
"""

from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enum import Enum
import uuid

# Enums
class TradeType(str, Enum):
    SPOT = "spot"
    FORWARD = "forward"
    FUTURES = "futures"
    OPTIONS = "options"
    SWAP = "swap"
    MURABAHA = "murabaha"  # Islamic finance
    SUKUK = "sukuk"        # Islamic bonds
    STRUCTURED = "structured"  # Structured products

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
    COAL = "coal"
    URANIUM = "uranium"
    BIOFUELS = "biofuels"

class SettlementType(str, Enum):
    T_PLUS_1 = "T+1"
    T_PLUS_2 = "T+2"
    T_PLUS_3 = "T+3"
    SPOT = "spot"
    FORWARD = "forward"

class TradeDirection(str, Enum):
    BUY = "buy"
    SELL = "sell"
    BUY_SELL = "buy_sell"  # For swaps

class ComplianceStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    UNDER_REVIEW = "under_review"

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
    
    # Multi-tenant support
    organization_id: Optional[uuid.UUID] = Field(None, description="Organization ID for multi-tenancy")
    
    # Enhanced trade details
    trade_direction: TradeDirection = Field(TradeDirection.BUY, description="Trade direction")
    settlement_type: SettlementType = Field(SettlementType.T_PLUS_2, description="Settlement type")
    
    # Islamic finance compliance
    is_islamic_compliant: bool = Field(False, description="Islamic finance compliance flag")
    sharia_approval: Optional[str] = Field(None, description="Sharia board approval reference")
    
    # Risk and compliance
    risk_category: Optional[str] = Field(None, description="Risk category classification")
    compliance_notes: Optional[str] = Field(None, description="Compliance-related notes")
    
    @field_validator('delivery_date')
    @classmethod
    def delivery_date_must_be_future(cls, v):
        if v <= datetime.now():
            raise ValueError('Delivery date must be in the future')
        return v
    
    @field_validator('organization_id')
    @classmethod
    def validate_organization_id(cls, v):
        if v is not None:
            try:
                uuid.UUID(str(v))
            except ValueError:
                raise ValueError('Invalid organization ID format')
        return v

class TradeCreate(TradeBase):
    user_id: Optional[str] = Field(None, description="User ID (auto-filled)")
    capture_timestamp: Optional[datetime] = Field(None, description="Capture timestamp (auto-filled)")
    additional_terms: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional trade terms")
    
    # Correlation ID for event tracking
    correlation_id: Optional[str] = Field(None, description="Correlation ID for event tracking")
    
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
                "trade_direction": "buy",
                "settlement_type": "T+2",
                "is_islamic_compliant": False,
                "organization_id": "123e4567-e89b-12d3-a456-426614174000",
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
    risk_category: Optional[str] = None
    compliance_notes: Optional[str] = None
    is_islamic_compliant: Optional[bool] = None
    sharia_approval: Optional[str] = None

# Response Models
class TradeResponse(BaseModel):
    trade_id: str
    status: TradeStatus
    message: str
    timestamp: datetime
    
    # Enhanced response fields
    organization_id: Optional[uuid.UUID] = None
    correlation_id: Optional[str] = None
    compliance_status: Optional[ComplianceStatus] = None
    risk_score: Optional[float] = None
    
    model_config = {
        "from_attributes": True
    }

class TradeStatusResponse(BaseModel):
    trade_id: str
    status: TradeStatus
    valid: bool
    compliant: bool
    sharia_result: Dict[str, Any]
    
    # Enhanced status fields
    organization_id: Optional[uuid.UUID] = None
    compliance_status: ComplianceStatus
    risk_assessment: Optional[Dict[str, Any]] = None
    validation_errors: Optional[List[str]] = None
    
    model_config = {
        "from_attributes": True
    }

class TradeDetails(BaseModel):
    """Detailed trade information"""
    trade_id: str
    trade_type: TradeType
    commodity: CommodityType
    quantity: float
    price: float
    currency: str
    counterparty: str
    delivery_date: datetime
    delivery_location: str
    status: TradeStatus
    trade_direction: TradeDirection
    settlement_type: SettlementType
    
    # Multi-tenant fields
    organization_id: Optional[uuid.UUID] = None
    user_id: Optional[str] = None
    
    # Compliance and risk
    is_islamic_compliant: bool
    compliance_status: ComplianceStatus
    risk_category: Optional[str] = None
    risk_score: Optional[float] = None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    captured_at: Optional[datetime] = None
    validated_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None
    settled_at: Optional[datetime] = None
    
    # Additional fields
    additional_terms: Dict[str, Any]
    correlation_id: Optional[str] = None
    
    model_config = {
        "from_attributes": True
    }

# Trade lifecycle models
class TradeConfirmation(BaseModel):
    trade_id: str
    confirmation_number: str
    confirmation_date: datetime
    confirmed_by: str
    confirmation_notes: Optional[str] = None

class ConfirmationResponse(BaseModel):
    trade_id: str
    confirmation_id: str
    status: str
    timestamp: str

class TradeAllocation(BaseModel):
    trade_id: str
    allocation_date: datetime
    allocated_quantity: float
    allocated_price: float
    allocation_notes: Optional[str] = None

class AllocationResponse(BaseModel):
    trade_id: str
    allocation_id: str
    status: str
    details: Dict[str, Any]
    timestamp: str

class TradeSettlement(BaseModel):
    trade_id: str
    settlement_date: datetime
    settlement_amount: float
    settlement_currency: str
    settlement_method: str
    settlement_notes: Optional[str] = None

class SettlementResponse(BaseModel):
    trade_id: str
    settlement_id: str
    status: str
    details: Dict[str, Any]
    timestamp: str

class TradeInvoice(BaseModel):
    trade_id: str
    invoice_number: str
    invoice_date: datetime
    invoice_amount: float
    invoice_currency: str
    payment_terms: str
    invoice_notes: Optional[str] = None

class InvoiceResponse(BaseModel):
    trade_id: str
    invoice_id: str
    status: str
    details: Dict[str, Any]
    timestamp: str

class TradePayment(BaseModel):
    trade_id: str
    payment_reference: str
    payment_date: datetime
    payment_amount: float
    payment_currency: str
    payment_method: str
    payment_notes: Optional[str] = None

class PaymentResponse(BaseModel):
    trade_id: str
    payment_id: str
    status: str
    details: Dict[str, Any]
    timestamp: str

# Credit management schemas
class CreditLimit(BaseModel):
    counterparty_id: str
    limit_amount: float
    currency: str
    risk_rating: str
    expiry_date: str
    set_by: Optional[str] = None
    set_timestamp: Optional[str] = None

class CreditExposure(BaseModel):
    counterparty_id: str
    current_exposure: float
    available_limit: float
    utilization_rate: float
    last_updated: str

class CreditReport(BaseModel):
    counterparty_id: str
    credit_score: float
    risk_assessment: Dict[str, Any]
    recommendations: List[str]
    report_date: str

# API response schemas
class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: str
    timestamp: Optional[str] = None

class ErrorResponse(BaseModel):
    success: bool
    error: str
    message: str
    timestamp: Optional[str] = None

# Regulatory compliance schemas
class ComplianceCheck(BaseModel):
    trade_id: str
    regulation_type: str
    region: str
    is_compliant: bool
    compliance_score: float
    violations: List[str]
    recommendations: List[str]
    check_date: str

class RegulatoryReport(BaseModel):
    report_id: str
    regulation_type: str
    region: str
    report_date: str
    trades_covered: int
    compliance_summary: Dict[str, Any]
    violations_found: int
    recommendations: List[str]

# Risk analytics schemas
class RiskMetrics(BaseModel):
    trade_id: str
    var_value: float
    confidence_level: float
    time_horizon: int
    method: str
    portfolio_value: float
    volatility: float
    calculated_at: str

# Options and structured products schemas
class OptionCreate(BaseModel):
    underlying_asset: str
    option_type: str  # call/put
    strike_price: float
    expiration_date: str
    premium: float
    quantity: int

class StructuredProductCreate(BaseModel):
    product_name: str
    product_type: str
    underlying_assets: List[str]
    payoff_structure: Dict[str, Any]
    maturity_date: str
    notional_amount: float

class AlgoStrategyCreate(BaseModel):
    strategy_name: str
    strategy_type: str
    parameters: Dict[str, Any]
    risk_limits: Dict[str, float]
    execution_algorithm: str

# Islamic compliance schemas
class IslamicComplianceResponse(BaseModel):
    trade_id: str
    is_compliant: bool
    compliance_score: float
    sharia_approval: str
    restrictions: List[str]
    recommendations: List[str]
    approval_date: str

# Trade search and filtering
class TradeFilter(BaseModel):
    """Trade filtering criteria"""
    organization_id: Optional[uuid.UUID] = None
    user_id: Optional[str] = None
    trade_type: Optional[TradeType] = None
    commodity: Optional[CommodityType] = None
    status: Optional[TradeStatus] = None
    trade_direction: Optional[TradeDirection] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    quantity_min: Optional[float] = None
    quantity_max: Optional[float] = None
    counterparty: Optional[str] = None
    is_islamic_compliant: Optional[bool] = None
    compliance_status: Optional[ComplianceStatus] = None

class TradeSearchResponse(BaseModel):
    """Trade search response with pagination"""
    trades: List[TradeDetails]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    filters_applied: TradeFilter

# Trade analytics and reporting
class TradeAnalytics(BaseModel):
    """Trade analytics data"""
    total_trades: int
    total_volume: float
    total_value: float
    average_price: float
    trade_count_by_type: Dict[TradeType, int]
    trade_count_by_commodity: Dict[CommodityType, int]
    trade_count_by_status: Dict[TradeStatus, int]
    compliance_rate: float
    islamic_compliance_rate: float
    risk_distribution: Dict[str, int]

# Islamic finance specific models
class ShariaComplianceCheck(BaseModel):
    """Sharia compliance check result"""
    trade_id: str
    is_compliant: bool
    compliance_score: float
    restrictions: List[str]
    recommendations: List[str]
    sharia_board_approval: Optional[str] = None
    approval_date: Optional[datetime] = None

class IslamicTradeTerms(BaseModel):
    """Islamic trade specific terms"""
    murabaha_markup: Optional[float] = None
    asset_backing: Optional[str] = None
    profit_sharing_ratio: Optional[float] = None
    riba_free: bool = True
    gharar_free: bool = True
    haram_asset_free: bool = True
