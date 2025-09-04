"""
Authentication and Authorization Module
Handles user authentication, authorization, and session management
"""

from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Get current authenticated user from JWT token
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        Dict containing user information
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        # For demo purposes, return a mock user
        # In production, this would validate the JWT token and extract user info
        
        # Mock user data
        mock_user = {
            "user_id": "user_123",
            "username": "demo_user",
            "email": "demo@quantaenergi.com",
            "organization_id": "123e4567-e89b-12d3-a456-426614174000",
            "role": "trader",
            "permissions": ["trade_capture", "trade_validation", "trade_confirmation"],
            "is_active": True
        }
        
        return mock_user
        
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get current active user
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        Active user information
        
    Raises:
        HTTPException: If user is not active
    """
    if not current_user.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

async def require_permission(permission: str):
    """
    Decorator to require specific permission
    
    Args:
        permission: Required permission string
        
    Returns:
        Dependency function that checks permissions
    """
    async def check_permission(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_permissions = current_user.get("permissions", [])
        
        if permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        
        return current_user
    
    return check_permission

async def require_role(role: str):
    """
    Decorator to require specific role
    
    Args:
        role: Required role string
        
    Returns:
        Dependency function that checks roles
    """
    async def check_role(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_role = current_user.get("role", "")
        
        if user_role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' required"
            )
        
        return current_user
    
    return check_role

async def get_user_organization(current_user: Dict[str, Any] = Depends(get_current_user)) -> str:
    """
    Get current user's organization ID
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        Organization ID string
    """
    organization_id = current_user.get("organization_id")
    if not organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not associated with any organization"
        )
    return organization_id

# Mock authentication for testing
async def get_current_user_mock() -> Dict[str, Any]:
    """
    Mock current user for testing purposes
    
    Returns:
        Mock user data
    """
    return {
        "user_id": "user_123",
        "username": "demo_user",
        "email": "demo@quantaenergi.com",
        "organization_id": "123e4567-e89b-12d3-a456-426614174000",
        "role": "trader",
        "permissions": ["trade_capture", "trade_validation", "trade_confirmation"],
        "is_active": True
    }
