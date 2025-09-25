"""
Reports API endpoints for custom report generation and export
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from ...services.report_builder import report_builder_service
from ...core.security import get_current_user
from ...schemas.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["reports"])

@router.post("/build")
async def build_report(
    report_type: str,
    data: Dict[str, Any],
    template_config: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Build a report using specified template and data
    
    Args:
        report_type: Type of report to build (ferc, remit, trade_summary, etc.)
        data: Data to populate the report
        template_config: Optional custom template configuration
        current_user: Current authenticated user
        
    Returns:
        Dict with generated report details
    """
    try:
        data["generated_by"] = current_user.id
        result = await report_builder_service.build_report(report_type, data, template_config)
        logger.info(f"Report built by user {current_user.id}: {result['report_id']}")
        return result
    except Exception as e:
        logger.error(f"Failed to build report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{report_id}/export")
async def export_report(
    report_id: str,
    export_format: str,
    export_options: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Export report in specified format
    
    Args:
        report_id: Report identifier
        export_format: Export format (pdf, excel, csv, json, html)
        export_options: Optional export configuration
        current_user: Current authenticated user
        
    Returns:
        Dict with export details and file data
    """
    try:
        result = await report_builder_service.export_report(report_id, export_format, export_options)
        logger.info(f"Report exported by user {current_user.id}: {report_id} in {export_format}")
        return result
    except Exception as e:
        logger.error(f"Failed to export report {report_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/templates")
async def get_report_templates(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get available report templates
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Dict with available templates
    """
    try:
        result = await report_builder_service.get_report_templates()
        return result
    except Exception as e:
        logger.error(f"Failed to get report templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/")
async def get_generated_reports(
    report_type: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get list of generated reports with optional filters
    
    Args:
        report_type: Filter by report type
        date_from: Filter from date (ISO format)
        date_to: Filter to date (ISO format)
        current_user: Current authenticated user
        
    Returns:
        Dict with list of generated reports
    """
    try:
        filters = {}
        
        if report_type:
            filters['report_type'] = report_type
        if date_from:
            filters['date_from'] = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
        if date_to:
            filters['date_to'] = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
        
        result = await report_builder_service.get_generated_reports(filters)
        return result
    except Exception as e:
        logger.error(f"Failed to get generated reports: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{report_id}")
async def get_report_details(
    report_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get detailed information about a specific report
    
    Args:
        report_id: Report identifier
        current_user: Current authenticated user
        
    Returns:
        Dict with report details
    """
    try:
        if report_id not in report_builder_service.generated_reports:
            raise HTTPException(status_code=404, detail="Report not found")
        
        report_content = report_builder_service.generated_reports[report_id]
        
        return {
            "success": True,
            "report_content": report_content
        }
    except Exception as e:
        logger.error(f"Failed to get report details {report_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
