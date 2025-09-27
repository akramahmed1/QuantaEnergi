from datetime import datetime
from typing import Dict, Any, List
from enum import Enum

class ComplianceFramework(Enum):
    REMIT = "REMIT"
    DODD_FRANK = "DODD_FRANK"
    FERC = "FERC"

class ComplianceService:
    """Compliance service for regulatory reporting"""
    
    @staticmethod
    def validate_trade_compliance(trade_data: Dict[str, Any], framework: ComplianceFramework) -> Dict[str, Any]:
        """Validate trade against compliance framework"""
        violations = []
        warnings = []
        
        if framework == ComplianceFramework.REMIT:
            # REMIT compliance checks
            if not trade_data.get("asset"):
                violations.append("Asset type is required for REMIT reporting")
            
            if trade_data.get("quantity", 0) > 1000000:  # 1M threshold
                warnings.append("Large trade requires additional reporting")
                
        elif framework == ComplianceFramework.DODD_FRANK:
            # Dodd-Frank compliance checks
            if trade_data.get("price", 0) > 1000:  # High-value threshold
                violations.append("High-value trade requires enhanced reporting")
                
            if not trade_data.get("counterparty"):
                warnings.append("Counterparty information recommended")
        
        return {
            "framework": framework.value,
            "compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "timestamp": datetime.now().isoformat()
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