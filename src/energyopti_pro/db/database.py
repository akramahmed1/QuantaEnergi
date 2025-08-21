from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from ..core.config import settings

# Get database URL from settings
DATABASE_URL = settings.get_database_url(async_driver=True)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.database.echo,
    pool_size=settings.database.pool_size,
    max_overflow=settings.database.max_overflow,
    pool_timeout=settings.database.pool_timeout,
    pool_recycle=settings.database.pool_recycle
)

# Create async session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Import Base from models to avoid circular imports
from .models import Base

async def get_db():
    """Get database session."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()