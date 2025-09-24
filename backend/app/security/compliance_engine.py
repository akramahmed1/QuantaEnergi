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
