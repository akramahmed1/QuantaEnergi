"""
GraphQL module for QuantaEnergi API
Provides GraphQL support as an alternative to REST API
"""

from .schema import schema, graphql_router

__all__ = ["schema", "graphql_router"]
