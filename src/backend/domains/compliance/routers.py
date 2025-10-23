"""
Compliance API Routers
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..base import get_db
from .services import ComplianceService, ComplianceFramework

router = APIRouter(prefix="/compliance", tags=["Compliance"])

@router.post("/validate-trade")
async def validate_trade_compliance(
    trade_data: Dict[str, Any] = Body(..., description="Trade data to validate"),
    framework: ComplianceFramework = Body(..., description="Compliance framework to check against"),
    db: Session = Depends(get_db)
):
    """Validate trade compliance against specific framework"""
    compliance_service = ComplianceService()
    
    result = compliance_service.validate_trade_compliance(trade_data, framework)
    
    return {
        "success": True,
        "validation_result": result
    }

@router.post("/generate-report")
async def generate_compliance_report(
    entity_id: str = Body(..., description="Entity ID for the report"),
    framework: ComplianceFramework = Body(..., description="Compliance framework"),
    start_date: datetime = Body(..., description="Report start date"),
    end_date: datetime = Body(..., description="Report end date"),
    db: Session = Depends(get_db)
):
    """Generate comprehensive compliance report"""
    compliance_service = ComplianceService()
    
    try:
        report = compliance_service.generate_compliance_report(entity_id, framework, start_date, end_date)
        
        return {
            "success": True,
            "report": {
                "report_id": report.report_id,
                "framework": report.framework.value,
                "entity_id": report.entity_id,
                "report_period": {
                    "start_date": report.report_period[0].isoformat(),
                    "end_date": report.report_period[1].isoformat()
                },
                "compliance_status": report.compliance_status.value,
                "violations": [
                    {
                        "violation_id": v.violation_id,
                        "rule_id": v.rule_id,
                        "entity_id": v.entity_id,
                        "violation_type": v.violation_type,
                        "severity": v.severity,
                        "description": v.description,
                        "detected_at": v.detected_at.isoformat(),
                        "status": v.status,
                        "remediation_required": v.remediation_required,
                        "deadline": v.deadline.isoformat() if v.deadline else None
                    } for v in report.violations
                ],
                "recommendations": report.recommendations,
                "generated_at": report.generated_at.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/frameworks")
async def get_compliance_frameworks():
    """Get available compliance frameworks"""
    return {
        "frameworks": [
            {
                "framework": "remit",
                "name": "REMIT",
                "description": "EU Regulation on Energy Market Integrity and Transparency",
                "region": "European Union",
                "key_rules": [
                    "Inside Information Disclosure",
                    "Market Manipulation Prevention",
                    "Position Reporting to ACER"
                ]
            },
            {
                "framework": "ferc",
                "name": "FERC",
                "description": "US Federal Energy Regulatory Commission",
                "region": "United States",
                "key_rules": [
                    "Market Manipulation Prevention",
                    "Price Reporting",
                    "Anti-Manipulation Rule"
                ]
            },
            {
                "framework": "cftc",
                "name": "CFTC",
                "description": "US Commodity Futures Trading Commission",
                "region": "United States",
                "key_rules": [
                    "Large Trader Reporting",
                    "Record Keeping",
                    "Position Limits"
                ]
            },
            {
                "framework": "emir",
                "name": "EMIR",
                "description": "EU European Market Infrastructure Regulation",
                "region": "European Union",
                "key_rules": [
                    "Trade Reporting",
                    "Central Clearing",
                    "Risk Management"
                ]
            },
            {
                "framework": "dodd_frank",
                "name": "Dodd-Frank Act",
                "description": "US Dodd-Frank Wall Street Reform",
                "region": "United States",
                "key_rules": [
                    "Volcker Rule",
                    "Swap Data Reporting",
                    "Capital Requirements"
                ]
            },
            {
                "framework": "islamic_finance",
                "name": "Islamic Finance",
                "description": "AAOIFI Islamic Finance Standards",
                "region": "Global",
                "key_rules": [
                    "Sharia Compliance",
                    "Asset Backing Verification",
                    "Prohibition of Interest (Riba)"
                ]
            }
        ]
    }

@router.get("/rules/{framework}")
async def get_compliance_rules(
    framework: ComplianceFramework,
    db: Session = Depends(get_db)
):
    """Get compliance rules for specific framework"""
    compliance_service = ComplianceService()
    
    # Get rules for the framework
    framework_rules = [
        rule for rule in compliance_service.compliance_rules.values()
        if rule.framework == framework
    ]
    
    return {
        "framework": framework.value,
        "rules": [
            {
                "rule_id": rule.rule_id,
                "name": rule.name,
                "description": rule.description,
                "severity": rule.severity,
                "is_mandatory": rule.is_mandatory,
                "reporting_frequency": rule.reporting_frequency,
                "data_requirements": rule.data_requirements,
                "applicable_entities": rule.applicable_entities
            } for rule in framework_rules
        ],
        "total_rules": len(framework_rules)
    }

@router.get("/violations")
async def get_compliance_violations(
    entity_id: str = Query(None, description="Filter by entity ID"),
    framework: ComplianceFramework = Query(None, description="Filter by framework"),
    severity: str = Query(None, description="Filter by severity"),
    status: str = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
):
    """Get compliance violations with optional filters"""
    compliance_service = ComplianceService()
    
    # Filter violations
    violations = compliance_service.violations
    
    if entity_id:
        violations = [v for v in violations if v.entity_id == entity_id]
    
    if framework:
        # Get rule IDs for framework
        framework_rule_ids = [
            rule.rule_id for rule in compliance_service.compliance_rules.values()
            if rule.framework == framework
        ]
        violations = [v for v in violations if v.rule_id in framework_rule_ids]
    
    if severity:
        violations = [v for v in violations if v.severity == severity]
    
    if status:
        violations = [v for v in violations if v.status == status]
    
    return {
        "success": True,
        "violations": [
            {
                "violation_id": v.violation_id,
                "rule_id": v.rule_id,
                "entity_id": v.entity_id,
                "violation_type": v.violation_type,
                "severity": v.severity,
                "description": v.description,
                "detected_at": v.detected_at.isoformat(),
                "status": v.status,
                "remediation_required": v.remediation_required,
                "deadline": v.deadline.isoformat() if v.deadline else None
            } for v in violations
        ],
        "total_violations": len(violations),
        "filters_applied": {
            "entity_id": entity_id,
            "framework": framework.value if framework else None,
            "severity": severity,
            "status": status
        }
    }

@router.get("/status")
async def get_compliance_status():
    """Get overall compliance status and statistics"""
    compliance_service = ComplianceService()
    
    total_violations = len(compliance_service.violations)
    active_violations = len([v for v in compliance_service.violations if v.status == "active"])
    critical_violations = len([v for v in compliance_service.violations if v.severity == "critical"])
    
    return {
        "success": True,
        "compliance_status": {
            "total_violations": total_violations,
            "active_violations": active_violations,
            "critical_violations": critical_violations,
            "compliance_score": max(0, 100 - (active_violations * 10) - (critical_violations * 20)),
            "frameworks_supported": len(set(rule.framework for rule in compliance_service.compliance_rules.values())),
            "total_rules": len(compliance_service.compliance_rules)
        },
        "recommendations": [
            "Address critical violations immediately" if critical_violations > 0 else None,
            "Resolve active violations within 7 days" if active_violations > 0 else None,
            "Implement automated compliance monitoring" if total_violations > 10 else None
        ]
    }
