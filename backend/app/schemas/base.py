"""
Base schemas and type definitions for QuantaEnergi API
Provides strict typing and Pydantic models for all API endpoints
"""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, validator, root_validator
from pydantic.types import condecimal, constr


class BaseSchema(BaseModel):
    """Base schema with common configuration"""
    
    class Config:
        """Pydantic configuration"""
        use_enum_values = True
        validate_assignment = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v),
        }
        schema_extra = {
            "example": {}
        }


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields"""
    
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when the record was created"
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when the record was last updated"
    )


class IdMixin(BaseModel):
    """Mixin for ID fields"""
    
    id: UUID = Field(
        description="Unique identifier for the record"
    )


class TenantMixin(BaseModel):
    """Mixin for multi-tenant support"""
    
    tenant_id: UUID = Field(
        description="Tenant identifier for multi-tenant isolation"
    )


# Enums for common values
class TradeStatus(str, Enum):
    """Trade status enumeration"""
    PENDING = "pending"
    CAPTURED = "captured"
    VALIDATED = "validated"
    CONFIRMED = "confirmed"
    ALLOCATED = "allocated"
    SETTLED = "settled"
    INVOICED = "invoiced"
    PAID = "paid"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class TradeType(str, Enum):
    """Trade type enumeration"""
    SPOT = "spot"
    FORWARD = "forward"
    FUTURES = "futures"
    OPTIONS = "options"
    SWAP = "swap"
    CREDIT_DEFAULT_SWAP = "credit_default_swap"
    INTEREST_RATE_SWAP = "interest_rate_swap"
    CURRENCY_SWAP = "currency_swap"


class CommodityType(str, Enum):
    """Commodity type enumeration"""
    CRUDE_OIL = "crude_oil"
    NATURAL_GAS = "natural_gas"
    ELECTRICITY = "electricity"
    CARBON_CREDITS = "carbon_credits"
    RENEWABLE_ENERGY = "renewable_energy"
    COAL = "coal"
    URANIUM = "uranium"


class RiskLevel(str, Enum):
    """Risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceRegion(str, Enum):
    """Compliance region enumeration"""
    US = "us"
    UK = "uk"
    EU = "eu"
    MIDDLE_EAST = "middle_east"
    GUYANA = "guyana"
    GLOBAL = "global"


class UserRole(str, Enum):
    """User role enumeration"""
    ADMIN = "admin"
    TRADER = "trader"
    RISK_MANAGER = "risk_manager"
    COMPLIANCE_OFFICER = "compliance_officer"
    VIEWER = "viewer"


class Currency(str, Enum):
    """Currency enumeration"""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    AED = "AED"
    SAR = "SAR"
    GYD = "GYD"


# Base response schemas
class SuccessResponse(BaseSchema):
    """Standard success response"""
    
    success: bool = Field(default=True, description="Success indicator")
    message: str = Field(description="Success message")
    data: Optional[Any] = Field(default=None, description="Response data")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Response timestamp"
    )


class ErrorResponse(BaseSchema):
    """Standard error response"""
    
    success: bool = Field(default=False, description="Success indicator")
    error: Dict[str, Any] = Field(description="Error details")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Error timestamp"
    )


class PaginationParams(BaseSchema):
    """Pagination parameters"""
    
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Page size")
    sort_by: Optional[str] = Field(default=None, description="Sort field")
    sort_order: Optional[str] = Field(default="asc", pattern="^(asc|desc)$", description="Sort order")


class PaginatedResponse(BaseSchema):
    """Paginated response wrapper"""
    
    data: List[Any] = Field(description="List of items")
    pagination: Dict[str, Any] = Field(description="Pagination metadata")
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Page size")
    total_pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Whether there is a next page")
    has_prev: bool = Field(description="Whether there is a previous page")


# Validation helpers
class StrictDecimal(condecimal(ge=0, decimal_places=2)):
    """Strict decimal type for monetary values"""
    pass


class StrictString(constr(min_length=1, max_length=255)):
    """Strict string type for required fields"""
    pass


# Type aliases
Money = StrictDecimal
Percentage = condecimal(ge=0, le=100, decimal_places=2)
Quantity = condecimal(ge=0, decimal_places=4)
Rate = condecimal(ge=0, decimal_places=6)


# Common field definitions
def money_field(description: str = "Monetary amount") -> Any:
    """Create a money field"""
    return Field(description=description, example=1000.50)


def percentage_field(description: str = "Percentage value") -> Any:
    """Create a percentage field"""
    return Field(description=description, example=5.25)


def quantity_field(description: str = "Quantity amount") -> Any:
    """Create a quantity field"""
    return Field(description=description, example=100.0000)


def rate_field(description: str = "Rate value") -> Any:
    """Create a rate field"""
    return Field(description=description, example=0.052500)


def optional_money_field(description: str = "Optional monetary amount") -> Any:
    """Create an optional money field"""
    return Field(default=None, description=description, example=1000.50)


def optional_percentage_field(description: str = "Optional percentage value") -> Any:
    """Create an optional percentage field"""
    return Field(default=None, description=description, example=5.25)


def optional_quantity_field(description: str = "Optional quantity amount") -> Any:
    """Create an optional quantity field"""
    return Field(default=None, description=description, example=100.0000)


def optional_rate_field(description: str = "Optional rate value") -> Any:
    """Create an optional rate field"""
    return Field(default=None, description=description, example=0.052500)
