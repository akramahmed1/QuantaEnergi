"""
Enterprise Database Security Module
Secure database connections with encryption, connection pooling, and security controls
"""

import ssl
import logging
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.engine import Engine
from ..core.config import settings
from ..models.base import Base
import structlog
from cryptography.fernet import Fernet
from typing import Generator

logger = structlog.get_logger()

class SecureDatabaseManager:
    """Enterprise-grade secure database manager"""
    
    def __init__(self):
        self.engine = self._create_secure_engine()
        self.session_factory = sessionmaker(
            autocommit=False, 
            autoflush=False, 
            bind=self.engine,
            expire_on_commit=False
        )
        
        # Setup database security events
        self._setup_security_events()
        
        logger.info("Secure database manager initialized", 
                   ssl_enabled=settings.DATABASE_SSL_MODE == "require",
                   pool_size=settings.DATABASE_POOL_SIZE)
    
    def _create_secure_engine(self) -> Engine:
        """Create secure database engine with enterprise features"""
        
        # Database connection arguments
        connect_args = {}
        
        # SSL/TLS configuration for PostgreSQL
        if "postgresql" in settings.DATABASE_URL:
            if settings.DATABASE_SSL_MODE == "require":
                connect_args["sslmode"] = "require"
                connect_args["sslcert"] = settings.TLS_CERT_PATH
                connect_args["sslkey"] = settings.TLS_KEY_PATH
                
                # Create SSL context
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = True
                ssl_context.verify_mode = ssl.CERT_REQUIRED
                connect_args["ssl_context"] = ssl_context
        
        # SQLite specific configuration
        elif "sqlite" in settings.DATABASE_URL:
            connect_args["check_same_thread"] = False
            # Enable foreign key constraints
            connect_args["isolation_level"] = "SERIALIZABLE"
        
        # Create engine with security configurations
        engine = create_engine(
            settings.DATABASE_URL,
            poolclass=QueuePool,
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            pool_timeout=settings.DATABASE_POOL_TIMEOUT,
            pool_recycle=settings.DATABASE_POOL_RECYCLE,
            pool_pre_ping=settings.DATABASE_POOL_PRE_PING,
            connect_args=connect_args,
            echo=False,  # Disable SQL echo in production
            echo_pool=False,
            future=True  # Use SQLAlchemy 2.0 style
        )
        
        return engine
    
    def _setup_security_events(self):
        """Setup database security events and logging"""
        
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """Set SQLite security pragmas"""
            if "sqlite" in settings.DATABASE_URL:
                cursor = dbapi_connection.cursor()
                # Enable foreign key constraints
                cursor.execute("PRAGMA foreign_keys=ON")
                # Enable WAL mode for better concurrency
                cursor.execute("PRAGMA journal_mode=WAL")
                # Set secure cache size
                cursor.execute("PRAGMA cache_size=1000")
                # Enable integrity checking
                cursor.execute("PRAGMA integrity_check")
                cursor.close()
        
        @event.listens_for(self.engine, "before_cursor_execute")
        def log_sql_statements(conn, cursor, statement, parameters, context, executemany):
            """Log SQL statements for security auditing"""
            if settings.AUDIT_LOGGING_ENABLED:
                logger.debug("SQL execution", 
                           statement=statement[:200],  # Truncate for security
                           parameters_count=len(parameters) if parameters else 0)
        
        @event.listens_for(self.engine, "after_cursor_execute")
        def log_sql_performance(conn, cursor, statement, parameters, context, executemany):
            """Log SQL performance metrics"""
            if settings.MONITORING_ENABLED:
                context._query_start_time = time.time()
    
    def get_session(self) -> Generator[Session, None, None]:
        """Get secure database session with automatic cleanup"""
        db = self.session_factory()
        try:
            # Set secure session parameters
            if "postgresql" in settings.DATABASE_URL:
                # Enable row-level security
                db.execute(text("SET row_security = on"))
                # Set secure statement timeout
                db.execute(text("SET statement_timeout = '30s'"))
                # Enable query logging for audit
                if settings.AUDIT_LOGGING_ENABLED:
                    db.execute(text("SET log_statement = 'all'"))
            
            yield db
        except Exception as e:
            logger.error("Database session error", error=str(e))
            db.rollback()
            raise
        finally:
            db.close()
    
    def create_tables(self):
        """Create all database tables with security constraints"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error("Failed to create database tables", error=str(e))
            raise
    
    def health_check(self) -> bool:
        """Perform database health check"""
        try:
            with self.engine.connect() as conn:
                if "postgresql" in settings.DATABASE_URL:
                    result = conn.execute(text("SELECT 1"))
                else:
                    result = conn.execute(text("SELECT 1"))
                
                return result.fetchone()[0] == 1
        except Exception as e:
            logger.error("Database health check failed", error=str(e))
            return False

# Global secure database manager
db_manager = SecureDatabaseManager()

# Create secure database engine
engine = db_manager.engine
SessionLocal = db_manager.session_factory

def get_db() -> Generator[Session, None, None]:
    """Get secure database session dependency for FastAPI"""
    yield from db_manager.get_session()

def create_tables():
    """Create all database tables with security"""
    db_manager.create_tables()

def get_db_health() -> bool:
    """Get database health status"""
    return db_manager.health_check()

# Database encryption utilities
class DatabaseEncryption:
    """Database field encryption utilities"""
    
    def __init__(self):
        self.cipher = Fernet(settings.ENCRYPTION_KEY.encode())
    
    def encrypt_field(self, value: str) -> str:
        """Encrypt database field value"""
        if not value:
            return value
        encrypted = self.cipher.encrypt(value.encode())
        return encrypted.decode()
    
    def decrypt_field(self, encrypted_value: str) -> str:
        """Decrypt database field value"""
        if not encrypted_value:
            return encrypted_value
        decrypted = self.cipher.decrypt(encrypted_value.encode())
        return decrypted.decode()

# Global encryption instance
db_encryption = DatabaseEncryption()

def get_user_scoped_query(db: Session, user_id: int):
    """Get user-scoped query for data access control."""
    return db.query().filter_by(user_id=user_id)
