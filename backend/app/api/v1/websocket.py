"""
WebSocket API Endpoints for Real-Time Communication
Provides WebSocket connections for real-time updates and offline-first capabilities
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException
from typing import Optional
import logging

from app.core.websocket_manager import WebSocketEndpoint, connection_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSocket"])

# WebSocket endpoint instance
websocket_endpoint = WebSocketEndpoint()

@router.websocket("/trade-updates/{user_id}/{organization_id}")
async def websocket_trade_updates(
    websocket: WebSocket,
    user_id: str,
    organization_id: str
):
    """
    WebSocket endpoint for real-time trade updates
    """
    try:
        await websocket_endpoint.handle_websocket(websocket, user_id, organization_id)
    except Exception as e:
        logger.error(f"Error in trade updates WebSocket: {e}")

@router.websocket("/market-data/{user_id}/{organization_id}")
async def websocket_market_data(
    websocket: WebSocket,
    user_id: str,
    organization_id: str
):
    """
    WebSocket endpoint for real-time market data
    """
    try:
        await websocket_endpoint.handle_websocket(websocket, user_id, organization_id)
    except Exception as e:
        logger.error(f"Error in market data WebSocket: {e}")

@router.websocket("/risk-alerts/{user_id}/{organization_id}")
async def websocket_risk_alerts(
    websocket: WebSocket,
    user_id: str,
    organization_id: str
):
    """
    WebSocket endpoint for real-time risk alerts
    """
    try:
        await websocket_endpoint.handle_websocket(websocket, user_id, organization_id)
    except Exception as e:
        logger.error(f"Error in risk alerts WebSocket: {e}")

@router.websocket("/compliance-updates/{user_id}/{organization_id}")
async def websocket_compliance_updates(
    websocket: WebSocket,
    user_id: str,
    organization_id: str
):
    """
    WebSocket endpoint for real-time compliance updates
    """
    try:
        await websocket_endpoint.handle_websocket(websocket, user_id, organization_id)
    except Exception as e:
        logger.error(f"Error in compliance updates WebSocket: {e}")

@router.websocket("/general/{user_id}/{organization_id}")
async def websocket_general(
    websocket: WebSocket,
    user_id: str,
    organization_id: str
):
    """
    General WebSocket endpoint for all types of updates
    """
    try:
        await websocket_endpoint.handle_websocket(websocket, user_id, organization_id)
    except Exception as e:
        logger.error(f"Error in general WebSocket: {e}")

# WebSocket management endpoints
@router.get("/stats")
async def get_websocket_stats():
    """
    Get WebSocket connection statistics
    """
    try:
        stats = connection_manager.get_connection_stats()
        return {
            "success": True,
            "data": stats,
            "message": "WebSocket statistics retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting WebSocket stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/connections/{connection_id}")
async def get_connection_info(connection_id: str):
    """
    Get information about a specific WebSocket connection
    """
    try:
        info = connection_manager.get_connection_info(connection_id)
        if not info:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        return {
            "success": True,
            "data": info,
            "message": "Connection information retrieved successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting connection info: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/cleanup")
async def cleanup_inactive_connections():
    """
    Clean up inactive WebSocket connections
    """
    try:
        await connection_manager.cleanup_inactive_connections()
        return {
            "success": True,
            "message": "Inactive connections cleaned up successfully"
        }
    except Exception as e:
        logger.error(f"Error cleaning up connections: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/broadcast/organization/{organization_id}")
async def broadcast_to_organization(
    organization_id: str,
    message: dict
):
    """
    Broadcast a message to all connections in an organization
    """
    try:
        await connection_manager.broadcast_to_organization(organization_id, message)
        return {
            "success": True,
            "message": f"Message broadcasted to organization {organization_id} successfully"
        }
    except Exception as e:
        logger.error(f"Error broadcasting to organization: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/broadcast/user/{user_id}")
async def broadcast_to_user(
    user_id: str,
    message: dict
):
    """
    Broadcast a message to all connections of a specific user
    """
    try:
        await connection_manager.broadcast_to_user(user_id, message)
        return {
            "success": True,
            "message": f"Message broadcasted to user {user_id} successfully"
        }
    except Exception as e:
        logger.error(f"Error broadcasting to user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/broadcast/all")
async def broadcast_to_all(message: dict):
    """
    Broadcast a message to all active connections
    """
    try:
        await connection_manager.broadcast_to_all(message)
        return {
            "success": True,
            "message": "Message broadcasted to all connections successfully"
        }
    except Exception as e:
        logger.error(f"Error broadcasting to all: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/offline-queue/process/{user_id}")
async def process_offline_queue(user_id: str):
    """
    Process offline queue for a specific user
    """
    try:
        await connection_manager.process_offline_queue(user_id)
        return {
            "success": True,
            "message": f"Offline queue processed for user {user_id} successfully"
        }
    except Exception as e:
        logger.error(f"Error processing offline queue: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/offline-queue/{user_id}")
async def get_offline_queue(user_id: str):
    """
    Get offline queue for a specific user
    """
    try:
        if user_id in connection_manager.offline_queue:
            queue = connection_manager.offline_queue[user_id]
            return {
                "success": True,
                "data": {
                    "user_id": user_id,
                    "queue_size": len(queue),
                    "items": queue
                },
                "message": "Offline queue retrieved successfully"
            }
        else:
            return {
                "success": True,
                "data": {
                    "user_id": user_id,
                    "queue_size": 0,
                    "items": []
                },
                "message": "No offline queue found for user"
            }
    except Exception as e:
        logger.error(f"Error getting offline queue: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Health check endpoint
@router.get("/health")
async def websocket_health():
    """
    WebSocket health check endpoint
    """
    try:
        stats = connection_manager.get_connection_stats()
        return {
            "success": True,
            "data": {
                "status": "healthy",
                "active_connections": stats["active_connections"],
                "total_connections": stats["total_connections"],
                "message": "WebSocket service is healthy"
            }
        }
    except Exception as e:
        logger.error(f"WebSocket health check failed: {e}")
        return {
            "success": False,
            "data": {
                "status": "unhealthy",
                "error": str(e),
                "message": "WebSocket service is unhealthy"
            }
        }
