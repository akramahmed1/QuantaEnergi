"""
Tenant-aware database session for multi-tenancy data isolation.

This module provides a custom SQLAlchemy session that automatically
scopes all queries to the authenticated user's company_id, ensuring
complete data isolation between tenants.
"""

from sqlalchemy import event, and_, inspect
from sqlalchemy.orm import Session, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Any, Type
import uuid
from .models import CompanyScopedModel, Base

class TenantAwareSession(Session):
    """
    Custom SQLAlchemy session that automatically scopes queries to company_id.
    
    This session ensures that all queries for tenant-scoped models automatically
    include a WHERE clause for company_id, preventing data leakage between tenants.
    """
    
    def __init__(self, company_id: uuid.UUID, *args, **kwargs):
        """
        Initialize tenant-aware session.
        
        Args:
            company_id: The UUID of the company/tenant this session belongs to
            *args, **kwargs: Standard Session arguments
        """
        self.company_id = company_id
        super().__init__(*args, **kwargs)
        
        # Register event listeners for automatic company scoping
        self._setup_company_scoping()
    
    def _setup_company_scoping(self):
        """Setup automatic company scoping for all queries."""
        
        @event.listens_for(self, "do_orm_execute")
        def _add_company_scope(execute_state):
            """Automatically add company_id filter to all queries."""
            if not execute_state.is_column_load:
                if hasattr(execute_state.select_statement, 'froms'):
                    for from_clause in execute_state.select_statement.froms:
                        if hasattr(from_clause, 'entity_namespace'):
                            entity_class = from_clause.entity_namespace.class_
                            if (isinstance(entity_class, type) and 
                                issubclass(entity_class, CompanyScopedModel)):
                                # Check if company_id filter already exists
                                if not self._has_company_filter(execute_state.select_statement):
                                    # Add company_id filter
                                    execute_state.select_statement = (
                                        execute_state.select_statement.where(
                                            from_clause.c.company_id == self.company_id
                                        )
                                    )
    
    def _has_company_filter(self, statement) -> bool:
        """Check if a company_id filter already exists in the statement."""
        if hasattr(statement, 'whereclause') and statement.whereclause:
            # Check if company_id filter exists in WHERE clause
            where_clause = statement.whereclause
            if hasattr(where_clause, 'left') and hasattr(where_clause, 'right'):
                if (hasattr(where_clause.left, 'name') and 
                    where_clause.left.name == 'company_id'):
                    return True
        return False
    
    def query(self, *entities, **kwargs) -> Query:
        """
        Override query method to ensure company scoping.
        
        Args:
            *entities: Query entities
            **kwargs: Query options
            
        Returns:
            Company-scoped query
        """
        query = super().query(*entities, **kwargs)
        
        # Apply company scoping to the query
        for entity in entities:
            if isinstance(entity, type) and issubclass(entity, CompanyScopedModel):
                query = query.filter(entity.company_id == self.company_id)
        
        return query
    
    def add(self, instance: Any) -> None:
        """
        Override add method to automatically set company_id.
        
        Args:
            instance: Model instance to add
        """
        if isinstance(instance, CompanyScopedModel):
            # Ensure company_id is set
            if not hasattr(instance, 'company_id') or instance.company_id is None:
                instance.company_id = self.company_id
        
        super().add(instance)
    
    def merge(self, instance: Any, load: bool = True) -> Any:
        """
        Override merge method to ensure company scoping.
        
        Args:
            instance: Model instance to merge
            load: Whether to load existing instance
            
        Returns:
            Merged instance
        """
        if isinstance(instance, CompanyScopedModel):
            # Ensure company_id is set
            if not hasattr(instance, 'company_id') or instance.company_id is None:
                instance.company_id = self.company_id
        
        return super().merge(instance, load=load)

class AsyncTenantAwareSession(AsyncSession):
    """
    Async version of tenant-aware session.
    
    This provides the same functionality as TenantAwareSession but for async operations.
    """
    
    def __init__(self, company_id: uuid.UUID, *args, **kwargs):
        """
        Initialize async tenant-aware session.
        
        Args:
            company_id: The UUID of the company/tenant this session belongs to
            *args, **kwargs: Standard AsyncSession arguments
        """
        self.company_id = company_id
        super().__init__(*args, **kwargs)
    
    async def execute(self, statement, *args, **kwargs):
        """
        Override execute to add company scoping for async operations.
        
        Args:
            statement: SQL statement to execute
            *args, **kwargs: Execution arguments
            
        Returns:
            Execution result
        """
        # Apply company scoping for select statements
        if hasattr(statement, 'froms'):
            for from_clause in statement.froms:
                if hasattr(from_clause, 'entity_namespace'):
                    entity_class = from_clause.entity_namespace.class_
                    if (isinstance(entity_class, type) and 
                        issubclass(entity_class, CompanyScopedModel)):
                        # Add company_id filter if not present
                        if not self._has_company_filter_async(statement):
                            statement = statement.where(
                                from_clause.c.company_id == self.company_id
                            )
        
        return await super().execute(statement, *args, **kwargs)
    
    def _has_company_filter_async(self, statement) -> bool:
        """Check if company_id filter exists in async statement."""
        return self._has_company_filter(statement)
    
    def _has_company_filter(self, statement) -> bool:
        """Check if a company_id filter already exists in the statement."""
        if hasattr(statement, 'whereclause') and statement.whereclause:
            where_clause = statement.whereclause
            if hasattr(where_clause, 'left') and hasattr(where_clause, 'right'):
                if (hasattr(where_clause.left, 'name') and 
                    where_clause.left.name == 'company_id'):
                    return True
        return False

def create_tenant_session_factory(company_id: uuid.UUID):
    """
    Create a factory function for tenant-aware sessions.
    
    Args:
        company_id: The company ID to scope sessions to
        
    Returns:
        Factory function that creates tenant-aware sessions
    """
    def session_factory(*args, **kwargs):
        return TenantAwareSession(company_id, *args, **kwargs)
    
    return session_factory

def create_async_tenant_session_factory(company_id: uuid.UUID):
    """
    Create a factory function for async tenant-aware sessions.
    
    Args:
        company_id: The company ID to scope sessions to
        
    Returns:
        Factory function that creates async tenant-aware sessions
    """
    def session_factory(*args, **kwargs):
        return AsyncTenantAwareSession(company_id, *args, **kwargs)
    
    return session_factory 