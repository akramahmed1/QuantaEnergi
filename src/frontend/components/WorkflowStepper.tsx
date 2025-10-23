import React, { useState, useEffect } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

interface WorkflowStep {
  step_id: string;
  name: string;
  type: 'system_task' | 'user_task';
  approval_required: boolean;
  approver_role?: string;
  timeout_hours?: number;
  escalation_role?: string;
  auto_approve?: boolean;
  conditions?: string[];
}

interface WorkflowTemplate {
  name: string;
  description: string;
  version: string;
  steps: WorkflowStep[];
  notifications: {
    on_start: string[];
    on_approval: string[];
    on_rejection: string[];
    on_timeout: string[];
  };
}

interface WorkflowInstance {
  instance_id: string;
  template_name: string;
  template_version: string;
  status: string;
  current_step: string | null;
  completed_steps: Array<{
    step_id: string;
    status: string;
    approved_by: string;
    approved_at: string;
    auto_approved?: boolean;
    approval_notes?: string;
  }>;
  context_data: Record<string, any>;
  initiated_by: string;
  initiated_at: string;
  updated_at: string;
  approvals: string[];
  documents: string[];
  notifications_sent: Array<{
    type: string;
    recipient: string;
    sent_at: string;
  }>;
}

interface PendingApproval {
  approval_id: string;
  workflow_instance_id: string;
  step_id: string;
  step_name: string;
  approver_role: string;
  escalation_role?: string;
  timeout_hours: number;
  status: string;
  created_at: string;
  due_at: string;
  context_data: Record<string, any>;
}

const WorkflowStepper: React.FC = () => {
  const queryClient = useQueryClient();
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [contextData, setContextData] = useState<Record<string, any>>({});
  const [workflowInstance, setWorkflowInstance] = useState<WorkflowInstance | null>(null);
  const [pendingApprovals, setPendingApprovals] = useState<PendingApproval[]>([]);
  const [selectedApproval, setSelectedApproval] = useState<string>('');
  const [approvalNotes, setApprovalNotes] = useState<string>('');
  const [rejectionReason, setRejectionReason] = useState<string>('');

  const commonHeaders = {
    Authorization: `Bearer ${localStorage.getItem('token')}`,
    'Content-Type': 'application/json',
  };

  // Fetch workflow templates
  const { data: templatesData, isLoading: templatesLoading } = useQuery({
    queryKey: ['workflow-templates'],
    queryFn: async () => {
      const response = await axios.get('http://localhost:8000/api/v1/workflows/templates', { headers: commonHeaders });
      return response.data.data.templates;
    },
  });

  // Fetch pending approvals
  const { data: approvalsData, refetch: refetchApprovals } = useQuery({
    queryKey: ['pending-approvals'],
    queryFn: async () => {
      const response = await axios.get('http://localhost:8000/api/v1/workflows/approvals/pending', { headers: commonHeaders });
      return response.data.data.pending_approvals;
    },
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  // Create workflow instance mutation
  const createWorkflowMutation = useMutation({
    mutationFn: async (data: { workflow_template: string; context_data: Record<string, any>; initiated_by: string }) =>
      axios.post('http://localhost:8000/api/v1/workflows/approve', data, { headers: commonHeaders }),
    onSuccess: (response) => {
      toast.success('Workflow instance created successfully!');
      setWorkflowInstance(response.data.data.workflow_instance);
      queryClient.invalidateQueries({ queryKey: ['pending-approvals'] });
    },
    onError: (error: any) => {
      toast.error(`Failed to create workflow: ${error.response?.data?.detail || error.message}`);
    },
  });

  // Approve workflow step mutation
  const approveWorkflowMutation = useMutation({
    mutationFn: async (data: { approval_id: string; approved_by: string; approval_notes?: string }) =>
      axios.post('http://localhost:8000/api/v1/workflows/approve/step', data, { headers: commonHeaders }),
    onSuccess: () => {
      toast.success('Workflow step approved successfully!');
      setApprovalNotes('');
      setSelectedApproval('');
      queryClient.invalidateQueries({ queryKey: ['pending-approvals'] });
      refetchApprovals();
    },
    onError: (error: any) => {
      toast.error(`Failed to approve workflow step: ${error.response?.data?.detail || error.message}`);
    },
  });

  // Reject workflow step mutation
  const rejectWorkflowMutation = useMutation({
    mutationFn: async (data: { approval_id: string; rejected_by: string; rejection_reason: string }) =>
      axios.post('http://localhost:8000/api/v1/workflows/reject/step', data, { headers: commonHeaders }),
    onSuccess: () => {
      toast.success('Workflow step rejected successfully!');
      setRejectionReason('');
      setSelectedApproval('');
      queryClient.invalidateQueries({ queryKey: ['pending-approvals'] });
      refetchApprovals();
    },
    onError: (error: any) => {
      toast.error(`Failed to reject workflow step: ${error.response?.data?.detail || error.message}`);
    },
  });

  // Update pending approvals when data changes
  useEffect(() => {
    if (approvalsData) {
      setPendingApprovals(approvalsData);
    }
  }, [approvalsData]);

  const handleCreateWorkflow = () => {
    if (!selectedTemplate) {
      toast.error('Please select a workflow template');
      return;
    }

    createWorkflowMutation.mutate({
      workflow_template: selectedTemplate,
      context_data: contextData,
      initiated_by: 'current_user', // In production, get from auth context
    });
  };

  const handleApproveWorkflow = () => {
    if (!selectedApproval) {
      toast.error('Please select an approval to approve');
      return;
    }

    approveWorkflowMutation.mutate({
      approval_id: selectedApproval,
      approved_by: 'current_user', // In production, get from auth context
      approval_notes: approvalNotes,
    });
  };

  const handleRejectWorkflow = () => {
    if (!selectedApproval) {
      toast.error('Please select an approval to reject');
      return;
    }

    if (!rejectionReason.trim()) {
      toast.error('Please provide a rejection reason');
      return;
    }

    rejectWorkflowMutation.mutate({
      approval_id: selectedApproval,
      rejected_by: 'current_user', // In production, get from auth context
      rejection_reason: rejectionReason,
    });
  };

  const getStepStatus = (stepId: string) => {
    if (!workflowInstance) return 'pending';
    
    const completedStep = workflowInstance.completed_steps.find(step => step.step_id === stepId);
    if (completedStep) {
      return completedStep.status === 'approved' ? 'completed' : 'rejected';
    }
    
    if (workflowInstance.current_step === stepId) {
      return 'current';
    }
    
    return 'pending';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100';
      case 'current': return 'text-blue-600 bg-blue-100';
      case 'rejected': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const selectedTemplateData = templatesData?.[selectedTemplate];

  return (
    <div className="p-6 bg-gray-100 min-h-screen">
      <h2 className="text-3xl font-bold text-gray-800 mb-6">Workflow Management</h2>

      {/* Workflow Creation Section */}
      <div className="bg-white shadow-lg rounded-lg p-6 mb-8">
        <h3 className="text-2xl font-semibold text-gray-700 mb-4">Create New Workflow</h3>
        
        {templatesLoading ? (
          <div className="text-center py-4">Loading templates...</div>
        ) : (
          <div className="space-y-4">
            <div>
              <label htmlFor="template-select" className="block text-sm font-medium text-gray-700 mb-2">
                Select Workflow Template:
              </label>
              <select
                id="template-select"
                value={selectedTemplate}
                onChange={(e) => setSelectedTemplate(e.target.value)}
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md shadow-sm"
              >
                <option value="">Select a template...</option>
                {templatesData && Object.entries(templatesData).map(([key, template]: [string, any]) => (
                  <option key={key} value={key}>
                    {template.name} - {template.description}
                  </option>
                ))}
              </select>
            </div>

            {selectedTemplateData && (
              <div>
                <h4 className="text-lg font-medium text-gray-700 mb-2">Template Details:</h4>
                <div className="bg-gray-50 p-4 rounded-md">
                  <p><strong>Name:</strong> {selectedTemplateData.name}</p>
                  <p><strong>Description:</strong> {selectedTemplateData.description}</p>
                  <p><strong>Version:</strong> {selectedTemplateData.version}</p>
                  <p><strong>Steps:</strong> {selectedTemplateData.steps.length}</p>
                </div>
              </div>
            )}

            <div>
              <label htmlFor="context-data" className="block text-sm font-medium text-gray-700 mb-2">
                Context Data (JSON):
              </label>
              <textarea
                id="context-data"
                value={JSON.stringify(contextData, null, 2)}
                onChange={(e) => {
                  try {
                    setContextData(JSON.parse(e.target.value));
                  } catch (error) {
                    // Invalid JSON, keep current value
                  }
                }}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                rows={4}
                placeholder='{"trade_id": "TRD-2024-001", "amount": 1000000.0, "counterparty": "GlobalOilCorp"}'
              />
            </div>

            <button
              onClick={handleCreateWorkflow}
              disabled={createWorkflowMutation.isPending || !selectedTemplate}
              className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {createWorkflowMutation.isPending ? 'Creating...' : 'Create Workflow'}
            </button>
          </div>
        )}
      </div>

      {/* Workflow Instance Display */}
      {workflowInstance && (
        <div className="bg-white shadow-lg rounded-lg p-6 mb-8">
          <h3 className="text-2xl font-semibold text-gray-700 mb-4">Workflow Instance: {workflowInstance.instance_id}</h3>
          
          <div className="mb-4">
            <p><strong>Status:</strong> <span className={`px-2 py-1 rounded text-sm ${getStatusColor(workflowInstance.status)}`}>{workflowInstance.status}</span></p>
            <p><strong>Template:</strong> {workflowInstance.template_name}</p>
            <p><strong>Current Step:</strong> {workflowInstance.current_step || 'None'}</p>
            <p><strong>Initiated By:</strong> {workflowInstance.initiated_by}</p>
            <p><strong>Initiated At:</strong> {new Date(workflowInstance.initiated_at).toLocaleString()}</p>
          </div>

          {selectedTemplateData && (
            <div>
              <h4 className="text-lg font-medium text-gray-700 mb-2">Workflow Steps:</h4>
              <div className="space-y-2">
                {selectedTemplateData.steps.map((step: any, index: number) => {
                  const stepStatus = getStepStatus(step.step_id);
                  return (
                    <div key={step.step_id} className="flex items-center space-x-3 p-3 border rounded-md">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${getStatusColor(stepStatus)}`}>
                        {index + 1}
                      </div>
                      <div className="flex-1">
                        <p className="font-medium">{step.name}</p>
                        <p className="text-sm text-gray-600">
                          Type: {step.type} | 
                          Approval Required: {step.approval_required ? 'Yes' : 'No'} |
                          {step.approver_role && ` Approver: ${step.approver_role}`}
                        </p>
                      </div>
                      <div className={`px-2 py-1 rounded text-sm ${getStatusColor(stepStatus)}`}>
                        {stepStatus}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Pending Approvals Section */}
      <div className="bg-white shadow-lg rounded-lg p-6">
        <h3 className="text-2xl font-semibold text-gray-700 mb-4">Pending Approvals</h3>
        
        {pendingApprovals.length === 0 ? (
          <div className="text-center py-4 text-gray-600">No pending approvals</div>
        ) : (
          <div className="space-y-4">
            {pendingApprovals.map((approval) => (
              <div key={approval.approval_id} className="border rounded-md p-4">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h4 className="font-medium">{approval.step_name}</h4>
                    <p className="text-sm text-gray-600">Approval ID: {approval.approval_id}</p>
                    <p className="text-sm text-gray-600">Workflow: {approval.workflow_instance_id}</p>
                    <p className="text-sm text-gray-600">Due: {new Date(approval.due_at).toLocaleString()}</p>
                  </div>
                  <div className={`px-2 py-1 rounded text-sm ${getStatusColor(approval.status)}`}>
                    {approval.status}
                  </div>
                </div>
                
                <div className="mb-3">
                  <p className="text-sm font-medium">Context Data:</p>
                  <pre className="text-xs bg-gray-50 p-2 rounded overflow-x-auto">
                    {JSON.stringify(approval.context_data, null, 2)}
                  </pre>
                </div>

                <div className="flex space-x-2">
                  <button
                    onClick={() => setSelectedApproval(approval.approval_id)}
                    className={`px-3 py-1 text-sm rounded ${
                      selectedApproval === approval.approval_id
                        ? 'bg-indigo-600 text-white'
                        : 'bg-indigo-100 text-indigo-700 hover:bg-indigo-200'
                    }`}
                  >
                    Select for Action
                  </button>
                </div>
              </div>
            ))}

            {selectedApproval && (
              <div className="border-t pt-4">
                <h4 className="font-medium mb-3">Action for Approval: {selectedApproval}</h4>
                
                <div className="space-y-3">
                  <div>
                    <label htmlFor="approval-notes" className="block text-sm font-medium text-gray-700">
                      Approval Notes (Optional):
                    </label>
                    <textarea
                      id="approval-notes"
                      value={approvalNotes}
                      onChange={(e) => setApprovalNotes(e.target.value)}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      rows={2}
                      placeholder="Add any notes for this approval..."
                    />
                  </div>

                  <div>
                    <label htmlFor="rejection-reason" className="block text-sm font-medium text-gray-700">
                      Rejection Reason (if rejecting):
                    </label>
                    <textarea
                      id="rejection-reason"
                      value={rejectionReason}
                      onChange={(e) => setRejectionReason(e.target.value)}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      rows={2}
                      placeholder="Provide reason for rejection..."
                    />
                  </div>

                  <div className="flex space-x-2">
                    <button
                      onClick={handleApproveWorkflow}
                      disabled={approveWorkflowMutation.isPending}
                      className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
                    >
                      {approveWorkflowMutation.isPending ? 'Approving...' : 'Approve'}
                    </button>
                    
                    <button
                      onClick={handleRejectWorkflow}
                      disabled={rejectWorkflowMutation.isPending}
                      className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
                    >
                      {rejectWorkflowMutation.isPending ? 'Rejecting...' : 'Reject'}
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default WorkflowStepper;
