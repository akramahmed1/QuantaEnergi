"""
EnergyOpti-Pro: Disruptive Energy Trading SaaS Platform

Main FastAPI application with organized module structure.
"""

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import structlog
import uvicorn
from contextlib import asynccontextmanager

# Import organized modules
from .core import SecurityMiddleware, SecurityAuditor
from .api import auth_router, disruptive_router, admin_router, energy_data_router
from .db.database import engine, Base
from .schemas.user import User
from .core.security import verify_token

# Configure structured logging
logger = structlog.get_logger()

# Global security auditor instance
security_auditor = SecurityAuditor()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting EnergyOpti-Pro: Disruptive Energy Trading SaaS")
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
    
    # Initialize security components
    try:
        security_auditor.initialize_security_rules()
        logger.info("✅ Security auditor initialized successfully")
    except Exception as e:
        logger.error(f"❌ Security auditor initialization failed: {e}")
    
    logger.info("🎯 EnergyOpti-Pro startup complete")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down EnergyOpti-Pro")

# Create FastAPI app with organized structure
app = FastAPI(
    title="EnergyOpti-Pro: Disruptive Energy Trading SaaS",
    description="""
    Revolutionary SaaS platform that transforms energy trading through cutting-edge AI, 
    quantum computing, blockchain technology, and IoT integration.
    
    ## 🌟 Key Features
    
    * **AI-Powered Forecasting** with Prophet and Grok AI integration
    * **Quantum Portfolio Optimization** using Qiskit algorithms  
    * **Blockchain Smart Contracts** for transparent energy trading
    * **Real-time IoT Integration** for grid and weather data
    * **Multi-Region Compliance** across FERC, Dodd-Frank, REMIT, Islamic Finance
    * **ESG Scoring & Sustainability** metrics for responsible trading
    
    ## 🚀 Getting Started
    
    1. **Authentication**: Use `/api/auth/register` and `/api/auth/login`
    2. **AI Forecasting**: Use `/api/disruptive/ai/forecast`
    3. **Quantum Optimization**: Use `/api/disruptive/quantum/optimize-portfolio`
    4. **Blockchain Contracts**: Use `/api/disruptive/blockchain/deploy-contract`
    5. **IoT Integration**: Use `/api/disruptive/iot/grid-data`
    6. **Compliance**: Use `/api/disruptive/compliance/check`
    
    ## 🔐 Security
    
    * JWT-based authentication with post-quantum cryptography (Kyber)
    * OWASP Top 10 compliance
    * Rate limiting and threat detection
    * Multi-factor authentication support
    """,
    version="2.0.0",
    contact={
        "name": "EnergyOpti-Pro Team",
        "email": "support@energyopti-pro.com",
        "url": "https://energyopti-pro.com"
    },
    license_info={
        "name": "Commercial License",
        "url": "https://energyopti-pro.com/license"
    },
    lifespan=lifespan
)

# Security middleware
app.add_middleware(SecurityMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "https://energyopti-pro-frontend.vercel.app",  # Production frontend
        "https://energyopti-pro.com"  # Custom domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "localhost",
        "127.0.0.1",
        "energyopti-pro-backend.onrender.com",
        "energyopti-pro.com",
        "*.energyopti-pro.com"
    ]
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler with security logging"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # Log security-relevant information
    await security_auditor.audit_request(request)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "request_id": request.headers.get("X-Request-ID", "unknown")
        }
    )

# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "EnergyOpti-Pro Backend",
        "version": "2.0.0",
        "timestamp": "2024-01-01T00:00:00Z"
    }

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with service information"""
    return {
        "message": "Welcome to EnergyOpti-Pro: Disruptive Energy Trading SaaS",
        "version": "2.0.0",
        "status": "operational",
        "features": [
            "AI-Powered Forecasting",
            "Quantum Portfolio Optimization", 
            "Blockchain Smart Contracts",
            "IoT Integration",
            "Multi-Region Compliance",
            "ESG Scoring"
        ],
        "documentation": "/docs",
        "api_status": "/health"
    }

# Include organized API routers
app.include_router(auth_router, tags=["authentication"])
app.include_router(disruptive_router, prefix="/api/disruptive", tags=["disruptive-features"])
app.include_router(admin_router, prefix="/api/admin", tags=["administration"])
app.include_router(energy_data_router, prefix="/api/energy", tags=["energy-data"])

# Dependency for protected endpoints
async def get_current_user(token: str = Depends(verify_token)) -> User:
    """Get current authenticated user"""
    if not token:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return token

# Protected endpoint example
@app.get("/api/protected", tags=["protected"])
async def protected_endpoint(current_user: User = Depends(get_current_user)):
    """Example protected endpoint"""
    return {
        "message": "Access granted to protected resource",
        "user": current_user.email,
        "timestamp": "2024-01-01T00:00:00Z"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main_refactored:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
