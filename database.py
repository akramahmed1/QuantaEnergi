import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import redis.asyncio as redis

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

Base = declarative_base()

AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
async def get_redis_client() -> redis.Redis:
    return redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)