"""
QuantaEnergi - Configuration Settings
"""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    DATABASE_URL: str = "postgresql://user:pass@localhost:5432/quanta_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # JWT
    JWT_SECRET: str = "supersecretkeyfornow"
    
    # API
    API_BASE_URL: str = "http://localhost:8000"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()