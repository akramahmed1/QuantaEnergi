"""
Workflow Manager Service for ETRM/CTRM Trading
Handles approvals, document management (BPMN-lite), and SendGrid email integration
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
import asyncio
import uuid
import json
from enum import Enum
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    """Workflow status enumeration"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ApprovalType(Enum):
    """Approval type enumeration"""
    TRADE_APPROVAL = "trade_approval"
    CREDIT_LIMIT = "credit_limit"
    RISK_REVIEW = "risk_review"
    COMPLIANCE_CHECK = "compliance_check"
    DOCUMENT_REVIEW = "document_review"
    SETTLEMENT_APPROVAL = "settlement_approval"

class DocumentType(Enum):
    """Document type enumeration"""
    CONTRACT = "contract"
    INVOICE = "invoice"
    SETTLEMENT = "settlement"
    COMPLIANCE = "compliance"
    RISK_ASSESSMENT = "risk_assessment"
    TRADE_CONFIRMATION = "trade_confirmation"

# Mock SendGrid client for demonstration
class MockSendGridClient:
    def __init__(self):
        self.sent_emails = []
        self.api_key = "mock_sendgrid_key"

    async def send_email(self, to_email: str, subject: str, content: str, from_email: str = "noreply@quantaenergi.com"):
        """Mock SendGrid email sending"""
        email_data = {
            "to": to_email,
            "from": from_email,
            "subject": subject,
            "content": content,
            "sent_at": datetime.now().isoformat(),
            "status": "sent"
        }
        self.sent_emails.append(email_data)
        logger.info(f"Mock SendGrid: Email sent to {to_email} with subject '{subject}'")
        await asyncio.sleep(0.1)  # Simulate API call delay
        return {"message_id": f"msg_{uuid.uuid4().hex[:12]}"}

class WorkflowManager:
    """
    Service for managing ETRM/CTRM workflows including approvals and document management
    Implements BPMN-lite workflow patterns and integrates with SendGrid for notifications
    """
    
    def __init__(self):
        # Workflow storage
        self.workflows = {}
        self.workflow_instances = {}
        self.approvals = {}
        self.documents = {}
        
        # Workflow templates
        self.workflow_templates = {}
        
        # Email client
        self.sendgrid_client = MockSendGridClient()
        
        # Initialize workflow templates
        self._initialize_workflow_templates()
    
    def _initialize_workflow_templates(self):
        """Initialize BPMN-lite workflow templates"""
        
        self.workflow_templates = {
            "trade_approval_workflow": {
                "name": "Trade Approval Workflow",
                "description": "Standard workflow for trade approvals",
                "version": "1.0",
                "steps": [
                    {
                        "step_id": "trade_validation",
                        "name": "Trade Validation",
                        "type": "system_task",
                        "approval_required": False,
                        "auto_approve": True,
                        "conditions": ["trade_data_valid", "counterparty_verified"]
                    },
                    {
                        "step_id": "risk_assessment",
                        "name": "Risk Assessment",
                        "type": "user_task",
                        "approval_required": True,
                        "approver_role": "risk_manager",
                        "timeout_hours": 4,
                        "escalation_role": "senior_risk_manager"
                    },
                    {
                        "step_id": "compliance_check",
                        "name": "Compliance Check",
                        "type": "user_task",
                        "approval_required": True,
                        "approver_role": "compliance_officer",
                        "timeout_hours": 2,
                        "escalation_role": "chief_compliance_officer"
                    },
                    {
                        "step_id": "final_approval",
                        "name": "Final Approval",
                        "type": "user_task",
                        "approval_required": True,
                        "approver_role": "trader_manager",
                        "timeout_hours": 8,
                        "escalation_role": "trading_director"
                    }
                ],
                "notifications": {
                    "on_start": ["trader", "risk_manager"],
                    "on_approval": ["trader", "next_approver"],
                    "on_rejection": ["trader", "original_approver"],
                    "on_timeout": ["escalation_role", "workflow_admin"]
                }
            },
            "document_review_workflow": {
                "name": "Document Review Workflow",
                "description": "Workflow for document review and approval",
                "version": "1.0",
                "steps": [
                    {
                        "step_id": "document_upload",
                        "name": "Document Upload",
                        "type": "system_task",
                        "approval_required": False,
                        "auto_approve": True
                    },
                    {
                        "step_id": "legal_review",
                        "name": "Legal Review",
                        "type": "user_task",
                        "approval_required": True,
                        "approver_role": "legal_counsel",
                        "timeout_hours": 24,
                        "escalation_role": "senior_legal_counsel"
                    },
                    {
                        "step_id": "compliance_review",
                        "name": "Compliance Review",
                        "type": "user_task",
                        "approval_required": True,
                        "approver_role": "compliance_officer",
                        "timeout_hours": 12,
                        "escalation_role": "chief_compliance_officer"
                    },
                    {
                        "step_id": "final_approval",
                        "name": "Final Approval",
                        "type": "user_task",
                        "approval_required": True,
                        "approver_role": "document_manager",
                        "timeout_hours": 8
                    }
                ],
                "notifications": {
                    "on_start": ["document_owner", "legal_counsel"],
                    "on_approval": ["document_owner", "next_reviewer"],
                    "on_rejection": ["document_owner", "original_reviewer"],
                    "on_timeout": ["escalation_role", "workflow_admin"]
                }
            },
            "settlement_approval_workflow": {
                "name": "Settlement Approval Workflow",
                "description": "Workflow for settlement approvals",
                "version": "1.0",
                "steps": [
                    {
                        "step_id": "settlement_validation",
                        "name": "Settlement Validation",
                        "type": "system_task",
                        "approval_required": False,
                        "auto_approve": True,
                        "conditions": ["amount_valid", "counterparty_verified", "currency_supported"]
                    },
                    {
                        "step_id": "treasury_review",
                        "name": "Treasury Review",
                        "type": "user_task",
                        "approval_required": True,
                        "approver_role": "treasury_manager",
                        "timeout_hours": 4,
                        "escalation_role": "treasury_director"
                    },
                    {
                        "step_id": "final_approval",
                        "name": "Final Approval",
                        "type": "user_task",
                        "approval_required": True,
                        "approver_role": "settlement_manager",
                        "timeout_hours": 2
                    }
                ],
                "notifications": {
                    "on_start": ["settlement_team", "treasury_manager"],
                    "on_approval": ["settlement_team", "next_approver"],
                    "on_rejection": ["settlement_team", "original_approver"],
                    "on_timeout": ["escalation_role", "workflow_admin"]
                }
            }
        }
    
    async def create_workflow_instance(
        self, 
        workflow_template: str, 
        context_data: Dict[str, Any],
        initiated_by: str
    ) -> Dict[str, Any]:
        """
        Create a new workflow instance
        
        Args:
            workflow_template: Template name to use
            context_data: Context data for the workflow
            initiated_by: User who initiated the workflow
            
        Returns:
            Dict with workflow instance details
        """
        try:
            if workflow_template not in self.workflow_templates:
                raise HTTPException(status_code=404, detail=f"Workflow template '{workflow_template}' not found")
            
            template = self.workflow_templates[workflow_template]
            
            # Create workflow instance
            instance_id = f"WF-{uuid.uuid4().hex[:8]}"
            workflow_instance = {
                "instance_id": instance_id,
                "template_name": workflow_template,
                "template_version": template["version"],
                "status": WorkflowStatus.DRAFT.value,
                "current_step": None,
                "completed_steps": [],
                "context_data": context_data,
                "initiated_by": initiated_by,
                "initiated_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "approvals": [],
                "documents": [],
                "notifications_sent": []
            }
            
            # Store workflow instance
            self.workflow_instances[instance_id] = workflow_instance
            
            # Start the workflow
            await self._start_workflow(instance_id)
            
            logger.info(f"Created workflow instance: {instance_id}")
            
            return {
                "success": True,
                "workflow_instance": workflow_instance,
                "message": "Workflow instance created successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to create workflow instance: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _start_workflow(self, instance_id: str):
        """Start a workflow instance"""
        
        try:
            instance = self.workflow_instances[instance_id]
            template = self.workflow_templates[instance["template_name"]]
            
            # Update status
            instance["status"] = WorkflowStatus.IN_PROGRESS.value
            instance["updated_at"] = datetime.now().isoformat()
            
            # Start first step
            first_step = template["steps"][0]
            instance["current_step"] = first_step["step_id"]
            
            # Process first step
            await self._process_workflow_step(instance_id, first_step)
            
            # Send notifications
            await self._send_workflow_notifications(instance_id, "on_start")
            
            logger.info(f"Started workflow instance: {instance_id}")
            
        except Exception as e:
            logger.error(f"Failed to start workflow: {str(e)}")
            instance["status"] = WorkflowStatus.CANCELLED.value
    
    async def _process_workflow_step(self, instance_id: str, step: Dict[str, Any]):
        """Process a workflow step"""
        
        try:
            instance = self.workflow_instances[instance_id]
            
            if step["type"] == "system_task":
                # Auto-process system tasks
                if step.get("auto_approve", False):
                    await self._auto_approve_step(instance_id, step)
                else:
                    # Run system validation
                    await self._run_system_validation(instance_id, step)
            
            elif step["type"] == "user_task":
                # Create approval request
                await self._create_approval_request(instance_id, step)
            
            logger.info(f"Processed workflow step: {step['step_id']} for instance: {instance_id}")
            
        except Exception as e:
            logger.error(f"Failed to process workflow step: {str(e)}")
            raise
    
    async def _auto_approve_step(self, instance_id: str, step: Dict[str, Any]):
        """Auto-approve a workflow step"""
        
        instance = self.workflow_instances[instance_id]
        
        # Mark step as completed
        instance["completed_steps"].append({
            "step_id": step["step_id"],
            "status": "approved",
            "approved_by": "system",
            "approved_at": datetime.now().isoformat(),
            "auto_approved": True
        })
        
        # Move to next step
        await self._move_to_next_step(instance_id)
    
    async def _run_system_validation(self, instance_id: str, step: Dict[str, Any]):
        """Run system validation for a step"""
        
        instance = self.workflow_instances[instance_id]
        context = instance["context_data"]
        
        # Check conditions
        conditions = step.get("conditions", [])
        all_conditions_met = True
        
        for condition in conditions:
            if condition == "trade_data_valid":
                # Mock trade data validation
                if not context.get("trade_data", {}).get("quantity", 0) > 0:
                    all_conditions_met = False
            elif condition == "counterparty_verified":
                # Mock counterparty verification
                if not context.get("counterparty", {}).get("verified", False):
                    all_conditions_met = False
            elif condition == "amount_valid":
                # Mock amount validation
                if not context.get("amount", 0) > 0:
                    all_conditions_met = False
        
        if all_conditions_met:
            await self._auto_approve_step(instance_id, step)
        else:
            # Reject workflow
            instance["status"] = WorkflowStatus.REJECTED.value
            instance["rejection_reason"] = "System validation failed"
            instance["updated_at"] = datetime.now().isoformat()
    
    async def _create_approval_request(self, instance_id: str, step: Dict[str, Any]):
        """Create an approval request for a user task"""
        
        instance = self.workflow_instances[instance_id]
        
        approval_id = f"APR-{uuid.uuid4().hex[:8]}"
        approval_request = {
            "approval_id": approval_id,
            "workflow_instance_id": instance_id,
            "step_id": step["step_id"],
            "step_name": step["name"],
            "approver_role": step.get("approver_role"),
            "escalation_role": step.get("escalation_role"),
            "timeout_hours": step.get("timeout_hours", 24),
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "due_at": (datetime.now() + timedelta(hours=step.get("timeout_hours", 24))).isoformat(),
            "context_data": instance["context_data"]
        }
        
        # Store approval request
        self.approvals[approval_id] = approval_request
        
        # Send notification to approver
        await self._send_approval_notification(approval_id)
        
        logger.info(f"Created approval request: {approval_id}")
    
    async def _send_approval_notification(self, approval_id: str):
        """Send notification for approval request"""
        
        approval = self.approvals[approval_id]
        instance = self.workflow_instances[approval["workflow_instance_id"]]
        
        # Mock approver email (in production, get from user management system)
        approver_email = f"{approval['approver_role'].replace('_', '.')}@quantaenergi.com"
        
        subject = f"Approval Required: {approval['step_name']} - {approval['workflow_instance_id']}"
        content = f"""
        <html>
        <body>
            <h2>Approval Required</h2>
            <p>You have a pending approval request for workflow instance: {approval['workflow_instance_id']}</p>
            <p><strong>Step:</strong> {approval['step_name']}</p>
            <p><strong>Due:</strong> {approval['due_at']}</p>
            <p><strong>Context:</strong></p>
            <pre>{json.dumps(approval['context_data'], indent=2)}</pre>
            <p>Please review and approve/reject this request.</p>
        </body>
        </html>
        """
        
        await self.sendgrid_client.send_email(approver_email, subject, content)
        
        # Track notification
        instance["notifications_sent"].append({
            "type": "approval_notification",
            "recipient": approver_email,
            "sent_at": datetime.now().isoformat(),
            "approval_id": approval_id
        })
    
    async def _send_workflow_notifications(self, instance_id: str, notification_type: str):
        """Send workflow notifications"""
        
        instance = self.workflow_instances[instance_id]
        template = self.workflow_templates[instance["template_name"]]
        
        notification_config = template.get("notifications", {}).get(notification_type, [])
        
        for recipient_role in notification_config:
            # Mock recipient email
            recipient_email = f"{recipient_role.replace('_', '.')}@quantaenergi.com"
            
            subject = f"Workflow Update: {template['name']} - {instance_id}"
            content = f"""
            <html>
            <body>
                <h2>Workflow Update</h2>
                <p>Workflow instance {instance_id} has been updated.</p>
                <p><strong>Status:</strong> {instance['status']}</p>
                <p><strong>Current Step:</strong> {instance['current_step']}</p>
                <p><strong>Initiated By:</strong> {instance['initiated_by']}</p>
            </body>
            </html>
            """
            
            await self.sendgrid_client.send_email(recipient_email, subject, content)
            
            # Track notification
            instance["notifications_sent"].append({
                "type": notification_type,
                "recipient": recipient_email,
                "sent_at": datetime.now().isoformat()
            })
    
    async def _move_to_next_step(self, instance_id: str):
        """Move workflow to next step"""
        
        instance = self.workflow_instances[instance_id]
        template = self.workflow_templates[instance["template_name"]]
        
        # Find current step index
        current_step_id = instance["current_step"]
        current_step_index = None
        
        for i, step in enumerate(template["steps"]):
            if step["step_id"] == current_step_id:
                current_step_index = i
                break
        
        if current_step_index is None:
            logger.error(f"Current step {current_step_id} not found in template")
            return
        
        # Check if there's a next step
        if current_step_index + 1 < len(template["steps"]):
            next_step = template["steps"][current_step_index + 1]
            instance["current_step"] = next_step["step_id"]
            
            # Process next step
            await self._process_workflow_step(instance_id, next_step)
        else:
            # Workflow completed
            instance["status"] = WorkflowStatus.COMPLETED.value
            instance["completed_at"] = datetime.now().isoformat()
            instance["updated_at"] = datetime.now().isoformat()
            
            # Send completion notifications
            await self._send_workflow_notifications(instance_id, "on_completion")
            
            logger.info(f"Workflow instance completed: {instance_id}")
    
    async def approve_workflow_step(
        self, 
        approval_id: str, 
        approved_by: str, 
        approval_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Approve a workflow step
        
        Args:
            approval_id: Approval request ID
            approved_by: User who approved
            approval_notes: Optional approval notes
            
        Returns:
            Dict with approval result
        """
        try:
            if approval_id not in self.approvals:
                raise HTTPException(status_code=404, detail="Approval request not found")
            
            approval = self.approvals[approval_id]
            instance = self.workflow_instances[approval["workflow_instance_id"]]
            
            # Update approval status
            approval["status"] = "approved"
            approval["approved_by"] = approved_by
            approval["approved_at"] = datetime.now().isoformat()
            approval["approval_notes"] = approval_notes
            
            # Mark step as completed
            instance["completed_steps"].append({
                "step_id": approval["step_id"],
                "status": "approved",
                "approved_by": approved_by,
                "approved_at": datetime.now().isoformat(),
                "approval_notes": approval_notes
            })
            
            # Move to next step
            await self._move_to_next_step(approval["workflow_instance_id"])
            
            # Send notifications
            await self._send_workflow_notifications(approval["workflow_instance_id"], "on_approval")
            
            logger.info(f"Approved workflow step: {approval_id}")
            
            return {
                "success": True,
                "approval_id": approval_id,
                "status": "approved",
                "message": "Workflow step approved successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to approve workflow step: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def reject_workflow_step(
        self, 
        approval_id: str, 
        rejected_by: str, 
        rejection_reason: str
    ) -> Dict[str, Any]:
        """
        Reject a workflow step
        
        Args:
            approval_id: Approval request ID
            rejected_by: User who rejected
            rejection_reason: Reason for rejection
            
        Returns:
            Dict with rejection result
        """
        try:
            if approval_id not in self.approvals:
                raise HTTPException(status_code=404, detail="Approval request not found")
            
            approval = self.approvals[approval_id]
            instance = self.workflow_instances[approval["workflow_instance_id"]]
            
            # Update approval status
            approval["status"] = "rejected"
            approval["rejected_by"] = rejected_by
            approval["rejected_at"] = datetime.now().isoformat()
            approval["rejection_reason"] = rejection_reason
            
            # Update workflow status
            instance["status"] = WorkflowStatus.REJECTED.value
            instance["rejection_reason"] = rejection_reason
            instance["rejected_at"] = datetime.now().isoformat()
            instance["updated_at"] = datetime.now().isoformat()
            
            # Send notifications
            await self._send_workflow_notifications(approval["workflow_instance_id"], "on_rejection")
            
            logger.info(f"Rejected workflow step: {approval_id}")
            
            return {
                "success": True,
                "approval_id": approval_id,
                "status": "rejected",
                "message": "Workflow step rejected successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to reject workflow step: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_workflow_instance(self, instance_id: str) -> Dict[str, Any]:
        """Get workflow instance details"""
        
        if instance_id not in self.workflow_instances:
            raise HTTPException(status_code=404, detail="Workflow instance not found")
        
        return {
            "success": True,
            "workflow_instance": self.workflow_instances[instance_id]
        }
    
    async def get_pending_approvals(self, approver_role: Optional[str] = None) -> Dict[str, Any]:
        """Get pending approvals"""
        
        pending_approvals = []
        
        for approval_id, approval in self.approvals.items():
            if approval["status"] == "pending":
                if approver_role is None or approval["approver_role"] == approver_role:
                    pending_approvals.append(approval)
        
        return {
            "success": True,
            "pending_approvals": pending_approvals,
            "count": len(pending_approvals)
        }
    
    async def upload_document(
        self, 
        workflow_instance_id: str, 
        document_data: Dict[str, Any],
        uploaded_by: str
    ) -> Dict[str, Any]:
        """
        Upload document to workflow
        
        Args:
            workflow_instance_id: Workflow instance ID
            document_data: Document information
            uploaded_by: User who uploaded
            
        Returns:
            Dict with upload result
        """
        try:
            if workflow_instance_id not in self.workflow_instances:
                raise HTTPException(status_code=404, detail="Workflow instance not found")
            
            instance = self.workflow_instances[workflow_instance_id]
            
            # Create document record
            document_id = f"DOC-{uuid.uuid4().hex[:8]}"
            document = {
                "document_id": document_id,
                "workflow_instance_id": workflow_instance_id,
                "document_type": document_data.get("document_type", "contract"),
                "filename": document_data.get("filename"),
                "content_type": document_data.get("content_type"),
                "file_size": document_data.get("file_size"),
                "uploaded_by": uploaded_by,
                "uploaded_at": datetime.now().isoformat(),
                "status": "uploaded",
                "version": "1.0",
                "metadata": document_data.get("metadata", {})
            }
            
            # Store document
            self.documents[document_id] = document
            
            # Add to workflow instance
            instance["documents"].append(document_id)
            instance["updated_at"] = datetime.now().isoformat()
            
            logger.info(f"Uploaded document: {document_id} to workflow: {workflow_instance_id}")
            
            return {
                "success": True,
                "document": document,
                "message": "Document uploaded successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to upload document: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_workflow_analytics(self) -> Dict[str, Any]:
        """Get workflow analytics"""
        
        total_workflows = len(self.workflow_instances)
        total_approvals = len(self.approvals)
        total_documents = len(self.documents)
        
        # Status breakdown
        status_counts = {}
        for instance in self.workflow_instances.values():
            status = instance["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Approval status breakdown
        approval_status_counts = {}
        for approval in self.approvals.values():
            status = approval["status"]
            approval_status_counts[status] = approval_status_counts.get(status, 0) + 1
        
        analytics = {
            "total_workflows": total_workflows,
            "total_approvals": total_approvals,
            "total_documents": total_documents,
            "workflow_status_breakdown": status_counts,
            "approval_status_breakdown": approval_status_counts,
            "average_completion_time_hours": 24.5,  # Mock data
            "workflow_templates_available": len(self.workflow_templates),
            "generated_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "analytics": analytics
        }


# Global service instance
workflow_manager = WorkflowManager()
