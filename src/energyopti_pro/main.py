"""
Main application entry point for EnergyOpti-Pro.

This module provides the FastAPI application factory and main entry point
with proper configuration, middleware, and route registration.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram
import structlog
import time
import uuid

from .core.config import settings
from .core.logging import get_logger, set_correlation_id, clear_correlation_id
from .api.v1.router import api_router

# Create logger
logger = get_logger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"]
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.
    
    Handles startup and shutdown events for the FastAPI application.
    """
    # Startup
    logger.info("Starting EnergyOpti-Pro application", version=settings.api.version)
    
    # Initialize services
    await initialize_services()
    
    logger.info("EnergyOpti-Pro application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down EnergyOpti-Pro application")
    await cleanup_services()
    logger.info("EnergyOpti-Pro application shutdown complete")


async def initialize_services() -> None:
    """Initialize application services."""
    try:
        # Initialize database connections
        # Initialize Redis connections
        # Initialize external service connections
        logger.info("Services initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize services", error=str(e))
        raise


async def cleanup_services() -> None:
    """Cleanup application services."""
    try:
        # Close database connections
        # Close Redis connections
        # Close external service connections
        logger.info("Services cleaned up successfully")
    except Exception as e:
        logger.error("Failed to cleanup services", error=str(e))


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI application instance
    """
    # Create FastAPI app
    app = FastAPI(
        title=settings.api.title,
        version=settings.api.version,
        description=settings.api.description,
        docs_url=settings.api.docs_url if settings.debug else None,
        redoc_url=settings.api.redoc_url if settings.debug else None,
        openapi_url=settings.api.openapi_url if settings.debug else None,
        lifespan=lifespan,
    )
    
    # Add middleware
    add_middleware(app)
    
    # Add exception handlers
    add_exception_handlers(app)
    
    # Add routes
    add_routes(app)
    
    return app


def add_middleware(app: FastAPI) -> None:
    """Add middleware to the FastAPI application."""
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.security.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Trusted host middleware
    if settings.is_production:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["energyopti-pro.com", "*.energyopti-pro.com"]
        )
    
    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all HTTP requests with correlation ID."""
        # Generate correlation ID
        correlation_id = str(uuid.uuid4())
        set_correlation_id(correlation_id)
        
        # Add correlation ID to response headers
        response = Response()
        response.headers["X-Correlation-ID"] = correlation_id
        
        # Log request
        start_time = time.time()
        logger.info(
            "HTTP request started",
            method=request.method,
            url=str(request.url),
            correlation_id=correlation_id,
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            logger.info(
                "HTTP request completed",
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                duration=duration,
                correlation_id=correlation_id,
            )
            
            # Update metrics
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code
            ).inc()
            
            REQUEST_DURATION.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(duration)
            
            # Add correlation ID to response
            response.headers["X-Correlation-ID"] = correlation_id
            
            return response
            
        except Exception as e:
            # Log error
            duration = time.time() - start_time
            logger.error(
                "HTTP request failed",
                method=request.method,
                url=str(request.url),
                error=str(e),
                duration=duration,
                correlation_id=correlation_id,
            )
            
            # Update metrics
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status=500
            ).inc()
            
            REQUEST_DURATION.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(duration)
            
            raise
        finally:
            # Clear correlation ID
            clear_correlation_id()


def add_exception_handlers(app: FastAPI) -> None:
    """Add exception handlers to the FastAPI application."""
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Global exception handler."""
        logger.error(
            "Unhandled exception",
            error=str(exc),
            url=str(request.url),
            method=request.method,
        )
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": "An unexpected error occurred",
                "correlation_id": request.headers.get("X-Correlation-ID"),
            }
        )


def add_routes(app: FastAPI) -> None:
    """Add routes to the FastAPI application."""
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "version": settings.api.version,
            "environment": settings.environment,
        }
    
    # Readiness check endpoint
    @app.get("/ready")
    async def readiness_check():
        """Readiness check endpoint."""
        # Check database connectivity
        # Check Redis connectivity
        # Check external services
        return {
            "status": "ready",
            "version": settings.api.version,
            "environment": settings.environment,
        }
    
    # Liveness check endpoint
    @app.get("/live")
    async def liveness_check():
        """Liveness check endpoint."""
        return {
            "status": "alive",
            "version": settings.api.version,
        }
    
    # Metrics endpoint
    @app.get("/metrics")
    async def metrics():
        """Prometheus metrics endpoint."""
        from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )
    
    # API routes
    app.include_router(api_router, prefix="/api/v1")


# Create application instance
app = create_application()


def main() -> None:
    """Main entry point for the application."""
    import uvicorn
    
    # Setup logging
    from .core.logging import setup_logging
    setup_logging(
        level=settings.logging.level,
        format_type=settings.logging.format,
        include_timestamp=settings.logging.include_timestamp,
        include_correlation_id=settings.logging.include_correlation_id,
        log_file=settings.logging.log_file,
    )
    
    # Run application
    uvicorn.run(
        "energyopti_pro.main:app",
        host=settings.api.host,
        port=settings.api.port,
        workers=settings.api.workers,
        reload=settings.api.reload and settings.is_development,
        log_level=settings.logging.level.lower(),
    )


if __name__ == "__main__":
    main()
