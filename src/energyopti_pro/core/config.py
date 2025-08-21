"""
Configuration management for EnergyOpti-Pro.

This module provides centralized configuration management using Pydantic Settings
with environment variable support, validation, and type safety.
"""

from functools import lru_cache
from typing import Any, Dict, List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    model_config = SettingsConfigDict(env_prefix="DB_")
    
    url: str = Field(default="postgresql://user:password@localhost/energyopti_pro")
    pool_size: int = Field(default=20, ge=1, le=100)
    max_overflow: int = Field(default=30, ge=0)
    pool_timeout: int = Field(default=30, ge=1)
    pool_recycle: int = Field(default=3600, ge=0)
    echo: bool = Field(default=False)
    
    @validator("url")
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format."""
        if not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError("Database URL must be a valid PostgreSQL URL")
        return v


class RedisSettings(BaseSettings):
    """Redis configuration settings."""
    
    model_config = SettingsConfigDict(env_prefix="REDIS_")
    
    url: str = Field(default="redis://localhost:6379/0")
    max_connections: int = Field(default=20, ge=1, le=100)
    socket_timeout: int = Field(default=5, ge=1)
    socket_connect_timeout: int = Field(default=5, ge=1)
    retry_on_timeout: bool = Field(default=True)
    health_check_interval: int = Field(default=30, ge=1)


class SecuritySettings(BaseSettings):
    """Security configuration settings."""
    
    model_config = SettingsConfigDict(env_prefix="SECURITY_")
    
    secret_key: str = Field(default="your-secret-key-change-in-production")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30, ge=1)
    refresh_token_expire_days: int = Field(default=7, ge=1)
    bcrypt_rounds: int = Field(default=12, ge=10, le=16)
    cors_origins: List[str] = Field(default=["http://localhost:3000"])
    rate_limit_requests: int = Field(default=100, ge=1)
    rate_limit_window: int = Field(default=60, ge=1)  # seconds
    
    @validator("secret_key")
    def validate_secret_key(cls, v: str) -> str:
        """Validate secret key strength."""
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        return v


class APISettings(BaseSettings):
    """API configuration settings."""
    
    model_config = SettingsConfigDict(env_prefix="API_")
    
    title: str = Field(default="EnergyOpti-Pro API")
    version: str = Field(default="1.0.0")
    description: str = Field(default="Next-Generation SaaS for Energy Optimization")
    docs_url: str = Field(default="/docs")
    redoc_url: str = Field(default="/redoc")
    openapi_url: str = Field(default="/openapi.json")
    debug: bool = Field(default=False)
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000, ge=1, le=65535)
    workers: int = Field(default=1, ge=1)
    reload: bool = Field(default=False)


class LoggingSettings(BaseSettings):
    """Logging configuration settings."""
    
    model_config = SettingsConfigDict(env_prefix="LOGGING_")
    
    level: str = Field(default="INFO")
    format: str = Field(default="json")
    include_timestamp: bool = Field(default=True)
    include_correlation_id: bool = Field(default=True)
    log_file: Optional[str] = Field(default=None)
    max_file_size: int = Field(default=100, ge=1)  # MB
    backup_count: int = Field(default=5, ge=0)

# US Market Data Settings
class PJMSettings(BaseSettings):
    """PJM Interconnection API configuration settings."""
    
    model_config = SettingsConfigDict(env_prefix="PJM_")
    
    api_key: Optional[str] = Field(default=None)
    base_url: str = Field(default="https://api.pjm.com/api/v1")
    rate_limit_delay: float = Field(default=0.1, ge=0.01)
    timeout: int = Field(default=30, ge=1)
    max_retries: int = Field(default=3, ge=0)
    cache_duration: int = Field(default=300, ge=1)  # 5 minutes

class RECSettings(BaseSettings):
    """Renewable Energy Certificate (REC) configuration settings."""
    
    model_config = SettingsConfigDict(env_prefix="REC_")
    
    mrets_api_key: Optional[str] = Field(default=None)
    nar_api_key: Optional[str] = Field(default=None)
    wregis_api_key: Optional[str] = Field(default=None)
    nepool_api_key: Optional[str] = Field(default=None)
    pjm_api_key: Optional[str] = Field(default=None)
    ercot_api_key: Optional[str] = Field(default=None)
    caiso_api_key: Optional[str] = Field(default=None)
    nyiso_api_key: Optional[str] = Field(default=None)
    default_registry: str = Field(default="mrets")
    compliance_deadline: str = Field(default="march_31")

class HenryHubSettings(BaseSettings):
    """Henry Hub natural gas futures configuration settings."""
    
    model_config = SettingsConfigDict(env_prefix="HENRY_HUB_")
    
    api_key: Optional[str] = Field(default=None)
    base_url: str = Field(default="https://api.cmegroup.com/v1")
    rate_limit_delay: float = Field(default=0.1, ge=0.01)
    timeout: int = Field(default=30, ge=1)
    max_retries: int = Field(default=3, ge=0)
    cache_duration: int = Field(default=300, ge=1)  # 5 minutes
    default_hub: str = Field(default="henry_hub")
    
    @validator("level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()


class MonitoringSettings(BaseSettings):
    """Monitoring and observability settings."""
    
    model_config = SettingsConfigDict(env_prefix="MONITORING_")
    
    enabled: bool = Field(default=True)
    metrics_port: int = Field(default=9090, ge=1, le=65535)
    health_check_path: str = Field(default="/health")
    readiness_path: str = Field(default="/ready")
    liveness_path: str = Field(default="/live")
    sentry_dsn: Optional[str] = Field(default=None)
    prometheus_enabled: bool = Field(default=True)
    jaeger_enabled: bool = Field(default=False)
    jaeger_host: str = Field(default="localhost")
    jaeger_port: int = Field(default=6831, ge=1, le=65535)


class IslamicFinanceSettings(BaseSettings):
    """Islamic finance configuration settings."""
    
    model_config = SettingsConfigDict(env_prefix="ISLAMIC_")
    
    enabled: bool = Field(default=True)
    zakat_rate: float = Field(default=0.025, ge=0, le=1)  # 2.5%
    nisab_threshold_usd: float = Field(default=5000.0, ge=0)
    gold_price_api_url: str = Field(default="https://api.metals.live/v1/spot/gold")
    silver_price_api_url: str = Field(default="https://api.metals.live/v1/spot/silver")
    prayer_times_api_url: str = Field(default="http://api.aladhan.com/v1/timings")
    ramadan_calendar_enabled: bool = Field(default=True)
    sharia_board_approval_required: bool = Field(default=True)


class TradingSettings(BaseSettings):
    """Trading and market data settings."""
    
    model_config = SettingsConfigDict(env_prefix="TRADING_")
    
    enabled: bool = Field(default=True)
    default_region: str = Field(default="ME")
    supported_regions: List[str] = Field(default=["ME", "US", "UK", "EU", "GUYANA"])
    market_data_cache_ttl: int = Field(default=300, ge=1)  # seconds
    order_timeout: int = Field(default=30, ge=1)  # seconds
    max_order_size: float = Field(default=1000000.0, ge=0)
    risk_limits_enabled: bool = Field(default=True)
    var_confidence_level: float = Field(default=0.95, ge=0.5, le=0.99)
    stress_test_scenarios: List[str] = Field(default=["market_crash", "liquidity_crisis"])


class Settings(BaseSettings):
    """Main application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Environment
    environment: str = Field(default="development")
    debug: bool = Field(default=False)
    
    # Sub-settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    api: APISettings = Field(default_factory=APISettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)
    islamic_finance: IslamicFinanceSettings = Field(default_factory=IslamicFinanceSettings)
    trading: TradingSettings = Field(default_factory=TradingSettings)
    
    # US Market Data settings
    pjm: PJMSettings = Field(default_factory=PJMSettings)
    rec: RECSettings = Field(default_factory=RECSettings)
    henry_hub: HenryHubSettings = Field(default_factory=HenryHubSettings)
    
    @validator("environment")
    def validate_environment(cls, v: str) -> str:
        """Validate environment name."""
        valid_environments = ["development", "staging", "production", "testing"]
        if v.lower() not in valid_environments:
            raise ValueError(f"Environment must be one of: {valid_environments}")
        return v.lower()
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.environment == "testing"
    
    def get_database_url(self, async_driver: bool = True) -> str:
        """Get database URL with optional async driver."""
        if async_driver and not self.database.url.startswith("postgresql+asyncpg://"):
            return self.database.url.replace("postgresql://", "postgresql+asyncpg://")
        return self.database.url
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return {
            "environment": self.environment,
            "debug": self.debug,
            "database": self.database.model_dump(),
            "redis": self.redis.model_dump(),
            "security": self.security.model_dump(),
            "api": self.api.model_dump(),
            "logging": self.logging.model_dump(),
            "monitoring": self.monitoring.model_dump(),
            "islamic_finance": self.islamic_finance.model_dump(),
            "trading": self.trading.model_dump(),
            "pjm": self.pjm.model_dump(),
            "rec": self.rec.model_dump(),
            "henry_hub": self.henry_hub.model_dump(),
        }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()