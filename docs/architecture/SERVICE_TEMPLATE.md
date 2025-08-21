# 🏗️ **Service Template for EnergyOpti-Pro**

## **📋 Overview**

This template demonstrates the **established patterns** for creating new services in EnergyOpti-Pro. Following these patterns ensures consistency, maintainability, and adherence to our enterprise-grade standards.

---

# **🎯 Service Creation Pattern**

## **1. Choose Your Base Class**

### **For Market Data Services**
```python
from .market_data.base_service import BaseMarketDataService, ServiceConfig, ServiceType, DataType
from .market_data.utils import validate_time_range, generate_unique_id, MarketDataValidationError

class YourMarketDataService(BaseMarketDataService):
    def __init__(self, api_key: Optional[str] = None):
        config = ServiceConfig(
            service_type=ServiceType.YOUR_SERVICE,  # Add to enum if new
            base_url="https://api.yourservice.com/v1",
            api_key=api_key,
            rate_limit_delay=0.1,
            timeout=30,
            max_retries=3,
            cache_duration=300
        )
        super().__init__(config)
```

### **For Islamic Finance Services**
```python
from .islamic_finance.base_service import BaseIslamicFinanceService

class YourIslamicFinanceService(BaseIslamicFinanceService):
    def __init__(self):
        super().__init__()
        # Your service-specific initialization
```

### **For General Business Services**
```python
from ...core.logging import get_logger
from ...core.config import settings

class YourBusinessService:
    def __init__(self):
        self.logger = get_logger(__name__)
        # Your service-specific initialization
```

---

# **🔧 Implementation Guidelines**

## **2. Follow the Established Patterns**

### **Error Handling**
```python
# ✅ DO: Use consistent error handling
try:
    result = await self._get(endpoint, params)
    return result
except Exception as e:
    self.logger.error(f"Failed to get data: {e}")
    raise MarketDataValidationError(f"Failed to get data: {str(e)}")

# ❌ DON'T: Use generic exceptions
try:
    result = await self._get(endpoint, params)
    return result
except:
    raise Exception("Something went wrong")
```

### **Logging**
```python
# ✅ DO: Use structured logging
self.logger.info(f"Processing request: {request_id}")
self.logger.error(f"Validation failed for {entity_id}: {error}")

# ❌ DON'T: Use print statements
print("Processing request")
print("Error occurred")
```

### **Validation**
```python
# ✅ DO: Use shared validation utilities
from .market_data.utils import validate_time_range, validate_required_fields

validate_time_range(start_time, end_time)
validate_required_fields(data, ["required_field1", "required_field2"])

# ❌ DON'T: Duplicate validation logic
if start_time >= end_time:
    raise ValueError("Invalid time range")
```

---

# **📊 Data Structures**

## **3. Use Consistent Data Models**

### **Market Data Points**
```python
from .market_data.utils import MarketDataPoint, Unit, Currency, DataQuality

@dataclass
class YourDataPoint(MarketDataPoint):
    """Your specific data structure."""
    # Inherit from base for consistency
    your_specific_field: str
    your_metric: float
```

### **Response Formats**
```python
from .market_data.base_service import MarketDataResponse, ServiceType, DataType

def format_response(self, data: List[Any]) -> MarketDataResponse:
    """Format standardized response."""
    return MarketDataResponse(
        success=True,
        data=data,
        count=len(data),
        timestamp=datetime.now(),
        service_type=ServiceType.YOUR_SERVICE,
        data_type=DataType.YOUR_DATA_TYPE
    )
```

---

# **🧪 Testing Patterns**

## **4. Test Your Service**

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
    
    @pytest.mark.asyncio
    async def test_data_retrieval(self, service):
        """Test data retrieval functionality."""
        with patch.object(service, '_get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"data": "test"}
            result = await service.get_data()
            assert result["data"] == "test"
```

### **Integration Tests**
```python
@pytest.mark.integration
class TestYourServiceIntegration:
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test complete workflow."""
        service = YourService()
        result = await service.complete_workflow()
        assert result.success is True
```

---

# **📚 Documentation Requirements**

## **5. Document Your Service**

### **Service Header**
```python
"""
Your Service Name for EnergyOpti-Pro.

This service provides [brief description]:
- [Feature 1]
- [Feature 2]
- [Feature 3]

Usage:
    service = YourService()
    result = await service.get_data()
"""
```

### **Method Documentation**
```python
async def get_data(
    self,
    start_time: datetime,
    end_time: datetime,
    filters: Optional[Dict[str, Any]] = None
) -> List[YourDataPoint]:
    """
    Get data for specified time range and filters.
    
    Args:
        start_time: Start time for data query
        end_time: End time for data query
        filters: Optional filters to apply
        
    Returns:
        List of data points matching criteria
        
    Raises:
        MarketDataValidationError: If parameters are invalid
        Exception: If data retrieval fails
    """
```

---

# **🚀 Best Practices**

## **6. Follow These Principles**

### **DRY (Don't Repeat Yourself)**
- ✅ Use shared utilities from `utils.py`
- ✅ Inherit from appropriate base classes
- ✅ Reuse common validation patterns
- ❌ Don't duplicate HTTP client logic
- ❌ Don't duplicate validation functions

### **Single Responsibility**
- ✅ Each service has one clear purpose
- ✅ Methods do one thing well
- ✅ Clear separation of concerns
- ❌ Don't mix data retrieval with business logic
- ❌ Don't combine multiple service responsibilities

### **Error Handling**
- ✅ Use specific exception types
- ✅ Log errors with context
- ✅ Provide helpful error messages
- ❌ Don't catch and ignore exceptions
- ❌ Don't use generic error types

### **Performance**
- ✅ Use async/await for I/O operations
- ✅ Implement proper rate limiting
- ✅ Cache frequently accessed data
- ❌ Don't block on I/O operations
- ❌ Don't make unnecessary API calls

---

# **📋 Checklist for New Services**

## **Before You Start**
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

# **🎯 Example: Complete Service Implementation**

```python
"""
Example Market Data Service for EnergyOpti-Pro.

This service demonstrates the complete pattern for creating
new market data services following our established architecture.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

from .market_data.base_service import BaseMarketDataService, ServiceConfig, ServiceType, DataType
from .market_data.utils import validate_time_range, generate_unique_id, MarketDataValidationError

@dataclass
class ExampleDataPoint:
    """Example data structure."""
    timestamp: datetime
    value: float
    location: str
    metadata: Optional[Dict[str, Any]] = None

class ExampleMarketDataService(BaseMarketDataService):
    """
    Example Market Data Service.
    
    This service demonstrates the complete pattern for market data services.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize example service."""
        config = ServiceConfig(
            service_type=ServiceType.EXAMPLE,
            base_url="https://api.example.com/v1",
            api_key=api_key,
            rate_limit_delay=0.1,
            timeout=30,
            max_retries=3,
            cache_duration=300
        )
        super().__init__(config)
    
    async def get_example_data(
        self,
        start_time: datetime,
        end_time: datetime,
        location: Optional[str] = None
    ) -> List[ExampleDataPoint]:
        """
        Get example data for specified time range and location.
        
        Args:
            start_time: Start time for data query
            end_time: End time for data query
            location: Optional location filter
            
        Returns:
            List of example data points
            
        Raises:
            MarketDataValidationError: If parameters are invalid
        """
        # Validate time range using shared utility
        validate_time_range(start_time, end_time)
        
        endpoint = "/example/data"
        params = {
            "start": start_time.isoformat(),
            "end": end_time.isoformat()
        }
        
        if location:
            params["location"] = location
        
        try:
            data = await self._get(endpoint, params)
            
            data_points = []
            for item in data.get("data", []):
                data_points.append(ExampleDataPoint(
                    timestamp=datetime.fromisoformat(item["timestamp"]),
                    value=float(item["value"]),
                    location=item.get("location", ""),
                    metadata=item.get("metadata")
                ))
            
            return data_points
            
        except Exception as e:
            self.logger.error(f"Failed to get example data: {e}")
            raise MarketDataValidationError(f"Failed to get example data: {str(e)}")
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information."""
        return {
            "service_name": "Example Market Data Service",
            "version": "1.0",
            "base_url": self.config.base_url,
            "service_type": self.config.service_type.value
        }
```

---

# **🏆 Success Metrics**

## **Your Service Should Achieve**
- ✅ **Inheritance**: Properly inherits from appropriate base class
- ✅ **Consistency**: Follows established patterns and conventions
- ✅ **Testing**: Comprehensive test coverage
- ✅ **Documentation**: Clear and complete documentation
- ✅ **Quality**: Passes all CI/CD checks including duplication guard

## **Remember**
**Following these patterns ensures your service contributes to EnergyOpti-Pro's enterprise-grade quality and maintainability standards.**

**Your service will be part of the most maintainable, scalable energy trading platform in the market!** 🚀✨ 