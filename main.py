from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
from sqlalchemy.future import select

from apis import router_predict, router_quantum, router_iot, router_carbon, router_forecast, router_metrics, router_logs, router_auth, router_webhook
from utils import initialize_ml_model, initialize_rl_model, initialize_pqc_signature, configure_logging
from database import engine

load_dotenv()
configure_logging()
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Startup...")
    initialize_ml_model()
    initialize_rl_model()
    initialize_pqc_signature()
    yield
    logger.info("Shutdown.")

app = FastAPI(title="EnergyOpti-Pro", lifespan=lifespan)

app.include_router(router_auth)
app.include_router(router_predict, prefix="/predict")
app.include_router(router_quantum, prefix="/quantum")
app.include_router(router_iot, prefix="/iot")
app.include_router(router_carbon, prefix="/carbon")
app.include_router(router_forecast, prefix="/forecast")
app.include_router(router_metrics, prefix="/metrics")
app.include_router(router_logs, prefix="/logs")
app.include_router(router_webhook, prefix="/webhook")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/ready")
async def readiness_check():
    try:
        async with engine.connect() as conn:
            await conn.execute(select(1))
        return {"status": "ready"}
    except:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="DB not ready")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)