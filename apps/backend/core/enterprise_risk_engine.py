"""
Enterprise Risk Management Engine
Implements comprehensive risk management for ETRM/CTRM
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from pydantic import BaseModel, Field
import numpy as np
from decimal import Decimal
import asyncio
import json

# Risk Enums
class RiskType(Enum):
    MARKET = "market"
    CREDIT = "credit"
    OPERATIONAL = "operational"
    LIQUIDITY = "liquidity"
    REGULATORY = "regulatory"
    WEATHER = "weather"
    COUNTERPARTY = "counterparty"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class VaRMethod(Enum):
    HISTORICAL = "historical"
    PARAMETRIC = "parametric"
    MONTE_CARLO = "monte_carlo"

# Risk Models
class RiskLimit(BaseModel):
    id: str
    user_id: str
    risk_type: RiskType
    limit_name: str
    limit_value: Decimal
    current_value: Decimal
    limit_period: str  # daily, weekly, monthly
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class RiskAlert(BaseModel):
    id: str
    user_id: str
    risk_type: RiskType
    alert_level: RiskLevel
    message: str
    limit_name: str
    current_value: Decimal
    limit_value: Decimal
    breach_percentage: float
    created_at: datetime = Field(default_factory=datetime.now)
    is_acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None

class VaRResult(BaseModel):
    confidence_level: float
    time_horizon: int  # days
    var_value: Decimal
    expected_shortfall: Decimal
    method: VaRMethod
    calculation_date: datetime = Field(default_factory=datetime.now)
    portfolio_value: Decimal
    risk_factors: Dict[str, Any] = Field(default_factory=dict)

class StressTestResult(BaseModel):
    scenario_name: str
    scenario_description: str
    portfolio_pnl: Decimal
    var_impact: Decimal
    worst_case_loss: Decimal
    probability: float
    created_at: datetime = Field(default_factory=datetime.now)

class CreditExposure(BaseModel):
    counterparty: str
    exposure_type: str
    current_exposure: Decimal
    potential_exposure: Decimal
    collateral_posted: Decimal
    net_exposure: Decimal
    credit_rating: str
    last_updated: datetime = Field(default_factory=datetime.now)

class RiskMetrics(BaseModel):
    user_id: str
    total_var_95: Decimal
    total_var_99: Decimal
    expected_shortfall: Decimal
    max_drawdown: Decimal
    sharpe_ratio: Decimal
    volatility: Decimal
    beta: Decimal
    correlation_matrix: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    calculated_at: datetime = Field(default_factory=datetime.now)

class EnterpriseRiskEngine:
    def __init__(self):
        self.risk_limits: Dict[str, RiskLimit] = {}
        self.risk_alerts: List[RiskAlert] = []
        self.var_results: Dict[str, VaRResult] = {}
        self.stress_tests: List[StressTestResult] = []
        self.credit_exposures: Dict[str, CreditExposure] = {}
        self.risk_metrics: Dict[str, RiskMetrics] = {}
        self.running = False
        
        # Default risk limits
        self._setup_default_limits()
    
    def _setup_default_limits(self):
        """Setup default risk limits"""
        default_limits = [
            {
                "id": "var_95_daily",
                "user_id": "default",
                "risk_type": RiskType.MARKET,
                "limit_name": "Daily VaR 95%",
                "limit_value": Decimal('1000000'),
                "current_value": Decimal('0'),
                "limit_period": "daily"
            },
            {
                "id": "var_99_daily",
                "user_id": "default",
                "risk_type": RiskType.MARKET,
                "limit_name": "Daily VaR 99%",
                "limit_value": Decimal('2000000'),
                "current_value": Decimal('0'),
                "limit_period": "daily"
            },
            {
                "id": "position_limit",
                "user_id": "default",
                "risk_type": RiskType.MARKET,
                "limit_name": "Position Limit",
                "limit_value": Decimal('5000000'),
                "current_value": Decimal('0'),
                "limit_period": "daily"
            },
            {
                "id": "credit_limit",
                "user_id": "default",
                "risk_type": RiskType.CREDIT,
                "limit_name": "Credit Exposure",
                "limit_value": Decimal('10000000'),
                "current_value": Decimal('0'),
                "limit_period": "daily"
            }
        ]
        
        for limit_data in default_limits:
            limit = RiskLimit(**limit_data)
            self.risk_limits[limit.id] = limit
    
    async def start(self):
        """Start the risk engine"""
        self.running = True
        asyncio.create_task(self._risk_monitor())
        asyncio.create_task(self._var_calculator())
        asyncio.create_task(self._stress_test_engine())
    
    async def stop(self):
        """Stop the risk engine"""
        self.running = False
    
    async def _risk_monitor(self):
        """Monitor risk limits and generate alerts"""
        while self.running:
            try:
                await self._check_risk_limits()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                print(f"Risk monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _var_calculator(self):
        """Calculate VaR periodically"""
        while self.running:
            try:
                await self._calculate_var()
                await asyncio.sleep(300)  # Calculate every 5 minutes
            except Exception as e:
                print(f"VaR calculation error: {e}")
                await asyncio.sleep(300)
    
    async def _stress_test_engine(self):
        """Run stress tests periodically"""
        while self.running:
            try:
                await self._run_stress_tests()
                await asyncio.sleep(3600)  # Run every hour
            except Exception as e:
                print(f"Stress test error: {e}")
                await asyncio.sleep(3600)
    
    async def _check_risk_limits(self):
        """Check all risk limits and generate alerts"""
        for limit_id, limit in self.risk_limits.items():
            if not limit.is_active:
                continue
            
            # Calculate current risk value
            current_value = await self._calculate_current_risk(limit)
            limit.current_value = current_value
            limit.updated_at = datetime.now()
            
            # Check for breaches
            breach_percentage = float((current_value / limit.limit_value) * 100)
            
            if current_value > limit.limit_value:
                # Create critical alert
                alert = RiskAlert(
                    id=f"alert_{limit_id}_{datetime.now().timestamp()}",
                    user_id=limit.user_id,
                    risk_type=limit.risk_type,
                    alert_level=RiskLevel.CRITICAL,
                    message=f"Risk limit breached: {limit.limit_name}",
                    limit_name=limit.limit_name,
                    current_value=current_value,
                    limit_value=limit.limit_value,
                    breach_percentage=breach_percentage
                )
                self.risk_alerts.append(alert)
            
            elif breach_percentage > 80:
                # Create high alert
                alert = RiskAlert(
                    id=f"alert_{limit_id}_{datetime.now().timestamp()}",
                    user_id=limit.user_id,
                    risk_type=limit.risk_type,
                    alert_level=RiskLevel.HIGH,
                    message=f"Risk limit approaching: {limit.limit_name}",
                    limit_name=limit.limit_name,
                    current_value=current_value,
                    limit_value=limit.limit_value,
                    breach_percentage=breach_percentage
                )
                self.risk_alerts.append(alert)
    
    async def _calculate_current_risk(self, limit: RiskLimit) -> Decimal:
        """Calculate current risk value for a limit"""
        if limit.risk_type == RiskType.MARKET:
            # Calculate market risk based on positions
            return await self._calculate_market_risk()
        elif limit.risk_type == RiskType.CREDIT:
            # Calculate credit exposure
            return await self._calculate_credit_exposure()
        elif limit.risk_type == RiskType.OPERATIONAL:
            # Calculate operational risk
            return await self._calculate_operational_risk()
        else:
            return Decimal('0')
    
    async def _calculate_market_risk(self) -> Decimal:
        """Calculate market risk"""
        # Simulate market risk calculation
        base_risk = Decimal('500000')
        volatility_factor = np.random.uniform(0.8, 1.2)
        return base_risk * Decimal(str(volatility_factor))
    
    async def _calculate_credit_exposure(self) -> Decimal:
        """Calculate credit exposure"""
        # Simulate credit exposure calculation
        base_exposure = Decimal('2000000')
        counterparty_factor = np.random.uniform(0.9, 1.1)
        return base_exposure * Decimal(str(counterparty_factor))
    
    async def _calculate_operational_risk(self) -> Decimal:
        """Calculate operational risk"""
        # Simulate operational risk calculation
        base_risk = Decimal('100000')
        operational_factor = np.random.uniform(0.5, 1.5)
        return base_risk * Decimal(str(operational_factor))
    
    async def _calculate_var(self):
        """Calculate Value at Risk"""
        # Simulate VaR calculation
        portfolio_value = Decimal('10000000')
        
        # Historical VaR
        var_95_historical = portfolio_value * Decimal('0.05')  # 5% of portfolio
        var_99_historical = portfolio_value * Decimal('0.08')  # 8% of portfolio
        
        # Monte Carlo VaR
        var_95_mc = portfolio_value * Decimal('0.06')
        var_99_mc = portfolio_value * Decimal('0.09')
        
        # Store results
        self.var_results["historical_95"] = VaRResult(
            confidence_level=0.95,
            time_horizon=1,
            var_value=var_95_historical,
            expected_shortfall=var_95_historical * Decimal('1.2'),
            method=VaRMethod.HISTORICAL,
            portfolio_value=portfolio_value
        )
        
        self.var_results["monte_carlo_95"] = VaRResult(
            confidence_level=0.95,
            time_horizon=1,
            var_value=var_95_mc,
            expected_shortfall=var_95_mc * Decimal('1.2'),
            method=VaRMethod.MONTE_CARLO,
            portfolio_value=portfolio_value
        )
    
    async def _run_stress_tests(self):
        """Run stress test scenarios"""
        scenarios = [
            {
                "name": "Market Crash",
                "description": "50% market decline",
                "pnl_impact": Decimal('-5000000'),
                "probability": 0.01
            },
            {
                "name": "Interest Rate Shock",
                "description": "300bp rate increase",
                "pnl_impact": Decimal('-2000000'),
                "probability": 0.05
            },
            {
                "name": "Commodity Price Shock",
                "description": "100% commodity price increase",
                "pnl_impact": Decimal('-3000000'),
                "probability": 0.02
            },
            {
                "name": "Credit Event",
                "description": "Major counterparty default",
                "pnl_impact": Decimal('-1000000'),
                "probability": 0.03
            }
        ]
        
        for scenario in scenarios:
            stress_test = StressTestResult(
                scenario_name=scenario["name"],
                scenario_description=scenario["description"],
                portfolio_pnl=scenario["pnl_impact"],
                var_impact=scenario["pnl_impact"] * Decimal('0.8'),
                worst_case_loss=scenario["pnl_impact"],
                probability=scenario["probability"]
            )
            self.stress_tests.append(stress_test)
    
    # Public API methods
    async def create_risk_limit(self, limit: RiskLimit) -> RiskLimit:
        """Create a new risk limit"""
        self.risk_limits[limit.id] = limit
        return limit
    
    async def get_risk_limits(self, user_id: str) -> List[RiskLimit]:
        """Get risk limits for user"""
        return [limit for limit in self.risk_limits.values() if limit.user_id == user_id]
    
    async def get_risk_alerts(self, user_id: str, acknowledged: Optional[bool] = None) -> List[RiskAlert]:
        """Get risk alerts for user"""
        alerts = [alert for alert in self.risk_alerts if alert.user_id == user_id]
        if acknowledged is not None:
            alerts = [alert for alert in alerts if alert.is_acknowledged == acknowledged]
        return sorted(alerts, key=lambda x: x.created_at, reverse=True)
    
    async def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """Acknowledge a risk alert"""
        for alert in self.risk_alerts:
            if alert.id == alert_id and alert.user_id == user_id:
                alert.is_acknowledged = True
                alert.acknowledged_by = user_id
                alert.acknowledged_at = datetime.now()
                return True
        return False
    
    async def get_var_results(self, method: Optional[VaRMethod] = None) -> List[VaRResult]:
        """Get VaR results"""
        results = list(self.var_results.values())
        if method:
            results = [result for result in results if result.method == method]
        return results
    
    async def get_stress_tests(self, limit: Optional[int] = None) -> List[StressTestResult]:
        """Get stress test results"""
        tests = sorted(self.stress_tests, key=lambda x: x.created_at, reverse=True)
        if limit:
            tests = tests[:limit]
        return tests
    
    async def calculate_portfolio_risk_metrics(self, user_id: str) -> RiskMetrics:
        """Calculate comprehensive risk metrics for portfolio"""
        # Simulate risk metrics calculation
        metrics = RiskMetrics(
            user_id=user_id,
            total_var_95=Decimal('500000'),
            total_var_99=Decimal('800000'),
            expected_shortfall=Decimal('600000'),
            max_drawdown=Decimal('-1200000'),
            sharpe_ratio=Decimal('1.8'),
            volatility=Decimal('0.15'),
            beta=Decimal('0.9'),
            correlation_matrix={
                "ELEC_SPOT": {"NG_HENRY": 0.7, "BRENT_CRUDE": 0.3},
                "NG_HENRY": {"ELEC_SPOT": 0.7, "BRENT_CRUDE": 0.5},
                "BRENT_CRUDE": {"ELEC_SPOT": 0.3, "NG_HENRY": 0.5}
            }
        )
        
        self.risk_metrics[user_id] = metrics
        return metrics
    
    async def get_credit_exposures(self, user_id: str) -> List[CreditExposure]:
        """Get credit exposures for user"""
        # Simulate credit exposures
        exposures = [
            CreditExposure(
                counterparty="EnergyCorp Ltd",
                exposure_type="Physical",
                current_exposure=Decimal('2000000'),
                potential_exposure=Decimal('3000000'),
                collateral_posted=Decimal('500000'),
                net_exposure=Decimal('1500000'),
                credit_rating="A+"
            ),
            CreditExposure(
                counterparty="PowerGen Inc",
                exposure_type="Financial",
                current_exposure=Decimal('1500000'),
                potential_exposure=Decimal('2000000'),
                collateral_posted=Decimal('300000'),
                net_exposure=Decimal('1200000'),
                credit_rating="A"
            )
        ]
        
        return exposures
    
    async def run_custom_stress_test(self, scenario_name: str, scenario_params: Dict[str, Any]) -> StressTestResult:
        """Run custom stress test scenario"""
        # Simulate custom stress test
        stress_test = StressTestResult(
            scenario_name=scenario_name,
            scenario_description=f"Custom scenario: {scenario_name}",
            portfolio_pnl=Decimal(str(scenario_params.get("pnl_impact", -1000000))),
            var_impact=Decimal(str(scenario_params.get("var_impact", -800000))),
            worst_case_loss=Decimal(str(scenario_params.get("worst_case", -1500000))),
            probability=scenario_params.get("probability", 0.1)
        )
        
        self.stress_tests.append(stress_test)
        return stress_test

# Global risk engine instance
risk_engine = EnterpriseRiskEngine()
