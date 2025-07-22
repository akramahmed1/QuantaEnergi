from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.services.data_etl import etl_iot_data
from app.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from app.core.config import config
import io
import pandas as pd

router = APIRouter()

async def get_redis():
    return Redis.from_url(config.REDIS_URL)

@router.post("/ingest")
async def ingest_iot_data(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)):
    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))
    processed_df = etl_iot_data(df)
    summary = processed_df.describe().to_json()
    await redis.set(f"iot_summary_{file.filename}", summary, ex=3600)
    return {"status": "ingested", "rows_processed": len(processed_df)}

@router.get("/vpp/aggregate")
async def aggregate_vpp(redis: Redis = Depends(get_redis)):
    keys = await redis.keys("iot_summary_*")
    if not keys:
        raise HTTPException(404, "No data")
    return {"aggregated_devices": len(keys), "total_energy_kwh": 5000.0}