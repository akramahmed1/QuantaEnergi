"""
ETRM/CTRM Schema Definitions for QuantaEnergi Enterprise Application
Comprehensive Pydantic schemas for all trading, risk, and analytics functionality
"""
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
from decimal import Decimal
from enum import Enum

# Enums
class OrderTypeEnum(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    ICEBERG = "iceberg"
    TWAP = "twap"
    VWAP = "vwap"
    PEG = "peg"

class OrderSideEnum(str, Enum):
    BUY = "buy"
    SELL = "sell"

class RiskTypeEnum(str, Enum):
    MARKET = "market"
    CREDIT = "credit"
    OPERATIONAL = "operational"
    LIQUIDITY = "liquidity"
    CONCENTRATION = "concentration"
    REGULATORY = "regulatory"

class PricingModelEnum(str, Enum):
    BLACK_SCHOLES = "black_scholes"
    BINOMIAL = "binomial"
    MONTE_CARLO = "monte_carlo"
    HESTON = "heston"
    SABR = "sabr"
    LOCAL_VOLATILITY = "local_volatility"

class OptionTypeEnum(str, Enum):
    CALL = "call"
    PUT = "put"

class ExerciseStyleEnum(str, Enum):
    EUROPEAN = "european"
    AMERICAN = "american"
    BERMUDAN = "bermudan"

class OptimizationObjectiveEnum(str, Enum):
    MAXIMIZE_RETURN = "maximize_return"
    MINIMIZE_RISK = "minimize_risk"
    MAXIMIZE_SHARPE = "maximize_sharpe"
    MINIMIZE_VAR = "minimize_var"
    MAXIMIZE_UTILITY = "maximize_utility"
    MINIMIZE_TRACKING_ERROR = "minimize_tracking_error"

class AttributionMethodEnum(str, Enum):
    BRINSON_HOOD_BEEBOWER = "brinson_hood_beebower"
    GEOMETRIC_ATTRIBUTION = "geometric_attribution"
    ARITHMETIC_ATTRIBUTION = "arithmetic_attribution"
    REGRESSION_ATTRIBUTION = "regression_attribution"
    FACTOR_ATTRIBUTION = "factor_attribution"

class RegulatoryFrameworkEnum(str, Enum):
    REMIT = "remit"
    FERC = "ferc"
    CFTC = "cftc"
    ESMA = "esma"
    ACER = "acer"
    OFGEM = "ofgem"
    AEMC = "aemc"
    ISLAMIC_FINANCE = "islamic_finance"

class CreditRatingEnum(str, Enum):
    AAA = "AAA"
    AA = "AA"
    A = "A"
    BBB = "BBB"
    BB = "BB"
    B = "B"
    CCC = "CCC"
    CC = "CC"
    C = "C"
    D = "D"

class OperationalRiskCategoryEnum(str, Enum):
    INTERNAL_FRAUD = "internal_fraud"
    EXTERNAL_FRAUD = "external_fraud"
    EMPLOYEE_PRACTICES = "employee_practices"
    CLIENT_PRODUCTS = "client_products"
    DAMAGE_TO_PHYSICAL_ASSETS = "damage_to_physical_assets"
    BUSINESS_DISRUPTION = "business_disruption"
    EXECUTION_DELIVERY = "execution_delivery"
    SYSTEM_FAILURE = "system_failure"
    PROCESS_FAILURE = "process_failure"
    REGULATORY_COMPLIANCE = "regulatory_compliance"

# Base Models
class BaseETRMModel(BaseModel):
    """Base model for ETRM entities"""
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }

# Trading Schemas
class TradeRequest(BaseETRMModel):
    """Trade creation request"""
    client_order_id: str = Field(..., description="Client order identifier")
    instrument: str = Field(..., description="Trading instrument")
    side: OrderSideEnum = Field(..., description="Order side")
    order_type: OrderTypeEnum = Field(..., description="Order type")
    quantity: float = Field(..., gt=0, description="Order quantity")
    price: Optional[float] = Field(None, gt=0, description="Order price")
    stop_price: Optional[float] = Field(None, gt=0, description="Stop price")
    time_in_force: str = Field("GTC", description="Time in force")
    execution_algorithm: str = Field("simple", description="Execution algorithm")
    counterparty_id: str = Field(..., description="Counterparty identifier")
    regulatory_framework: Optional[str] = Field("REMIT", description="Regulatory framework")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

class TradeResponse(BaseETRMModel):
    """Trade creation response"""
    trade_id: str = Field(..., description="Trade identifier")
    status: str = Field(..., description="Trade status")
    message: str = Field(..., description="Response message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

class OrderRequest(BaseETRMModel):
    """Order creation request"""
    client_order_id: str = Field(..., description="Client order identifier")
    instrument: str = Field(..., description="Trading instrument")
    side: OrderSideEnum = Field(..., description="Order side")
    order_type: OrderTypeEnum = Field(..., description="Order type")
    quantity: float = Field(..., gt=0, description="Order quantity")
    price: Optional[float] = Field(None, gt=0, description="Order price")
    stop_price: Optional[float] = Field(None, gt=0, description="Stop price")
    time_in_force: str = Field("GTC", description="Time in force")
    execution_algorithm: str = Field("simple", description="Execution algorithm")
    algorithm_params: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Algorithm parameters")

class OrderResponse(BaseETRMModel):
    """Order creation response"""
    order_id: str = Field(..., description="Order identifier")
    status: str = Field(..., description="Order status")
    message: str = Field(..., description="Response message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

# Risk Management Schemas
class RiskLimitRequest(BaseETRMModel):
    """Risk limit creation request"""
    limit_id: str = Field(..., description="Risk limit identifier")
    risk_type: RiskTypeEnum = Field(..., description="Risk type")
    limit_value: float = Field(..., gt=0, description="Limit value")
    breach_threshold: float = Field(0.8, ge=0, le=1, description="Breach threshold")
    currency: str = Field("USD", description="Currency")
    unit: str = Field("absolute", description="Unit of measurement")

class RiskLimitResponse(BaseETRMModel):
    """Risk limit response"""
    limit_id: str = Field(..., description="Risk limit identifier")
    risk_type: str = Field(..., description="Risk type")
    limit_value: float = Field(..., description="Limit value")
    current_value: float = Field(..., description="Current value")
    utilization: float = Field(..., description="Utilization percentage")
    is_breached: bool = Field(..., description="Breach status")
    status: str = Field(..., description="Response status")

class StressTestRequest(BaseETRMModel):
    """Stress test request"""
    scenario_id: str = Field(..., description="Stress scenario identifier")
    positions: List[Dict[str, Any]] = Field(..., description="Portfolio positions")
    confidence_level: float = Field(0.95, ge=0, le=1, description="Confidence level")
    time_horizon: int = Field(1, gt=0, description="Time horizon in days")

class StressTestResponse(BaseETRMModel):
    """Stress test response"""
    scenario_id: str = Field(..., description="Stress scenario identifier")
    total_pnl_impact: float = Field(..., description="Total P&L impact")
    stressed_var: float = Field(..., description="Stressed VaR")
    stressed_positions: Dict[str, Any] = Field(..., description="Stressed positions")
    run_time: str = Field(..., description="Run timestamp")

# Pricing Schemas
class PricingRequest(BaseETRMModel):
    """Pricing calculation request"""
    spot_price: float = Field(..., gt=0, description="Spot price")
    strike_price: float = Field(..., gt=0, description="Strike price")
    risk_free_rate: float = Field(0.05, ge=0, description="Risk-free rate")
    dividend_yield: float = Field(0.0, ge=0, description="Dividend yield")
    volatility: float = Field(0.2, gt=0, description="Volatility")
    time_to_expiry: float = Field(1.0, gt=0, description="Time to expiry")
    option_type: OptionTypeEnum = Field(..., description="Option type")
    exercise_style: ExerciseStyleEnum = Field(ExerciseStyleEnum.EUROPEAN, description="Exercise style")
    model: PricingModelEnum = Field(PricingModelEnum.BLACK_SCHOLES, description="Pricing model")

class PricingResponse(BaseETRMModel):
    """Pricing calculation response"""
    price: float = Field(..., description="Option price")
    delta: float = Field(..., description="Delta")
    gamma: float = Field(..., description="Gamma")
    theta: float = Field(..., description="Theta")
    vega: float = Field(..., description="Vega")
    rho: float = Field(..., description="Rho")
    model_used: str = Field(..., description="Model used")
    confidence_interval: Optional[Tuple[float, float]] = Field(None, description="Confidence interval")

# Portfolio Optimization Schemas
class AssetData(BaseETRMModel):
    """Asset data for portfolio optimization"""
    symbol: str = Field(..., description="Asset symbol")
    name: str = Field(..., description="Asset name")
    expected_return: float = Field(..., description="Expected return")
    volatility: float = Field(..., gt=0, description="Volatility")
    market_cap: Optional[float] = Field(None, ge=0, description="Market capitalization")
    sector: Optional[str] = Field(None, description="Sector")
    region: Optional[str] = Field(None, description="Region")
    currency: str = Field("USD", description="Currency")

class PortfolioOptimizationRequest(BaseETRMModel):
    """Portfolio optimization request"""
    assets: List[AssetData] = Field(..., description="Asset universe")
    objective: OptimizationObjectiveEnum = Field(..., description="Optimization objective")
    method: str = Field("scipy", description="Optimization method")
    constraints: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Constraints")
    covariance_matrix: Optional[List[List[float]]] = Field(None, description="Covariance matrix")
    expected_returns: Optional[List[float]] = Field(None, description="Expected returns")

class PortfolioOptimizationResponse(BaseETRMModel):
    """Portfolio optimization response"""
    weights: List[float] = Field(..., description="Optimal weights")
    expected_return: float = Field(..., description="Expected return")
    expected_risk: float = Field(..., description="Expected risk")
    sharpe_ratio: float = Field(..., description="Sharpe ratio")
    var_95: float = Field(..., description="95% VaR")
    var_99: float = Field(..., description="99% VaR")
    expected_shortfall: float = Field(..., description="Expected shortfall")
    diversification_ratio: float = Field(..., description="Diversification ratio")
    concentration_risk: float = Field(..., description="Concentration risk")
    optimization_time: float = Field(..., description="Optimization time")
    convergence_status: str = Field(..., description="Convergence status")
    objective_value: float = Field(..., description="Objective value")
    constraints_satisfied: bool = Field(..., description="Constraints satisfied")

# Compliance Schemas
class ComplianceCheckRequest(BaseETRMModel):
    """Compliance check request"""
    trade_data: Dict[str, Any] = Field(..., description="Trade data")
    counterparty_id: str = Field(..., description="Counterparty identifier")
    framework: RegulatoryFrameworkEnum = Field(..., description="Regulatory framework")

class ComplianceViolationData(BaseETRMModel):
    """Compliance violation data"""
    violation_id: str = Field(..., description="Violation identifier")
    rule_id: str = Field(..., description="Rule identifier")
    violation_type: str = Field(..., description="Violation type")
    severity: str = Field(..., description="Severity level")
    current_value: float = Field(..., description="Current value")
    threshold_value: float = Field(..., description="Threshold value")
    violation_amount: float = Field(..., description="Violation amount")
    violation_percentage: float = Field(..., description="Violation percentage")

class ComplianceCheckResponse(BaseETRMModel):
    """Compliance check response"""
    approved: bool = Field(..., description="Approval status")
    violations: List[ComplianceViolationData] = Field(..., description="Violations")
    status: str = Field(..., description="Check status")

# Credit Risk Schemas
class CreditRiskRequest(BaseETRMModel):
    """Credit risk calculation request"""
    counterparty_id: str = Field(..., description="Counterparty identifier")
    name: str = Field(..., description="Counterparty name")
    credit_rating: CreditRatingEnum = Field(..., description="Credit rating")
    probability_of_default: float = Field(..., ge=0, le=1, description="Probability of default")
    loss_given_default: float = Field(..., ge=0, le=1, description="Loss given default")
    exposure_at_default: float = Field(..., ge=0, description="Exposure at default")
    recovery_rate: float = Field(..., ge=0, le=1, description="Recovery rate")
    country: str = Field(..., description="Country")
    sector: str = Field(..., description="Sector")
    credit_limit: float = Field(..., ge=0, description="Credit limit")
    trades: List[Dict[str, Any]] = Field(..., description="Trade data")

class CreditRiskResponse(BaseETRMModel):
    """Credit risk calculation response"""
    counterparty_id: str = Field(..., description="Counterparty identifier")
    current_exposure: float = Field(..., description="Current exposure")
    peak_exposure: float = Field(..., description="Peak exposure")
    expected_exposure: float = Field(..., description="Expected exposure")
    potential_future_exposure: float = Field(..., description="Potential future exposure")
    cva_amount: float = Field(..., description="CVA amount")
    probability_of_default: float = Field(..., description="Probability of default")
    loss_given_default: float = Field(..., description="Loss given default")
    credit_limit_utilization: float = Field(..., description="Credit limit utilization")
    status: str = Field(..., description="Calculation status")

# Analytics Schemas
class AnalyticsRequest(BaseETRMModel):
    """Analytics calculation request"""
    returns: List[float] = Field(..., description="Portfolio returns")
    benchmark_returns: Optional[List[float]] = Field(None, description="Benchmark returns")
    risk_free_rate: Optional[float] = Field(0.02, ge=0, description="Risk-free rate")
    calculate_attribution: bool = Field(False, description="Calculate attribution")
    calculate_risk_attribution: bool = Field(False, description="Calculate risk attribution")
    portfolio_weights: Optional[List[float]] = Field(None, description="Portfolio weights")
    benchmark_weights: Optional[List[float]] = Field(None, description="Benchmark weights")
    sector_returns: Optional[Dict[str, List[float]]] = Field(None, description="Sector returns")
    factor_returns: Optional[Dict[str, List[float]]] = Field(None, description="Factor returns")
    attribution_method: AttributionMethodEnum = Field(AttributionMethodEnum.BRINSON_HOOD_BEEBOWER, description="Attribution method")

class PerformanceMetricsData(BaseETRMModel):
    """Performance metrics data"""
    total_return: float = Field(..., description="Total return")
    annualized_return: float = Field(..., description="Annualized return")
    volatility: float = Field(..., description="Volatility")
    sharpe_ratio: float = Field(..., description="Sharpe ratio")
    sortino_ratio: float = Field(..., description="Sortino ratio")
    calmar_ratio: float = Field(..., description="Calmar ratio")
    max_drawdown: float = Field(..., description="Maximum drawdown")
    var_95: float = Field(..., description="95% VaR")
    var_99: float = Field(..., description="99% VaR")
    expected_shortfall: float = Field(..., description="Expected shortfall")
    information_ratio: float = Field(..., description="Information ratio")
    tracking_error: float = Field(..., description="Tracking error")
    beta: float = Field(..., description="Beta")
    alpha: float = Field(..., description="Alpha")
    r_squared: float = Field(..., description="R-squared")

class AttributionResultData(BaseETRMModel):
    """Attribution result data"""
    total_attribution: float = Field(..., description="Total attribution")
    allocation_effect: float = Field(..., description="Allocation effect")
    selection_effect: float = Field(..., description="Selection effect")
    interaction_effect: float = Field(..., description="Interaction effect")
    currency_effect: float = Field(..., description="Currency effect")
    time_effect: float = Field(..., description="Time effect")
    sector_attribution: Dict[str, float] = Field(..., description="Sector attribution")
    security_attribution: Dict[str, float] = Field(..., description="Security attribution")

class RiskAttributionData(BaseETRMModel):
    """Risk attribution data"""
    total_risk: float = Field(..., description="Total risk")
    systematic_risk: float = Field(..., description="Systematic risk")
    idiosyncratic_risk: float = Field(..., description="Idiosyncratic risk")
    sector_risk: Dict[str, float] = Field(..., description="Sector risk")
    factor_risk: Dict[str, float] = Field(..., description="Factor risk")
    concentration_risk: float = Field(..., description="Concentration risk")
    currency_risk: float = Field(..., description="Currency risk")
    time_risk: float = Field(..., description="Time risk")

class AnalyticsResponse(BaseETRMModel):
    """Analytics calculation response"""
    performance_metrics: PerformanceMetricsData = Field(..., description="Performance metrics")
    attribution_result: Optional[AttributionResultData] = Field(None, description="Attribution result")
    risk_attribution: Optional[RiskAttributionData] = Field(None, description="Risk attribution")
    status: str = Field(..., description="Calculation status")

# System Status Schemas
class ComponentHealth(BaseETRMModel):
    """Component health data"""
    status: str = Field(..., description="Component status")
    last_heartbeat: str = Field(..., description="Last heartbeat")
    error_count: int = Field(..., description="Error count")
    performance_metrics: Dict[str, float] = Field(..., description="Performance metrics")

class SystemStatusResponse(BaseETRMModel):
    """System status response"""
    system_status: str = Field(..., description="System status")
    running: bool = Field(..., description="Running status")
    components: Dict[str, ComponentHealth] = Field(..., description="Component health")
    integration_events: Dict[str, Any] = Field(..., description="Integration events")
    timestamp: str = Field(..., description="Status timestamp")

class DashboardResponse(BaseETRMModel):
    """Dashboard response"""
    timestamp: str = Field(..., description="Dashboard timestamp")
    system_status: Dict[str, Any] = Field(..., description="System status")
    trading: Dict[str, Any] = Field(..., description="Trading data")
    risk_management: Dict[str, Any] = Field(..., description="Risk management data")
    compliance: Dict[str, Any] = Field(..., description="Compliance data")
    credit_risk: Dict[str, Any] = Field(..., description="Credit risk data")
    operational_risk: Dict[str, Any] = Field(..., description="Operational risk data")
    analytics: Dict[str, Any] = Field(..., description="Analytics data")

# Market Data Schemas
class MarketDataRequest(BaseETRMModel):
    """Market data request"""
    symbol: str = Field(..., description="Symbol")
    data_type: str = Field("tick", description="Data type")
    start_time: Optional[datetime] = Field(None, description="Start time")
    end_time: Optional[datetime] = Field(None, description="End time")

class MarketDataResponse(BaseETRMModel):
    """Market data response"""
    symbol: str = Field(..., description="Symbol")
    data_type: str = Field(..., description="Data type")
    data: List[Dict[str, Any]] = Field(..., description="Market data")
    timestamp: str = Field(..., description="Response timestamp")

# Operational Risk Schemas
class OperationalRiskRequest(BaseETRMModel):
    """Operational risk request"""
    business_line: str = Field(..., description="Business line")
    method: str = Field("basic_indicator", description="Risk assessment method")
    time_horizon: int = Field(1, gt=0, description="Time horizon")

class OperationalRiskResponse(BaseETRMModel):
    """Operational risk response"""
    business_line: str = Field(..., description="Business line")
    method: str = Field(..., description="Risk assessment method")
    expected_loss: float = Field(..., description="Expected loss")
    unexpected_loss: float = Field(..., description="Unexpected loss")
    value_at_risk: float = Field(..., description="Value at risk")
    expected_shortfall: float = Field(..., description="Expected shortfall")
    confidence_level: float = Field(..., description="Confidence level")
    time_horizon: int = Field(..., description="Time horizon")
    calculated_at: str = Field(..., description="Calculation timestamp")

# Clearing and Settlement Schemas
class SettlementRequest(BaseETRMModel):
    """Settlement request"""
    trade_id: str = Field(..., description="Trade identifier")
    settlement_type: str = Field("cash", description="Settlement type")
    counterparty_id: str = Field(..., description="Counterparty identifier")
    amount: float = Field(..., description="Settlement amount")
    currency: str = Field("USD", description="Currency")

class SettlementResponse(BaseETRMModel):
    """Settlement response"""
    trade_id: str = Field(..., description="Trade identifier")
    settlement_instruction_id: str = Field(..., description="Settlement instruction identifier")
    settlement_type: str = Field(..., description="Settlement type")
    status: str = Field(..., description="Settlement status")
    timestamp: str = Field(..., description="Settlement timestamp")

# Error Schemas
class ErrorResponse(BaseETRMModel):
    """Error response"""
    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code")
    timestamp: str = Field(..., description="Error timestamp")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")

# Validation Schemas
class ValidationError(BaseETRMModel):
    """Validation error"""
    field: str = Field(..., description="Field name")
    message: str = Field(..., description="Error message")
    value: Any = Field(..., description="Invalid value")

class ValidationResponse(BaseETRMModel):
    """Validation response"""
    valid: bool = Field(..., description="Validation status")
    errors: List[ValidationError] = Field(..., description="Validation errors")
    timestamp: str = Field(..., description="Validation timestamp")
