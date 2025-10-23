"""
Advanced Compliance Engine for ETRM/CTRM Enterprise Application
Implements comprehensive compliance engine with regulatory reporting and monitoring
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
import re

logger = logging.getLogger(__name__)

class RegulatoryFramework(Enum):
    REMIT = "remit"  # EU Regulation on Energy Market Integrity and Transparency
    FERC = "ferc"    # Federal Energy Regulatory Commission (US)
    CFTC = "cftc"    # Commodity Futures Trading Commission (US)
    ESMA = "esma"    # European Securities and Markets Authority
    ACER = "acer"    # Agency for the Cooperation of Energy Regulators
    OFGEM = "ofgem"  # Office of Gas and Electricity Markets (UK)
    AEMC = "aemc"    # Australian Energy Market Commission
    ISLAMIC_FINANCE = "islamic_finance"

class ComplianceRuleType(Enum):
    POSITION_LIMIT = "position_limit"
    VOLUME_LIMIT = "volume_limit"
    PRICE_LIMIT = "price_limit"
    TIME_LIMIT = "time_limit"
    REPORTING_REQUIREMENT = "reporting_requirement"
    DISCLOSURE_REQUIREMENT = "disclosure_requirement"
    ANTI_MANIPULATION = "anti_manipulation"
    MARKET_ABUSE = "market_abuse"
    INSIDER_TRADING = "insider_trading"
    WASH_TRADING = "wash_trading"

class ViolationSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ComplianceRule:
    """Compliance rule definition"""
    rule_id: str
    framework: RegulatoryFramework
    rule_type: ComplianceRuleType
    name: str
    description: str
    threshold: float
    unit: str
    currency: str = "USD"
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ComplianceViolation:
    """Compliance violation"""
    violation_id: str
    rule_id: str
    counterparty_id: str
    trade_id: str
    violation_type: ComplianceRuleType
    severity: ViolationSeverity
    current_value: float
    threshold_value: float
    violation_amount: float
    violation_percentage: float
    detected_at: datetime
    status: str = "open"  # open, acknowledged, resolved
    resolution_date: Optional[datetime] = None
    resolution_notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RegulatoryReport:
    """Regulatory report"""
    report_id: str
    framework: RegulatoryFramework
    report_type: str
    reporting_period: Tuple[datetime, datetime]
    submission_deadline: datetime
    status: str = "draft"  # draft, submitted, approved, rejected
    submitted_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MarketAbuseDetection:
    """Market abuse detection result"""
    detection_id: str
    detection_type: str
    confidence_score: float
    severity: ViolationSeverity
    description: str
    detected_at: datetime
    trade_ids: List[str] = field(default_factory=list)
    counterparty_ids: List[str] = field(default_factory=list)
    evidence: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"  # pending, investigated, resolved, false_positive

class ComplianceEngine:
    """Advanced compliance engine with regulatory monitoring"""
    
    def __init__(self, db: Session):
        self.db = db
        self.compliance_rules: Dict[str, ComplianceRule] = {}
        self.violations: Dict[str, ComplianceViolation] = {}
        self.regulatory_reports: Dict[str, RegulatoryReport] = {}
        self.market_abuse_detections: Dict[str, MarketAbuseDetection] = {}
        
        # Initialize regulatory frameworks
        self._initialize_regulatory_frameworks()
        
        # Initialize compliance rules
        self._initialize_compliance_rules()
        
    def _initialize_regulatory_frameworks(self):
        """Initialize regulatory frameworks and their requirements"""
        
        self.regulatory_frameworks = {
            RegulatoryFramework.REMIT: {
                "name": "Regulation on Energy Market Integrity and Transparency",
                "jurisdiction": "EU",
                "reporting_requirements": [
                    "inside_information_disclosure",
                    "transaction_reporting",
                    "position_reporting",
                    "market_abuse_monitoring"
                ],
                "position_limits": {
                    "power": 1000,  # MW
                    "gas": 500,     # MWh
                    "oil": 1000     # bbl
                },
                "reporting_deadlines": {
                    "transaction_reporting": "T+1",
                    "position_reporting": "weekly",
                    "inside_information": "immediate"
                }
            },
            RegulatoryFramework.FERC: {
                "name": "Federal Energy Regulatory Commission",
                "jurisdiction": "US",
                "reporting_requirements": [
                    "electric_sales_reporting",
                    "natural_gas_reporting",
                    "market_manipulation_prevention",
                    "price_reporting"
                ],
                "position_limits": {
                    "power": 2000,  # MW
                    "gas": 1000,    # MMBtu
                    "oil": 2000     # bbl
                },
                "reporting_deadlines": {
                    "electric_sales": "monthly",
                    "natural_gas": "monthly",
                    "price_reporting": "daily"
                }
            },
            RegulatoryFramework.CFTC: {
                "name": "Commodity Futures Trading Commission",
                "jurisdiction": "US",
                "reporting_requirements": [
                    "large_trader_reporting",
                    "position_limits",
                    "market_manipulation_prevention",
                    "swap_data_reporting"
                ],
                "position_limits": {
                    "crude_oil": 10000,  # contracts
                    "natural_gas": 5000,  # contracts
                    "power": 2000        # contracts
                },
                "reporting_deadlines": {
                    "large_trader": "daily",
                    "position_limits": "daily",
                    "swap_data": "T+1"
                }
            },
            RegulatoryFramework.ISLAMIC_FINANCE: {
                "name": "Islamic Finance Compliance",
                "jurisdiction": "Global",
                "reporting_requirements": [
                    "sharia_compliance_monitoring",
                    "riba_prevention",
                    "gharar_prevention",
                    "maysir_prevention"
                ],
                "compliance_requirements": {
                    "no_interest": True,
                    "no_speculation": True,
                    "asset_backed": True,
                    "ethical_investment": True
                }
            }
        }
    
    def _initialize_compliance_rules(self):
        """Initialize default compliance rules"""
        
        # REMIT rules
        self._add_compliance_rule(
            rule_id="REMIT_POSITION_LIMIT_POWER",
            framework=RegulatoryFramework.REMIT,
            rule_type=ComplianceRuleType.POSITION_LIMIT,
            name="REMIT Power Position Limit",
            description="Maximum position limit for power trading under REMIT",
            threshold=1000,
            unit="MW"
        )
        
        self._add_compliance_rule(
            rule_id="REMIT_VOLUME_LIMIT_DAILY",
            framework=RegulatoryFramework.REMIT,
            rule_type=ComplianceRuleType.VOLUME_LIMIT,
            name="REMIT Daily Volume Limit",
            description="Maximum daily trading volume under REMIT",
            threshold=10000,
            unit="MWh"
        )
        
        # FERC rules
        self._add_compliance_rule(
            rule_id="FERC_POSITION_LIMIT_POWER",
            framework=RegulatoryFramework.FERC,
            rule_type=ComplianceRuleType.POSITION_LIMIT,
            name="FERC Power Position Limit",
            description="Maximum position limit for power trading under FERC",
            threshold=2000,
            unit="MW"
        )
        
        # CFTC rules
        self._add_compliance_rule(
            rule_id="CFTC_POSITION_LIMIT_CRUDE",
            framework=RegulatoryFramework.CFTC,
            rule_type=ComplianceRuleType.POSITION_LIMIT,
            name="CFTC Crude Oil Position Limit",
            description="Maximum position limit for crude oil futures under CFTC",
            threshold=10000,
            unit="contracts"
        )
        
        # Islamic Finance rules
        self._add_compliance_rule(
            rule_id="ISLAMIC_NO_RIBA",
            framework=RegulatoryFramework.ISLAMIC_FINANCE,
            rule_type=ComplianceRuleType.ANTI_MANIPULATION,
            name="Islamic Finance - No Riba",
            description="Prohibition of interest-based transactions",
            threshold=0,
            unit="percentage"
        )
    
    def _add_compliance_rule(self, 
                           rule_id: str,
                           framework: RegulatoryFramework,
                           rule_type: ComplianceRuleType,
                           name: str,
                           description: str,
                           threshold: float,
                           unit: str,
                           currency: str = "USD") -> ComplianceRule:
        """Add a compliance rule"""
        
        rule = ComplianceRule(
            rule_id=rule_id,
            framework=framework,
            rule_type=rule_type,
            name=name,
            description=description,
            threshold=threshold,
            unit=unit,
            currency=currency
        )
        
        self.compliance_rules[rule_id] = rule
        logger.info(f"Compliance rule added: {rule_id}")
        return rule
    
    def check_compliance(self, 
                        trade_data: Dict[str, Any],
                        counterparty_id: str,
                        framework: RegulatoryFramework) -> List[ComplianceViolation]:
        """Check compliance for a trade"""
        
        violations = []
        
        # Get applicable rules for framework
        applicable_rules = [rule for rule in self.compliance_rules.values() 
                           if rule.framework == framework and rule.is_active]
        
        for rule in applicable_rules:
            violation = self._check_rule_compliance(rule, trade_data, counterparty_id)
            if violation:
                violations.append(violation)
                self.violations[violation.violation_id] = violation
        
        return violations
    
    def _check_rule_compliance(self, 
                              rule: ComplianceRule,
                              trade_data: Dict[str, Any],
                              counterparty_id: str) -> Optional[ComplianceViolation]:
        """Check compliance for a specific rule"""
        
        if rule.rule_type == ComplianceRuleType.POSITION_LIMIT:
            return self._check_position_limit(rule, trade_data, counterparty_id)
        elif rule.rule_type == ComplianceRuleType.VOLUME_LIMIT:
            return self._check_volume_limit(rule, trade_data, counterparty_id)
        elif rule.rule_type == ComplianceRuleType.PRICE_LIMIT:
            return self._check_price_limit(rule, trade_data, counterparty_id)
        elif rule.rule_type == ComplianceRuleType.ANTI_MANIPULATION:
            return self._check_anti_manipulation(rule, trade_data, counterparty_id)
        elif rule.rule_type == ComplianceRuleType.MARKET_ABUSE:
            return self._check_market_abuse(rule, trade_data, counterparty_id)
        else:
            return None
    
    def _check_position_limit(self, 
                             rule: ComplianceRule,
                             trade_data: Dict[str, Any],
                             counterparty_id: str) -> Optional[ComplianceViolation]:
        """Check position limit compliance"""
        
        # Get current position for counterparty
        current_position = self._get_current_position(counterparty_id, trade_data.get('instrument', ''))
        
        if current_position > rule.threshold:
            violation_id = f"VL_{rule.rule_id}_{counterparty_id}_{int(datetime.utcnow().timestamp())}"
            
            violation = ComplianceViolation(
                violation_id=violation_id,
                rule_id=rule.rule_id,
                counterparty_id=counterparty_id,
                trade_id=trade_data.get('trade_id', ''),
                violation_type=rule.rule_type,
                severity=ViolationSeverity.HIGH if current_position > rule.threshold * 1.5 else ViolationSeverity.MEDIUM,
                current_value=current_position,
                threshold_value=rule.threshold,
                violation_amount=current_position - rule.threshold,
                violation_percentage=((current_position - rule.threshold) / rule.threshold) * 100,
                detected_at=datetime.utcnow()
            )
            
            return violation
        
        return None
    
    def _check_volume_limit(self, 
                           rule: ComplianceRule,
                           trade_data: Dict[str, Any],
                           counterparty_id: str) -> Optional[ComplianceViolation]:
        """Check volume limit compliance"""
        
        # Get daily volume for counterparty
        daily_volume = self._get_daily_volume(counterparty_id, trade_data.get('instrument', ''))
        
        if daily_volume > rule.threshold:
            violation_id = f"VL_{rule.rule_id}_{counterparty_id}_{int(datetime.utcnow().timestamp())}"
            
            violation = ComplianceViolation(
                violation_id=violation_id,
                rule_id=rule.rule_id,
                counterparty_id=counterparty_id,
                trade_id=trade_data.get('trade_id', ''),
                violation_type=rule.rule_type,
                severity=ViolationSeverity.HIGH if daily_volume > rule.threshold * 1.5 else ViolationSeverity.MEDIUM,
                current_value=daily_volume,
                threshold_value=rule.threshold,
                violation_amount=daily_volume - rule.threshold,
                violation_percentage=((daily_volume - rule.threshold) / rule.threshold) * 100,
                detected_at=datetime.utcnow()
            )
            
            return violation
        
        return None
    
    def _check_price_limit(self, 
                          rule: ComplianceRule,
                          trade_data: Dict[str, Any],
                          counterparty_id: str) -> Optional[ComplianceViolation]:
        """Check price limit compliance"""
        
        trade_price = trade_data.get('price', 0)
        
        if trade_price > rule.threshold:
            violation_id = f"PL_{rule.rule_id}_{counterparty_id}_{int(datetime.utcnow().timestamp())}"
            
            violation = ComplianceViolation(
                violation_id=violation_id,
                rule_id=rule.rule_id,
                counterparty_id=counterparty_id,
                trade_id=trade_data.get('trade_id', ''),
                violation_type=rule.rule_type,
                severity=ViolationSeverity.HIGH if trade_price > rule.threshold * 1.2 else ViolationSeverity.MEDIUM,
                current_value=trade_price,
                threshold_value=rule.threshold,
                violation_amount=trade_price - rule.threshold,
                violation_percentage=((trade_price - rule.threshold) / rule.threshold) * 100,
                detected_at=datetime.utcnow()
            )
            
            return violation
        
        return None
    
    def _check_anti_manipulation(self, 
                                rule: ComplianceRule,
                                trade_data: Dict[str, Any],
                                counterparty_id: str) -> Optional[ComplianceViolation]:
        """Check anti-manipulation compliance"""
        
        # Check for wash trading
        if self._detect_wash_trading(trade_data, counterparty_id):
            violation_id = f"AM_{rule.rule_id}_{counterparty_id}_{int(datetime.utcnow().timestamp())}"
            
            violation = ComplianceViolation(
                violation_id=violation_id,
                rule_id=rule.rule_id,
                counterparty_id=counterparty_id,
                trade_id=trade_data.get('trade_id', ''),
                violation_type=rule.rule_type,
                severity=ViolationSeverity.CRITICAL,
                current_value=1,  # Wash trading detected
                threshold_value=0,
                violation_amount=1,
                violation_percentage=100,
                detected_at=datetime.utcnow()
            )
            
            return violation
        
        return None
    
    def _check_market_abuse(self, 
                           rule: ComplianceRule,
                           trade_data: Dict[str, Any],
                           counterparty_id: str) -> Optional[ComplianceViolation]:
        """Check market abuse compliance"""
        
        # Check for suspicious trading patterns
        if self._detect_suspicious_trading(trade_data, counterparty_id):
            violation_id = f"MA_{rule.rule_id}_{counterparty_id}_{int(datetime.utcnow().timestamp())}"
            
            violation = ComplianceViolation(
                violation_id=violation_id,
                rule_id=rule.rule_id,
                counterparty_id=counterparty_id,
                trade_id=trade_data.get('trade_id', ''),
                violation_type=rule.rule_type,
                severity=ViolationSeverity.HIGH,
                current_value=1,  # Suspicious activity detected
                threshold_value=0,
                violation_amount=1,
                violation_percentage=100,
                detected_at=datetime.utcnow()
            )
            
            return violation
        
        return None
    
    def _get_current_position(self, counterparty_id: str, instrument: str) -> float:
        """Get current position for counterparty and instrument"""
        # This would typically query the database
        # For now, return a simulated value
        return np.random.uniform(0, 2000)
    
    def _get_daily_volume(self, counterparty_id: str, instrument: str) -> float:
        """Get daily volume for counterparty and instrument"""
        # This would typically query the database
        # For now, return a simulated value
        return np.random.uniform(0, 15000)
    
    def _detect_wash_trading(self, trade_data: Dict[str, Any], counterparty_id: str) -> bool:
        """Detect wash trading patterns"""
        # Simplified wash trading detection
        # In practice, this would analyze trading patterns, timing, and counterparties
        
        # Check for same counterparty trading with itself
        if trade_data.get('counterparty_id') == counterparty_id:
            return True
        
        # Check for suspicious timing patterns
        trade_time = trade_data.get('timestamp', datetime.utcnow())
        if trade_time.hour in [0, 1, 2, 3, 4, 5]:  # Suspicious early morning trading
            return True
        
        return False
    
    def _detect_suspicious_trading(self, trade_data: Dict[str, Any], counterparty_id: str) -> bool:
        """Detect suspicious trading patterns"""
        # Simplified suspicious trading detection
        
        # Check for large trades
        if trade_data.get('quantity', 0) > 10000:
            return True
        
        # Check for unusual price movements
        if trade_data.get('price', 0) > 1000:  # Unusually high price
            return True
        
        return False
    
    def detect_market_abuse(self, 
                           trades: List[Dict[str, Any]],
                           timeframe_hours: int = 24) -> List[MarketAbuseDetection]:
        """Detect market abuse patterns across multiple trades"""
        
        detections = []
        
        # Detect layering
        layering_detection = self._detect_layering(trades)
        if layering_detection:
            detections.append(layering_detection)
        
        # Detect spoofing
        spoofing_detection = self._detect_spoofing(trades)
        if spoofing_detection:
            detections.append(spoofing_detection)
        
        # Detect pump and dump
        pump_dump_detection = self._detect_pump_and_dump(trades)
        if pump_dump_detection:
            detections.append(pump_dump_detection)
        
        # Store detections
        for detection in detections:
            self.market_abuse_detections[detection.detection_id] = detection
        
        return detections
    
    def _detect_layering(self, trades: List[Dict[str, Any]]) -> Optional[MarketAbuseDetection]:
        """Detect layering manipulation"""
        # Simplified layering detection
        # In practice, this would analyze order book data and trading patterns
        
        if len(trades) < 10:
            return None
        
        # Check for rapid-fire trades
        recent_trades = sorted(trades, key=lambda x: x.get('timestamp', datetime.utcnow()))
        
        if len(recent_trades) >= 5:
            # Check for 5+ trades within 1 minute
            time_diffs = []
            for i in range(1, len(recent_trades)):
                time_diff = (recent_trades[i]['timestamp'] - recent_trades[i-1]['timestamp']).total_seconds()
                time_diffs.append(time_diff)
            
            if min(time_diffs) < 60:  # Less than 1 minute between trades
                detection_id = f"LAYERING_{int(datetime.utcnow().timestamp())}"
                
                return MarketAbuseDetection(
                    detection_id=detection_id,
                    detection_type="layering",
                    confidence_score=0.8,
                    severity=ViolationSeverity.HIGH,
                    description="Potential layering manipulation detected",
                    detected_at=datetime.utcnow(),
                    trade_ids=[trade.get('trade_id', '') for trade in recent_trades[:5]],
                    counterparty_ids=list(set(trade.get('counterparty_id', '') for trade in recent_trades[:5])),
                    evidence={"trade_count": len(recent_trades), "time_analysis": time_diffs}
                )
        
        return None
    
    def _detect_spoofing(self, trades: List[Dict[str, Any]]) -> Optional[MarketAbuseDetection]:
        """Detect spoofing manipulation"""
        # Simplified spoofing detection
        
        if len(trades) < 3:
            return None
        
        # Check for large orders followed by cancellations
        large_trades = [trade for trade in trades if trade.get('quantity', 0) > 5000]
        
        if len(large_trades) >= 3:
            detection_id = f"SPOOFING_{int(datetime.utcnow().timestamp())}"
            
            return MarketAbuseDetection(
                detection_id=detection_id,
                detection_type="spoofing",
                confidence_score=0.7,
                severity=ViolationSeverity.MEDIUM,
                description="Potential spoofing manipulation detected",
                detected_at=datetime.utcnow(),
                trade_ids=[trade.get('trade_id', '') for trade in large_trades],
                counterparty_ids=list(set(trade.get('counterparty_id', '') for trade in large_trades)),
                evidence={"large_trade_count": len(large_trades)}
            )
        
        return None
    
    def _detect_pump_and_dump(self, trades: List[Dict[str, Any]]) -> Optional[MarketAbuseDetection]:
        """Detect pump and dump manipulation"""
        # Simplified pump and dump detection
        
        if len(trades) < 5:
            return None
        
        # Check for price manipulation patterns
        prices = [trade.get('price', 0) for trade in trades if trade.get('price', 0) > 0]
        
        if len(prices) >= 3:
            price_changes = []
            for i in range(1, len(prices)):
                change = (prices[i] - prices[i-1]) / prices[i-1] if prices[i-1] > 0 else 0
                price_changes.append(change)
            
            # Check for significant price increases followed by decreases
            if len(price_changes) >= 2:
                max_increase = max(price_changes)
                max_decrease = min(price_changes)
                
                if max_increase > 0.1 and max_decrease < -0.1:  # 10% increase followed by 10% decrease
                    detection_id = f"PUMP_DUMP_{int(datetime.utcnow().timestamp())}"
                    
                    return MarketAbuseDetection(
                        detection_id=detection_id,
                        detection_type="pump_and_dump",
                        confidence_score=0.9,
                        severity=ViolationSeverity.CRITICAL,
                        description="Potential pump and dump manipulation detected",
                        detected_at=datetime.utcnow(),
                        trade_ids=[trade.get('trade_id', '') for trade in trades],
                        counterparty_ids=list(set(trade.get('counterparty_id', '') for trade in trades)),
                        evidence={"price_changes": price_changes, "max_increase": max_increase, "max_decrease": max_decrease}
                    )
        
        return None
    
    def generate_regulatory_report(self, 
                                 framework: RegulatoryFramework,
                                 report_type: str,
                                 reporting_period: Tuple[datetime, datetime],
                                 submission_deadline: datetime) -> str:
        """Generate regulatory report"""
        
        report_id = f"RR_{framework.value}_{report_type}_{int(datetime.utcnow().timestamp())}"
        
        # Generate report data based on framework
        report_data = self._generate_report_data(framework, report_type, reporting_period)
        
        report = RegulatoryReport(
            report_id=report_id,
            framework=framework,
            report_type=report_type,
            reporting_period=reporting_period,
            submission_deadline=submission_deadline,
            data=report_data
        )
        
        self.regulatory_reports[report_id] = report
        logger.info(f"Regulatory report generated: {report_id}")
        
        return report_id
    
    def _generate_report_data(self, 
                             framework: RegulatoryFramework,
                             report_type: str,
                             reporting_period: Tuple[datetime, datetime]) -> Dict[str, Any]:
        """Generate report data based on framework and type"""
        
        if framework == RegulatoryFramework.REMIT:
            return self._generate_remit_report_data(report_type, reporting_period)
        elif framework == RegulatoryFramework.FERC:
            return self._generate_ferc_report_data(report_type, reporting_period)
        elif framework == RegulatoryFramework.CFTC:
            return self._generate_cftc_report_data(report_type, reporting_period)
        else:
            return {"message": f"Report generation not implemented for {framework.value}"}
    
    def _generate_remit_report_data(self, report_type: str, reporting_period: Tuple[datetime, datetime]) -> Dict[str, Any]:
        """Generate REMIT report data"""
        
        if report_type == "transaction_reporting":
            return {
                "transactions": [
                    {
                        "trade_id": f"T{i}",
                        "instrument": "POWER",
                        "quantity": 100,
                        "price": 50.0,
                        "timestamp": datetime.utcnow().isoformat(),
                        "counterparty": f"CP{i}"
                    }
                    for i in range(10)
                ],
                "total_transactions": 10,
                "total_volume": 1000,
                "total_value": 50000
            }
        elif report_type == "position_reporting":
            return {
                "positions": [
                    {
                        "instrument": "POWER",
                        "net_position": 500,
                        "unit": "MW",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                ],
                "total_positions": 1
            }
        else:
            return {"message": f"REMIT report type {report_type} not implemented"}
    
    def _generate_ferc_report_data(self, report_type: str, reporting_period: Tuple[datetime, datetime]) -> Dict[str, Any]:
        """Generate FERC report data"""
        
        if report_type == "electric_sales":
            return {
                "sales": [
                    {
                        "utility": "Utility A",
                        "sales_volume": 1000,
                        "sales_value": 50000,
                        "period": reporting_period[0].isoformat()
                    }
                ],
                "total_sales": 1000,
                "total_value": 50000
            }
        else:
            return {"message": f"FERC report type {report_type} not implemented"}
    
    def _generate_cftc_report_data(self, report_type: str, reporting_period: Tuple[datetime, datetime]) -> Dict[str, Any]:
        """Generate CFTC report data"""
        
        if report_type == "large_trader":
            return {
                "large_traders": [
                    {
                        "trader_id": "LT001",
                        "instrument": "CRUDE_OIL",
                        "position": 5000,
                        "unit": "contracts",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                ],
                "total_large_traders": 1
            }
        else:
            return {"message": f"CFTC report type {report_type} not implemented"}
    
    def get_compliance_summary(self) -> Dict[str, Any]:
        """Get compliance system summary"""
        
        total_violations = len(self.violations)
        open_violations = len([v for v in self.violations.values() if v.status == "open"])
        resolved_violations = len([v for v in self.violations.values() if v.status == "resolved"])
        
        violations_by_severity = {}
        for severity in ViolationSeverity:
            violations_by_severity[severity.value] = len([v for v in self.violations.values() if v.severity == severity])
        
        total_reports = len(self.regulatory_reports)
        submitted_reports = len([r for r in self.regulatory_reports.values() if r.status == "submitted"])
        
        total_detections = len(self.market_abuse_detections)
        pending_detections = len([d for d in self.market_abuse_detections.values() if d.status == "pending"])
        
        return {
            "total_violations": total_violations,
            "open_violations": open_violations,
            "resolved_violations": resolved_violations,
            "violation_resolution_rate": resolved_violations / total_violations if total_violations > 0 else 0,
            "violations_by_severity": violations_by_severity,
            "total_reports": total_reports,
            "submitted_reports": submitted_reports,
            "report_submission_rate": submitted_reports / total_reports if total_reports > 0 else 0,
            "total_detections": total_detections,
            "pending_detections": pending_detections,
            "detection_resolution_rate": (total_detections - pending_detections) / total_detections if total_detections > 0 else 0,
            "active_rules": len([r for r in self.compliance_rules.values() if r.is_active]),
            "frameworks": list(set(rule.framework.value for rule in self.compliance_rules.values()))
        }
    
    def get_violation_details(self, violation_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a violation"""
        
        violation = self.violations.get(violation_id)
        if not violation:
            return None
        
        rule = self.compliance_rules.get(violation.rule_id)
        
        return {
            "violation_id": violation.violation_id,
            "rule_name": rule.name if rule else "Unknown Rule",
            "rule_description": rule.description if rule else "Unknown Description",
            "framework": rule.framework.value if rule else "Unknown",
            "counterparty_id": violation.counterparty_id,
            "trade_id": violation.trade_id,
            "violation_type": violation.violation_type.value,
            "severity": violation.severity.value,
            "current_value": violation.current_value,
            "threshold_value": violation.threshold_value,
            "violation_amount": violation.violation_amount,
            "violation_percentage": violation.violation_percentage,
            "detected_at": violation.detected_at.isoformat(),
            "status": violation.status,
            "resolution_date": violation.resolution_date.isoformat() if violation.resolution_date else None,
            "resolution_notes": violation.resolution_notes
        }
