"""
Pydantic schemas for EnergyOpti-Pro disruptive features.

This module contains all the data models and validation schemas for:
- AI/ML Forecasting
- Quantum Optimization
- Blockchain Smart Contracts
- IoT Integration
- Multi-Region Compliance
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

# ============================================================================
# AI/ML Forecasting Schemas
# ============================================================================

class ForecastModelType(str, Enum):
    """Forecast model types"""
    ENSEMBLE = "ensemble"
    PROPHET = "prophet"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    XGBOOST = "xgboost"

class HistoricalDataPoint(BaseModel):
    """Historical data point for forecasting"""
    timestamp: datetime = Field(..., description="Timestamp of the data point")
    price: float = Field(..., gt=0, description="Price at timestamp")
    volume: float = Field(..., ge=0, description="Volume at timestamp")
    
    @field_validator('timestamp')
    @classmethod
    def validate_timestamp(cls, v):
        if v > datetime.now():
            raise ValueError('Timestamp cannot be in the future')
        return v

class ForecastRequest(BaseModel):
    """Request for AI forecasting"""
    commodity: str = Field(..., min_length=1, max_length=50, description="Energy commodity to forecast")
    days: int = Field(7, ge=1, le=365, description="Number of days to forecast")
    use_prophet: bool = Field(False, description="Use Prophet library for forecasting")
    model_type: ForecastModelType = Field(ForecastModelType.ENSEMBLE, description="Type of model to use")

class ForecastDataPoint(BaseModel):
    """Forecast data point"""
    timestamp: datetime = Field(..., description="Forecast timestamp")
    predicted_price: float = Field(..., description="Predicted price")
    confidence: float = Field(..., ge=0, le=1, description="Forecast confidence (0-1)")
    forecast_horizon: int = Field(..., ge=0, description="Hours ahead of current time")
    lower_bound: Optional[float] = Field(None, description="Lower confidence bound")
    upper_bound: Optional[float] = Field(None, description="Upper confidence bound")

class ForecastResponse(BaseModel):
    """AI forecasting response"""
    commodity: str = Field(..., description="Commodity forecasted")
    forecast_period_days: int = Field(..., description="Forecast period in days")
    forecast_data: List[ForecastDataPoint] = Field(..., description="Forecast data points")
    model_info: Dict[str, Any] = Field(..., description="Model information")
    grok_ai_insights: Optional[str] = Field(None, description="Grok AI insights")
    timestamp: datetime = Field(..., description="Response timestamp")

class ESGScoreRequest(BaseModel):
    """Request for ESG score calculation"""
    commodity: str = Field(..., description="Energy commodity")
    forecast_data: List[ForecastDataPoint] = Field(..., description="Forecast data for ESG analysis")

class ESGScoreResponse(BaseModel):
    """ESG score response"""
    commodity: str = Field(..., description="Energy commodity")
    esg_score: float = Field(..., ge=0, le=100, description="Overall ESG score (0-100)")
    rating: str = Field(..., description="ESG rating (A, B, C, D)")
    breakdown: Dict[str, float] = Field(..., description="ESG component breakdown")
    recommendations: List[str] = Field(..., description="ESG improvement recommendations")
    timestamp: datetime = Field(..., description="Response timestamp")

# ============================================================================
# Quantum Optimization Schemas
# ============================================================================

class PortfolioAsset(BaseModel):
    """Portfolio asset for quantum optimization"""
    symbol: str = Field(..., min_length=1, max_length=10, description="Asset symbol")
    weight: float = Field(..., ge=0, le=1, description="Current weight in portfolio")
    expected_return: float = Field(..., description="Expected annual return")
    volatility: float = Field(..., ge=0, description="Annual volatility")
    sector: str = Field(..., description="Asset sector")
    region: str = Field(..., description="Asset region")
    esg_score: float = Field(..., ge=0, le=100, description="ESG score (0-100)")

class PortfolioOptimizationRequest(BaseModel):
    """Request for portfolio optimization"""
    assets: List[PortfolioAsset] = Field(..., min_length=2, max_length=50, description="Portfolio assets")
    target_return: Optional[float] = Field(None, description="Target portfolio return")
    risk_tolerance: float = Field(0.5, ge=0, le=1, description="Risk tolerance (0-1)")
    max_iterations: int = Field(100, ge=10, le=1000, description="Maximum optimization iterations")

class PortfolioMetrics(BaseModel):
    """Portfolio performance metrics"""
    expected_return: float = Field(..., description="Expected portfolio return")
    portfolio_volatility: float = Field(..., description="Portfolio volatility")
    sharpe_ratio: float = Field(..., description="Sharpe ratio")
    portfolio_esg_score: float = Field(..., description="Portfolio ESG score")
    diversification_ratio: float = Field(..., description="Diversification ratio")
    risk_adjusted_return: float = Field(..., description="Risk-adjusted return")

class PortfolioOptimizationResponse(BaseModel):
    """Portfolio optimization response"""
    optimization_method: str = Field(..., description="Optimization method used")
    optimal_weights: List[float] = Field(..., description="Optimal asset weights")
    portfolio_metrics: PortfolioMetrics = Field(..., description="Portfolio performance metrics")
    quantum_result: Optional[str] = Field(None, description="Quantum algorithm result")
    optimization_success: Optional[bool] = Field(None, description="Optimization success status")
    timestamp: datetime = Field(..., description="Response timestamp")

class RiskAssessmentRequest(BaseModel):
    """Request for risk assessment"""
    portfolio_data: Dict[str, Any] = Field(..., description="Portfolio data for risk analysis")

class RiskAssessmentResponse(BaseModel):
    """Risk assessment response"""
    method: str = Field(..., description="Risk assessment method")
    risk_metrics: Dict[str, Any] = Field(..., description="Risk metrics and analysis")
    quantum_circuit: Optional[str] = Field(None, description="Quantum circuit used")
    measurement_counts: Optional[Dict[str, int]] = Field(None, description="Quantum measurement results")
    timestamp: datetime = Field(..., description="Response timestamp")

# ============================================================================
# Blockchain Smart Contracts Schemas
# ============================================================================

class ContractType(str, Enum):
    """Smart contract types"""
    ENERGY_TRADE = "energy_trade"
    CARBON_CREDIT = "carbon_credit"
    ESG_CERTIFICATE = "esg_certificate"
    COMPLIANCE_VERIFICATION = "compliance_verification"

class TransactionStatus(str, Enum):
    """Transaction status"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class SmartContract(BaseModel):
    """Smart contract representation"""
    contract_id: str = Field(..., description="Unique contract identifier")
    contract_address: str = Field(..., description="Blockchain contract address")
    contract_type: ContractType = Field(..., description="Type of smart contract")
    owner: str = Field(..., description="Contract owner address")
    participants: List[str] = Field(..., description="Contract participants")
    status: str = Field(..., description="Contract status")
    created_at: datetime = Field(..., description="Contract creation timestamp")
    metadata: Dict[str, Any] = Field(..., description="Contract metadata")

class EnergyTradeContractRequest(BaseModel):
    """Request for energy trade contract deployment"""
    owner: str = Field(..., description="Contract owner address")
    participants: List[str] = Field(..., min_length=2, description="Contract participants")
    energy_type: str = Field(..., description="Type of energy commodity")
    total_volume: float = Field(..., gt=0, description="Total energy volume")

class CarbonCreditContractRequest(BaseModel):
    """Request for carbon credit contract creation"""
    issuer: str = Field(..., description="Credit issuer address")
    credit_amount: float = Field(..., gt=0, description="Carbon credit amount")
    project_type: str = Field(..., description="Project type")
    verification_data: Dict[str, Any] = Field(..., description="Verification data")

class BlockchainResponse(BaseModel):
    """Blockchain operation response"""
    success: bool = Field(..., description="Operation success status")
    contract_id: Optional[str] = Field(None, description="Contract identifier")
    contract_address: Optional[str] = Field(None, description="Contract address")
    transaction_hash: Optional[str] = Field(None, description="Transaction hash")
    status: Optional[TransactionStatus] = Field(None, description="Transaction status")
    error: Optional[str] = Field(None, description="Error message if failed")
    timestamp: datetime = Field(..., description="Response timestamp")

# ============================================================================
# IoT Integration Schemas
# ============================================================================

class SensorType(str, Enum):
    """IoT sensor types"""
    GRID_VOLTAGE = "grid_voltage"
    GRID_FREQUENCY = "grid_frequency"
    POWER_FLOW = "power_flow"
    WEATHER_TEMPERATURE = "weather_temperature"
    WEATHER_HUMIDITY = "weather_humidity"
    SOLAR_RADIATION = "solar_radiation"
    WIND_SPEED = "wind_speed"

class DataQuality(str, Enum):
    """Data quality indicators"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    UNKNOWN = "unknown"

class SensorData(BaseModel):
    """IoT sensor data"""
    sensor_id: str = Field(..., description="Sensor identifier")
    sensor_type: SensorType = Field(..., description="Type of sensor")
    value: float = Field(..., description="Sensor reading value")
    unit: str = Field(..., description="Measurement unit")
    quality: DataQuality = Field(..., description="Data quality indicator")
    timestamp: datetime = Field(..., description="Data timestamp")
    location: Optional[str] = Field(None, description="Sensor location")

class GridStatus(BaseModel):
    """Power grid status"""
    location: str = Field(..., description="Grid location")
    voltage: float = Field(..., description="Grid voltage")
    frequency: float = Field(..., description="Grid frequency")
    power_flow: float = Field(..., description="Power flow")
    status: str = Field(..., description="Grid status")
    last_updated: datetime = Field(..., description="Last update timestamp")

class WeatherData(BaseModel):
    """Weather data from IoT sensors"""
    coordinates: Dict[str, float] = Field(..., description="Geographic coordinates")
    temperature: float = Field(..., description="Temperature in Celsius")
    humidity: float = Field(..., ge=0, le=100, description="Humidity percentage")
    wind_speed: float = Field(..., ge=0, description="Wind speed in m/s")
    pressure: Optional[float] = Field(None, description="Atmospheric pressure")
    timestamp: datetime = Field(..., description="Weather data timestamp")

class IoTResponse(BaseModel):
    """IoT integration response"""
    success: bool = Field(..., description="Operation success status")
    data: Union[GridStatus, WeatherData, List[SensorData]] = Field(..., description="IoT data")
    data_source: str = Field(..., description="Data source identifier")
    timestamp: datetime = Field(..., description="Response timestamp")

# ============================================================================
# Multi-Region Compliance Schemas
# ============================================================================

class ComplianceRegion(str, Enum):
    """Compliance regions"""
    US_FERC = "US_FERC"
    US_DODD_FRANK = "US_DODD_FRANK"
    EU_REMIT = "EU_REMIT"
    UK_ETS = "UK_ETS"
    ISLAMIC_FINANCE = "ISLAMIC_FINANCE"
    ADNOC = "ADNOC"
    GUYANA_PETROLEUM = "GUYANA_PETROLEUM"

class ComplianceStatus(str, Enum):
    """Compliance status"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    UNDER_REVIEW = "under_review"

class ComplianceRule(BaseModel):
    """Compliance rule definition"""
    rule_id: str = Field(..., description="Rule identifier")
    rule_name: str = Field(..., description="Rule name")
    description: str = Field(..., description="Rule description")
    region: ComplianceRegion = Field(..., description="Applicable region")
    severity: str = Field(..., description="Rule severity")
    category: str = Field(..., description="Rule category")

class ComplianceCheck(BaseModel):
    """Compliance check result"""
    check_id: str = Field(..., description="Check identifier")
    region: ComplianceRegion = Field(..., description="Compliance region")
    compliance_score: float = Field(..., ge=0, le=100, description="Compliance score (0-100)")
    status: ComplianceStatus = Field(..., description="Compliance status")
    violations: List[str] = Field(..., description="List of violations")
    recommendations: List[str] = Field(..., description="Compliance recommendations")
    timestamp: datetime = Field(..., description="Check timestamp")

class ComplianceRequest(BaseModel):
    """Request for compliance checking"""
    trading_data: Dict[str, Any] = Field(..., description="Trading data for compliance analysis")
    regions: Optional[List[ComplianceRegion]] = Field(None, description="Regions to check")

class ComprehensiveComplianceResponse(BaseModel):
    """Comprehensive compliance response"""
    overall_compliance_score: float = Field(..., ge=0, le=100, description="Overall compliance score")
    overall_status: ComplianceStatus = Field(..., description="Overall compliance status")
    regions_checked: List[ComplianceRegion] = Field(..., description="Regions checked")
    compliance_by_region: Dict[str, ComplianceCheck] = Field(..., description="Compliance by region")
    consolidated_recommendations: List[str] = Field(..., description="Consolidated recommendations")
    timestamp: datetime = Field(..., description="Response timestamp")

# ============================================================================
# Common Response Schemas
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Error type")
    timestamp: datetime = Field(..., description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Request identifier")

class SuccessResponse(BaseModel):
    """Standard success response"""
    success: bool = Field(True, description="Success status")
    message: str = Field(..., description="Success message")
    data: Optional[Any] = Field(None, description="Response data")
    timestamp: datetime = Field(..., description="Response timestamp")

class PaginationInfo(BaseModel):
    """Pagination information"""
    page: int = Field(..., ge=1, description="Current page number")
    per_page: int = Field(..., ge=1, le=100, description="Items per page")
    total: int = Field(..., ge=0, description="Total number of items")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    has_next: bool = Field(..., description="Has next page")
    has_prev: bool = Field(..., description="Has previous page")

class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    data: List[Any] = Field(..., description="Response data")
    pagination: PaginationInfo = Field(..., description="Pagination information")
    timestamp: datetime = Field(..., description="Response timestamp")
