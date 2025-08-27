from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import structlog

# Configure structured logging
logger = structlog.get_logger()

# Create FastAPI app
app = FastAPI(
    title="EnergyOpti-Pro API",
    description="Next-Generation Energy Trading Platform with AI and Quantum Security",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3003", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check without authentication for monitoring
@app.get("/health")
async def public_health_check():
    """Public health check endpoint"""
    return {
        "status": "healthy",
        "message": "EnergyOpti-Pro is running"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "EnergyOpti-Pro API",
        "version": "2.0.0",
        "status": "running",
        "documentation": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
