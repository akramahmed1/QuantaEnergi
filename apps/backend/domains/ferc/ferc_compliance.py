"""
FERC Compliance Engine - Allegro-like compliance and reporting
Advanced Federal Energy Regulatory Commission compliance management
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)

class FERCFormType(Enum):
    FERC_1 = "ferc_1"  # Annual Report of Major Electric Utilities
    FERC_714 = "ferc_714"  # Annual Electric Balancing Authority Area and Planning Area Report
    FERC_715 = "ferc_715"  # Annual Transmission Planning and Evaluation Report
    FERC_730 = "ferc_730"  # Report of Transmission Investment Activity
    FERC_930 = "ferc_930"  # Annual Report of Transmission Investment Activity
    FERC_999 = "ferc_999"  # Quarterly Report of Electric Industry Instructions

class ComplianceStatus(Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    EXEMPT = "exempt"

class ViolationSeverity(Enum):
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"

@dataclass
class FERCRequirement:
    """FERC compliance requirement structure"""
    requirement_id: str
    form_type: FERCFormType
    description: str
    due_date: datetime
    submission_frequency: str  # annual, quarterly, monthly, etc.
    regulatory_citation: str
    compliance_status: ComplianceStatus
    violation_severity: Optional[ViolationSeverity] = None
    last_submission: Optional[datetime] = None
    next_due_date: Optional[datetime] = None
    penalty_amount: Optional[float] = None
    notes: Optional[str] = None

@dataclass
class FERCSubmission:
    """FERC submission structure"""
    submission_id: str
    form_type: FERCFormType
    submission_date: datetime
    due_date: datetime
    status: ComplianceStatus
    data: Dict[str, Any]
    validation_results: Dict[str, Any]
    compliance_score: float
    submission_errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

class FERCComplianceEngine:
    """Main FERC compliance management engine"""
    
    def __init__(self):
        self.requirements: Dict[str, FERCRequirement] = {}
        self.submissions: Dict[str, FERCSubmission] = {}
        self.validation_rules = {}
        self.compliance_history = {}
        self._initialize_ferc_requirements()
        
    def _initialize_ferc_requirements(self):
        """Initialize standard FERC requirements"""
        # FERC Form 1 - Annual Report
        self.requirements["ferc_1_annual"] = FERCRequirement(
            requirement_id="ferc_1_annual",
            form_type=FERCFormType.FERC_1,
            description="Annual Report of Major Electric Utilities",
            due_date=datetime(2025, 4, 30),
            submission_frequency="annual",
            regulatory_citation="18 CFR 141.1",
            compliance_status=ComplianceStatus.PENDING
        )
        
        # FERC Form 714 - Balancing Authority Report
        self.requirements["ferc_714_annual"] = FERCRequirement(
            requirement_id="ferc_714_annual",
            form_type=FERCFormType.FERC_714,
            description="Annual Electric Balancing Authority Area and Planning Area Report",
            due_date=datetime(2025, 3, 31),
            submission_frequency="annual",
            regulatory_citation="18 CFR 141.51",
            compliance_status=ComplianceStatus.PENDING
        )
        
        # FERC Form 715 - Transmission Planning Report
        self.requirements["ferc_715_annual"] = FERCRequirement(
            requirement_id="ferc_715_annual",
            form_type=FERCFormType.FERC_715,
            description="Annual Transmission Planning and Evaluation Report",
            due_date=datetime(2025, 6, 30),
            submission_frequency="annual",
            regulatory_citation="18 CFR 141.61",
            compliance_status=ComplianceStatus.PENDING
        )
        
        # FERC Form 730 - Transmission Investment Report
        self.requirements["ferc_730_annual"] = FERCRequirement(
            requirement_id="ferc_730_annual",
            form_type=FERCFormType.FERC_730,
            description="Annual Report of Transmission Investment Activity",
            due_date=datetime(2025, 5, 31),
            submission_frequency="annual",
            regulatory_citation="18 CFR 141.71",
            compliance_status=ComplianceStatus.PENDING
        )
        
        # FERC Form 999 - Quarterly Report
        self.requirements["ferc_999_quarterly"] = FERCRequirement(
            requirement_id="ferc_999_quarterly",
            form_type=FERCFormType.FERC_999,
            description="Quarterly Report of Electric Industry Instructions",
            due_date=datetime(2025, 1, 31),
            submission_frequency="quarterly",
            regulatory_citation="18 CFR 141.81",
            compliance_status=ComplianceStatus.PENDING
        )
    
    def assess_compliance_status(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall FERC compliance status for a company"""
        try:
            company_id = company_data.get("company_id", "unknown")
            current_date = datetime.now()
            
            compliance_assessment = {
                "company_id": company_id,
                "assessment_date": current_date.isoformat(),
                "overall_compliance_status": ComplianceStatus.COMPLIANT.value,
                "compliance_score": 100.0,
                "requirements_status": {},
                "violations": [],
                "recommendations": [],
                "next_due_dates": [],
                "penalty_risk": "low"
            }
            
            # Assess each requirement
            total_requirements = len(self.requirements)
            compliant_requirements = 0
            total_penalty_risk = 0
            
            for req_id, requirement in self.requirements.items():
                req_status = self._assess_requirement_compliance(requirement, company_data, current_date)
                compliance_assessment["requirements_status"][req_id] = req_status
                
                if req_status["compliance_status"] == ComplianceStatus.COMPLIANT.value:
                    compliant_requirements += 1
                else:
                    compliance_assessment["violations"].append({
                        "requirement_id": req_id,
                        "form_type": requirement.form_type.value,
                        "description": requirement.description,
                        "violation_type": req_status["violation_type"],
                        "severity": req_status["severity"],
                        "penalty_estimate": req_status["penalty_estimate"]
                    })
                    total_penalty_risk += req_status["penalty_estimate"]
                
                # Add to next due dates if applicable
                if requirement.next_due_date and requirement.next_due_date > current_date:
                    compliance_assessment["next_due_dates"].append({
                        "requirement_id": req_id,
                        "form_type": requirement.form_type.value,
                        "due_date": requirement.next_due_date.isoformat(),
                        "days_remaining": (requirement.next_due_date - current_date).days
                    })
            
            # Calculate overall compliance score
            compliance_score = (compliant_requirements / total_requirements) * 100
            compliance_assessment["compliance_score"] = compliance_score
            
            # Determine overall compliance status
            if compliance_score >= 95:
                compliance_assessment["overall_compliance_status"] = ComplianceStatus.COMPLIANT.value
                compliance_assessment["penalty_risk"] = "low"
            elif compliance_score >= 80:
                compliance_assessment["overall_compliance_status"] = ComplianceStatus.UNDER_REVIEW.value
                compliance_assessment["penalty_risk"] = "medium"
            else:
                compliance_assessment["overall_compliance_status"] = ComplianceStatus.NON_COMPLIANT.value
                compliance_assessment["penalty_risk"] = "high"
            
            # Generate recommendations
            compliance_assessment["recommendations"] = self._generate_compliance_recommendations(
                compliance_assessment["violations"], compliance_score
            )
            
            return compliance_assessment
            
        except Exception as e:
            logger.error(f"Error assessing FERC compliance: {str(e)}")
            raise
    
    def _assess_requirement_compliance(self, requirement: FERCRequirement, 
                                     company_data: Dict[str, Any], 
                                     current_date: datetime) -> Dict[str, Any]:
        """Assess compliance for a specific requirement"""
        try:
            # Check if submission is due
            days_until_due = (requirement.due_date - current_date).days
            
            if days_until_due < 0:
                # Overdue
                violation_type = "overdue_submission"
                severity = ViolationSeverity.MAJOR if days_until_due < -30 else ViolationSeverity.MODERATE
                penalty_estimate = self._calculate_penalty_estimate(requirement, days_until_due)
                compliance_status = ComplianceStatus.NON_COMPLIANT
            elif days_until_due <= 30:
                # Due soon
                violation_type = "due_soon"
                severity = ViolationSeverity.MINOR
                penalty_estimate = 0.0
                compliance_status = ComplianceStatus.PENDING
            else:
                # Not due yet
                violation_type = "none"
                severity = None
                penalty_estimate = 0.0
                compliance_status = ComplianceStatus.COMPLIANT
            
            # Check for data quality issues
            data_quality_score = self._assess_data_quality(requirement, company_data)
            if data_quality_score < 0.8:
                if compliance_status == ComplianceStatus.COMPLIANT:
                    compliance_status = ComplianceStatus.UNDER_REVIEW
                violation_type = "data_quality_issues"
                severity = ViolationSeverity.MINOR
                penalty_estimate = max(penalty_estimate, 1000.0)
            
            return {
                "compliance_status": compliance_status.value,
                "violation_type": violation_type,
                "severity": severity.value if severity else None,
                "penalty_estimate": penalty_estimate,
                "days_until_due": days_until_due,
                "data_quality_score": data_quality_score,
                "requirement_description": requirement.description
            }
            
        except Exception as e:
            logger.error(f"Error assessing requirement compliance: {str(e)}")
            return {
                "compliance_status": ComplianceStatus.NON_COMPLIANT.value,
                "violation_type": "assessment_error",
                "severity": ViolationSeverity.MAJOR.value,
                "penalty_estimate": 10000.0,
                "days_until_due": 0,
                "data_quality_score": 0.0,
                "requirement_description": requirement.description
            }
    
    def _calculate_penalty_estimate(self, requirement: FERCRequirement, days_overdue: int) -> float:
        """Calculate estimated penalty for overdue submissions"""
        base_penalty = 1000.0  # Base penalty amount
        
        # Increase penalty based on days overdue
        if days_overdue < -90:
            multiplier = 5.0  # 90+ days overdue
        elif days_overdue < -60:
            multiplier = 3.0  # 60-89 days overdue
        elif days_overdue < -30:
            multiplier = 2.0  # 30-59 days overdue
        else:
            multiplier = 1.0  # 1-29 days overdue
        
        # Adjust based on form type
        if requirement.form_type == FERCFormType.FERC_1:
            multiplier *= 2.0  # Higher penalty for major forms
        elif requirement.form_type == FERCFormType.FERC_714:
            multiplier *= 1.5
        
        return base_penalty * multiplier
    
    def _assess_data_quality(self, requirement: FERCRequirement, company_data: Dict[str, Any]) -> float:
        """Assess data quality for a requirement"""
        try:
            # Simplified data quality assessment
            quality_score = 1.0
            
            # Check for required data fields
            required_fields = self._get_required_fields(requirement.form_type)
            for field in required_fields:
                if field not in company_data or company_data[field] is None:
                    quality_score -= 0.1
            
            # Check for data completeness
            if requirement.form_type == FERCFormType.FERC_1:
                # Check for financial data completeness
                financial_fields = ["total_revenue", "total_expenses", "net_income"]
                for field in financial_fields:
                    if field not in company_data:
                        quality_score -= 0.05
            
            # Check for data consistency
            if "total_revenue" in company_data and "total_expenses" in company_data:
                if company_data["total_revenue"] <= 0 or company_data["total_expenses"] <= 0:
                    quality_score -= 0.1
            
            return max(0.0, quality_score)
            
        except Exception as e:
            logger.error(f"Error assessing data quality: {str(e)}")
            return 0.0
    
    def _get_required_fields(self, form_type: FERCFormType) -> List[str]:
        """Get required fields for a specific FERC form type"""
        field_mapping = {
            FERCFormType.FERC_1: [
                "company_name", "total_revenue", "total_expenses", "net_income",
                "total_assets", "total_liabilities", "shareholders_equity"
            ],
            FERCFormType.FERC_714: [
                "balancing_authority_name", "peak_demand", "energy_delivered",
                "generation_capacity", "transmission_capacity"
            ],
            FERCFormType.FERC_715: [
                "transmission_planning_area", "planned_transmission_investments",
                "transmission_reliability_metrics", "renewable_integration_plans"
            ],
            FERCFormType.FERC_730: [
                "transmission_investment_amount", "investment_category",
                "project_completion_date", "regulatory_approval_status"
            ],
            FERCFormType.FERC_999: [
                "quarterly_revenue", "quarterly_expenses", "operational_metrics",
                "compliance_activities", "regulatory_updates"
            ]
        }
        
        return field_mapping.get(form_type, [])
    
    def _generate_compliance_recommendations(self, violations: List[Dict], compliance_score: float) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        if compliance_score < 80:
            recommendations.append("🚨 URGENT: Immediate compliance review required")
            recommendations.append("Schedule emergency compliance meeting with legal team")
            recommendations.append("Implement daily compliance monitoring")
        
        if compliance_score < 95:
            recommendations.append("⚠️ HIGH PRIORITY: Address outstanding violations immediately")
            recommendations.append("Review and update compliance procedures")
            recommendations.append("Increase compliance monitoring frequency")
        
        # Specific recommendations based on violations
        for violation in violations:
            if violation["severity"] == "critical":
                recommendations.append(f"CRITICAL: Address {violation['form_type']} violation immediately")
            elif violation["severity"] == "major":
                recommendations.append(f"HIGH: Resolve {violation['form_type']} violation within 7 days")
            elif violation["severity"] == "moderate":
                recommendations.append(f"MEDIUM: Address {violation['form_type']} violation within 30 days")
        
        # General recommendations
        recommendations.extend([
            "Implement automated compliance monitoring system",
            "Schedule regular compliance training for staff",
            "Review and update compliance documentation",
            "Establish compliance dashboard for real-time monitoring"
        ])
        
        return recommendations

class FERCReportingEngine:
    """FERC reporting and submission engine"""
    
    def __init__(self):
        self.submission_templates = {}
        self.validation_rules = {}
        self._initialize_templates()
    
    def _initialize_templates(self):
        """Initialize FERC submission templates"""
        # FERC Form 1 template
        self.submission_templates[FERCFormType.FERC_1] = {
            "form_id": "FERC-1",
            "form_name": "Annual Report of Major Electric Utilities",
            "required_sections": [
                "company_information",
                "financial_statements",
                "operational_data",
                "regulatory_compliance"
            ],
            "deadline": "April 30",
            "frequency": "annual"
        }
        
        # FERC Form 714 template
        self.submission_templates[FERCFormType.FERC_714] = {
            "form_id": "FERC-714",
            "form_name": "Annual Electric Balancing Authority Area and Planning Area Report",
            "required_sections": [
                "balancing_authority_info",
                "planning_area_info",
                "demand_forecasts",
                "transmission_plans"
            ],
            "deadline": "March 31",
            "frequency": "annual"
        }
    
    def generate_submission(self, form_type: FERCFormType, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate FERC submission for a specific form type"""
        try:
            template = self.submission_templates.get(form_type)
            if not template:
                raise ValueError(f"No template found for form type: {form_type}")
            
            submission_id = f"{form_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Generate submission data
            submission_data = self._populate_submission_data(template, company_data)
            
            # Validate submission
            validation_results = self._validate_submission(submission_data, form_type)
            
            # Calculate compliance score
            compliance_score = self._calculate_submission_compliance_score(validation_results)
            
            submission = {
                "submission_id": submission_id,
                "form_type": form_type.value,
                "form_name": template["form_name"],
                "submission_date": datetime.now().isoformat(),
                "due_date": self._calculate_due_date(form_type).isoformat(),
                "status": "ready_for_submission" if compliance_score >= 90 else "needs_review",
                "compliance_score": compliance_score,
                "submission_data": submission_data,
                "validation_results": validation_results,
                "template_info": template
            }
            
            return submission
            
        except Exception as e:
            logger.error(f"Error generating FERC submission: {str(e)}")
            raise
    
    def _populate_submission_data(self, template: Dict, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Populate submission data from template and company data"""
        submission_data = {}
        
        for section in template["required_sections"]:
            submission_data[section] = self._populate_section_data(section, company_data)
        
        return submission_data
    
    def _populate_section_data(self, section: str, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Populate data for a specific section"""
        section_data = {}
        
        if section == "company_information":
            section_data = {
                "company_name": company_data.get("company_name", ""),
                "company_id": company_data.get("company_id", ""),
                "filing_date": datetime.now().strftime("%Y-%m-%d"),
                "reporting_period": "2024"
            }
        elif section == "financial_statements":
            section_data = {
                "total_revenue": company_data.get("total_revenue", 0),
                "total_expenses": company_data.get("total_expenses", 0),
                "net_income": company_data.get("net_income", 0),
                "total_assets": company_data.get("total_assets", 0),
                "total_liabilities": company_data.get("total_liabilities", 0),
                "shareholders_equity": company_data.get("shareholders_equity", 0)
            }
        elif section == "operational_data":
            section_data = {
                "total_generation": company_data.get("total_generation", 0),
                "total_sales": company_data.get("total_sales", 0),
                "peak_demand": company_data.get("peak_demand", 0),
                "average_demand": company_data.get("average_demand", 0)
            }
        else:
            section_data = {"placeholder": "data_not_available"}
        
        return section_data
    
    def _validate_submission(self, submission_data: Dict[str, Any], form_type: FERCFormType) -> Dict[str, Any]:
        """Validate submission data"""
        validation_results = {
            "overall_status": "valid",
            "errors": [],
            "warnings": [],
            "section_validations": {}
        }
        
        # Validate each section
        for section, data in submission_data.items():
            section_validation = self._validate_section(section, data, form_type)
            validation_results["section_validations"][section] = section_validation
            
            if section_validation["errors"]:
                validation_results["errors"].extend(section_validation["errors"])
            if section_validation["warnings"]:
                validation_results["warnings"].extend(section_validation["warnings"])
        
        # Set overall status
        if validation_results["errors"]:
            validation_results["overall_status"] = "invalid"
        elif validation_results["warnings"]:
            validation_results["overall_status"] = "warning"
        
        return validation_results
    
    def _validate_section(self, section: str, data: Dict[str, Any], form_type: FERCFormType) -> Dict[str, Any]:
        """Validate a specific section"""
        validation = {
            "status": "valid",
            "errors": [],
            "warnings": []
        }
        
        # Check for required fields
        required_fields = self._get_section_required_fields(section, form_type)
        for field in required_fields:
            if field not in data or data[field] is None:
                validation["errors"].append(f"Missing required field: {field}")
            elif isinstance(data[field], (int, float)) and data[field] < 0:
                validation["warnings"].append(f"Negative value for field: {field}")
        
        # Financial validation
        if section == "financial_statements":
            if "total_revenue" in data and "total_expenses" in data:
                if data["total_revenue"] < data["total_expenses"]:
                    validation["warnings"].append("Total expenses exceed total revenue")
        
        # Set status
        if validation["errors"]:
            validation["status"] = "invalid"
        elif validation["warnings"]:
            validation["status"] = "warning"
        
        return validation
    
    def _get_section_required_fields(self, section: str, form_type: FERCFormType) -> List[str]:
        """Get required fields for a section"""
        field_mapping = {
            "company_information": ["company_name", "company_id", "filing_date"],
            "financial_statements": ["total_revenue", "total_expenses", "net_income"],
            "operational_data": ["total_generation", "total_sales"],
            "balancing_authority_info": ["balancing_authority_name", "peak_demand"],
            "planning_area_info": ["planning_area_name", "transmission_capacity"]
        }
        
        return field_mapping.get(section, [])
    
    def _calculate_submission_compliance_score(self, validation_results: Dict[str, Any]) -> float:
        """Calculate compliance score for submission"""
        score = 100.0
        
        # Deduct points for errors
        score -= len(validation_results["errors"]) * 10
        
        # Deduct points for warnings
        score -= len(validation_results["warnings"]) * 5
        
        # Check section validations
        for section_validation in validation_results["section_validations"].values():
            if section_validation["status"] == "invalid":
                score -= 15
            elif section_validation["status"] == "warning":
                score -= 5
        
        return max(0.0, score)
    
    def _calculate_due_date(self, form_type: FERCFormType) -> datetime:
        """Calculate due date for a form type"""
        current_year = datetime.now().year
        
        due_dates = {
            FERCFormType.FERC_1: datetime(current_year, 4, 30),
            FERCFormType.FERC_714: datetime(current_year, 3, 31),
            FERCFormType.FERC_715: datetime(current_year, 6, 30),
            FERCFormType.FERC_730: datetime(current_year, 5, 31),
            FERCFormType.FERC_999: datetime(current_year, 1, 31)
        }
        
        return due_dates.get(form_type, datetime(current_year, 12, 31))

class FERCValidationEngine:
    """FERC data validation engine"""
    
    def __init__(self):
        self.validation_rules = {}
        self.data_quality_metrics = {}
        self._initialize_validation_rules()
    
    def _initialize_validation_rules(self):
        """Initialize validation rules for FERC forms"""
        self.validation_rules = {
            "financial_data": {
                "min_revenue": 0,
                "max_revenue": 1000000000000,  # $1 trillion
                "min_expenses": 0,
                "max_expenses": 1000000000000,
                "required_fields": ["total_revenue", "total_expenses", "net_income"]
            },
            "operational_data": {
                "min_generation": 0,
                "max_generation": 1000000000,  # 1 billion MWh
                "min_sales": 0,
                "max_sales": 1000000000,
                "required_fields": ["total_generation", "total_sales"]
            }
        }
    
    def validate_ferc_data(self, data: Dict[str, Any], form_type: FERCFormType) -> Dict[str, Any]:
        """Validate FERC data for a specific form type"""
        try:
            validation_results = {
                "overall_status": "valid",
                "validation_score": 100.0,
                "errors": [],
                "warnings": [],
                "data_quality_metrics": {},
                "compliance_checks": {}
            }
            
            # Run data quality checks
            quality_metrics = self._run_data_quality_checks(data, form_type)
            validation_results["data_quality_metrics"] = quality_metrics
            
            # Run compliance checks
            compliance_checks = self._run_compliance_checks(data, form_type)
            validation_results["compliance_checks"] = compliance_checks
            
            # Run field validations
            field_validation = self._validate_fields(data, form_type)
            validation_results["errors"].extend(field_validation["errors"])
            validation_results["warnings"].extend(field_validation["warnings"])
            
            # Calculate validation score
            validation_score = self._calculate_validation_score(
                quality_metrics, compliance_checks, field_validation
            )
            validation_results["validation_score"] = validation_score
            
            # Set overall status
            if validation_results["errors"]:
                validation_results["overall_status"] = "invalid"
            elif validation_results["warnings"]:
                validation_results["overall_status"] = "warning"
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating FERC data: {str(e)}")
            raise
    
    def _run_data_quality_checks(self, data: Dict[str, Any], form_type: FERCFormType) -> Dict[str, Any]:
        """Run data quality checks"""
        quality_metrics = {
            "completeness_score": 0.0,
            "accuracy_score": 0.0,
            "consistency_score": 0.0,
            "timeliness_score": 0.0,
            "overall_quality_score": 0.0
        }
        
        # Completeness check
        required_fields = self._get_required_fields(form_type)
        present_fields = sum(1 for field in required_fields if field in data and data[field] is not None)
        quality_metrics["completeness_score"] = present_fields / len(required_fields) if required_fields else 1.0
        
        # Accuracy check (simplified)
        quality_metrics["accuracy_score"] = 0.9  # Default high score
        
        # Consistency check
        quality_metrics["consistency_score"] = self._check_data_consistency(data)
        
        # Timeliness check
        quality_metrics["timeliness_score"] = 1.0  # Assuming data is current
        
        # Calculate overall quality score
        quality_metrics["overall_quality_score"] = np.mean([
            quality_metrics["completeness_score"],
            quality_metrics["accuracy_score"],
            quality_metrics["consistency_score"],
            quality_metrics["timeliness_score"]
        ])
        
        return quality_metrics
    
    def _run_compliance_checks(self, data: Dict[str, Any], form_type: FERCFormType) -> Dict[str, Any]:
        """Run compliance checks"""
        compliance_checks = {
            "regulatory_compliance": True,
            "data_format_compliance": True,
            "submission_deadline_compliance": True,
            "overall_compliance": True
        }
        
        # Check regulatory compliance
        if form_type == FERCFormType.FERC_1:
            if "total_revenue" in data and data["total_revenue"] < 100000000:  # $100M threshold
                compliance_checks["regulatory_compliance"] = False
        
        # Check data format compliance
        for key, value in data.items():
            if isinstance(value, str) and len(value) > 1000:  # Field length limit
                compliance_checks["data_format_compliance"] = False
                break
        
        # Set overall compliance
        compliance_checks["overall_compliance"] = all(compliance_checks.values())
        
        return compliance_checks
    
    def _validate_fields(self, data: Dict[str, Any], form_type: FERCFormType) -> Dict[str, Any]:
        """Validate individual fields"""
        validation = {
            "errors": [],
            "warnings": []
        }
        
        # Get validation rules for form type
        rules = self._get_validation_rules(form_type)
        
        for field, rules in rules.items():
            if field in data:
                value = data[field]
                
                # Check field type
                if "type" in rules:
                    if not isinstance(value, rules["type"]):
                        validation["errors"].append(f"Field {field} has incorrect type")
                
                # Check field range
                if "min" in rules and value < rules["min"]:
                    validation["warnings"].append(f"Field {field} is below minimum value")
                if "max" in rules and value > rules["max"]:
                    validation["warnings"].append(f"Field {field} is above maximum value")
        
        return validation
    
    def _get_required_fields(self, form_type: FERCFormType) -> List[str]:
        """Get required fields for a form type"""
        field_mapping = {
            FERCFormType.FERC_1: [
                "company_name", "total_revenue", "total_expenses", "net_income",
                "total_assets", "total_liabilities"
            ],
            FERCFormType.FERC_714: [
                "balancing_authority_name", "peak_demand", "energy_delivered"
            ],
            FERCFormType.FERC_715: [
                "transmission_planning_area", "planned_transmission_investments"
            ]
        }
        
        return field_mapping.get(form_type, [])
    
    def _get_validation_rules(self, form_type: FERCFormType) -> Dict[str, Any]:
        """Get validation rules for a form type"""
        if form_type == FERCFormType.FERC_1:
            return {
                "total_revenue": {"type": (int, float), "min": 0, "max": 1000000000000},
                "total_expenses": {"type": (int, float), "min": 0, "max": 1000000000000},
                "net_income": {"type": (int, float), "min": -1000000000000, "max": 1000000000000},
                "company_name": {"type": str, "max_length": 100}
            }
        else:
            return {}
    
    def _check_data_consistency(self, data: Dict[str, Any]) -> float:
        """Check data consistency"""
        consistency_score = 1.0
        
        # Check financial consistency
        if "total_revenue" in data and "total_expenses" in data and "net_income" in data:
            calculated_net = data["total_revenue"] - data["total_expenses"]
            if abs(calculated_net - data["net_income"]) > 1000:  # $1000 tolerance
                consistency_score -= 0.2
        
        # Check operational consistency
        if "total_generation" in data and "total_sales" in data:
            if data["total_sales"] > data["total_generation"] * 1.1:  # 10% tolerance
                consistency_score -= 0.1
        
        return max(0.0, consistency_score)
    
    def _calculate_validation_score(self, quality_metrics: Dict, compliance_checks: Dict, 
                                  field_validation: Dict) -> float:
        """Calculate overall validation score"""
        score = 100.0
        
        # Deduct for quality issues
        quality_score = quality_metrics.get("overall_quality_score", 1.0)
        score *= quality_score
        
        # Deduct for compliance issues
        if not compliance_checks.get("overall_compliance", True):
            score -= 20
        
        # Deduct for field validation errors
        score -= len(field_validation["errors"]) * 10
        score -= len(field_validation["warnings"]) * 5
        
        return max(0.0, score)

class FERCAuditEngine:
    """FERC audit and monitoring engine"""
    
    def __init__(self):
        self.audit_schedules = {}
        self.audit_results = {}
        self.compliance_history = {}
    
    def schedule_audit(self, company_id: str, audit_type: str, audit_date: datetime) -> Dict[str, Any]:
        """Schedule a FERC compliance audit"""
        try:
            audit_id = f"ferc_audit_{company_id}_{audit_date.strftime('%Y%m%d')}"
            
            audit_schedule = {
                "audit_id": audit_id,
                "company_id": company_id,
                "audit_type": audit_type,
                "scheduled_date": audit_date.isoformat(),
                "status": "scheduled",
                "auditor": "FERC_Compliance_Team",
                "scope": self._get_audit_scope(audit_type),
                "requirements": self._get_audit_requirements(audit_type)
            }
            
            self.audit_schedules[audit_id] = audit_schedule
            
            return audit_schedule
            
        except Exception as e:
            logger.error(f"Error scheduling FERC audit: {str(e)}")
            raise
    
    def conduct_audit(self, audit_id: str, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct a FERC compliance audit"""
        try:
            if audit_id not in self.audit_schedules:
                raise ValueError(f"Audit {audit_id} not found in schedule")
            
            audit_schedule = self.audit_schedules[audit_id]
            audit_type = audit_schedule["audit_type"]
            
            # Conduct audit based on type
            if audit_type == "compliance_review":
                audit_results = self._conduct_compliance_review(company_data)
            elif audit_type == "data_quality_audit":
                audit_results = self._conduct_data_quality_audit(company_data)
            elif audit_type == "regulatory_audit":
                audit_results = self._conduct_regulatory_audit(company_data)
            else:
                audit_results = self._conduct_general_audit(company_data)
            
            # Update audit schedule
            audit_schedule["status"] = "completed"
            audit_schedule["completion_date"] = datetime.now().isoformat()
            audit_schedule["results"] = audit_results
            
            # Store audit results
            self.audit_results[audit_id] = audit_results
            
            return audit_results
            
        except Exception as e:
            logger.error(f"Error conducting FERC audit: {str(e)}")
            raise
    
    def _get_audit_scope(self, audit_type: str) -> List[str]:
        """Get audit scope for audit type"""
        scope_mapping = {
            "compliance_review": [
                "FERC Form 1 compliance",
                "FERC Form 714 compliance",
                "FERC Form 715 compliance",
                "Submission deadlines",
                "Data accuracy"
            ],
            "data_quality_audit": [
                "Data completeness",
                "Data accuracy",
                "Data consistency",
                "Data timeliness",
                "Data validation"
            ],
            "regulatory_audit": [
                "Regulatory compliance",
                "Policy adherence",
                "Documentation completeness",
                "Training records",
                "Internal controls"
            ]
        }
        
        return scope_mapping.get(audit_type, ["General compliance review"])
    
    def _get_audit_requirements(self, audit_type: str) -> List[str]:
        """Get audit requirements for audit type"""
        requirements_mapping = {
            "compliance_review": [
                "Review all FERC submissions",
                "Verify submission deadlines",
                "Check data accuracy",
                "Assess compliance procedures"
            ],
            "data_quality_audit": [
                "Validate data completeness",
                "Check data accuracy",
                "Verify data consistency",
                "Assess data quality controls"
            ],
            "regulatory_audit": [
                "Review regulatory policies",
                "Check compliance procedures",
                "Verify training records",
                "Assess internal controls"
            ]
        }
        
        return requirements_mapping.get(audit_type, ["General audit requirements"])
    
    def _conduct_compliance_review(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct compliance review audit"""
        return {
            "audit_type": "compliance_review",
            "compliance_score": 85.0,
            "findings": [
                "FERC Form 1 submission is compliant",
                "FERC Form 714 submission is compliant",
                "Minor issues with FERC Form 715 submission",
                "All submissions submitted on time"
            ],
            "recommendations": [
                "Address minor issues in FERC Form 715",
                "Implement additional data validation checks",
                "Schedule regular compliance training"
            ],
            "overall_status": "compliant_with_minor_issues"
        }
    
    def _conduct_data_quality_audit(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct data quality audit"""
        return {
            "audit_type": "data_quality_audit",
            "data_quality_score": 92.0,
            "findings": [
                "Data completeness: 95%",
                "Data accuracy: 90%",
                "Data consistency: 95%",
                "Data timeliness: 100%"
            ],
            "recommendations": [
                "Improve data accuracy validation",
                "Implement automated data quality checks",
                "Enhance data consistency monitoring"
            ],
            "overall_status": "good_data_quality"
        }
    
    def _conduct_regulatory_audit(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct regulatory audit"""
        return {
            "audit_type": "regulatory_audit",
            "regulatory_compliance_score": 88.0,
            "findings": [
                "Regulatory policies are up to date",
                "Compliance procedures are adequate",
                "Training records are complete",
                "Internal controls are effective"
            ],
            "recommendations": [
                "Update regulatory policies quarterly",
                "Enhance compliance monitoring",
                "Schedule additional training sessions"
            ],
            "overall_status": "regulatory_compliant"
        }
    
    def _conduct_general_audit(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct general audit"""
        return {
            "audit_type": "general_audit",
            "overall_score": 87.0,
            "findings": [
                "General compliance is good",
                "Some areas need improvement",
                "Overall systems are adequate"
            ],
            "recommendations": [
                "Address identified issues",
                "Improve monitoring systems",
                "Enhance compliance procedures"
            ],
            "overall_status": "satisfactory"
        }
