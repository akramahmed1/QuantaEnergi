"""
Comprehensive Error Handling Middleware for QuantaEnergi FastAPI
Provides centralized error handling with custom JSON responses, logging, and monitoring
"""

import traceback
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Union
from enum import Enum

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
from redis.exceptions import RedisError
import structlog

# Configure structured logging
logger = structlog.get_logger(__name__)


class ErrorCode(str, Enum):
    """Standardized error codes for the application"""
    # Authentication & Authorization
    AUTH_INVALID_CREDENTIALS = "AUTH_INVALID_CREDENTIALS"
    AUTH_TOKEN_EXPIRED = "AUTH_TOKEN_EXPIRED"
    AUTH_TOKEN_INVALID = "AUTH_TOKEN_INVALID"
    AUTH_INSUFFICIENT_PERMISSIONS = "AUTH_INSUFFICIENT_PERMISSIONS"
    
    # Validation Errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    
    # Business Logic Errors
    TRADE_NOT_FOUND = "TRADE_NOT_FOUND"
    INSUFFICIENT_BALANCE = "INSUFFICIENT_BALANCE"
    INVALID_TRADE_STATE = "INVALID_TRADE_STATE"
    CREDIT_LIMIT_EXCEEDED = "CREDIT_LIMIT_EXCEEDED"
    
    # External Service Errors
    EXTERNAL_API_ERROR = "EXTERNAL_API_ERROR"
    MARKET_DATA_UNAVAILABLE = "MARKET_DATA_UNAVAILABLE"
    WEATHER_API_ERROR = "WEATHER_API_ERROR"
    
    # System Errors
    DATABASE_ERROR = "DATABASE_ERROR"
    REDIS_ERROR = "REDIS_ERROR"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"


class QuantaEnergiError(Exception):
    """Base exception class for QuantaEnergi application"""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        self.cause = cause
        super().__init__(self.message)


class AuthenticationError(QuantaEnergiError):
    """Authentication related errors"""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(
            message=message,
            error_code=ErrorCode.AUTH_INVALID_CREDENTIALS,
            status_code=status.HTTP_401_UNAUTHORIZED,
            **kwargs
        )


class AuthorizationError(QuantaEnergiError):
    """Authorization related errors"""
    
    def __init__(self, message: str = "Insufficient permissions", **kwargs):
        super().__init__(
            message=message,
            error_code=ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS,
            status_code=status.HTTP_403_FORBIDDEN,
            **kwargs
        )


class ValidationError(QuantaEnergiError):
    """Validation related errors"""
    
    def __init__(self, message: str = "Validation failed", **kwargs):
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            **kwargs
        )


class BusinessLogicError(QuantaEnergiError):
    """Business logic related errors"""
    
    def __init__(self, message: str, error_code: ErrorCode, **kwargs):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_400_BAD_REQUEST,
            **kwargs
        )


class ExternalServiceError(QuantaEnergiError):
    """External service related errors"""
    
    def __init__(self, message: str, error_code: ErrorCode, **kwargs):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_502_BAD_GATEWAY,
            **kwargs
        )


def create_error_response(
    error: Exception,
    request: Request,
    error_id: str,
    include_traceback: bool = False
) -> JSONResponse:
    """
    Create standardized error response
    
    Args:
        error: The exception that occurred
        request: FastAPI request object
        error_id: Unique error identifier for tracking
        include_traceback: Whether to include traceback in response (dev only)
    
    Returns:
        JSONResponse with standardized error format
    """
    # Base error response structure
    error_response = {
        "error": {
            "id": error_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": str(error),
            "path": str(request.url.path),
            "method": request.method,
            "user_agent": request.headers.get("user-agent", ""),
            "ip_address": request.client.host if request.client else None,
        },
        "request_id": request.headers.get("x-request-id", ""),
        "correlation_id": request.headers.get("x-correlation-id", "")
    }
    
    # Add specific error details based on error type
    if isinstance(error, QuantaEnergiError):
        error_response["error"].update({
            "code": error.error_code.value,
            "details": error.details,
            "status_code": error.status_code
        })
        status_code = error.status_code
    elif isinstance(error, HTTPException):
        error_response["error"].update({
            "code": ErrorCode.VALIDATION_ERROR.value,
            "details": {"detail": error.detail},
            "status_code": error.status_code
        })
        status_code = error.status_code
    elif isinstance(error, RequestValidationError):
        error_response["error"].update({
            "code": ErrorCode.VALIDATION_ERROR.value,
            "details": {"validation_errors": error.errors()},
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY
        })
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    elif isinstance(error, SQLAlchemyError):
        error_response["error"].update({
            "code": ErrorCode.DATABASE_ERROR.value,
            "details": {"database_error": str(error)},
            "status_code": status.HTTP_503_SERVICE_UNAVAILABLE
        })
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif isinstance(error, RedisError):
        error_response["error"].update({
            "code": ErrorCode.REDIS_ERROR.value,
            "details": {"redis_error": str(error)},
            "status_code": status.HTTP_503_SERVICE_UNAVAILABLE
        })
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    else:
        error_response["error"].update({
            "code": ErrorCode.INTERNAL_SERVER_ERROR.value,
            "details": {},
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR
        })
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    # Add traceback in development mode
    if include_traceback and status_code >= 500:
        error_response["error"]["traceback"] = traceback.format_exc()
    
    return JSONResponse(
        status_code=status_code,
        content=error_response,
        headers={
            "X-Error-ID": error_id,
            "X-Request-ID": request.headers.get("x-request-id", ""),
        }
    )


async def quantaenergi_exception_handler(request: Request, exc: QuantaEnergiError) -> JSONResponse:
    """Handle QuantaEnergi custom exceptions"""
    error_id = str(uuid.uuid4())
    
    # Log the error with structured logging
    logger.error(
        "QuantaEnergi error occurred",
        error_id=error_id,
        error_code=exc.error_code.value,
        message=exc.message,
        path=request.url.path,
        method=request.method,
        status_code=exc.status_code,
        details=exc.details,
        user_id=request.headers.get("x-user-id"),
        correlation_id=request.headers.get("x-correlation-id")
    )
    
    return create_error_response(exc, request, error_id)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions"""
    error_id = str(uuid.uuid4())
    
    logger.warning(
        "HTTP exception occurred",
        error_id=error_id,
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path,
        method=request.method,
        user_id=request.headers.get("x-user-id"),
        correlation_id=request.headers.get("x-correlation-id")
    )
    
    return create_error_response(exc, request, error_id)


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation errors"""
    error_id = str(uuid.uuid4())
    
    logger.warning(
        "Validation error occurred",
        error_id=error_id,
        validation_errors=exc.errors(),
        path=request.url.path,
        method=request.method,
        user_id=request.headers.get("x-user-id"),
        correlation_id=request.headers.get("x-correlation-id")
    )
    
    return create_error_response(exc, request, error_id)


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle SQLAlchemy database errors"""
    error_id = str(uuid.uuid4())
    
    logger.error(
        "Database error occurred",
        error_id=error_id,
        error_type=type(exc).__name__,
        error_message=str(exc),
        path=request.url.path,
        method=request.method,
        user_id=request.headers.get("x-user-id"),
        correlation_id=request.headers.get("x-correlation-id")
    )
    
    return create_error_response(exc, request, error_id)


async def redis_exception_handler(request: Request, exc: RedisError) -> JSONResponse:
    """Handle Redis errors"""
    error_id = str(uuid.uuid4())
    
    logger.error(
        "Redis error occurred",
        error_id=error_id,
        error_type=type(exc).__name__,
        error_message=str(exc),
        path=request.url.path,
        method=request.method,
        user_id=request.headers.get("x-user-id"),
        correlation_id=request.headers.get("x-correlation-id")
    )
    
    return create_error_response(exc, request, error_id)


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other unhandled exceptions"""
    error_id = str(uuid.uuid4())
    
    logger.error(
        "Unhandled exception occurred",
        error_id=error_id,
        error_type=type(exc).__name__,
        error_message=str(exc),
        path=request.url.path,
        method=request.method,
        user_id=request.headers.get("x-user-id"),
        correlation_id=request.headers.get("x-correlation-id"),
        traceback=traceback.format_exc()
    )
    
    # Include traceback in development
    include_traceback = request.headers.get("x-debug-mode") == "true"
    return create_error_response(exc, request, error_id, include_traceback)


def setup_error_handlers(app):
    """
    Setup all error handlers for the FastAPI application
    
    Args:
        app: FastAPI application instance
    """
    # Add custom exception handlers
    app.add_exception_handler(QuantaEnergiError, quantaenergi_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(RedisError, redis_exception_handler)
    
    # Add general exception handler as fallback
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Error handlers configured successfully")


# Utility functions for common error scenarios
def raise_authentication_error(message: str = "Authentication failed", **kwargs):
    """Raise authentication error"""
    raise AuthenticationError(message, **kwargs)


def raise_authorization_error(message: str = "Insufficient permissions", **kwargs):
    """Raise authorization error"""
    raise AuthorizationError(message, **kwargs)


def raise_validation_error(message: str = "Validation failed", **kwargs):
    """Raise validation error"""
    raise ValidationError(message, **kwargs)


def raise_business_logic_error(message: str, error_code: ErrorCode, **kwargs):
    """Raise business logic error"""
    raise BusinessLogicError(message, error_code, **kwargs)


def raise_external_service_error(message: str, error_code: ErrorCode, **kwargs):
    """Raise external service error"""
    raise ExternalServiceError(message, error_code, **kwargs)
