"""
Compliance Service for EnergyOpti-Pro.

Handles multi-region regulatory compliance, Islamic finance rules, and automated compliance checking.
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import structlog
from dataclasses import dataclass
from enum import Enum

logger = structlog.get_logger()

class ComplianceRegion(Enum):
    """Compliance region enumeration."""
    MIDDLE_EAST = "middle_east"
    UNITED_STATES = "united_states"
    UNITED_KINGDOM = "united_kingdom"
    EUROPEAN_UNION = "european_union"
    GUYANA = "guyana"

class ComplianceStatus(Enum):
    """Compliance status enumeration."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"
    EXEMPT = "exempt"

@dataclass
class ComplianceRule:
    """Compliance rule definition."""
    rule_id: str
    region: ComplianceRegion
    rule_type: str
    description: str
    requirements: List[str]
    severity: str  # low, medium, high, critical
    active: bool = True
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)

@dataclass
class ComplianceCheck:
    """Compliance check result."""
    rule_id: str
    status: ComplianceStatus
    details: str
    violations: List[str]
    recommendations: List[str]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)

class ComplianceService:
    """Multi-region compliance service with Islamic finance support."""
    
    def __init__(self):
        self.compliance_rules: Dict[str, ComplianceRule] = {}
        self.compliance_checks: List[ComplianceCheck] = []
        self.islamic_finance_rules: Dict[str, Any] = {}
        
        # Initialize compliance rules
        self._initialize_compliance_rules()
        self._initialize_islamic_finance_rules()
    
    def _initialize_compliance_rules(self):
        """Initialize compliance rules for all regions."""
        # Middle East Compliance Rules
        me_rules = [
            ComplianceRule(
                rule_id="ME_001",
                region=ComplianceRegion.MIDDLE_EAST,
                rule_type="ADNOC_Compliance",
                description="ADNOC trading and reporting requirements",
                requirements=["Daily position reporting", "Monthly compliance review", "ADNOC certification"],
                severity="high"
            ),
            ComplianceRule(
                rule_id="ME_002",
                region=ComplianceRegion.MIDDLE_EAST,
                rule_type="Saudi_Vision_2030",
                description="Saudi Vision 2030 energy sector compliance",
                requirements=["Local content requirements", "Technology transfer", "Saudi employment targets"],
                severity="high"
            ),
            ComplianceRule(
                rule_id="ME_003",
                region=ComplianceRegion.MIDDLE_EAST,
                rule_type="UAE_Energy_Law",
                description="UAE energy law compliance",
                requirements=["Energy efficiency standards", "Renewable energy targets", "Carbon reduction"],
                severity="medium"
            )
        ]
        
        # US Compliance Rules
        us_rules = [
            ComplianceRule(
                rule_id="US_001",
                region=ComplianceRegion.UNITED_STATES,
                rule_type="FERC_Compliance",
                description="Federal Energy Regulatory Commission compliance",
                requirements=["Market manipulation prevention", "Transparency reporting", "Fair access"],
                severity="critical"
            ),
            ComplianceRule(
                rule_id="US_002",
                region=ComplianceRegion.UNITED_STATES,
                rule_type="CFTC_Compliance",
                description="Commodity Futures Trading Commission compliance",
                requirements=["Position limits", "Reporting requirements", "Anti-fraud measures"],
                severity="critical"
            ),
            ComplianceRule(
                rule_id="US_003",
                region=ComplianceRegion.UNITED_STATES,
                rule_type="EPA_Compliance",
                description="Environmental Protection Agency compliance",
                requirements=["Emissions reporting", "Environmental impact assessment", "Clean energy standards"],
                severity="high"
            )
        ]
        
        # UK Compliance Rules
        uk_rules = [
            ComplianceRule(
                rule_id="UK_001",
                region=ComplianceRegion.UNITED_KINGDOM,
                rule_type="UK_ETS_Compliance",
                description="UK Emissions Trading Scheme compliance",
                requirements=["Carbon allowance management", "Emissions reporting", "Compliance verification"],
                severity="high"
            ),
            ComplianceRule(
                rule_id="UK_002",
                region=ComplianceRegion.UNITED_KINGDOM,
                rule_type="Ofgem_Compliance",
                description="Office of Gas and Electricity Markets compliance",
                requirements=["Market conduct rules", "Consumer protection", "Grid access"],
                severity="high"
            ),
            ComplianceRule(
                rule_id="UK_003",
                region=ComplianceRegion.UNITED_KINGDOM,
                rule_type="FCA_Compliance",
                description="Financial Conduct Authority compliance",
                requirements=["Financial services regulation", "Market abuse prevention", "Client money protection"],
                severity="critical"
            )
        ]
        
        # EU Compliance Rules
        eu_rules = [
            ComplianceRule(
                rule_id="EU_001",
                region=ComplianceRegion.EUROPEAN_UNION,
                rule_type="EU_ETS_Compliance",
                description="EU Emissions Trading Scheme compliance",
                requirements=["Carbon market participation", "Emissions monitoring", "Compliance reporting"],
                severity="high"
            ),
            ComplianceRule(
                rule_id="EU_002",
                region=ComplianceRegion.EUROPEAN_UNION,
                rule_type="REMIT_Compliance",
                description="Regulation on Energy Market Integrity and Transparency",
                requirements=["Market abuse prevention", "Inside information disclosure", "Transaction reporting"],
                severity="critical"
            ),
            ComplianceRule(
                rule_id="EU_003",
                region=ComplianceRegion.EUROPEAN_UNION,
                rule_type="MiFID_II_Compliance",
                description="Markets in Financial Instruments Directive II compliance",
                requirements=["Client categorization", "Best execution", "Transaction reporting"],
                severity="critical"
            ),
            ComplianceRule(
                rule_id="EU_004",
                region=ComplianceRegion.EUROPEAN_UNION,
                rule_type="GDPR_Compliance",
                description="General Data Protection Regulation compliance",
                requirements=["Data protection", "Privacy by design", "Data subject rights"],
                severity="high"
            )
        ]
        
        # Guyana Compliance Rules
        guyana_rules = [
            ComplianceRule(
                rule_id="GY_001",
                region=ComplianceRegion.GUYANA,
                rule_type="Local_Content_Compliance",
                description="Guyana local content requirements",
                requirements=["Local employment", "Local procurement", "Technology transfer"],
                severity="medium"
            ),
            ComplianceRule(
                rule_id="GY_002",
                region=ComplianceRegion.GUYANA,
                rule_type="Environmental_Protection",
                description="Environmental protection compliance",
                requirements=["Environmental impact assessment", "Biodiversity protection", "Waste management"],
                severity="high"
            ),
            ComplianceRule(
                rule_id="GY_003",
                region=ComplianceRegion.GUYANA,
                rule_type="Community_Development",
                description="Community development requirements",
                requirements=["Community consultation", "Infrastructure development", "Social programs"],
                severity="medium"
            )
        ]
        
        # Add all rules
        all_rules = me_rules + us_rules + uk_rules + eu_rules + guyana_rules
        for rule in all_rules:
            self.compliance_rules[rule.rule_id] = rule
    
    def _initialize_islamic_finance_rules(self):
        """Initialize Islamic finance compliance rules."""
        self.islamic_finance_rules = {
            "riba_prohibition": {
                "description": "Prohibition of interest (riba)",
                "requirements": [
                    "No interest-based transactions",
                    "Profit-sharing instead of fixed returns",
                    "Asset-backed financing"
                ],
                "severity": "critical"
            },
            "gharar_prohibition": {
                "description": "Prohibition of excessive uncertainty (gharar)",
                "requirements": [
                    "Clear contract terms",
                    "Transparent pricing",
                    "Avoidance of speculative contracts"
                ],
                "severity": "high"
            },
            "maysir_prohibition": {
                "description": "Prohibition of gambling (maysir)",
                "requirements": [
                    "No pure speculation",
                    "Real economic activity",
                    "Risk-sharing contracts"
                ],
                "severity": "high"
            },
            "halal_investment": {
                "description": "Halal investment screening",
                "requirements": [
                    "No alcohol, tobacco, gambling",
                    "No pork or non-halal food",
                    "No conventional banking"
                ],
                "severity": "medium"
            },
            "zakat_compliance": {
                "description": "Zakat calculation and distribution",
                "requirements": [
                    "Annual wealth assessment",
                    "2.5% calculation on eligible assets",
                    "Distribution to eligible recipients"
                ],
                "severity": "medium"
            }
        }
    
    async def check_compliance(
        self,
        user_id: str,
        region: ComplianceRegion,
        transaction_data: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check compliance for a specific transaction and region."""
        try:
            compliance_results = {
                "user_id": user_id,
                "region": region.value,
                "overall_status": ComplianceStatus.COMPLIANT,
                "rule_checks": [],
                "violations": [],
                "warnings": [],
                "timestamp": datetime.now().isoformat()
            }
            
            # Get applicable rules for the region
            applicable_rules = [
                rule for rule in self.compliance_rules.values()
                if rule.region == region and rule.active
            ]
            
            # Check each applicable rule
            for rule in applicable_rules:
                rule_check = await self._check_rule_compliance(rule, transaction_data, user_profile)
                compliance_results["rule_checks"].append(rule_check)
                
                if rule_check.status == ComplianceStatus.NON_COMPLIANT:
                    compliance_results["overall_status"] = ComplianceStatus.NON_COMPLIANT
                    compliance_results["violations"].append({
                        "rule_id": rule.rule_id,
                        "description": rule.description,
                        "severity": rule.severity,
                        "details": rule_check.details
                    })
                elif rule_check.status == ComplianceStatus.PENDING_REVIEW:
                    if compliance_results["overall_status"] == ComplianceStatus.COMPLIANT:
                        compliance_results["overall_status"] = ComplianceStatus.PENDING_REVIEW
                    compliance_results["warnings"].append({
                        "rule_id": rule.rule_id,
                        "description": rule.description,
                        "severity": rule.severity,
                        "details": rule_check.details
                    })
            
            # Check Islamic finance compliance if applicable
            if user_profile.get("islamic_finance_enabled", False):
                islamic_compliance = await self._check_islamic_finance_compliance(transaction_data)
                compliance_results["islamic_finance_compliance"] = islamic_compliance
                
                if islamic_compliance["overall_status"] == ComplianceStatus.NON_COMPLIANT:
                    compliance_results["overall_status"] = ComplianceStatus.NON_COMPLIANT
                    compliance_results["violations"].extend(islamic_compliance["violations"])
            
            # Store compliance check
            self.compliance_checks.append(ComplianceCheck(
                rule_id="comprehensive_check",
                status=compliance_results["overall_status"],
                details=f"Comprehensive compliance check for {region.value}",
                violations=[v["description"] for v in compliance_results["violations"]],
                recommendations=self._generate_compliance_recommendations(compliance_results)
            ))
            
            return compliance_results
            
        except Exception as e:
            logger.error(f"Failed to check compliance: {e}")
            raise
    
    async def _check_rule_compliance(
        self,
        rule: ComplianceRule,
        transaction_data: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> ComplianceCheck:
        """Check compliance for a specific rule."""
        try:
            # This is a simplified compliance check
            # In real implementation, this would involve complex rule evaluation
            
            violations = []
            status = ComplianceStatus.COMPLIANT
            
            # Example compliance checks based on rule type
            if "ADNOC" in rule.rule_type:
                # Check ADNOC-specific requirements
                if not transaction_data.get("adnoc_certification"):
                    violations.append("Missing ADNOC certification")
                    status = ComplianceStatus.NON_COMPLIANT
            
            elif "FERC" in rule.rule_type:
                # Check FERC compliance
                if transaction_data.get("market_manipulation_risk", 0) > 0.7:
                    violations.append("High market manipulation risk detected")
                    status = ComplianceStatus.NON_COMPLIANT
            
            elif "GDPR" in rule.rule_type:
                # Check GDPR compliance
                if not transaction_data.get("data_consent"):
                    violations.append("Missing data consent")
                    status = ComplianceStatus.NON_COMPLIANT
            
            # Generate recommendations
            recommendations = self._generate_rule_recommendations(rule, violations)
            
            return ComplianceCheck(
                rule_id=rule.rule_id,
                status=status,
                details=f"Compliance check for {rule.description}",
                violations=violations,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Failed to check rule compliance: {e}")
            return ComplianceCheck(
                rule_id=rule.rule_id,
                status=ComplianceStatus.PENDING_REVIEW,
                details=f"Error checking compliance: {e}",
                violations=[],
                recommendations=["Review compliance check implementation"]
            )
    
    async def _check_islamic_finance_compliance(
        self,
        transaction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check Islamic finance compliance."""
        try:
            islamic_compliance = {
                "overall_status": ComplianceStatus.COMPLIANT,
                "rule_checks": [],
                "violations": [],
                "warnings": [],
                "timestamp": datetime.now().isoformat()
            }
            
            # Check each Islamic finance rule
            for rule_name, rule_details in self.islamic_finance_rules.items():
                rule_check = await self._check_islamic_rule(rule_name, rule_details, transaction_data)
                islamic_compliance["rule_checks"].append(rule_check)
                
                if rule_check.status == ComplianceStatus.NON_COMPLIANT:
                    islamic_compliance["overall_status"] = ComplianceStatus.NON_COMPLIANT
                    islamic_compliance["violations"].append({
                        "rule": rule_name,
                        "description": rule_details["description"],
                        "severity": rule_details["severity"],
                        "details": rule_check.details
                    })
            
            return islamic_compliance
            
        except Exception as e:
            logger.error(f"Failed to check Islamic finance compliance: {e}")
            raise
    
    async def _check_islamic_rule(
        self,
        rule_name: str,
        rule_details: Dict[str, Any],
        transaction_data: Dict[str, Any]
    ) -> ComplianceCheck:
        """Check compliance for a specific Islamic finance rule."""
        try:
            violations = []
            status = ComplianceStatus.COMPLIANT
            details = f"Islamic finance rule check for {rule_details['description']}"
            
            if rule_name == "riba_prohibition":
                # Check for interest-based transactions
                if transaction_data.get("interest_rate", 0) > 0:
                    violations.append("Interest-based transaction detected")
                    status = ComplianceStatus.NON_COMPLIANT
            
            elif rule_name == "gharar_prohibition":
                # Check for excessive uncertainty
                if transaction_data.get("uncertainty_level", 0) > 0.8:
                    violations.append("Excessive uncertainty in contract terms")
                    status = ComplianceStatus.NON_COMPLIANT
            
            elif rule_name == "maysir_prohibition":
                # Check for gambling-like behavior
                if transaction_data.get("speculation_level", 0) > 0.9:
                    violations.append("Pure speculation detected")
                    status = ComplianceStatus.NON_COMPLIANT
            
            elif rule_name == "halal_investment":
                # Check for non-halal investments
                if transaction_data.get("investment_type") in ["alcohol", "tobacco", "gambling"]:
                    violations.append("Non-halal investment detected")
                    status = ComplianceStatus.NON_COMPLIANT
            
            elif rule_name == "zakat_compliance":
                # Check zakat calculation
                if transaction_data.get("zakat_calculated", False) == False:
                    violations.append("Zakat calculation required")
                    status = ComplianceStatus.PENDING_REVIEW
            
            recommendations = self._generate_islamic_rule_recommendations(rule_name, violations)
            
            return ComplianceCheck(
                rule_id=f"islamic_{rule_name}",
                status=status,
                details=details,
                violations=violations,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Failed to check Islamic rule {rule_name}: {e}")
            return ComplianceCheck(
                rule_id=f"islamic_{rule_name}",
                status=ComplianceStatus.PENDING_REVIEW,
                details=f"Error checking Islamic rule: {e}",
                violations=[],
                recommendations=["Review Islamic rule implementation"]
            )
    
    def _generate_compliance_recommendations(self, compliance_results: Dict[str, Any]) -> List[str]:
        """Generate compliance recommendations based on check results."""
        recommendations = []
        
        for violation in compliance_results.get("violations", []):
            if "ADNOC" in violation.get("description", ""):
                recommendations.append("Obtain ADNOC certification before trading")
            elif "FERC" in violation.get("description", ""):
                recommendations.append("Implement market manipulation prevention measures")
            elif "GDPR" in violation.get("description", ""):
                recommendations.append("Ensure proper data consent and privacy measures")
            else:
                recommendations.append(f"Review and address {violation.get('description', 'compliance issue')}")
        
        if not recommendations:
            recommendations.append("All compliance requirements met")
        
        return recommendations
    
    def _generate_rule_recommendations(self, rule: ComplianceRule, violations: List[str]) -> List[str]:
        """Generate recommendations for a specific rule."""
        recommendations = []
        
        if not violations:
            recommendations.append(f"Compliant with {rule.description}")
        else:
            for violation in violations:
                recommendations.append(f"Address: {violation}")
        
        return recommendations
    
    def _generate_islamic_rule_recommendations(self, rule_name: str, violations: List[str]) -> List[str]:
        """Generate recommendations for Islamic finance rules."""
        recommendations = []
        
        if rule_name == "riba_prohibition" and violations:
            recommendations.append("Use profit-sharing contracts instead of interest-based financing")
        elif rule_name == "gharar_prohibition" and violations:
            recommendations.append("Ensure clear contract terms and transparent pricing")
        elif rule_name == "maysir_prohibition" and violations:
            recommendations.append("Focus on real economic activity rather than speculation")
        elif rule_name == "halal_investment" and violations:
            recommendations.append("Screen investments for halal compliance")
        elif rule_name == "zakat_compliance" and violations:
            recommendations.append("Implement annual zakat calculation and distribution")
        
        if not violations:
            recommendations.append("Islamic finance requirements met")
        
        return recommendations
    
    async def get_compliance_history(
        self,
        user_id: Optional[str] = None,
        region: Optional[ComplianceRegion] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[ComplianceCheck]:
        """Get compliance check history with optional filtering."""
        try:
            filtered_checks = self.compliance_checks
            
            if user_id:
                # Filter by user (in real implementation, this would be stored per user)
                pass
            
            if region:
                # Filter by region
                filtered_checks = [
                    check for check in filtered_checks
                    if any(rule.region == region for rule in self.compliance_rules.values() if rule.rule_id == check.rule_id)
                ]
            
            if start_date:
                filtered_checks = [
                    check for check in filtered_checks
                    if check.timestamp >= start_date
                ]
            
            if end_date:
                filtered_checks = [
                    check for check in filtered_checks
                    if check.timestamp <= end_date
                ]
            
            return sorted(filtered_checks, key=lambda x: x.timestamp, reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to get compliance history: {e}")
            raise
    
    async def generate_compliance_report(
        self,
        user_id: str,
        region: ComplianceRegion,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Generate comprehensive compliance report for a user and region."""
        try:
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=period_days)
            
            # Get compliance history
            compliance_history = await self.get_compliance_history(
                user_id=user_id,
                region=region,
                start_date=start_date,
                end_date=end_date
            )
            
            # Calculate compliance statistics
            total_checks = len(compliance_history)
            compliant_checks = len([c for c in compliance_history if c.status == ComplianceStatus.COMPLIANT])
            non_compliant_checks = len([c for c in compliance_history if c.status == ComplianceStatus.NON_COMPLIANT])
            pending_checks = len([c for c in compliance_history if c.status == ComplianceStatus.PENDING_REVIEW])
            
            compliance_rate = (compliant_checks / total_checks * 100) if total_checks > 0 else 0
            
            return {
                "user_id": user_id,
                "region": region.value,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": period_days
                },
                "statistics": {
                    "total_checks": total_checks,
                    "compliant_checks": compliant_checks,
                    "non_compliant_checks": non_compliant_checks,
                    "pending_checks": pending_checks,
                    "compliance_rate": round(compliance_rate, 2)
                },
                "compliance_history": compliance_history,
                "recommendations": self._generate_report_recommendations(compliance_history),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate compliance report: {e}")
            raise
    
    def _generate_report_recommendations(self, compliance_history: List[ComplianceCheck]) -> List[str]:
        """Generate recommendations based on compliance history."""
        recommendations = []
        
        # Analyze compliance patterns
        non_compliant_rules = {}
        for check in compliance_history:
            if check.status == ComplianceStatus.NON_COMPLIANT:
                rule_id = check.rule_id
                if rule_id not in non_compliant_rules:
                    non_compliant_rules[rule_id] = 0
                non_compliant_rules[rule_id] += 1
        
        # Generate specific recommendations
        for rule_id, count in non_compliant_rules.items():
            if count > 3:
                recommendations.append(f"Frequent non-compliance with {rule_id}, consider additional training")
            elif count > 1:
                recommendations.append(f"Review compliance with {rule_id}")
        
        if not recommendations:
            recommendations.append("Good compliance record maintained")
        
        return recommendations 