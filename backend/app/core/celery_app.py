"""
Celery Configuration for Async Task Processing
Handles background tasks, trade processing, and performance optimization
"""

from celery import Celery
import os
from kombu import Queue

# Redis configuration for Celery broker
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "quantaenergi",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "app.tasks.trade_processing",
        "app.tasks.risk_calculation",
        "app.tasks.market_data",
        "app.tasks.notifications"
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task routing
    task_routes={
        "app.tasks.trade_processing.*": {"queue": "trade_processing"},
        "app.tasks.risk_calculation.*": {"queue": "risk_calculation"},
        "app.tasks.market_data.*": {"queue": "market_data"},
        "app.tasks.notifications.*": {"queue": "notifications"},
    },
    
    # Queue configuration
    task_default_queue="default",
    task_queues=(
        Queue("default", routing_key="default"),
        Queue("trade_processing", routing_key="trade_processing"),
        Queue("risk_calculation", routing_key="risk_calculation"),
        Queue("market_data", routing_key="market_data"),
        Queue("notifications", routing_key="notifications"),
    ),
    
    # Task execution
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Performance settings
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    result_persistent=True,
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # Error handling
    task_reject_on_worker_lost=True,
    task_ignore_result=False,
)

# Task time limits
celery_app.conf.task_soft_time_limit = 300  # 5 minutes
celery_app.conf.task_time_limit = 600  # 10 minutes

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "market-data-update": {
        "task": "app.tasks.market_data.update_market_data",
        "schedule": 30.0,  # Every 30 seconds
    },
    "risk-calculation": {
        "task": "app.tasks.risk_calculation.calculate_portfolio_risk",
        "schedule": 60.0,  # Every minute
    },
    "cleanup-expired-tokens": {
        "task": "app.tasks.auth.cleanup_expired_tokens",
        "schedule": 3600.0,  # Every hour
    },
    "generate-daily-reports": {
        "task": "app.tasks.reporting.generate_daily_reports",
        "schedule": 86400.0,  # Daily at midnight
    },
}

# Task priority levels
celery_app.conf.task_default_priority = 5
celery_app.conf.task_queue_max_priority = 10

# Worker configuration
celery_app.conf.worker_hijack_root_logger = False
celery_app.conf.worker_log_color = False

# Security
celery_app.conf.worker_direct = True
celery_app.conf.broker_connection_retry_on_startup = True

# Health check endpoint
@celery_app.task(bind=True)
def health_check(self):
    """Health check task for monitoring"""
    return {
        "status": "healthy",
        "worker": self.request.hostname,
        "task_id": self.request.id,
        "timestamp": self.request.utcnow().isoformat()
    }

# Performance monitoring
@celery_app.task(bind=True)
def performance_metrics(self):
    """Collect performance metrics"""
    from app.core.monitoring import collect_metrics
    
    try:
        metrics = collect_metrics()
        return {
            "status": "success",
            "metrics": metrics,
            "timestamp": self.request.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": self.request.utcnow().isoformat()
        }

# Trade processing task
@celery_app.task(bind=True, queue="trade_processing")
def process_trade_async(self, trade_data):
    """Process trade asynchronously"""
    from app.services.enhanced_trade_lifecycle import EnhancedTradeLifecycleService
    
    try:
        service = EnhancedTradeLifecycleService()
        result = service.process_trade(trade_data)
        
        return {
            "status": "success",
            "trade_id": result.get("trade_id"),
            "processing_time": self.request.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": self.request.utcnow().isoformat()
        }

# Risk calculation task
@celery_app.task(bind=True, queue="risk_calculation")
def calculate_risk_async(self, portfolio_data):
    """Calculate portfolio risk asynchronously"""
    from app.services.advanced_risk_analytics import AdvancedRiskAnalytics
    
    try:
        analytics = AdvancedRiskAnalytics()
        risk_metrics = analytics.calculate_portfolio_risk(portfolio_data)
        
        return {
            "status": "success",
            "risk_metrics": risk_metrics,
            "timestamp": self.request.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": self.request.utcnow().isoformat()
        }

# Market data update task
@celery_app.task(bind=True, queue="market_data")
def update_market_data(self):
    """Update market data asynchronously"""
    from app.services.market_data_integration import MarketDataService
    
    try:
        service = MarketDataService()
        updated_data = service.fetch_and_update_market_data()
        
        return {
            "status": "success",
            "updated_symbols": len(updated_data),
            "timestamp": self.request.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": self.request.utcnow().isoformat()
        }

# Notification task
@celery_app.task(bind=True, queue="notifications")
def send_notification_async(self, notification_data):
    """Send notification asynchronously"""
    from app.services.notification_service import NotificationService
    
    try:
        service = NotificationService()
        result = service.send_notification(notification_data)
        
        return {
            "status": "success",
            "notification_id": result.get("notification_id"),
            "timestamp": self.request.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": self.request.utcnow().isoformat()
        }

# Export Celery app for use in other modules
__all__ = ["celery_app"]
