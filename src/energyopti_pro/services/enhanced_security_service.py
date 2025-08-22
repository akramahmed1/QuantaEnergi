"""
Enhanced Security Service for EnergyOpti-Pro.

Implements JWT RBAC, Kyber post-quantum cryptography, audit logging, and rate limiting.
"""

import asyncio
import hashlib
import hmac
import json
import time
from typing import Dict, Any, Optional, List, Set, Union
from datetime import datetime, timezone, timedelta
import structlog
from dataclasses import dataclass, asdict
from enum import Enum
import jwt
from passlib.context import CryptContext
import secrets

# Post-quantum cryptography
try:
    from liboqs import KeyEncapsulation
    OQS_AVAILABLE = True
except ImportError:
    OQS_AVAILABLE = False
    print("liboqs not available, using mock post-quantum crypto")

logger = structlog.get_logger()

class Permission(Enum):
    """System permissions."""
    READ_MARKET_DATA = "read_market_data"
    WRITE_MARKET_DATA = "write_market_data"
    READ_TRADING_DATA = "read_trading_data"
    WRITE_TRADING_DATA = "write_trading_data"
    READ_RISK_DATA = "read_risk_data"
    WRITE_RISK_DATA = "write_risk_data"
    READ_COMPLIANCE_DATA = "read_compliance_data"
    WRITE_COMPLIANCE_DATA = "write_compliance_data"
    READ_AI_ML_DATA = "read_ai_ml_data"
    WRITE_AI_ML_DATA = "write_ai_ml_data"
    READ_USER_DATA = "read_user_data"
    WRITE_USER_DATA = "write_user_data"
    ADMIN = "admin"

class Role(Enum):
    """User roles."""
    VIEWER = "viewer"
    TRADER = "trader"
    ANALYST = "analyst"
    RISK_MANAGER = "risk_manager"
    COMPLIANCE_OFFICER = "compliance_officer"
    ADMIN = "admin"
    SYSTEM = "system"

@dataclass
class User:
    """User entity."""
    id: str
    username: str
    email: str
    role: Role
    permissions: Set[Permission]
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None

@dataclass
class AuditLog:
    """Audit log entry."""
    id: str
    user_id: str
    action: str
    resource: str
    details: Dict[str, Any]
    ip_address: str
    user_agent: str
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None

@dataclass
class SecurityEvent:
    """Security event."""
    id: str
    event_type: str
    severity: str
    description: str
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    timestamp: datetime
    metadata: Dict[str, Any]

class RateLimiter:
    """Rate limiting implementation."""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = {}
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed."""
        current_time = time.time()
        
        # Clean old requests
        if identifier in self.requests:
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if current_time - req_time < self.window_seconds
            ]
        else:
            self.requests[identifier] = []
        
        # Check if under limit
        if len(self.requests[identifier]) < self.max_requests:
            self.requests[identifier].append(current_time)
            return True
        
        return False
    
    def get_remaining(self, identifier: str) -> int:
        """Get remaining requests for identifier."""
        current_time = time.time()
        
        if identifier in self.requests:
            valid_requests = [
                req_time for req_time in self.requests[identifier]
                if current_time - req_time < self.window_seconds
            ]
            return max(0, self.max_requests - len(valid_requests))
        
        return self.max_requests

class PostQuantumCrypto:
    """Post-quantum cryptography using Kyber."""
    
    def __init__(self):
        self.kem = None
        self.public_key = None
        self.secret_key = None
        
        if OQS_AVAILABLE:
            self._initialize_kyber()
    
    def _initialize_kyber(self):
        """Initialize Kyber key encapsulation mechanism."""
        try:
            self.kem = KeyEncapsulation("Kyber1024")
            self.secret_key = self.kem.generate_keypair()
            self.public_key = self.kem.export_public_key()
            logger.info("Kyber post-quantum cryptography initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Kyber: {e}")
            self.kem = None
    
    def encrypt(self, plaintext: str) -> Dict[str, Any]:
        """Encrypt data using Kyber."""
        if not self.kem or not self.public_key:
            return self._mock_encrypt(plaintext)
        
        try:
            # Generate shared secret
            ciphertext, shared_secret = self.kem.encap_secret(self.public_key)
            
            # Use shared secret to encrypt plaintext (simplified)
            encrypted_data = self._encrypt_with_secret(plaintext, shared_secret)
            
            return {
                "status": "quantum",
                "ciphertext": ciphertext.hex(),
                "encrypted_data": encrypted_data,
                "algorithm": "Kyber1024",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Kyber encryption failed: {e}")
            return self._mock_encrypt(plaintext)
    
    def decrypt(self, ciphertext: str, encrypted_data: str) -> Optional[str]:
        """Decrypt data using Kyber."""
        if not self.kem or not self.secret_key:
            return self._mock_decrypt(encrypted_data)
        
        try:
            # Decapsulate shared secret
            shared_secret = self.kem.decap_secret(bytes.fromhex(ciphertext), self.secret_key)
            
            # Decrypt data using shared secret
            decrypted_data = self._decrypt_with_secret(encrypted_data, shared_secret)
            
            return decrypted_data
            
        except Exception as e:
            logger.error(f"Kyber decryption failed: {e}")
            return self._mock_decrypt(encrypted_data)
    
    def _encrypt_with_secret(self, plaintext: str, shared_secret: bytes) -> str:
        """Encrypt data using shared secret (simplified)."""
        # In real implementation, use proper symmetric encryption
        secret_hash = hashlib.sha256(shared_secret).digest()
        encrypted = ""
        for i, char in enumerate(plaintext):
            encrypted += chr(ord(char) ^ secret_hash[i % len(secret_hash)])
        return encrypted.encode().hex()
    
    def _decrypt_with_secret(self, encrypted_data: str, shared_secret: bytes) -> str:
        """Decrypt data using shared secret (simplified)."""
        # In real implementation, use proper symmetric decryption
        secret_hash = hashlib.sha256(shared_secret).digest()
        encrypted_bytes = bytes.fromhex(encrypted_data)
        decrypted = ""
        for i, byte in enumerate(encrypted_bytes):
            decrypted += chr(byte ^ secret_hash[i % len(secret_hash)])
        return decrypted
    
    def _mock_encrypt(self, plaintext: str) -> Dict[str, Any]:
        """Mock encryption when Kyber is not available."""
        return {
            "status": "mock",
            "ciphertext": "mock_ciphertext",
            "encrypted_data": plaintext.encode().hex(),
            "algorithm": "mock",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _mock_decrypt(self, encrypted_data: str) -> str:
        """Mock decryption when Kyber is not available."""
        return bytes.fromhex(encrypted_data).decode()

class EnhancedSecurityService:
    """Enhanced security service with comprehensive protection."""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Initialize components
        self.post_quantum_crypto = PostQuantumCrypto()
        self.rate_limiters: Dict[str, RateLimiter] = {}
        
        # User management
        self.users: Dict[str, User] = {}
        self.user_tokens: Dict[str, Dict[str, Any]] = {}  # token -> user_info
        
        # Audit logging
        self.audit_logs: List[AuditLog] = []
        self.security_events: List[SecurityEvent] = []
        
        # Initialize default users
        self._initialize_default_users()
        
        # Security settings
        self.max_failed_logins = 5
        self.lockout_duration = timedelta(minutes=15)
        self.token_expiry = timedelta(hours=1)
        self.refresh_token_expiry = timedelta(days=7)
    
    def _initialize_default_users(self):
        """Initialize default system users."""
        admin_user = User(
            id="admin_001",
            username="admin",
            email="admin@energyopti-pro.com",
            role=Role.ADMIN,
            permissions={Permission.ADMIN},
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        
        system_user = User(
            id="system_001",
            username="system",
            email="system@energyopti-pro.com",
            role=Role.SYSTEM,
            permissions={Permission.ADMIN},
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        
        self.users[admin_user.id] = admin_user
        self.users[system_user.id] = system_user
        
        # Set default passwords (in production, use secure defaults)
        self._set_user_password(admin_user.id, "admin123")
        self._set_user_password(system_user.id, "system123")
    
    def _set_user_password(self, user_id: str, password: str):
        """Set user password hash."""
        if user_id in self.users:
            hashed_password = self.password_context.hash(password)
            # Store hash in user object (in real implementation, use database)
            setattr(self.users[user_id], 'password_hash', hashed_password)
    
    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        role: Role,
        permissions: Optional[Set[Permission]] = None
    ) -> User:
        """Create a new user."""
        user_id = f"user_{len(self.users) + 1:03d}"
        
        if permissions is None:
            permissions = self._get_default_permissions(role)
        
        user = User(
            id=user_id,
            username=username,
            email=email,
            role=role,
            permissions=permissions,
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        
        # Set password
        self._set_user_password(user_id, password)
        
        # Store user
        self.users[user_id] = user
        
        # Log creation
        self._log_audit_event(
            user_id="system",
            action="create_user",
            resource=f"user:{user_id}",
            details={"username": username, "email": email, "role": role.value},
            ip_address="system",
            user_agent="system",
            success=True
        )
        
        logger.info(f"Created user: {username} with role {role.value}")
        return user
    
    def _get_default_permissions(self, role: Role) -> Set[Permission]:
        """Get default permissions for a role."""
        if role == Role.ADMIN:
            return {Permission.ADMIN}
        elif role == Role.TRADER:
            return {
                Permission.READ_MARKET_DATA,
                Permission.READ_TRADING_DATA,
                Permission.WRITE_TRADING_DATA,
                Permission.READ_RISK_DATA
            }
        elif role == Role.ANALYST:
            return {
                Permission.READ_MARKET_DATA,
                Permission.READ_TRADING_DATA,
                Permission.READ_RISK_DATA,
                Permission.READ_AI_ML_DATA
            }
        elif role == Role.RISK_MANAGER:
            return {
                Permission.READ_MARKET_DATA,
                Permission.READ_TRADING_DATA,
                Permission.READ_RISK_DATA,
                Permission.WRITE_RISK_DATA
            }
        elif role == Role.COMPLIANCE_OFFICER:
            return {
                Permission.READ_MARKET_DATA,
                Permission.READ_TRADING_DATA,
                Permission.READ_COMPLIANCE_DATA,
                Permission.WRITE_COMPLIANCE_DATA
            }
        else:  # VIEWER
            return {
                Permission.READ_MARKET_DATA,
                Permission.READ_TRADING_DATA
            }
    
    def authenticate_user(self, username: str, password: str, ip_address: str) -> Optional[str]:
        """Authenticate user and return JWT token."""
        # Find user
        user = None
        for u in self.users.values():
            if u.username == username:
                user = u
                break
        
        if not user:
            self._log_security_event(
                "failed_login",
                "high",
                f"Failed login attempt for unknown user: {username}",
                ip_address=ip_address
            )
            return None
        
        # Check if account is locked
        if user.locked_until and datetime.now(timezone.utc) < user.locked_until:
            self._log_security_event(
                "account_locked",
                "medium",
                f"Login attempt to locked account: {username}",
                user_id=user.id,
                ip_address=ip_address
            )
            return None
        
        # Verify password
        if not hasattr(user, 'password_hash'):
            self._log_security_event(
                "authentication_error",
                "high",
                f"User {username} has no password hash",
                user_id=user.id,
                ip_address=ip_address
            )
            return None
        
        if not self.password_context.verify(password, user.password_hash):
            # Increment failed attempts
            user.failed_login_attempts += 1
            
            # Check if account should be locked
            if user.failed_login_attempts >= self.max_failed_logins:
                user.locked_until = datetime.now(timezone.utc) + self.lockout_duration
                self._log_security_event(
                    "account_locked",
                    "high",
                    f"Account locked due to multiple failed attempts: {username}",
                    user_id=user.id,
                    ip_address=ip_address
                )
            
            self._log_audit_event(
                user_id=user.id,
                action="failed_login",
                resource="auth",
                details={"username": username, "failed_attempts": user.failed_login_attempts},
                ip_address=ip_address,
                user_agent="unknown",
                success=False,
                error_message="Invalid password"
            )
            return None
        
        # Reset failed attempts on successful login
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.now(timezone.utc)
        
        # Generate JWT token
        token = self._generate_jwt_token(user)
        
        # Store token info
        self.user_tokens[token] = {
            "user_id": user.id,
            "username": user.username,
            "role": user.role.value,
            "permissions": [p.value for p in user.permissions],
            "created_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + self.token_expiry
        }
        
        # Log successful login
        self._log_audit_event(
            user_id=user.id,
            action="login",
            resource="auth",
            details={"username": username},
            ip_address=ip_address,
            user_agent="unknown",
            success=True
        )
        
        logger.info(f"User {username} authenticated successfully")
        return token
    
    def _generate_jwt_token(self, user: User) -> str:
        """Generate JWT token for user."""
        payload = {
            "user_id": user.id,
            "username": user.username,
            "role": user.role.value,
            "permissions": [p.value for p in user.permissions],
            "exp": datetime.now(timezone.utc) + self.token_expiry,
            "iat": datetime.now(timezone.utc)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return user info."""
        try:
            # Decode token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check if token is in our store
            if token not in self.user_tokens:
                return None
            
            # Check if token has expired
            if datetime.now(timezone.utc) > self.user_tokens[token]["expires_at"]:
                del self.user_tokens[token]
                return None
            
            return self.user_tokens[token]
            
        except jwt.ExpiredSignatureError:
            # Clean up expired token
            if token in self.user_tokens:
                del self.user_tokens[token]
            return None
        except jwt.InvalidTokenError:
            return None
    
    def check_permission(self, token: str, permission: Permission) -> bool:
        """Check if user has specific permission."""
        user_info = self.verify_token(token)
        if not user_info:
            return False
        
        # Admin has all permissions
        if Permission.ADMIN.value in user_info["permissions"]:
            return True
        
        return permission.value in user_info["permissions"]
    
    def refresh_token(self, token: str) -> Optional[str]:
        """Refresh JWT token."""
        user_info = self.verify_token(token)
        if not user_info:
            return None
        
        # Generate new token
        new_token = self._generate_jwt_token(self.users[user_info["user_id"]])
        
        # Update token store
        self.user_tokens[new_token] = {
            **user_info,
            "created_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + self.token_expiry
        }
        
        # Remove old token
        del self.user_tokens[token]
        
        return new_token
    
    def revoke_token(self, token: str) -> bool:
        """Revoke JWT token."""
        if token in self.user_tokens:
            del self.user_tokens[token]
            return True
        return False
    
    def encrypt_sensitive_data(self, data: str) -> Dict[str, Any]:
        """Encrypt sensitive data using post-quantum cryptography."""
        return self.post_quantum_crypto.encrypt(data)
    
    def decrypt_sensitive_data(self, ciphertext: str, encrypted_data: str) -> Optional[str]:
        """Decrypt sensitive data using post-quantum cryptography."""
        return self.post_quantum_crypto.decrypt(ciphertext, encrypted_data)
    
    def check_rate_limit(self, identifier: str, limit_type: str = "default") -> bool:
        """Check rate limiting for identifier."""
        if limit_type not in self.rate_limiters:
            # Create rate limiter based on type
            if limit_type == "api":
                self.rate_limiters[limit_type] = RateLimiter(100, 60)  # 100 requests per minute
            elif limit_type == "login":
                self.rate_limiters[limit_type] = RateLimiter(5, 300)   # 5 attempts per 5 minutes
            else:
                self.rate_limiters[limit_type] = RateLimiter(1000, 60)  # 1000 requests per minute
        
        return self.rate_limiters[limit_type].is_allowed(identifier)
    
    def _log_audit_event(
        self,
        user_id: str,
        action: str,
        resource: str,
        details: Dict[str, Any],
        ip_address: str,
        user_agent: str,
        success: bool,
        error_message: Optional[str] = None
    ):
        """Log audit event."""
        audit_log = AuditLog(
            id=f"audit_{len(self.audit_logs) + 1:06d}",
            user_id=user_id,
            action=action,
            resource=resource,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.now(timezone.utc),
            success=success,
            error_message=error_message
        )
        
        self.audit_logs.append(audit_log)
        
        # Log to structured logger
        if success:
            logger.info(
                "Audit event",
                user_id=user_id,
                action=action,
                resource=resource,
                ip_address=ip_address
            )
        else:
            logger.warning(
                "Audit event failed",
                user_id=user_id,
                action=action,
                resource=resource,
                ip_address=ip_address,
                error=error_message
            )
    
    def _log_security_event(
        self,
        event_type: str,
        severity: str,
        description: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log security event."""
        security_event = SecurityEvent(
            id=f"sec_{len(self.security_events) + 1:06d}",
            event_type=event_type,
            severity=severity,
            description=description,
            user_id=user_id,
            ip_address=ip_address,
            timestamp=datetime.now(timezone.utc),
            metadata=metadata or {}
        )
        
        self.security_events.append(security_event)
        
        # Log to structured logger
        if severity == "high":
            logger.error(
                "Security event",
                event_type=event_type,
                severity=severity,
                description=description,
                user_id=user_id,
                ip_address=ip_address
            )
        else:
            logger.warning(
                "Security event",
                event_type=event_type,
                severity=severity,
                description=description,
                user_id=user_id,
                ip_address=ip_address
            )
    
    def get_audit_logs(
        self,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """Get filtered audit logs."""
        logs = self.audit_logs
        
        if user_id:
            logs = [log for log in logs if log.user_id == user_id]
        
        if action:
            logs = [log for log in logs if log.action == action]
        
        if start_time:
            logs = [log for log in logs if log.timestamp >= start_time]
        
        if end_time:
            logs = [log for log in logs if log.timestamp <= end_time]
        
        # Sort by timestamp (newest first) and limit
        logs.sort(key=lambda x: x.timestamp, reverse=True)
        return logs[:limit]
    
    def get_security_events(
        self,
        event_type: Optional[str] = None,
        severity: Optional[str] = None,
        start_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[SecurityEvent]:
        """Get filtered security events."""
        events = self.security_events
        
        if event_type:
            events = [event for event in events if event.event_type == event_type]
        
        if severity:
            events = [event for event in events if event.severity == severity]
        
        if start_time:
            events = [event for event in events if event.timestamp >= start_time]
        
        # Sort by timestamp (newest first) and limit
        events.sort(key=lambda x: x.timestamp, reverse=True)
        return events[:limit]
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get security service status."""
        return {
            "status": "active",
            "post_quantum_crypto": OQS_AVAILABLE,
            "total_users": len(self.users),
            "active_tokens": len(self.user_tokens),
            "total_audit_logs": len(self.audit_logs),
            "total_security_events": len(self.security_events),
            "rate_limiters": list(self.rate_limiters.keys()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# Global security service instance
_security_service: Optional[EnhancedSecurityService] = None

def get_security_service(secret_key: str = "your-secret-key-change-in-production") -> EnhancedSecurityService:
    """Get global security service instance."""
    global _security_service
    if _security_service is None:
        _security_service = EnhancedSecurityService(secret_key)
    return _security_service
