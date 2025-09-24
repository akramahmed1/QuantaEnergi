"""
Compliance Reporting Service
Provides regulatory reporting for CFTC, EMIR, GDPR, and Guyana regulations
"""

import json
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import structlog
from enum import Enum

logger = structlog.get_logger(__name__)

class ReportType(Enum):
    CFTC = "cftc"
    EMIR = "emir"
    GDPR = "gdpr"
    GUYANA = "guyana"

class ComplianceReportingService:
    """Compliance reporting service for various regulatory requirements"""
    
    def __init__(self):
        self.report_templates = self._initialize_report_templates()
        self.data_retention_periods = {
            'cftc': 5,  # years
            'emir': 7,  # years
            'gdpr': 3,  # years
            'guyana': 5  # years
        }
    
    def _initialize_report_templates(self) -> Dict:
        """Initialize report templates for different regulations"""
        return {
            'cftc': {
                'name': 'CFTC Large Trader Report',
                'frequency': 'daily',
                'fields': [
                    'trader_id', 'commodity', 'contract_month', 'position_type',
                    'long_position', 'short_position', 'net_position', 'report_date'
                ],
                'threshold': 1000000  # $1M threshold
            },
            'emir': {
                'name': 'EMIR Trade Repository Report',
                'frequency': 'daily',
                'fields': [
                    'trade_id', 'counterparty_id', 'commodity', 'notional_amount',
                    'trade_date', 'settlement_date', 'collateral_amount', 'report_date'
                ],
                'threshold': 1000000  # €1M threshold
            },
            'gdpr': {
                'name': 'GDPR Data Processing Report',
                'frequency': 'monthly',
                'fields': [
                    'data_subject_id', 'data_type', 'processing_purpose',
                    'data_controller', 'consent_status', 'retention_period', 'report_date'
                ],
                'threshold': 0  # All personal data
            },
            'guyana': {
                'name': 'Guyana Energy Sector Report',
                'frequency': 'quarterly',
                'fields': [
                    'company_id', 'energy_type', 'production_volume', 'export_volume',
                    'revenue', 'tax_paid', 'environmental_impact', 'report_date'
                ],
                'threshold': 500000  # $500K threshold
            }
        }
    
    def generate_report(self, 
                       report_type: str,
                       start_date: datetime,
                       end_date: datetime,
                       data: List[Dict],
                       anonymize: bool = True) -> Dict:
        """
        Generate compliance report for specified regulation
        
        Args:
            report_type: Type of report (cftc, emir, gdpr, guyana)
            start_date: Report start date
            end_date: Report end date
            data: Raw data to include in report
            anonymize: Whether to anonymize personal data
            
        Returns:
            Dictionary containing report data and metadata
        """
        try:
            logger.info("Generating compliance report", 
                       report_type=report_type,
                       start_date=start_date.isoformat(),
                       end_date=end_date.isoformat())
            
            if report_type not in self.report_templates:
                raise ValueError(f"Unsupported report type: {report_type}")
            
            template = self.report_templates[report_type]
            
            # Filter and process data
            filtered_data = self._filter_data_by_date(data, start_date, end_date)
            processed_data = self._process_data_for_report(filtered_data, template, anonymize)
            
            # Generate report
            report = {
                'report_id': f"{report_type.upper()}-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                'report_type': report_type,
                'report_name': template['name'],
                'generated_at': datetime.now().isoformat(),
                'report_period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'data_summary': self._generate_data_summary(processed_data, template),
                'report_data': processed_data,
                'compliance_status': self._assess_compliance_status(processed_data, template),
                'anonymized': anonymize,
                'retention_until': self._calculate_retention_date(report_type)
            }
            
            logger.info("Compliance report generated successfully", 
                       report_id=report['report_id'],
                       record_count=len(processed_data))
            
            return report
            
        except Exception as e:
            logger.error("Report generation failed", error=str(e))
            raise Exception(f"Report generation failed: {str(e)}")
    
    def _filter_data_by_date(self, data: List[Dict], start_date: datetime, end_date: datetime) -> List[Dict]:
        """Filter data by date range"""
        filtered_data = []
        
        for record in data:
            try:
                # Extract date from record (assuming 'timestamp' or 'date' field)
                record_date = None
                if 'timestamp' in record:
                    record_date = datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00'))
                elif 'date' in record:
                    record_date = datetime.fromisoformat(record['date'].replace('Z', '+00:00'))
                elif 'created_at' in record:
                    record_date = datetime.fromisoformat(record['created_at'].replace('Z', '+00:00'))
                
                if record_date and start_date <= record_date <= end_date:
                    filtered_data.append(record)
            except Exception as e:
                logger.warning("Failed to parse date from record", record=record, error=str(e))
                continue
        
        return filtered_data
    
    def _process_data_for_report(self, 
                                data: List[Dict], 
                                template: Dict, 
                                anonymize: bool) -> List[Dict]:
        """Process data according to report template and anonymization rules"""
        processed_data = []
        
        for record in data:
            try:
                processed_record = {}
                
                # Map fields according to template
                for field in template['fields']:
                    if field in record:
                        processed_record[field] = record[field]
                    else:
                        processed_record[field] = None
                
                # Add report-specific fields
                processed_record['report_date'] = datetime.now().isoformat()
                
                # Anonymize sensitive data if required
                if anonymize:
                    processed_record = self._anonymize_record(processed_record, template)
                
                processed_data.append(processed_record)
                
            except Exception as e:
                logger.warning("Failed to process record", record=record, error=str(e))
                continue
        
        return processed_data
    
    def _anonymize_record(self, record: Dict, template: Dict) -> Dict:
        """Anonymize sensitive data in record"""
        anonymized_record = record.copy()
        
        # Fields that should be anonymized
        sensitive_fields = ['trader_id', 'counterparty_id', 'data_subject_id', 'company_id']
        
        for field in sensitive_fields:
            if field in anonymized_record and anonymized_record[field]:
                # Hash the sensitive ID
                import hashlib
                original_id = str(anonymized_record[field])
                hashed_id = hashlib.sha256(original_id.encode()).hexdigest()[:8]
                anonymized_record[field] = f"ANON_{hashed_id}"
        
        return anonymized_record
    
    def _generate_data_summary(self, data: List[Dict], template: Dict) -> Dict:
        """Generate summary statistics for the report data"""
        if not data:
            return {
                'total_records': 0,
                'total_value': 0,
                'date_range': None
            }
        
        # Calculate total value if applicable
        total_value = 0
        value_fields = ['notional_amount', 'revenue', 'net_position', 'long_position', 'short_position']
        
        for record in data:
            for field in value_fields:
                if field in record and record[field] is not None:
                    try:
                        total_value += float(record[field])
                    except (ValueError, TypeError):
                        continue
        
        return {
            'total_records': len(data),
            'total_value': total_value,
            'date_range': {
                'earliest': min(record.get('report_date', '') for record in data),
                'latest': max(record.get('report_date', '') for record in data)
            },
            'threshold_exceeded': total_value > template.get('threshold', 0)
        }
    
    def _assess_compliance_status(self, data: List[Dict], template: Dict) -> Dict:
        """Assess compliance status based on data and regulations"""
        total_records = len(data)
        threshold = template.get('threshold', 0)
        
        # Check if data exceeds reporting thresholds
        exceeds_threshold = any(
            record.get('notional_amount', 0) > threshold or
            record.get('revenue', 0) > threshold or
            record.get('net_position', 0) > threshold
            for record in data
        )
        
        # Determine compliance status
        if total_records == 0:
            status = "no_data"
        elif exceeds_threshold:
            status = "reporting_required"
        else:
            status = "compliant"
        
        return {
            'status': status,
            'exceeds_threshold': exceeds_threshold,
            'total_records': total_records,
            'threshold': threshold,
            'assessment_date': datetime.now().isoformat()
        }
    
    def _calculate_retention_date(self, report_type: str) -> str:
        """Calculate data retention end date"""
        retention_years = self.data_retention_periods.get(report_type, 5)
        retention_date = datetime.now() + timedelta(days=retention_years * 365)
        return retention_date.isoformat()
    
    def export_report_csv(self, report: Dict) -> str:
        """Export report data to CSV format"""
        try:
            report_id = report['report_id']
            report_data = report['report_data']
            
            if not report_data:
                return f"# {report['report_name']}\n# No data available for the specified period"
            
            # Create CSV content
            csv_content = []
            
            # Add header
            if report_data:
                headers = list(report_data[0].keys())
                csv_content.append(','.join(headers))
                
                # Add data rows
                for record in report_data:
                    row = []
                    for header in headers:
                        value = record.get(header, '')
                        # Escape CSV values
                        if isinstance(value, str) and (',' in value or '"' in value or '\n' in value):
                            value = f'"{value.replace('"', '""')}"'
                        row.append(str(value))
                    csv_content.append(','.join(row))
            
            csv_text = '\n'.join(csv_content)
            
            logger.info("Report exported to CSV", report_id=report_id)
            return csv_text
            
        except Exception as e:
            logger.error("CSV export failed", error=str(e))
            raise Exception(f"CSV export failed: {str(e)}")
    
    def generate_consolidated_report(self, 
                                   report_types: List[str],
                                   start_date: datetime,
                                   end_date: datetime,
                                   data: List[Dict]) -> Dict:
        """Generate consolidated report for multiple regulations"""
        try:
            logger.info("Generating consolidated compliance report", 
                       report_types=report_types)
            
            consolidated_report = {
                'consolidated_report_id': f"CONSOLIDATED-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                'generated_at': datetime.now().isoformat(),
                'report_period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'individual_reports': {},
                'overall_compliance_status': 'compliant',
                'summary': {
                    'total_regulations': len(report_types),
                    'total_records': len(data),
                    'compliance_issues': []
                }
            }
            
            # Generate individual reports
            for report_type in report_types:
                try:
                    individual_report = self.generate_report(
                        report_type, start_date, end_date, data, anonymize=True
                    )
                    consolidated_report['individual_reports'][report_type] = individual_report
                    
                    # Check for compliance issues
                    if individual_report['compliance_status']['status'] != 'compliant':
                        consolidated_report['summary']['compliance_issues'].append({
                            'regulation': report_type.upper(),
                            'issue': individual_report['compliance_status']['status']
                        })
                        consolidated_report['overall_compliance_status'] = 'requires_attention'
                        
                except Exception as e:
                    logger.warning("Failed to generate individual report", 
                                 report_type=report_type, error=str(e))
                    consolidated_report['summary']['compliance_issues'].append({
                        'regulation': report_type.upper(),
                        'issue': f'Report generation failed: {str(e)}'
                    })
                    consolidated_report['overall_compliance_status'] = 'error'
            
            logger.info("Consolidated report generated", 
                       report_id=consolidated_report['consolidated_report_id'])
            
            return consolidated_report
            
        except Exception as e:
            logger.error("Consolidated report generation failed", error=str(e))
            raise Exception(f"Consolidated report generation failed: {str(e)}")

# Global instance
compliance_reporting_service = ComplianceReportingService()
