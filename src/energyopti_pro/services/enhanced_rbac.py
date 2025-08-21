import asyncio
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from enum import Enum
import uuid
import json

class PermissionLevel(Enum):
    """Permission levels for RBAC system"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class ResourceType(Enum):
    """Resource types for permission management"""
    USER = "user"
    TRADE = "trade"
    CONTRACT = "contract"
    RISK = "risk"
    COMPLIANCE = "compliance"
    REPORT = "report"
    SYSTEM = "system"
    AUDIT = "audit"

class EnhancedRBACService:
    """Enhanced Role-Based Access Control service"""
    
    def __init__(self):
        # Predefined roles with permissions
        self.predefined_roles = {
            "super_admin": {
                "description": "Super Administrator with full system access",
                "permissions": self._get_super_admin_permissions(),
                "can_manage_roles": True,
                "can_manage_users": True,
                "can_manage_system": True
            },
            "system_admin": {
                "description": "System Administrator with system management access",
                "permissions": self._get_system_admin_permissions(),
                "can_manage_roles": False,
                "can_manage_users": True,
                "can_manage_system": True
            },
            "compliance_admin": {
                "description": "Compliance Administrator with regulatory oversight",
                "permissions": self._get_compliance_admin_permissions(),
                "can_manage_roles": False,
                "can_manage_users": False,
                "can_manage_system": False
            },
            "risk_manager": {
                "description": "Risk Manager with risk management access",
                "permissions": self._get_risk_manager_permissions(),
                "can_manage_roles": False,
                "can_manage_users": False,
                "can_manage_system": False
            },
            "trader": {
                "description": "Trader with trading and position access",
                "permissions": self._get_trader_permissions(),
                "can_manage_roles": False,
                "can_manage_users": False,
                "can_manage_system": False
            },
            "analyst": {
                "description": "Analyst with read access to trading data",
                "permissions": self._get_analyst_permissions(),
                "can_manage_roles": False,
                "can_manage_users": False,
                "can_manage_system": False
            },
            "viewer": {
                "description": "Viewer with limited read access",
                "permissions": self._get_viewer_permissions(),
                "can_manage_roles": False,
                "can_manage_users": False,
                "can_manage_system": False
            }
        }
        
        # Regional permissions
        self.regional_permissions = {
            "ME": ["middle_east_trading", "islamic_compliance", "ramadan_mode"],
            "US": ["us_trading", "ferc_compliance", "cftc_reporting"],
            "UK": ["uk_trading", "uk_ets_compliance", "brexit_compliance"],
            "EU": ["eu_trading", "eu_ets_compliance", "remit_reporting"],
            "GUYANA": ["guyana_trading", "local_content", "environmental_compliance"]
        }
    
    async def create_user(
        self,
        username: str,
        email: str,
        password_hash: str,
        role: str,
        regions: List[str],
        company_id: int,
        is_active: bool = True
    ) -> Dict[str, Any]:
        """Create a new user with role and regional permissions"""
        
        # Validate role
        if role not in self.predefined_roles:
            raise ValueError(f"Invalid role: {role}")
        
        # Validate regions
        for region in regions:
            if region not in self.regional_permissions:
                raise ValueError(f"Invalid region: {region}")
        
        user_id = str(uuid.uuid4())
        
        user = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "role": role,
            "regions": regions,
            "company_id": company_id,
            "is_active": is_active,
            "created_at": datetime.now(),
            "last_login": None,
            "permissions": self._get_user_permissions(role, regions),
            "regional_access": self._get_regional_access(regions)
        }
        
        return {
            "status": "created",
            "user_id": user_id,
            "user_data": user
        }
    
    async def update_user_role(
        self,
        user_id: str,
        new_role: str,
        updated_by: str
    ) -> Dict[str, Any]:
        """Update user role and permissions"""
        
        # Validate new role
        if new_role not in self.predefined_roles:
            raise ValueError(f"Invalid role: {new_role}")
        
        # Check if updater has permission
        if not await self._can_manage_users(updated_by):
            raise PermissionError("Insufficient permissions to update user roles")
        
        # Update user permissions
        updated_permissions = self._get_user_permissions(new_role, [])
        
        return {
            "status": "updated",
            "user_id": user_id,
            "new_role": new_role,
            "new_permissions": updated_permissions,
            "updated_by": updated_by,
            "updated_at": datetime.now()
        }
    
    async def add_regional_access(
        self,
        user_id: str,
        new_regions: List[str],
        updated_by: str
    ) -> Dict[str, Any]:
        """Add regional access to user"""
        
        # Validate regions
        for region in new_regions:
            if region not in self.regional_permissions:
                raise ValueError(f"Invalid region: {region}")
        
        # Check if updater has permission
        if not await self._can_manage_users(updated_by):
            raise PermissionError("Insufficient permissions to update user access")
        
        # Get current user permissions
        current_permissions = await self._get_user_permissions_by_id(user_id)
        current_regions = current_permissions.get("regions", [])
        
        # Add new regions
        updated_regions = list(set(current_regions + new_regions))
        updated_permissions = self._get_user_permissions(
            current_permissions.get("role", "viewer"),
            updated_regions
        )
        
        return {
            "status": "updated",
            "user_id": user_id,
            "added_regions": new_regions,
            "updated_regions": updated_regions,
            "updated_permissions": updated_permissions,
            "updated_by": updated_by,
            "updated_at": datetime.now()
        }
    
    async def check_permission(
        self,
        user_id: str,
        resource: str,
        action: str,
        region: Optional[str] = None
    ) -> bool:
        """Check if user has permission for specific action on resource"""
        
        user_permissions = await self._get_user_permissions_by_id(user_id)
        
        if not user_permissions or not user_permissions.get("is_active", False):
            return False
        
        # Check basic permissions
        resource_permissions = user_permissions.get("permissions", {})
        if resource not in resource_permissions:
            return False
        
        resource_actions = resource_permissions[resource]
        if action not in resource_actions:
            return False
        
        # Check regional permissions if region is specified
        if region:
            user_regions = user_permissions.get("regions", [])
            if region not in user_regions:
                return False
        
        return True
    
    async def get_user_permissions_summary(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """Get comprehensive user permissions summary"""
        
        user_permissions = await self._get_user_permissions_by_id(user_id)
        
        if not user_permissions:
            return {"error": "User not found"}
        
        return {
            "user_id": user_id,
            "username": user_permissions.get("username"),
            "role": user_permissions.get("role"),
            "regions": user_permissions.get("regions", []),
            "is_active": user_permissions.get("is_active", False),
            "permissions_summary": self._summarize_permissions(user_permissions.get("permissions", {})),
            "regional_access": user_permissions.get("regional_access", {}),
            "last_login": user_permissions.get("last_login"),
            "created_at": user_permissions.get("created_at")
        }
    
    async def create_custom_role(
        self,
        role_name: str,
        description: str,
        permissions: Dict[str, List[str]],
        regions: List[str],
        created_by: str
    ) -> Dict[str, Any]:
        """Create a custom role with specific permissions"""
        
        # Check if creator has permission
        if not await self._can_manage_roles(created_by):
            raise PermissionError("Insufficient permissions to create custom roles")
        
        # Validate permissions
        if not self._validate_custom_permissions(permissions):
            raise ValueError("Invalid permissions structure")
        
        # Validate regions
        for region in regions:
            if region not in self.regional_permissions:
                raise ValueError(f"Invalid region: {region}")
        
        custom_role = {
            "role_name": role_name,
            "description": description,
            "permissions": permissions,
            "regions": regions,
            "is_custom": True,
            "created_by": created_by,
            "created_at": datetime.now(),
            "can_manage_roles": False,
            "can_manage_users": False,
            "can_manage_system": False
        }
        
        return {
            "status": "created",
            "role_name": role_name,
            "custom_role": custom_role
        }
    
    async def audit_user_actions(
        self,
        user_id: str,
        action: str,
        resource: str,
        details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Audit user actions for compliance and security"""
        
        audit_entry = {
            "audit_id": str(uuid.uuid4()),
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "details": details,
            "timestamp": datetime.now(),
            "ip_address": details.get("ip_address"),
            "user_agent": details.get("user_agent"),
            "session_id": details.get("session_id")
        }
        
        return {
            "status": "audited",
            "audit_entry": audit_entry
        }
    
    def _get_super_admin_permissions(self) -> Dict[str, List[str]]:
        """Get super admin permissions"""
        
        return {
            ResourceType.USER.value: [p.value for p in PermissionLevel],
            ResourceType.TRADE.value: [p.value for p in PermissionLevel],
            ResourceType.CONTRACT.value: [p.value for p in PermissionLevel],
            ResourceType.RISK.value: [p.value for p in PermissionLevel],
            ResourceType.COMPLIANCE.value: [p.value for p in PermissionLevel],
            ResourceType.REPORT.value: [p.value for p in PermissionLevel],
            ResourceType.SYSTEM.value: [p.value for p in PermissionLevel],
            ResourceType.AUDIT.value: [p.value for p in PermissionLevel]
        }
    
    def _get_system_admin_permissions(self) -> Dict[str, List[str]]:
        """Get system admin permissions"""
        
        return {
            ResourceType.USER.value: [PermissionLevel.READ.value, PermissionLevel.WRITE.value],
            ResourceType.TRADE.value: [PermissionLevel.READ.value],
            ResourceType.CONTRACT.value: [PermissionLevel.READ.value],
            ResourceType.RISK.value: [PermissionLevel.READ.value],
            ResourceType.COMPLIANCE.value: [PermissionLevel.READ.value],
            ResourceType.REPORT.value: [PermissionLevel.READ.value, PermissionLevel.WRITE.value],
            ResourceType.SYSTEM.value: [PermissionLevel.READ.value, PermissionLevel.WRITE.value],
            ResourceType.AUDIT.value: [PermissionLevel.READ.value]
        }
    
    def _get_compliance_admin_permissions(self) -> Dict[str, List[str]]:
        """Get compliance admin permissions"""
        
        return {
            ResourceType.USER.value: [PermissionLevel.READ.value],
            ResourceType.TRADE.value: [PermissionLevel.READ.value],
            ResourceType.CONTRACT.value: [PermissionLevel.READ.value, PermissionLevel.WRITE.value],
            ResourceType.RISK.value: [PermissionLevel.READ.value],
            ResourceType.COMPLIANCE.value: [PermissionLevel.READ.value, PermissionLevel.WRITE.value, PermissionLevel.ADMIN.value],
            ResourceType.REPORT.value: [PermissionLevel.READ.value, PermissionLevel.WRITE.value],
            ResourceType.SYSTEM.value: [PermissionLevel.READ.value],
            ResourceType.AUDIT.value: [PermissionLevel.READ.value, PermissionLevel.WRITE.value]
        }
    
    def _get_risk_manager_permissions(self) -> Dict[str, List[str]]:
        """Get risk manager permissions"""
        
        return {
            ResourceType.USER.value: [PermissionLevel.READ.value],
            ResourceType.TRADE.value: [PermissionLevel.READ.value, PermissionLevel.WRITE.value],
            ResourceType.CONTRACT.value: [PermissionLevel.READ.value],
            ResourceType.RISK.value: [PermissionLevel.READ.value, PermissionLevel.WRITE.value, PermissionLevel.ADMIN.value],
            ResourceType.COMPLIANCE.value: [PermissionLevel.READ.value],
            ResourceType.REPORT.value: [PermissionLevel.READ.value, PermissionLevel.WRITE.value],
            ResourceType.SYSTEM.value: [PermissionLevel.READ.value],
            ResourceType.AUDIT.value: [PermissionLevel.READ.value]
        }
    
    def _get_trader_permissions(self) -> Dict[str, List[str]]:
        """Get trader permissions"""
        
        return {
            ResourceType.USER.value: [PermissionLevel.READ.value],
            ResourceType.TRADE.value: [PermissionLevel.READ.value, PermissionLevel.WRITE.value],
            ResourceType.CONTRACT.value: [PermissionLevel.READ.value, PermissionLevel.WRITE.value],
            ResourceType.RISK.value: [PermissionLevel.READ.value],
            ResourceType.COMPLIANCE.value: [PermissionLevel.READ.value],
            ResourceType.REPORT.value: [PermissionLevel.READ.value],
            ResourceType.SYSTEM.value: [PermissionLevel.READ.value],
            ResourceType.AUDIT.value: [PermissionLevel.READ.value]
        }
    
    def _get_analyst_permissions(self) -> Dict[str, List[str]]:
        """Get analyst permissions"""
        
        return {
            ResourceType.USER.value: [PermissionLevel.READ.value],
            ResourceType.TRADE.value: [PermissionLevel.READ.value],
            ResourceType.CONTRACT.value: [PermissionLevel.READ.value],
            ResourceType.RISK.value: [PermissionLevel.READ.value],
            ResourceType.COMPLIANCE.value: [PermissionLevel.READ.value],
            ResourceType.REPORT.value: [PermissionLevel.READ.value, PermissionLevel.WRITE.value],
            ResourceType.SYSTEM.value: [PermissionLevel.READ.value],
            ResourceType.AUDIT.value: [PermissionLevel.READ.value]
        }
    
    def _get_viewer_permissions(self) -> Dict[str, List[str]]:
        """Get viewer permissions"""
        
        return {
            ResourceType.USER.value: [PermissionLevel.READ.value],
            ResourceType.TRADE.value: [PermissionLevel.READ.value],
            ResourceType.CONTRACT.value: [PermissionLevel.READ.value],
            ResourceType.RISK.value: [PermissionLevel.READ.value],
            ResourceType.COMPLIANCE.value: [PermissionLevel.READ.value],
            ResourceType.REPORT.value: [PermissionLevel.READ.value],
            ResourceType.SYSTEM.value: [PermissionLevel.READ.value],
            ResourceType.AUDIT.value: [PermissionLevel.READ.value]
        }
    
    def _get_user_permissions(self, role: str, regions: List[str]) -> Dict[str, Any]:
        """Get user permissions based on role and regions"""
        
        base_permissions = self.predefined_roles.get(role, {}).get("permissions", {})
        
        # Add regional permissions
        regional_perms = {}
        for region in regions:
            if region in self.regional_permissions:
                regional_perms[region] = self.regional_permissions[region]
        
        return {
            "base_permissions": base_permissions,
            "regional_permissions": regional_perms,
            "regions": regions
        }
    
    def _get_regional_access(self, regions: List[str]) -> Dict[str, Any]:
        """Get regional access details"""
        
        access_details = {}
        for region in regions:
            if region in self.regional_permissions:
                access_details[region] = {
                    "permissions": self.regional_permissions[region],
                    "access_granted": datetime.now(),
                    "status": "active"
                }
        
        return access_details
    
    async def _can_manage_users(self, user_id: str) -> bool:
        """Check if user can manage other users"""
        
        user_permissions = await self._get_user_permissions_by_id(user_id)
        if not user_permissions:
            return False
        
        role = user_permissions.get("role", "")
        role_config = self.predefined_roles.get(role, {})
        
        return role_config.get("can_manage_users", False)
    
    async def _can_manage_roles(self, user_id: str) -> bool:
        """Check if user can manage roles"""
        
        user_permissions = await self._get_user_permissions_by_id(user_id)
        if not user_permissions:
            return False
        
        role = user_permissions.get("role", "")
        role_config = self.predefined_roles.get(role, {})
        
        return role_config.get("can_manage_roles", False)
    
    async def _get_user_permissions_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user permissions by ID (mock implementation)"""
        
        # Mock implementation - in production, query database
        await asyncio.sleep(0.01)
        
        # Return mock user data
        return {
            "user_id": user_id,
            "username": f"user_{user_id[:8]}",
            "role": "trader",
            "regions": ["ME", "US"],
            "is_active": True,
            "permissions": self._get_user_permissions("trader", ["ME", "US"]),
            "last_login": datetime.now() - timedelta(hours=2),
            "created_at": datetime.now() - timedelta(days=30)
        }
    
    def _summarize_permissions(self, permissions: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize user permissions for display"""
        
        base_perms = permissions.get("base_permissions", {})
        regional_perms = permissions.get("regional_permissions", {})
        
        summary = {
            "total_resources": len(base_perms),
            "read_access": sum(1 for resource in base_perms.values() if "read" in resource),
            "write_access": sum(1 for resource in base_perms.values() if "write" in resource),
            "admin_access": sum(1 for resource in base_perms.values() if "admin" in resource),
            "regions_with_access": len(regional_perms),
            "permission_level": self._get_permission_level(base_perms)
        }
        
        return summary
    
    def _get_permission_level(self, permissions: Dict[str, List[str]]) -> str:
        """Get overall permission level"""
        
        if any("super_admin" in perms for perms in permissions.values()):
            return "Super Admin"
        elif any("admin" in perms for perms in permissions.values()):
            return "Admin"
        elif any("write" in perms for perms in permissions.values()):
            return "Write"
        elif any("read" in perms for perms in permissions.values()):
            return "Read"
        else:
            return "None"
    
    def _validate_custom_permissions(self, permissions: Dict[str, List[str]]) -> bool:
        """Validate custom permissions structure"""
        
        valid_actions = [p.value for p in PermissionLevel]
        valid_resources = [r.value for r in ResourceType]
        
        for resource, actions in permissions.items():
            if resource not in valid_resources:
                return False
            
            if not isinstance(actions, list):
                return False
            
            for action in actions:
                if action not in valid_actions:
                    return False
        
        return True 