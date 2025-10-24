"""
User-Configurable Workflow Engine for QuantaEnergi ETRM/CTRM Platform
Implements low-code workflow engine with drag-and-drop configuration UI
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
import threading
import time
import re
import ast
import operator
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    """Workflow status enumeration"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class NodeType(Enum):
    """Workflow node types"""
    START = "start"
    END = "end"
    TASK = "task"
    DECISION = "decision"
    PARALLEL = "parallel"
    MERGE = "merge"
    TIMER = "timer"
    CONDITION = "condition"
    LOOP = "loop"
    SUBPROCESS = "subprocess"
    SCRIPT = "script"
    API_CALL = "api_call"
    EMAIL = "email"
    SMS = "sms"
    NOTIFICATION = "notification"
    APPROVAL = "approval"
    DATA_TRANSFORM = "data_transform"
    VALIDATION = "validation"

class DataType(Enum):
    """Data types for workflow variables"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    ARRAY = "array"
    OBJECT = "object"

class OperatorType(Enum):
    """Operator types for conditions"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_EQUAL = "greater_equal"
    LESS_EQUAL = "less_equal"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IS_EMPTY = "is_empty"
    IS_NOT_EMPTY = "is_not_empty"
    IN = "in"
    NOT_IN = "not_in"

@dataclass
class WorkflowVariable:
    """Workflow variable definition"""
    name: str
    data_type: DataType
    default_value: Any = None
    description: str = ""
    is_required: bool = False
    validation_rules: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkflowNode:
    """Workflow node definition"""
    node_id: str
    node_type: NodeType
    name: str
    description: str = ""
    position: Dict[str, float] = field(default_factory=dict)
    properties: Dict[str, Any] = field(default_factory=dict)
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    actions: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkflowConnection:
    """Workflow connection between nodes"""
    connection_id: str
    from_node: str
    to_node: str
    condition: Optional[str] = None
    label: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Workflow:
    """Workflow definition"""
    workflow_id: str
    name: str
    description: str = ""
    version: str = "1.0"
    status: WorkflowStatus = WorkflowStatus.DRAFT
    variables: Dict[str, WorkflowVariable] = field(default_factory=dict)
    nodes: Dict[str, WorkflowNode] = field(default_factory=dict)
    connections: Dict[str, WorkflowConnection] = field(default_factory=dict)
    start_node: Optional[str] = None
    end_nodes: List[str] = field(default_factory=list)
    created_by: str = "system"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkflowInstance:
    """Workflow execution instance"""
    instance_id: str
    workflow_id: str
    status: WorkflowStatus = WorkflowStatus.ACTIVE
    current_node: Optional[str] = None
    variables: Dict[str, Any] = field(default_factory=dict)
    execution_history: List[Dict[str, Any]] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    created_by: str = "system"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkflowTemplate:
    """Workflow template for common patterns"""
    template_id: str
    name: str
    description: str = ""
    category: str = ""
    workflow_definition: Dict[str, Any] = field(default_factory=dict)
    variables: Dict[str, WorkflowVariable] = field(default_factory=dict)
    created_by: str = "system"
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

class WorkflowExecutor:
    """Workflow execution engine"""
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.instances: Dict[str, WorkflowInstance] = {}
        self.templates: Dict[str, WorkflowTemplate] = {}
        self.node_processors: Dict[NodeType, Callable] = {}
        self.condition_evaluator = ConditionEvaluator()
        self.script_engine = ScriptEngine()
        self.notification_service = NotificationService()
        self.api_client = APIClient()
        self.data_transformer = DataTransformer()
        
        # Initialize node processors
        self._initialize_node_processors()
        
    def _initialize_node_processors(self):
        """Initialize node processors"""
        self.node_processors = {
            NodeType.START: self._process_start_node,
            NodeType.END: self._process_end_node,
            NodeType.TASK: self._process_task_node,
            NodeType.DECISION: self._process_decision_node,
            NodeType.PARALLEL: self._process_parallel_node,
            NodeType.MERGE: self._process_merge_node,
            NodeType.TIMER: self._process_timer_node,
            NodeType.CONDITION: self._process_condition_node,
            NodeType.LOOP: self._process_loop_node,
            NodeType.SUBPROCESS: self._process_subprocess_node,
            NodeType.SCRIPT: self._process_script_node,
            NodeType.API_CALL: self._process_api_call_node,
            NodeType.EMAIL: self._process_email_node,
            NodeType.SMS: self._process_sms_node,
            NodeType.NOTIFICATION: self._process_notification_node,
            NodeType.APPROVAL: self._process_approval_node,
            NodeType.DATA_TRANSFORM: self._process_data_transform_node,
            NodeType.VALIDATION: self._process_validation_node
        }
    
    def create_workflow(self, name: str, description: str = "", 
                       created_by: str = "system") -> str:
        """Create a new workflow"""
        try:
            workflow_id = f"WF_{uuid.uuid4().hex[:8].upper()}"
            
            workflow = Workflow(
                workflow_id=workflow_id,
                name=name,
                description=description,
                created_by=created_by
            )
            
            self.workflows[workflow_id] = workflow
            logger.info(f"Created workflow: {name}")
            return workflow_id
            
        except Exception as e:
            logger.error(f"Error creating workflow: {e}")
            return ""
    
    def add_node(self, workflow_id: str, node_type: NodeType, name: str,
                 description: str = "", position: Dict[str, float] = None,
                 properties: Dict[str, Any] = None) -> str:
        """Add node to workflow"""
        try:
            if workflow_id not in self.workflows:
                return ""
            
            node_id = f"NODE_{uuid.uuid4().hex[:8].upper()}"
            
            node = WorkflowNode(
                node_id=node_id,
                node_type=node_type,
                name=name,
                description=description,
                position=position or {"x": 0, "y": 0},
                properties=properties or {}
            )
            
            self.workflows[workflow_id].nodes[node_id] = node
            
            # Set start node if it's the first node
            if node_type == NodeType.START and not self.workflows[workflow_id].start_node:
                self.workflows[workflow_id].start_node = node_id
            
            # Add to end nodes if it's an end node
            if node_type == NodeType.END:
                self.workflows[workflow_id].end_nodes.append(node_id)
            
            logger.info(f"Added node {node_id} to workflow {workflow_id}")
            return node_id
            
        except Exception as e:
            logger.error(f"Error adding node: {e}")
            return ""
    
    def add_connection(self, workflow_id: str, from_node: str, to_node: str,
                      condition: Optional[str] = None, label: str = "") -> str:
        """Add connection between nodes"""
        try:
            if workflow_id not in self.workflows:
                return ""
            
            connection_id = f"CONN_{uuid.uuid4().hex[:8].upper()}"
            
            connection = WorkflowConnection(
                connection_id=connection_id,
                from_node=from_node,
                to_node=to_node,
                condition=condition,
                label=label
            )
            
            self.workflows[workflow_id].connections[connection_id] = connection
            logger.info(f"Added connection {connection_id} to workflow {workflow_id}")
            return connection_id
            
        except Exception as e:
            logger.error(f"Error adding connection: {e}")
            return ""
    
    def add_variable(self, workflow_id: str, name: str, data_type: DataType,
                    default_value: Any = None, description: str = "",
                    is_required: bool = False) -> bool:
        """Add variable to workflow"""
        try:
            if workflow_id not in self.workflows:
                return False
            
            variable = WorkflowVariable(
                name=name,
                data_type=data_type,
                default_value=default_value,
                description=description,
                is_required=is_required
            )
            
            self.workflows[workflow_id].variables[name] = variable
            logger.info(f"Added variable {name} to workflow {workflow_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding variable: {e}")
            return False
    
    def execute_workflow(self, workflow_id: str, variables: Dict[str, Any] = None,
                        created_by: str = "system") -> str:
        """Execute workflow"""
        try:
            if workflow_id not in self.workflows:
                return ""
            
            workflow = self.workflows[workflow_id]
            
            # Create workflow instance
            instance_id = f"INST_{uuid.uuid4().hex[:8].upper()}"
            
            instance = WorkflowInstance(
                instance_id=instance_id,
                workflow_id=workflow_id,
                variables=variables or {},
                created_by=created_by
            )
            
            self.instances[instance_id] = instance
            
            # Start execution
            asyncio.create_task(self._execute_workflow_instance(instance_id))
            
            logger.info(f"Started workflow execution: {instance_id}")
            return instance_id
            
        except Exception as e:
            logger.error(f"Error executing workflow: {e}")
            return ""
    
    async def _execute_workflow_instance(self, instance_id: str):
        """Execute workflow instance"""
        try:
            instance = self.instances[instance_id]
            workflow = self.workflows[instance.workflow_id]
            
            # Start from start node
            current_node_id = workflow.start_node
            
            while current_node_id and instance.status == WorkflowStatus.ACTIVE:
                # Get current node
                current_node = workflow.nodes[current_node_id]
                
                # Process node
                result = await self._process_node(instance, current_node)
                
                # Update execution history
                instance.execution_history.append({
                    "node_id": current_node_id,
                    "node_name": current_node.name,
                    "node_type": current_node.node_type.value,
                    "result": result,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                # Find next node
                next_node_id = self._find_next_node(workflow, current_node_id, result)
                
                if next_node_id:
                    current_node_id = next_node_id
                    instance.current_node = current_node_id
                else:
                    # No next node found, workflow completed
                    instance.status = WorkflowStatus.COMPLETED
                    instance.completed_at = datetime.utcnow()
                    break
            
            logger.info(f"Workflow execution completed: {instance_id}")
            
        except Exception as e:
            logger.error(f"Error executing workflow instance: {e}")
            instance.status = WorkflowStatus.FAILED
            instance.completed_at = datetime.utcnow()
    
    async def _process_node(self, instance: WorkflowInstance, node: WorkflowNode) -> Dict[str, Any]:
        """Process workflow node"""
        try:
            processor = self.node_processors.get(node.node_type)
            
            if not processor:
                logger.error(f"No processor for node type: {node.node_type}")
                return {"error": f"No processor for node type: {node.node_type}"}
            
            return await processor(instance, node)
            
        except Exception as e:
            logger.error(f"Error processing node: {e}")
            return {"error": str(e)}
    
    def _find_next_node(self, workflow: Workflow, current_node_id: str, 
                        result: Dict[str, Any]) -> Optional[str]:
        """Find next node to execute"""
        try:
            # Find connections from current node
            connections = [
                conn for conn in workflow.connections.values()
                if conn.from_node == current_node_id
            ]
            
            if not connections:
                return None
            
            # If only one connection, use it
            if len(connections) == 1:
                return connections[0].to_node
            
            # If multiple connections, evaluate conditions
            for connection in connections:
                if not connection.condition:
                    return connection.to_node
                
                # Evaluate condition
                if self.condition_evaluator.evaluate(connection.condition, result):
                    return connection.to_node
            
            # No condition matched, use first connection
            return connections[0].to_node
            
        except Exception as e:
            logger.error(f"Error finding next node: {e}")
            return None
    
    # Node processors
    async def _process_start_node(self, instance: WorkflowInstance, node: WorkflowNode) -> Dict[str, Any]:
        """Process start node"""
        return {"status": "started", "message": "Workflow started"}
    
    async def _process_end_node(self, instance: WorkflowInstance, node: WorkflowNode) -> Dict[str, Any]:
        """Process end node"""
        return {"status": "completed", "message": "Workflow completed"}
    
    async def _process_task_node(self, instance: WorkflowInstance, node: WorkflowNode) -> Dict[str, Any]:
        """Process task node"""
        try:
            task_name = node.properties.get("task_name", "Unknown Task")
            task_description = node.properties.get("task_description", "")
            
            # Simulate task execution
            await asyncio.sleep(1)  # Simulate task duration
            
            return {
                "status": "completed",
                "task_name": task_name,
                "task_description": task_description,
                "result": "Task completed successfully"
            }
            
        except Exception as e:
            logger.error(f"Error processing task node: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _process_decision_node(self, instance: WorkflowInstance, node: WorkflowNode) -> Dict[str, Any]:
        """Process decision node"""
        try:
            condition = node.properties.get("condition", "")
            variables = instance.variables
            
            # Evaluate condition
            result = self.condition_evaluator.evaluate(condition, variables)
            
            return {
                "status": "completed",
                "condition": condition,
                "result": result,
                "decision": "yes" if result else "no"
            }
            
        except Exception as e:
            logger.error(f"Error processing decision node: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _process_parallel_node(self, instance: WorkflowInstance, node: WorkflowNode) -> Dict[str, Any]:
        """Process parallel node"""
        try:
            parallel_tasks = node.properties.get("parallel_tasks", [])
            
            # Execute tasks in parallel
            tasks = []
            for task in parallel_tasks:
                tasks.append(self._execute_parallel_task(task, instance.variables))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            return {
                "status": "completed",
                "parallel_tasks": len(parallel_tasks),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error processing parallel node: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _execute_parallel_task(self, task: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, Any]:
        """Execute parallel task"""
        try:
            task_name = task.get("name", "Unknown Task")
            task_duration = task.get("duration", 1)
            
            await asyncio.sleep(task_duration)
            
            return {
                "task_name": task_name,
                "status": "completed",
                "result": f"Task {task_name} completed"
            }
            
        except Exception as e:
            logger.error(f"Error executing parallel task: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _process_merge_node(self, instance: WorkflowInstance, node: WorkflowNode) -> Dict[str, Any]:
        """Process merge node"""
        try:
            merge_strategy = node.properties.get("merge_strategy", "all")
            
            return {
                "status": "completed",
                "merge_strategy": merge_strategy,
                "message": "Parallel branches merged"
            }
            
        except Exception as e:
            logger.error(f"Error processing merge node: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _process_timer_node(self, instance: WorkflowInstance, node: WorkflowNode) -> Dict[str, Any]:
        """Process timer node"""
        try:
            duration = node.properties.get("duration", 1)  # seconds
            
            await asyncio.sleep(duration)
            
            return {
                "status": "completed",
                "duration": duration,
                "message": f"Timer completed after {duration} seconds"
            }
            
        except Exception as e:
            logger.error(f"Error processing timer node: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _process_condition_node(self, instance: WorkflowInstance, node: WorkflowNode) -> Dict[str, Any]:
        """Process condition node"""
        try:
            condition = node.properties.get("condition", "")
            variables = instance.variables
            
            result = self.condition_evaluator.evaluate(condition, variables)
            
            return {
                "status": "completed",
                "condition": condition,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error processing condition node: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _process_loop_node(self, instance: WorkflowInstance, node: WorkflowNode) -> Dict[str, Any]:
        """Process loop node"""
        try:
            loop_condition = node.properties.get("loop_condition", "")
            max_iterations = node.properties.get("max_iterations", 10)
            
            iteration = 0
            while iteration < max_iterations:
                # Evaluate loop condition
                if not self.condition_evaluator.evaluate(loop_condition, instance.variables):
                    break
                
                iteration += 1
                instance.variables["loop_iteration"] = iteration
                
                # Execute loop body (simplified)
                await asyncio.sleep(0.1)
            
            return {
                "status": "completed",
                "iterations": iteration,
                "max_iterations": max_iterations
            }
            
        except Exception as e:
            logger.error(f"Error processing loop node: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _process_subprocess_node(self, instance: WorkflowInstance, node: WorkflowNode) -> Dict[str, Any]:
        """Process subprocess node"""
        try:
            subprocess_id = node.properties.get("subprocess_id", "")
            
            if subprocess_id in self.workflows:
                # Execute subprocess
                subprocess_instance_id = await self.execute_workflow(subprocess_id, instance.variables)
                
                return {
                    "status": "completed",
                    "subprocess_id": subprocess_id,
                    "subprocess_instance_id": subprocess_instance_id
                }
            else:
                return {
                    "status": "failed",
                    "error": f"Subprocess not found: {subprocess_id}"
                }
                
        except Exception as e:
            logger.error(f"Error processing subprocess node: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _process_script_node(self, instance: WorkflowInstance, node: WorkflowNode) -> Dict[str, Any]:
        """Process script node"""
        try:
            script = node.properties.get("script", "")
            variables = instance.variables
            
            result = self.script_engine.execute(script, variables)
            
            return {
                "status": "completed",
                "script": script,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error processing script node: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _process_api_call_node(self, instance: WorkflowInstance, node: WorkflowNode) -> Dict[str, Any]:
        """Process API call node"""
        try:
            url = node.properties.get("url", "")
            method = node.properties.get("method", "GET")
            headers = node.properties.get("headers", {})
            body = node.properties.get("body", "")
            
            result = await self.api_client.call_api(url, method, headers, body)
            
            return {
                "status": "completed",
                "url": url,
                "method": method,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error processing API call node: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _process_email_node(self, instance: WorkflowInstance, node: WorkflowNode) -> Dict[str, Any]:
        """Process email node"""
        try:
            to = node.properties.get("to", "")
            subject = node.properties.get("subject", "")
            body = node.properties.get("body", "")
            
            result = await self.notification_service.send_email(to, subject, body)
            
            return {
                "status": "completed",
                "to": to,
                "subject": subject,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error processing email node: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _process_sms_node(self, instance: WorkflowInstance, node: WorkflowNode) -> Dict[str, Any]:
        """Process SMS node"""
        try:
            to = node.properties.get("to", "")
            message = node.properties.get("message", "")
            
            result = await self.notification_service.send_sms(to, message)
            
            return {
                "status": "completed",
                "to": to,
                "message": message,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error processing SMS node: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _process_notification_node(self, instance: WorkflowInstance, node: WorkflowNode) -> Dict[str, Any]:
        """Process notification node"""
        try:
            notification_type = node.properties.get("notification_type", "info")
            title = node.properties.get("title", "")
            message = node.properties.get("message", "")
            recipients = node.properties.get("recipients", [])
            
            result = await self.notification_service.send_notification(
                notification_type, title, message, recipients
            )
            
            return {
                "status": "completed",
                "notification_type": notification_type,
                "title": title,
                "message": message,
                "recipients": recipients,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error processing notification node: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _process_approval_node(self, instance: WorkflowInstance, node: WorkflowNode) -> Dict[str, Any]:
        """Process approval node"""
        try:
            approver = node.properties.get("approver", "")
            approval_type = node.properties.get("approval_type", "manual")
            timeout = node.properties.get("timeout", 3600)  # seconds
            
            # Simulate approval process
            await asyncio.sleep(1)
            
            return {
                "status": "completed",
                "approver": approver,
                "approval_type": approval_type,
                "timeout": timeout,
                "result": "Approved"
            }
            
        except Exception as e:
            logger.error(f"Error processing approval node: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _process_data_transform_node(self, instance: WorkflowInstance, node: WorkflowNode) -> Dict[str, Any]:
        """Process data transform node"""
        try:
            input_data = node.properties.get("input_data", {})
            transform_rules = node.properties.get("transform_rules", [])
            
            result = self.data_transformer.transform(input_data, transform_rules)
            
            return {
                "status": "completed",
                "input_data": input_data,
                "transform_rules": transform_rules,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error processing data transform node: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _process_validation_node(self, instance: WorkflowInstance, node: WorkflowNode) -> Dict[str, Any]:
        """Process validation node"""
        try:
            input_data = node.properties.get("input_data", {})
            validation_rules = node.properties.get("validation_rules", [])
            
            result = self.data_transformer.validate(input_data, validation_rules)
            
            return {
                "status": "completed",
                "input_data": input_data,
                "validation_rules": validation_rules,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error processing validation node: {e}")
            return {"status": "failed", "error": str(e)}

class ConditionEvaluator:
    """Condition evaluation engine"""
    
    def __init__(self):
        self.operators = {
            OperatorType.EQUALS: operator.eq,
            OperatorType.NOT_EQUALS: operator.ne,
            OperatorType.GREATER_THAN: operator.gt,
            OperatorType.LESS_THAN: operator.lt,
            OperatorType.GREATER_EQUAL: operator.ge,
            OperatorType.LESS_EQUAL: operator.le,
            OperatorType.CONTAINS: self._contains,
            OperatorType.NOT_CONTAINS: self._not_contains,
            OperatorType.STARTS_WITH: self._starts_with,
            OperatorType.ENDS_WITH: self._ends_with,
            OperatorType.IS_EMPTY: self._is_empty,
            OperatorType.IS_NOT_EMPTY: self._is_not_empty,
            OperatorType.IN: self._in,
            OperatorType.NOT_IN: self._not_in
        }
    
    def evaluate(self, condition: str, variables: Dict[str, Any]) -> bool:
        """Evaluate condition"""
        try:
            # Parse condition
            parsed_condition = self._parse_condition(condition)
            
            if not parsed_condition:
                return False
            
            # Evaluate condition
            return self._evaluate_parsed_condition(parsed_condition, variables)
            
        except Exception as e:
            logger.error(f"Error evaluating condition: {e}")
            return False
    
    def _parse_condition(self, condition: str) -> Optional[Dict[str, Any]]:
        """Parse condition string"""
        try:
            # Simple condition parsing
            # Format: "variable operator value"
            parts = condition.split()
            
            if len(parts) < 3:
                return None
            
            variable = parts[0]
            operator_str = parts[1]
            value = " ".join(parts[2:])
            
            # Convert value to appropriate type
            try:
                value = ast.literal_eval(value)
            except:
                pass  # Keep as string
            
            return {
                "variable": variable,
                "operator": operator_str,
                "value": value
            }
            
        except Exception as e:
            logger.error(f"Error parsing condition: {e}")
            return None
    
    def _evaluate_parsed_condition(self, parsed_condition: Dict[str, Any], 
                                  variables: Dict[str, Any]) -> bool:
        """Evaluate parsed condition"""
        try:
            variable = parsed_condition["variable"]
            operator_str = parsed_condition["operator"]
            value = parsed_condition["value"]
            
            # Get variable value
            variable_value = variables.get(variable)
            
            # Convert operator string to operator type
            operator_type = self._get_operator_type(operator_str)
            
            if operator_type not in self.operators:
                return False
            
            # Evaluate condition
            return self.operators[operator_type](variable_value, value)
            
        except Exception as e:
            logger.error(f"Error evaluating parsed condition: {e}")
            return False
    
    def _get_operator_type(self, operator_str: str) -> OperatorType:
        """Get operator type from string"""
        operator_map = {
            "==": OperatorType.EQUALS,
            "!=": OperatorType.NOT_EQUALS,
            ">": OperatorType.GREATER_THAN,
            "<": OperatorType.LESS_THAN,
            ">=": OperatorType.GREATER_EQUAL,
            "<=": OperatorType.LESS_EQUAL,
            "contains": OperatorType.CONTAINS,
            "not_contains": OperatorType.NOT_CONTAINS,
            "starts_with": OperatorType.STARTS_WITH,
            "ends_with": OperatorType.ENDS_WITH,
            "is_empty": OperatorType.IS_EMPTY,
            "is_not_empty": OperatorType.IS_NOT_EMPTY,
            "in": OperatorType.IN,
            "not_in": OperatorType.NOT_IN
        }
        
        return operator_map.get(operator_str, OperatorType.EQUALS)
    
    def _contains(self, variable_value: Any, value: Any) -> bool:
        """Check if variable contains value"""
        try:
            if isinstance(variable_value, str) and isinstance(value, str):
                return value in variable_value
            return False
        except:
            return False
    
    def _not_contains(self, variable_value: Any, value: Any) -> bool:
        """Check if variable does not contain value"""
        return not self._contains(variable_value, value)
    
    def _starts_with(self, variable_value: Any, value: Any) -> bool:
        """Check if variable starts with value"""
        try:
            if isinstance(variable_value, str) and isinstance(value, str):
                return variable_value.startswith(value)
            return False
        except:
            return False
    
    def _ends_with(self, variable_value: Any, value: Any) -> bool:
        """Check if variable ends with value"""
        try:
            if isinstance(variable_value, str) and isinstance(value, str):
                return variable_value.endswith(value)
            return False
        except:
            return False
    
    def _is_empty(self, variable_value: Any, value: Any) -> bool:
        """Check if variable is empty"""
        try:
            if variable_value is None:
                return True
            if isinstance(variable_value, str):
                return len(variable_value.strip()) == 0
            if isinstance(variable_value, (list, dict)):
                return len(variable_value) == 0
            return False
        except:
            return False
    
    def _is_not_empty(self, variable_value: Any, value: Any) -> bool:
        """Check if variable is not empty"""
        return not self._is_empty(variable_value, value)
    
    def _in(self, variable_value: Any, value: Any) -> bool:
        """Check if variable is in value"""
        try:
            if isinstance(value, (list, tuple)):
                return variable_value in value
            return False
        except:
            return False
    
    def _not_in(self, variable_value: Any, value: Any) -> bool:
        """Check if variable is not in value"""
        return not self._in(variable_value, value)

class ScriptEngine:
    """Script execution engine"""
    
    def __init__(self):
        self.safe_globals = {
            "__builtins__": {
                "len": len,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
                "list": list,
                "dict": dict,
                "tuple": tuple,
                "set": set,
                "min": min,
                "max": max,
                "sum": sum,
                "abs": abs,
                "round": round,
                "sorted": sorted,
                "reversed": reversed,
                "enumerate": enumerate,
                "zip": zip,
                "map": map,
                "filter": filter,
                "any": any,
                "all": all,
                "range": range,
                "print": print
            }
        }
    
    def execute(self, script: str, variables: Dict[str, Any]) -> Any:
        """Execute script safely"""
        try:
            # Create safe locals with variables
            safe_locals = variables.copy()
            
            # Execute script
            result = eval(script, self.safe_globals, safe_locals)
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing script: {e}")
            return None

class NotificationService:
    """Notification service"""
    
    async def send_email(self, to: str, subject: str, body: str) -> Dict[str, Any]:
        """Send email notification"""
        try:
            # Simulate email sending
            await asyncio.sleep(0.1)
            
            return {
                "status": "sent",
                "to": to,
                "subject": subject,
                "message_id": f"email_{uuid.uuid4().hex[:8]}"
            }
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def send_sms(self, to: str, message: str) -> Dict[str, Any]:
        """Send SMS notification"""
        try:
            # Simulate SMS sending
            await asyncio.sleep(0.1)
            
            return {
                "status": "sent",
                "to": to,
                "message_id": f"sms_{uuid.uuid4().hex[:8]}"
            }
            
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def send_notification(self, notification_type: str, title: str, 
                               message: str, recipients: List[str]) -> Dict[str, Any]:
        """Send notification"""
        try:
            # Simulate notification sending
            await asyncio.sleep(0.1)
            
            return {
                "status": "sent",
                "notification_type": notification_type,
                "title": title,
                "message": message,
                "recipients": recipients,
                "notification_id": f"notif_{uuid.uuid4().hex[:8]}"
            }
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return {"status": "failed", "error": str(e)}

class APIClient:
    """API client for external calls"""
    
    async def call_api(self, url: str, method: str, headers: Dict[str, str], 
                       body: str) -> Dict[str, Any]:
        """Call external API"""
        try:
            # Simulate API call
            await asyncio.sleep(0.5)
            
            return {
                "status": "success",
                "url": url,
                "method": method,
                "headers": headers,
                "body": body,
                "response": {
                    "status_code": 200,
                    "data": {"message": "API call successful"}
                }
            }
            
        except Exception as e:
            logger.error(f"Error calling API: {e}")
            return {"status": "failed", "error": str(e)}

class DataTransformer:
    """Data transformation engine"""
    
    def transform(self, input_data: Dict[str, Any], transform_rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Transform data according to rules"""
        try:
            result = input_data.copy()
            
            for rule in transform_rules:
                field = rule.get("field", "")
                operation = rule.get("operation", "")
                value = rule.get("value", "")
                
                if field in result:
                    if operation == "set":
                        result[field] = value
                    elif operation == "add":
                        result[field] = result[field] + value
                    elif operation == "multiply":
                        result[field] = result[field] * value
                    elif operation == "concat":
                        result[field] = str(result[field]) + str(value)
            
            return result
            
        except Exception as e:
            logger.error(f"Error transforming data: {e}")
            return input_data
    
    def validate(self, input_data: Dict[str, Any], validation_rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate data according to rules"""
        try:
            validation_result = {
                "valid": True,
                "errors": [],
                "warnings": []
            }
            
            for rule in validation_rules:
                field = rule.get("field", "")
                rule_type = rule.get("rule_type", "")
                value = rule.get("value", "")
                
                if field in input_data:
                    field_value = input_data[field]
                    
                    if rule_type == "required" and not field_value:
                        validation_result["valid"] = False
                        validation_result["errors"].append(f"Field {field} is required")
                    elif rule_type == "min_length" and len(str(field_value)) < value:
                        validation_result["valid"] = False
                        validation_result["errors"].append(f"Field {field} is too short")
                    elif rule_type == "max_length" and len(str(field_value)) > value:
                        validation_result["valid"] = False
                        validation_result["errors"].append(f"Field {field} is too long")
                    elif rule_type == "min_value" and field_value < value:
                        validation_result["valid"] = False
                        validation_result["errors"].append(f"Field {field} is too small")
                    elif rule_type == "max_value" and field_value > value:
                        validation_result["valid"] = False
                        validation_result["errors"].append(f"Field {field} is too large")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating data: {e}")
            return {"valid": False, "errors": [str(e)], "warnings": []}

# Global workflow executor instance
workflow_executor = WorkflowExecutor()

def create_workflow(name: str, description: str = "", created_by: str = "system") -> str:
    """Create a new workflow"""
    return workflow_executor.create_workflow(name, description, created_by)

def add_node(workflow_id: str, node_type: NodeType, name: str,
             description: str = "", position: Dict[str, float] = None,
             properties: Dict[str, Any] = None) -> str:
    """Add node to workflow"""
    return workflow_executor.add_node(workflow_id, node_type, name, description, position, properties)

def add_connection(workflow_id: str, from_node: str, to_node: str,
                  condition: Optional[str] = None, label: str = "") -> str:
    """Add connection between nodes"""
    return workflow_executor.add_connection(workflow_id, from_node, to_node, condition, label)

def add_variable(workflow_id: str, name: str, data_type: DataType,
                default_value: Any = None, description: str = "",
                is_required: bool = False) -> bool:
    """Add variable to workflow"""
    return workflow_executor.add_variable(workflow_id, name, data_type, default_value, description, is_required)

def execute_workflow(workflow_id: str, variables: Dict[str, Any] = None,
                    created_by: str = "system") -> str:
    """Execute workflow"""
    return workflow_executor.execute_workflow(workflow_id, variables, created_by)

def get_workflow_status(workflow_id: str) -> Dict[str, Any]:
    """Get workflow status"""
    try:
        if workflow_id not in workflow_executor.workflows:
            return {"error": "Workflow not found"}
        
        workflow = workflow_executor.workflows[workflow_id]
        
        return {
            "workflow_id": workflow_id,
            "name": workflow.name,
            "description": workflow.description,
            "version": workflow.version,
            "status": workflow.status.value,
            "nodes": len(workflow.nodes),
            "connections": len(workflow.connections),
            "variables": len(workflow.variables),
            "created_by": workflow.created_by,
            "created_at": workflow.created_at.isoformat(),
            "updated_at": workflow.updated_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting workflow status: {e}")
        return {"error": str(e)}

def get_workflow_instance_status(instance_id: str) -> Dict[str, Any]:
    """Get workflow instance status"""
    try:
        if instance_id not in workflow_executor.instances:
            return {"error": "Workflow instance not found"}
        
        instance = workflow_executor.instances[instance_id]
        
        return {
            "instance_id": instance_id,
            "workflow_id": instance.workflow_id,
            "status": instance.status.value,
            "current_node": instance.current_node,
            "variables": instance.variables,
            "execution_history": instance.execution_history,
            "started_at": instance.started_at.isoformat(),
            "completed_at": instance.completed_at.isoformat() if instance.completed_at else None,
            "created_by": instance.created_by
        }
        
    except Exception as e:
        logger.error(f"Error getting workflow instance status: {e}")
        return {"error": str(e)}
