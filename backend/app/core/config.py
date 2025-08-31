import os
from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./quantaenergi.db")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "quantaenergi")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "user")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password")
    
    # JWT Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    ISSUER: str = os.getenv("ISSUER", "quantaenergi")
    AUDIENCE: str = os.getenv("AUDIENCE", "quantaenergi-users")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    
    # Blockchain (Infura)
    INFURA_URL: str = os.getenv("INFURA_URL", "https://mainnet.infura.io/v3/your_key")
    WEB3_PROVIDER_URI: str = os.getenv("WEB3_PROVIDER_URI", "https://mainnet.infura.io/v3/your_key")
    
    # IoT & External APIs
    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "demo_key")
    OPENWEATHER_BASE_URL: str = os.getenv("OPENWEATHER_BASE_URL", "https://api.openweathermap.org/data/2.5")
    
    # API Keys
    CME_API_KEY: str = os.getenv("CME_API_KEY", "demo_key")
    ICE_API_KEY: str = os.getenv("ICE_API_KEY", "demo_key")
    NYMEX_API_KEY: str = os.getenv("NYMEX_API_KEY", "demo_key")
    
    # Quantum Security
    QUANTUM_SECURITY_ENABLED: bool = os.getenv("QUANTUM_SECURITY_ENABLED", "true").lower() == "true"
    
    # Feature Flags
    GENERATIVE_AI_ENABLED: bool = os.getenv("GENERATIVE_AI_ENABLED", "false").lower() == "true"
    QUANTUM_HARDWARE_ENABLED: bool = os.getenv("QUANTUM_HARDWARE_ENABLED", "false").lower() == "true"
    OPTIMIZATION_ENGINE_ENABLED: bool = os.getenv("OPTIMIZATION_ENGINE_ENABLED", "false").lower() == "true"
    
    # External APIs
    GROK_API_KEY: Optional[str] = os.getenv("GROK_API_KEY")
    IBMQ_TOKEN: Optional[str] = os.getenv("IBMQ_TOKEN")
    
    # Billing
    STRIPE_SECRET_KEY: Optional[str] = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET: Optional[str] = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))
    ENABLE_RATE_LIMITING: bool = os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://quantaenergi-frontend.vercel.app",
        "https://quantaenergi.vercel.app"
    ]
    
    # Monitoring
    PROMETHEUS_MULTIPROC_DIR: str = os.getenv("PROMETHEUS_MULTIPROC_DIR", "/tmp")
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    
    # Security
    ENABLE_HTTPS: bool = os.getenv("ENABLE_HTTPS", "true").lower() == "true"
    
    # Development
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"
        extra = "allow"  # Allow extra fields from .env

settings = Settings()
