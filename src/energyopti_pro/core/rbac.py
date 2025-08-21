"""
Role-Based Access Control (RBAC) system for EnergyOpti-Pro.

This module provides comprehensive RBAC functionality including role checking,
permission validation, and user authorization for different system features.
"""

from functools import wraps
from typing import List, Optional, Union, Callable, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..db.schemas import User
from ..db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Security scheme
security = HTTPBearer()

# Role hierarchy and permissions
ROLE_HIERARCHY = {
    "super_admin": {
        "level": 10,
        "permissions": ["*"],  # All permissions
        "description": "Super administrator with full system access"
    },
    "system_admin": {
        "level": 9,
        "permissions": ["system_management", "user_management", "security_management"],
        "description": "System administrator with system management access"
    },
    "compliance_admin": {
        "level": 8,
        "permissions": ["compliance_management", "regulatory_reporting", "audit_access"],
        "description": "Compliance administrator with regulatory oversight"
    },
    "risk_manager": {
        "level": 7,
        "permissions": ["risk_management", "position_monitoring", "limit_management"],
        "description": "Risk manager with portfolio risk oversight"
    },
    "trader": {
        "level": 6,
        "permissions": ["trading", "position_management", "market_data", "basic_reports"],
        "description": "Trader with trading and position management access"
    },
    "analyst": {
        "level": 5,
        "permissions": ["data_analysis", "reporting", "market_research", "basic_trading"],
        "description": "Analyst with data analysis and reporting access"
    },
    "engineer": {
        "level": 4,
        "permissions": ["system_monitoring", "technical_support", "data_access"],
        "description": "Engineer with technical system access"
    },
    "viewer": {
        "level": 3,
        "permissions": ["read_access", "basic_reports", "market_data_view"],
        "description": "Viewer with read-only access to basic information"
    },
    "guest": {
        "level": 2,
        "permissions": ["public_data", "basic_info"],
        "description": "Guest with access to public information only"
    }
}

# Feature permissions mapping
FEATURE_PERMISSIONS = {
    "trading": {
        "required_role": "trader",
        "permissions": ["trading", "position_management"],
        "description": "Trading operations and position management"
    },
    "risk_management": {
        "required_role": "risk_manager",
        "permissions": ["risk_management", "position_monitoring"],
        "description": "Risk management and monitoring"
    },
    "compliance": {
        "required_role": "compliance_admin",
        "permissions": ["compliance_management", "regulatory_reporting"],
        "description": "Compliance and regulatory reporting"
    },
    "system_admin": {
        "required_role": "system_admin",
        "permissions": ["system_management", "user_management"],
        "description": "System administration"
    },
    "user_management": {
        "required_role": "system_admin",
        "permissions": ["user_management"],
        "description": "User account management"
    },
    "data_analysis": {
        "required_role": "analyst",
        "permissions": ["data_analysis", "reporting"],
        "description": "Data analysis and reporting"
    },
    "market_data": {
        "required_role": "trader",
        "permissions": ["market_data", "trading"],
        "description": "Market data access"
    }
}


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP authorization credentials
        db: Database session
        
    Returns:
        Authenticated user object
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        # In production, decode and validate JWT token
        # For now, return a mock user
        from ..db.schemas import User
        
        # Mock user for development
        user = User(
            id=1,
            username="demo_user",
            email="demo@energyopti-pro.com",
            role="trader",
            is_active=True,
            company_id=1,
            region="ME"
        )
        
        return user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def check_role(required_roles: Union[str, List[str]]) -> Callable:
    """
    Decorator to check if user has required role(s).
    
    Args:
        required_roles: Single role or list of roles that grant access
        
    Returns:
        Decorator function that checks role permissions
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from dependencies
            current_user = kwargs.get('current_user')
            if not current_user:
                # Try to get from function parameters
                for arg in args:
                    if hasattr(arg, 'role'):
                        current_user = arg
                        break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not authenticated"
                )
            
            # Check if user has required role
            if isinstance(required_roles, str):
                required_roles_list = [required_roles]
            else:
                required_roles_list = required_roles
            
            user_role = current_user.role
            user_level = ROLE_HIERARCHY.get(user_role, {}).get("level", 0)
            
            # Check if user has any of the required roles
            has_access = False
            for required_role in required_roles_list:
                required_level = ROLE_HIERARCHY.get(required_role, {}).get("level", 0)
                
                # User can access if their role level is >= required level
                if user_level >= required_level:
                    has_access = True
                    break
            
            if not has_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required roles: {required_roles_list}, User role: {user_role}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def check_permission(required_permission: str) -> Callable:
    """
    Decorator to check if user has required permission.
    
    Args:
        required_permission: Permission required to access the resource
        
    Returns:
        Decorator function that checks permissions
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from dependencies
            current_user = kwargs.get('current_user')
            if not current_user:
                # Try to get from function parameters
                for arg in args:
                    if hasattr(arg, 'role'):
                        current_user = arg
                        break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not authenticated"
                )
            
            user_role = current_user.role
            user_permissions = ROLE_HIERARCHY.get(user_role, {}).get("permissions", [])
            
            # Check if user has required permission
            if "*" not in user_permissions and required_permission not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required: {required_permission}, User permissions: {user_permissions}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def check_feature_access(feature_name: str) -> Callable:
    """
    Decorator to check if user has access to a specific feature.
    
    Args:
        feature_name: Name of the feature to check access for
        
    Returns:
        Decorator function that checks feature access
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from dependencies
            current_user = kwargs.get('current_user')
            if not current_user:
                # Try to get from function parameters
                for arg in args:
                    if hasattr(arg, 'role'):
                        current_user = arg
                        break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not authenticated"
                )
            
            user_role = current_user.role
            feature_config = FEATURE_PERMISSIONS.get(feature_name)
            
            if not feature_config:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unknown feature: {feature_name}"
                )
            
            required_role = feature_config["required_role"]
            required_permissions = feature_config["permissions"]
            
            # Check if user has required role level
            user_level = ROLE_HIERARCHY.get(user_role, {}).get("level", 0)
            required_level = ROLE_HIERARCHY.get(required_role, {}).get("level", 0)
            
            if user_level < required_level:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient role level for feature '{feature_name}'. Required: {required_role}, User: {user_role}"
                )
            
            # Check if user has required permissions
            user_permissions = ROLE_HIERARCHY.get(user_role, {}).get("permissions", [])
            if "*" not in user_permissions:
                for permission in required_permissions:
                    if permission not in user_permissions:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Insufficient permissions for feature '{feature_name}'. Required: {permission}"
                        )
            
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def get_user_permissions(user_role: str) -> List[str]:
    """
    Get permissions for a specific user role.
    
    Args:
        user_role: Role to get permissions for
        
    Returns:
        List of permissions for the role
    """
    return ROLE_HIERARCHY.get(user_role, {}).get("permissions", [])


def get_role_hierarchy() -> dict:
    """
    Get the complete role hierarchy.
    
    Returns:
        Dictionary containing role hierarchy information
    """
    return ROLE_HIERARCHY


def get_feature_permissions() -> dict:
    """
    Get the complete feature permissions mapping.
    
    Returns:
        Dictionary containing feature permissions information
    """
    return FEATURE_PERMISSIONS


def validate_role_assignment(current_user_role: str, target_role: str) -> bool:
    """
    Validate if a user can assign a specific role to another user.
    
    Args:
        current_user_role: Role of the user making the assignment
        target_role: Role being assigned
        
    Returns:
        True if assignment is allowed, False otherwise
    """
    current_user_level = ROLE_HIERARCHY.get(current_user_role, {}).get("level", 0)
    target_role_level = ROLE_HIERARCHY.get(target_role, {}).get("level", 0)
    
    # Users can only assign roles with lower or equal level
    return current_user_level >= target_role_level


def get_accessible_features(user_role: str) -> List[str]:
    """
    Get list of features accessible to a specific user role.
    
    Args:
        user_role: Role to check access for
        
    Returns:
        List of accessible feature names
    """
    user_level = ROLE_HIERARCHY.get(user_role, {}).get("level", 0)
    accessible_features = []
    
    for feature_name, feature_config in FEATURE_PERMISSIONS.items():
        required_role = feature_config["required_role"]
        required_level = ROLE_HIERARCHY.get(required_role, {}).get("level", 0)
        
        if user_level >= required_level:
            accessible_features.append(feature_name)
    
    return accessible_features 