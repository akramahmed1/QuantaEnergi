"""
Authentication and Authorization Module
Enterprise-grade JWT authentication with comprehensive security
"""

import jwt
import bcrypt
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from passlib.hash import bcrypt
import structlog
from ..core.config import settings

logger = structlog.get_logger()

# Security scheme with auto_error disabled for custom handling
security = HTTPBearer(auto_error=False)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class JWTAuthManager:
    """Enterprise-grade JWT authentication manager"""
    
    def __init__(self):
        self.secret_key = settings.JWT_SECRET
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire_minutes = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        self.issuer = settings.JWT_ISSUER
        self.audience = settings.JWT_AUDIENCE
        
        # Role-based permissions mapping
        self.role_permissions = {
            "admin": [
                "trade_capture", "trade_validation", "trade_confirmation",
                "portfolio_management", "risk_management", "compliance_monitoring",
                "user_management", "system_admin", "audit_access"
            ],
            "trader": [
                "trade_capture", "trade_validation", "trade_confirmation",
                "portfolio_management", "risk_management"
            ],
            "compliance_officer": [
                "compliance_monitoring", "audit_access", "trade_validation",
                "risk_management"
            ],
            "risk_manager": [
                "risk_management", "portfolio_management", "trade_validation"
            ],
            "viewer": [
                "read_only"
            ]
        }
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create JWT access token with security claims"""
        to_encode = data.copy()
        
        # Add security claims
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "iss": self.issuer,
            "aud": self.audience,
            "type": "access"
        })
        
        # Add security headers
        headers = {
            "alg": self.algorithm,
            "typ": "JWT",
            "kid": "quantaenergi-key-1"  # Key ID for key rotation
        }
        
        encoded_jwt = jwt.encode(
            to_encode, 
            self.secret_key, 
            algorithm=self.algorithm,
            headers=headers
        )
        
        logger.info("Access token created", 
                   user_id=data.get("user_id"),
                   expires_at=expire.isoformat())
        
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "iss": self.issuer,
            "aud": self.audience,
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(
            to_encode, 
            self.secret_key, 
            algorithm=self.algorithm
        )
        
        logger.info("Refresh token created", 
                   user_id=data.get("user_id"),
                   expires_at=expire.isoformat())
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token with comprehensive validation"""
        try:
            # Decode token with all security checks
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                issuer=self.issuer,
                audience=self.audience,
                options={
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_iss": True,
                    "verify_aud": True,
                    "require_exp": True,
                    "require_iat": True
                }
            )
            
            # Validate token type
            if payload.get("type") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            # Check if user is active (would check database in production)
            if not payload.get("is_active", True):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User account is inactive"
                )
            
            # Check if token is not blacklisted (would check Redis in production)
            # This would be implemented with a token blacklist system
            
            logger.debug("Token verified successfully", 
                        user_id=payload.get("user_id"))
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            logger.warning("Invalid token", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        except Exception as e:
            logger.error("Token verification error", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token verification failed"
            )
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_user_permissions(self, role: str) -> List[str]:
        """Get permissions for a user role"""
        return self.role_permissions.get(role, ["read_only"])

# Global JWT auth manager
auth_manager = JWTAuthManager()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Get current authenticated user from JWT token with comprehensive validation
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        Dict containing user information
        
    Raises:
        HTTPException: If authentication fails
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Verify JWT token
        payload = auth_manager.verify_token(credentials.credentials)
        
        # Extract user information
        user_info = {
            "user_id": payload.get("user_id"),
            "username": payload.get("username"),
            "email": payload.get("email"),
            "organization_id": payload.get("organization_id"),
            "role": payload.get("role"),
            "permissions": auth_manager.get_user_permissions(payload.get("role", "viewer")),
            "is_active": payload.get("is_active", True),
            "token_issued_at": payload.get("iat"),
            "token_expires_at": payload.get("exp"),
            "session_id": payload.get("session_id")
        }
        
        # Validate required fields
        if not user_info["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user information in token"
            )
        
        logger.info("User authenticated successfully", 
                   user_id=user_info["user_id"],
                   role=user_info["role"])
        
        return user_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Authentication error", error=str(e))
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
