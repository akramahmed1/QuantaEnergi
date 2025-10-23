"""
Celery Configuration for QuantaEnergi
Handles CPU-intensive tasks asynchronously
"""

import os
from celery import Celery
from celery.signals import worker_init, worker_shutdown
import structlog

logger = structlog.get_logger(__name__)

# Celery configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "quantaenergi",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.risk_calculations",
        "app.tasks.market_data_processing",
        "app.tasks.compliance_reports",
        "app.tasks.portfolio_optimization",
        "app.tasks.esg_calculations"
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task routing
    task_routes={
        "app.tasks.risk_calculations.*": {"queue": "risk_calculations"},
        "app.tasks.market_data_processing.*": {"queue": "market_data"},
        "app.tasks.compliance_reports.*": {"queue": "compliance"},
        "app.tasks.portfolio_optimization.*": {"queue": "portfolio"},
        "app.tasks.esg_calculations.*": {"queue": "esg"},
    },
    
    # Worker configuration
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    
    # Result backend configuration
    result_expires=3600,  # 1 hour
    
    # Task execution configuration
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # Retry configuration
    task_default_retry_delay=60,
    task_max_retries=3,
    
    # Concurrency
    worker_concurrency=4,
    worker_pool="prefork",  # Use multiprocessing for CPU-bound tasks
)

# Celery Beat configuration for scheduled tasks
celery_app.conf.beat_schedule = {
    "calculate-daily-var": {
        "task": "app.tasks.risk_calculations.calculate_daily_var",
        "schedule": 60.0 * 60.0 * 24.0,  # Daily
    },
    "process-market-data": {
        "task": "app.tasks.market_data_processing.process_realtime_data",
        "schedule": 30.0,  # Every 30 seconds
    },
    "generate-compliance-reports": {
        "task": "app.tasks.compliance_reports.generate_daily_reports",
        "schedule": 60.0 * 60.0 * 24.0,  # Daily
    },
    "optimize-portfolios": {
        "task": "app.tasks.portfolio_optimization.optimize_all_portfolios",
        "schedule": 60.0 * 60.0 * 6.0,  # Every 6 hours
    },
    "calculate-esg-scores": {
        "task": "app.tasks.esg_calculations.calculate_esg_scores",
        "schedule": 60.0 * 60.0 * 12.0,  # Every 12 hours
    },
}

# Worker initialization
@worker_init.connect
def worker_init_handler(sender=None, **kwargs):
    """Initialize worker"""
    logger.info("Celery worker initialized", worker=sender)


@worker_shutdown.connect
def worker_shutdown_handler(sender=None, **kwargs):
    """Shutdown worker"""
    logger.info("Celery worker shutting down", worker=sender)


def get_celery_app() -> Celery:
    """Get Celery app instance"""
    return celery_app