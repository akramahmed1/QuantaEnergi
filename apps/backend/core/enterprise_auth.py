"""
Enterprise Authentication & Authorization System
Implements JWT, RBAC, and multi-tenant security
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import secrets
import hashlib

# Security configuration
SECRET_KEY = "quantaenergi_enterprise_secret_key_2024_ultra_secure"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# User roles and permissions
class UserRole:
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    TRADER = "trader"
    RISK_MANAGER = "risk_manager"
    COMPLIANCE_OFFICER = "compliance_officer"
    ANALYST = "analyst"
    VIEWER = "viewer"

class Permission:
    # Trading permissions
    CREATE_TRADE = "create_trade"
    MODIFY_TRADE = "modify_trade"
    DELETE_TRADE = "delete_trade"
    VIEW_TRADES = "view_trades"
    
    # Risk permissions
    VIEW_RISK = "view_risk"
    MODIFY_RISK_LIMITS = "modify_risk_limits"
    APPROVE_TRADES = "approve_trades"
    
    # Compliance permissions
    VIEW_COMPLIANCE = "view_compliance"
    GENERATE_REPORTS = "generate_reports"
    AUDIT_ACCESS = "audit_access"
    
    # Admin permissions
    USER_MANAGEMENT = "user_management"
    SYSTEM_CONFIG = "system_config"
    MARKET_DATA = "market_data"

# Role-based permissions mapping
ROLE_PERMISSIONS = {
    UserRole.SUPER_ADMIN: [
        Permission.CREATE_TRADE, Permission.MODIFY_TRADE, Permission.DELETE_TRADE,
        Permission.VIEW_TRADES, Permission.VIEW_RISK, Permission.MODIFY_RISK_LIMITS,
        Permission.APPROVE_TRADES, Permission.VIEW_COMPLIANCE, Permission.GENERATE_REPORTS,
        Permission.AUDIT_ACCESS, Permission.USER_MANAGEMENT, Permission.SYSTEM_CONFIG,
        Permission.MARKET_DATA
    ],
    UserRole.ADMIN: [
        Permission.CREATE_TRADE, Permission.MODIFY_TRADE, Permission.VIEW_TRADES,
        Permission.VIEW_RISK, Permission.MODIFY_RISK_LIMITS, Permission.APPROVE_TRADES,
        Permission.VIEW_COMPLIANCE, Permission.GENERATE_REPORTS, Permission.USER_MANAGEMENT
    ],
    UserRole.TRADER: [
        Permission.CREATE_TRADE, Permission.MODIFY_TRADE, Permission.VIEW_TRADES,
        Permission.VIEW_RISK
    ],
    UserRole.RISK_MANAGER: [
        Permission.VIEW_TRADES, Permission.VIEW_RISK, Permission.MODIFY_RISK_LIMITS,
        Permission.APPROVE_TRADES, Permission.VIEW_COMPLIANCE, Permission.GENERATE_REPORTS
    ],
    UserRole.COMPLIANCE_OFFICER: [
        Permission.VIEW_TRADES, Permission.VIEW_RISK, Permission.VIEW_COMPLIANCE,
        Permission.GENERATE_REPORTS, Permission.AUDIT_ACCESS
    ],
    UserRole.ANALYST: [
        Permission.VIEW_TRADES, Permission.VIEW_RISK, Permission.VIEW_COMPLIANCE,
        Permission.GENERATE_REPORTS
    ],
    UserRole.VIEWER: [
        Permission.VIEW_TRADES, Permission.VIEW_RISK, Permission.VIEW_COMPLIANCE
    ]
}

# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str
    tenant_id: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    tenant_id: Optional[str]
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int

class LoginRequest(BaseModel):
    username: str
    password: str
    tenant_id: Optional[str] = None

# In-memory user store (replace with database in production)
users_db = {}
sessions_db = {}

# Default admin user
default_admin = {
    "id": "admin_001",
    "username": "admin",
    "email": "admin@quantaenergi.com",
    "hashed_password": pwd_context.hash("QuantaEnergi2024!"),
    "role": UserRole.SUPER_ADMIN,
    "tenant_id": "default",
    "is_active": True,
    "created_at": datetime.now(),
    "last_login": None
}
users_db["admin"] = default_admin

class EnterpriseAuth:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict):
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    def authenticate_user(username: str, password: str, tenant_id: Optional[str] = None) -> Optional[dict]:
        """Authenticate user with username and password"""
        user = users_db.get(username)
        if not user:
            return None
        
        if not EnterpriseAuth.verify_password(password, user["hashed_password"]):
            return None
        
        if not user["is_active"]:
            return None
        
        if tenant_id and user.get("tenant_id") != tenant_id:
            return None
        
        return user
    
    @staticmethod
    def get_user_permissions(role: str) -> List[str]:
        """Get permissions for a user role"""
        return ROLE_PERMISSIONS.get(role, [])
    
    @staticmethod
    def has_permission(user_permissions: List[str], required_permission: str) -> bool:
        """Check if user has required permission"""
        return required_permission in user_permissions

# Dependency functions
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = EnterpriseAuth.verify_token(token)
    username = payload.get("sub")
    
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = users_db.get(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

async def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    """Get current active user"""
    if not current_user.get("is_active"):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def require_permission(permission: str):
    """Decorator to require specific permission"""
    def permission_dependency(current_user: dict = Depends(get_current_active_user)):
        user_permissions = EnterpriseAuth.get_user_permissions(current_user["role"])
        if not EnterpriseAuth.has_permission(user_permissions, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return permission_dependency

# Authentication endpoints
async def login(login_data: LoginRequest) -> Token:
    """Enterprise login with multi-tenant support"""
    user = EnterpriseAuth.authenticate_user(
        login_data.username, 
        login_data.password, 
        login_data.tenant_id
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    user["last_login"] = datetime.now()
    
    # Create tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = EnterpriseAuth.create_access_token(
        data={"sub": user["username"], "role": user["role"], "tenant_id": user.get("tenant_id")},
        expires_delta=access_token_expires
    )
    
    refresh_token = EnterpriseAuth.create_refresh_token(
        data={"sub": user["username"], "role": user["role"], "tenant_id": user.get("tenant_id")}
    )
    
    # Store session
    session_id = secrets.token_urlsafe(32)
    sessions_db[session_id] = {
        "user_id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "tenant_id": user.get("tenant_id"),
        "created_at": datetime.now(),
        "last_activity": datetime.now()
    }
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

async def refresh_token(refresh_token: str) -> Token:
    """Refresh access token using refresh token"""
    payload = EnterpriseAuth.verify_token(refresh_token)
    
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    username = payload.get("sub")
    user = users_db.get(username)
    
    if not user or not user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = EnterpriseAuth.create_access_token(
        data={"sub": user["username"], "role": user["role"], "tenant_id": user.get("tenant_id")},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

async def logout(current_user: dict = Depends(get_current_active_user)):
    """Logout user and invalidate session"""
    # In production, add token to blacklist
    return {"message": "Successfully logged out"}

async def get_user_profile(current_user: dict = Depends(get_current_active_user)) -> UserResponse:
    """Get current user profile"""
    return UserResponse(
        id=current_user["id"],
        username=current_user["username"],
        email=current_user["email"],
        role=current_user["role"],
        tenant_id=current_user.get("tenant_id"),
        is_active=current_user["is_active"],
        created_at=current_user["created_at"],
        last_login=current_user.get("last_login")
    )
