"""
Authentication API Endpoints
QuantaEnergi Production Readiness
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from ...middleware.auth import (
    auth_service, 
    get_current_user, 
    get_current_active_user,
    login as auth_login,
    logout as auth_logout,
    refresh_token as auth_refresh_token
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Pydantic models
class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    full_name: str
    company: Optional[str] = None
    role: str = "trader"

class UserResponse(BaseModel):
    user_id: str
    username: str
    email: str
    full_name: str
    company: Optional[str] = None
    roles: list
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: UserResponse

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    token: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class ResetPasswordRequest(BaseModel):
    email: str

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None

# Mock user database - in production, use PostgreSQL
MOCK_USERS = {
    "admin": {
        "user_id": "admin_001",
        "username": "admin",
        "email": "admin@quantaenergi.com",
        "password_hash": "admin123",  # In production, use bcrypt
        "full_name": "System Administrator",
        "company": "QuantaEnergi",
        "roles": ["admin", "trader", "compliance"],
        "is_active": True,
        "created_at": datetime.now(),
        "last_login": None,
        "phone": "+1-555-0123",
        "country": "USA",
        "timezone": "UTC-5"
    },
    "trader1": {
        "user_id": "trader_001",
        "username": "trader1",
        "email": "trader1@quantaenergi.com",
        "password_hash": "trader123",
        "full_name": "John Trader",
        "company": "Energy Corp",
        "roles": ["trader"],
        "is_active": True,
        "created_at": datetime.now(),
        "last_login": None,
        "phone": "+1-555-0124",
        "country": "USA",
        "timezone": "UTC-5"
    },
    "compliance1": {
        "user_id": "compliance_001",
        "username": "compliance1",
        "email": "compliance1@quantaenergi.com",
        "password_hash": "compliance123",
        "full_name": "Sarah Compliance",
        "company": "Energy Corp",
        "roles": ["compliance", "risk"],
        "is_active": True,
        "created_at": datetime.now(),
        "last_login": None,
        "phone": "+1-555-0125",
        "country": "USA",
        "timezone": "UTC-5"
    }
}

@router.post("/login", response_model=TokenResponse)
async def user_login(user_credentials: UserLogin):
    """User login endpoint"""
    try:
        # Validate credentials
        if user_credentials.username not in MOCK_USERS:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        user = MOCK_USERS[user_credentials.username]
        
        if user_credentials.password != user["password_hash"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        if not user["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is inactive"
            )
        
        # Update last login
        user["last_login"] = datetime.now()
        
        # Create tokens
        access_token = auth_service.create_access_token({
            "user_id": user["user_id"],
            "username": user["username"],
            "email": user["email"],
            "roles": user["roles"]
        })
        
        refresh_token = auth_service.create_refresh_token({
            "user_id": user["user_id"],
            "username": user["username"],
            "email": user["email"],
            "roles": user["roles"]
        })
        
        # Create user response
        user_response = UserResponse(
            user_id=user["user_id"],
            username=user["username"],
            email=user["email"],
            full_name=user["full_name"],
            company=user["company"],
            roles=user["roles"],
            is_active=user["is_active"],
            created_at=user["created_at"],
            last_login=user["last_login"]
        )
        
        logger.info(f"User {user_credentials.username} logged in successfully")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=1800,  # 30 minutes
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed for user {user_credentials.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/register", response_model=UserResponse)
async def user_register(user_data: UserRegister):
    """User registration endpoint"""
    try:
        # Check if username already exists
        if user_data.username in MOCK_USERS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        # Check if email already exists
        for user in MOCK_USERS.values():
            if user["email"] == user_data.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )
        
        # Validate role
        valid_roles = ["trader", "compliance", "risk", "admin"]
        if user_data.role not in valid_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
            )
        
        # Create new user
        new_user_id = f"user_{len(MOCK_USERS) + 1:03d}"
        new_user = {
            "user_id": new_user_id,
            "username": user_data.username,
            "email": user_data.email,
            "password_hash": user_data.password,  # In production, hash with bcrypt
            "full_name": user_data.full_name,
            "company": user_data.company,
            "roles": [user_data.role],
            "is_active": True,
            "created_at": datetime.now(),
            "last_login": None,
            "phone": None,
            "country": None,
            "timezone": "UTC"
        }
        
        # Add to mock database
        MOCK_USERS[user_data.username] = new_user
        
        logger.info(f"User {user_data.username} registered successfully")
        
        return UserResponse(
            user_id=new_user["user_id"],
            username=new_user["username"],
            email=new_user["email"],
            full_name=new_user["full_name"],
            company=new_user["company"],
            roles=new_user["roles"],
            is_active=new_user["is_active"],
            created_at=new_user["created_at"],
            last_login=new_user["last_login"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/refresh", response_model=Dict[str, Any])
async def refresh_access_token(refresh_request: RefreshTokenRequest):
    """Refresh access token endpoint"""
    try:
        # Refresh access token
        new_access_token = auth_service.refresh_access_token(refresh_request.refresh_token)
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": 1800  # 30 minutes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.post("/logout")
async def user_logout(logout_request: LogoutRequest):
    """User logout endpoint"""
    try:
        # Revoke token
        success = auth_service.revoke_token(logout_request.token)
        
        if success:
            logger.info("User logged out successfully")
            return {
                "message": "Successfully logged out",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Logout failed"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """Get current user profile"""
    try:
        username = current_user.get("username")
        if username not in MOCK_USERS:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user = MOCK_USERS[username]
        
        return UserResponse(
            user_id=user["user_id"],
            username=user["username"],
            email=user["email"],
            full_name=user["full_name"],
            company=user["company"],
            roles=user["roles"],
            is_active=user["is_active"],
            created_at=user["created_at"],
            last_login=user["last_login"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user profile"
        )

@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    profile_update: UserProfileUpdate,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Update current user profile"""
    try:
        username = current_user.get("username")
        if username not in MOCK_USERS:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user = MOCK_USERS[username]
        
        # Update profile fields
        if profile_update.full_name is not None:
            user["full_name"] = profile_update.full_name
        
        if profile_update.company is not None:
            user["company"] = profile_update.company
        
        if profile_update.phone is not None:
            user["phone"] = profile_update.phone
        
        if profile_update.country is not None:
            user["country"] = profile_update.country
        
        if profile_update.timezone is not None:
            user["timezone"] = profile_update.timezone
        
        logger.info(f"User {username} profile updated successfully")
        
        return UserResponse(
            user_id=user["user_id"],
            username=user["username"],
            email=user["email"],
            full_name=user["full_name"],
            company=user["company"],
            roles=user["roles"],
            is_active=user["is_active"],
            created_at=user["created_at"],
            last_login=user["last_login"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )

@router.post("/change-password")
async def change_password(
    password_request: ChangePasswordRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Change user password"""
    try:
        username = current_user.get("username")
        if username not in MOCK_USERS:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user = MOCK_USERS[username]
        
        # Verify current password
        if password_request.current_password != user["password_hash"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        user["password_hash"] = password_request.new_password
        
        logger.info(f"User {username} password changed successfully")
        
        return {
            "message": "Password changed successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to change password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )

@router.post("/reset-password")
async def reset_password(reset_request: ResetPasswordRequest):
    """Reset user password (send reset email)"""
    try:
        # Find user by email
        user_found = None
        for user in MOCK_USERS.values():
            if user["email"] == reset_request.email:
                user_found = user
                break
        
        if not user_found:
            # Don't reveal if email exists or not
            logger.info(f"Password reset requested for email: {reset_request.email}")
            return {
                "message": "If the email exists, a password reset link has been sent",
                "timestamp": datetime.now().isoformat()
            }
        
        # In production, send reset email
        # TODO: Implement email sending service
        
        logger.info(f"Password reset email sent to {reset_request.email}")
        
        return {
            "message": "Password reset email sent",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Password reset failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed"
        )

@router.get("/users", response_model=list[UserResponse])
async def get_all_users(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get all users (admin only)"""
    try:
        # Check if user has admin role
        if "admin" not in current_user.get("roles", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        users = []
        for user in MOCK_USERS.values():
            users.append(UserResponse(
                user_id=user["user_id"],
                username=user["username"],
                email=user["email"],
                full_name=user["full_name"],
                company=user["company"],
                roles=user["roles"],
                is_active=user["is_active"],
                created_at=user["created_at"],
                last_login=user["last_login"]
            ))
        
        return users
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get all users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get users"
        )

@router.get("/health")
async def auth_health():
    """Authentication service health check"""
    try:
        return {
            "status": "healthy",
            "service": "authentication",
            "timestamp": datetime.now().isoformat(),
            "message": "Authentication service is operational",
            "active_tokens": len(auth_service.active_tokens),
            "blacklisted_tokens": len(auth_service.blacklisted_tokens)
        }
    except Exception as e:
        logger.error(f"Authentication health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "authentication",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
