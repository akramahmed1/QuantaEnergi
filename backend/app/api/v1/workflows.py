from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from ...services.workflow_manager import workflow_manager, WorkflowStatus, ApprovalType, DocumentType
from ...core.security import get_current_active_user
from ...models.user import User

router = APIRouter()

class CreateWorkflowInstanceRequest(BaseModel):
    workflow_template: str = Field(..., example="trade_approval_workflow", description="Workflow template name")
    context_data: Dict[str, Any] = Field(..., example={"trade_id": "TRD-2024-001", "amount": 1000000.0, "counterparty": "GlobalOilCorp"})
    initiated_by: str = Field(..., example="user_id_123", description="User who initiated the workflow")

class ApproveWorkflowStepRequest(BaseModel):
    approval_id: str = Field(..., example="APR-abc123", description="Approval request ID")
    approved_by: str = Field(..., example="user_id_456", description="User who approved")
    approval_notes: Optional[str] = Field(None, example="Approved after risk assessment review", description="Optional approval notes")

class RejectWorkflowStepRequest(BaseModel):
    approval_id: str = Field(..., example="APR-abc123", description="Approval request ID")
    rejected_by: str = Field(..., example="user_id_456", description="User who rejected")
    rejection_reason: str = Field(..., example="Insufficient documentation provided", description="Reason for rejection")

class UploadDocumentRequest(BaseModel):
    workflow_instance_id: str = Field(..., example="WF-abc123", description="Workflow instance ID")
    document_type: str = Field(..., example="contract", description="Type of document")
    filename: str = Field(..., example="contract_2024_001.pdf", description="Document filename")
    content_type: str = Field(..., example="application/pdf", description="Document content type")
    file_size: int = Field(..., example=1024000, description="File size in bytes")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, example={"contract_type": "futures", "expiry_date": "2024-12-31"})

@router.post("/workflows/approve", summary="Create a new workflow instance")
async def create_workflow_instance_endpoint(
    request: CreateWorkflowInstanceRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Creates a new workflow instance based on a template.
    Requires 'workflows:write' permission.
    """
    # TODO: Add permission check for current_user
    try:
        result = await workflow_manager.create_workflow_instance(
            request.workflow_template,
            request.context_data,
            request.initiated_by
        )
        return {"message": "Workflow instance created successfully", "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/workflows/approve/step", summary="Approve a workflow step")
async def approve_workflow_step_endpoint(
    request: ApproveWorkflowStepRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Approves a pending workflow step.
    Requires 'workflows:approve' permission.
    """
    # TODO: Add permission check for current_user
    try:
        result = await workflow_manager.approve_workflow_step(
            request.approval_id,
            request.approved_by,
            request.approval_notes
        )
        return {"message": "Workflow step approved successfully", "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/workflows/reject/step", summary="Reject a workflow step")
async def reject_workflow_step_endpoint(
    request: RejectWorkflowStepRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Rejects a pending workflow step.
    Requires 'workflows:approve' permission.
    """
    # TODO: Add permission check for current_user
    try:
        result = await workflow_manager.reject_workflow_step(
            request.approval_id,
            request.rejected_by,
            request.rejection_reason
        )
        return {"message": "Workflow step rejected successfully", "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/workflows/instance/{instance_id}", summary="Get workflow instance details")
async def get_workflow_instance_endpoint(
    instance_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieves details of a specific workflow instance.
    Requires 'workflows:read' permission.
    """
    # TODO: Add permission check for current_user
    try:
        result = await workflow_manager.get_workflow_instance(instance_id)
        return {"message": "Workflow instance retrieved successfully", "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/workflows/approvals/pending", summary="Get pending approvals")
async def get_pending_approvals_endpoint(
    approver_role: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieves list of pending approvals, optionally filtered by approver role.
    Requires 'workflows:read' permission.
    """
    # TODO: Add permission check for current_user
    try:
        result = await workflow_manager.get_pending_approvals(approver_role)
        return {"message": "Pending approvals retrieved successfully", "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/workflows/documents/upload", summary="Upload document to workflow")
async def upload_document_endpoint(
    request: UploadDocumentRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Uploads a document to a workflow instance.
    Requires 'workflows:write' permission.
    """
    # TODO: Add permission check for current_user
    try:
        document_data = {
            "document_type": request.document_type,
            "filename": request.filename,
            "content_type": request.content_type,
            "file_size": request.file_size,
            "metadata": request.metadata
        }
        
        result = await workflow_manager.upload_document(
            request.workflow_instance_id,
            document_data,
            current_user.id  # Use current user as uploader
        )
        return {"message": "Document uploaded successfully", "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/workflows/analytics", summary="Get workflow analytics")
async def get_workflow_analytics_endpoint(
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieves analytics and performance metrics for workflow operations.
    Requires 'workflows:admin' permission.
    """
    # TODO: Add permission check for current_user
    try:
        result = await workflow_manager.get_workflow_analytics()
        return {"message": "Workflow analytics retrieved successfully", "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/workflows/templates", summary="Get available workflow templates")
async def get_workflow_templates_endpoint(
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieves list of available workflow templates.
    Requires 'workflows:read' permission.
    """
    # TODO: Add permission check for current_user
    try:
        templates = workflow_manager.workflow_templates
        return {"message": "Workflow templates retrieved successfully", "data": {"templates": templates}}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/workflows/status/{status}", summary="Get workflows by status")
async def get_workflows_by_status_endpoint(
    status: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieves workflow instances filtered by status.
    Requires 'workflows:read' permission.
    """
    # TODO: Add permission check for current_user
    try:
        workflows = []
        for instance_id, instance in workflow_manager.workflow_instances.items():
            if instance["status"] == status:
                workflows.append(instance)
        
        return {"message": f"Workflows with status '{status}' retrieved successfully", "data": {"workflows": workflows}}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/workflows/user/{user_id}", summary="Get workflows initiated by user")
async def get_workflows_by_user_endpoint(
    user_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieves workflow instances initiated by a specific user.
    Requires 'workflows:read' permission.
    """
    # TODO: Add permission check for current_user
    try:
        workflows = []
        for instance_id, instance in workflow_manager.workflow_instances.items():
            if instance["initiated_by"] == user_id:
                workflows.append(instance)
        
        return {"message": f"Workflows for user '{user_id}' retrieved successfully", "data": {"workflows": workflows}}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
