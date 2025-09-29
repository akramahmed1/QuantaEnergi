"""
ETRM/CTRM API Endpoints for QuantaEnergi Enterprise Application
Comprehensive API exposing all trading, risk, and analytics functionality
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from decimal import Decimal
import logging

from app.db.session import get_db
from app.core.etrm_integration_engine import ETRMIntegrationEngine
from app.core.advanced_trade_engine import OrderType, OrderSide, ExecutionAlgorithm
from app.core.advanced_risk_engine import RiskType, StressTestType
from app.core.pricing_models import PricingModel, OptionType, ExerciseStyle
from app.core.portfolio_optimizer import OptimizationObjective, ConstraintType
from app.core.clearing_settlement_engine import SettlementType, MarginType
from app.core.compliance_engine import RegulatoryFramework, ComplianceRuleType
from app.core.credit_risk_engine import CreditRating, CreditRiskModel
from app.core.operational_risk_engine import OperationalRiskCategory, RiskAssessmentMethod
from app.core.analytics_engine import AttributionMethod, AnalyticsType
from app.schemas.etrm_schemas import (
    TradeRequest, TradeResponse, OrderRequest, OrderResponse,
    RiskLimitRequest, RiskLimitResponse, PricingRequest, PricingResponse,
    PortfolioOptimizationRequest, PortfolioOptimizationResponse,
    ComplianceCheckRequest, ComplianceCheckResponse,
    CreditRiskRequest, CreditRiskResponse,
    AnalyticsRequest, AnalyticsResponse,
    SystemStatusResponse, DashboardResponse
)

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/v1/etrm", tags=["ETRM/CTRM"])

# Global integration engine instance
integration_engine: Optional[ETRMIntegrationEngine] = None

async def get_integration_engine(db: Session = Depends(get_db)) -> ETRMIntegrationEngine:
    """Get or create integration engine instance"""
    global integration_engine
    if integration_engine is None:
        integration_engine = ETRMIntegrationEngine(db)
        await integration_engine.start_system()
    return integration_engine

# Trading Endpoints
@router.post("/trades", response_model=TradeResponse)
async def create_trade(
    trade_request: TradeRequest,
    background_tasks: BackgroundTasks,
    engine: ETRMIntegrationEngine = Depends(get_integration_engine)
):
    """Create a new trade"""
    try:
        trade_data = trade_request.dict()
        trade_id = engine.create_trade(trade_data)
        
        return TradeResponse(
            trade_id=trade_id,
            status="created",
            message="Trade created successfully",
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Error creating trade: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trades/{trade_id}/execute")
async def execute_trade(
    trade_id: str,
    market_price: float,
    engine: ETRMIntegrationEngine = Depends(get_integration_engine)
):
    """Execute a trade"""
    try:
        executions = engine.execute_trade(trade_id, market_price)
        
        return {
            "trade_id": trade_id,
            "executions": [
                {
                    "execution_id": exec.execution_id,
                    "quantity": float(exec.quantity),
                    "price": float(exec.price),
                    "execution_time": exec.execution_time.isoformat()
                }
                for exec in executions
            ],
            "status": "executed",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error executing trade: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trades/portfolio")
async def get_portfolio_summary(
    engine: ETRMIntegrationEngine = Depends(get_integration_engine)
):
    """Get portfolio summary"""
    try:
        summary = engine.trade_engine.get_portfolio_summary()
        return summary
    except Exception as e:
        logger.error(f"Error getting portfolio summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Risk Management Endpoints
@router.post("/risk/limits", response_model=RiskLimitResponse)
async def add_risk_limit(
    risk_limit_request: RiskLimitRequest,
    engine: ETRMIntegrationEngine = Depends(get_integration_engine)
):
    """Add a new risk limit"""
    try:
        limit = engine.risk_engine.add_risk_limit(
            limit_id=risk_limit_request.limit_id,
            risk_type=RiskType(risk_limit_request.risk_type),
            limit_value=risk_limit_request.limit_value,
            breach_threshold=risk_limit_request.breach_threshold,
            currency=risk_limit_request.currency,
            unit=risk_limit_request.unit
        )
        
        return RiskLimitResponse(
            limit_id=limit.limit_id,
            risk_type=limit.risk_type.value,
            limit_value=limit.limit_value,
            current_value=limit.current_value,
            utilization=limit.utilization,
            is_breached=limit.is_breached,
            status="created"
        )
    except Exception as e:
        logger.error(f"Error adding risk limit: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/risk/limits/status")
async def get_risk_limits_status(
    engine: ETRMIntegrationEngine = Depends(get_integration_engine)
):
    """Get risk limits status"""
    try:
        status = engine.risk_engine.get_risk_limits_status()
        return status
    except Exception as e:
        logger.error(f"Error getting risk limits status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/risk/stress-test")
async def run_stress_test(
    scenario_id: str,
    positions: List[Dict[str, Any]],
    engine: ETRMIntegrationEngine = Depends(get_integration_engine)
):
    """Run stress test"""
    try:
        result = engine.risk_engine.run_stress_test(scenario_id, positions)
        return result
    except Exception as e:
        logger.error(f"Error running stress test: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Pricing Endpoints
@router.post("/pricing/calculate", response_model=PricingResponse)
async def calculate_pricing(
    pricing_request: PricingRequest,
    engine: ETRMIntegrationEngine = Depends(get_integration_engine)
):
    """Calculate option pricing"""
    try:
        from app.core.pricing_models import MarketData, PricingModel, OptionType, ExerciseStyle
        
        market_data = MarketData(
            spot_price=pricing_request.spot_price,
            strike_price=pricing_request.strike_price,
            risk_free_rate=pricing_request.risk_free_rate,
            dividend_yield=pricing_request.dividend_yield,
            volatility=pricing_request.volatility,
            time_to_expiry=pricing_request.time_to_expiry,
            option_type=OptionType(pricing_request.option_type),
            exercise_style=ExerciseStyle(pricing_request.exercise_style)
        )
        
        result = engine.pricing_engine.price_option(
            market_data,
            PricingModel(pricing_request.model)
        )
        
        return PricingResponse(
            price=result.price,
            delta=result.delta,
            gamma=result.gamma,
            theta=result.theta,
            vega=result.vega,
            rho=result.rho,
            model_used=result.model_used,
            confidence_interval=result.confidence_interval
        )
    except Exception as e:
        logger.error(f"Error calculating pricing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Portfolio Optimization Endpoints
@router.post("/portfolio/optimize", response_model=PortfolioOptimizationResponse)
async def optimize_portfolio(
    optimization_request: PortfolioOptimizationRequest,
    engine: ETRMIntegrationEngine = Depends(get_integration_engine)
):
    """Optimize portfolio"""
    try:
        # Add assets to optimizer
        for asset_data in optimization_request.assets:
            from app.core.portfolio_optimizer import Asset
            asset = Asset(
                symbol=asset_data["symbol"],
                name=asset_data["name"],
                expected_return=asset_data["expected_return"],
                volatility=asset_data["volatility"],
                market_cap=asset_data.get("market_cap", 0),
                sector=asset_data.get("sector", ""),
                region=asset_data.get("region", ""),
                currency=asset_data.get("currency", "USD")
            )
            engine.portfolio_optimizer.add_asset(asset)
        
        # Set covariance matrix if provided
        if optimization_request.covariance_matrix:
            import numpy as np
            cov_matrix = np.array(optimization_request.covariance_matrix)
            engine.portfolio_optimizer.set_covariance_matrix(cov_matrix)
        
        # Optimize portfolio
        result = engine.portfolio_optimizer.optimize_portfolio(
            OptimizationObjective(optimization_request.objective),
            method=optimization_request.method
        )
        
        return PortfolioOptimizationResponse(
            weights=result.weights.tolist(),
            expected_return=result.expected_return,
            expected_risk=result.expected_risk,
            sharpe_ratio=result.sharpe_ratio,
            var_95=result.var_95,
            var_99=result.var_99,
            expected_shortfall=result.expected_shortfall,
            diversification_ratio=result.diversification_ratio,
            concentration_risk=result.concentration_risk,
            optimization_time=result.optimization_time,
            convergence_status=result.convergence_status,
            objective_value=result.objective_value,
            constraints_satisfied=result.constraints_satisfied
        )
    except Exception as e:
        logger.error(f"Error optimizing portfolio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Compliance Endpoints
@router.post("/compliance/check", response_model=ComplianceCheckResponse)
async def check_compliance(
    compliance_request: ComplianceCheckRequest,
    engine: ETRMIntegrationEngine = Depends(get_integration_engine)
):
    """Check compliance for trade"""
    try:
        violations = engine.compliance_engine.check_compliance(
            compliance_request.trade_data,
            compliance_request.counterparty_id,
            RegulatoryFramework(compliance_request.framework)
        )
        
        return ComplianceCheckResponse(
            approved=len(violations) == 0,
            violations=[
                {
                    "violation_id": v.violation_id,
                    "rule_id": v.rule_id,
                    "violation_type": v.violation_type.value,
                    "severity": v.severity.value,
                    "current_value": v.current_value,
                    "threshold_value": v.threshold_value,
                    "violation_amount": v.violation_amount,
                    "violation_percentage": v.violation_percentage
                }
                for v in violations
            ],
            status="checked"
        )
    except Exception as e:
        logger.error(f"Error checking compliance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Credit Risk Endpoints
@router.post("/credit-risk/calculate", response_model=CreditRiskResponse)
async def calculate_credit_risk(
    credit_request: CreditRiskRequest,
    engine: ETRMIntegrationEngine = Depends(get_integration_engine)
):
    """Calculate credit risk metrics"""
    try:
        # Add counterparty if not exists
        from app.core.credit_risk_engine import Counterparty, CreditRating
        counterparty = Counterparty(
            counterparty_id=credit_request.counterparty_id,
            name=credit_request.name,
            credit_rating=CreditRating(credit_request.credit_rating),
            probability_of_default=credit_request.probability_of_default,
            loss_given_default=credit_request.loss_given_default,
            exposure_at_default=credit_request.exposure_at_default,
            recovery_rate=credit_request.recovery_rate,
            country=credit_request.country,
            sector=credit_request.sector,
            credit_limit=credit_request.credit_limit
        )
        engine.credit_risk_engine.add_counterparty(counterparty)
        
        # Calculate credit exposure
        exposure = engine.credit_risk_engine.calculate_credit_exposure(
            credit_request.counterparty_id,
            credit_request.trades
        )
        
        # Calculate CVA
        cva = engine.credit_risk_engine.calculate_cva(
            credit_request.counterparty_id,
            exposure
        )
        
        return CreditRiskResponse(
            counterparty_id=credit_request.counterparty_id,
            current_exposure=exposure.current_exposure,
            peak_exposure=exposure.peak_exposure,
            expected_exposure=exposure.expected_exposure,
            potential_future_exposure=exposure.potential_future_exposure,
            cva_amount=cva.cva_amount,
            probability_of_default=counterparty.probability_of_default,
            loss_given_default=counterparty.loss_given_default,
            credit_limit_utilization=exposure.current_exposure / credit_request.credit_limit if credit_request.credit_limit > 0 else 0,
            status="calculated"
        )
    except Exception as e:
        logger.error(f"Error calculating credit risk: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Analytics Endpoints
@router.post("/analytics/performance", response_model=AnalyticsResponse)
async def calculate_performance_analytics(
    analytics_request: AnalyticsRequest,
    engine: ETRMIntegrationEngine = Depends(get_integration_engine)
):
    """Calculate performance analytics"""
    try:
        # Calculate performance metrics
        metrics = engine.analytics_engine.calculate_performance_metrics(
            analytics_request.returns,
            analytics_request.benchmark_returns,
            analytics_request.risk_free_rate
        )
        
        # Calculate attribution if requested
        attribution_result = None
        if analytics_request.calculate_attribution:
            attribution_result = engine.analytics_engine.calculate_performance_attribution(
                analytics_request.returns,
                analytics_request.benchmark_returns,
                analytics_request.portfolio_weights,
                analytics_request.benchmark_weights,
                analytics_request.sector_returns,
                AttributionMethod(analytics_request.attribution_method)
            )
        
        # Calculate risk attribution if requested
        risk_attribution = None
        if analytics_request.calculate_risk_attribution:
            risk_attribution = engine.analytics_engine.calculate_risk_attribution(
                analytics_request.returns,
                analytics_request.factor_returns,
                analytics_request.portfolio_weights
            )
        
        return AnalyticsResponse(
            performance_metrics={
                "total_return": metrics.total_return,
                "annualized_return": metrics.annualized_return,
                "volatility": metrics.volatility,
                "sharpe_ratio": metrics.sharpe_ratio,
                "sortino_ratio": metrics.sortino_ratio,
                "calmar_ratio": metrics.calmar_ratio,
                "max_drawdown": metrics.max_drawdown,
                "var_95": metrics.var_95,
                "var_99": metrics.var_99,
                "expected_shortfall": metrics.expected_shortfall,
                "information_ratio": metrics.information_ratio,
                "tracking_error": metrics.tracking_error,
                "beta": metrics.beta,
                "alpha": metrics.alpha,
                "r_squared": metrics.r_squared
            },
            attribution_result=attribution_result.__dict__ if attribution_result else None,
            risk_attribution=risk_attribution.__dict__ if risk_attribution else None,
            status="calculated"
        )
    except Exception as e:
        logger.error(f"Error calculating analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# System Status Endpoints
@router.get("/system/status", response_model=SystemStatusResponse)
async def get_system_status(
    engine: ETRMIntegrationEngine = Depends(get_integration_engine)
):
    """Get system status"""
    try:
        status = engine.get_system_status()
        return SystemStatusResponse(**status)
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    engine: ETRMIntegrationEngine = Depends(get_integration_engine)
):
    """Get comprehensive dashboard"""
    try:
        dashboard = engine.get_comprehensive_dashboard()
        return DashboardResponse(**dashboard)
    except Exception as e:
        logger.error(f"Error getting dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system/health/{engine_name}")
async def get_engine_health(
    engine_name: str,
    engine: ETRMIntegrationEngine = Depends(get_integration_engine)
):
    """Get specific engine health"""
    try:
        health = engine.get_engine_health(engine_name)
        return health
    except Exception as e:
        logger.error(f"Error getting engine health: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Market Data Endpoints
@router.get("/market-data/{symbol}/price")
async def get_latest_price(
    symbol: str,
    engine: ETRMIntegrationEngine = Depends(get_integration_engine)
):
    """Get latest price for symbol"""
    try:
        price = await engine.market_data_engine.get_latest_price(symbol)
        return {"symbol": symbol, "price": price, "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Error getting latest price: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market-data/{symbol}/volatility")
async def get_volatility(
    symbol: str,
    vol_type: str = "historical",
    engine: ETRMIntegrationEngine = Depends(get_integration_engine)
):
    """Get volatility for symbol"""
    try:
        volatility = await engine.market_data_engine.get_volatility(symbol, vol_type)
        return {"symbol": symbol, "volatility": volatility, "type": vol_type, "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Error getting volatility: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market-data/{symbol1}/{symbol2}/correlation")
async def get_correlation(
    symbol1: str,
    symbol2: str,
    engine: ETRMIntegrationEngine = Depends(get_integration_engine)
):
    """Get correlation between two symbols"""
    try:
        correlation = await engine.market_data_engine.get_correlation(symbol1, symbol2)
        return {
            "symbol1": symbol1,
            "symbol2": symbol2,
            "correlation": correlation,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting correlation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Operational Risk Endpoints
@router.get("/operational-risk/summary")
async def get_operational_risk_summary(
    engine: ETRMIntegrationEngine = Depends(get_integration_engine)
):
    """Get operational risk summary"""
    try:
        summary = engine.operational_risk_engine.get_operational_risk_summary()
        return summary
    except Exception as e:
        logger.error(f"Error getting operational risk summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/operational-risk/calculate")
async def calculate_operational_risk_capital(
    business_line: str,
    method: str = "basic_indicator",
    engine: ETRMIntegrationEngine = Depends(get_integration_engine)
):
    """Calculate operational risk capital"""
    try:
        result = engine.operational_risk_engine.calculate_operational_risk_capital(
            business_line,
            RiskAssessmentMethod(method)
        )
        return {
            "business_line": business_line,
            "method": method,
            "expected_loss": result.expected_loss,
            "unexpected_loss": result.unexpected_loss,
            "value_at_risk": result.value_at_risk,
            "expected_shortfall": result.expected_shortfall,
            "confidence_level": result.confidence_level,
            "time_horizon": result.time_horizon,
            "calculated_at": result.calculated_at.isoformat()
        }
    except Exception as e:
        logger.error(f"Error calculating operational risk capital: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Clearing and Settlement Endpoints
@router.get("/clearing/summary")
async def get_clearing_summary(
    engine: ETRMIntegrationEngine = Depends(get_integration_engine)
):
    """Get clearing and settlement summary"""
    try:
        summary = engine.clearing_engine.get_settlement_summary()
        return summary
    except Exception as e:
        logger.error(f"Error getting clearing summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clearing/settle")
async def process_settlement(
    trade_id: str,
    settlement_type: str = "cash",
    engine: ETRMIntegrationEngine = Depends(get_integration_engine)
):
    """Process settlement for trade"""
    try:
        instruction_id = engine.clearing_engine.process_settlement(
            trade_id,
            SettlementType(settlement_type)
        )
        return {
            "trade_id": trade_id,
            "settlement_instruction_id": instruction_id,
            "settlement_type": settlement_type,
            "status": "settlement_instruction_created",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error processing settlement: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Health Check Endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "ETRM/CTRM API",
        "version": "1.0.0"
    }
