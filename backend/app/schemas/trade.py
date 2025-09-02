"""
Trade-related Pydantic models for EnergyOpti-Pro
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum


# Enums
class TradeType(str, Enum):
    BUY = "buy"
    SELL = "sell"


class CommodityType(str, Enum):
    CRUDE_OIL = "crude_oil"
    NATURAL_GAS = "natural_gas"
    REFINED_PRODUCTS = "refined_products"
    LNG = "lng"


class TradeStatus(str, Enum):
    PENDING = "pending"
    EXECUTED = "executed"
    CANCELLED = "cancelled"
    SETTLED = "settled"


class IslamicStructureType(str, Enum):
    MURABAHA = "murabaha"
    SALAM = "salam"
    ISTISNA = "istisna"
    ARBUN = "arbun"


# Phase 1: Core ETRM Models
class DealCreate(BaseModel):
    """Model for creating a new trading deal"""
    commodity: CommodityType
    quantity: float = Field(..., gt=0)
    price: float = Field(..., gt=0)
    trade_type: TradeType
    counterparty: str
    delivery_date: str
    delivery_location: str
    is_islamic: bool = True
    islamic_structure: Optional[IslamicStructureType] = None
    additional_terms: Optional[Dict[str, Any]] = None


class DealUpdate(BaseModel):
    """Model for updating a trading deal"""
    quantity: Optional[float] = Field(None, gt=0)
    price: Optional[float] = Field(None, gt=0)
    delivery_date: Optional[str] = None
    delivery_location: Optional[str] = None
    additional_terms: Optional[Dict[str, Any]] = None


class DealResponse(BaseModel):
    """Model for deal response"""
    deal_id: str
    commodity: CommodityType
    quantity: float
    price: float
    trade_type: TradeType
    counterparty: str
    delivery_date: str
    delivery_location: str
    is_islamic: bool
    islamic_structure: Optional[IslamicStructureType] = None
    status: TradeStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    additional_terms: Optional[Dict[str, Any]] = None


class PositionResponse(BaseModel):
    """Model for position response"""
    position_id: str
    deal_id: str
    commodity: CommodityType
    quantity: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float
    total_pnl: float
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class ShariaComplianceRequest(BaseModel):
    """Model for Sharia compliance request"""
    commodity_data: Dict[str, Any]
    trading_structure: Dict[str, Any]
    portfolio_value: float


class IslamicContractRequest(BaseModel):
    """Model for Islamic contract validation request"""
    contract_data: Dict[str, Any]
    contract_type: IslamicStructureType


# Phase 2: Advanced ETRM Models
class OptionCreate(BaseModel):
    """Model for creating an option"""
    underlying_commodity: CommodityType
    option_type: str = Field(..., regex="^(call|put)$")
    strike_price: float = Field(..., gt=0)
    expiry_date: str
    quantity: float = Field(..., gt=0)
    is_islamic: bool = True
    islamic_structure: Optional[IslamicStructureType] = None
    additional_params: Optional[Dict[str, Any]] = None


class StructuredProductCreate(BaseModel):
    """Model for creating a structured product"""
    product_type: str
    underlying_commodity: CommodityType
    notional_amount: float = Field(..., gt=0)
    tenor: str
    islamic_structure: IslamicStructureType
    profit_sharing_ratio: float = Field(..., ge=0, le=1)
    risk_mitigation: Optional[str] = None
    additional_features: Optional[Dict[str, Any]] = None


class AlgoStrategyCreate(BaseModel):
    """Model for creating an algorithmic trading strategy"""
    strategy_type: str = Field(..., regex="^(twap|vwap|iceberg|smart_order_routing)$")
    commodity: CommodityType
    quantity: float = Field(..., gt=0)
    execution_mode: str = Field(..., regex="^(aggressive|passive|adaptive)$")
    risk_limits: Dict[str, float]
    islamic_compliance: bool = True
    additional_params: Optional[Dict[str, Any]] = None


class QuantumOptimizationRequest(BaseModel):
    """Model for quantum optimization request"""
    portfolio_data: Dict[str, Any]
    optimization_method: str = Field(..., regex="^(quantum_annealing|quantum_approximate|classical_fallback)$")
    risk_tolerance: str = Field(..., regex="^(low|moderate|high)$")
    constraints: Dict[str, Any]
    objectives: List[str]


class MonteCarloRequest(BaseModel):
    """Model for Monte Carlo simulation request"""
    portfolio_data: Dict[str, Any]
    num_simulations: int = Field(..., ge=100, le=10000)
    confidence_level: float = Field(..., ge=0.9, le=0.99)
    time_horizon: int = Field(..., ge=1, le=252)


class StressTestRequest(BaseModel):
    """Model for stress testing request"""
    portfolio_data: Dict[str, Any]
    scenarios: List[Dict[str, Any]]
    risk_metrics: List[str] = ["var", "expected_shortfall", "max_drawdown"]


class SupplyChainOptimizationRequest(BaseModel):
    """Model for supply chain optimization request"""
    supply_chain_data: Dict[str, Any]
    optimization_method: str = Field(..., regex="^(linear_programming|genetic_algorithm|simulation)$")
    constraints: Dict[str, Any]
    objectives: List[str]


class BlendingOptimizationRequest(BaseModel):
    """Model for blending optimization request"""
    crude_specs: List[Dict[str, Any]]
    target_specs: Dict[str, Any]
    cost_constraints: Optional[Dict[str, float]] = None
    quality_constraints: Optional[Dict[str, Any]] = None


# Islamic Compliance Models
class IslamicComplianceResponse(BaseModel):
    """Model for Islamic compliance response"""
    is_compliant: bool
    compliance_score: float
    structure_type: Optional[IslamicStructureType] = None
    violations: List[str]
    recommendations: List[str]
    aaofii_standards: Optional[List[str]] = None
    timestamp: datetime


class RiskMetricsResponse(BaseModel):
    """Model for risk metrics response"""
    var_95: float
    var_99: float
    expected_shortfall: float
    portfolio_volatility: float
    sharpe_ratio: float
    max_drawdown: float
    correlation_matrix: Optional[List[List[float]]] = None
    timestamp: datetime


class OptimizationResponse(BaseModel):
    """Model for optimization response"""
    optimization_id: str
    method: str
    optimal_weights: List[float]
    expected_return: float
    portfolio_volatility: float
    sharpe_ratio: float
    constraints_satisfied: bool
    islamic_compliant: bool
    execution_time_ms: int
    timestamp: datetime


class SupplyChainResponse(BaseModel):
    """Model for supply chain response"""
    optimization_id: str
    method: str
    total_cost: float
    cost_savings: float
    optimization_metrics: Dict[str, Any]
    optimal_routes: List[Dict[str, Any]]
    storage_allocation: Dict[str, float]
    timestamp: datetime


# Response Models
class ApiResponse(BaseModel):
    """Generic API response model"""
    status: str
    data: Any
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseModel):
    """Error response model"""
    status: str = "error"
    error: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)
