from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from prophet import Prophet
import pandas as pd
from datetime import datetime
import uuid
from app.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

class ForecastRequest(BaseModel):
    model_type: str = "prophet"
    period: str
    data_points_required: int

class ForecastResponse(BaseModel):
    forecast_id: str
    data: list

@router.post("/", response_model=ForecastResponse)
async def generate_forecast(request: ForecastRequest, db: AsyncSession = Depends(get_db)):
    historical_data = pd.DataFrame({
        'ds': pd.date_range(start=datetime.now() - pd.Timedelta(days=30), periods=30, freq='D'),
        'y': [100 + i for i in range(30)]
    })
    if len(historical_data) < request.data_points_required:
        raise HTTPException(400, "Insufficient data")
    model = Prophet()
    model.fit(historical_data)
    periods = int(request.period[:-1]) if request.period.endswith(('d', 'h', 'm')) else 1
    future = model.make_future_dataframe(periods=periods, freq=request.period[-1].upper())
    forecast = model.predict(future)
    forecast_data = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods).to_dict(orient='records')
    forecast_id = str(uuid.uuid4())
    return {"forecast_id": forecast_id, "data": forecast_data}