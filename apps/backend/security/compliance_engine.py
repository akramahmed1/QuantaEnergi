"""
Compliance Engine for Multi-Regional Regulatory Requirements
Automatically configures compliance rules for different regions and generates regulatory reports
"""

from typing import Dict, List, Any, Optional, Union
from enum import Enum
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict
import json
import xml.etree.ElementTree as ET
import csv
import io

import structlog

logger = structlog.get_logger(__name__)


class ComplianceRegion(str, Enum):
    """Supported compliance regions"""
    US = "us"
    UK = "uk"
    EU = "eu"
    MIDDLE_EAST = "middle_east"
    GUYANA = "guyana"
    GLOBAL = "global"


class RegulatoryFramework(str, Enum):
    """Regulatory frameworks per region"""
    # US Regulations
    CFTC = "cftc"  # Commodity Futures Trading Commission
    FERC = "ferc"  # Federal Energy Regulatory Commission
    NERC = "nerc"  # North American Electric Reliability Corporation
    SEC = "sec"    # Securities and Exchange Commission
    
    # EU/UK Regulations
    EMIR = "emir"  # European Market Infrastructure Regulation
    REMIT = "remit"  # Regulation on Energy Market Integrity and Transparency
    ACER = "acer"  # Agency for the Cooperation of Energy Regulators
    GDPR = "gdpr"  # General Data Protection Regulation
    PSD2 = "psd2"  # Payment Services Directive 2
    
    # Middle East
    DFSA = "dfsa"  # Dubai Financial Services Authority
    SAMA = "sama"  # Saudi Arabian Monetary Authority
    CBUAE = "cbua"  # Central Bank of UAE
    
    # Guyana
    EPA = "epa"    # Environmental Protection Agency
    BANK_OF_GUYANA = "bog"  # Bank of Guyana
    PETROLEUM_COMMISSION = "pc"  # Petroleum Commission


@dataclass
class ComplianceRule:
    """Individual compliance rule definition"""
    rule_id: str
    name: str
    description: str
    region: ComplianceRegion
    framework: RegulatoryFramework
    severity: str  # critical, high, medium, low
    is_mandatory: bool
    validation_function: str
    reporting_frequency: str  # daily, weekly, monthly, quarterly, annually
    data_requirements: List[str]
    applicable_entities: List[str]  # trades, portfolios, users, etc.


@dataclass
class ComplianceReport:
    """Compliance report structure"""
    report_id: str
    report_type: str
    region: ComplianceRegion
    framework: RegulatoryFramework
    period_start: datetime
    period_end: datetime
    generated_at: datetime
    generated_by: str
    status: str  # draft, submitted, approved, rejected
    data: Dict[str, Any]
    violations: List[Dict[str, Any]]
    recommendations: List[str]


class ComplianceEngine:
    """Main compliance engine for regulatory requirements"""
    
    def __init__(self):
        """Initialize compliance engine with regional rules"""
        self.rules = self._load_compliance_rules()
        self.report_templates = self._load_report_templates()
        logger.info("Compliance engine initialized", 
                   rules_count=len(self.rules),
                   regions=list(set(rule.region for rule in self.rules)))
    
    def _load_compliance_rules(self) -> List[ComplianceRule]:
        """Load compliance rules for all regions"""
        rules = []
        
        # US Compliance Rules
        rules.extend([
            ComplianceRule(
                rule_id="CFTC-001",
                name="Large Trader Reporting",
                description="Report large positions in energy commodities",
                region=ComplianceRegion.US,
                framework=RegulatoryFramework.CFTC,
                severity="critical",
                is_mandatory=True,
                validation_function="validate_large_trader_positions",
                reporting_frequency="daily",
                data_requirements=["position_data", "trader_info", "commodity_data"],
                applicable_entities=["trades", "positions"]
            ),
            ComplianceRule(
                rule_id="FERC-001",
                name="Market Manipulation Prevention",
                description="Prevent market manipulation in energy markets",
                region=ComplianceRegion.US,
                framework=RegulatoryFramework.FERC,
                severity="critical",
                is_mandatory=True,
                validation_function="validate_market_manipulation",
                reporting_frequency="real_time",
                data_requirements=["trade_data", "market_data", "trader_behavior"],
                applicable_entities=["trades", "market_data"]
            ),
            ComplianceRule(
                rule_id="NERC-001",
                name="Critical Infrastructure Protection",
                description="Protect critical energy infrastructure",
                region=ComplianceRegion.US,
                framework=RegulatoryFramework.NERC,
                severity="high",
                is_mandatory=True,
                validation_function="validate_critical_infrastructure",
                reporting_frequency="quarterly",
                data_requirements=["infrastructure_data", "security_measures"],
                applicable_entities=["infrastructure", "security"]
            )
        ])
        
        # EU Compliance Rules
        rules.extend([
            ComplianceRule(
                rule_id="EMIR-001",
                name="Trade Repository Reporting",
                description="Report all derivatives trades to trade repository",
                region=ComplianceRegion.EU,
                framework=RegulatoryFramework.EMIR,
                severity="critical",
                is_mandatory=True,
                validation_function="validate_emir_reporting",
                reporting_frequency="daily",
                data_requirements=["trade_data", "counterparty_data", "collateral_data"],
                applicable_entities=["trades", "counterparties"]
            ),
            ComplianceRule(
                rule_id="REMIT-001",
                name="Inside Information Disclosure",
                description="Disclose inside information in energy markets",
                region=ComplianceRegion.EU,
                framework=RegulatoryFramework.REMIT,
                severity="high",
                is_mandatory=True,
                validation_function="validate_inside_information",
                reporting_frequency="real_time",
                data_requirements=["inside_information", "disclosure_records"],
                applicable_entities=["market_data", "disclosures"]
            ),
            ComplianceRule(
                rule_id="GDPR-001",
                name="Data Protection Compliance",
                description="Ensure GDPR compliance for personal data",
                region=ComplianceRegion.EU,
                framework=RegulatoryFramework.GDPR,
                severity="high",
                is_mandatory=True,
                validation_function="validate_gdpr_compliance",
                reporting_frequency="monthly",
                data_requirements=["personal_data", "consent_records", "data_processing"],
                applicable_entities=["users", "personal_data"]
            )
        ])
        
        # UK Compliance Rules
        rules.extend([
            ComplianceRule(
                rule_id="UK-EMIR-001",
                name="UK EMIR Reporting",
                description="UK specific EMIR reporting requirements",
                region=ComplianceRegion.UK,
                framework=RegulatoryFramework.EMIR,
                severity="critical",
                is_mandatory=True,
                validation_function="validate_uk_emir_reporting",
                reporting_frequency="daily",
                data_requirements=["trade_data", "uk_specific_fields"],
                applicable_entities=["trades"]
            )
        ])
        
        # Middle East Compliance Rules
        rules.extend([
            ComplianceRule(
                rule_id="DFSA-001",
                name="Islamic Finance Compliance",
                description="Ensure Sharia compliance for Islamic finance",
                region=ComplianceRegion.MIDDLE_EAST,
                framework=RegulatoryFramework.DFSA,
                severity="critical",
                is_mandatory=True,
                validation_function="validate_sharia_compliance",
                reporting_frequency="monthly",
                data_requirements=["sharia_compliance_data", "halal_assets"],
                applicable_entities=["trades", "products"]
            ),
            ComplianceRule(
                rule_id="SAMA-001",
                name="Saudi Financial Regulations",
                description="Compliance with Saudi financial regulations",
                region=ComplianceRegion.MIDDLE_EAST,
                framework=RegulatoryFramework.SAMA,
                severity="high",
                is_mandatory=True,
                validation_function="validate_sama_compliance",
                reporting_frequency="quarterly",
                data_requirements=["financial_data", "regulatory_capital"],
                applicable_entities=["financial_data"]
            )
        ])
        
        # Guyana Compliance Rules
        rules.extend([
            ComplianceRule(
                rule_id="EPA-001",
                name="Environmental Impact Assessment",
                description="Assess environmental impact of energy operations",
                region=ComplianceRegion.GUYANA,
                framework=RegulatoryFramework.EPA,
                severity="medium",
                is_mandatory=True,
                validation_function="validate_environmental_impact",
                reporting_frequency="annually",
                data_requirements=["environmental_data", "impact_assessments"],
                applicable_entities=["operations", "environmental"]
            ),
            ComplianceRule(
                rule_id="BOG-001",
                name="Bank of Guyana Reporting",
                description="Financial reporting to Bank of Guyana",
                region=ComplianceRegion.GUYANA,
                framework=RegulatoryFramework.BANK_OF_GUYANA,
                severity="high",
                is_mandatory=True,
                validation_function="validate_bog_reporting",
                reporting_frequency="monthly",
                data_requirements=["financial_data", "gyd_currency_data"],
                applicable_entities=["financial_data", "currency"]
            )
        ])
        
        return rules
    
    def _load_report_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load report templates for different regulatory frameworks"""
        return {
            "CFTC": {
                "format": "XML",
                "template": "cftc_large_trader_report.xml",
                "fields": ["trader_id", "commodity", "position_size", "reporting_date"],
                "validation_rules": ["position_threshold", "data_completeness"]
            },
            "EMIR": {
                "format": "XML",
                "template": "emir_trade_report.xml",
                "fields": ["trade_id", "counterparty", "product_type", "notional_amount"],
                "validation_rules": ["mandatory_fields", "data_accuracy"]
            },
            "GDPR": {
                "format": "JSON",
                "template": "gdpr_data_protection_report.json",
                "fields": ["data_subject", "data_type", "processing_purpose", "consent_status"],
                "validation_rules": ["consent_validity", "data_minimization"]
            },
            "DFSA": {
                "format": "XML",
                "template": "dfsa_islamic_finance_report.xml",
                "fields": ["sharia_compliance", "halal_assets", "prohibited_activities"],
                "validation_rules": ["sharia_approval", "asset_verification"]
            },
            "EPA": {
                "format": "CSV",
                "template": "epa_environmental_report.csv",
                "fields": ["operation_type", "environmental_impact", "mitigation_measures"],
                "validation_rules": ["impact_assessment", "mitigation_adequacy"]
            }
        }
    
    def get_compliance_rules_for_region(self, region: ComplianceRegion) -> List[ComplianceRule]:
        """
        Get compliance rules for specific region
        
        Args:
            region: Compliance region
            
        Returns:
            List of applicable compliance rules
        """
        return [rule for rule in self.rules if rule.region == region]
    
    def get_compliance_rules_for_framework(self, framework: RegulatoryFramework) -> List[ComplianceRule]:
        """
        Get compliance rules for specific regulatory framework
        
        Args:
            framework: Regulatory framework
            
        Returns:
            List of applicable compliance rules
        """
        return [rule for rule in self.rules if rule.framework == framework]
    
    async def validate_compliance(self, 
                                region: ComplianceRegion,
                                entity_type: str,
                                entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate compliance for specific entity and region
        
        Args:
            region: Compliance region
            entity_type: Type of entity (trades, portfolios, users, etc.)
            entity_data: Entity data to validate
            
        Returns:
            Validation results
        """
        try:
            applicable_rules = [
                rule for rule in self.rules 
                if rule.region == region and entity_type in rule.applicable_entities
            ]
            
            validation_results = {
                "entity_type": entity_type,
                "region": region.value,
                "validation_timestamp": datetime.now(timezone.utc).isoformat(),
                "rules_applied": len(applicable_rules),
                "violations": [],
                "warnings": [],
                "compliant": True
            }
            
            for rule in applicable_rules:
                try:
                    # Execute validation function
                    validation_result = await self._execute_validation_function(
                        rule.validation_function, entity_data, rule
                    )
                    
                    if not validation_result["compliant"]:
                        validation_results["violations"].append({
                            "rule_id": rule.rule_id,
                            "rule_name": rule.name,
                            "severity": rule.severity,
                            "description": rule.description,
                            "details": validation_result["details"]
                        })
                        
                        if rule.severity in ["critical", "high"]:
                            validation_results["compliant"] = False
                    
                    if validation_result.get("warnings"):
                        validation_results["warnings"].extend(validation_result["warnings"])
                        
                except Exception as e:
                    logger.error("Validation function failed", 
                               rule_id=rule.rule_id, 
                               error=str(e))
                    validation_results["violations"].append({
                        "rule_id": rule.rule_id,
                        "rule_name": rule.name,
                        "severity": "high",
                        "description": f"Validation function error: {str(e)}",
                        "details": {}
                    })
                    validation_results["compliant"] = False
            
            return validation_results
            
        except Exception as e:
            logger.error("Compliance validation failed", 
                        region=region.value, 
                        entity_type=entity_type, 
                        error=str(e))
            return {
                "entity_type": entity_type,
                "region": region.value,
                "validation_timestamp": datetime.now(timezone.utc).isoformat(),
                "rules_applied": 0,
                "violations": [{"error": str(e)}],
                "warnings": [],
                "compliant": False
            }
    
    async def _execute_validation_function(self, 
                                         function_name: str, 
                                         entity_data: Dict[str, Any],
                                         rule: ComplianceRule) -> Dict[str, Any]:
        """Execute specific validation function"""
        
        # Map validation functions to actual implementations
        validation_functions = {
            "validate_large_trader_positions": self._validate_large_trader_positions,
            "validate_market_manipulation": self._validate_market_manipulation,
            "validate_critical_infrastructure": self._validate_critical_infrastructure,
            "validate_emir_reporting": self._validate_emir_reporting,
            "validate_inside_information": self._validate_inside_information,
            "validate_gdpr_compliance": self._validate_gdpr_compliance,
            "validate_uk_emir_reporting": self._validate_uk_emir_reporting,
            "validate_sharia_compliance": self._validate_sharia_compliance,
            "validate_sama_compliance": self._validate_sama_compliance,
            "validate_environmental_impact": self._validate_environmental_impact,
            "validate_bog_reporting": self._validate_bog_reporting
        }
        
        validation_func = validation_functions.get(function_name)
        if not validation_func:
            raise ValueError(f"Unknown validation function: {function_name}")
        
        return await validation_func(entity_data, rule)
    
    # Validation function implementations
    async def _validate_large_trader_positions(self, data: Dict[str, Any], rule: ComplianceRule) -> Dict[str, Any]:
        """Validate large trader position reporting requirements"""
        position_size = data.get("position_size", 0)
        threshold = 1000000  # $1M threshold
        
        if position_size > threshold:
            return {
                "compliant": True,
                "details": {"position_size": position_size, "threshold": threshold},
                "warnings": [f"Large position detected: ${position_size:,.2f}"]
            }
        
        return {"compliant": True, "details": {"position_size": position_size}}
    
    async def _validate_market_manipulation(self, data: Dict[str, Any], rule: ComplianceRule) -> Dict[str, Any]:
        """Validate market manipulation prevention"""
        # Check for suspicious trading patterns
        trade_volume = data.get("volume", 0)
        price_impact = data.get("price_impact", 0)
        
        if trade_volume > 1000000 and price_impact > 0.05:  # 5% price impact
            return {
                "compliant": False,
                "details": {
                    "trade_volume": trade_volume,
                    "price_impact": price_impact,
                    "risk_level": "high"
                }
            }
        
        return {"compliant": True, "details": {"trade_volume": trade_volume}}
    
    async def _validate_critical_infrastructure(self, data: Dict[str, Any], rule: ComplianceRule) -> Dict[str, Any]:
        """Validate critical infrastructure protection"""
        security_measures = data.get("security_measures", [])
        required_measures = ["encryption", "access_control", "audit_logging"]
        
        missing_measures = [measure for measure in required_measures if measure not in security_measures]
        
        if missing_measures:
            return {
                "compliant": False,
                "details": {"missing_security_measures": missing_measures}
            }
        
        return {"compliant": True, "details": {"security_measures": security_measures}}
    
    async def _validate_emir_reporting(self, data: Dict[str, Any], rule: ComplianceRule) -> Dict[str, Any]:
        """Validate EMIR reporting requirements"""
        required_fields = ["trade_id", "counterparty", "product_type", "notional_amount"]
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return {
                "compliant": False,
                "details": {"missing_fields": missing_fields}
            }
        
        return {"compliant": True, "details": {"fields_present": required_fields}}
    
    async def _validate_inside_information(self, data: Dict[str, Any], rule: ComplianceRule) -> Dict[str, Any]:
        """Validate inside information disclosure"""
        inside_info = data.get("inside_information", False)
        disclosure_time = data.get("disclosure_time")
        
        if inside_info and not disclosure_time:
            return {
                "compliant": False,
                "details": {"inside_information_detected": True, "disclosure_missing": True}
            }
        
        return {"compliant": True, "details": {"inside_information": inside_info}}
    
    async def _validate_gdpr_compliance(self, data: Dict[str, Any], rule: ComplianceRule) -> Dict[str, Any]:
        """Validate GDPR compliance"""
        personal_data = data.get("personal_data", False)
        consent_given = data.get("consent_given", False)
        
        if personal_data and not consent_given:
            return {
                "compliant": False,
                "details": {"personal_data_detected": True, "consent_missing": True}
            }
        
        return {"compliant": True, "details": {"personal_data": personal_data, "consent": consent_given}}
    
    async def _validate_uk_emir_reporting(self, data: Dict[str, Any], rule: ComplianceRule) -> Dict[str, Any]:
        """Validate UK EMIR reporting requirements"""
        # Similar to EMIR but with UK-specific fields
        uk_fields = ["uk_entity_id", "uk_reporting_obligation"]
        missing_uk_fields = [field for field in uk_fields if not data.get(field)]
        
        if missing_uk_fields:
            return {
                "compliant": False,
                "details": {"missing_uk_fields": missing_uk_fields}
            }
        
        return {"compliant": True, "details": {"uk_fields_present": uk_fields}}
    
    async def _validate_sharia_compliance(self, data: Dict[str, Any], rule: ComplianceRule) -> Dict[str, Any]:
        """Validate Sharia compliance for Islamic finance"""
        is_sharia_compliant = data.get("is_sharia_compliant", False)
        halal_assets = data.get("halal_assets", True)
        prohibited_activities = data.get("prohibited_activities", [])
        
        if not is_sharia_compliant or not halal_assets or prohibited_activities:
            return {
                "compliant": False,
                "details": {
                    "sharia_compliant": is_sharia_compliant,
                    "halal_assets": halal_assets,
                    "prohibited_activities": prohibited_activities
                }
            }
        
        return {"compliant": True, "details": {"sharia_compliant": True}}
    
    async def _validate_sama_compliance(self, data: Dict[str, Any], rule: ComplianceRule) -> Dict[str, Any]:
        """Validate SAMA compliance"""
        regulatory_capital = data.get("regulatory_capital", 0)
        minimum_capital = 10000000  # SAR 10M minimum
        
        if regulatory_capital < minimum_capital:
            return {
                "compliant": False,
                "details": {
                    "regulatory_capital": regulatory_capital,
                    "minimum_required": minimum_capital
                }
            }
        
        return {"compliant": True, "details": {"regulatory_capital": regulatory_capital}}
    
    async def _validate_environmental_impact(self, data: Dict[str, Any], rule: ComplianceRule) -> Dict[str, Any]:
        """Validate environmental impact assessment"""
        environmental_impact = data.get("environmental_impact", 0)
        impact_threshold = 100  # Impact score threshold
        
        if environmental_impact > impact_threshold:
            return {
                "compliant": False,
                "details": {
                    "environmental_impact": environmental_impact,
                    "threshold": impact_threshold
                }
            }
        
        return {"compliant": True, "details": {"environmental_impact": environmental_impact}}
    
    async def _validate_bog_reporting(self, data: Dict[str, Any], rule: ComplianceRule) -> Dict[str, Any]:
        """Validate Bank of Guyana reporting"""
        financial_data = data.get("financial_data", {})
        required_fields = ["total_assets", "total_liabilities", "capital_adequacy"]
        missing_fields = [field for field in required_fields if not financial_data.get(field)]
        
        if missing_fields:
            return {
                "compliant": False,
                "details": {"missing_financial_fields": missing_fields}
            }
        
        return {"compliant": True, "details": {"financial_fields_present": required_fields}}
    
    async def generate_compliance_report(self,
                                       region: ComplianceRegion,
                                       framework: RegulatoryFramework,
                                       period_start: datetime,
                                       period_end: datetime,
                                       data: Dict[str, Any]) -> ComplianceReport:
        """
        Generate compliance report for specific region and framework
        
        Args:
            region: Compliance region
            framework: Regulatory framework
            period_start: Report period start
            period_end: Report period end
            data: Report data
            
        Returns:
            Generated compliance report
        """
        try:
            report_id = f"{framework.value}_{region.value}_{period_start.strftime('%Y%m%d')}"
            
            # Get applicable rules
            applicable_rules = self.get_compliance_rules_for_framework(framework)
            
            # Validate compliance for the period
            violations = []
            for rule in applicable_rules:
                validation_result = await self.validate_compliance(
                    region, "trades", data
                )
                if not validation_result["compliant"]:
                    violations.extend(validation_result["violations"])
            
            # Generate report based on template
            template = self.report_templates.get(framework.value, {})
            report_format = template.get("format", "JSON")
            
            if report_format == "XML":
                report_data = self._generate_xml_report(data, template, violations)
            elif report_format == "CSV":
                report_data = self._generate_csv_report(data, template, violations)
            else:
                report_data = self._generate_json_report(data, template, violations)
            
            report = ComplianceReport(
                report_id=report_id,
                report_type=f"{framework.value}_REPORT",
                region=region,
                framework=framework,
                period_start=period_start,
                period_end=period_end,
                generated_at=datetime.now(timezone.utc),
                generated_by="system",
                status="draft",
                data=report_data,
                violations=violations,
                recommendations=self._generate_recommendations(violations)
            )
            
            logger.info("Compliance report generated", 
                       report_id=report_id, 
                       region=region.value, 
                       framework=framework.value)
            
            return report
            
        except Exception as e:
            logger.error("Failed to generate compliance report", 
                        region=region.value, 
                        framework=framework.value, 
                        error=str(e))
            raise
    
    def _generate_xml_report(self, data: Dict[str, Any], template: Dict[str, Any], violations: List[Dict[str, Any]]) -> str:
        """Generate XML compliance report"""
        root = ET.Element("ComplianceReport")
        
        # Add report metadata
        metadata = ET.SubElement(root, "Metadata")
        ET.SubElement(metadata, "GeneratedAt").text = datetime.now(timezone.utc).isoformat()
        ET.SubElement(metadata, "ReportType").text = template.get("template", "unknown")
        
        # Add data
        data_elem = ET.SubElement(root, "Data")
        for key, value in data.items():
            ET.SubElement(data_elem, key).text = str(value)
        
        # Add violations
        violations_elem = ET.SubElement(root, "Violations")
        for violation in violations:
            violation_elem = ET.SubElement(violations_elem, "Violation")
            ET.SubElement(violation_elem, "RuleId").text = violation.get("rule_id", "")
            ET.SubElement(violation_elem, "Severity").text = violation.get("severity", "")
            ET.SubElement(violation_elem, "Description").text = violation.get("description", "")
        
        return ET.tostring(root, encoding='unicode')
    
    def _generate_csv_report(self, data: Dict[str, Any], template: Dict[str, Any], violations: List[Dict[str, Any]]) -> str:
        """Generate CSV compliance report"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(["Field", "Value", "Status"])
        
        # Write data
        for key, value in data.items():
            writer.writerow([key, value, "OK"])
        
        # Write violations
        for violation in violations:
            writer.writerow([
                violation.get("rule_id", ""),
                violation.get("description", ""),
                f"VIOLATION: {violation.get('severity', '').upper()}"
            ])
        
        return output.getvalue()
    
    def _generate_json_report(self, data: Dict[str, Any], template: Dict[str, Any], violations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate JSON compliance report"""
        return {
            "metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "template": template.get("template", "unknown"),
                "format": "JSON"
            },
            "data": data,
            "violations": violations,
            "summary": {
                "total_violations": len(violations),
                "critical_violations": len([v for v in violations if v.get("severity") == "critical"]),
                "high_violations": len([v for v in violations if v.get("severity") == "high"])
            }
        }
    
    def _generate_recommendations(self, violations: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on violations"""
        recommendations = []
        
        for violation in violations:
            rule_id = violation.get("rule_id", "")
            severity = violation.get("severity", "")
            
            if severity == "critical":
                recommendations.append(f"CRITICAL: Address {rule_id} violation immediately")
            elif severity == "high":
                recommendations.append(f"HIGH: Resolve {rule_id} violation within 24 hours")
            elif severity == "medium":
                recommendations.append(f"MEDIUM: Address {rule_id} violation within 7 days")
            else:
                recommendations.append(f"LOW: Monitor {rule_id} violation")
        
        return recommendations


# Global compliance engine instance
_compliance_engine: Optional[ComplianceEngine] = None


def get_compliance_engine() -> ComplianceEngine:
    """Get the global compliance engine instance"""
    global _compliance_engine
    
    if _compliance_engine is None:
        _compliance_engine = ComplianceEngine()
    
    return _compliance_engine


class CAPAEngine:
    """Corrective and Preventive Action (CAPA) engine for compliance management"""
    
    def __init__(self):
        self.capa_records = {}
        self.corrective_actions = {}
        self.preventive_actions = {}
        self.action_plans = {}
        self.effectiveness_reviews = {}
        
    def create_corrective_action(self, 
                               violation_id: str, 
                               violation_details: Dict[str, Any],
                               assigned_to: str,
                               due_date: datetime) -> Dict[str, Any]:
        """Create a corrective action for a compliance violation"""
        try:
            capa_id = f"CAPA_{violation_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            corrective_action = {
                "capa_id": capa_id,
                "violation_id": violation_id,
                "action_type": "corrective",
                "status": "open",
                "assigned_to": assigned_to,
                "created_date": datetime.now().isoformat(),
                "due_date": due_date.isoformat(),
                "violation_details": violation_details,
                "root_cause_analysis": {},
                "corrective_measures": [],
                "implementation_plan": {},
                "effectiveness_metrics": {},
                "review_status": "pending",
                "closure_date": None,
                "lessons_learned": []
            }
            
            self.corrective_actions[capa_id] = corrective_action
            
            logger.info("Corrective action created", 
                       capa_id=capa_id, 
                       violation_id=violation_id,
                       assigned_to=assigned_to)
            
            return corrective_action
            
        except Exception as e:
            logger.error("Failed to create corrective action", 
                        violation_id=violation_id, 
                        error=str(e))
            raise
    
    def create_preventive_action(self, 
                               risk_id: str,
                               risk_assessment: Dict[str, Any],
                               assigned_to: str,
                               due_date: datetime) -> Dict[str, Any]:
        """Create a preventive action for identified risks"""
        try:
            capa_id = f"CAPA_{risk_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            preventive_action = {
                "capa_id": capa_id,
                "risk_id": risk_id,
                "action_type": "preventive",
                "status": "open",
                "assigned_to": assigned_to,
                "created_date": datetime.now().isoformat(),
                "due_date": due_date.isoformat(),
                "risk_assessment": risk_assessment,
                "preventive_measures": [],
                "implementation_plan": {},
                "monitoring_plan": {},
                "review_status": "pending",
                "closure_date": None,
                "effectiveness_review": {}
            }
            
            self.preventive_actions[capa_id] = preventive_action
            
            logger.info("Preventive action created", 
                       capa_id=capa_id, 
                       risk_id=risk_id,
                       assigned_to=assigned_to)
            
            return preventive_action
            
        except Exception as e:
            logger.error("Failed to create preventive action", 
                        risk_id=risk_id, 
                        error=str(e))
            raise
    
    def perform_root_cause_analysis(self, capa_id: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform root cause analysis for a corrective action"""
        try:
            if capa_id not in self.corrective_actions:
                raise ValueError(f"CAPA {capa_id} not found")
            
            corrective_action = self.corrective_actions[capa_id]
            
            # Perform 5-Why analysis
            five_why_analysis = self._perform_five_why_analysis(analysis_data)
            
            # Perform fishbone analysis
            fishbone_analysis = self._perform_fishbone_analysis(analysis_data)
            
            # Identify root causes
            root_causes = self._identify_root_causes(analysis_data)
            
            # Generate recommendations
            recommendations = self._generate_rca_recommendations(root_causes, five_why_analysis)
            
            root_cause_analysis = {
                "analysis_date": datetime.now().isoformat(),
                "five_why_analysis": five_why_analysis,
                "fishbone_analysis": fishbone_analysis,
                "root_causes": root_causes,
                "recommendations": recommendations,
                "analysis_confidence": self._calculate_analysis_confidence(analysis_data)
            }
            
            corrective_action["root_cause_analysis"] = root_cause_analysis
            corrective_action["status"] = "analysis_complete"
            
            logger.info("Root cause analysis completed", 
                       capa_id=capa_id,
                       root_causes_count=len(root_causes))
            
            return root_cause_analysis
            
        except Exception as e:
            logger.error("Failed to perform root cause analysis", 
                        capa_id=capa_id, 
                        error=str(e))
            raise
    
    def implement_corrective_measures(self, capa_id: str, measures: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Implement corrective measures for a CAPA"""
        try:
            if capa_id not in self.corrective_actions:
                raise ValueError(f"CAPA {capa_id} not found")
            
            corrective_action = self.corrective_actions[capa_id]
            
            implementation_plan = {
                "measures": measures,
                "implementation_date": datetime.now().isoformat(),
                "implementation_status": "in_progress",
                "progress_tracking": {},
                "milestones": self._create_implementation_milestones(measures),
                "resource_requirements": self._calculate_resource_requirements(measures),
                "risk_assessment": self._assess_implementation_risks(measures)
            }
            
            corrective_action["corrective_measures"] = measures
            corrective_action["implementation_plan"] = implementation_plan
            corrective_action["status"] = "implementation_in_progress"
            
            logger.info("Corrective measures implementation started", 
                       capa_id=capa_id,
                       measures_count=len(measures))
            
            return implementation_plan
            
        except Exception as e:
            logger.error("Failed to implement corrective measures", 
                        capa_id=capa_id, 
                        error=str(e))
            raise
    
    def track_implementation_progress(self, capa_id: str, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track implementation progress for a CAPA"""
        try:
            if capa_id not in self.corrective_actions and capa_id not in self.preventive_actions:
                raise ValueError(f"CAPA {capa_id} not found")
            
            # Get the appropriate action
            if capa_id in self.corrective_actions:
                action = self.corrective_actions[capa_id]
                action_type = "corrective"
            else:
                action = self.preventive_actions[capa_id]
                action_type = "preventive"
            
            # Update progress tracking
            progress_update = {
                "update_date": datetime.now().isoformat(),
                "progress_percentage": progress_data.get("progress_percentage", 0),
                "completed_measures": progress_data.get("completed_measures", []),
                "pending_measures": progress_data.get("pending_measures", []),
                "challenges": progress_data.get("challenges", []),
                "next_steps": progress_data.get("next_steps", []),
                "resource_utilization": progress_data.get("resource_utilization", {}),
                "timeline_status": self._assess_timeline_status(action, progress_data)
            }
            
            if "implementation_plan" in action:
                action["implementation_plan"]["progress_tracking"] = progress_update
            elif "monitoring_plan" in action:
                action["monitoring_plan"]["progress_tracking"] = progress_update
            
            # Update status based on progress
            if progress_data.get("progress_percentage", 0) >= 100:
                action["status"] = "completed"
                action["closure_date"] = datetime.now().isoformat()
            
            logger.info("CAPA progress updated", 
                       capa_id=capa_id,
                       progress_percentage=progress_data.get("progress_percentage", 0))
            
            return progress_update
            
        except Exception as e:
            logger.error("Failed to track CAPA progress", 
                        capa_id=capa_id, 
                        error=str(e))
            raise
    
    def perform_effectiveness_review(self, capa_id: str, review_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform effectiveness review for a completed CAPA"""
        try:
            if capa_id not in self.corrective_actions and capa_id not in self.preventive_actions:
                raise ValueError(f"CAPA {capa_id} not found")
            
            # Get the appropriate action
            if capa_id in self.corrective_actions:
                action = self.corrective_actions[capa_id]
                action_type = "corrective"
            else:
                action = self.preventive_actions[capa_id]
                action_type = "preventive"
            
            # Perform effectiveness assessment
            effectiveness_metrics = self._calculate_effectiveness_metrics(action, review_data)
            
            # Assess recurrence risk
            recurrence_risk = self._assess_recurrence_risk(action, review_data)
            
            # Generate lessons learned
            lessons_learned = self._generate_lessons_learned(action, review_data)
            
            # Determine overall effectiveness
            overall_effectiveness = self._determine_overall_effectiveness(effectiveness_metrics, recurrence_risk)
            
            effectiveness_review = {
                "review_date": datetime.now().isoformat(),
                "reviewer": review_data.get("reviewer", "system"),
                "effectiveness_metrics": effectiveness_metrics,
                "recurrence_risk": recurrence_risk,
                "lessons_learned": lessons_learned,
                "overall_effectiveness": overall_effectiveness,
                "recommendations": self._generate_effectiveness_recommendations(effectiveness_metrics, recurrence_risk),
                "closure_recommendation": self._recommend_closure(action, overall_effectiveness)
            }
            
            action["effectiveness_review"] = effectiveness_review
            action["review_status"] = "completed"
            
            if effectiveness_review["closure_recommendation"] == "close":
                action["status"] = "closed"
                action["closure_date"] = datetime.now().isoformat()
            
            logger.info("CAPA effectiveness review completed", 
                       capa_id=capa_id,
                       overall_effectiveness=overall_effectiveness)
            
            return effectiveness_review
            
        except Exception as e:
            logger.error("Failed to perform effectiveness review", 
                        capa_id=capa_id, 
                        error=str(e))
            raise
    
    def _perform_five_why_analysis(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform 5-Why analysis"""
        problem = analysis_data.get("problem", "Unknown problem")
        
        five_why_analysis = {
            "problem": problem,
            "why_1": analysis_data.get("why_1", "Why did this problem occur?"),
            "why_2": analysis_data.get("why_2", "Why did the first cause happen?"),
            "why_3": analysis_data.get("why_3", "Why did the second cause happen?"),
            "why_4": analysis_data.get("why_4", "Why did the third cause happen?"),
            "why_5": analysis_data.get("why_5", "Why did the fourth cause happen?"),
            "root_cause": analysis_data.get("root_cause", "Root cause not identified"),
            "analysis_confidence": analysis_data.get("confidence", 0.7)
        }
        
        return five_why_analysis
    
    def _perform_fishbone_analysis(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform fishbone (Ishikawa) analysis"""
        fishbone_analysis = {
            "problem": analysis_data.get("problem", "Unknown problem"),
            "categories": {
                "people": analysis_data.get("people_factors", []),
                "process": analysis_data.get("process_factors", []),
                "equipment": analysis_data.get("equipment_factors", []),
                "environment": analysis_data.get("environment_factors", []),
                "materials": analysis_data.get("materials_factors", []),
                "methods": analysis_data.get("methods_factors", [])
            },
            "primary_causes": analysis_data.get("primary_causes", []),
            "secondary_causes": analysis_data.get("secondary_causes", [])
        }
        
        return fishbone_analysis
    
    def _identify_root_causes(self, analysis_data: Dict[str, Any]) -> List[str]:
        """Identify root causes from analysis data"""
        root_causes = analysis_data.get("identified_root_causes", [])
        
        # Add default root causes if none provided
        if not root_causes:
            root_causes = [
                "Inadequate training",
                "Process deficiency",
                "System failure",
                "Human error",
                "Environmental factors"
            ]
        
        return root_causes
    
    def _generate_rca_recommendations(self, root_causes: List[str], five_why_analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on root cause analysis"""
        recommendations = []
        
        for root_cause in root_causes:
            if "training" in root_cause.lower():
                recommendations.append("Implement comprehensive training program")
                recommendations.append("Establish competency assessment procedures")
            elif "process" in root_cause.lower():
                recommendations.append("Review and update process documentation")
                recommendations.append("Implement process controls and checkpoints")
            elif "system" in root_cause.lower():
                recommendations.append("Upgrade system infrastructure")
                recommendations.append("Implement system monitoring and alerts")
            elif "human" in root_cause.lower():
                recommendations.append("Enhance human factors engineering")
                recommendations.append("Implement error prevention mechanisms")
            elif "environment" in root_cause.lower():
                recommendations.append("Improve environmental controls")
                recommendations.append("Implement environmental monitoring")
        
        return recommendations
    
    def _calculate_analysis_confidence(self, analysis_data: Dict[str, Any]) -> float:
        """Calculate confidence level of root cause analysis"""
        confidence_factors = [
            analysis_data.get("data_quality", 0.8),
            analysis_data.get("stakeholder_input", 0.7),
            analysis_data.get("expert_review", 0.9),
            analysis_data.get("historical_data", 0.6)
        ]
        
        return sum(confidence_factors) / len(confidence_factors)
    
    def _create_implementation_milestones(self, measures: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create implementation milestones for corrective measures"""
        milestones = []
        
        for i, measure in enumerate(measures):
            milestone = {
                "milestone_id": f"milestone_{i+1}",
                "measure_name": measure.get("name", f"Measure {i+1}"),
                "description": measure.get("description", ""),
                "target_date": measure.get("target_date", ""),
                "responsible_party": measure.get("responsible_party", ""),
                "status": "pending",
                "completion_criteria": measure.get("completion_criteria", [])
            }
            milestones.append(milestone)
        
        return milestones
    
    def _calculate_resource_requirements(self, measures: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate resource requirements for implementation"""
        total_cost = 0
        total_time = 0
        required_skills = []
        
        for measure in measures:
            total_cost += measure.get("estimated_cost", 0)
            total_time += measure.get("estimated_time", 0)
            required_skills.extend(measure.get("required_skills", []))
        
        return {
            "total_estimated_cost": total_cost,
            "total_estimated_time": total_time,
            "required_skills": list(set(required_skills)),
            "resource_availability": "to_be_assessed"
        }
    
    def _assess_implementation_risks(self, measures: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess implementation risks"""
        risks = []
        
        for measure in measures:
            if measure.get("complexity", "low") == "high":
                risks.append("High complexity implementation risk")
            if measure.get("cost", 0) > 100000:
                risks.append("High cost implementation risk")
            if measure.get("timeline", 0) < 30:
                risks.append("Tight timeline implementation risk")
        
        return {
            "identified_risks": risks,
            "risk_level": "high" if len(risks) > 2 else "medium" if len(risks) > 0 else "low",
            "mitigation_strategies": ["Regular progress monitoring", "Stakeholder communication", "Contingency planning"]
        }
    
    def _assess_timeline_status(self, action: Dict[str, Any], progress_data: Dict[str, Any]) -> str:
        """Assess timeline status for implementation"""
        due_date = datetime.fromisoformat(action.get("due_date", datetime.now().isoformat()))
        current_date = datetime.now()
        progress_percentage = progress_data.get("progress_percentage", 0)
        
        days_remaining = (due_date - current_date).days
        expected_progress = max(0, 100 - (days_remaining / 30) * 100)
        
        if progress_percentage >= expected_progress:
            return "on_track"
        elif progress_percentage >= expected_progress * 0.8:
            return "slightly_behind"
        else:
            return "behind_schedule"
    
    def _calculate_effectiveness_metrics(self, action: Dict[str, Any], review_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate effectiveness metrics for the CAPA"""
        metrics = {
            "problem_resolution": review_data.get("problem_resolved", False),
            "recurrence_prevention": review_data.get("recurrence_prevented", True),
            "timeline_adherence": review_data.get("timeline_adherence", 0.8),
            "cost_effectiveness": review_data.get("cost_effectiveness", 0.7),
            "stakeholder_satisfaction": review_data.get("stakeholder_satisfaction", 0.8),
            "process_improvement": review_data.get("process_improvement", 0.6)
        }
        
        # Calculate overall effectiveness score
        metrics["overall_score"] = sum(metrics.values()) / len(metrics)
        
        return metrics
    
    def _assess_recurrence_risk(self, action: Dict[str, Any], review_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk of problem recurrence"""
        recurrence_risk = {
            "risk_level": review_data.get("recurrence_risk_level", "low"),
            "risk_factors": review_data.get("risk_factors", []),
            "mitigation_measures": review_data.get("mitigation_measures", []),
            "monitoring_plan": review_data.get("monitoring_plan", {}),
            "risk_score": review_data.get("risk_score", 0.3)
        }
        
        return recurrence_risk
    
    def _generate_lessons_learned(self, action: Dict[str, Any], review_data: Dict[str, Any]) -> List[str]:
        """Generate lessons learned from the CAPA"""
        lessons_learned = review_data.get("lessons_learned", [])
        
        # Add default lessons if none provided
        if not lessons_learned:
            lessons_learned = [
                "Importance of thorough root cause analysis",
                "Need for effective implementation monitoring",
                "Value of stakeholder engagement",
                "Importance of documentation and communication"
            ]
        
        return lessons_learned
    
    def _determine_overall_effectiveness(self, effectiveness_metrics: Dict[str, Any], recurrence_risk: Dict[str, Any]) -> str:
        """Determine overall effectiveness of the CAPA"""
        overall_score = effectiveness_metrics.get("overall_score", 0.5)
        risk_score = recurrence_risk.get("risk_score", 0.3)
        
        if overall_score >= 0.8 and risk_score <= 0.3:
            return "highly_effective"
        elif overall_score >= 0.6 and risk_score <= 0.5:
            return "effective"
        elif overall_score >= 0.4 and risk_score <= 0.7:
            return "partially_effective"
        else:
            return "ineffective"
    
    def _generate_effectiveness_recommendations(self, effectiveness_metrics: Dict[str, Any], recurrence_risk: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on effectiveness review"""
        recommendations = []
        
        if effectiveness_metrics.get("overall_score", 0) < 0.6:
            recommendations.append("Implement additional corrective measures")
            recommendations.append("Review and update implementation approach")
        
        if recurrence_risk.get("risk_score", 0) > 0.5:
            recommendations.append("Strengthen preventive measures")
            recommendations.append("Enhance monitoring and surveillance")
        
        if effectiveness_metrics.get("stakeholder_satisfaction", 0) < 0.7:
            recommendations.append("Improve stakeholder communication")
            recommendations.append("Address stakeholder concerns")
        
        return recommendations
    
    def _recommend_closure(self, action: Dict[str, Any], overall_effectiveness: str) -> str:
        """Recommend whether to close the CAPA"""
        if overall_effectiveness in ["highly_effective", "effective"]:
            return "close"
        elif overall_effectiveness == "partially_effective":
            return "continue_monitoring"
        else:
            return "reopen"