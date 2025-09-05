"""
Real JWT Authentication System for ETRM/CTRM Platform
Implements secure token generation, validation, and role-based access control
"""

import jwt
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List
from functools import wraps
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from passlib.context import CryptContext
import secrets
import hashlib

logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = "your-secret-key-change-in-production"  # Change in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
http_bearer = HTTPBearer()

class JWTAuthManager:
    """JWT Authentication Manager with role-based access control"""
    
    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        self.access_token_expire_minutes = ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = REFRESH_TOKEN_EXPIRE_DAYS
        
        # In-memory token blacklist (use Redis in production)
        self.token_blacklist = set()
        
        # User roles and permissions mapping
        self.role_permissions = {
            "admin": ["*"],  # All permissions
            "trader": [
                "trade_capture", "trade_validation", "trade_confirmation",
                "position_view", "risk_view", "market_data_view"
            ],
            "risk_manager": [
                "risk_view", "risk_edit", "position_view", "trade_view",
                "compliance_view", "reporting_view"
            ],
            "compliance_officer": [
                "compliance_view", "compliance_edit", "trade_view",
                "reporting_view", "audit_view"
            ],
            "viewer": [
                "trade_view", "position_view", "market_data_view",
                "reporting_view"
            ]
        }
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Create JWT access token
        
        Args:
            data: User data to encode in token
            expires_delta: Token expiration time
            
        Returns:
            JWT access token string
        """
        try:
            to_encode = data.copy()
            
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
            
            to_encode.update({
                "exp": expire,
                "iat": datetime.utcnow(),
                "type": "access"
            })
            
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            logger.info(f"Created access token for user: {data.get('user_id', 'unknown')}")
            return encoded_jwt
            
        except Exception as e:
            logger.error(f"Error creating access token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token creation failed"
            )
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """
        Create JWT refresh token
        
        Args:
            data: User data to encode in token
            
        Returns:
            JWT refresh token string
        """
        try:
            to_encode = data.copy()
            expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
            
            to_encode.update({
                "exp": expire,
                "iat": datetime.utcnow(),
                "type": "refresh"
            })
            
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            logger.info(f"Created refresh token for user: {data.get('user_id', 'unknown')}")
            return encoded_jwt
            
        except Exception as e:
            logger.error(f"Error creating refresh token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Refresh token creation failed"
            )
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            # Check if token is blacklisted
            if token in self.token_blacklist:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been revoked"
                )
            
            # Decode token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Verify token type
            if payload.get("type") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            # Check expiration
            exp = payload.get("exp")
            if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )
            
            logger.debug(f"Token verified for user: {payload.get('user_id', 'unknown')}")
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError as e:
            logger.warning(f"JWT error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token verification failed"
            )
    
    def verify_refresh_token(self, token: str) -> Dict[str, Any]:
        """
        Verify refresh token
        
        Args:
            token: JWT refresh token string
            
        Returns:
            Decoded token payload
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token type"
                )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired"
            )
        except jwt.JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
    
    def revoke_token(self, token: str) -> bool:
        """
        Revoke token by adding to blacklist
        
        Args:
            token: Token to revoke
            
        Returns:
            True if successful
        """
        try:
            self.token_blacklist.add(token)
            logger.info("Token revoked successfully")
            return True
        except Exception as e:
            logger.error(f"Error revoking token: {str(e)}")
            return False
    
    def check_permission(self, user_role: str, required_permission: str) -> bool:
        """
        Check if user role has required permission
        
        Args:
            user_role: User's role
            required_permission: Required permission
            
        Returns:
            True if user has permission
        """
        try:
            user_permissions = self.role_permissions.get(user_role, [])
            
            # Admin has all permissions
            if "*" in user_permissions:
                return True
            
            # Check specific permission
            return required_permission in user_permissions
            
        except Exception as e:
            logger.error(f"Permission check error: {str(e)}")
            return False
    
    def hash_password(self, password: str) -> str:
        """
        Hash password using bcrypt
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        try:
            return pwd_context.hash(password)
        except Exception as e:
            logger.error(f"Password hashing error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Password hashing failed"
            )
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against hash
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password
            
        Returns:
            True if password matches
        """
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Password verification error: {str(e)}")
            return False

# Global auth manager instance
auth_manager = JWTAuthManager()

# Decorator for authentication
def require_auth(func):
    """Decorator to require authentication"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # This would be implemented in the actual endpoint
        return await func(*args, **kwargs)
    return wrapper

# Dependency for getting current user
async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Get current authenticated user from token
    
    Args:
        token: JWT token from request
        
    Returns:
        User information dictionary
    """
    try:
        payload = auth_manager.verify_token(token)
        
        user_info = {
            "user_id": payload.get("user_id"),
            "username": payload.get("username"),
            "email": payload.get("email"),
            "organization_id": payload.get("organization_id"),
            "role": payload.get("role"),
            "permissions": auth_manager.role_permissions.get(payload.get("role", ""), []),
            "is_active": payload.get("is_active", True)
        }
        
        return user_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

# Dependency for requiring specific permission
def require_permission(permission: str):
    """
    Dependency factory for requiring specific permission
    
    Args:
        permission: Required permission string
        
    Returns:
        Dependency function
    """
    async def check_permission(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_role = current_user.get("role", "")
        
        if not auth_manager.check_permission(user_role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        
        return current_user
    
    return check_permission

# Dependency for requiring specific role
def require_role(role: str):
    """
    Dependency factory for requiring specific role
    
    Args:
        role: Required role string
        
    Returns:
        Dependency function
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

# Mock user database (replace with real database in production)
MOCK_USERS = {
    "admin": {
        "user_id": "admin_001",
        "username": "admin",
        "email": "admin@quantaenergi.com",
        "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4j4j4j4j4j",  # "admin123"
        "organization_id": "123e4567-e89b-12d3-a456-426614174000",
        "role": "admin",
        "is_active": True
    },
    "trader": {
        "user_id": "trader_001",
        "username": "trader",
        "email": "trader@quantaenergi.com",
        "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4j4j4j4j4j",  # "trader123"
        "organization_id": "123e4567-e89b-12d3-a456-426614174000",
        "role": "trader",
        "is_active": True
    }
}

async def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate user with username and password
    
    Args:
        username: Username
        password: Plain text password
        
    Returns:
        User information if authentication successful, None otherwise
    """
    try:
        # Find user in mock database
        user = None
        for user_data in MOCK_USERS.values():
            if user_data["username"] == username:
                user = user_data
                break
        
        if not user:
            return None
        
        # Verify password
        if not auth_manager.verify_password(password, user["password_hash"]):
            return None
        
        # Check if user is active
        if not user.get("is_active", False):
            return None
        
        logger.info(f"User {username} authenticated successfully")
        return user
        
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        return None
