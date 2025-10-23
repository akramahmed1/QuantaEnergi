"""
Tenant Service for Multi-Tenant Operations
Manages tenant lifecycle and operations
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass

import structlog
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.tenant_router import TenantRouter, get_tenant_router
from app.core.config import settings

logger = structlog.get_logger(__name__)


@dataclass
class TenantInfo:
    """Tenant information"""
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


class TenantService:
    """Service for managing tenant operations"""
    
    def __init__(self):
        """Initialize tenant service"""
        self.router = get_tenant_router()
        self.tenant_cache: Dict[str, TenantInfo] = {}
        
        logger.info("Tenant service initialized")
    
    async def create_tenant(self, tenant_data: Dict[str, Any]) -> bool:
        """
        Create a new tenant
        
        Args:
            tenant_data: Tenant information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            tenant_id = tenant_data.get("tenant_id")
            if not tenant_id:
                raise ValueError("Tenant ID is required")
            
            logger.info("Creating tenant", tenant_id=tenant_id)
            
            # Create tenant schema
            success = await self.router.create_tenant_schema(tenant_id)
            if not success:
                raise Exception("Failed to create tenant schema")
            
            # Store tenant information in main database
            with self.router.default_engine.connect() as conn:
                # Check if tenant already exists
                result = conn.execute(text("""
                    SELECT id FROM tenants WHERE tenant_id = :tenant_id
                """), {"tenant_id": tenant_id})
                
                if result.fetchone():
                    logger.warning("Tenant already exists", tenant_id=tenant_id)
                    return True
                
                # Insert tenant record
                conn.execute(text("""
                    INSERT INTO tenants (
                        tenant_id, name, region, subscription_tier, 
                        max_users, max_trades_per_day, features, 
                        created_at, updated_at, is_active
                    ) VALUES (
                        :tenant_id, :name, :region, :subscription_tier,
                        :max_users, :max_trades_per_day, :features,
                        :created_at, :updated_at, :is_active
                    )
                """), {
                    "tenant_id": tenant_id,
                    "name": tenant_data.get("name", ""),
                    "region": tenant_data.get("region", "us"),
                    "subscription_tier": tenant_data.get("subscription_tier", "basic"),
                    "max_users": tenant_data.get("max_users", 10),
                    "max_trades_per_day": tenant_data.get("max_trades_per_day", 1000),
                    "features": tenant_data.get("features", []),
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc),
                    "is_active": True
                })
                
                conn.commit()
            
            # Cache tenant info
            tenant_info = TenantInfo(
                tenant_id=tenant_id,
                name=tenant_data.get("name", ""),
                region=tenant_data.get("region", "us"),
                subscription_tier=tenant_data.get("subscription_tier", "basic"),
                max_users=tenant_data.get("max_users", 10),
                max_trades_per_day=tenant_data.get("max_trades_per_day", 1000),
                features=tenant_data.get("features", []),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                is_active=True
            )
            
            self.tenant_cache[tenant_id] = tenant_info
            
            logger.info("Tenant created successfully", tenant_id=tenant_id)
            return True
            
        except Exception as e:
            logger.error("Failed to create tenant", 
                        tenant_id=tenant_data.get("tenant_id"), 
                        error=str(e))
            return False
    
    async def get_tenant_info(self, tenant_id: str) -> Optional[TenantInfo]:
        """
        Get tenant information
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            Tenant information or None
        """
        try:
            # Check cache first
            if tenant_id in self.tenant_cache:
                return self.tenant_cache[tenant_id]
            
            # Query database
            with self.router.default_engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT tenant_id, name, region, subscription_tier,
                           max_users, max_trades_per_day, features,
                           created_at, updated_at, is_active
                    FROM tenants 
                    WHERE tenant_id = :tenant_id
                """), {"tenant_id": tenant_id})
                
                row = result.fetchone()
                if not row:
                    return None
                
                tenant_info = TenantInfo(
                    tenant_id=row[0],
                    name=row[1],
                    region=row[2],
                    subscription_tier=row[3],
                    max_users=row[4],
                    max_trades_per_day=row[5],
                    features=row[6] if row[6] else [],
                    created_at=row[7],
                    updated_at=row[8],
                    is_active=row[9]
                )
                
                # Cache the result
                self.tenant_cache[tenant_id] = tenant_info
                
                return tenant_info
                
        except Exception as e:
            logger.error("Failed to get tenant info", 
                        tenant_id=tenant_id, 
                        error=str(e))
            return None
    
    async def update_tenant(self, tenant_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update tenant information
        
        Args:
            tenant_id: Tenant identifier
            update_data: Update data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Updating tenant", tenant_id=tenant_id)
            
            # Build update query
            update_fields = []
            update_values = {"tenant_id": tenant_id}
            
            for field, value in update_data.items():
                if field in ["name", "region", "subscription_tier", "max_users", 
                           "max_trades_per_day", "features", "is_active"]:
                    update_fields.append(f"{field} = :{field}")
                    update_values[field] = value
            
            if not update_fields:
                logger.warning("No valid fields to update", tenant_id=tenant_id)
                return False
            
            update_fields.append("updated_at = :updated_at")
            update_values["updated_at"] = datetime.now(timezone.utc)
            
            # Update database
            with self.router.default_engine.connect() as conn:
                conn.execute(text(f"""
                    UPDATE tenants 
                    SET {', '.join(update_fields)}
                    WHERE tenant_id = :tenant_id
                """), update_values)
                
                conn.commit()
            
            # Update cache
            if tenant_id in self.tenant_cache:
                tenant_info = self.tenant_cache[tenant_id]
                for field, value in update_data.items():
                    if hasattr(tenant_info, field):
                        setattr(tenant_info, field, value)
                tenant_info.updated_at = datetime.now(timezone.utc)
            
            logger.info("Tenant updated successfully", tenant_id=tenant_id)
            return True
            
        except Exception as e:
            logger.error("Failed to update tenant", 
                        tenant_id=tenant_id, 
                        error=str(e))
            return False
    
    async def delete_tenant(self, tenant_id: str) -> bool:
        """
        Delete tenant and all associated data
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Deleting tenant", tenant_id=tenant_id)
            
            # Delete tenant schema
            success = self.router.delete_tenant_schema(tenant_id)
            if not success:
                raise Exception("Failed to delete tenant schema")
            
            # Mark tenant as inactive in main database
            with self.router.default_engine.connect() as conn:
                conn.execute(text("""
                    UPDATE tenants 
                    SET is_active = false, updated_at = :updated_at
                    WHERE tenant_id = :tenant_id
                """), {
                    "tenant_id": tenant_id,
                    "updated_at": datetime.now(timezone.utc)
                })
                
                conn.commit()
            
            # Remove from cache
            if tenant_id in self.tenant_cache:
                del self.tenant_cache[tenant_id]
            
            logger.info("Tenant deleted successfully", tenant_id=tenant_id)
            return True
            
        except Exception as e:
            logger.error("Failed to delete tenant", 
                        tenant_id=tenant_id, 
                        error=str(e))
            return False
    
    async def list_tenants(self, active_only: bool = True) -> List[TenantInfo]:
        """
        List all tenants
        
        Args:
            active_only: Only return active tenants
            
        Returns:
            List of tenant information
        """
        try:
            with self.router.default_engine.connect() as conn:
                query = """
                    SELECT tenant_id, name, region, subscription_tier,
                           max_users, max_trades_per_day, features,
                           created_at, updated_at, is_active
                    FROM tenants
                """
                
                if active_only:
                    query += " WHERE is_active = true"
                
                query += " ORDER BY created_at DESC"
                
                result = conn.execute(text(query))
                
                tenants = []
                for row in result.fetchall():
                    tenant_info = TenantInfo(
                        tenant_id=row[0],
                        name=row[1],
                        region=row[2],
                        subscription_tier=row[3],
                        max_users=row[4],
                        max_trades_per_day=row[5],
                        features=row[6] if row[6] else [],
                        created_at=row[7],
                        updated_at=row[8],
                        is_active=row[9]
                    )
                    tenants.append(tenant_info)
                
                logger.info("Retrieved tenants list", count=len(tenants))
                return tenants
                
        except Exception as e:
            logger.error("Failed to list tenants", error=str(e))
            return []
    
    async def get_tenant_stats(self, tenant_id: str) -> Dict[str, Any]:
        """
        Get tenant statistics
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            Tenant statistics
        """
        try:
            # Get basic tenant info
            tenant_info = await self.get_tenant_info(tenant_id)
            if not tenant_info:
                return {}
            
            # Get database stats
            db_stats = self.router.get_tenant_stats(tenant_id)
            
            # Get tenant session for additional stats
            session = self.router.get_tenant_session(tenant_id)
            
            try:
                # Get trade count
                result = session.execute(text("SELECT COUNT(*) FROM trades"))
                trade_count = result.scalar()
                
                # Get portfolio count
                result = session.execute(text("SELECT COUNT(*) FROM portfolios"))
                portfolio_count = result.scalar()
                
                # Get position count
                result = session.execute(text("SELECT COUNT(*) FROM positions"))
                position_count = result.scalar()
                
                # Get total trade value
                result = session.execute(text("SELECT SUM(total_value) FROM trades"))
                total_trade_value = result.scalar() or 0
                
                stats = {
                    "tenant_id": tenant_id,
                    "tenant_info": tenant_info,
                    "trade_count": trade_count,
                    "portfolio_count": portfolio_count,
                    "position_count": position_count,
                    "total_trade_value": float(total_trade_value),
                    "database_stats": db_stats,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                logger.info("Retrieved tenant stats", tenant_id=tenant_id)
                return stats
                
            finally:
                session.close()
                
        except Exception as e:
            logger.error("Failed to get tenant stats", 
                        tenant_id=tenant_id, 
                        error=str(e))
            return {}
    
    async def validate_tenant_limits(self, tenant_id: str, operation: str) -> bool:
        """
        Validate tenant limits for operations
        
        Args:
            tenant_id: Tenant identifier
            operation: Operation type
            
        Returns:
            True if within limits, False otherwise
        """
        try:
            tenant_info = await self.get_tenant_info(tenant_id)
            if not tenant_info or not tenant_info.is_active:
                return False
            
            # Get current usage
            session = self.router.get_tenant_session(tenant_id)
            
            try:
                if operation == "trade":
                    # Check daily trade limit
                    result = session.execute(text("""
                        SELECT COUNT(*) FROM trades 
                        WHERE trade_date >= CURRENT_DATE
                    """))
                    daily_trades = result.scalar()
                    
                    if daily_trades >= tenant_info.max_trades_per_day:
                        logger.warning("Daily trade limit exceeded", 
                                     tenant_id=tenant_id,
                                     daily_trades=daily_trades,
                                     limit=tenant_info.max_trades_per_day)
                        return False
                
                elif operation == "user":
                    # Check user limit (this would need user management integration)
                    # For now, just return True
                    pass
                
                return True
                
            finally:
                session.close()
                
        except Exception as e:
            logger.error("Failed to validate tenant limits", 
                        tenant_id=tenant_id, 
                        operation=operation,
                        error=str(e))
            return False
    
    async def get_tenant_features(self, tenant_id: str) -> List[str]:
        """
        Get tenant features
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            List of enabled features
        """
        try:
            tenant_info = await self.get_tenant_info(tenant_id)
            if not tenant_info:
                return []
            
            return tenant_info.features
            
        except Exception as e:
            logger.error("Failed to get tenant features", 
                        tenant_id=tenant_id, 
                        error=str(e))
            return []
    
    async def is_feature_enabled(self, tenant_id: str, feature: str) -> bool:
        """
        Check if a feature is enabled for tenant
        
        Args:
            tenant_id: Tenant identifier
            feature: Feature name
            
        Returns:
            True if feature is enabled, False otherwise
        """
        try:
            features = await self.get_tenant_features(tenant_id)
            return feature in features
            
        except Exception as e:
            logger.error("Failed to check feature", 
                        tenant_id=tenant_id, 
                        feature=feature,
                        error=str(e))
            return False


def get_tenant_service() -> TenantService:
    """
    Get tenant service instance
    
    Returns:
        Tenant service instance
    """
    return TenantService()
