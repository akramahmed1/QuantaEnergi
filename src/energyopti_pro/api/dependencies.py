"""
FastAPI dependencies for EnergyOpti-Pro.

This module provides dependencies for authentication, authorization,
and tenant-aware database sessions for multi-tenancy support.
"""

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Annotated
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.security import decode_access_token
from ..db.database import get_db
from ..db.tenant_session import create_async_tenant_session_factory
from ..db.schemas import User
from ..core.rbac import check_role

# Security scheme
security = HTTPBearer()

async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> User:
    """
    Get the current authenticated user from JWT token.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        Authenticated user object
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        # Decode JWT token
        payload = decode_access_token(credentials.credentials)
        
        # Extract user information
        user_id = payload.get("sub")
        company_id = payload.get("company_id")
        role = payload.get("role")
        
        if not user_id or not company_id or not role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Create user object (in production, fetch from database)
        user = User(
            id=int(user_id),
            username=payload.get("username", "user"),
            email=payload.get("email", "user@example.com"),
            role=role,
            is_active=True,
            company_id=uuid.UUID(company_id),
            region=payload.get("region", "ME")
        )
        
        return user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}"
        )

async def get_tenant_session(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> AsyncSession:
    """
    Create a tenant-aware database session for the current user.
    
    This dependency ensures that all database operations are automatically
    scoped to the authenticated user's company_id, providing complete
    data isolation between tenants.
    
    Args:
        current_user: Authenticated user object
        db: Regular database session
        
    Returns:
        Tenant-aware database session
    """
    # Create tenant-aware session factory
    tenant_session_factory = create_async_tenant_session_factory(
        current_user.company_id
    )
    
    # Create and return tenant-aware session
    tenant_session = tenant_session_factory(
        bind=db.bind,
        expire_on_commit=False
    )
    
    return tenant_session

def require_role(required_roles: list[str]):
    """
    Dependency factory for role-based access control.
    
    Args:
        required_roles: List of roles that can access the endpoint
        
    Returns:
        Dependency function that checks user roles
    """
    async def role_checker(
        current_user: Annotated[User, Depends(get_current_user)]
    ) -> User:
        """
        Check if current user has required role.
        
        Args:
            current_user: Authenticated user object
            
        Returns:
            User object if role check passes
            
        Raises:
            HTTPException: If user doesn't have required role
        """
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {required_roles}"
            )
        
        return current_user
    
    return role_checker

def require_permission(required_permission: str):
    """
    Dependency factory for permission-based access control.
    
    Args:
        required_permission: Permission required to access the endpoint
        
    Returns:
        Dependency function that checks user permissions
    """
    async def permission_checker(
        current_user: Annotated[User, Depends(get_current_user)]
    ) -> User:
        """
        Check if current user has required permission.
        
        Args:
            current_user: Authenticated user object
            
        Returns:
            User object if permission check passes
            
        Raises:
            HTTPException: If user doesn't have required permission
        """
        # Import here to avoid circular imports
        from ..core.rbac import check_permission
        
        if not check_permission(current_user.role, required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required permission: {required_permission}"
            )
        
        return current_user
    
    return permission_checker

# Common role dependencies
require_trader = require_role(["trader", "analyst", "super_admin", "system_admin"])
require_analyst = require_role(["analyst", "super_admin", "system_admin"])
require_risk_manager = require_role(["risk_manager", "super_admin", "system_admin"])
require_compliance_admin = require_role(["compliance_admin", "super_admin", "system_admin"])
require_super_admin = require_role(["super_admin"])
require_system_admin = require_role(["system_admin"])

# Common permission dependencies
require_trading_permission = require_permission("trading")
require_risk_permission = require_permission("risk_management")
require_compliance_permission = require_permission("compliance")
require_admin_permission = require_permission("admin")

# Optional authentication for public endpoints
async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise return None.
    
    This is useful for endpoints that can be accessed by both
    authenticated and anonymous users.
    
    Args:
        credentials: Optional HTTP authorization credentials
        
    Returns:
        User object if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None 