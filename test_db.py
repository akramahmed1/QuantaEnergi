import asyncpg
import asyncio

async def test():
    try:
        conn = await asyncpg.connect('postgresql://energyuser:energypassword@localhost:5432/energyoptipro_db')
        print('Connected')
        await conn.close()
    except Exception as e:
        print(f"Connection failed: {str(e)}")

asyncio.run(test())