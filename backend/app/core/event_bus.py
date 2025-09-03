"""
Event Bus System for QuantaEnergi Platform
Implements event-driven architecture for loose coupling between services
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Type
from uuid import uuid4
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class EventType(Enum):
    """Core event types for the platform"""
    # Trade lifecycle events
    TRADE_CAPTURED = "trade_captured"
    TRADE_VALIDATED = "trade_validated"
    TRADE_CONFIRMED = "trade_confirmed"
    TRADE_ALLOCATED = "trade_allocated"
    TRADE_SETTLED = "trade_settled"
    TRADE_INVOICED = "trade_invoiced"
    TRADE_PAID = "trade_paid"
    TRADE_CANCELLED = "trade_cancelled"
    
    # Risk management events
    RISK_LIMIT_BREACHED = "risk_limit_breached"
    CREDIT_LIMIT_EXCEEDED = "credit_limit_exceeded"
    POSITION_LIMIT_VIOLATION = "position_limit_violation"
    VAR_ALERT = "var_alert"
    
    # Compliance events
    COMPLIANCE_VIOLATION = "compliance_violation"
    REGULATORY_REPORT_DUE = "regulatory_report_due"
    AUDIT_TRAIL_CREATED = "audit_trail_created"
    
    # Market data events
    MARKET_PRICE_UPDATE = "market_price_update"
    MARKET_VOLATILITY_ALERT = "market_volatility_alert"
    EXCHANGE_STATUS_CHANGE = "exchange_status_change"
    
    # System events
    SYSTEM_HEALTH_ALERT = "system_health_alert"
    PERFORMANCE_METRIC_UPDATE = "performance_metric_update"
    USER_ACTIVITY_LOG = "user_activity_log"

@dataclass
class EventMetadata:
    """Metadata for all events"""
    event_id: str
    event_type: EventType
    timestamp: datetime
    correlation_id: str
    user_id: Optional[str] = None
    organization_id: Optional[str] = None
    source_service: str = ""
    version: str = "1.0"

@dataclass
class BaseEvent:
    """Base class for all events"""
    metadata: EventMetadata
    payload: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        return {
            "metadata": asdict(self.metadata),
            "payload": self.payload
        }
    
    def to_json(self) -> str:
        """Convert event to JSON string"""
        return json.dumps(self.to_dict(), default=str)

class EventHandler:
    """Base class for event handlers"""
    
    async def handle(self, event: BaseEvent) -> None:
        """Handle an event - must be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement handle method")
    
    def can_handle(self, event_type: EventType) -> bool:
        """Check if this handler can handle the given event type"""
        return True

class EventBus:
    """Central event bus for the platform"""
    
    def __init__(self):
        self._subscribers: Dict[EventType, List[EventHandler]] = {}
        self._middleware: List[Callable] = []
        self._event_history: List[BaseEvent] = []
        self._max_history_size = 10000
        self._is_running = False
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._worker_task: Optional[asyncio.Task] = None
    
    async def start(self) -> None:
        """Start the event bus worker"""
        if self._is_running:
            return
        
        self._is_running = True
        self._worker_task = asyncio.create_task(self._worker())
        logger.info("Event bus started successfully")
    
    async def stop(self) -> None:
        """Stop the event bus worker"""
        if not self._is_running:
            return
        
        self._is_running = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Event bus stopped successfully")
    
    async def _worker(self) -> None:
        """Background worker for processing events"""
        while self._is_running:
            try:
                event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)
                await self._process_event(event)
                self._event_queue.task_done()
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error in event worker: {e}")
    
    async def _process_event(self, event: BaseEvent) -> None:
        """Process a single event"""
        try:
            # Apply middleware
            for middleware in self._middleware:
                event = await middleware(event)
            
            # Store in history
            self._event_history.append(event)
            if len(self._event_history) > self._max_history_size:
                self._event_history.pop(0)
            
            # Notify subscribers
            handlers = self._subscribers.get(event.metadata.event_type, [])
            if handlers:
                await asyncio.gather(*[
                    self._safe_handler_call(handler, event)
                    for handler in handlers
                ], return_exceptions=True)
            
            logger.debug(f"Processed event: {event.metadata.event_type.value}")
            
        except Exception as e:
            logger.error(f"Error processing event {event.metadata.event_id}: {e}")
    
    async def _safe_handler_call(self, handler: EventHandler, event: BaseEvent) -> None:
        """Safely call an event handler"""
        try:
            await handler.handle(event)
        except Exception as e:
            logger.error(f"Handler {handler.__class__.__name__} failed for event {event.metadata.event_id}: {e}")
    
    async def publish(self, event: BaseEvent) -> None:
        """Publish an event to the bus"""
        if not self._is_running:
            raise RuntimeError("Event bus is not running")
        
        await self._event_queue.put(event)
        logger.debug(f"Published event: {event.metadata.event_type.value}")
    
    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """Subscribe to events of a specific type"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        self._subscribers[event_type].append(handler)
        logger.info(f"Handler {handler.__class__.__name__} subscribed to {event_type.value}")
    
    def unsubscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """Unsubscribe from events of a specific type"""
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(handler)
                logger.info(f"Handler {handler.__class__.__name__} unsubscribed from {event_type.value}")
            except ValueError:
                logger.warning(f"Handler {handler.__class__.__name__} was not subscribed to {event_type.value}")
    
    def add_middleware(self, middleware: Callable) -> None:
        """Add middleware to the event processing pipeline"""
        self._middleware.append(middleware)
        logger.info(f"Added middleware: {middleware.__class__.__name__}")
    
    def get_event_history(self, event_type: Optional[EventType] = None, limit: int = 100) -> List[BaseEvent]:
        """Get event history, optionally filtered by type"""
        history = self._event_history
        
        if event_type:
            history = [e for e in history if e.metadata.event_type == event_type]
        
        return history[-limit:] if limit > 0 else history
    
    def get_subscriber_count(self, event_type: EventType) -> int:
        """Get the number of subscribers for an event type"""
        return len(self._subscribers.get(event_type, []))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics"""
        return {
            "is_running": self._is_running,
            "queue_size": self._event_queue.qsize(),
            "total_events_processed": len(self._event_history),
            "subscriber_counts": {
                event_type.value: len(handlers)
                for event_type, handlers in self._subscribers.items()
            },
            "middleware_count": len(self._middleware)
        }

# Global event bus instance
event_bus = EventBus()

# Utility functions for creating events
def create_event(
    event_type: EventType,
    payload: Dict[str, Any],
    correlation_id: Optional[str] = None,
    user_id: Optional[str] = None,
    organization_id: Optional[str] = None,
    source_service: str = ""
) -> BaseEvent:
    """Create a new event with the given parameters"""
    metadata = EventMetadata(
        event_id=str(uuid4()),
        event_type=event_type,
        timestamp=datetime.utcnow(),
        correlation_id=correlation_id or str(uuid4()),
        user_id=user_id,
        organization_id=organization_id,
        source_service=source_service
    )
    
    return BaseEvent(metadata=metadata, payload=payload)

async def publish_event(
    event_type: EventType,
    payload: Dict[str, Any],
    correlation_id: Optional[str] = None,
    user_id: Optional[str] = None,
    organization_id: Optional[str] = None,
    source_service: str = ""
) -> None:
    """Create and publish an event"""
    event = create_event(
        event_type=event_type,
        payload=payload,
        correlation_id=correlation_id,
        user_id=user_id,
        organization_id=organization_id,
        source_service=source_service
    )
    
    await event_bus.publish(event)
    return event.metadata.event_id

# Event handler decorator
def event_handler(event_type: EventType):
    """Decorator to register an event handler"""
    def decorator(cls: Type[EventHandler]) -> Type[EventHandler]:
        event_bus.subscribe(event_type, cls())
        return cls
    return decorator

# Middleware decorator
def event_middleware(func: Callable):
    """Decorator to register event middleware"""
    event_bus.add_middleware(func)
    return func
