from sqlalchemy.ext.asyncio import create_async_engine
from app.db.models import Base
from app.core.config import config

async def init_db():
    engine = create_async_engine(config.DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    import asyncio
    asyncio.run(init_db())