import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./energyopti_pro.db")
    
    # JWT Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ISSUER: str = "energyopti-pro"
    AUDIENCE: str = "energyopti-pro-users"
    
    # API Keys
    CME_API_KEY: str = os.getenv("CME_API_KEY", "demo_key")
    ICE_API_KEY: str = os.getenv("ICE_API_KEY", "demo_key")
    NYMEX_API_KEY: str = os.getenv("NYMEX_API_KEY", "demo_key")
    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "demo_key")
    
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
    
    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://energyopti-pro-frontend.vercel.app",
        "https://energyopti-pro.vercel.app"
    ]
    
    class Config:
        env_file = ".env"

settings = Settings()
