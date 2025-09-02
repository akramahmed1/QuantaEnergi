"""
Authentication Middleware for Production Security
QuantaEnergi Production Readiness
"""

from fastapi import HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Optional, Any
import jwt
import time
import hashlib
import hmac
import base64
from datetime import datetime, timedelta
import logging
import asyncio
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = "quantaenergi-super-secret-key-2025"  # TODO: Use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Rate limiting configuration
RATE_LIMIT_REQUESTS = 100  # requests per minute
RATE_LIMIT_WINDOW = 60  # seconds

# Initialize security components
security = HTTPBearer(auto_error=False)

class AuthenticationService:
    """Authentication service for QuantaEnergi"""
    
    def __init__(self):
        self.active_tokens = {}  # In production, use Redis
        self.rate_limit_store = {}  # In production, use Redis
        self.blacklisted_tokens = set()  # In production, use Redis
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        try:
            to_encode = data.copy()
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            
            to_encode.update({"exp": expire, "type": "access"})
            encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
            
            # Store token in active tokens
            self.active_tokens[encoded_jwt] = {
                "user_id": data.get("user_id"),
                "expires": expire.isoformat(),
                "created": datetime.utcnow().isoformat()
            }
            
            return encoded_jwt
            
        except Exception as e:
            logger.error(f"Token creation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token creation failed"
            )
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        try:
            to_encode = data.copy()
            expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
            
            to_encode.update({"exp": expire, "type": "refresh"})
            encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
            
            return encoded_jwt
            
        except Exception as e:
            logger.error(f"Refresh token creation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Refresh token creation failed"
            )
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token"""
        try:
            # Check if token is blacklisted
            if token in self.blacklisted_tokens:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been revoked"
                )
            
            # Decode token
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # Check token type
            if payload.get("type") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            # Check if token is expired
            if datetime.utcnow() > datetime.fromtimestamp(payload["exp"]):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )
            
            # Check if token is in active tokens
            if token not in self.active_tokens:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token not found in active tokens"
                )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token verification failed"
            )
    
    def revoke_token(self, token: str) -> bool:
        """Revoke JWT token"""
        try:
            if token in self.active_tokens:
                del self.active_tokens[token]
            
            self.blacklisted_tokens.add(token)
            return True
            
        except Exception as e:
            logger.error(f"Token revocation failed: {e}")
            return False
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """Refresh access token using refresh token"""
        try:
            # Verify refresh token
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token type"
                )
            
            # Create new access token
            user_data = {
                "user_id": payload.get("user_id"),
                "username": payload.get("username"),
                "email": payload.get("email"),
                "roles": payload.get("roles", [])
            }
            
            return self.create_access_token(user_data)
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired"
            )
        except jwt.JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid refresh token: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token refresh failed"
            )

class RateLimiter:
    """Rate limiting service"""
    
    def __init__(self, requests_per_minute: int = RATE_LIMIT_REQUESTS):
        self.requests_per_minute = requests_per_minute
        self.rate_limit_store = {}
    
    def is_rate_limited(self, client_id: str) -> bool:
        """Check if client is rate limited"""
        try:
            current_time = time.time()
            
            if client_id not in self.rate_limit_store:
                self.rate_limit_store[client_id] = {
                    "requests": [],
                    "blocked_until": 0
                }
            
            client_data = self.rate_limit_store[client_id]
            
            # Check if client is blocked
            if current_time < client_data["blocked_until"]:
                return True
            
            # Clean old requests
            client_data["requests"] = [
                req_time for req_time in client_data["requests"]
                if current_time - req_time < 60
            ]
            
            # Check rate limit
            if len(client_data["requests"]) >= self.requests_per_minute:
                # Block client for 5 minutes
                client_data["blocked_until"] = current_time + 300
                return True
            
            # Add current request
            client_data["requests"].append(current_time)
            return False
            
        except Exception as e:
            logger.error(f"Rate limiting check failed: {e}")
            return False
    
    def get_client_id(self, request: Request) -> str:
        """Get client identifier from request"""
        try:
            # Try to get client IP
            client_ip = request.client.host if request.client else "unknown"
            
            # Try to get user agent
            user_agent = request.headers.get("user-agent", "unknown")
            
            # Create client ID hash
            client_string = f"{client_ip}:{user_agent}"
            return hashlib.md5(client_string.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"Client ID generation failed: {e}")
            return "unknown"

# Initialize services
auth_service = AuthenticationService()
rate_limiter = RateLimiter()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current authenticated user"""
    try:
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = credentials.credentials
        payload = auth_service.verify_token(token)
        
        return payload
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

async def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Get current active user"""
    try:
        # Check if user is active
        if not current_user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        return current_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Active user check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User validation failed"
        )

def require_roles(required_roles: list):
    """Decorator to require specific roles"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # This would be implemented in the actual endpoint
            # For now, return the function as is
            return await func(*args, **kwargs)
        return wrapper
    return decorator

async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    try:
        # Get client ID
        client_id = rate_limiter.get_client_id(request)
        
        # Check rate limit
        if rate_limiter.is_rate_limited(client_id):
            return HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Continue with request
        response = await call_next(request)
        return response
        
    except Exception as e:
        logger.error(f"Rate limiting middleware failed: {e}")
        # Continue with request if rate limiting fails
        response = await call_next(request)
        return response

# Authentication endpoints
async def login(username: str, password: str) -> Dict[str, Any]:
    """User login endpoint"""
    try:
        # TODO: Replace with real user authentication
        # Mock user data for demonstration
        if username == "admin" and password == "admin123":
            user_data = {
                "user_id": "admin_001",
                "username": "admin",
                "email": "admin@quantaenergi.com",
                "roles": ["admin", "trader"],
                "is_active": True
            }
            
            # Create tokens
            access_token = auth_service.create_access_token(user_data)
            refresh_token = auth_service.create_refresh_token(user_data)
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "user": user_data
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

async def logout(token: str) -> Dict[str, Any]:
    """User logout endpoint"""
    try:
        # Revoke token
        success = auth_service.revoke_token(token)
        
        if success:
            return {
                "message": "Successfully logged out",
                "timestamp": datetime.utcnow().isoformat()
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

async def refresh_token(refresh_token: str) -> Dict[str, Any]:
    """Refresh access token endpoint"""
    try:
        # Refresh access token
        new_access_token = auth_service.refresh_access_token(refresh_token)
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )
