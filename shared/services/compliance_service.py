import json
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import structlog
import os
from dataclasses import dataclass
from enum import Enum
import re

logger = structlog.get_logger()

class ComplianceRegion(Enum):
    """Supported compliance regions"""
    US_FERC = "us_ferc"
    US_DODD_FRANK = "us_dodd_frank"
    EU_REMIT = "eu_remit"
    UK_ETS = "uk_ets"
    EU_ETS = "eu_ets"
    UAE_ADNOC = "uae_adnoc"
    GUYANA_PETROLEUM = "guyana_petroleum"
    ISLAMIC_FINANCE = "islamic_finance"

class ComplianceStatus(Enum):
    """Compliance status enumeration"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"
    UNDER_INVESTIGATION = "under_investigation"
    EXEMPT = "exempt"

@dataclass
class ComplianceRule:
    """Represents a compliance rule"""
    rule_id: str
    region: ComplianceRegion
    rule_name: str
    description: str
    category: str
    effective_date: datetime
    last_updated: datetime
    requirements: List[str]
    penalties: List[str]
    status: str

@dataclass
class ComplianceCheck:
    """Represents a compliance check result"""
    check_id: str
    rule_id: str
    region: ComplianceRegion
    status: ComplianceStatus
    details: Dict[str, Any]
    timestamp: datetime
    compliance_score: float
    recommendations: List[str]

class ComplianceRuleFactory:
    """Factory for creating compliance rules based on region and type"""
    
    @staticmethod
    def create_rule(rule_type: str, region: ComplianceRegion, **kwargs) -> ComplianceRule:
        """Create a compliance rule based on type and region"""
        if rule_type == "trading":
            return ComplianceRule(
                rule_id=f"trading_{region.value}_{hash(str(kwargs))}",
                region=region,
                rule_name=f"Trading Compliance Rule - {region.value}",
                description=f"Trading compliance requirements for {region.value}",
                category="trading",
                effective_date=datetime.now(),
                last_updated=datetime.now(),
                requirements=["Transaction reporting", "Price transparency", "Record keeping"],
                penalties=["Fines", "Trading suspension", "License revocation"],
                status="active"
            )
        elif rule_type == "reporting":
            return ComplianceRule(
                rule_id=f"reporting_{region.value}_{hash(str(kwargs))}",
                region=region,
                rule_name=f"Reporting Compliance Rule - {region.value}",
                description=f"Reporting compliance requirements for {region.value}",
                category="reporting",
                effective_date=datetime.now(),
                last_updated=datetime.now(),
                requirements=["Regular reporting", "Data accuracy", "Timely submission"],
                penalties=["Fines", "Reporting delays", "Compliance review"],
                status="active"
            )
        else:
            raise ValueError(f"Unknown rule type: {rule_type}")

class ComplianceService:
    """Multi-region compliance service for energy trading"""
    
    def __init__(self):
        self.compliance_rules = self._initialize_compliance_rules()
        self.compliance_history = []
        self.region_configs = self._initialize_region_configs()
        self.rule_factory = ComplianceRuleFactory()
        
    def check_ferc_compliance(self, trading_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check compliance with FERC (Federal Energy Regulatory Commission) regulations"""
        try:
            compliance_score = 100.0
            violations = []
            recommendations = []
            
            # Check reporting requirements
            if not trading_data.get("transaction_reporting"):
                violations.append("Missing transaction reporting")
                compliance_score -= 20
                recommendations.append("Implement automated transaction reporting system")
            
            # Check market manipulation prevention
            if trading_data.get("market_manipulation_detection"):
                if not trading_data["market_manipulation_detection"].get("active"):
                    violations.append("Market manipulation detection not active")
                    compliance_score -= 15
                    recommendations.append("Activate market manipulation detection systems")
            else:
                violations.append("No market manipulation detection system")
                compliance_score -= 25
                recommendations.append("Implement market manipulation detection system")
            
            # Check price reporting
            if not trading_data.get("price_reporting"):
                violations.append("Missing price reporting")
                compliance_score -= 20
                recommendations.append("Establish price reporting mechanisms")
            
            # Check record keeping
            if not trading_data.get("record_keeping", {}).get("retention_period"):
                violations.append("Insufficient record keeping")
                compliance_score -= 10
                recommendations.append("Implement 3-year record retention policy")
            
            compliance_status = ComplianceStatus.COMPLIANT if compliance_score >= 90 else ComplianceStatus.NON_COMPLIANT
            
            result = {
                "region": "US_FERC",
                "compliance_score": max(0, compliance_score),
                "status": compliance_status.value,
                "violations": violations,
                "recommendations": recommendations,
                "required_actions": len(violations),
                "timestamp": datetime.now().isoformat()
            }
            
            self._record_compliance_check("FERC", result)
            return result
            
        except Exception as e:
            logger.error(f"Error checking FERC compliance: {e}")
            return {"error": str(e)}
    
    def check_dodd_frank_compliance(self, trading_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check compliance with Dodd-Frank Act regulations"""
        try:
            compliance_score = 100.0
            violations = []
            recommendations = []
            
            # Check swap reporting
            if not trading_data.get("swap_reporting"):
                violations.append("Missing swap transaction reporting")
                compliance_score -= 25
                recommendations.append("Implement swap reporting to SDRs")
            
            # Check clearing requirements
            if not trading_data.get("clearing_requirements"):
                violations.append("Missing clearing requirements compliance")
                compliance_score -= 20
                recommendations.append("Establish clearing house relationships")
            
            # Check capital requirements
            if not trading_data.get("capital_requirements"):
                violations.append("Missing capital requirements documentation")
                compliance_score -= 15
                recommendations.append("Document capital adequacy requirements")
            
            # Check business conduct standards
            if not trading_data.get("business_conduct_standards"):
                violations.append("Missing business conduct standards")
                compliance_score -= 20
                recommendations.append("Implement business conduct standards")
            
            # Check record keeping
            if not trading_data.get("record_keeping", {}).get("swap_records"):
                violations.append("Missing swap record keeping")
                compliance_score -= 20
                recommendations.append("Establish swap record keeping system")
            
            compliance_status = ComplianceStatus.COMPLIANT if compliance_score >= 90 else ComplianceStatus.NON_COMPLIANT
            
            result = {
                "region": "US_DODD_FRANK",
                "compliance_score": max(0, compliance_score),
                "status": compliance_status.value,
                "violations": violations,
                "recommendations": recommendations,
                "required_actions": len(violations),
                "timestamp": datetime.now().isoformat()
            }
            
            self._record_compliance_check("DODD_FRANK", result)
            return result
            
        except Exception as e:
            logger.error(f"Error checking Dodd-Frank compliance: {e}")
            return {"error": str(e)}
    
    def check_remit_compliance(self, trading_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check compliance with EU REMIT (Regulation on Energy Market Integrity and Transparency)"""
        try:
            compliance_score = 100.0
            violations = []
            recommendations = []
            
            # Check inside information disclosure
            if not trading_data.get("inside_information_disclosure"):
                violations.append("Missing inside information disclosure")
                compliance_score -= 25
                recommendations.append("Implement inside information disclosure system")
            
            # Check transaction reporting
            if not trading_data.get("transaction_reporting"):
                violations.append("Missing transaction reporting to ACER")
                compliance_score -= 25
                recommendations.append("Establish ACER reporting mechanisms")
            
            # Check market abuse prevention
            if not trading_data.get("market_abuse_prevention"):
                violations.append("Missing market abuse prevention measures")
                compliance_score -= 20
                recommendations.append("Implement market abuse prevention system")
            
            # Check record keeping
            if not trading_data.get("record_keeping", {}).get("remit_records"):
                violations.append("Missing REMIT record keeping")
                compliance_score -= 15
                recommendations.append("Establish 5-year REMIT record retention")
            
            # Check registration requirements
            if not trading_data.get("remit_registration"):
                violations.append("Missing REMIT registration")
                compliance_score -= 15
                recommendations.append("Complete REMIT registration with ACER")
            
            compliance_status = ComplianceStatus.COMPLIANT if compliance_score >= 90 else ComplianceStatus.NON_COMPLIANT
            
            result = {
                "region": "EU_REMIT",
                "compliance_score": max(0, compliance_score),
                "status": compliance_status.value,
                "violations": violations,
                "recommendations": recommendations,
                "required_actions": len(violations),
                "timestamp": datetime.now().isoformat()
            }
            
            self._record_compliance_check("REMIT", result)
            return result
            
        except Exception as e:
            logger.error(f"Error checking REMIT compliance: {e}")
            return {"error": str(e)}
    
    def check_islamic_finance_compliance(self, trading_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check compliance with Islamic Finance principles"""
        try:
            compliance_score = 100.0
            violations = []
            recommendations = []
            
            # Check interest prohibition (Riba)
            if trading_data.get("interest_bearing_instruments"):
                violations.append("Interest-bearing instruments not allowed in Islamic finance")
                compliance_score -= 30
                recommendations.append("Replace interest-bearing instruments with Shariah-compliant alternatives")
            
            # Check uncertainty prohibition (Gharar)
            if trading_data.get("excessive_uncertainty"):
                violations.append("Excessive uncertainty in contracts (Gharar)")
                compliance_score -= 25
                recommendations.append("Ensure all contract terms are clearly defined")
            
            # Check gambling prohibition (Maysir)
            if trading_data.get("speculative_trading"):
                violations.append("Excessive speculative trading (Maysir)")
                compliance_score -= 20
                recommendations.append("Limit speculative trading to reasonable levels")
            
            # Check asset-backed requirements
            if not trading_data.get("asset_backed_transactions"):
                violations.append("Missing asset-backed transaction requirements")
                compliance_score -= 15
                recommendations.append("Ensure transactions are backed by real assets")
            
            # Check Shariah board approval
            if not trading_data.get("shariah_board_approval"):
                violations.append("Missing Shariah board approval")
                compliance_score -= 10
                recommendations.append("Obtain Shariah board approval for all products")
            
            compliance_status = ComplianceStatus.COMPLIANT if compliance_score >= 90 else ComplianceStatus.NON_COMPLIANT
            
            result = {
                "region": "ISLAMIC_FINANCE",
                "compliance_score": max(0, compliance_score),
                "status": compliance_status.value,
                "violations": violations,
                "recommendations": recommendations,
                "required_actions": len(violations),
                "shariah_compliance": compliance_score >= 90,
                "timestamp": datetime.now().isoformat()
            }
            
            self._record_compliance_check("ISLAMIC_FINANCE", result)
            return result
            
        except Exception as e:
            logger.error(f"Error checking Islamic Finance compliance: {e}")
            return {"error": str(e)}
    
    def check_adnoc_compliance(self, trading_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check compliance with ADNOC (Abu Dhabi National Oil Company) rules"""
        try:
            compliance_score = 100.0
            violations = []
            recommendations = []
            
            # Check local content requirements
            if not trading_data.get("local_content_requirements"):
                violations.append("Missing local content requirements compliance")
                compliance_score -= 25
                recommendations.append("Ensure compliance with UAE local content requirements")
            
            # Check Emiratization requirements
            if not trading_data.get("emiratization_compliance"):
                violations.append("Missing Emiratization compliance")
                compliance_score -= 20
                recommendations.append("Implement Emiratization hiring policies")
            
            # Check environmental standards
            if not trading_data.get("environmental_standards"):
                violations.append("Missing environmental standards compliance")
                compliance_score -= 20
                recommendations.append("Implement ADNOC environmental standards")
            
            # Check safety requirements
            if not trading_data.get("safety_requirements"):
                violations.append("Missing safety requirements compliance")
                compliance_score -= 20
                recommendations.append("Implement ADNOC safety standards")
            
            # Check reporting requirements
            if not trading_data.get("adnoc_reporting"):
                violations.append("Missing ADNOC reporting requirements")
                compliance_score -= 15
                recommendations.append("Establish ADNOC reporting mechanisms")
            
            compliance_status = ComplianceStatus.COMPLIANT if compliance_score >= 90 else ComplianceStatus.NON_COMPLIANT
            
            result = {
                "region": "UAE_ADNOC",
                "compliance_score": max(0, compliance_score),
                "status": compliance_status.value,
                "violations": violations,
                "recommendations": recommendations,
                "required_actions": len(violations),
                "timestamp": datetime.now().isoformat()
            }
            
            self._record_compliance_check("ADNOC", result)
            return result
            
        except Exception as e:
            logger.error(f"Error checking ADNOC compliance: {e}")
            return {"error": str(e)}
    
    def check_guyana_petroleum_compliance(self, trading_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check compliance with Guyana Petroleum Act"""
        try:
            compliance_score = 100.0
            violations = []
            recommendations = []
            
            # Check local participation requirements
            if not trading_data.get("local_participation"):
                violations.append("Missing local participation requirements")
                compliance_score -= 25
                recommendations.append("Ensure compliance with Guyana local participation requirements")
            
            # Check environmental impact assessment
            if not trading_data.get("environmental_assessment"):
                violations.append("Missing environmental impact assessment")
                compliance_score -= 25
                recommendations.append("Complete environmental impact assessment")
            
            # Check revenue sharing
            if not trading_data.get("revenue_sharing"):
                violations.append("Missing revenue sharing compliance")
                compliance_score -= 20
                recommendations.append("Implement Guyana revenue sharing requirements")
            
            # Check local employment
            if not trading_data.get("local_employment"):
                violations.append("Missing local employment requirements")
                compliance_score -= 15
                recommendations.append("Implement local employment policies")
            
            # Check technology transfer
            if not trading_data.get("technology_transfer"):
                violations.append("Missing technology transfer requirements")
                compliance_score -= 15
                recommendations.append("Establish technology transfer programs")
            
            compliance_status = ComplianceStatus.COMPLIANT if compliance_score >= 90 else ComplianceStatus.NON_COMPLIANT
            
            result = {
                "region": "GUYANA_PETROLEUM",
                "compliance_score": max(0, compliance_score),
                "status": compliance_status.value,
                "violations": violations,
                "recommendations": recommendations,
                "required_actions": len(violations),
                "timestamp": datetime.now().isoformat()
            }
            
            self._record_compliance_check("GUYANA_PETROLEUM", result)
            return result
            
        except Exception as e:
            logger.error(f"Error checking Guyana Petroleum compliance: {e}")
            return {"error": str(e)}
    
    def check_ets_compliance(self, trading_data: Dict[str, Any], region: str = "EU") -> Dict[str, Any]:
        """Check compliance with EU-ETS or UK-ETS (Emissions Trading System)"""
        try:
            compliance_score = 100.0
            violations = []
            recommendations = []
            
            # Check emissions monitoring
            if not trading_data.get("emissions_monitoring"):
                violations.append("Missing emissions monitoring system")
                compliance_score -= 25
                recommendations.append("Implement emissions monitoring and reporting system")
            
            # Check allowance trading
            if not trading_data.get("allowance_trading"):
                violations.append("Missing allowance trading compliance")
                compliance_score -= 25
                recommendations.append("Establish allowance trading mechanisms")
            
            # Check verification requirements
            if not trading_data.get("emissions_verification"):
                violations.append("Missing emissions verification")
                compliance_score -= 20
                recommendations.append("Implement third-party emissions verification")
            
            # Check surrender requirements
            if not trading_data.get("allowance_surrender"):
                violations.append("Missing allowance surrender compliance")
                compliance_score -= 20
                recommendations.append("Establish allowance surrender procedures")
            
            # Check reporting requirements
            if not trading_data.get("ets_reporting"):
                violations.append("Missing ETS reporting requirements")
                compliance_score -= 10
                recommendations.append("Implement ETS reporting mechanisms")
            
            compliance_status = ComplianceStatus.COMPLIANT if compliance_score >= 90 else ComplianceStatus.NON_COMPLIANT
            
            result = {
                "region": f"{region}_ETS",
                "compliance_score": max(0, compliance_score),
                "status": compliance_status.value,
                "violations": violations,
                "recommendations": recommendations,
                "required_actions": len(violations),
                "emissions_compliance": compliance_score >= 90,
                "timestamp": datetime.now().isoformat()
            }
            
            self._record_compliance_check(f"{region}_ETS", result)
            return result
            
        except Exception as e:
            logger.error(f"Error checking ETS compliance: {e}")
            return {"error": str(e)}
    
    def comprehensive_compliance_check(self, trading_data: Dict[str, Any], 
                                    regions: List[ComplianceRegion] = None) -> Dict[str, Any]:
        """Perform comprehensive compliance check across multiple regions"""
        try:
            if regions is None:
                regions = list(ComplianceRegion)
            
            compliance_results = {}
            overall_score = 0
            total_violations = 0
            all_recommendations = []
            
            # Check compliance for each region
            for region in regions:
                if region == ComplianceRegion.US_FERC:
                    result = self.check_ferc_compliance(trading_data)
                elif region == ComplianceRegion.US_DODD_FRANK:
                    result = self.check_dodd_frank_compliance(trading_data)
                elif region == ComplianceRegion.EU_REMIT:
                    result = self.check_remit_compliance(trading_data)
                elif region == ComplianceRegion.ISLAMIC_FINANCE:
                    result = self.check_islamic_finance_compliance(trading_data)
                elif region == ComplianceRegion.UAE_ADNOC:
                    result = self.check_adnoc_compliance(trading_data)
                elif region == ComplianceRegion.GUYANA_PETROLEUM:
                    result = self.check_guyana_petroleum_compliance(trading_data)
                elif region == ComplianceRegion.EU_ETS:
                    result = self.check_ets_compliance(trading_data, "EU")
                elif region == ComplianceRegion.UK_ETS:
                    result = self.check_ets_compliance(trading_data, "UK")
                else:
                    continue
                
                if "error" not in result:
                    compliance_results[region.value] = result
                    overall_score += result.get("compliance_score", 0)
                    total_violations += result.get("required_actions", 0)
                    all_recommendations.extend(result.get("recommendations", []))
            
            # Calculate overall compliance score
            if compliance_results:
                overall_score = overall_score / len(compliance_results)
                overall_status = ComplianceStatus.COMPLIANT if overall_score >= 90 else ComplianceStatus.NON_COMPLIANT
            else:
                overall_score = 0
                overall_status = ComplianceStatus.NON_COMPLIANT
            
            comprehensive_result = {
                "overall_compliance_score": round(overall_score, 2),
                "overall_status": overall_status.value,
                "regions_checked": len(compliance_results),
                "total_violations": total_violations,
                "compliance_by_region": compliance_results,
                "consolidated_recommendations": list(set(all_recommendations)),
                "priority_actions": self._prioritize_recommendations(all_recommendations),
                "timestamp": datetime.now().isoformat()
            }
            
            return comprehensive_result
            
        except Exception as e:
            logger.error(f"Error in comprehensive compliance check: {e}")
            return {"error": str(e)}
    
    def _prioritize_recommendations(self, recommendations: List[str]) -> List[Dict[str, Any]]:
        """Prioritize compliance recommendations"""
        priority_keywords = {
            "high": ["immediate", "critical", "missing", "not allowed", "prohibition"],
            "medium": ["implement", "establish", "ensure", "complete"],
            "low": ["consider", "review", "monitor", "enhance"]
        }
        
        prioritized = []
        for rec in recommendations:
            priority = "low"
            for level, keywords in priority_keywords.items():
                if any(keyword in rec.lower() for keyword in keywords):
                    priority = level
                    break
            
            prioritized.append({
                "recommendation": rec,
                "priority": priority,
                "estimated_effort": "medium" if priority == "high" else "low"
            })
        
        # Sort by priority
        priority_order = {"high": 3, "medium": 2, "low": 1}
        prioritized.sort(key=lambda x: priority_order[x["priority"]], reverse=True)
        
        return prioritized
    
    def _record_compliance_check(self, region: str, result: Dict[str, Any]):
        """Record compliance check in history"""
        check_record = {
            "check_id": f"check_{int(datetime.now().timestamp())}",
            "region": region,
            "timestamp": datetime.now(),
            "result": result
        }
        self.compliance_history.append(check_record)
    
    def get_compliance_history(self, region: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get compliance check history"""
        try:
            if region:
                filtered_history = [
                    record for record in self.compliance_history 
                    if record["region"] == region
                ]
            else:
                filtered_history = self.compliance_history
            
            # Sort by timestamp and limit results
            sorted_history = sorted(filtered_history, key=lambda x: x["timestamp"], reverse=True)
            return sorted_history[:limit]
            
        except Exception as e:
            logger.error(f"Error getting compliance history: {e}")
            return []
    
    def _initialize_compliance_rules(self) -> Dict[str, ComplianceRule]:
        """Initialize compliance rules database"""
        rules = {}
        
        # FERC Rules
        rules["ferc_001"] = ComplianceRule(
            rule_id="ferc_001",
            region=ComplianceRegion.US_FERC,
            rule_name="Transaction Reporting",
            description="All energy transactions must be reported to FERC",
            category="Reporting",
            effective_date=datetime(2020, 1, 1),
            last_updated=datetime.now(),
            requirements=["Automated reporting", "Real-time data", "3-year retention"],
            penalties=["Fines up to $1M per day", "License revocation"],
            status="active"
        )
        
        # Dodd-Frank Rules
        rules["df_001"] = ComplianceRule(
            rule_id="df_001",
            region=ComplianceRegion.US_DODD_FRANK,
            rule_name="Swap Reporting",
            description="All swap transactions must be reported to SDRs",
            category="Reporting",
            effective_date=datetime(2012, 7, 16),
            last_updated=datetime.now(),
            requirements=["SDR reporting", "Real-time pricing", "Capital requirements"],
            penalties=["Fines up to $250K per violation", "Criminal charges"],
            status="active"
        )
        
        return rules
    
    def _initialize_region_configs(self) -> Dict[str, Dict[str, Any]]:
        """Initialize region-specific configurations"""
        return {
            "US_FERC": {
                "reporting_frequency": "real_time",
                "retention_period": "3 years",
                "penalties": ["Fines", "License revocation", "Criminal charges"]
            },
            "US_DODD_FRANK": {
                "reporting_frequency": "real_time",
                "retention_period": "5 years",
                "penalties": ["Fines", "Criminal charges", "Trading restrictions"]
            },
            "EU_REMIT": {
                "reporting_frequency": "real_time",
                "retention_period": "5 years",
                "penalties": ["Fines", "Trading restrictions", "Criminal charges"]
            },
            "ISLAMIC_FINANCE": {
                "reporting_frequency": "daily",
                "retention_period": "7 years",
                "penalties": ["Contract invalidation", "Reputational damage"]
            }
        }
    
    def get_compliance_status(self) -> Dict[str, Any]:
        """Get compliance service status"""
        return {
            "total_rules": len(self.compliance_rules),
            "total_checks": len(self.compliance_history),
            "supported_regions": [region.value for region in ComplianceRegion],
            "active_rules": len([r for r in self.compliance_rules.values() if r.status == "active"]),
            "last_check": self.compliance_history[-1]["timestamp"].isoformat() if self.compliance_history else None,
            "timestamp": datetime.now().isoformat()
        }

# Global instance
compliance_service = ComplianceService()
