"""
Production Configuration for QuantaEnergi
Post-Phase 3: Production Readiness & Market Launch
"""

import os
from typing import Optional, Dict, Any
from pydantic import BaseSettings, Field
from datetime import timedelta

class ProductionSettings(BaseSettings):
    """Production configuration settings"""
    
    # Application Settings
    APP_NAME: str = "QuantaEnergi"
    APP_VERSION: str = "4.0.0"
    APP_ENV: str = Field(default="production", env="APP_ENV")
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Server Settings
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    WORKERS: int = Field(default=4, env="WORKERS")
    
    # Security Settings
    SECRET_KEY: str = Field(default="quantaenergi-super-secret-key-2025", env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=60, env="RATE_LIMIT_WINDOW")
    
    # Database Settings
    DATABASE_URL: str = Field(default="postgresql://user:pass@localhost/quantaenergi", env="DATABASE_URL")
    DATABASE_POOL_SIZE: int = Field(default=20, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=30, env="DATABASE_MAX_OVERFLOW")
    DATABASE_POOL_TIMEOUT: int = Field(default=30, env="DATABASE_POOL_TIMEOUT")
    
    # Redis Settings
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    REDIS_POOL_SIZE: int = Field(default=10, env="REDIS_POOL_SIZE")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    
    # Monitoring Settings
    PROMETHEUS_ENABLED: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    GRAFANA_ENABLED: bool = Field(default=True, env="GRAFANA_ENABLED")
    ELK_ENABLED: bool = Field(default=True, env="ELK_ENABLED")
    SENTRY_ENABLED: bool = Field(default=True, env="SENTRY_ENABLED")
    
    # External APIs
    BLOOMBERG_API_KEY: Optional[str] = Field(default=None, env="BLOOMBERG_API_KEY")
    VERRA_API_KEY: Optional[str] = Field(default=None, env="VERRA_API_KEY")
    GOLD_STANDARD_API_KEY: Optional[str] = Field(default=None, env="GOLD_STANDARD_API_KEY")
    
    # Blockchain Settings
    ETHEREUM_NETWORK: str = Field(default="sepolia", env="ETHEREUM_NETWORK")
    ETHEREUM_RPC_URL: str = Field(default="https://sepolia.infura.io/v3/YOUR_PROJECT_ID", env="ETHEREUM_RPC_URL")
    ETHEREUM_PRIVATE_KEY: Optional[str] = Field(default=None, env="ETHEREUM_PRIVATE_KEY")
    
    # Quantum Computing
    QUANTUM_BACKEND: str = Field(default="qutip", env="QUANTUM_BACKEND")
    DWAVE_API_TOKEN: Optional[str] = Field(default=None, env="DWAVE_API_TOKEN")
    DWAVE_SOLVER: str = Field(default="Advantage_system6.4", env="DWAVE_SOLVER")
    
    # AI/ML Settings
    TORCH_DEVICE: str = Field(default="cpu", env="TORCH_DEVICE")
    TRANSFORMERS_CACHE_DIR: str = Field(default="./models", env="TRANSFORMERS_CACHE_DIR")
    MODEL_UPDATE_FREQUENCY: int = Field(default=3600, env="MODEL_UPDATE_FREQUENCY")
    
    # IoT Settings
    MQTT_BROKER: str = Field(default="localhost", env="MQTT_BROKER")
    MQTT_PORT: int = Field(default=1883, env="MQTT_PORT")
    MQTT_USERNAME: Optional[str] = Field(default=None, env="MQTT_USERNAME")
    MQTT_PASSWORD: Optional[str] = Field(default=None, env="MQTT_PASSWORD")
    
    # Logging Settings
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    LOG_FILE: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # CORS Settings
    CORS_ORIGINS: list = Field(default=["*"], env="CORS_ORIGINS")
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    CORS_ALLOW_METHODS: list = Field(default=["*"], env="CORS_ALLOW_METHODS")
    CORS_ALLOW_HEADERS: list = Field(default=["*"], env="CORS_ALLOW_HEADERS")
    
    # Performance Settings
    MAX_CONCURRENT_REQUESTS: int = Field(default=1000, env="MAX_CONCURRENT_REQUESTS")
    REQUEST_TIMEOUT: int = Field(default=30, env="REQUEST_TIMEOUT")
    RESPONSE_CACHE_TTL: int = Field(default=300, env="RESPONSE_CACHE_TTL")
    
    # Compliance Settings
    ISLAMIC_COMPLIANCE_ENABLED: bool = Field(default=True, env="ISLAMIC_COMPLIANCE_ENABLED")
    GDPR_COMPLIANCE_ENABLED: bool = Field(default=True, env="GDPR_COMPLIANCE_ENABLED")
    SOC2_COMPLIANCE_ENABLED: bool = Field(default=True, env="SOC2_COMPLIANCE_ENABLED")
    
    # Market Settings
    DEFAULT_CURRENCY: str = Field(default="USD", env="DEFAULT_CURRENCY")
    DEFAULT_TIMEZONE: str = Field(default="UTC", env="DEFAULT_TIMEZONE")
    TRADING_HOURS_START: str = Field(default="00:00", env="TRADING_HOURS_START")
    TRADING_HOURS_END: str = Field(default="23:59", env="TRADING_HOURS_END")
    
    # Notification Settings
    EMAIL_ENABLED: bool = Field(default=False, env="EMAIL_ENABLED")
    SMS_ENABLED: bool = Field(default=False, env="SMS_ENABLED")
    PUSH_NOTIFICATIONS_ENABLED: bool = Field(default=True, env="PUSH_NOTIFICATIONS_ENABLED")
    
    # Backup Settings
    BACKUP_ENABLED: bool = Field(default=True, env="BACKUP_ENABLED")
    BACKUP_FREQUENCY: str = Field(default="daily", env="BACKUP_FREQUENCY")
    BACKUP_RETENTION_DAYS: int = Field(default=30, env="BACKUP_RETENTION_DAYS")
    
    class Config:
        env_file = ".env.production"
        case_sensitive = True

class DevelopmentSettings(ProductionSettings):
    """Development configuration settings"""
    
    APP_ENV: str = "development"
    DEBUG: bool = True
    HOST: str = "127.0.0.1"
    WORKERS: int = 1
    
    # Use local databases
    DATABASE_URL: str = "postgresql://user:pass@localhost/quantaenergi_dev"
    REDIS_URL: str = "redis://localhost:6379/1"
    
    # Disable external services in development
    PROMETHEUS_ENABLED: bool = False
    GRAFANA_ENABLED: bool = False
    ELK_ENABLED: bool = False
    SENTRY_ENABLED: bool = False
    
    # Use mock external APIs
    BLOOMBERG_API_KEY: Optional[str] = None
    VERRA_API_KEY: Optional[str] = None
    GOLD_STANDARD_API_KEY: Optional[str] = None
    
    # Use testnet for blockchain
    ETHEREUM_NETWORK: str = "sepolia"
    
    # Use CPU for quantum simulations
    QUANTUM_BACKEND: str = "qutip"
    TORCH_DEVICE: str = "cpu"
    
    # Local IoT
    MQTT_BROKER: str = "localhost"
    
    # Development logging
    LOG_LEVEL: str = "DEBUG"
    LOG_FORMAT: str = "text"
    
    # Development CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Development performance
    MAX_CONCURRENT_REQUESTS: int = 100
    REQUEST_TIMEOUT: int = 60
    
    class Config:
        env_file = ".env.development"
        case_sensitive = True

class TestingSettings(ProductionSettings):
    """Testing configuration settings"""
    
    APP_ENV: str = "testing"
    DEBUG: bool = True
    HOST: str = "127.0.0.1"
    WORKERS: int = 1
    
    # Use test databases
    DATABASE_URL: str = "postgresql://user:pass@localhost/quantaenergi_test"
    REDIS_URL: str = "redis://localhost:6379/2"
    
    # Disable external services in testing
    PROMETHEUS_ENABLED: bool = False
    GRAFANA_ENABLED: bool = False
    ELK_ENABLED: bool = False
    SENTRY_ENABLED: bool = False
    
    # Use mock external APIs
    BLOOMBERG_API_KEY: Optional[str] = None
    VERRA_API_KEY: Optional[str] = None
    GOLD_STANDARD_API_KEY: Optional[str] = None
    
    # Use testnet for blockchain
    ETHEREUM_NETWORK: str = "sepolia"
    
    # Use CPU for quantum simulations
    QUANTUM_BACKEND: str = "qutip"
    TORCH_DEVICE: str = "cpu"
    
    # Local IoT
    MQTT_BROKER: str = "localhost"
    
    # Testing logging
    LOG_LEVEL: str = "DEBUG"
    LOG_FORMAT: str = "text"
    
    # Testing CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Testing performance
    MAX_CONCURRENT_REQUESTS: int = 50
    REQUEST_TIMEOUT: int = 120
    
    class Config:
        env_file = ".env.testing"
        case_sensitive = True

def get_settings() -> ProductionSettings:
    """Get configuration settings based on environment"""
    env = os.getenv("APP_ENV", "production").lower()
    
    if env == "development":
        return DevelopmentSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return ProductionSettings()

# Initialize settings
settings = get_settings()

# Configuration validation
def validate_settings() -> Dict[str, Any]:
    """Validate configuration settings"""
    validation_results = {
        "database": False,
        "redis": False,
        "security": False,
        "monitoring": False,
        "external_apis": False,
        "blockchain": False,
        "quantum": False,
        "ai_ml": False,
        "iot": False
    }
    
    try:
        # Validate database URL
        if settings.DATABASE_URL and "postgresql://" in settings.DATABASE_URL:
            validation_results["database"] = True
        
        # Validate Redis URL
        if settings.REDIS_URL and "redis://" in settings.REDIS_URL:
            validation_results["redis"] = True
        
        # Validate security settings
        if settings.SECRET_KEY and len(settings.SECRET_KEY) >= 32:
            validation_results["security"] = True
        
        # Validate monitoring settings
        if any([settings.PROMETHEUS_ENABLED, settings.GRAFANA_ENABLED, 
                settings.ELK_ENABLED, settings.SENTRY_ENABLED]):
            validation_results["monitoring"] = True
        
        # Validate external APIs
        if any([settings.BLOOMBERG_API_KEY, settings.VERRA_API_KEY, 
                settings.GOLD_STANDARD_API_KEY]):
            validation_results["external_apis"] = True
        
        # Validate blockchain settings
        if settings.ETHEREUM_RPC_URL and "infura.io" in settings.ETHEREUM_RPC_URL:
            validation_results["blockchain"] = True
        
        # Validate quantum settings
        if settings.QUANTUM_BACKEND in ["qutip", "dwave", "cirq"]:
            validation_results["quantum"] = True
        
        # Validate AI/ML settings
        if settings.TORCH_DEVICE in ["cpu", "cuda", "mps"]:
            validation_results["ai_ml"] = True
        
        # Validate IoT settings
        if settings.MQTT_BROKER and settings.MQTT_PORT:
            validation_results["iot"] = True
        
    except Exception as e:
        print(f"Configuration validation failed: {e}")
    
    return validation_results

# Configuration summary
def get_config_summary() -> Dict[str, Any]:
    """Get configuration summary"""
    validation = validate_settings()
    
    return {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "app_environment": settings.APP_ENV,
        "debug_mode": settings.DEBUG,
        "server": {
            "host": settings.HOST,
            "port": settings.PORT,
            "workers": settings.WORKERS
        },
        "security": {
            "secret_key_length": len(settings.SECRET_KEY),
            "token_expiry": f"{settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes",
            "rate_limit": f"{settings.RATE_LIMIT_REQUESTS} requests per {settings.RATE_LIMIT_WINDOW} seconds"
        },
        "database": {
            "url": settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else "Not configured",
            "pool_size": settings.DATABASE_POOL_SIZE,
            "max_overflow": settings.DATABASE_MAX_OVERFLOW
        },
        "redis": {
            "url": settings.REDIS_URL.split("@")[-1] if "@" in settings.REDIS_URL else "Not configured",
            "pool_size": settings.REDIS_POOL_SIZE,
            "database": settings.REDIS_DB
        },
        "monitoring": {
            "prometheus": settings.PROMETHEUS_ENABLED,
            "grafana": settings.GRAFANA_ENABLED,
            "elk": settings.ELK_ENABLED,
            "sentry": settings.SENTRY_ENABLED
        },
        "external_apis": {
            "bloomberg": bool(settings.BLOOMBERG_API_KEY),
            "verra": bool(settings.VERRA_API_KEY),
            "gold_standard": bool(settings.GOLD_STANDARD_API_KEY)
        },
        "blockchain": {
            "network": settings.ETHEREUM_NETWORK,
            "rpc_configured": bool(settings.ETHEREUM_RPC_URL and "YOUR_PROJECT_ID" not in settings.ETHEREUM_RPC_URL)
        },
        "quantum": {
            "backend": settings.QUANTUM_BACKEND,
            "dwave_configured": bool(settings.DWAVE_API_TOKEN)
        },
        "ai_ml": {
            "torch_device": settings.TORCH_DEVICE,
            "models_cache": settings.TRANSFORMERS_CACHE_DIR
        },
        "iot": {
            "mqtt_broker": settings.MQTT_BROKER,
            "mqtt_port": settings.MQTT_PORT
        },
        "compliance": {
            "islamic": settings.ISLAMIC_COMPLIANCE_ENABLED,
            "gdpr": settings.GDPR_COMPLIANCE_ENABLED,
            "soc2": settings.SOC2_COMPLIANCE_ENABLED
        },
        "validation": validation,
        "validation_score": sum(validation.values()) / len(validation) * 100
    }
