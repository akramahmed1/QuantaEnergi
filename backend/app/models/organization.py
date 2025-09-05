"""
Organization Model for Multi-Tenant Architecture
Supports multiple organizations with data isolation and compliance requirements
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, String, DateTime, Boolean, JSON, Text, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from pydantic import BaseModel, Field, validator
import uuid

from ..db.database import Base

class Organization(Base):
    """Organization model for multi-tenant support"""
    
    __tablename__ = "organizations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text)
    
    # Organization type and classification
    organization_type = Column(String(100), nullable=False)  # 'oil_company', 'trading_firm', 'bank', 'exchange'
    classification = Column(String(100), nullable=False)     # 'tier1', 'tier2', 'tier3'
    
    # Regional and compliance information
    primary_region = Column(String(100), nullable=False)    # 'ME', 'US', 'UK', 'EU'
    operating_regions = Column(JSON)                        # List of regions where they operate
    compliance_requirements = Column(JSON)                  # Regional compliance requirements
    
    # Contact and business information
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    website = Column(String(255))
    address = Column(JSON)
    
    # Business details
    business_license = Column(String(255))
    tax_id = Column(String(255))
    regulatory_licenses = Column(JSON)
    
    # Islamic finance compliance
    is_islamic_compliant = Column(Boolean, default=False)
    sharia_board_approval = Column(Boolean, default=False)
    islamic_compliance_certificate = Column(String(255))
    
    # Trading capabilities and limits
    trading_limits = Column(JSON)  # Daily, monthly, annual limits
    credit_rating = Column(String(10))
    risk_tolerance = Column(String(50))  # 'conservative', 'moderate', 'aggressive'
    
    # System configuration
    timezone = Column(String(50), default='UTC')
    currency = Column(String(10), default='USD')
    language = Column(String(10), default='en')
    
    # Status and lifecycle
    status = Column(String(50), default='active')  # 'active', 'suspended', 'inactive'
    subscription_tier = Column(String(50), default='standard')  # 'standard', 'premium', 'enterprise'
    subscription_start_date = Column(DateTime)
    subscription_end_date = Column(DateTime)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))
    
    # Soft delete
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime)
    deleted_by = Column(UUID(as_uuid=True))
    
    # Relationships - will be set up after Trade models are defined
    # trades = relationship("Trade", back_populates="organization")
    # trade_allocations = relationship("TradeAllocation", back_populates="organization")
    # trade_settlements = relationship("TradeSettlement", back_populates="organization")
    
    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}', code='{self.code}')>"
    
    @property
    def is_active(self) -> bool:
        """Check if organization is active"""
        return self.status == 'active' and not self.is_deleted
    
    @property
    def has_expired_subscription(self) -> bool:
        """Check if subscription has expired"""
        if not self.subscription_end_date:
            return False
        return datetime.utcnow() > self.subscription_end_date
    
    def get_compliance_requirement(self, region: str, requirement: str) -> Any:
        """Get specific compliance requirement for a region"""
        if not self.compliance_requirements:
            return None
        
        region_compliance = self.compliance_requirements.get(region, {})
        return region_compliance.get(requirement)
    
    def can_trade_commodity(self, commodity: str) -> bool:
        """Check if organization can trade specific commodity"""
        if not self.trading_limits:
            return True
        
        allowed_commodities = self.trading_limits.get('allowed_commodities', [])
        if not allowed_commodities:
            return True
        
        return commodity in allowed_commodities
    
    def get_trading_limit(self, limit_type: str) -> Optional[float]:
        """Get trading limit of specific type"""
        if not self.trading_limits:
            return None
        
        return self.trading_limits.get(limit_type)
    
    def update_trading_limits(self, new_limits: Dict[str, Any]) -> None:
        """Update trading limits"""
        if not self.trading_limits:
            self.trading_limits = {}
        
        self.trading_limits.update(new_limits)
        self.updated_at = datetime.utcnow()

# Pydantic schemas for API
class OrganizationBase(BaseModel):
    """Base organization schema"""
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=2, max_length=50, pattern=r'^[A-Z0-9_]+$')
    description: Optional[str] = None
    organization_type: str = Field(..., pattern=r'^(oil_company|trading_firm|bank|exchange)$')
    classification: str = Field(..., pattern=r'^(tier1|tier2|tier3)$')
    primary_region: str = Field(..., pattern=r'^(ME|US|UK|EU)$')
    operating_regions: Optional[List[str]] = None
    contact_email: Optional[str] = Field(None, pattern=r'^[^@]+@[^@]+\.[^@]+$')
    contact_phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[Dict[str, Any]] = None
    business_license: Optional[str] = None
    tax_id: Optional[str] = None
    is_islamic_compliant: bool = False
    timezone: str = 'UTC'
    currency: str = 'USD'
    language: str = 'en'
    subscription_tier: str = Field('standard', pattern=r'^(standard|premium|enterprise)$')
    
    @validator('code')
    def validate_code(cls, v):
        """Validate organization code format"""
        if not v.isupper() or ' ' in v:
            raise ValueError('Code must be uppercase and contain no spaces')
        return v
    
    @validator('operating_regions')
    def validate_operating_regions(cls, v):
        """Validate operating regions"""
        if v:
            valid_regions = {'ME', 'US', 'UK', 'EU'}
            invalid_regions = set(v) - valid_regions
            if invalid_regions:
                raise ValueError(f'Invalid regions: {invalid_regions}')
        return v

class OrganizationCreate(OrganizationBase):
    """Schema for creating organization"""
    pass

class OrganizationUpdate(BaseModel):
    """Schema for updating organization"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    organization_type: Optional[str] = Field(None, pattern=r'^(oil_company|trading_firm|bank|exchange)$')
    classification: Optional[str] = Field(None, pattern=r'^(tier1|tier2|tier3)$')
    primary_region: Optional[str] = Field(None, pattern=r'^(ME|US|UK|EU)$')
    operating_regions: Optional[List[str]] = None
    contact_email: Optional[str] = Field(None, pattern=r'^[^@]+@[^@]+\.[^@]+$')
    contact_phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[Dict[str, Any]] = None
    business_license: Optional[str] = None
    tax_id: Optional[str] = None
    is_islamic_compliant: Optional[bool] = None
    timezone: Optional[str] = None
    currency: Optional[str] = None
    language: Optional[str] = None
    subscription_tier: Optional[str] = Field(None, pattern=r'^(standard|premium|enterprise)$')
    status: Optional[str] = Field(None, pattern=r'^(active|suspended|inactive)$')

class OrganizationResponse(OrganizationBase):
    """Schema for organization response"""
    id: uuid.UUID
    status: str
    subscription_start_date: Optional[datetime]
    subscription_end_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    is_active: bool
    has_expired_subscription: bool
    
    class Config:
        from_attributes = True

class OrganizationListResponse(BaseModel):
    """Schema for organization list response"""
    organizations: List[OrganizationResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int

# Organization configuration schemas
class ComplianceRequirement(BaseModel):
    """Schema for compliance requirement"""
    region: str
    requirement_type: str
    requirement_value: Any
    is_mandatory: bool = True
    last_updated: datetime
    next_review_date: Optional[datetime] = None

class TradingLimit(BaseModel):
    """Schema for trading limit"""
    limit_type: str  # 'daily', 'monthly', 'annual', 'per_trade'
    limit_value: float
    currency: str = 'USD'
    commodity: Optional[str] = None  # None means all commodities
    is_hard_limit: bool = True
    reset_frequency: str = 'daily'  # 'daily', 'monthly', 'annual'

class OrganizationConfig(BaseModel):
    """Schema for organization configuration"""
    compliance_requirements: List[ComplianceRequirement]
    trading_limits: List[TradingLimit]
    allowed_commodities: List[str]
    risk_parameters: Dict[str, Any]
    notification_preferences: Dict[str, Any]
