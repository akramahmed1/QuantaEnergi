from fastapi import APIRouter
from .endpoints import auth, esg, forecast, iot, predict, quantum

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(esg.router, prefix="/esg", tags=["ESG"])
api_router.include_router(forecast.router, prefix="/forecast", tags=["Forecasting"])
api_router.include_router(iot.router, prefix="/iot", tags=["IoT & VPP"])
api_router.include_router(predict.router, prefix="/predict", tags=["Predictive Analytics (RL)"])
api_router.include_router(quantum.router, prefix="/quantum", tags=["Quantum Trading"])