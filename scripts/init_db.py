import asyncio
from database import create_db_and_tables

async def main():
    await create_db_and_tables()

if __name__ == "__main__":
    asyncio.run(main())