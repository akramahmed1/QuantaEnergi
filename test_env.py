from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class TestConfig(BaseSettings):
    SECRET_KEY: str
    DATABASE_URL: str
    REDIS_URL: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    LOG_LEVEL: str
    PQC_ALGORITHM: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

config = TestConfig()
print(config.SECRET_KEY)
print(config.DATABASE_URL)
print(config.REDIS_URL)
print(config.POSTGRES_DB)
print(config.POSTGRES_USER)
print(config.POSTGRES_PASSWORD)
print(config.LOG_LEVEL)
print(config.PQC_ALGORITHM)