"""
Advanced Operational Risk Engine for ETRM/CTRM Enterprise Application
Implements operational risk models and controls
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from decimal import Decimal
from sqlalchemy.orm import Session
import json
from scipy import stats
from scipy.optimize import minimize

logger = logging.getLogger(__name__)

class OperationalRiskCategory(Enum):
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

class RiskControlType(Enum):
    PREVENTIVE = "preventive"
    DETECTIVE = "detective"
    CORRECTIVE = "corrective"
    COMPENSATING = "compensating"

class RiskAssessmentMethod(Enum):
    BASIC_INDICATOR = "basic_indicator"
    STANDARDIZED_APPROACH = "standardized_approach"
    ADVANCED_MEASUREMENT = "advanced_measurement"
    SCENARIO_ANALYSIS = "scenario_analysis"
    LOSS_DISTRIBUTION = "loss_distribution"

@dataclass
class OperationalRiskEvent:
    """Operational risk event"""
    event_id: str
    event_type: OperationalRiskCategory
    description: str
    severity: str  # low, medium, high, critical
    impact_amount: float
    impact_currency: str
    occurrence_date: datetime
    discovery_date: datetime
    resolution_date: Optional[datetime] = None
    root_cause: str = ""
    business_line: str = ""
    location: str = ""
    status: str = "open"  # open, investigating, resolved, closed
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RiskControl:
    """Risk control definition"""
    control_id: str
    control_name: str
    control_type: RiskControlType
    risk_category: OperationalRiskCategory
    description: str
    effectiveness_score: float  # 0-1
    cost: float
    implementation_date: datetime
    review_frequency: int  # days
    last_review: datetime
    next_review: datetime
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RiskScenario:
    """Risk scenario for scenario analysis"""
    scenario_id: str
    scenario_name: str
    risk_category: OperationalRiskCategory
    description: str
    probability: float  # 0-1
    impact_amount: float
    impact_currency: str
    frequency: int  # events per year
    severity: str
    business_line: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class OperationalRiskAssessment:
    """Operational risk assessment result"""
    assessment_id: str
    business_line: str
    risk_category: OperationalRiskCategory
    assessment_method: RiskAssessmentMethod
    expected_loss: float
    unexpected_loss: float
    value_at_risk: float
    expected_shortfall: float
    confidence_level: float
    time_horizon: int  # days
    calculated_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

class OperationalRiskEngine:
    """Advanced operational risk engine"""
    
    def __init__(self, db: Session):
        self.db = db
        self.risk_events: Dict[str, OperationalRiskEvent] = {}
        self.risk_controls: Dict[str, RiskControl] = {}
        self.risk_scenarios: Dict[str, RiskScenario] = {}
        self.risk_assessments: Dict[str, OperationalRiskAssessment] = {}
        
        # Risk parameters
        self.risk_parameters = {
            "confidence_level": 0.99,
            "time_horizon": 1,  # year
            "correlation": 0.3,
            "volatility": 0.2
        }
        
        # Business line mapping
        self.business_lines = {
            "trading": ["power_trading", "gas_trading", "oil_trading"],
            "risk_management": ["market_risk", "credit_risk", "operational_risk"],
            "operations": ["settlement", "clearing", "reporting"],
            "technology": ["systems", "infrastructure", "cybersecurity"],
            "compliance": ["regulatory", "audit", "legal"]
        }
        
        # Initialize risk controls
        self._initialize_risk_controls()
        
        # Initialize risk scenarios
        self._initialize_risk_scenarios()
    
    def _initialize_risk_controls(self):
        """Initialize default risk controls"""
        
        # Internal fraud controls
        self._add_risk_control(
            control_id="IF_001",
            control_name="Segregation of Duties",
            control_type=RiskControlType.PREVENTIVE,
            risk_category=OperationalRiskCategory.INTERNAL_FRAUD,
            description="Separation of trading, settlement, and risk management functions",
            effectiveness_score=0.8,
            cost=50000
        )
        
        self._add_risk_control(
            control_id="IF_002",
            control_name="Dual Authorization",
            control_type=RiskControlType.PREVENTIVE,
            risk_category=OperationalRiskCategory.INTERNAL_FRAUD,
            description="Require dual authorization for large trades",
            effectiveness_score=0.7,
            cost=30000
        )
        
        # External fraud controls
        self._add_risk_control(
            control_id="EF_001",
            control_name="KYC/AML Procedures",
            control_type=RiskControlType.PREVENTIVE,
            risk_category=OperationalRiskCategory.EXTERNAL_FRAUD,
            description="Know Your Customer and Anti-Money Laundering procedures",
            effectiveness_score=0.9,
            cost=100000
        )
        
        # System failure controls
        self._add_risk_control(
            control_id="SF_001",
            control_name="System Redundancy",
            control_type=RiskControlType.PREVENTIVE,
            risk_category=OperationalRiskCategory.SYSTEM_FAILURE,
            description="Backup systems and disaster recovery",
            effectiveness_score=0.85,
            cost=200000
        )
        
        self._add_risk_control(
            control_id="SF_002",
            control_name="System Monitoring",
            control_type=RiskControlType.DETECTIVE,
            risk_category=OperationalRiskCategory.SYSTEM_FAILURE,
            description="Real-time system monitoring and alerting",
            effectiveness_score=0.75,
            cost=150000
        )
        
        # Process failure controls
        self._add_risk_control(
            control_id="PF_001",
            control_name="Process Documentation",
            control_type=RiskControlType.PREVENTIVE,
            risk_category=OperationalRiskCategory.PROCESS_FAILURE,
            description="Comprehensive process documentation and training",
            effectiveness_score=0.6,
            cost=80000
        )
        
        # Regulatory compliance controls
        self._add_risk_control(
            control_id="RC_001",
            control_name="Compliance Monitoring",
            control_type=RiskControlType.DETECTIVE,
            risk_category=OperationalRiskCategory.REGULATORY_COMPLIANCE,
            description="Automated compliance monitoring and reporting",
            effectiveness_score=0.9,
            cost=120000
        )
    
    def _initialize_risk_scenarios(self):
        """Initialize risk scenarios for scenario analysis"""
        
        # Internal fraud scenarios
        self._add_risk_scenario(
            scenario_id="SC_001",
            scenario_name="Rogue Trader",
            risk_category=OperationalRiskCategory.INTERNAL_FRAUD,
            description="Unauthorized trading by employee resulting in significant losses",
            probability=0.01,
            impact_amount=10000000,
            impact_currency="USD",
            frequency=1,
            severity="critical",
            business_line="trading"
        )
        
        # External fraud scenarios
        self._add_risk_scenario(
            scenario_id="SC_002",
            scenario_name="Cyber Attack",
            risk_category=OperationalRiskCategory.EXTERNAL_FRAUD,
            description="Cyber attack resulting in data breach and system compromise",
            probability=0.05,
            impact_amount=5000000,
            impact_currency="USD",
            frequency=2,
            severity="high",
            business_line="technology"
        )
        
        # System failure scenarios
        self._add_risk_scenario(
            scenario_id="SC_003",
            scenario_name="Trading System Failure",
            risk_category=OperationalRiskCategory.SYSTEM_FAILURE,
            description="Complete failure of trading system during market hours",
            probability=0.02,
            impact_amount=2000000,
            impact_currency="USD",
            frequency=1,
            severity="high",
            business_line="technology"
        )
        
        # Business disruption scenarios
        self._add_risk_scenario(
            scenario_id="SC_004",
            scenario_name="Natural Disaster",
            risk_category=OperationalRiskCategory.BUSINESS_DISRUPTION,
            description="Natural disaster affecting trading operations",
            probability=0.01,
            impact_amount=15000000,
            impact_currency="USD",
            frequency=1,
            severity="critical",
            business_line="operations"
        )
        
        # Regulatory compliance scenarios
        self._add_risk_scenario(
            scenario_id="SC_005",
            scenario_name="Regulatory Fine",
            risk_category=OperationalRiskCategory.REGULATORY_COMPLIANCE,
            description="Significant regulatory fine for compliance violations",
            probability=0.03,
            impact_amount=8000000,
            impact_currency="USD",
            frequency=1,
            severity="high",
            business_line="compliance"
        )
    
    def _add_risk_control(self, 
                         control_id: str,
                         control_name: str,
                         control_type: RiskControlType,
                         risk_category: OperationalRiskCategory,
                         description: str,
                         effectiveness_score: float,
                         cost: float) -> RiskControl:
        """Add risk control"""
        
        control = RiskControl(
            control_id=control_id,
            control_name=control_name,
            control_type=control_type,
            risk_category=risk_category,
            description=description,
            effectiveness_score=effectiveness_score,
            cost=cost,
            implementation_date=datetime.utcnow(),
            review_frequency=365,  # Annual review
            last_review=datetime.utcnow(),
            next_review=datetime.utcnow() + timedelta(days=365)
        )
        
        self.risk_controls[control_id] = control
        logger.info(f"Risk control added: {control_id}")
        return control
    
    def _add_risk_scenario(self, 
                          scenario_id: str,
                          scenario_name: str,
                          risk_category: OperationalRiskCategory,
                          description: str,
                          probability: float,
                          impact_amount: float,
                          impact_currency: str,
                          frequency: int,
                          severity: str,
                          business_line: str) -> RiskScenario:
        """Add risk scenario"""
        
        scenario = RiskScenario(
            scenario_id=scenario_id,
            scenario_name=scenario_name,
            risk_category=risk_category,
            description=description,
            probability=probability,
            impact_amount=impact_amount,
            impact_currency=impact_currency,
            frequency=frequency,
            severity=severity,
            business_line=business_line
        )
        
        self.risk_scenarios[scenario_id] = scenario
        logger.info(f"Risk scenario added: {scenario_id}")
        return scenario
    
    def add_risk_event(self, event: OperationalRiskEvent) -> str:
        """Add operational risk event"""
        self.risk_events[event.event_id] = event
        logger.info(f"Risk event added: {event.event_id}")
        return event.event_id
    
    def calculate_operational_risk_capital(self, 
                                         business_line: str,
                                         method: RiskAssessmentMethod = RiskAssessmentMethod.BASIC_INDICATOR) -> OperationalRiskAssessment:
        """Calculate operational risk capital using specified method"""
        
        if method == RiskAssessmentMethod.BASIC_INDICATOR:
            return self._calculate_basic_indicator_approach(business_line)
        elif method == RiskAssessmentMethod.STANDARDIZED_APPROACH:
            return self._calculate_standardized_approach(business_line)
        elif method == RiskAssessmentMethod.ADVANCED_MEASUREMENT:
            return self._calculate_advanced_measurement_approach(business_line)
        elif method == RiskAssessmentMethod.SCENARIO_ANALYSIS:
            return self._calculate_scenario_analysis(business_line)
        elif method == RiskAssessmentMethod.LOSS_DISTRIBUTION:
            return self._calculate_loss_distribution_approach(business_line)
        else:
            raise ValueError(f"Unknown risk assessment method: {method}")
    
    def _calculate_basic_indicator_approach(self, business_line: str) -> OperationalRiskAssessment:
        """Calculate operational risk capital using Basic Indicator Approach"""
        
        # Get gross income for business line
        gross_income = self._get_gross_income(business_line)
        
        # Basic Indicator Approach: 15% of gross income
        operational_risk_capital = gross_income * 0.15
        
        # Calculate VaR and ES
        var_99 = operational_risk_capital * 0.8  # Simplified
        expected_shortfall = operational_risk_capital * 0.9  # Simplified
        
        assessment = OperationalRiskAssessment(
            assessment_id=f"ORA_{business_line}_{int(datetime.utcnow().timestamp())}",
            business_line=business_line,
            risk_category=OperationalRiskCategory.INTERNAL_FRAUD,  # Default category
            assessment_method=RiskAssessmentMethod.BASIC_INDICATOR,
            expected_loss=operational_risk_capital * 0.1,
            unexpected_loss=operational_risk_capital * 0.9,
            value_at_risk=var_99,
            expected_shortfall=expected_shortfall,
            confidence_level=0.99,
            time_horizon=1,
            calculated_at=datetime.utcnow()
        )
        
        self.risk_assessments[assessment.assessment_id] = assessment
        return assessment
    
    def _calculate_standardized_approach(self, business_line: str) -> OperationalRiskAssessment:
        """Calculate operational risk capital using Standardized Approach"""
        
        # Get business line beta factors
        beta_factors = {
            "trading": 0.18,
            "risk_management": 0.12,
            "operations": 0.15,
            "technology": 0.12,
            "compliance": 0.10
        }
        
        beta_factor = beta_factors.get(business_line, 0.15)
        gross_income = self._get_gross_income(business_line)
        
        # Standardized Approach: beta * gross income
        operational_risk_capital = gross_income * beta_factor
        
        # Calculate VaR and ES
        var_99 = operational_risk_capital * 0.8
        expected_shortfall = operational_risk_capital * 0.9
        
        assessment = OperationalRiskAssessment(
            assessment_id=f"ORA_{business_line}_{int(datetime.utcnow().timestamp())}",
            business_line=business_line,
            risk_category=OperationalRiskCategory.INTERNAL_FRAUD,
            assessment_method=RiskAssessmentMethod.STANDARDIZED_APPROACH,
            expected_loss=operational_risk_capital * 0.1,
            unexpected_loss=operational_risk_capital * 0.9,
            value_at_risk=var_99,
            expected_shortfall=expected_shortfall,
            confidence_level=0.99,
            time_horizon=1,
            calculated_at=datetime.utcnow()
        )
        
        self.risk_assessments[assessment.assessment_id] = assessment
        return assessment
    
    def _calculate_advanced_measurement_approach(self, business_line: str) -> OperationalRiskAssessment:
        """Calculate operational risk capital using Advanced Measurement Approach"""
        
        # Get historical loss data
        historical_losses = self._get_historical_losses(business_line)
        
        if not historical_losses:
            # Fallback to basic approach
            return self._calculate_basic_indicator_approach(business_line)
        
        # Fit loss distribution (simplified)
        losses_array = np.array(historical_losses)
        
        # Calculate statistics
        mean_loss = np.mean(losses_array)
        std_loss = np.std(losses_array)
        
        # Calculate VaR and ES using normal distribution
        z_score = stats.norm.ppf(0.99)
        var_99 = mean_loss + z_score * std_loss
        expected_shortfall = mean_loss + (z_score + 1) * std_loss
        
        # Operational risk capital
        operational_risk_capital = max(var_99, mean_loss * 2)
        
        assessment = OperationalRiskAssessment(
            assessment_id=f"ORA_{business_line}_{int(datetime.utcnow().timestamp())}",
            business_line=business_line,
            risk_category=OperationalRiskCategory.INTERNAL_FRAUD,
            assessment_method=RiskAssessmentMethod.ADVANCED_MEASUREMENT,
            expected_loss=mean_loss,
            unexpected_loss=operational_risk_capital - mean_loss,
            value_at_risk=var_99,
            expected_shortfall=expected_shortfall,
            confidence_level=0.99,
            time_horizon=1,
            calculated_at=datetime.utcnow()
        )
        
        self.risk_assessments[assessment.assessment_id] = assessment
        return assessment
    
    def _calculate_scenario_analysis(self, business_line: str) -> OperationalRiskAssessment:
        """Calculate operational risk capital using scenario analysis"""
        
        # Get scenarios for business line
        business_scenarios = [scenario for scenario in self.risk_scenarios.values() 
                            if scenario.business_line == business_line]
        
        if not business_scenarios:
            return self._calculate_basic_indicator_approach(business_line)
        
        # Calculate expected loss from scenarios
        expected_loss = sum(scenario.probability * scenario.impact_amount for scenario in business_scenarios)
        
        # Calculate VaR and ES
        scenario_impacts = [scenario.impact_amount for scenario in business_scenarios]
        var_99 = np.percentile(scenario_impacts, 99)
        expected_shortfall = np.mean([impact for impact in scenario_impacts if impact >= var_99])
        
        # Operational risk capital
        operational_risk_capital = max(var_99, expected_loss * 2)
        
        assessment = OperationalRiskAssessment(
            assessment_id=f"ORA_{business_line}_{int(datetime.utcnow().timestamp())}",
            business_line=business_line,
            risk_category=OperationalRiskCategory.INTERNAL_FRAUD,
            assessment_method=RiskAssessmentMethod.SCENARIO_ANALYSIS,
            expected_loss=expected_loss,
            unexpected_loss=operational_risk_capital - expected_loss,
            value_at_risk=var_99,
            expected_shortfall=expected_shortfall,
            confidence_level=0.99,
            time_horizon=1,
            calculated_at=datetime.utcnow()
        )
        
        self.risk_assessments[assessment.assessment_id] = assessment
        return assessment
    
    def _calculate_loss_distribution_approach(self, business_line: str) -> OperationalRiskAssessment:
        """Calculate operational risk capital using Loss Distribution Approach"""
        
        # Get historical loss data
        historical_losses = self._get_historical_losses(business_line)
        
        if not historical_losses:
            return self._calculate_basic_indicator_approach(business_line)
        
        # Fit loss distribution (simplified - using lognormal)
        losses_array = np.array(historical_losses)
        log_losses = np.log(losses_array)
        
        # Calculate parameters
        mu = np.mean(log_losses)
        sigma = np.std(log_losses)
        
        # Calculate VaR and ES
        var_99 = np.exp(mu + sigma * stats.norm.ppf(0.99))
        expected_shortfall = np.exp(mu + sigma * (stats.norm.ppf(0.99) + 1))
        
        # Operational risk capital
        operational_risk_capital = max(var_99, np.mean(losses_array) * 2)
        
        assessment = OperationalRiskAssessment(
            assessment_id=f"ORA_{business_line}_{int(datetime.utcnow().timestamp())}",
            business_line=business_line,
            risk_category=OperationalRiskCategory.INTERNAL_FRAUD,
            assessment_method=RiskAssessmentMethod.LOSS_DISTRIBUTION,
            expected_loss=np.mean(losses_array),
            unexpected_loss=operational_risk_capital - np.mean(losses_array),
            value_at_risk=var_99,
            expected_shortfall=expected_shortfall,
            confidence_level=0.99,
            time_horizon=1,
            calculated_at=datetime.utcnow()
        )
        
        self.risk_assessments[assessment.assessment_id] = assessment
        return assessment
    
    def _get_gross_income(self, business_line: str) -> float:
        """Get gross income for business line"""
        # Simplified gross income calculation
        base_income = {
            "trading": 100000000,  # $100M
            "risk_management": 20000000,  # $20M
            "operations": 30000000,  # $30M
            "technology": 15000000,  # $15M
            "compliance": 10000000   # $10M
        }
        
        return base_income.get(business_line, 50000000)  # Default $50M
    
    def _get_historical_losses(self, business_line: str) -> List[float]:
        """Get historical loss data for business line"""
        # Get risk events for business line
        business_events = [event for event in self.risk_events.values() 
                         if event.business_line == business_line]
        
        if not business_events:
            # Return simulated historical losses
            return [100000, 500000, 200000, 800000, 300000, 150000, 400000, 600000, 250000, 350000]
        
        return [event.impact_amount for event in business_events]
    
    def calculate_control_effectiveness(self, business_line: str) -> Dict[str, Any]:
        """Calculate control effectiveness for business line"""
        
        # Get controls for business line
        business_controls = [control for control in self.risk_controls.values() 
                           if control.is_active]
        
        if not business_controls:
            return {"message": f"No controls found for business line {business_line}"}
        
        # Calculate effectiveness metrics
        total_effectiveness = sum(control.effectiveness_score for control in business_controls)
        average_effectiveness = total_effectiveness / len(business_controls)
        
        # Calculate cost-effectiveness
        total_cost = sum(control.cost for control in business_controls)
        cost_effectiveness = total_effectiveness / total_cost if total_cost > 0 else 0
        
        # Control coverage by risk category
        risk_category_coverage = {}
        for category in OperationalRiskCategory:
            category_controls = [control for control in business_controls 
                              if control.risk_category == category]
            risk_category_coverage[category.value] = {
                "control_count": len(category_controls),
                "average_effectiveness": np.mean([c.effectiveness_score for c in category_controls]) if category_controls else 0
            }
        
        return {
            "business_line": business_line,
            "total_controls": len(business_controls),
            "average_effectiveness": average_effectiveness,
            "total_cost": total_cost,
            "cost_effectiveness": cost_effectiveness,
            "risk_category_coverage": risk_category_coverage,
            "controls_requiring_review": len([control for control in business_controls 
                                            if control.next_review <= datetime.utcnow()])
        }
    
    def calculate_risk_metrics(self, business_line: str) -> Dict[str, Any]:
        """Calculate comprehensive risk metrics for business line"""
        
        # Get risk events for business line
        business_events = [event for event in self.risk_events.values() 
                         if event.business_line == business_line]
        
        if not business_events:
            return {"message": f"No risk events found for business line {business_line}"}
        
        # Calculate event metrics
        total_events = len(business_events)
        total_impact = sum(event.impact_amount for event in business_events)
        average_impact = total_impact / total_events if total_events > 0 else 0
        
        # Event frequency by severity
        severity_distribution = {}
        for severity in ["low", "medium", "high", "critical"]:
            severity_events = [event for event in business_events if event.severity == severity]
            severity_distribution[severity] = {
                "count": len(severity_events),
                "total_impact": sum(event.impact_amount for event in severity_events),
                "percentage": len(severity_events) / total_events * 100 if total_events > 0 else 0
            }
        
        # Event frequency by risk category
        category_distribution = {}
        for category in OperationalRiskCategory:
            category_events = [event for event in business_events if event.event_type == category]
            category_distribution[category.value] = {
                "count": len(category_events),
                "total_impact": sum(event.impact_amount for event in category_events),
                "percentage": len(category_events) / total_events * 100 if total_events > 0 else 0
            }
        
        # Time-based analysis
        recent_events = [event for event in business_events 
                        if event.occurrence_date >= datetime.utcnow() - timedelta(days=365)]
        recent_impact = sum(event.impact_amount for event in recent_events)
        
        return {
            "business_line": business_line,
            "total_events": total_events,
            "total_impact": total_impact,
            "average_impact": average_impact,
            "recent_events_1y": len(recent_events),
            "recent_impact_1y": recent_impact,
            "severity_distribution": severity_distribution,
            "category_distribution": category_distribution,
            "trend_analysis": {
                "events_last_30d": len([event for event in business_events 
                                      if event.occurrence_date >= datetime.utcnow() - timedelta(days=30)]),
                "events_last_90d": len([event for event in business_events 
                                      if event.occurrence_date >= datetime.utcnow() - timedelta(days=90)]),
                "events_last_365d": len(recent_events)
            }
        }
    
    def get_operational_risk_summary(self) -> Dict[str, Any]:
        """Get operational risk system summary"""
        
        total_events = len(self.risk_events)
        total_controls = len(self.risk_controls)
        total_scenarios = len(self.risk_scenarios)
        total_assessments = len(self.risk_assessments)
        
        # Event analysis
        open_events = len([event for event in self.risk_events.values() if event.status == "open"])
        resolved_events = len([event for event in self.risk_events.values() if event.status == "resolved"])
        
        # Control analysis
        active_controls = len([control for control in self.risk_controls.values() if control.is_active])
        controls_requiring_review = len([control for control in self.risk_controls.values() 
                                        if control.next_review <= datetime.utcnow()])
        
        # Impact analysis
        total_impact = sum(event.impact_amount for event in self.risk_events.values())
        average_impact = total_impact / total_events if total_events > 0 else 0
        
        # Risk category analysis
        risk_category_counts = {}
        for category in OperationalRiskCategory:
            risk_category_counts[category.value] = len([event for event in self.risk_events.values() 
                                                      if event.event_type == category])
        
        return {
            "total_events": total_events,
            "open_events": open_events,
            "resolved_events": resolved_events,
            "resolution_rate": resolved_events / total_events if total_events > 0 else 0,
            "total_controls": total_controls,
            "active_controls": active_controls,
            "controls_requiring_review": controls_requiring_review,
            "total_scenarios": total_scenarios,
            "total_assessments": total_assessments,
            "total_impact": total_impact,
            "average_impact": average_impact,
            "risk_category_distribution": risk_category_counts,
            "business_lines": list(self.business_lines.keys())
        }
