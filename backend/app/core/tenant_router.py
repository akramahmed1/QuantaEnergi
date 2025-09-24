"""
Tenant Router for Schema-per-Tenant Multi-Tenancy
Routes database operations to tenant-specific schemas
"""

import asyncio
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from functools import wraps

import structlog
from sqlalchemy import create_engine, text, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from app.core.config import settings

logger = structlog.get_logger(__name__)


class TenantRouter:
    """
    Router for tenant-specific database operations
    Manages schema-per-tenant architecture
    """
    
    def __init__(self):
        """Initialize tenant router"""
        self.engines: Dict[str, Any] = {}
        self.sessions: Dict[str, sessionmaker] = {}
        self.tenant_schemas: Dict[str, str] = {}
        self.connection_pools: Dict[str, QueuePool] = {}
        
        # Initialize default engine
        self._initialize_default_engine()
        
        logger.info("Tenant router initialized")
    
    def _initialize_default_engine(self):
        """Initialize default database engine"""
        try:
            # Create default engine for tenant management
            default_url = settings.DATABASE_URL
            self.default_engine = create_engine(
                default_url,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=3600
            )
            
            # Create default session factory
            self.default_session_factory = sessionmaker(
                bind=self.default_engine,
                autocommit=False,
                autoflush=False
            )
            
            logger.info("Default database engine initialized")
            
        except Exception as e:
            logger.error("Failed to initialize default engine", error=str(e))
            raise
    
    def _get_tenant_schema_name(self, tenant_id: str) -> str:
        """
        Generate schema name for tenant
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            Schema name
        """
        # Sanitize tenant ID for schema name
        safe_tenant_id = tenant_id.replace("-", "_").replace(".", "_").lower()
        schema_name = f"tenant_{safe_tenant_id}"
        
        # Store mapping
        self.tenant_schemas[tenant_id] = schema_name
        
        return schema_name
    
    async def create_tenant_schema(self, tenant_id: str) -> bool:
        """
        Create database schema for tenant
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            schema_name = self._get_tenant_schema_name(tenant_id)
            
            # Create schema
            with self.default_engine.connect() as conn:
                # Check if schema exists
                result = conn.execute(text("""
                    SELECT schema_name 
                    FROM information_schema.schemata 
                    WHERE schema_name = :schema_name
                """), {"schema_name": schema_name})
                
                if result.fetchone():
                    logger.info("Schema already exists", tenant_id=tenant_id, schema=schema_name)
                    return True
                
                # Create schema
                conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
                conn.commit()
                
                # Set default privileges
                conn.execute(text(f"GRANT USAGE ON SCHEMA {schema_name} TO quantaenergi_user"))
                conn.execute(text(f"GRANT CREATE ON SCHEMA {schema_name} TO quantaenergi_user"))
                conn.commit()
                
                logger.info("Tenant schema created", tenant_id=tenant_id, schema=schema_name)
                
                # Create tenant-specific tables
                await self._create_tenant_tables(tenant_id, schema_name)
                
                return True
                
        except Exception as e:
            logger.error("Failed to create tenant schema", 
                        tenant_id=tenant_id, 
                        error=str(e))
            return False
    
    async def _create_tenant_tables(self, tenant_id: str, schema_name: str):
        """
        Create tenant-specific tables
        
        Args:
            tenant_id: Tenant identifier
            schema_name: Schema name
        """
        try:
            with self.default_engine.connect() as conn:
                # Create trades table
                conn.execute(text(f"""
                    CREATE TABLE IF NOT EXISTS {schema_name}.trades (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        trade_id VARCHAR(50) NOT NULL,
                        commodity VARCHAR(50) NOT NULL,
                        trade_type VARCHAR(20) NOT NULL,
                        quantity DECIMAL(15,2) NOT NULL,
                        price DECIMAL(15,4) NOT NULL,
                        total_value DECIMAL(15,2) NOT NULL,
                        currency VARCHAR(3) NOT NULL,
                        counterparty VARCHAR(100),
                        trade_date TIMESTAMP WITH TIME ZONE NOT NULL,
                        settlement_date TIMESTAMP WITH TIME ZONE,
                        status VARCHAR(20) NOT NULL,
                        region VARCHAR(50),
                        is_sharia_compliant BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """))
                
                # Create portfolios table
                conn.execute(text(f"""
                    CREATE TABLE IF NOT EXISTS {schema_name}.portfolios (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        portfolio_id VARCHAR(50) NOT NULL,
                        name VARCHAR(100) NOT NULL,
                        description TEXT,
                        total_value DECIMAL(15,2) DEFAULT 0,
                        cash_balance DECIMAL(15,2) DEFAULT 0,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """))
                
                # Create positions table
                conn.execute(text(f"""
                    CREATE TABLE IF NOT EXISTS {schema_name}.positions (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        portfolio_id UUID REFERENCES {schema_name}.portfolios(id),
                        commodity VARCHAR(50) NOT NULL,
                        quantity DECIMAL(15,2) NOT NULL,
                        average_price DECIMAL(15,4) NOT NULL,
                        current_price DECIMAL(15,4),
                        market_value DECIMAL(15,2),
                        unrealized_pnl DECIMAL(15,2),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """))
                
                # Create risk metrics table
                conn.execute(text(f"""
                    CREATE TABLE IF NOT EXISTS {schema_name}.risk_metrics (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        portfolio_id UUID REFERENCES {schema_name}.portfolios(id),
                        var_95 DECIMAL(15,2),
                        var_99 DECIMAL(15,2),
                        expected_shortfall DECIMAL(15,2),
                        max_loss DECIMAL(15,2),
                        sharpe_ratio DECIMAL(8,4),
                        beta DECIMAL(8,4),
                        alpha DECIMAL(8,4),
                        calculation_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """))
                
                # Create indexes
                conn.execute(text(f"""
                    CREATE INDEX IF NOT EXISTS idx_{schema_name}_trades_date 
                    ON {schema_name}.trades(trade_date)
                """))
                
                conn.execute(text(f"""
                    CREATE INDEX IF NOT EXISTS idx_{schema_name}_trades_commodity 
                    ON {schema_name}.trades(commodity)
                """))
                
                conn.execute(text(f"""
                    CREATE INDEX IF NOT EXISTS idx_{schema_name}_positions_portfolio 
                    ON {schema_name}.positions(portfolio_id)
                """))
                
                conn.commit()
                
                logger.info("Tenant tables created", 
                           tenant_id=tenant_id, 
                           schema=schema_name)
                
        except Exception as e:
            logger.error("Failed to create tenant tables", 
                        tenant_id=tenant_id, 
                        error=str(e))
            raise
    
    def get_tenant_engine(self, tenant_id: str):
        """
        Get database engine for tenant
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            Database engine
        """
        if tenant_id not in self.engines:
            # Create tenant-specific engine
            schema_name = self._get_tenant_schema_name(tenant_id)
            
            # Create engine with schema in search path
            tenant_url = f"{settings.DATABASE_URL}?options=-csearch_path%3D{schema_name},public"
            
            engine = create_engine(
                tenant_url,
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                pool_recycle=3600
            )
            
            self.engines[tenant_id] = engine
            
            # Create session factory
            session_factory = sessionmaker(
                bind=engine,
                autocommit=False,
                autoflush=False
            )
            
            self.sessions[tenant_id] = session_factory
            
            logger.info("Tenant engine created", tenant_id=tenant_id, schema=schema_name)
        
        return self.engines[tenant_id]
    
    def get_tenant_session(self, tenant_id: str) -> Session:
        """
        Get database session for tenant
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            Database session
        """
        if tenant_id not in self.sessions:
            self.get_tenant_engine(tenant_id)
        
        return self.sessions[tenant_id]()
    
    @asynccontextmanager
    async def get_tenant_session_async(self, tenant_id: str):
        """
        Get async database session for tenant
        
        Args:
            tenant_id: Tenant identifier
            
        Yields:
            Async database session
        """
        try:
            schema_name = self._get_tenant_schema_name(tenant_id)
            
            # Create async engine for tenant
            tenant_url = f"{settings.DATABASE_URL}?options=-csearch_path%3D{schema_name},public"
            
            async_engine = create_async_engine(
                tenant_url.replace("postgresql://", "postgresql+asyncpg://"),
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                pool_recycle=3600
            )
            
            async_session_factory = sessionmaker(
                bind=async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            async with async_session_factory() as session:
                yield session
                
        except Exception as e:
            logger.error("Failed to get tenant async session", 
                        tenant_id=tenant_id, 
                        error=str(e))
            raise
        finally:
            if 'async_engine' in locals():
                await async_engine.dispose()
    
    def delete_tenant_schema(self, tenant_id: str) -> bool:
        """
        Delete tenant schema and all data
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            schema_name = self._get_tenant_schema_name(tenant_id)
            
            with self.default_engine.connect() as conn:
                # Drop schema and all objects
                conn.execute(text(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE"))
                conn.commit()
                
                # Clean up engines and sessions
                if tenant_id in self.engines:
                    self.engines[tenant_id].dispose()
                    del self.engines[tenant_id]
                
                if tenant_id in self.sessions:
                    del self.sessions[tenant_id]
                
                if tenant_id in self.tenant_schemas:
                    del self.tenant_schemas[tenant_id]
                
                logger.info("Tenant schema deleted", tenant_id=tenant_id, schema=schema_name)
                return True
                
        except Exception as e:
            logger.error("Failed to delete tenant schema", 
                        tenant_id=tenant_id, 
                        error=str(e))
            return False
    
    def list_tenant_schemas(self) -> List[str]:
        """
        List all tenant schemas
        
        Returns:
            List of tenant schemas
        """
        try:
            with self.default_engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT schema_name 
                    FROM information_schema.schemata 
                    WHERE schema_name LIKE 'tenant_%'
                    ORDER BY schema_name
                """))
                
                schemas = [row[0] for row in result.fetchall()]
                logger.info("Retrieved tenant schemas", count=len(schemas))
                
                return schemas
                
        except Exception as e:
            logger.error("Failed to list tenant schemas", error=str(e))
            return []
    
    def get_tenant_stats(self, tenant_id: str) -> Dict[str, Any]:
        """
        Get statistics for tenant
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            Tenant statistics
        """
        try:
            schema_name = self._get_tenant_schema_name(tenant_id)
            
            with self.default_engine.connect() as conn:
                # Get table sizes
                result = conn.execute(text(f"""
                    SELECT 
                        schemaname,
                        tablename,
                        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
                    FROM pg_tables 
                    WHERE schemaname = '{schema_name}'
                    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                """))
                
                table_sizes = [dict(row) for row in result.fetchall()]
                
                # Get row counts
                result = conn.execute(text(f"""
                    SELECT 
                        'trades' as table_name,
                        COUNT(*) as row_count
                    FROM {schema_name}.trades
                    UNION ALL
                    SELECT 
                        'portfolios' as table_name,
                        COUNT(*) as row_count
                    FROM {schema_name}.portfolios
                    UNION ALL
                    SELECT 
                        'positions' as table_name,
                        COUNT(*) as row_count
                    FROM {schema_name}.positions
                """))
                
                row_counts = [dict(row) for row in result.fetchall()]
                
                stats = {
                    "tenant_id": tenant_id,
                    "schema_name": schema_name,
                    "table_sizes": table_sizes,
                    "row_counts": row_counts,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                logger.info("Retrieved tenant stats", tenant_id=tenant_id)
                return stats
                
        except Exception as e:
            logger.error("Failed to get tenant stats", 
                        tenant_id=tenant_id, 
                        error=str(e))
            return {}


def tenant_required(func):
    """
    Decorator to ensure tenant context is available
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract tenant_id from various sources
        tenant_id = None
        
        # Check function arguments
        if 'tenant_id' in kwargs:
            tenant_id = kwargs['tenant_id']
        elif args and hasattr(args[0], 'tenant_id'):
            tenant_id = args[0].tenant_id
        
        # Check request context (if available)
        if not tenant_id and hasattr(args[0], 'request'):
            tenant_id = args[0].request.headers.get('X-Tenant-ID')
        
        if not tenant_id:
            raise ValueError("Tenant ID is required")
        
        # Ensure tenant schema exists
        router = TenantRouter()
        if tenant_id not in router.tenant_schemas:
            await router.create_tenant_schema(tenant_id)
        
        # Add router to kwargs
        kwargs['tenant_router'] = router
        
        return await func(*args, **kwargs)
    
    return wrapper


def get_tenant_router() -> TenantRouter:
    """
    Get tenant router instance
    
    Returns:
        Tenant router instance
    """
    return TenantRouter()


# Global tenant router instance
_tenant_router: Optional[TenantRouter] = None


def get_global_tenant_router() -> TenantRouter:
    """
    Get global tenant router instance
    
    Returns:
        Global tenant router instance
    """
    global _tenant_router
    
    if _tenant_router is None:
        _tenant_router = TenantRouter()
    
    return _tenant_router
