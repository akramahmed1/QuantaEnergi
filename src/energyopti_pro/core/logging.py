"""
Logging configuration for EnergyOpti-Pro.

This module provides structured logging with correlation IDs, JSON formatting,
and integration with monitoring systems.
"""

import logging
import sys
from contextvars import ContextVar
from typing import Any, Dict, Optional

import structlog
from structlog.stdlib import LoggerFactory

# Correlation ID context variable
correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)


def get_correlation_id() -> Optional[str]:
    """Get current correlation ID from context."""
    return correlation_id.get()


def set_correlation_id(corr_id: str) -> None:
    """Set correlation ID in context."""
    correlation_id.set(corr_id)


def clear_correlation_id() -> None:
    """Clear correlation ID from context."""
    correlation_id.set(None)


def add_correlation_id(_, __, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add correlation ID to log event."""
    corr_id = get_correlation_id()
    if corr_id:
        event_dict["correlation_id"] = corr_id
    return event_dict


def setup_logging(
    level: str = "INFO",
    format_type: str = "json",
    include_timestamp: bool = True,
    include_correlation_id: bool = True,
    log_file: Optional[str] = None,
) -> None:
    """
    Setup structured logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Log format type (json, console)
        include_timestamp: Whether to include timestamps
        include_correlation_id: Whether to include correlation IDs
        log_file: Optional log file path
    """
    # Configure structlog
    processors = []
    
    # Add timestamp if requested
    if include_timestamp:
        processors.append(structlog.stdlib.filter_by_level)
        processors.append(structlog.stdlib.add_logger_name)
        processors.append(structlog.stdlib.add_log_level)
        processors.append(structlog.stdlib.PositionalArgumentsFormatter())
        processors.append(structlog.processors.TimeStamper(fmt="iso"))
    
    # Add correlation ID if requested
    if include_correlation_id:
        processors.append(add_correlation_id)
    
    # Add stack info
    processors.append(structlog.processors.StackInfoRenderer())
    processors.append(structlog.processors.format_exc_info)
    
    # Add format processor
    if format_type == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(
            structlog.dev.ConsoleRenderer(colors=True)
        )
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout if not log_file else None,
        filename=log_file,
        level=getattr(logging, level.upper()),
    )
    
    # Set loggers to propagate to root
    for logger_name in ["uvicorn", "uvicorn.error", "fastapi"]:
        logging.getLogger(logger_name).handlers = []
        logging.getLogger(logger_name).propagate = True


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Structured logger instance
    """
    return structlog.get_logger(name)


# Create default logger
logger = get_logger(__name__) 