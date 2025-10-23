"""
Multi-Tenancy Security Implementation
Provides tenant isolation, row-level security, and data segregation
"""

from typing import Dict, List, Any, Optional, Union
from uuid import UUID
from datetime import datetime, timezone
from enum import Enum

import structlog
from sqlalchemy import text, create_engine, MetaData, Table, Column, String, UUID as SQLUUID, Boolean
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID

logger = structlog.get_logger(__name__)


class TenantIsolationLevel(str, Enum):
    """Tenant isolation levels"""
    DATABASE = "database"  # Separate database per tenant
    SCHEMA = "schema"      # Separate schema per tenant
    ROW_LEVEL = "row_level"  # Row-level security with tenant_id column


class TenantManager:
    """Manages tenant isolation and security"""
    
    def __init__(self, 
                 database_url: str,
                 isolation_level: TenantIsolationLevel = TenantIsolationLevel.ROW_LEVEL,
                 default_tenant_id: Optional[UUID] = None):
        """
        Initialize tenant manager
        
        Args:
            database_url: Database connection URL
            isolation_level: Level of tenant isolation
            default_tenant_id: Default tenant ID for system operations
        """
        self.database_url = database_url
        self.isolation_level = isolation_level
        self.default_tenant_id = default_tenant_id
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        logger.info("TenantManager initialized", 
                   isolation_level=isolation_level.value,
                   default_tenant=default_tenant_id)
    
    def get_tenant_schema_name(self, tenant_id: UUID) -> str:
        """
        Get schema name for tenant
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            Schema name
        """
        return f"tenant_{str(tenant_id).replace('-', '_')}"
    
    def get_tenant_database_name(self, tenant_id: UUID) -> str:
        """
        Get database name for tenant
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            Database name
        """
        return f"quantaenergi_tenant_{str(tenant_id).replace('-', '_')}"
    
    async def create_tenant(self, tenant_id: UUID, tenant_name: str, admin_user_id: UUID) -> bool:
        """
        Create a new tenant with proper isolation
        
        Args:
            tenant_id: Unique tenant identifier
            tenant_name: Human-readable tenant name
            admin_user_id: ID of the admin user for this tenant
            
        Returns:
            Success status
        """
        try:
            with self.engine.connect() as conn:
                if self.isolation_level == TenantIsolationLevel.DATABASE:
                    await self._create_tenant_database(conn, tenant_id, tenant_name)
                elif self.isolation_level == TenantIsolationLevel.SCHEMA:
                    await self._create_tenant_schema(conn, tenant_id, tenant_name)
                elif self.isolation_level == TenantIsolationLevel.ROW_LEVEL:
                    await self._setup_row_level_security(conn, tenant_id, tenant_name)
                
                # Create tenant record
                await self._create_tenant_record(conn, tenant_id, tenant_name, admin_user_id)
                
                conn.commit()
                
            logger.info("Tenant created successfully", 
                       tenant_id=tenant_id, 
                       tenant_name=tenant_name,
                       isolation_level=self.isolation_level.value)
            return True
            
        except Exception as e:
            logger.error("Failed to create tenant", 
                        tenant_id=tenant_id, 
                        error=str(e))
            return False
    
    async def _create_tenant_database(self, conn, tenant_id: UUID, tenant_name: str):
        """Create separate database for tenant"""
        db_name = self.get_tenant_database_name(tenant_id)
        
        # Create database
        conn.execute(text(f"CREATE DATABASE {db_name}"))
        
        # Create tables in tenant database
        tenant_engine = create_engine(self.database_url.replace('/quantaenergi', f'/{db_name}'))
        await self._create_tenant_tables(tenant_engine)
        
        logger.info("Tenant database created", tenant_id=tenant_id, database=db_name)
    
    async def _create_tenant_schema(self, conn, tenant_id: UUID, tenant_name: str):
        """Create separate schema for tenant"""
        schema_name = self.get_tenant_schema_name(tenant_id)
        
        # Create schema
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
        
        # Set search path for tenant
        conn.execute(text(f"ALTER USER {tenant_name} SET search_path TO {schema_name}, public"))
        
        # Create tables in tenant schema
        await self._create_tenant_tables_in_schema(conn, schema_name)
        
        logger.info("Tenant schema created", tenant_id=tenant_id, schema=schema_name)
    
    async def _setup_row_level_security(self, conn, tenant_id: UUID, tenant_name: str):
        """Setup row-level security for tenant"""
        # Enable RLS on all tenant tables
        tables = ['trades', 'portfolios', 'users', 'positions', 'risk_calculations']
        
        for table in tables:
            try:
                # Enable RLS
                conn.execute(text(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY"))
                
                # Create policy for tenant isolation
                policy_name = f"tenant_isolation_{table}"
                conn.execute(text(f"""
                    CREATE POLICY {policy_name} ON {table}
                    FOR ALL
                    TO PUBLIC
                    USING (tenant_id = '{tenant_id}')
                """))
                
            except Exception as e:
                logger.warning(f"Failed to setup RLS for table {table}", error=str(e))
        
        logger.info("Row-level security configured", tenant_id=tenant_id)
    
    async def _create_tenant_record(self, conn, tenant_id: UUID, tenant_name: str, admin_user_id: UUID):
        """Create tenant record in tenants table"""
        conn.execute(text("""
            INSERT INTO tenants (id, name, admin_user_id, created_at, is_active)
            VALUES (:tenant_id, :tenant_name, :admin_user_id, :created_at, :is_active)
            ON CONFLICT (id) DO NOTHING
        """), {
            "tenant_id": tenant_id,
            "tenant_name": tenant_name,
            "admin_user_id": admin_user_id,
            "created_at": datetime.now(timezone.utc),
            "is_active": True
        })
    
    async def _create_tenant_tables(self, engine):
        """Create tables for tenant database"""
        metadata = MetaData()
        
        # Define tenant tables
        trades_table = Table('trades', metadata,
            Column('id', PostgresUUID(as_uuid=True), primary_key=True),
            Column('tenant_id', PostgresUUID(as_uuid=True), nullable=False),
            Column('trade_id', String(50), nullable=False),
            Column('trade_type', String(50), nullable=False),
            Column('commodity_type', String(50), nullable=False),
            Column('quantity', String(50), nullable=False),
            Column('price', String(50), nullable=False),
            Column('currency', String(10), nullable=False),
            Column('counterparty', String(100), nullable=False),
            Column('trade_date', String(50), nullable=False),
            Column('settlement_date', String(50), nullable=False),
            Column('status', String(50), nullable=False),
            Column('region', String(50), nullable=False),
            Column('is_sharia_compliant', Boolean, default=False),
            Column('risk_level', String(50), nullable=False),
            Column('created_by', String(100), nullable=False),
            Column('created_at', String(50), nullable=False),
            Column('updated_at', String(50)),
            Column('metadata', String(1000))
        )
        
        portfolios_table = Table('portfolios', metadata,
            Column('id', PostgresUUID(as_uuid=True), primary_key=True),
            Column('tenant_id', PostgresUUID(as_uuid=True), nullable=False),
            Column('user_id', PostgresUUID(as_uuid=True), nullable=False),
            Column('name', String(100), nullable=False),
            Column('total_value', String(50), nullable=False),
            Column('cash', String(50), nullable=False),
            Column('invested', String(50), nullable=False),
            Column('daily_change', String(50), nullable=False),
            Column('monthly_change', String(50), nullable=False),
            Column('yearly_change', String(50), nullable=False),
            Column('created_at', String(50), nullable=False),
            Column('updated_at', String(50))
        )
        
        users_table = Table('users', metadata,
            Column('id', PostgresUUID(as_uuid=True), primary_key=True),
            Column('tenant_id', PostgresUUID(as_uuid=True), nullable=False),
            Column('username', String(100), nullable=False),
            Column('email', String(255), nullable=False),
            Column('first_name', String(100), nullable=False),
            Column('last_name', String(100), nullable=False),
            Column('role', String(50), nullable=False),
            Column('is_active', Boolean, default=True),
            Column('created_at', String(50), nullable=False),
            Column('updated_at', String(50))
        )
        
        # Create all tables
        metadata.create_all(engine)
        
        logger.info("Tenant tables created")
    
    async def _create_tenant_tables_in_schema(self, conn, schema_name: str):
        """Create tables in tenant schema"""
        # Similar to _create_tenant_tables but with schema prefix
        # Implementation would be similar but with schema qualification
        pass
    
    async def delete_tenant(self, tenant_id: UUID) -> bool:
        """
        Delete a tenant and all associated data
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            Success status
        """
        try:
            with self.engine.connect() as conn:
                if self.isolation_level == TenantIsolationLevel.DATABASE:
                    db_name = self.get_tenant_database_name(tenant_id)
                    conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))
                    
                elif self.isolation_level == TenantIsolationLevel.SCHEMA:
                    schema_name = self.get_tenant_schema_name(tenant_id)
                    conn.execute(text(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE"))
                    
                elif self.isolation_level == TenantIsolationLevel.ROW_LEVEL:
                    # Delete all tenant data
                    tables = ['trades', 'portfolios', 'users', 'positions', 'risk_calculations']
                    for table in tables:
                        conn.execute(text(f"DELETE FROM {table} WHERE tenant_id = :tenant_id"), 
                                   {"tenant_id": tenant_id})
                
                # Delete tenant record
                conn.execute(text("DELETE FROM tenants WHERE id = :tenant_id"), 
                           {"tenant_id": tenant_id})
                
                conn.commit()
                
            logger.info("Tenant deleted successfully", tenant_id=tenant_id)
            return True
            
        except Exception as e:
            logger.error("Failed to delete tenant", tenant_id=tenant_id, error=str(e))
            return False
    
    async def get_tenant_by_id(self, tenant_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get tenant information by ID
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            Tenant information dictionary or None
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT id, name, admin_user_id, created_at, is_active
                    FROM tenants
                    WHERE id = :tenant_id
                """), {"tenant_id": tenant_id})
                
                row = result.fetchone()
                if row:
                    return {
                        "id": row[0],
                        "name": row[1],
                        "admin_user_id": row[2],
                        "created_at": row[3],
                        "is_active": row[4]
                    }
                return None
                
        except Exception as e:
            logger.error("Failed to get tenant", tenant_id=tenant_id, error=str(e))
            return None
    
    async def list_tenants(self) -> List[Dict[str, Any]]:
        """
        List all tenants
        
        Returns:
            List of tenant information dictionaries
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT id, name, admin_user_id, created_at, is_active
                    FROM tenants
                    ORDER BY created_at DESC
                """))
                
                tenants = []
                for row in result:
                    tenants.append({
                        "id": row[0],
                        "name": row[1],
                        "admin_user_id": row[2],
                        "created_at": row[3],
                        "is_active": row[4]
                    })
                
                return tenants
                
        except Exception as e:
            logger.error("Failed to list tenants", error=str(e))
            return []
    
    async def get_tenant_session(self, tenant_id: UUID) -> Session:
        """
        Get database session for specific tenant
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            SQLAlchemy session
        """
        if self.isolation_level == TenantIsolationLevel.DATABASE:
            db_name = self.get_tenant_database_name(tenant_id)
            tenant_db_url = self.database_url.replace('/quantaenergi', f'/{db_name}')
            tenant_engine = create_engine(tenant_db_url)
            return sessionmaker(autocommit=False, autoflush=False, bind=tenant_engine)()
            
        elif self.isolation_level == TenantIsolationLevel.SCHEMA:
            schema_name = self.get_tenant_schema_name(tenant_id)
            session = self.SessionLocal()
            session.execute(text(f"SET search_path TO {schema_name}, public"))
            return session
            
        else:  # ROW_LEVEL
            session = self.SessionLocal()
            session.execute(text("SET app.current_tenant_id = :tenant_id"), 
                          {"tenant_id": str(tenant_id)})
            return session


class TenantContext:
    """Context manager for tenant operations"""
    
    def __init__(self, tenant_manager: TenantManager, tenant_id: UUID):
        self.tenant_manager = tenant_manager
        self.tenant_id = tenant_id
        self.session = None
    
    def __enter__(self) -> Session:
        """Enter tenant context"""
        self.session = self.tenant_manager.get_tenant_session(self.tenant_id)
        return self.session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit tenant context"""
        if self.session:
            if exc_type:
                self.session.rollback()
            else:
                self.session.commit()
            self.session.close()


class TenantMiddleware:
    """Middleware for tenant context management"""
    
    def __init__(self, tenant_manager: TenantManager):
        self.tenant_manager = tenant_manager
    
    async def get_tenant_from_request(self, request) -> Optional[UUID]:
        """
        Extract tenant ID from request
        
        Args:
            request: FastAPI request object
            
        Returns:
            Tenant ID or None
        """
        # Try to get tenant from header
        tenant_id = request.headers.get("X-Tenant-ID")
        if tenant_id:
            try:
                return UUID(tenant_id)
            except ValueError:
                logger.warning("Invalid tenant ID in header", tenant_id=tenant_id)
        
        # Try to get tenant from user context
        user = getattr(request.state, 'user', None)
        if user and hasattr(user, 'tenant_id'):
            return user.tenant_id
        
        # Try to get tenant from JWT token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if token:
            try:
                # Decode JWT and extract tenant_id
                # This would integrate with your JWT authentication
                pass
            except Exception:
                pass
        
        return None
    
    async def validate_tenant_access(self, tenant_id: UUID, user_id: UUID) -> bool:
        """
        Validate user access to tenant
        
        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
            
        Returns:
            Access granted status
        """
        try:
            with self.tenant_manager.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM users
                    WHERE tenant_id = :tenant_id AND id = :user_id AND is_active = true
                """), {"tenant_id": tenant_id, "user_id": user_id})
                
                count = result.scalar()
                return count > 0
                
        except Exception as e:
            logger.error("Failed to validate tenant access", 
                        tenant_id=tenant_id, 
                        user_id=user_id, 
                        error=str(e))
            return False


# Global tenant manager instance
_tenant_manager: Optional[TenantManager] = None


def get_tenant_manager() -> TenantManager:
    """Get the global tenant manager instance"""
    global _tenant_manager
    
    if _tenant_manager is None:
        import os
        database_url = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/quantaenergi")
        isolation_level = TenantIsolationLevel(os.getenv("TENANT_ISOLATION_LEVEL", "row_level"))
        default_tenant_id = os.getenv("DEFAULT_TENANT_ID")
        
        if default_tenant_id:
            default_tenant_id = UUID(default_tenant_id)
        
        _tenant_manager = TenantManager(
            database_url=database_url,
            isolation_level=isolation_level,
            default_tenant_id=default_tenant_id
        )
    
    return _tenant_manager


async def get_tenant_context(tenant_id: UUID) -> TenantContext:
    """
    Get tenant context for operations
    
    Args:
        tenant_id: Tenant identifier
        
    Returns:
        Tenant context manager
    """
    manager = get_tenant_manager()
    return TenantContext(manager, tenant_id)
