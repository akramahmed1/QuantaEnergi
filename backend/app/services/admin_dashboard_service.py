"""
Admin Dashboard Service for ETRM/CTRM Trading
Handles administrative functions, user management, system monitoring, and administrative controls
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
import asyncio
import json
import uuid
from enum import Enum
from fastapi import HTTPException
import hashlib
import base64

logger = logging.getLogger(__name__)

class UserRole(Enum):
    """User role enumeration"""
    ADMIN = "admin"
    TRADER = "trader"
    COMPLIANCE_OFFICER = "compliance_officer"
    RISK_MANAGER = "risk_manager"
    OPERATIONS = "operations"
    VIEWER = "viewer"

class SystemStatus(Enum):
    """System status enumeration"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    MAINTENANCE = "maintenance"

class AdminDashboardService:
    """Service for administrative dashboard functionality"""
    
    def __init__(self):
        self.users = {}
        self.user_sessions = {}
        self.system_alerts = []
        self.audit_logs = []
        self.system_metrics = {}
        self.maintenance_schedules = []
        self.user_counter = 1000
        
        # Initialize system with default admin user
        self._initialize_system()
    
    def _initialize_system(self):
        """Initialize system with default admin user and basic configuration"""
        
        # Create default admin user
        admin_user = {
            "user_id": "admin",
            "internal_id": "ADMIN-0001",
            "username": "admin",
            "email": "admin@quantaenergi.com",
            "role": UserRole.ADMIN.value,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "permissions": self._get_role_permissions(UserRole.ADMIN.value),
            "metadata": {
                "first_name": "System",
                "last_name": "Administrator",
                "department": "IT",
                "phone": "+1-555-0001"
            }
        }
        
        self.users["admin"] = admin_user
        
        # Initialize system metrics
        self.system_metrics = {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "disk_usage": 0.0,
            "network_throughput": 0.0,
            "active_connections": 0,
            "last_updated": datetime.now().isoformat()
        }
        
        logger.info("Admin Dashboard Service initialized with default admin user")
    
    def _get_role_permissions(self, role: str) -> List[str]:
        """Get permissions for a specific role"""
        
        permissions_map = {
            UserRole.ADMIN.value: [
                "user_management", "system_monitoring", "audit_logs", 
                "maintenance_scheduling", "system_configuration", "all_data_access"
            ],
            UserRole.TRADER.value: [
                "trade_execution", "position_viewing", "market_data_access", 
                "risk_metrics", "portfolio_management"
            ],
            UserRole.COMPLIANCE_OFFICER.value: [
                "compliance_monitoring", "regulatory_reporting", "audit_logs", 
                "policy_management", "violation_tracking"
            ],
            UserRole.RISK_MANAGER.value: [
                "risk_monitoring", "position_viewing", "risk_metrics", 
                "stress_testing", "limit_management"
            ],
            UserRole.OPERATIONS.value: [
                "system_monitoring", "user_management", "maintenance_scheduling", 
                "backup_management", "performance_monitoring"
            ],
            UserRole.VIEWER.value: [
                "read_only_access", "basic_reports", "market_data_viewing"
            ]
        }
        
        return permissions_map.get(role, [])
    
    async def create_user(
        self, 
        user_data: Dict[str, Any],
        admin_user_id: str
    ) -> Dict[str, Any]:
        """
        Create a new user (admin only)
        
        Args:
            user_data: User information
            admin_user_id: ID of admin user creating the account
            
        Returns:
            Dict with created user details
        """
        try:
            # Verify admin permissions
            if not self._has_permission(admin_user_id, "user_management"):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            # Validate required fields
            required_fields = ["username", "email", "role", "first_name", "last_name"]
            for field in required_fields:
                if field not in user_data or not user_data[field]:
                    raise HTTPException(status_code=400, detail=f"Required field '{field}' is missing")
            
            username = user_data["username"]
            
            # Check if user already exists
            if username in self.users:
                raise HTTPException(status_code=409, detail="Username already exists")
            
            # Validate role
            if user_data["role"] not in [r.value for r in UserRole]:
                raise HTTPException(status_code=400, detail=f"Invalid role: {user_data['role']}")
            
            # Generate internal user ID
            internal_id = f"USER-{self.user_counter:06d}"
            self.user_counter += 1
            
            # Create user record
            user = {
                "user_id": username,
                "internal_id": internal_id,
                "username": username,
                "email": user_data["email"],
                "role": user_data["role"],
                "status": "active",
                "created_at": datetime.now().isoformat(),
                "created_by": admin_user_id,
                "last_login": None,
                "permissions": self._get_role_permissions(user_data["role"]),
                "metadata": {
                    "first_name": user_data["first_name"],
                    "last_name": user_data["last_name"],
                    "department": user_data.get("department", ""),
                    "phone": user_data.get("phone", ""),
                    "location": user_data.get("location", "")
                }
            }
            
            # Store user
            self.users[username] = user
            
            # Log admin action
            self._log_admin_action(admin_user_id, "create_user", f"Created user: {username}")
            
            logger.info(f"User created successfully: {username} by {admin_user_id}")
            
            return {
                "success": True,
                "user": user
            }
            
        except Exception as e:
            logger.error(f"User creation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def update_user(
        self, 
        username: str,
        update_data: Dict[str, Any],
        admin_user_id: str
    ) -> Dict[str, Any]:
        """
        Update user information (admin only)
        
        Args:
            username: Username to update
            update_data: Data to update
            admin_user_id: ID of admin user making the update
            
        Returns:
            Dict with updated user details
        """
        try:
            # Verify admin permissions
            if not self._has_permission(admin_user_id, "user_management"):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            if username not in self.users:
                raise HTTPException(status_code=404, detail="User not found")
            
            user = self.users[username]
            
            # Update allowed fields
            allowed_fields = ["email", "role", "status", "metadata"]
            for field in allowed_fields:
                if field in update_data:
                    if field == "role" and update_data[field] not in [r.value for r in UserRole]:
                        raise HTTPException(status_code=400, detail=f"Invalid role: {update_data[field]}")
                    
                    user[field] = update_data[field]
            
            # Update permissions if role changed
            if "role" in update_data:
                user["permissions"] = self._get_role_permissions(update_data["role"])
            
            user["last_updated"] = datetime.now().isoformat()
            user["updated_by"] = admin_user_id
            
            # Store updated user
            self.users[username] = user
            
            # Log admin action
            self._log_admin_action(admin_user_id, "update_user", f"Updated user: {username}")
            
            logger.info(f"User updated successfully: {username} by {admin_user_id}")
            
            return {
                "success": True,
                "user": user
            }
            
        except Exception as e:
            logger.error(f"User update failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def delete_user(
        self, 
        username: str,
        admin_user_id: str
    ) -> Dict[str, Any]:
        """
        Delete a user (admin only)
        
        Args:
            username: Username to delete
            admin_user_id: ID of admin user performing the deletion
            
        Returns:
            Dict with deletion result
        """
        try:
            # Verify admin permissions
            if not self._has_permission(admin_user_id, "user_management"):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            if username not in self.users:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Prevent deletion of admin user
            if username == "admin":
                raise HTTPException(status_code=400, detail="Cannot delete admin user")
            
            # Get user info before deletion
            user_info = self.users[username]
            
            # Remove user
            del self.users[username]
            
            # Log admin action
            self._log_admin_action(admin_user_id, "delete_user", f"Deleted user: {username}")
            
            logger.info(f"User deleted successfully: {username} by {admin_user_id}")
            
            return {
                "success": True,
                "deleted_user": user_info
            }
            
        except Exception as e:
            logger.error(f"User deletion failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_user_list(
        self, 
        admin_user_id: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get list of users (admin only)
        
        Args:
            admin_user_id: ID of admin user requesting the list
            filters: Optional filters for user list
            
        Returns:
            Dict with user list
        """
        try:
            # Verify admin permissions
            if not self._has_permission(admin_user_id, "user_management"):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            user_list = [user.copy() for user in self.users.values()]
            
            # Apply filters
            if filters:
                if "role" in filters:
                    user_list = [u for u in user_list if u["role"] == filters["role"]]
                
                if "status" in filters:
                    user_list = [u for u in user_list if u["status"] == filters["status"]]
                
                if "department" in filters:
                    user_list = [u for u in user_list if u["metadata"].get("department") == filters["department"]]
            
            # Remove sensitive information
            for user in user_list:
                if "permissions" in user:
                    del user["permissions"]
            
            return {
                "success": True,
                "users": user_list,
                "total_count": len(user_list)
            }
            
        except Exception as e:
            logger.error(f"User list retrieval failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_system_metrics(self, user_id: str) -> Dict[str, Any]:
        """
        Get system metrics and status
        
        Args:
            user_id: ID of user requesting metrics
            
        Returns:
            Dict with system metrics
        """
        try:
            # Verify permissions
            if not self._has_permission(user_id, "system_monitoring"):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            # Update system metrics (simulate real-time monitoring)
            await self._update_system_metrics()
            
            # Determine overall system status
            system_status = self._determine_system_status()
            
            metrics = {
                "system_status": system_status,
                "metrics": self.system_metrics,
                "alerts": self._get_active_alerts(),
                "performance_summary": self._get_performance_summary()
            }
            
            return {
                "success": True,
                "system_metrics": metrics
            }
            
        except Exception as e:
            logger.error(f"System metrics retrieval failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _update_system_metrics(self):
        """Update system metrics with simulated real-time data"""
        
        # Simulate real-time system monitoring
        # In practice, this would query actual system resources
        
        import random
        
        self.system_metrics.update({
            "cpu_usage": round(random.uniform(20, 80), 2),
            "memory_usage": round(random.uniform(30, 85), 2),
            "disk_usage": round(random.uniform(40, 90), 2),
            "network_throughput": round(random.uniform(100, 1000), 2),
            "active_connections": random.randint(50, 200),
            "last_updated": datetime.now().isoformat()
        })
    
    def _determine_system_status(self) -> str:
        """Determine overall system status based on metrics"""
        
        cpu = self.system_metrics["cpu_usage"]
        memory = self.system_metrics["memory_usage"]
        disk = self.system_metrics["disk_usage"]
        
        if cpu > 90 or memory > 90 or disk > 95:
            return SystemStatus.CRITICAL.value
        elif cpu > 80 or memory > 80 or disk > 85:
            return SystemStatus.WARNING.value
        else:
            return SystemStatus.HEALTHY.value
    
    def _get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active system alerts"""
        
        # Return recent alerts
        return self.system_alerts[-10:] if self.system_alerts else []
    
    def _get_performance_summary(self) -> Dict[str, Any]:
        """Get system performance summary"""
        
        metrics = self.system_metrics
        
        return {
            "overall_health": self._determine_system_status(),
            "resource_utilization": {
                "cpu": f"{metrics['cpu_usage']}%",
                "memory": f"{metrics['memory_usage']}%",
                "disk": f"{metrics['disk_usage']}%"
            },
            "network": {
                "throughput_mbps": metrics["network_throughput"],
                "active_connections": metrics["active_connections"]
            },
            "last_updated": metrics["last_updated"]
        }
    
    async def create_system_alert(
        self, 
        alert_data: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Create a system alert
        
        Args:
            alert_data: Alert information
            user_id: ID of user creating the alert
            
        Returns:
            Dict with created alert details
        """
        try:
            # Verify permissions
            if not self._has_permission(user_id, "system_monitoring"):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            # Validate required fields
            required_fields = ["title", "message", "severity"]
            for field in required_fields:
                if field not in alert_data or not alert_data[field]:
                    raise HTTPException(status_code=400, detail=f"Required field '{field}' is missing")
            
            # Generate alert ID
            alert_id = str(uuid.uuid4())
            
            # Create alert
            alert = {
                "alert_id": alert_id,
                "title": alert_data["title"],
                "message": alert_data["message"],
                "severity": alert_data["severity"],
                "status": "active",
                "created_by": user_id,
                "created_at": datetime.now().isoformat(),
                "acknowledged_by": None,
                "acknowledged_at": None,
                "resolved_by": None,
                "resolved_at": None,
                "metadata": alert_data.get("metadata", {})
            }
            
            # Add to alerts list
            self.system_alerts.append(alert)
            
            # Log action
            self._log_admin_action(user_id, "create_alert", f"Created alert: {alert_data['title']}")
            
            logger.info(f"System alert created: {alert_id} by {user_id}")
            
            return {
                "success": True,
                "alert": alert
            }
            
        except Exception as e:
            logger.error(f"System alert creation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def acknowledge_alert(
        self, 
        alert_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Acknowledge a system alert
        
        Args:
            alert_id: Alert identifier
            user_id: ID of user acknowledging the alert
            
        Returns:
            Dict with acknowledgment result
        """
        try:
            # Find alert
            alert = None
            for a in self.system_alerts:
                if a["alert_id"] == alert_id:
                    alert = a
                    break
            
            if not alert:
                raise HTTPException(status_code=404, detail="Alert not found")
            
            if alert["status"] != "active":
                raise HTTPException(status_code=400, detail="Alert is not active")
            
            # Acknowledge alert
            alert["status"] = "acknowledged"
            alert["acknowledged_by"] = user_id
            alert["acknowledged_at"] = datetime.now().isoformat()
            
            # Log action
            self._log_admin_action(user_id, "acknowledge_alert", f"Acknowledged alert: {alert_id}")
            
            logger.info(f"Alert acknowledged: {alert_id} by {user_id}")
            
            return {
                "success": True,
                "alert": alert
            }
            
        except Exception as e:
            logger.error(f"Alert acknowledgment failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_audit_logs(
        self, 
        user_id: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get audit logs (admin/compliance only)
        
        Args:
            user_id: ID of user requesting logs
            filters: Optional filters for logs
            
        Returns:
            Dict with audit logs
        """
        try:
            # Verify permissions
            if not self._has_permission(user_id, "audit_logs"):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            logs = self.audit_logs.copy()
            
            # Apply filters
            if filters:
                if "action_type" in filters:
                    logs = [l for l in logs if l["action_type"] == filters["action_type"]]
                
                if "user_id" in filters:
                    logs = [l for l in logs if l["user_id"] == filters["user_id"]]
                
                if "start_date" in filters:
                    start_date = datetime.fromisoformat(filters["start_date"])
                    logs = [l for l in logs if datetime.fromisoformat(l["timestamp"]) >= start_date]
                
                if "end_date" in filters:
                    end_date = datetime.fromisoformat(filters["end_date"])
                    logs = [l for l in logs if datetime.fromisoformat(l["timestamp"]) <= end_date]
            
            # Sort by timestamp (newest first)
            logs.sort(key=lambda x: x["timestamp"], reverse=True)
            
            return {
                "success": True,
                "audit_logs": logs,
                "total_count": len(logs)
            }
            
        except Exception as e:
            logger.error(f"Audit logs retrieval failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def _log_admin_action(self, user_id: str, action_type: str, description: str):
        """Log an administrative action"""
        
        log_entry = {
            "log_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "action_type": action_type,
            "description": description,
            "ip_address": "127.0.0.1",  # In practice, get from request
            "user_agent": "Admin Dashboard"  # In practice, get from request
        }
        
        self.audit_logs.append(log_entry)
        
        # Keep only last 10000 logs
        if len(self.audit_logs) > 10000:
            self.audit_logs = self.audit_logs[-10000:]
    
    def _has_permission(self, user_id: str, permission: str) -> bool:
        """Check if user has specific permission"""
        
        # Check if user_id is a username or internal_id
        if user_id not in self.users:
            # Try to find by username
            for user in self.users.values():
                if user.get("username") == user_id:
                    return permission in user.get("permissions", [])
            return False
        
        user = self.users[user_id]
        return permission in user.get("permissions", [])
    
    async def schedule_maintenance(
        self, 
        maintenance_data: Dict[str, Any],
        admin_user_id: str
    ) -> Dict[str, Any]:
        """
        Schedule system maintenance (admin only)
        
        Args:
            maintenance_data: Maintenance schedule information
            admin_user_id: ID of admin user scheduling maintenance
            
        Returns:
            Dict with maintenance schedule details
        """
        try:
            # Verify admin permissions
            if not self._has_permission(admin_user_id, "maintenance_scheduling"):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            # Validate required fields
            required_fields = ["title", "description", "start_time", "end_time", "affected_services"]
            for field in required_fields:
                if field not in maintenance_data or not maintenance_data[field]:
                    raise HTTPException(status_code=400, detail=f"Required field '{field}' is missing")
            
            # Generate maintenance ID
            maintenance_id = str(uuid.uuid4())
            
            # Create maintenance schedule
            maintenance = {
                "maintenance_id": maintenance_id,
                "title": maintenance_data["title"],
                "description": maintenance_data["description"],
                "start_time": maintenance_data["start_time"],
                "end_time": maintenance_data["end_time"],
                "affected_services": maintenance_data["affected_services"],
                "status": "scheduled",
                "created_by": admin_user_id,
                "created_at": datetime.now().isoformat(),
                "notified_users": [],
                "metadata": maintenance_data.get("metadata", {})
            }
            
            # Add to maintenance schedules
            self.maintenance_schedules.append(maintenance)
            
            # Log action
            self._log_admin_action(admin_user_id, "schedule_maintenance", f"Scheduled maintenance: {maintenance_data['title']}")
            
            logger.info(f"Maintenance scheduled: {maintenance_id} by {admin_user_id}")
            
            return {
                "success": True,
                "maintenance": maintenance
            }
            
        except Exception as e:
            logger.error(f"Maintenance scheduling failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_maintenance_schedules(
        self, 
        user_id: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get maintenance schedules
        
        Args:
            user_id: ID of user requesting schedules
            filters: Optional filters for schedules
            
        Returns:
            Dict with maintenance schedules
        """
        try:
            # Verify permissions
            if not self._has_permission(user_id, "maintenance_scheduling"):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            schedules = self.maintenance_schedules.copy()
            
            # Apply filters
            if filters:
                if "status" in filters:
                    schedules = [s for s in schedules if s["status"] == filters["status"]]
                
                if "start_date" in filters:
                    start_date = datetime.fromisoformat(filters["start_date"])
                    schedules = [s for s in schedules if datetime.fromisoformat(s["start_time"]) >= start_date]
            
            # Sort by start time
            schedules.sort(key=lambda x: x["start_time"])
            
            return {
                "success": True,
                "maintenance_schedules": schedules,
                "total_count": len(schedules)
            }
            
        except Exception as e:
            logger.error(f"Maintenance schedules retrieval failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_dashboard_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get dashboard summary for admin users
        
        Args:
            user_id: ID of user requesting summary
            
        Returns:
            Dict with dashboard summary
        """
        try:
            # Verify admin permissions
            if not self._has_permission(user_id, "system_monitoring"):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            # Get various metrics
            total_users = len(self.users)
            active_users = sum(1 for u in self.users.values() if u["status"] == "active")
            
            total_alerts = len(self.system_alerts)
            active_alerts = sum(1 for a in self.system_alerts if a["status"] == "active")
            
            total_maintenance = len(self.maintenance_schedules)
            scheduled_maintenance = sum(1 for m in self.maintenance_schedules if m["status"] == "scheduled")
            
            # Get recent activity
            recent_logs = self.audit_logs[-10:] if self.audit_logs else []
            
            summary = {
                "user_statistics": {
                    "total_users": total_users,
                    "active_users": active_users,
                    "user_health": (active_users / total_users * 100) if total_users > 0 else 0
                },
                "system_health": {
                    "status": self._determine_system_status(),
                    "total_alerts": total_alerts,
                    "active_alerts": active_alerts
                },
                "maintenance": {
                    "total_schedules": total_maintenance,
                    "scheduled_maintenance": scheduled_maintenance
                },
                "recent_activity": recent_logs,
                "generated_at": datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "dashboard_summary": summary
            }
            
        except Exception as e:
            logger.error(f"Dashboard summary retrieval failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
