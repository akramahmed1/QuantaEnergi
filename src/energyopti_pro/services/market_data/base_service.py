"""
Base Market Data Service for EnergyOpti-Pro.

This module provides a unified base class for all market data services,
eliminating duplication and providing consistent patterns for:
- API client management
- Rate limiting
- Error handling
- Data validation
- Caching
- Logging
"""

import asyncio
import aiohttp
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, TypeVar, Generic
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from enum import Enum

from ...core.config import settings
from ...core.logging import get_logger

logger = get_logger(__name__)

T = TypeVar('T')

class ServiceType(Enum):
    """Market data service types."""
    PJM = "pjm"
    REC = "rec"
    HENRY_HUB = "henry_hub"
    CAISO = "caiso"
    NYISO = "nyiso"
    ERCOT = "ercot"

class DataType(Enum):
    """Market data types."""
    LMP = "lmp"
    FTR = "ftr"
    SCHEDULE = "schedule"
    CAPACITY = "capacity"
    ANCILLARY = "ancillary"
    FUTURES = "futures"
    BASIS = "basis"
    STORAGE = "storage"
    PIPELINE = "pipeline"

@dataclass
class ServiceConfig:
    """Configuration for market data services."""
    service_type: ServiceType
    base_url: str
    api_key: Optional[str] = None
    rate_limit_delay: float = 0.1
    timeout: int = 30
    max_retries: int = 3
    cache_duration: int = 300
    headers: Optional[Dict[str, str]] = None

@dataclass
class MarketDataRequest:
    """Base request structure for market data."""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    service_type: ServiceType
    data_type: DataType
    parameters: Optional[Dict[str, Any]] = None

@dataclass
class MarketDataResponse:
    """Base response structure for market data."""
    success: bool
    data: List[Any]
    count: int
    timestamp: datetime
    service_type: ServiceType
    data_type: DataType
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class BaseMarketDataService(ABC, Generic[T]):
    """
    Base class for all market data services.
    
    This class provides:
    - Unified HTTP client management
    - Consistent rate limiting
    - Standardized error handling
    - Common data validation patterns
    - Shared utility functions
    """
    
    def __init__(self, config: ServiceConfig):
        """
        Initialize base market data service.
        
        Args:
            config: Service configuration
        """
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self._setup_default_headers()
        self._setup_logging()
    
    def _setup_default_headers(self):
        """Setup default HTTP headers."""
        self.default_headers = {
            "User-Agent": "EnergyOpti-Pro/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        if self.config.headers:
            self.default_headers.update(self.config.headers)
    
    def _setup_logging(self):
        """Setup service-specific logging."""
        self.logger = logger.getChild(f"{self.config.service_type.value}_service")
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            headers=self.default_headers,
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make authenticated HTTP request with retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters
            data: Request body data
            headers: Additional headers
            
        Returns:
            API response data
            
        Raises:
            Exception: If request fails after retries
        """
        if not self.session:
            raise RuntimeError("Service not initialized. Use async context manager.")
        
        url = f"{self.config.base_url}{endpoint}"
        
        # Add API key if available
        if self.config.api_key:
            params = params or {}
            params["api_key"] = self.config.api_key
        
        # Merge headers
        request_headers = self.default_headers.copy()
        if headers:
            request_headers.update(headers)
        
        for attempt in range(self.config.max_retries):
            try:
                async with self.session.request(
                    method, url, params=params, json=data, headers=request_headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        await asyncio.sleep(self.config.rate_limit_delay)
                        return data
                    else:
                        error_msg = f"API error: {response.status} - {response.reason}"
                        self.logger.error(f"Attempt {attempt + 1}: {error_msg}")
                        
                        if attempt == self.config.max_retries - 1:
                            raise Exception(error_msg)
                        
                        # Exponential backoff
                        await asyncio.sleep(2 ** attempt)
                        
            except aiohttp.ClientError as e:
                self.logger.error(f"Attempt {attempt + 1}: Request failed: {e}")
                
                if attempt == self.config.max_retries - 1:
                    raise Exception(f"Request failed after {self.config.max_retries} attempts: {e}")
                
                # Exponential backoff
                await asyncio.sleep(2 ** attempt)
    
    async def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make GET request."""
        return await self._make_request("GET", endpoint, params=params)
    
    async def _post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make POST request."""
        return await self._make_request("POST", endpoint, data=data)
    
    async def _put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make PUT request."""
        return await self._make_request("PUT", endpoint, data=data)
    
    async def _delete(self, endpoint: str) -> Dict[str, Any]:
        """Make DELETE request."""
        return await self._make_request("DELETE", endpoint)
    
    def _validate_time_range(self, start_time: datetime, end_time: datetime) -> None:
        """
        Validate time range parameters.
        
        Args:
            start_time: Start time
            end_time: End time
            
        Raises:
            ValueError: If time range is invalid
        """
        if start_time >= end_time:
            raise ValueError("Start time must be before end time")
        
        if end_time > datetime.now() + timedelta(days=365):
            raise ValueError("End time cannot be more than 1 year in the future")
    
    def _validate_required_params(self, params: Dict[str, Any], required: List[str]) -> None:
        """
        Validate required parameters.
        
        Args:
            params: Parameters to validate
            required: List of required parameter names
            
        Raises:
            ValueError: If required parameters are missing
        """
        missing = [param for param in required if param not in params or params[param] is None]
        if missing:
            raise ValueError(f"Missing required parameters: {missing}")
    
    def _format_response(
        self, 
        data: List[Any], 
        service_type: ServiceType, 
        data_type: DataType,
        metadata: Optional[Dict[str, Any]] = None
    ) -> MarketDataResponse:
        """
        Format standardized response.
        
        Args:
            data: Response data
            service_type: Service type
            data_type: Data type
            metadata: Additional metadata
            
        Returns:
            Formatted response
        """
        return MarketDataResponse(
            success=True,
            data=data,
            count=len(data),
            timestamp=datetime.now(),
            service_type=service_type,
            data_type=data_type,
            metadata=metadata
        )
    
    def _format_error_response(
        self, 
        error: str, 
        service_type: ServiceType, 
        data_type: DataType
    ) -> MarketDataResponse:
        """
        Format error response.
        
        Args:
            error: Error message
            service_type: Service type
            data_type: Data type
            
        Returns:
            Formatted error response
        """
        return MarketDataResponse(
            success=False,
            data=[],
            count=0,
            timestamp=datetime.now(),
            service_type=service_type,
            data_type=data_type,
            error=error
        )
    
    @abstractmethod
    async def get_data(self, request: MarketDataRequest) -> MarketDataResponse:
        """
        Get market data based on request.
        
        Args:
            request: Market data request
            
        Returns:
            Market data response
        """
        pass
    
    @abstractmethod
    async def validate_request(self, request: MarketDataRequest) -> bool:
        """
        Validate market data request.
        
        Args:
            request: Market data request
            
        Returns:
            True if valid, False otherwise
        """
        pass
    
    def get_service_info(self) -> Dict[str, Any]:
        """
        Get service information.
        
        Returns:
            Service metadata
        """
        return {
            "service_type": self.config.service_type.value,
            "base_url": self.config.base_url,
            "rate_limit_delay": self.config.rate_limit_delay,
            "timeout": self.config.timeout,
            "max_retries": self.config.max_retries,
            "cache_duration": self.config.cache_duration,
            "has_api_key": bool(self.config.api_key)
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform service health check.
        
        Returns:
            Health status
        """
        try:
            # Try to make a simple request
            await self._get("/health")
            return {
                "service": self.config.service_type.value,
                "status": "healthy",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "service": self.config.service_type.value,
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Utility functions for common operations
def create_service_config(
    service_type: ServiceType,
    base_url: str,
    api_key: Optional[str] = None,
    **kwargs
) -> ServiceConfig:
    """
    Create service configuration with defaults.
    
    Args:
        service_type: Type of service
        base_url: Base URL for API
        api_key: Optional API key
        **kwargs: Additional configuration options
        
    Returns:
        Service configuration
    """
    return ServiceConfig(
        service_type=service_type,
        base_url=base_url,
        api_key=api_key,
        **kwargs
    )

def validate_market_data_request(request: MarketDataRequest) -> None:
    """
    Validate market data request.
    
    Args:
        request: Request to validate
        
    Raises:
        ValueError: If request is invalid
    """
    if request.start_time and request.end_time:
        if request.start_time >= request.end_time:
            raise ValueError("Start time must be before end time")
    
    if not request.service_type:
        raise ValueError("Service type is required")
    
    if not request.data_type:
        raise ValueError("Data type is required")

# Common error messages
class MarketDataError(Exception):
    """Base exception for market data services."""
    pass

class ValidationError(MarketDataError):
    """Validation error."""
    pass

class APIError(MarketDataError):
    """API error."""
    pass

class RateLimitError(MarketDataError):
    """Rate limit error."""
    pass

class AuthenticationError(MarketDataError):
    """Authentication error."""
    pass 