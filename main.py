import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core import config
from app.core.security import initialize_pqc_system
from app.api.v1.router import api_router
from app.db.database import init_db, shutdown_db
from app.services import ai_services
from app.graphql.schema import graphql_app

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(level=config.LOG_LEVEL)
    logger = logging.getLogger(__name__)
    logger.info("Initializing EnergyOpti-Pro")
    initialize_pqc_system()
    await init_db()
    await ai_services.load_core_models()
    yield
    logger.info("Shutting down EnergyOpti-Pro")
    await shutdown_db()

app = FastAPI(
    title="EnergyOpti-Pro",
    description="Next-Gen SaaS for Energy Optimization. Launch: July 20, 2025.",
    version="2.3.0",
    lifespan=lifespan,
    docs_url="/explorer"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
async def root():
    return {"message": "Welcome to EnergyOpti-Pro"}