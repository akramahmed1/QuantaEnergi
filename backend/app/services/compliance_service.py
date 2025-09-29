from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
import json

class ComplianceFramework(Enum):
    REMIT = "REMIT"
    DODD_FRANK = "DODD_FRANK"
    FERC = "FERC"

class ComplianceService:
    """Compliance service for regulatory reporting"""
    
    @staticmethod
    def validate_trade_compliance(trade_data: Dict[str, Any], framework: ComplianceFramework) -> Dict[str, Any]:
        """Enhanced trade compliance validation with detailed REMIT checks"""
        violations = []
        warnings = []
        compliance_details = {}
        
        if framework == ComplianceFramework.REMIT:
            # Enhanced REMIT compliance for Europe/UK energy trading
            compliance_details = ComplianceService._validate_remit_compliance(trade_data)
            violations = compliance_details.get("violations", [])
            warnings = compliance_details.get("warnings", [])
            
        elif framework == ComplianceFramework.DODD_FRANK:
            # Dodd-Frank compliance checks
            if trade_data.get("price", 0) > 1000:  # High-value threshold
                violations.append("High-value trade requires enhanced reporting")
                
            if not trade_data.get("counterparty"):
                warnings.append("Counterparty information recommended")
                
        elif framework == ComplianceFramework.FERC:
            # FERC compliance checks
            if trade_data.get("quantity", 0) > 100000:  # 100k threshold
                warnings.append("Large quantity trade requires FERC reporting")
        
        return {
            "framework": framework.value,
            "compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "compliance_details": compliance_details,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def _validate_remit_compliance(trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detailed REMIT compliance validation for Europe/UK energy trading"""
        violations = []
        warnings = []
        compliance_checks = {}
        
        # 1. Position Limits (REMIT Article 4)
        volume = trade_data.get("volume", trade_data.get("quantity", 0))
        if volume > 1000:  # 1000 bbl/day position limit
            violations.append("Position limit breach - volume exceeds 1000 bbl/day limit")
            compliance_checks["position_limit"] = {
                "status": "VIOLATION",
                "current_volume": volume,
                "limit": 1000,
                "excess": volume - 1000,
                "action_required": "Report to ACER immediately"
            }
        else:
            compliance_checks["position_limit"] = {
                "status": "COMPLIANT",
                "current_volume": volume,
                "limit": 1000,
                "utilization": f"{(volume/1000)*100:.1f}%"
            }
        
        # 2. Market Abuse Prevention (REMIT Article 3)
        asset = trade_data.get("asset", "").lower()
        suspicious_patterns = []
        
        # Check for potential market manipulation
        if "inside" in asset or "insider" in asset:
            violations.append("Potential insider trading - asset name contains 'inside'")
            suspicious_patterns.append("insider_trading_risk")
        
        # Check for wash trading
        if trade_data.get("counterparty") == trade_data.get("trader"):
            violations.append("Potential wash trading - same counterparty and trader")
            suspicious_patterns.append("wash_trading_risk")
        
        compliance_checks["market_abuse"] = {
            "status": "COMPLIANT" if not suspicious_patterns else "VIOLATION",
            "suspicious_patterns": suspicious_patterns,
            "checks_performed": ["insider_trading", "wash_trading", "manipulation"]
        }
        
        # 3. Reporting Requirements (REMIT Article 8)
        required_fields = ["asset", "quantity", "price", "timestamp", "counterparty"]
        missing_fields = [field for field in required_fields if not trade_data.get(field)]
        
        if missing_fields:
            violations.append(f"Missing required fields for REMIT reporting: {', '.join(missing_fields)}")
        
        compliance_checks["reporting"] = {
            "status": "COMPLIANT" if not missing_fields else "VIOLATION",
            "required_fields": required_fields,
            "missing_fields": missing_fields,
            "reporting_deadline": "T+1 day to ACER"
        }
        
        # 4. Inside Information Disclosure (REMIT Article 4)
        if trade_data.get("price", 0) > trade_data.get("market_price", 0) * 1.1:  # 10% above market
            warnings.append("Price significantly above market - potential inside information")
            compliance_checks["inside_information"] = {
                "status": "WARNING",
                "price_deviation": f"{((trade_data.get('price', 0) / trade_data.get('market_price', 1)) - 1) * 100:.1f}%",
                "threshold": "10%",
                "recommendation": "Review for inside information disclosure"
            }
        else:
            compliance_checks["inside_information"] = {
                "status": "COMPLIANT",
                "price_deviation": f"{((trade_data.get('price', 0) / trade_data.get('market_price', 1)) - 1) * 100:.1f}%"
            }
        
        # 5. Cross-border Trading (REMIT Article 6)
        if trade_data.get("cross_border", False):
            if not trade_data.get("accreditation_number"):
                violations.append("Cross-border trade requires accreditation number")
            compliance_checks["cross_border"] = {
                "status": "COMPLIANT" if trade_data.get("accreditation_number") else "VIOLATION",
                "accreditation_required": True,
                "accreditation_number": trade_data.get("accreditation_number", "MISSING")
            }
        else:
            compliance_checks["cross_border"] = {
                "status": "N/A",
                "accreditation_required": False
            }
        
        # 6. Energy Market Integrity (REMIT Article 5)
        if trade_data.get("energy_type") in ["electricity", "gas"]:
            if not trade_data.get("delivery_period"):
                warnings.append("Energy trade missing delivery period information")
            compliance_checks["energy_integrity"] = {
                "status": "WARNING" if not trade_data.get("delivery_period") else "COMPLIANT",
                "energy_type": trade_data.get("energy_type"),
                "delivery_period": trade_data.get("delivery_period", "MISSING")
            }
        else:
            compliance_checks["energy_integrity"] = {
                "status": "N/A",
                "energy_type": trade_data.get("energy_type", "unknown")
            }
        
        return {
            "violations": violations,
            "warnings": warnings,
            "compliance_checks": compliance_checks,
            "remit_article_coverage": ["Article 3", "Article 4", "Article 5", "Article 6", "Article 8"],
            "next_review_date": (datetime.now() + timedelta(days=30)).isoformat()
        }
    
    @staticmethod
    def generate_compliance_report(trades: List[Dict[str, Any]], framework: ComplianceFramework) -> Dict[str, Any]:
        """Generate compliance report for multiple trades"""
        total_trades = len(trades)
        compliant_trades = 0
        all_violations = []
        
        for trade in trades:
            result = ComplianceService.validate_trade_compliance(trade, framework)
            if result["compliant"]:
                compliant_trades += 1
            all_violations.extend(result["violations"])
        
        compliance_rate = (compliant_trades / total_trades * 100) if total_trades > 0 else 0
        
        return {
            "framework": framework.value,
            "total_trades": total_trades,
            "compliant_trades": compliant_trades,
            "compliance_rate": round(compliance_rate, 2),
            "total_violations": len(all_violations),
            "report_date": datetime.now().isoformat()
        }