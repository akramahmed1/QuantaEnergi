import asyncio
import csv
from datetime import datetime, timedelta
import random
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import AsyncSessionLocal
from app.db.models import User, EmissionFactor
from app.services.security import hash_password

async def seed_data():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Seed users
            users = [
                {"username": "trader_ahmed", "email": "trader_ahmed@eop.com", "password": "traderpass", "role": "trader"},
                {"username": "analyst_sara", "email": "analyst_sara@eop.com", "password": "analystpass", "role": "analyst"},
            ]
            for user_data in users:
                user = User(
                    username=user_data["username"],
                    email=user_data["email"],
                    hashed_password=hash_password(user_data["password"]),
                    role=user_data["role"],
                    is_active=True
                )
                session.add(user)
            print("Seeded users")

            # Seed emission factors
            emission_factors = [
                {"country_code": "US", "factor_kgco2e_per_kwh": 0.4, "source": "EPA", "year": 2023},
                {"country_code": "DE", "factor_kgco2e_per_kwh": 0.35, "source": "UBA", "year": 2023},
            ]
            for ef_data in emission_factors:
                ef = EmissionFactor(
                    country_code=ef_data["country_code"],
                    factor_kgco2e_per_kwh=ef_data["factor_kgco2e_per_kwh"],
                    source=ef_data["source"],
                    year=ef_data["year"]
                )
                session.add(ef)
            print("Seeded emission factors")

    # Generate pilot_iot_data.csv
    with open("pilot_iot_data.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["timestamp", "device_id", "energy_kwh", "location"])
        start_time = datetime.now() - timedelta(days=7)
        for i in range(100):
            timestamp = start_time + timedelta(hours=i)
            writer.writerow([
                timestamp.isoformat(),
                f"device_{random.randint(1, 10)}",
                round(random.uniform(0.1, 10.0), 2),
                random.choice(["US", "DE"])
            ])
    print("Generated pilot_iot_data.csv")

if __name__ == "__main__":
    asyncio.run(seed_data())