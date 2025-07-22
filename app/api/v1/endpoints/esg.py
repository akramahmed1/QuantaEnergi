from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.db.database import get_db
from app.db.models import EmissionFactor
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

class ESGRequest(BaseModel):
    energy_consumption_kwh: float
    country_code: str

@router.post("/footprint")
async def calculate_footprint(request: ESGRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EmissionFactor.factor_kgco2e_per_kwh).where(EmissionFactor.country_code == request.country_code))
    factor = result.scalar()
    if factor is None:
        raise HTTPException(404, "Factor not found")
    emissions = request.energy_consumption_kwh * factor
    return {"carbon_emissions_kgCO2e": emissions}