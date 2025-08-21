# 🏗️ **Refactoring Patterns - EnergyOpti-Pro Architecture**

## **📋 Overview**

This document details the **refactoring patterns** implemented during the duplication elimination project. These patterns represent **industry best practices** and form the foundation of EnergyOpti-Pro's enterprise-grade architecture.

---

# **🎯 Pattern 1: Service Inheritance Architecture**

## **When to Use**
- When multiple services share common infrastructure
- When you need consistent error handling across domains
- When you want to enforce common patterns across services

## **Implementation**

### **Base Service Class**
```python
class BaseMarketDataService(ABC, Generic[T]):
    """
    Base class for all market data services.
    
    Provides unified HTTP client management, rate limiting,
    error handling, and common data validation patterns.
    """
    
    def __init__(self, config: ServiceConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self._setup_default_headers()
        self._setup_logging()
    
    async def _make_request(self, method: str, endpoint: str, **kwargs):
        """Unified HTTP request handling with retry logic."""
        # Implementation with rate limiting, retries, error handling
        pass
    
    def _validate_time_range(self, start_time: datetime, end_time: datetime):
        """Shared time range validation."""
        # Common validation logic
        pass
```

### **Specific Service Implementation**
```python
class PJMService(BaseMarketDataService):
    """PJM Market Data Service."""
    
    def __init__(self, api_key: Optional[str] = None):
        config = ServiceConfig(
            service_type=ServiceType.PJM,
            base_url="https://api.pjm.com/api/v1",
            api_key=api_key
        )
        super().__init__(config)
    
    async def get_lmp_data(self, start_time: datetime, end_time: datetime):
        """Get LMP data using inherited infrastructure."""
        # Uses inherited _make_request and _validate_time_range
        self._validate_time_range(start_time, end_time)
        return await self._get("/inst_load", {"start": start_time, "end": end_time})
```

## **Benefits**
- ✅ **Consistency**: All services follow identical patterns
- ✅ **Maintainability**: Changes to common logic only need to be made in one place
- ✅ **Testing**: Easier to test with consistent interfaces
- ✅ **Onboarding**: New developers can quickly understand the architecture

---

# **🎯 Pattern 2: Shared Utility Modules**

## **When to Use**
- When multiple services need the same utility functions
- When you want to centralize common business logic
- When you need consistent validation across the application

## **Implementation**

### **Utility Module Structure**
```python
# src/energyopti_pro/services/market_data/utils.py

class MarketStatus(Enum):
    """Market status values."""
    OPEN = "open"
    CLOSED = "closed"
    PRE_MARKET = "pre_market"

@dataclass
class MarketDataPoint:
    """Base market data point structure."""
    timestamp: datetime
    value: float
    unit: Unit
    quality: DataQuality = DataQuality.GOOD

def validate_time_range(start_time: datetime, end_time: datetime, max_days: int = 365):
    """Validate time range parameters."""
    if start_time >= end_time:
        raise ValueError("Start time must be before end time")
    
    if end_time > datetime.now() + timedelta(days=max_days):
        raise ValueError(f"End time cannot be more than {max_days} days in the future")

def generate_unique_id(prefix: str = "") -> str:
    """Generate unique identifier."""
    unique_part = uuid.uuid4().hex[:8].upper()
    return f"{prefix}{unique_part}" if prefix else unique_part
```

### **Usage in Services**
```python
from .utils import validate_time_range, generate_unique_id, MarketDataPoint

class YourService:
    async def get_data(self, start_time: datetime, end_time: datetime):
        # Use shared validation
        validate_time_range(start_time, end_time)
        
        # Use shared data structures
        data_point = MarketDataPoint(
            timestamp=datetime.now(),
            value=100.0,
            unit=Unit.MEGAWATT
        )
        
        # Use shared utilities
        id = generate_unique_id("DATA-")
```

## **Benefits**
- ✅ **DRY Principle**: No duplication of utility functions
- ✅ **Consistency**: All services use identical validation logic
- ✅ **Maintainability**: Updates to utilities benefit all services
- ✅ **Testing**: Utilities can be tested independently

---

# **🎯 Pattern 3: Configuration Management**

## **When to Use**
- When services need configurable parameters
- When you want to centralize configuration management
- When you need environment-specific settings

## **Implementation**

### **Configuration Structure**
```python
class ServiceConfig(BaseSettings):
    """Configuration for market data services."""
    service_type: ServiceType
    base_url: str
    api_key: Optional[str] = None
    rate_limit_delay: float = 0.1
    timeout: int = 30
    max_retries: int = 3
    cache_duration: int = 300
    headers: Optional[Dict[str, str]] = None

class Settings(BaseSettings):
    """Main application settings."""
    # ... other settings ...
    
    # Market Data settings
    pjm: PJMSettings = Field(default_factory=PJMSettings)
    rec: RECSettings = Field(default_factory=RECSettings)
    henry_hub: HenryHubSettings = Field(default_factory=HenryHubSettings)
```

### **Service Configuration Usage**
```python
class YourService(BaseMarketDataService):
    def __init__(self, api_key: Optional[str] = None):
        config = ServiceConfig(
            service_type=ServiceType.YOUR_SERVICE,
            base_url=settings.your_service.base_url,
            api_key=api_key or settings.your_service.api_key,
            rate_limit_delay=settings.your_service.rate_limit_delay,
            timeout=settings.your_service.timeout
        )
        super().__init__(config)
```

## **Benefits**
- ✅ **Centralization**: All configuration in one place
- ✅ **Environment Support**: Easy to switch between dev/staging/prod
- ✅ **Validation**: Pydantic validates configuration at startup
- ✅ **Documentation**: Configuration is self-documenting

---

# **🎯 Pattern 4: Error Handling Strategy**

## **When to Use**
- When you need consistent error handling across services
- When you want to provide meaningful error messages
- When you need to log errors with context

## **Implementation**

### **Custom Exception Classes**
```python
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
```

### **Error Handling in Services**
```python
async def get_data(self, start_time: datetime, end_time: datetime):
    try:
        # Validate parameters
        validate_time_range(start_time, end_time)
        
        # Make API request
        data = await self._get("/data", {"start": start_time, "end": end_time})
        return data
        
    except ValidationError as e:
        self.logger.error(f"Validation error: {e}")
        raise ValidationError(f"Invalid parameters: {str(e)}")
        
    except APIError as e:
        self.logger.error(f"API error: {e}")
        raise MarketDataError(f"Failed to retrieve data: {str(e)}")
        
    except Exception as e:
        self.logger.error(f"Unexpected error: {e}")
        raise MarketDataError(f"Unexpected error occurred: {str(e)}")
```

## **Benefits**
- ✅ **Consistency**: All services handle errors the same way
- ✅ **Debugging**: Clear error messages and logging
- ✅ **User Experience**: Meaningful error messages for API consumers
- ✅ **Monitoring**: Structured error logging for observability

---

# **🎯 Pattern 5: Async Context Managers**

## **When to Use**
- When services need to manage resources (HTTP sessions, database connections)
- When you want automatic cleanup of resources
- When you need to ensure proper resource lifecycle management

## **Implementation**

### **Context Manager Implementation**
```python
class BaseMarketDataService(ABC, Generic[T]):
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
```

### **Usage Pattern**
```python
async def get_pjm_data():
    """Get PJM data using context manager."""
    async with PJMService() as service:
        return await service.get_lmp_data(start_time, end_time)

# Or in your own code
async def process_market_data():
    async with YourService() as service:
        data = await service.get_data()
        processed = await service.process_data(data)
        return processed
```

## **Benefits**
- ✅ **Resource Management**: Automatic cleanup of resources
- ✅ **Error Safety**: Resources are cleaned up even if errors occur
- ✅ **Performance**: Proper connection pooling and reuse
- ✅ **Reliability**: No resource leaks

---

# **🎯 Pattern 6: Data Validation and Transformation**

## **When to Use**
- When you need to validate input data
- When you need to transform data between formats
- When you want to ensure data quality

## **Implementation**

### **Validation Functions**
```python
def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
    """Validate required fields in data dictionary."""
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    if missing_fields:
        raise ValueError(f"Missing required fields: {missing_fields}")

def validate_numeric_range(value: float, min_value: float, max_value: float, field_name: str) -> None:
    """Validate numeric value is within range."""
    if not min_value <= value <= max_value:
        raise ValueError(f"{field_name} must be between {min_value} and {max_value}, got {value}")
```

### **Data Transformation**
```python
def flatten_nested_dict(data: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    """Flatten nested dictionary structure."""
    flattened = {}
    
    for key, value in data.items():
        new_key = f"{prefix}.{key}" if prefix else key
        
        if isinstance(value, dict):
            flattened.update(flatten_nested_dict(value, new_key))
        else:
            flattened[new_key] = value
    
    return flattened

def group_by_field(data: List[Dict[str, Any]], field: str) -> Dict[str, List[Dict[str, Any]]]:
    """Group data by specified field."""
    grouped = {}
    
    for item in data:
        key = item.get(field)
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(item)
    
    return grouped
```

## **Benefits**
- ✅ **Data Quality**: Ensures data meets requirements
- ✅ **Consistency**: All services validate data the same way
- ✅ **Error Prevention**: Catches data issues early
- ✅ **Maintainability**: Centralized validation logic

---

# **🎯 Pattern 7: Logging and Observability**

## **When to Use**
- When you need to track service behavior
- When you want to debug issues in production
- When you need to monitor service performance

## **Implementation**

### **Structured Logging**
```python
from ...core.logging import get_logger

class YourService:
    def __init__(self):
        self.logger = get_logger(__name__)
    
    async def process_data(self, data: Dict[str, Any]):
        """Process data with comprehensive logging."""
        self.logger.info(f"Starting data processing for {len(data)} items")
        
        try:
            # Process data
            result = await self._process(data)
            
            self.logger.info(f"Successfully processed {len(result)} items")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to process data: {e}", extra={
                "data_count": len(data),
                "error_type": type(e).__name__,
                "error_details": str(e)
            })
            raise
```

### **Performance Monitoring**
```python
import time

async def get_data_with_timing(self, **kwargs):
    """Get data with performance monitoring."""
    start_time = time.time()
    
    try:
        data = await self._get_data(**kwargs)
        
        duration = time.time() - start_time
        self.logger.info(f"Data retrieval completed in {duration:.2f}s", extra={
            "operation": "get_data",
            "duration_ms": int(duration * 1000),
            "data_count": len(data) if isinstance(data, list) else 1
        })
        
        return data
        
    except Exception as e:
        duration = time.time() - start_time
        self.logger.error(f"Data retrieval failed after {duration:.2f}s: {e}", extra={
            "operation": "get_data",
            "duration_ms": int(duration * 1000),
            "error": str(e)
        })
        raise
```

## **Benefits**
- ✅ **Debugging**: Clear visibility into service behavior
- ✅ **Monitoring**: Track performance and errors
- ✅ **Compliance**: Audit trail for regulatory requirements
- ✅ **User Support**: Better understanding of user issues

---

# **🎯 Pattern 8: Testing Strategy**

## **When to Use**
- When you want to ensure code quality
- When you need to prevent regressions
- When you want to document expected behavior

## **Implementation**

### **Unit Tests**
```python
import pytest
from unittest.mock import AsyncMock, patch

class TestYourService:
    @pytest.fixture
    def service(self):
        return YourService()
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, service):
        """Test service initializes correctly."""
        assert service is not None
        assert hasattr(service, 'logger')
        assert service.config.service_type == ServiceType.YOUR_SERVICE
    
    @pytest.mark.asyncio
    async def test_data_validation(self, service):
        """Test data validation logic."""
        with pytest.raises(ValidationError, match="Start time must be before end time"):
            await service.get_data(
                start_time=datetime.now(),
                end_time=datetime.now() - timedelta(hours=1)
            )
```

### **Integration Tests**
```python
@pytest.mark.integration
class TestYourServiceIntegration:
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test complete workflow."""
        service = YourService()
        
        async with service:
            data = await service.get_data(
                start_time=datetime.now() - timedelta(hours=1),
                end_time=datetime.now()
            )
            
            assert len(data) > 0
            assert all(isinstance(item, DataPoint) for item in data)
```

## **Benefits**
- ✅ **Quality Assurance**: Ensures code works as expected
- ✅ **Regression Prevention**: Catches breaking changes
- ✅ **Documentation**: Tests serve as living documentation
- ✅ **Confidence**: Enables safe refactoring and changes

---

# **🏆 Best Practices Summary**

## **Do's**
- ✅ **Inherit from appropriate base classes** for consistency
- ✅ **Use shared utilities** instead of duplicating code
- ✅ **Implement proper error handling** with custom exceptions
- ✅ **Use structured logging** for observability
- ✅ **Write comprehensive tests** for quality assurance
- ✅ **Follow established patterns** for maintainability

## **Don'ts**
- ❌ **Don't duplicate common logic** - use shared utilities
- ❌ **Don't ignore errors** - handle them appropriately
- ❌ **Don't use print statements** - use proper logging
- ❌ **Don't skip validation** - validate all inputs
- ❌ **Don't ignore testing** - test thoroughly
- ❌ **Don't deviate from patterns** - maintain consistency

---

# **🚀 Implementation Checklist**

## **Before Starting**
- [ ] Identify the appropriate base class
- [ ] Plan your service's responsibility
- [ ] Design your data structures
- [ ] Plan error handling strategy

## **During Implementation**
- [ ] Follow the established patterns
- [ ] Use shared utilities and validation
- [ ] Implement proper logging
- [ ] Handle errors consistently

## **Before Committing**
- [ ] Write comprehensive tests
- [ ] Update documentation
- [ ] Run duplication check locally
- [ ] Ensure CI/CD passes

---

# **🎯 Success Metrics**

## **Your Implementation Should Achieve**
- ✅ **Inheritance**: Properly inherits from appropriate base class
- ✅ **Consistency**: Follows established patterns and conventions
- ✅ **Testing**: Comprehensive test coverage
- ✅ **Documentation**: Clear and complete documentation
- ✅ **Quality**: Passes all CI/CD checks including duplication guard

## **Remember**
**Following these patterns ensures your service contributes to EnergyOpti-Pro's enterprise-grade quality and maintainability standards.**

**Your service will be part of the most maintainable, scalable energy trading platform in the market!** 🚀✨

---

**Document Version**: 1.0  
**Last Updated**: August 20, 2025  
**Status**: **ACTIVE REFERENCE** ✅ 