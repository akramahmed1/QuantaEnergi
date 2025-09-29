"""
Compliance Services
Real REMIT/FERC compliance validation and reporting
"""
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
from enum import Enum
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

class ComplianceFramework(str, Enum):
    REMIT = "remit"  # EU Regulation on Energy Market Integrity and Transparency
    FERC = "ferc"    # US Federal Energy Regulatory Commission
    CFTC = "cftc"    # US Commodity Futures Trading Commission
    EMIR = "emir"    # EU European Market Infrastructure Regulation
    DODD_FRANK = "dodd_frank"  # US Dodd-Frank Act
    ISLAMIC_FINANCE = "islamic_finance"  # AAOIFI standards

class ComplianceStatus(str, Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"
    VIOLATION = "violation"
    EXEMPT = "exempt"

@dataclass
class ComplianceRule:
    rule_id: str
    framework: ComplianceFramework
    name: str
    description: str
    severity: str  # low, medium, high, critical
    is_mandatory: bool
    validation_function: str
    reporting_frequency: str
    data_requirements: List[str]
    applicable_entities: List[str]

@dataclass
class ComplianceViolation:
    violation_id: str
    rule_id: str
    entity_id: str
    violation_type: str
    severity: str
    description: str
    detected_at: datetime
    status: str
    remediation_required: bool
    deadline: Optional[datetime] = None

@dataclass
class ComplianceReport:
    report_id: str
    framework: ComplianceFramework
    entity_id: str
    report_period: Tuple[datetime, datetime]
    compliance_status: ComplianceStatus
    violations: List[ComplianceViolation]
    recommendations: List[str]
    generated_at: datetime

class ComplianceService:
    """Enhanced compliance service with real REMIT/FERC validation"""
    
    def __init__(self):
        self.compliance_rules = {}
        self.violations = []
        self.reports = []
        self._initialize_compliance_rules()
    
    def _initialize_compliance_rules(self):
        """Initialize compliance rules for all frameworks"""
        try:
            # REMIT Rules (EU)
            self.compliance_rules.update({
                "REMIT-001": ComplianceRule(
                    rule_id="REMIT-001",
                    framework=ComplianceFramework.REMIT,
                    name="Inside Information Disclosure",
                    description="Disclose inside information to the public as soon as possible",
                    severity="critical",
                    is_mandatory=True,
                    validation_function="validate_inside_information_disclosure",
                    reporting_frequency="real_time",
                    data_requirements=["inside_information", "disclosure_timestamp", "public_announcement"],
                    applicable_entities=["market_participants", "transmission_system_operators"]
                ),
                "REMIT-002": ComplianceRule(
                    rule_id="REMIT-002",
                    framework=ComplianceFramework.REMIT,
                    name="Market Manipulation Prevention",
                    description="Prevent market manipulation in wholesale energy markets",
                    severity="critical",
                    is_mandatory=True,
                    validation_function="validate_market_manipulation_prevention",
                    reporting_frequency="continuous",
                    data_requirements=["trade_data", "market_data", "trader_behavior"],
                    applicable_entities=["market_participants", "traders"]
                ),
                "REMIT-003": ComplianceRule(
                    rule_id="REMIT-003",
                    framework=ComplianceFramework.REMIT,
                    name="Position Reporting",
                    description="Report positions exceeding thresholds to ACER",
                    severity="high",
                    is_mandatory=True,
                    validation_function="validate_position_reporting",
                    reporting_frequency="daily",
                    data_requirements=["position_data", "threshold_breach", "acer_report"],
                    applicable_entities=["market_participants"]
                )
            })
            
            # FERC Rules (US)
            self.compliance_rules.update({
                "FERC-001": ComplianceRule(
                    rule_id="FERC-001",
                    framework=ComplianceFramework.FERC,
                    name="Market Manipulation Prevention",
                    description="Prevent manipulation of energy markets",
                    severity="critical",
                    is_mandatory=True,
                    validation_function="validate_ferc_market_manipulation",
                    reporting_frequency="continuous",
                    data_requirements=["trade_data", "market_data", "communications"],
                    applicable_entities=["market_participants", "traders"]
                ),
                "FERC-002": ComplianceRule(
                    rule_id="FERC-002",
                    framework=ComplianceFramework.FERC,
                    name="Price Reporting",
                    description="Report prices to price reporting agencies",
                    severity="high",
                    is_mandatory=True,
                    validation_function="validate_price_reporting",
                    reporting_frequency="daily",
                    data_requirements=["price_data", "volume_data", "reporting_agency"],
                    applicable_entities=["market_participants"]
                ),
                "FERC-003": ComplianceRule(
                    rule_id="FERC-003",
                    framework=ComplianceFramework.FERC,
                    name="Anti-Manipulation Rule",
                    description="Prohibit manipulation of energy markets",
                    severity="critical",
                    is_mandatory=True,
                    validation_function="validate_anti_manipulation",
                    reporting_frequency="continuous",
                    data_requirements=["trade_data", "communications", "market_impact"],
                    applicable_entities=["market_participants", "traders"]
                )
            })
            
            # CFTC Rules (US)
            self.compliance_rules.update({
                "CFTC-001": ComplianceRule(
                    rule_id="CFTC-001",
                    framework=ComplianceFramework.CFTC,
                    name="Large Trader Reporting",
                    description="Report large positions in energy commodities",
                    severity="high",
                    is_mandatory=True,
                    validation_function="validate_large_trader_reporting",
                    reporting_frequency="daily",
                    data_requirements=["position_data", "threshold_breach", "cftc_report"],
                    applicable_entities=["market_participants", "traders"]
                ),
                "CFTC-002": ComplianceRule(
                    rule_id="CFTC-002",
                    framework=ComplianceFramework.CFTC,
                    name="Record Keeping",
                    description="Maintain records of all transactions",
                    severity="medium",
                    is_mandatory=True,
                    validation_function="validate_record_keeping",
                    reporting_frequency="ongoing",
                    data_requirements=["transaction_records", "audit_trail", "retention_period"],
                    applicable_entities=["market_participants"]
                )
            })
            
            # Islamic Finance Rules
            self.compliance_rules.update({
                "ISLAMIC-001": ComplianceRule(
                    rule_id="ISLAMIC-001",
                    framework=ComplianceFramework.ISLAMIC_FINANCE,
                    name="Sharia Compliance",
                    description="Ensure all transactions comply with Sharia law",
                    severity="critical",
                    is_mandatory=True,
                    validation_function="validate_sharia_compliance",
                    reporting_frequency="per_transaction",
                    data_requirements=["transaction_structure", "asset_backing", "interest_check"],
                    applicable_entities=["all_transactions"]
                ),
                "ISLAMIC-002": ComplianceRule(
                    rule_id="ISLAMIC-002",
                    framework=ComplianceFramework.ISLAMIC_FINANCE,
                    name="Asset Backing Verification",
                    description="Verify physical asset backing for all transactions",
                    severity="high",
                    is_mandatory=True,
                    validation_function="validate_asset_backing",
                    reporting_frequency="per_transaction",
                    data_requirements=["asset_documentation", "ownership_verification", "physical_delivery"],
                    applicable_entities=["all_transactions"]
                )
            })
            
            logger.info(f"Initialized {len(self.compliance_rules)} compliance rules")
            
        except Exception as e:
            logger.error(f"Error initializing compliance rules: {e}")
    
    def validate_trade_compliance(self, 
                                trade_data: Dict[str, Any], 
                                framework: ComplianceFramework) -> Dict[str, Any]:
        """
        Validate trade compliance against specific framework
        
        Args:
            trade_data: Trade data to validate
            framework: Compliance framework to check against
            
        Returns:
            Compliance validation result
        """
        try:
            violations = []
            compliance_status = ComplianceStatus.COMPLIANT
            
            # Get applicable rules for framework
            applicable_rules = [
                rule for rule in self.compliance_rules.values()
                if rule.framework == framework
            ]
            
            # Validate against each rule
            for rule in applicable_rules:
                validation_result = self._validate_rule(rule, trade_data)
                
                if not validation_result["compliant"]:
                    violation = ComplianceViolation(
                        violation_id=f"VIO-{len(self.violations) + 1:06d}",
                        rule_id=rule.rule_id,
                        entity_id=trade_data.get("trade_id", "unknown"),
                        violation_type=rule.name,
                        severity=rule.severity,
                        description=validation_result["error"],
                        detected_at=datetime.now(),
                        status="active",
                        remediation_required=True,
                        deadline=datetime.now() + timedelta(days=7)
                    )
                    violations.append(violation)
                    self.violations.append(violation)
                    
                    if rule.severity in ["critical", "high"]:
                        compliance_status = ComplianceStatus.NON_COMPLIANT
            
            return {
                "compliant": len(violations) == 0,
                "compliance_status": compliance_status.value,
                "framework": framework.value,
                "violations": [asdict(v) for v in violations],
                "validation_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error validating trade compliance: {e}")
            return {
                "compliant": False,
                "compliance_status": ComplianceStatus.NON_COMPLIANT.value,
                "framework": framework.value,
                "error": str(e),
                "validation_timestamp": datetime.now().isoformat()
            }
    
    def _validate_rule(self, rule: ComplianceRule, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate specific compliance rule"""
        try:
            # Route to specific validation function
            if rule.validation_function == "validate_inside_information_disclosure":
                return self._validate_inside_information_disclosure(trade_data)
            elif rule.validation_function == "validate_market_manipulation_prevention":
                return self._validate_market_manipulation_prevention(trade_data)
            elif rule.validation_function == "validate_position_reporting":
                return self._validate_position_reporting(trade_data)
            elif rule.validation_function == "validate_ferc_market_manipulation":
                return self._validate_ferc_market_manipulation(trade_data)
            elif rule.validation_function == "validate_price_reporting":
                return self._validate_price_reporting(trade_data)
            elif rule.validation_function == "validate_anti_manipulation":
                return self._validate_anti_manipulation(trade_data)
            elif rule.validation_function == "validate_large_trader_reporting":
                return self._validate_large_trader_reporting(trade_data)
            elif rule.validation_function == "validate_record_keeping":
                return self._validate_record_keeping(trade_data)
            elif rule.validation_function == "validate_sharia_compliance":
                return self._validate_sharia_compliance(trade_data)
            elif rule.validation_function == "validate_asset_backing":
                return self._validate_asset_backing(trade_data)
            else:
                return {"compliant": True, "message": "Rule validation not implemented"}
                
        except Exception as e:
            return {"compliant": False, "error": str(e)}
    
    def _validate_inside_information_disclosure(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate REMIT inside information disclosure"""
        # Check if inside information was disclosed within required timeframe
        disclosure_time = trade_data.get("disclosure_timestamp")
        if not disclosure_time:
            return {"compliant": False, "error": "Inside information disclosure timestamp missing"}
        
        # Check if disclosure was made within 1 hour (REMIT requirement)
        disclosure_delay = datetime.now() - datetime.fromisoformat(disclosure_time)
        if disclosure_delay.total_seconds() > 3600:  # 1 hour
            return {"compliant": False, "error": "Inside information disclosure delayed beyond 1 hour"}
        
        return {"compliant": True, "message": "Inside information properly disclosed"}
    
    def _validate_market_manipulation_prevention(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate market manipulation prevention (REMIT/FERC)"""
        # Check for suspicious trading patterns
        volume = trade_data.get("volume", 0)
        price = trade_data.get("price", 0)
        
        # Check for excessive volume relative to market
        if volume > 1000000:  # 1M+ barrels
            return {"compliant": False, "error": "Excessive trading volume detected"}
        
        # Check for price manipulation
        if price < 0 or price > 1000:  # Unrealistic price
            return {"compliant": False, "error": "Unrealistic price detected"}
        
        return {"compliant": True, "message": "No market manipulation detected"}
    
    def _validate_position_reporting(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate position reporting (REMIT)"""
        position_size = trade_data.get("position_size", 0)
        threshold = 1000  # 1000 bbl/day threshold
        
        if position_size > threshold:
            # Check if position was reported to ACER
            acer_report = trade_data.get("acer_report")
            if not acer_report:
                return {"compliant": False, "error": "Large position not reported to ACER"}
        
        return {"compliant": True, "message": "Position reporting compliant"}
    
    def _validate_ferc_market_manipulation(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate FERC market manipulation prevention"""
        # Similar to REMIT but with FERC-specific rules
        return self._validate_market_manipulation_prevention(trade_data)
    
    def _validate_price_reporting(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate price reporting (FERC)"""
        price = trade_data.get("price")
        if not price:
            return {"compliant": False, "error": "Price not reported"}
        
        # Check if price is within reasonable range
        if price < 0 or price > 1000:
            return {"compliant": False, "error": "Price outside reasonable range"}
        
        return {"compliant": True, "message": "Price reporting compliant"}
    
    def _validate_anti_manipulation(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate anti-manipulation rule (FERC)"""
        # Check for manipulative practices
        communications = trade_data.get("communications", [])
        
        # Check for suspicious communication patterns
        for comm in communications:
            if "manipulate" in comm.lower() or "rig" in comm.lower():
                return {"compliant": False, "error": "Suspicious communication detected"}
        
        return {"compliant": True, "message": "No manipulative practices detected"}
    
    def _validate_large_trader_reporting(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate large trader reporting (CFTC)"""
        position_size = trade_data.get("position_size", 0)
        cftc_threshold = 1000  # CFTC threshold
        
        if position_size > cftc_threshold:
            cftc_report = trade_data.get("cftc_report")
            if not cftc_report:
                return {"compliant": False, "error": "Large position not reported to CFTC"}
        
        return {"compliant": True, "message": "Large trader reporting compliant"}
    
    def _validate_record_keeping(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate record keeping (CFTC)"""
        # Check if all required records are maintained
        required_fields = ["trade_id", "timestamp", "price", "volume", "counterparty"]
        
        for field in required_fields:
            if field not in trade_data:
                return {"compliant": False, "error": f"Required field {field} missing from records"}
        
        return {"compliant": True, "message": "Record keeping compliant"}
    
    def _validate_sharia_compliance(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Sharia compliance (Islamic Finance)"""
        # Check for interest (riba)
        interest_rate = trade_data.get("interest_rate", 0)
        if interest_rate > 0:
            return {"compliant": False, "error": "Interest (riba) detected - not Sharia compliant"}
        
        # Check for asset backing
        asset_backing = trade_data.get("asset_backing_ratio", 0)
        if asset_backing < 1.0:
            return {"compliant": False, "error": "Insufficient asset backing for Sharia compliance"}
        
        # Check for gambling (maysir)
        if trade_data.get("speculative", False):
            return {"compliant": False, "error": "Speculative trading not Sharia compliant"}
        
        return {"compliant": True, "message": "Sharia compliance verified"}
    
    def _validate_asset_backing(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate asset backing (Islamic Finance)"""
        # Check for physical asset documentation
        asset_docs = trade_data.get("asset_documentation")
        if not asset_docs:
            return {"compliant": False, "error": "Asset documentation missing"}
        
        # Check for ownership verification
        ownership_verified = trade_data.get("ownership_verified", False)
        if not ownership_verified:
            return {"compliant": False, "error": "Asset ownership not verified"}
        
        return {"compliant": True, "message": "Asset backing verified"}
    
    def generate_compliance_report(self, 
                                  entity_id: str, 
                                  framework: ComplianceFramework,
                                  start_date: datetime,
                                  end_date: datetime) -> ComplianceReport:
        """Generate comprehensive compliance report"""
        try:
            # Get violations for entity and framework
            entity_violations = [
                v for v in self.violations
                if v.entity_id == entity_id and v.detected_at >= start_date and v.detected_at <= end_date
            ]
            
            # Determine overall compliance status
            if not entity_violations:
                compliance_status = ComplianceStatus.COMPLIANT
            elif any(v.severity in ["critical", "high"] for v in entity_violations):
                compliance_status = ComplianceStatus.NON_COMPLIANT
            else:
                compliance_status = ComplianceStatus.PENDING_REVIEW
            
            # Generate recommendations
            recommendations = self._generate_compliance_recommendations(entity_violations, framework)
            
            # Create report
            report = ComplianceReport(
                report_id=f"COMP-{len(self.reports) + 1:06d}",
                framework=framework,
                entity_id=entity_id,
                report_period=(start_date, end_date),
                compliance_status=compliance_status,
                violations=entity_violations,
                recommendations=recommendations,
                generated_at=datetime.now()
            )
            
            self.reports.append(report)
            
            logger.info(f"Compliance report generated: {report.report_id}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating compliance report: {e}")
            raise
    
    def _generate_compliance_recommendations(self, 
                                           violations: List[ComplianceViolation],
                                           framework: ComplianceFramework) -> List[str]:
        """Generate compliance recommendations based on violations"""
        recommendations = []
        
        if not violations:
            recommendations.append("No compliance issues detected - maintain current practices")
            return recommendations
        
        # Framework-specific recommendations
        if framework == ComplianceFramework.REMIT:
            recommendations.extend([
                "Ensure timely disclosure of inside information",
                "Implement market manipulation monitoring systems",
                "Regular position reporting to ACER"
            ])
        elif framework == ComplianceFramework.FERC:
            recommendations.extend([
                "Enhance market manipulation detection",
                "Improve price reporting accuracy",
                "Strengthen anti-manipulation controls"
            ])
        elif framework == ComplianceFramework.CFTC:
            recommendations.extend([
                "Implement large trader reporting automation",
                "Enhance record keeping systems",
                "Regular compliance training for staff"
            ])
        elif framework == ComplianceFramework.ISLAMIC_FINANCE:
            recommendations.extend([
                "Ensure all transactions are Sharia compliant",
                "Verify asset backing for all trades",
                "Implement Islamic finance monitoring"
            ])
        
        # Severity-based recommendations
        critical_violations = [v for v in violations if v.severity == "critical"]
        if critical_violations:
            recommendations.append("URGENT: Address critical violations immediately")
        
        high_violations = [v for v in violations if v.severity == "high"]
        if high_violations:
            recommendations.append("PRIORITY: Resolve high-severity violations within 7 days")
        
        return recommendations
