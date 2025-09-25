"""
Report Builder Service for ETRM/CTRM Trading
Handles custom templates (FERC/REMIT), automated generation via Pandas, and export capabilities
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
import pandas as pd
import json
import io
import base64
from enum import Enum
from fastapi import HTTPException
import uuid

logger = logging.getLogger(__name__)

class ReportType(Enum):
    """Report type enumeration"""
    FERC = "ferc"
    REMIT = "remit"
    TRADE_SUMMARY = "trade_summary"
    RISK_REPORT = "risk_report"
    COMPLIANCE_REPORT = "compliance_report"
    SETTLEMENT_REPORT = "settlement_report"
    CUSTOM = "custom"

class ReportFormat(Enum):
    """Report format enumeration"""
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"
    HTML = "html"

class ReportBuilderService:
    """
    Service for building custom reports with templates and automated generation
    Supports FERC/REMIT compliance reporting and custom templates
    """
    
    def __init__(self):
        # Report templates
        self.report_templates = {}
        self.generated_reports = {}
        self.report_counter = 1000
        
        # Initialize standard templates
        self._initialize_report_templates()
    
    def _initialize_report_templates(self):
        """Initialize standard report templates"""
        
        # FERC Template
        self.report_templates[ReportType.FERC.value] = {
            "name": "FERC Compliance Report",
            "description": "Federal Energy Regulatory Commission compliance reporting",
            "sections": [
                {
                    "id": "executive_summary",
                    "title": "Executive Summary",
                    "fields": ["total_trades", "total_volume", "total_value", "compliance_status"]
                },
                {
                    "id": "trade_details",
                    "title": "Trade Details",
                    "fields": ["trade_id", "commodity", "quantity", "price", "counterparty", "delivery_date", "status"]
                },
                {
                    "id": "risk_metrics",
                    "title": "Risk Metrics",
                    "fields": ["var_95", "var_99", "expected_shortfall", "stress_test_results"]
                },
                {
                    "id": "regulatory_compliance",
                    "title": "Regulatory Compliance",
                    "fields": ["ferc_compliance", "reporting_accuracy", "audit_trail"]
                }
            ],
            "formatting": {
                "header_style": "bold",
                "table_style": "grid",
                "font_size": 12,
                "margins": {"top": 1, "bottom": 1, "left": 1, "right": 1}
            }
        }
        
        # REMIT Template
        self.report_templates[ReportType.REMIT.value] = {
            "name": "REMIT Compliance Report",
            "description": "Regulation on Energy Market Integrity and Transparency reporting",
            "sections": [
                {
                    "id": "market_participant_info",
                    "title": "Market Participant Information",
                    "fields": ["participant_id", "name", "registration_status", "contact_info"]
                },
                {
                    "id": "transaction_reporting",
                    "title": "Transaction Reporting",
                    "fields": ["transaction_id", "market", "product", "quantity", "price", "timestamp"]
                },
                {
                    "id": "fundamental_data",
                    "title": "Fundamental Data",
                    "fields": ["facility_id", "generation_capacity", "outage_info", "forecast_data"]
                },
                {
                    "id": "inside_information",
                    "title": "Inside Information",
                    "fields": ["information_type", "disclosure_time", "recipients", "market_impact"]
                }
            ],
            "formatting": {
                "header_style": "bold",
                "table_style": "striped",
                "font_size": 11,
                "margins": {"top": 0.8, "bottom": 0.8, "left": 0.8, "right": 0.8}
            }
        }
        
        # Trade Summary Template
        self.report_templates[ReportType.TRADE_SUMMARY.value] = {
            "name": "Trade Summary Report",
            "description": "Comprehensive trade activity summary",
            "sections": [
                {
                    "id": "summary_metrics",
                    "title": "Summary Metrics",
                    "fields": ["total_trades", "total_volume", "total_value", "average_price", "top_commodities"]
                },
                {
                    "id": "performance_analysis",
                    "title": "Performance Analysis",
                    "fields": ["pnl_summary", "risk_metrics", "compliance_score", "efficiency_metrics"]
                },
                {
                    "id": "market_analysis",
                    "title": "Market Analysis",
                    "fields": ["price_trends", "volume_analysis", "market_share", "competitive_position"]
                }
            ],
            "formatting": {
                "header_style": "bold",
                "table_style": "modern",
                "font_size": 12,
                "margins": {"top": 1, "bottom": 1, "left": 1, "right": 1}
            }
        }
    
    async def build_report(
        self, 
        report_type: str, 
        data: Dict[str, Any], 
        template_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Build a report using specified template and data
        
        Args:
            report_type: Type of report to build (ferc, remit, trade_summary, etc.)
            data: Data to populate the report
            template_config: Optional custom template configuration
            
        Returns:
            Dict with generated report details
        """
        try:
            logger.info(f"Building report of type: {report_type}")
            
            # Validate report type
            if report_type not in [rt.value for rt in ReportType]:
                raise HTTPException(status_code=400, detail=f"Invalid report type: {report_type}")
            
            # Get template
            template = self.report_templates.get(report_type, {})
            if not template:
                raise HTTPException(status_code=404, detail=f"Template not found for report type: {report_type}")
            
            # Apply custom template configuration if provided
            if template_config:
                template = self._merge_template_config(template, template_config)
            
            # Generate report ID
            report_id = str(uuid.uuid4())
            self.report_counter += 1
            
            # Build report sections
            report_sections = self._build_report_sections(template, data)
            
            # Create report metadata
            report_metadata = {
                "report_id": report_id,
                "report_type": report_type,
                "template_name": template["name"],
                "generated_at": datetime.now().isoformat(),
                "generated_by": data.get("generated_by", "system"),
                "data_period": data.get("data_period", {}),
                "sections_count": len(report_sections),
                "total_pages": self._calculate_total_pages(report_sections),
                "status": "completed"
            }
            
            # Create report content
            report_content = {
                "metadata": report_metadata,
                "sections": report_sections,
                "template": template,
                "data_summary": self._create_data_summary(data)
            }
            
            # Store generated report
            self.generated_reports[report_id] = report_content
            
            logger.info(f"Report built successfully: {report_id}")
            
            return {
                "success": True,
                "report_id": report_id,
                "report_metadata": report_metadata,
                "report_content": report_content
            }
            
        except Exception as e:
            logger.error(f"Report building failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def _build_report_sections(self, template: Dict[str, Any], data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build report sections from template and data"""
        
        sections = []
        
        for section_template in template.get("sections", []):
            section_id = section_template["id"]
            section_title = section_template["title"]
            section_fields = section_template["fields"]
            
            # Extract section data
            section_data = self._extract_section_data(data, section_fields)
            
            # Create section content
            section = {
                "id": section_id,
                "title": section_title,
                "fields": section_fields,
                "data": section_data,
                "formatting": self._apply_section_formatting(section_template, section_data)
            }
            
            sections.append(section)
        
        return sections
    
    def _extract_section_data(self, data: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
        """Extract relevant data for a report section"""
        
        section_data = {}
        
        for field in fields:
            if field in data:
                section_data[field] = data[field]
            else:
                # Try to find field in nested data
                section_data[field] = self._find_field_in_data(data, field)
        
        return section_data
    
    def _find_field_in_data(self, data: Dict[str, Any], field: str) -> Any:
        """Find field in nested data structure"""
        
        # Common field mappings
        field_mappings = {
            "total_trades": lambda d: len(d.get("trades", [])),
            "total_volume": lambda d: sum(trade.get("quantity", 0) for trade in d.get("trades", [])),
            "total_value": lambda d: sum(trade.get("quantity", 0) * trade.get("price", 0) for trade in d.get("trades", [])),
            "average_price": lambda d: self._calculate_average_price(d.get("trades", [])),
            "compliance_status": lambda d: d.get("compliance", {}).get("status", "unknown")
        }
        
        if field in field_mappings:
            try:
                return field_mappings[field](data)
            except Exception:
                return "N/A"
        
        # Try direct access
        return data.get(field, "N/A")
    
    def _calculate_average_price(self, trades: List[Dict[str, Any]]) -> float:
        """Calculate average price from trades"""
        if not trades:
            return 0.0
        
        total_value = sum(trade.get("quantity", 0) * trade.get("price", 0) for trade in trades)
        total_quantity = sum(trade.get("quantity", 0) for trade in trades)
        
        return total_value / total_quantity if total_quantity > 0 else 0.0
    
    def _apply_section_formatting(self, section_template: Dict[str, Any], section_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply formatting to section data"""
        
        formatting = {
            "table_headers": section_template.get("fields", []),
            "data_rows": self._format_data_rows(section_data),
            "summary_stats": self._calculate_summary_stats(section_data),
            "charts": self._generate_chart_data(section_data)
        }
        
        return formatting
    
    def _format_data_rows(self, section_data: Dict[str, Any]) -> List[List[str]]:
        """Format section data into table rows"""
        
        rows = []
        
        # Handle different data types
        for key, value in section_data.items():
            if isinstance(value, list):
                # Handle list data (e.g., trades)
                for item in value:
                    if isinstance(item, dict):
                        row = [str(item.get(field, "")) for field in ["trade_id", "commodity", "quantity", "price"]]
                        rows.append(row)
            elif isinstance(value, dict):
                # Handle dict data
                row = [key, str(value)]
                rows.append(row)
            else:
                # Handle simple values
                row = [key, str(value)]
                rows.append(row)
        
        return rows
    
    def _calculate_summary_stats(self, section_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate summary statistics for section data"""
        
        stats = {}
        
        # Calculate basic statistics
        numeric_values = []
        for key, value in section_data.items():
            if isinstance(value, (int, float)):
                numeric_values.append(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        for v in item.values():
                            if isinstance(v, (int, float)):
                                numeric_values.append(v)
        
        if numeric_values:
            stats = {
                "count": len(numeric_values),
                "sum": sum(numeric_values),
                "average": sum(numeric_values) / len(numeric_values),
                "min": min(numeric_values),
                "max": max(numeric_values)
            }
        
        return stats
    
    def _generate_chart_data(self, section_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate chart data for visualization"""
        
        charts = []
        
        # Generate pie chart for categorical data
        categorical_data = {}
        for key, value in section_data.items():
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) and "commodity" in item:
                        commodity = item["commodity"]
                        categorical_data[commodity] = categorical_data.get(commodity, 0) + 1
        
        if categorical_data:
            charts.append({
                "type": "pie",
                "title": "Commodity Distribution",
                "data": [{"name": k, "value": v} for k, v in categorical_data.items()]
            })
        
        # Generate line chart for time series data
        time_series_data = {}
        for key, value in section_data.items():
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) and "date" in item:
                        date = item["date"]
                        price = item.get("price", 0)
                        if date not in time_series_data:
                            time_series_data[date] = []
                        time_series_data[date].append(price)
        
        if time_series_data:
            chart_data = []
            for date, prices in time_series_data.items():
                chart_data.append({
                    "date": date,
                    "average_price": sum(prices) / len(prices)
                })
            
            charts.append({
                "type": "line",
                "title": "Price Trend",
                "data": sorted(chart_data, key=lambda x: x["date"])
            })
        
        return charts
    
    def _merge_template_config(self, template: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge custom template configuration with base template"""
        
        merged_template = template.copy()
        
        # Merge sections
        if "sections" in config:
            merged_template["sections"] = config["sections"]
        
        # Merge formatting
        if "formatting" in config:
            merged_template["formatting"].update(config["formatting"])
        
        return merged_template
    
    def _create_data_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create summary of input data"""
        
        summary = {
            "total_records": 0,
            "data_types": {},
            "date_range": {},
            "field_count": len(data)
        }
        
        # Count records
        for key, value in data.items():
            if isinstance(value, list):
                summary["total_records"] += len(value)
                summary["data_types"][key] = f"list({len(value)} items)"
            elif isinstance(value, dict):
                summary["data_types"][key] = "object"
            else:
                summary["data_types"][key] = type(value).__name__
        
        return summary
    
    def _calculate_total_pages(self, sections: List[Dict[str, Any]]) -> int:
        """Calculate total pages for the report"""
        
        total_pages = 1  # Cover page
        
        for section in sections:
            # Estimate pages per section based on data volume
            data_count = len(section.get("data", {}))
            estimated_pages = max(1, (data_count // 20) + 1)  # 20 items per page
            total_pages += estimated_pages
        
        return total_pages
    
    async def export_report(
        self, 
        report_id: str, 
        export_format: str, 
        export_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Export report in specified format
        
        Args:
            report_id: Report identifier
            export_format: Export format (pdf, excel, csv, json, html)
            export_options: Optional export configuration
            
        Returns:
            Dict with export details and file data
        """
        try:
            if report_id not in self.generated_reports:
                raise HTTPException(status_code=404, detail="Report not found")
            
            report_content = self.generated_reports[report_id]
            
            logger.info(f"Exporting report {report_id} in format: {export_format}")
            
            # Generate export based on format
            if export_format == ReportFormat.PDF.value:
                export_data = self._export_to_pdf(report_content, export_options)
            elif export_format == ReportFormat.EXCEL.value:
                export_data = self._export_to_excel(report_content, export_options)
            elif export_format == ReportFormat.CSV.value:
                export_data = self._export_to_csv(report_content, export_options)
            elif export_format == ReportFormat.JSON.value:
                export_data = self._export_to_json(report_content, export_options)
            elif export_format == ReportFormat.HTML.value:
                export_data = self._export_to_html(report_content, export_options)
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported export format: {export_format}")
            
            return {
                "success": True,
                "report_id": report_id,
                "export_format": export_format,
                "export_data": export_data,
                "exported_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Report export failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def _export_to_pdf(self, report_content: Dict[str, Any], options: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Export report to PDF format"""
        
        # Mock PDF generation (in production, use libraries like ReportLab or WeasyPrint)
        pdf_content = self._generate_pdf_content(report_content)
        
        return {
            "content_type": "application/pdf",
            "content": base64.b64encode(pdf_content.encode()).decode(),
            "filename": f"report_{report_content['metadata']['report_id']}.pdf",
            "size_bytes": len(pdf_content)
        }
    
    def _export_to_excel(self, report_content: Dict[str, Any], options: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Export report to Excel format"""
        
        # Create Excel file using pandas
        excel_buffer = io.BytesIO()
        
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            # Write metadata sheet
            metadata_df = pd.DataFrame([report_content['metadata']])
            metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
            
            # Write sections
            for section in report_content['sections']:
                section_df = pd.DataFrame([section['data']])
                sheet_name = section['title'][:31]  # Excel sheet name limit
                section_df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        excel_content = excel_buffer.getvalue()
        
        return {
            "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "content": base64.b64encode(excel_content).decode(),
            "filename": f"report_{report_content['metadata']['report_id']}.xlsx",
            "size_bytes": len(excel_content)
        }
    
    def _export_to_csv(self, report_content: Dict[str, Any], options: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Export report to CSV format"""
        
        # Combine all sections into a single CSV
        all_data = []
        
        for section in report_content['sections']:
            section_data = section['data']
            if isinstance(section_data, dict):
                all_data.append(section_data)
        
        if all_data:
            df = pd.DataFrame(all_data)
            csv_content = df.to_csv(index=False)
        else:
            csv_content = "No data available"
        
        return {
            "content_type": "text/csv",
            "content": base64.b64encode(csv_content.encode()).decode(),
            "filename": f"report_{report_content['metadata']['report_id']}.csv",
            "size_bytes": len(csv_content)
        }
    
    def _export_to_json(self, report_content: Dict[str, Any], options: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Export report to JSON format"""
        
        json_content = json.dumps(report_content, indent=2, default=str)
        
        return {
            "content_type": "application/json",
            "content": base64.b64encode(json_content.encode()).decode(),
            "filename": f"report_{report_content['metadata']['report_id']}.json",
            "size_bytes": len(json_content)
        }
    
    def _export_to_html(self, report_content: Dict[str, Any], options: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Export report to HTML format"""
        
        html_content = self._generate_html_content(report_content)
        
        return {
            "content_type": "text/html",
            "content": base64.b64encode(html_content.encode()).decode(),
            "filename": f"report_{report_content['metadata']['report_id']}.html",
            "size_bytes": len(html_content)
        }
    
    def _generate_pdf_content(self, report_content: Dict[str, Any]) -> str:
        """Generate PDF content (mock implementation)"""
        
        # Mock PDF content generation
        pdf_content = f"""
        REPORT: {report_content['metadata']['template_name']}
        Generated: {report_content['metadata']['generated_at']}
        Report ID: {report_content['metadata']['report_id']}
        
        """
        
        for section in report_content['sections']:
            pdf_content += f"\n{section['title']}\n"
            pdf_content += "=" * len(section['title']) + "\n"
            
            for key, value in section['data'].items():
                pdf_content += f"{key}: {value}\n"
            
            pdf_content += "\n"
        
        return pdf_content
    
    def _generate_html_content(self, report_content: Dict[str, Any]) -> str:
        """Generate HTML content"""
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{report_content['metadata']['template_name']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; margin-bottom: 30px; }}
                .section {{ margin-bottom: 30px; }}
                .section-title {{ font-size: 18px; font-weight: bold; margin-bottom: 10px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{report_content['metadata']['template_name']}</h1>
                <p>Generated: {report_content['metadata']['generated_at']}</p>
                <p>Report ID: {report_content['metadata']['report_id']}</p>
            </div>
        """
        
        for section in report_content['sections']:
            html_content += f"""
            <div class="section">
                <div class="section-title">{section['title']}</div>
                <table>
                    <tr><th>Field</th><th>Value</th></tr>
            """
            
            for key, value in section['data'].items():
                html_content += f"<tr><td>{key}</td><td>{value}</td></tr>"
            
            html_content += "</table></div>"
        
        html_content += "</body></html>"
        
        return html_content
    
    async def get_report_templates(self) -> Dict[str, Any]:
        """Get available report templates"""
        
        return {
            "success": True,
            "templates": self.report_templates,
            "generated_at": datetime.now().isoformat()
        }
    
    async def get_generated_reports(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get list of generated reports with optional filters"""
        
        reports = []
        
        for report_id, report_content in self.generated_reports.items():
            metadata = report_content['metadata']
            
            # Apply filters if provided
            if filters:
                if 'report_type' in filters and metadata['report_type'] != filters['report_type']:
                    continue
                if 'date_from' in filters:
                    generated_date = datetime.fromisoformat(metadata['generated_at'])
                    if generated_date < filters['date_from']:
                        continue
                if 'date_to' in filters:
                    generated_date = datetime.fromisoformat(metadata['generated_at'])
                    if generated_date > filters['date_to']:
                        continue
            
            reports.append({
                "report_id": report_id,
                "report_type": metadata['report_type'],
                "template_name": metadata['template_name'],
                "generated_at": metadata['generated_at'],
                "generated_by": metadata['generated_by'],
                "status": metadata['status'],
                "sections_count": metadata['sections_count'],
                "total_pages": metadata['total_pages']
            })
        
        # Sort by generated date (newest first)
        reports.sort(key=lambda x: x['generated_at'], reverse=True)
        
        return {
            "success": True,
            "reports": reports,
            "total_count": len(reports),
            "generated_at": datetime.now().isoformat()
        }


# Global service instance
report_builder_service = ReportBuilderService()
