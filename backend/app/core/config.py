"""
QuantaEnergi - Configuration Settings
Enterprise-grade secure configuration management
"""

import secrets
import os
from pydantic_settings import BaseSettings
from typing import Optional
from cryptography.fernet import Fernet
import structlog

logger = structlog.get_logger()

class SecureSettings(BaseSettings):
    """Enterprise-grade secure application settings"""
    
    # Database Configuration
    DATABASE_URL: str = "postgresql://user:pass@localhost:5432/quanta_db"
    DATABASE_SSL_MODE: str = "require"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 3600
    DATABASE_POOL_PRE_PING: bool = True
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_SSL: bool = True
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    
    # JWT Security Configuration
    JWT_SECRET: str = secrets.token_urlsafe(32)  # Auto-generated secure secret
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ISSUER: str = "quantaenergi.com"
    JWT_AUDIENCE: str = "quantaenergi-api"
    
    # API Security Configuration
    API_BASE_URL: str = "https://localhost:8000"
    API_VERSION: str = "v1"
    CORS_ORIGINS: list = ["https://quantaenergi.com", "https://app.quantaenergi.com"]
    CORS_METHODS: list = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_HEADERS: list = ["Authorization", "Content-Type", "X-Requested-With"]
    
    # Security Configuration
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ENCRYPTION_KEY: str = Fernet.generate_key().decode()
    PASSWORD_HASH_ALGORITHM: str = "bcrypt"
    PASSWORD_MIN_LENGTH: int = 12
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_NUMBERS: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True
    
    # Rate Limiting Configuration
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 100
    RATE_LIMIT_REQUESTS_PER_HOUR: int = 1000
    RATE_LIMIT_REQUESTS_PER_DAY: int = 10000
    RATE_LIMIT_BURST_LIMIT: int = 20
    
    # Security Headers Configuration
    SECURITY_HEADERS_ENABLED: bool = True
    HSTS_MAX_AGE: int = 31536000  # 1 year
    CSP_ENABLED: bool = True
    X_FRAME_OPTIONS: str = "DENY"
    X_CONTENT_TYPE_OPTIONS: str = "nosniff"
    X_XSS_PROTECTION: str = "1; mode=block"
    
    # TLS/SSL Configuration
    TLS_ENABLED: bool = True
    TLS_CERT_PATH: Optional[str] = None
    TLS_KEY_PATH: Optional[str] = None
    TLS_VERIFY_MODE: str = "strict"
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE_PATH: Optional[str] = None
    LOG_ROTATION: str = "daily"
    LOG_RETENTION_DAYS: int = 30
    
    # Monitoring Configuration
    MONITORING_ENABLED: bool = True
    METRICS_ENDPOINT: str = "/metrics"
    HEALTH_CHECK_ENDPOINT: str = "/health"
    PROMETHEUS_ENABLED: bool = True
    
    # Compliance Configuration
    COMPLIANCE_MODE: str = "strict"  # strict, moderate, lenient
    AUDIT_LOGGING_ENABLED: bool = True
    DATA_RETENTION_DAYS: int = 2555  # 7 years for compliance
    ENCRYPTION_AT_REST: bool = True
    ENCRYPTION_IN_TRANSIT: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        validate_assignment = True
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Validate critical security settings
        self._validate_security_settings()
        
        # Log security configuration status
        logger.info("Secure configuration loaded", 
                   jwt_algorithm=self.JWT_ALGORITHM,
                   tls_enabled=self.TLS_ENABLED,
                   rate_limiting_enabled=self.RATE_LIMIT_ENABLED,
                   compliance_mode=self.COMPLIANCE_MODE)
    
    def _validate_security_settings(self):
        """Validate critical security settings"""
        if len(self.JWT_SECRET) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters long")
        
        if not self.TLS_ENABLED:
            logger.warning("TLS is disabled - this is not recommended for production")
        
        if self.COMPLIANCE_MODE == "lenient":
            logger.warning("Compliance mode is lenient - security features may be reduced")
        
        if not self.RATE_LIMIT_ENABLED:
            logger.warning("Rate limiting is disabled - DDoS protection reduced")

# Create secure settings instance
settings = SecureSettings()