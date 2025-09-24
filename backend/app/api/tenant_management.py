"""
Tenant Management API Endpoints
RESTful API for managing multi-tenant operations
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field

import structlog

from app.services.tenant_service import TenantService, get_tenant_service
from app.core.tenant_router import get_tenant_router
from app.security.authentication import get_current_user

logger = structlog.get_logger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/tenant-management", tags=["Tenant Management"])
security = HTTPBearer()


# Pydantic models
class TenantCreateRequest(BaseModel):
    """Request model for creating a tenant"""
    tenant_id: str = Field(..., description="Unique tenant identifier")
    name: str = Field(..., description="Tenant name")
    region: str = Field(default="us", description="Tenant region")
    subscription_tier: str = Field(default="basic", description="Subscription tier")
    max_users: int = Field(default=10, description="Maximum number of users")
    max_trades_per_day: int = Field(default=1000, description="Maximum trades per day")
    features: List[str] = Field(default=[], description="Enabled features")


class TenantUpdateRequest(BaseModel):
    """Request model for updating a tenant"""
    name: Optional[str] = Field(None, description="Tenant name")
    region: Optional[str] = Field(None, description="Tenant region")
    subscription_tier: Optional[str] = Field(None, description="Subscription tier")
    max_users: Optional[int] = Field(None, description="Maximum number of users")
    max_trades_per_day: Optional[int] = Field(None, description="Maximum trades per day")
    features: Optional[List[str]] = Field(None, description="Enabled features")
    is_active: Optional[bool] = Field(None, description="Active status")


class TenantResponse(BaseModel):
    """Response model for tenant information"""
    tenant_id: str
    name: str
    region: str
    subscription_tier: str
    max_users: int
    max_trades_per_day: int
    features: List[str]
    created_at: datetime
    updated_at: datetime
    is_active: bool


class TenantStatsResponse(BaseModel):
    """Response model for tenant statistics"""
    tenant_id: str
    trade_count: int
    portfolio_count: int
    position_count: int
    total_trade_value: float
    database_stats: Dict[str, Any]
    timestamp: datetime


class TenantListResponse(BaseModel):
    """Response model for tenant list"""
    tenants: List[TenantResponse]
    total_count: int
    page: int
    page_size: int


# API Endpoints
@router.post("/tenants", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    request: TenantCreateRequest,
    tenant_service: TenantService = Depends(get_tenant_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new tenant
    
    Args:
        request: Tenant creation request
        tenant_service: Tenant service dependency
        current_user: Current authenticated user
        
    Returns:
        Created tenant information
        
    Raises:
        HTTPException: If tenant creation fails
    """
    try:
        logger.info("Creating tenant", 
                   tenant_id=request.tenant_id,
                   user_id=current_user.get("user_id"))
        
        # Check if user has permission to create tenants
        if not current_user.get("is_admin", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to create tenants"
            )
        
        # Create tenant
        tenant_data = request.dict()
        success = await tenant_service.create_tenant(tenant_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create tenant"
            )
        
        # Get created tenant info
        tenant_info = await tenant_service.get_tenant_info(request.tenant_id)
        if not tenant_info:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve created tenant"
            )
        
        return TenantResponse(
            tenant_id=tenant_info.tenant_id,
            name=tenant_info.name,
            region=tenant_info.region,
            subscription_tier=tenant_info.subscription_tier,
            max_users=tenant_info.max_users,
            max_trades_per_day=tenant_info.max_trades_per_day,
            features=tenant_info.features,
            created_at=tenant_info.created_at,
            updated_at=tenant_info.updated_at,
            is_active=tenant_info.is_active
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create tenant", 
                    tenant_id=request.tenant_id,
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/tenants/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: str,
    tenant_service: TenantService = Depends(get_tenant_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Get tenant information
    
    Args:
        tenant_id: Tenant identifier
        tenant_service: Tenant service dependency
        current_user: Current authenticated user
        
    Returns:
        Tenant information
        
    Raises:
        HTTPException: If tenant not found or access denied
    """
    try:
        logger.info("Getting tenant info", 
                   tenant_id=tenant_id,
                   user_id=current_user.get("user_id"))
        
        # Check if user has access to this tenant
        user_tenant_id = current_user.get("tenant_id")
        if not current_user.get("is_admin", False) and user_tenant_id != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to tenant"
            )
        
        # Get tenant info
        tenant_info = await tenant_service.get_tenant_info(tenant_id)
        if not tenant_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        return TenantResponse(
            tenant_id=tenant_info.tenant_id,
            name=tenant_info.name,
            region=tenant_info.region,
            subscription_tier=tenant_info.subscription_tier,
            max_users=tenant_info.max_users,
            max_trades_per_day=tenant_info.max_trades_per_day,
            features=tenant_info.features,
            created_at=tenant_info.created_at,
            updated_at=tenant_info.updated_at,
            is_active=tenant_info.is_active
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get tenant", 
                    tenant_id=tenant_id,
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/tenants/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: str,
    request: TenantUpdateRequest,
    tenant_service: TenantService = Depends(get_tenant_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Update tenant information
    
    Args:
        tenant_id: Tenant identifier
        request: Tenant update request
        tenant_service: Tenant service dependency
        current_user: Current authenticated user
        
    Returns:
        Updated tenant information
        
    Raises:
        HTTPException: If tenant not found or update fails
    """
    try:
        logger.info("Updating tenant", 
                   tenant_id=tenant_id,
                   user_id=current_user.get("user_id"))
        
        # Check if user has permission to update this tenant
        if not current_user.get("is_admin", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to update tenant"
            )
        
        # Check if tenant exists
        tenant_info = await tenant_service.get_tenant_info(tenant_id)
        if not tenant_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        # Update tenant
        update_data = {k: v for k, v in request.dict().items() if v is not None}
        success = await tenant_service.update_tenant(tenant_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update tenant"
            )
        
        # Get updated tenant info
        updated_tenant_info = await tenant_service.get_tenant_info(tenant_id)
        
        return TenantResponse(
            tenant_id=updated_tenant_info.tenant_id,
            name=updated_tenant_info.name,
            region=updated_tenant_info.region,
            subscription_tier=updated_tenant_info.subscription_tier,
            max_users=updated_tenant_info.max_users,
            max_trades_per_day=updated_tenant_info.max_trades_per_day,
            features=updated_tenant_info.features,
            created_at=updated_tenant_info.created_at,
            updated_at=updated_tenant_info.updated_at,
            is_active=updated_tenant_info.is_active
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update tenant", 
                    tenant_id=tenant_id,
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/tenants/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant(
    tenant_id: str,
    tenant_service: TenantService = Depends(get_tenant_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete tenant and all associated data
    
    Args:
        tenant_id: Tenant identifier
        tenant_service: Tenant service dependency
        current_user: Current authenticated user
        
    Raises:
        HTTPException: If tenant not found or deletion fails
    """
    try:
        logger.info("Deleting tenant", 
                   tenant_id=tenant_id,
                   user_id=current_user.get("user_id"))
        
        # Check if user has permission to delete tenants
        if not current_user.get("is_admin", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to delete tenant"
            )
        
        # Check if tenant exists
        tenant_info = await tenant_service.get_tenant_info(tenant_id)
        if not tenant_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        # Delete tenant
        success = await tenant_service.delete_tenant(tenant_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete tenant"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete tenant", 
                    tenant_id=tenant_id,
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/tenants", response_model=TenantListResponse)
async def list_tenants(
    page: int = 1,
    page_size: int = 20,
    active_only: bool = True,
    tenant_service: TenantService = Depends(get_tenant_service),
    current_user: dict = Depends(get_current_user)
):
    """
    List all tenants
    
    Args:
        page: Page number
        page_size: Number of items per page
        active_only: Only return active tenants
        tenant_service: Tenant service dependency
        current_user: Current authenticated user
        
    Returns:
        List of tenants
        
    Raises:
        HTTPException: If access denied
    """
    try:
        logger.info("Listing tenants", 
                   user_id=current_user.get("user_id"),
                   page=page,
                   page_size=page_size)
        
        # Check if user has permission to list tenants
        if not current_user.get("is_admin", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to list tenants"
            )
        
        # Get tenants
        tenants = await tenant_service.list_tenants(active_only=active_only)
        
        # Apply pagination
        total_count = len(tenants)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_tenants = tenants[start_idx:end_idx]
        
        # Convert to response format
        tenant_responses = [
            TenantResponse(
                tenant_id=t.tenant_id,
                name=t.name,
                region=t.region,
                subscription_tier=t.subscription_tier,
                max_users=t.max_users,
                max_trades_per_day=t.max_trades_per_day,
                features=t.features,
                created_at=t.created_at,
                updated_at=t.updated_at,
                is_active=t.is_active
            ) for t in paginated_tenants
        ]
        
        return TenantListResponse(
            tenants=tenant_responses,
            total_count=total_count,
            page=page,
            page_size=page_size
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to list tenants", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/tenants/{tenant_id}/stats", response_model=TenantStatsResponse)
async def get_tenant_stats(
    tenant_id: str,
    tenant_service: TenantService = Depends(get_tenant_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Get tenant statistics
    
    Args:
        tenant_id: Tenant identifier
        tenant_service: Tenant service dependency
        current_user: Current authenticated user
        
    Returns:
        Tenant statistics
        
    Raises:
        HTTPException: If tenant not found or access denied
    """
    try:
        logger.info("Getting tenant stats", 
                   tenant_id=tenant_id,
                   user_id=current_user.get("user_id"))
        
        # Check if user has access to this tenant
        user_tenant_id = current_user.get("tenant_id")
        if not current_user.get("is_admin", False) and user_tenant_id != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to tenant"
            )
        
        # Get tenant stats
        stats = await tenant_service.get_tenant_stats(tenant_id)
        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        return TenantStatsResponse(
            tenant_id=stats["tenant_id"],
            trade_count=stats["trade_count"],
            portfolio_count=stats["portfolio_count"],
            position_count=stats["position_count"],
            total_trade_value=stats["total_trade_value"],
            database_stats=stats["database_stats"],
            timestamp=datetime.fromisoformat(stats["timestamp"])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get tenant stats", 
                    tenant_id=tenant_id,
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/tenants/{tenant_id}/features")
async def get_tenant_features(
    tenant_id: str,
    tenant_service: TenantService = Depends(get_tenant_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Get tenant features
    
    Args:
        tenant_id: Tenant identifier
        tenant_service: Tenant service dependency
        current_user: Current authenticated user
        
    Returns:
        List of enabled features
        
    Raises:
        HTTPException: If tenant not found or access denied
    """
    try:
        logger.info("Getting tenant features", 
                   tenant_id=tenant_id,
                   user_id=current_user.get("user_id"))
        
        # Check if user has access to this tenant
        user_tenant_id = current_user.get("tenant_id")
        if not current_user.get("is_admin", False) and user_tenant_id != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to tenant"
            )
        
        # Get tenant features
        features = await tenant_service.get_tenant_features(tenant_id)
        
        return {"features": features}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get tenant features", 
                    tenant_id=tenant_id,
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/tenants/{tenant_id}/features/{feature}")
async def check_tenant_feature(
    tenant_id: str,
    feature: str,
    tenant_service: TenantService = Depends(get_tenant_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Check if a feature is enabled for tenant
    
    Args:
        tenant_id: Tenant identifier
        feature: Feature name
        tenant_service: Tenant service dependency
        current_user: Current authenticated user
        
    Returns:
        Feature status
        
    Raises:
        HTTPException: If tenant not found or access denied
    """
    try:
        logger.info("Checking tenant feature", 
                   tenant_id=tenant_id,
                   feature=feature,
                   user_id=current_user.get("user_id"))
        
        # Check if user has access to this tenant
        user_tenant_id = current_user.get("tenant_id")
        if not current_user.get("is_admin", False) and user_tenant_id != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to tenant"
            )
        
        # Check feature
        is_enabled = await tenant_service.is_feature_enabled(tenant_id, feature)
        
        return {"feature": feature, "enabled": is_enabled}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to check tenant feature", 
                    tenant_id=tenant_id,
                    feature=feature,
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
