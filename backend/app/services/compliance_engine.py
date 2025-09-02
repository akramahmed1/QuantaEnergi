"""
Compliance Engine for ETRM/CTRM Trading
Handles regulatory compliance, risk monitoring, and audit trails
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import math
import logging

logger = logging.getLogger(__name__)


class ComplianceEngine:
    """Service for managing regulatory compliance and risk monitoring"""
    
    def __init__(self):
        self.compliance_rules = {}
        self.risk_thresholds = {}
        self.audit_logs = []
        self.violations = []
        self.rule_counter = 1000
        
        # Initialize compliance rules
        self._initialize_compliance_rules()
    
    def _initialize_compliance_rules(self):
        """Initialize compliance rules and thresholds"""
        # Regulatory limits
        self.compliance_rules = {
            "position_limits": {
                "max_single_position": 10000000,      # $10M max single position
                "max_portfolio_concentration": 0.25,   # 25% max concentration
                "max_daily_turnover": 50000000        # $50M max daily turnover
            },
            "exposure_limits": {
                "max_counterparty_exposure": 0.15,    # 15% max counterparty exposure
                "max_commodity_exposure": 0.30,       # 30% max commodity exposure
                "max_geographic_exposure": 0.40       # 40% max geographic exposure
            },
            "risk_limits": {
                "max_var": 2000000,                   # $2M max VaR
                "max_stress_loss": 5000000,           # $5M max stress loss
                "max_leverage": 3.0                   # 3x max leverage
            }
        }
        
        # Risk thresholds
        self.risk_thresholds = {
            "warning": 0.7,    # 70% of limit triggers warning
            "critical": 0.9,   # 90% of limit triggers critical alert
            "breach": 1.0      # 100% of limit triggers breach
        }
    
    def check_position_compliance(self, positions: List[Dict[str, Any]], 
                                 portfolio_value: float) -> Dict[str, Any]:
        """
        Check position compliance against regulatory limits
        
        Args:
            positions: List of trading positions
            portfolio_value: Total portfolio value
            
        Returns:
            Dict with compliance check results
        """
        # TODO: Implement comprehensive position compliance checking
        violations = []
        warnings = []
        
        # Check single position limits
        for position in positions:
            position_value = position.get("notional_value", 0)
            if position_value > self.compliance_rules["position_limits"]["max_single_position"]:
                violations.append({
                    "rule": "max_single_position",
                    "position_id": position.get("position_id"),
                    "current_value": position_value,
                    "limit": self.compliance_rules["position_limits"]["max_single_position"],
                    "severity": "breach"
                })
            elif position_value > self.compliance_rules["position_limits"]["max_single_position"] * self.risk_thresholds["warning"]:
                warnings.append({
                    "rule": "max_single_position",
                    "position_id": position.get("position_id"),
                    "current_value": position_value,
                    "limit": self.compliance_rules["position_limits"]["max_single_position"],
                    "severity": "warning"
                })
        
        # Check portfolio concentration
        if portfolio_value > 0:
            for position in positions:
                concentration = position.get("notional_value", 0) / portfolio_value
                if concentration > self.compliance_rules["position_limits"]["max_portfolio_concentration"]:
                    violations.append({
                        "rule": "max_portfolio_concentration",
                        "position_id": position.get("position_id"),
                        "current_concentration": concentration,
                        "limit": self.compliance_rules["position_limits"]["max_portfolio_concentration"],
                        "severity": "breach"
                    })
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "total_positions": len(positions),
            "portfolio_value": portfolio_value,
            "checked_at": datetime.now().isoformat()
        }
    
    def check_exposure_compliance(self, positions: List[Dict[str, Any]], 
                                 counterparties: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check exposure compliance against limits
        
        Args:
            positions: List of trading positions
            counterparties: List of counterparty information
            
        Returns:
            Dict with exposure compliance results
        """
        # TODO: Implement comprehensive exposure checking
        violations = []
        warnings = []
        
        # Check counterparty exposure
        counterparty_exposure = {}
        for position in positions:
            counterparty_id = position.get("counterparty_id")
            if counterparty_id:
                if counterparty_id not in counterparty_exposure:
                    counterparty_exposure[counterparty_id] = 0
                counterparty_exposure[counterparty_id] += position.get("notional_value", 0)
        
        total_portfolio_value = sum(p.get("notional_value", 0) for p in positions)
        
        for counterparty_id, exposure in counterparty_exposure.items():
            if total_portfolio_value > 0:
                exposure_ratio = exposure / total_portfolio_value
                if exposure_ratio > self.compliance_rules["exposure_limits"]["max_counterparty_exposure"]:
                    violations.append({
                        "rule": "max_counterparty_exposure",
                        "counterparty_id": counterparty_id,
                        "current_exposure": exposure_ratio,
                        "limit": self.compliance_rules["exposure_limits"]["max_counterparty_exposure"],
                        "severity": "breach"
                    })
        
        # Check commodity exposure
        commodity_exposure = {}
        for position in positions:
            commodity = position.get("commodity")
            if commodity:
                if commodity not in commodity_exposure:
                    commodity_exposure[commodity] = 0
                commodity_exposure[commodity] += position.get("notional_value", 0)
        
        for commodity, exposure in commodity_exposure.items():
            if total_portfolio_value > 0:
                exposure_ratio = exposure / total_portfolio_value
                if exposure_ratio > self.compliance_rules["exposure_limits"]["max_commodity_exposure"]:
                    violations.append({
                        "rule": "max_commodity_exposure",
                        "commodity": commodity,
                        "current_exposure": exposure_ratio,
                        "limit": self.compliance_rules["exposure_limits"]["max_commodity_exposure"],
                        "severity": "breach"
                    })
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "counterparty_exposure": counterparty_exposure,
            "commodity_exposure": commodity_exposure,
            "total_portfolio_value": total_portfolio_value,
            "checked_at": datetime.now().isoformat()
        }
    
    def check_risk_compliance(self, risk_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check risk metrics against compliance limits
        
        Args:
            risk_metrics: Calculated risk metrics
            
        Returns:
            Dict with risk compliance results
        """
        # TODO: Implement comprehensive risk compliance checking
        violations = []
        warnings = []
        
        # Check VaR limits
        var_95 = risk_metrics.get("var_95", 0)
        if var_95 > self.compliance_rules["risk_limits"]["max_var"]:
            violations.append({
                "rule": "max_var",
                "current_value": var_95,
                "limit": self.compliance_rules["risk_limits"]["max_var"],
                "severity": "breach"
            })
        elif var_95 > self.compliance_rules["risk_limits"]["max_var"] * self.risk_thresholds["warning"]:
            warnings.append({
                "rule": "max_var",
                "current_value": var_95,
                "limit": self.compliance_rules["risk_limits"]["max_var"],
                "severity": "warning"
            })
        
        # Check leverage limits
        leverage = risk_metrics.get("leverage", 1.0)
        if leverage > self.compliance_rules["risk_limits"]["max_leverage"]:
            violations.append({
                "rule": "max_leverage",
                "current_value": leverage,
                "limit": self.compliance_rules["risk_limits"]["max_leverage"],
                "severity": "breach"
            })
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "risk_metrics": risk_metrics,
            "checked_at": datetime.now().isoformat()
        }
    
    def log_audit_event(self, event_type: str, event_data: Dict[str, Any], 
                        user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Log audit event for compliance tracking
        
        Args:
            event_type: Type of audit event
            event_data: Event details
            user_id: User who triggered the event
            
        Returns:
            Dict with audit log confirmation
        """
        # TODO: Implement proper audit logging with database
        audit_id = f"AUDIT-{self.rule_counter:06d}"
        self.rule_counter += 1
        
        audit_entry = {
            "audit_id": audit_id,
            "event_type": event_type,
            "event_data": event_data,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "ip_address": "127.0.0.1",  # TODO: Get real IP
            "session_id": "stub_session"  # TODO: Get real session
        }
        
        self.audit_logs.append(audit_entry)
        
        return {
            "success": True,
            "audit_id": audit_id,
            "logged_at": audit_entry["timestamp"]
        }
    
    def get_audit_logs(self, filters: Optional[Dict[str, Any]] = None, 
                       limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve audit logs with optional filtering
        
        Args:
            filters: Optional filter criteria
            limit: Maximum number of logs to return
            
        Returns:
            List of audit log entries
        """
        # TODO: Implement proper audit log retrieval
        logs = self.audit_logs.copy()
        
        if filters:
            if "event_type" in filters:
                logs = [log for log in logs if log.get("event_type") == filters["event_type"]]
            if "user_id" in filters:
                logs = [log for log in logs if log.get("user_id") == filters["user_id"]]
            if "start_date" in filters:
                start_date = datetime.fromisoformat(filters["start_date"])
                logs = [log for log in logs if datetime.fromisoformat(log["timestamp"]) >= start_date]
            if "end_date" in filters:
                end_date = datetime.fromisoformat(filters["end_date"])
                logs = [log for log in logs if datetime.fromisoformat(log["timestamp"]) <= end_date]
        
        # Sort by timestamp (newest first) and limit results
        logs.sort(key=lambda x: x["timestamp"], reverse=True)
        return logs[:limit]
    
    def generate_compliance_report(self, positions: List[Dict[str, Any]], 
                                  risk_metrics: Dict[str, Any], 
                                  period: str = "daily") -> Dict[str, Any]:
        """
        Generate comprehensive compliance report
        
        Args:
            positions: List of trading positions
            risk_metrics: Calculated risk metrics
            period: Reporting period
            
        Returns:
            Dict with compliance report
        """
        # TODO: Implement comprehensive compliance reporting
        portfolio_value = sum(p.get("notional_value", 0) for p in positions)
        
        # Run all compliance checks
        position_compliance = self.check_position_compliance(positions, portfolio_value)
        exposure_compliance = self.check_exposure_compliance(positions, [])
        risk_compliance = self.check_risk_compliance(risk_metrics)
        
        # Calculate compliance score
        total_checks = 3
        passed_checks = sum([
            1 if position_compliance["compliant"] else 0,
            1 if exposure_compliance["compliant"] else 0,
            1 if risk_compliance["compliant"] else 0
        ])
        
        compliance_score = (passed_checks / total_checks) * 100
        
        # Generate report
        report = {
            "report_id": f"COMP-{datetime.now().strftime('%Y%m%d')}-{self.rule_counter:04d}",
            "period": period,
            "generated_at": datetime.now().isoformat(),
            "portfolio_summary": {
                "total_positions": len(positions),
                "portfolio_value": portfolio_value,
                "total_violations": len(position_compliance["violations"]) + 
                                  len(exposure_compliance["violations"]) + 
                                  len(risk_compliance["violations"])
            },
            "compliance_checks": {
                "position_compliance": position_compliance,
                "exposure_compliance": exposure_compliance,
                "risk_compliance": risk_compliance
            },
            "compliance_score": compliance_score,
            "overall_status": "compliant" if compliance_score == 100 else "non_compliant",
            "recommendations": self._generate_recommendations(position_compliance, exposure_compliance, risk_compliance)
        }
        
        # Log report generation
        self.log_audit_event("compliance_report_generated", {"report_id": report["report_id"]})
        
        return report
    
    def _generate_recommendations(self, position_compliance: Dict[str, Any], 
                                 exposure_compliance: Dict[str, Any], 
                                 risk_compliance: Dict[str, Any]) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        # Position recommendations
        if not position_compliance["compliant"]:
            recommendations.append("Review and reduce oversized positions to meet regulatory limits")
        
        # Exposure recommendations
        if not exposure_compliance["compliant"]:
            recommendations.append("Diversify counterparty and commodity exposure to meet concentration limits")
        
        # Risk recommendations
        if not risk_compliance["compliant"]:
            recommendations.append("Implement risk reduction strategies to meet VaR and leverage limits")
        
        if not recommendations:
            recommendations.append("Maintain current compliance practices")
        
        return recommendations
    
    def check_regulatory_updates(self, jurisdiction: str) -> Dict[str, Any]:
        """
        Check for regulatory updates and changes
        
        Args:
            jurisdiction: Regulatory jurisdiction
            
        Returns:
            Dict with regulatory update information
        """
        # TODO: Implement real regulatory monitoring
        # Stub regulatory updates
        updates = {
            "usa": [
                {
                    "regulation": "Dodd-Frank Act",
                    "update_type": "position_limit_review",
                    "effective_date": "2024-06-01",
                    "impact": "medium",
                    "description": "Position limits review for energy commodities"
                }
            ],
            "europe": [
                {
                    "regulation": "MiFID II",
                    "update_type": "reporting_requirement",
                    "effective_date": "2024-07-01",
                    "impact": "high",
                    "description": "Enhanced trade reporting requirements"
                }
            ],
            "uk": [
                {
                    "regulation": "UK EMIR",
                    "update_type": "clearing_requirement",
                    "effective_date": "2024-08-01",
                    "impact": "medium",
                    "description": "Updated clearing requirements for derivatives"
                }
            ]
        }
        
        return {
            "jurisdiction": jurisdiction,
            "updates": updates.get(jurisdiction, []),
            "total_updates": len(updates.get(jurisdiction, [])),
            "checked_at": datetime.now().isoformat()
        }
