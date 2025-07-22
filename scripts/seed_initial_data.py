import asyncio
import pandas as pd
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import async_session, Base
from app.db.models import User, EmissionFactor
from app.core.security import get_password_hash
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PILOT_USERS = [
    {"username": "trader_ahmed@eop", "email": "trader_ahmed@eop", "password": "E0P@Tr@d3r!", "role": "trader"},
    # Add others as per history
]

EMISSION_FACTORS = [
    {"country_code": "US", "factor_kgco2e_per_kwh": 0.43, "source": "EPA 2023", "year": 2023},
    # Add others
]

def generate_pilot_iot_data(filename="pilot_iot_data.csv"):
    time_index = pd.date_range(start=datetime.now() - timedelta(days=365), end=datetime.now(), freq='H')
    n_points = len(time_index)
    values = 500 + 100 * np.sin(2 * np.pi * np.arange(n_points) / (24 * 7)) + np.linspace(0, 50, n_points) + np.random.normal(0, 25, n_points)
    df = pd.DataFrame({'timestamp': time_index, 'value': values})
    df.to_csv(filename, index=False)
    logger.info("Data generated")
    return df

async def seed_database():
    async with async_session() as db:
        async with db.begin():
            for user_data in PILOT_USERS:
                result = await db.execute(select(User).where(User.email == user_data["email"]))
                if not result.scalar():
                    hashed = get_password_hash(user_data["password"])
                    db.add(User(username=user_data["username"], email=user_data["email"], hashed_password=hashed, role=user_data["role"], is_active=True))
            for factor in EMISSION_FACTORS:
                result = await db.execute(select(EmissionFactor).where(EmissionFactor.country_code == factor["country_code"]))
                if not result.scalar():
                    db.add(EmissionFactor(**factor))
        await db.commit()
        logger.info("Seeded")

async def main():
    await seed_database()
    generate_pilot_iot_data()

if __name__ == "__main__":
    asyncio.run(main())