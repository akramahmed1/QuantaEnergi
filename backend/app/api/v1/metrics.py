"""
Prometheus Metrics Endpoint for Production Monitoring
QuantaEnergi Production Readiness
"""

from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
from typing import Dict, Any
import time
import psutil
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/metrics", tags=["Metrics"])

class MetricsCollector:
    """Metrics collector for Prometheus monitoring"""
    
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.trading_volume = 0.0
        self.active_users = 0
        self.last_metrics_update = datetime.now()
    
    def increment_request_count(self):
        """Increment request counter"""
        self.request_count += 1
    
    def increment_error_count(self):
        """Increment error counter"""
        self.error_count += 1
    
    def update_trading_volume(self, volume: float):
        """Update trading volume metric"""
        self.trading_volume += volume
    
    def update_active_users(self, users: int):
        """Update active users metric"""
        self.active_users = users
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Collect system metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_usage_percent": cpu_percent,
                "memory_usage_percent": memory.percent,
                "memory_available_bytes": memory.available,
                "memory_total_bytes": memory.total,
                "disk_usage_percent": disk.percent,
                "disk_free_bytes": disk.free,
                "disk_total_bytes": disk.total
            }
        except Exception as e:
            logger.error(f"System metrics collection failed: {e}")
            return {}
    
    def get_application_metrics(self) -> Dict[str, Any]:
        """Collect application-specific metrics"""
        try:
            uptime = time.time() - self.start_time
            
            return {
                "uptime_seconds": uptime,
                "request_count_total": self.request_count,
                "error_count_total": self.error_count,
                "trading_volume_total": self.trading_volume,
                "active_users_current": self.active_users,
                "last_metrics_update_timestamp": self.last_metrics_update.timestamp()
            }
        except Exception as e:
            logger.error(f"Application metrics collection failed: {e}")
            return {}
    
    def get_service_metrics(self) -> Dict[str, Any]:
        """Collect service health metrics"""
        try:
            # Mock service metrics - in production these would be real
            # TODO: Replace with real service metrics collection
            services = {
                "agi_trading": {"status": 1, "response_time_ms": 150, "requests_per_second": 100},
                "quantum_trading": {"status": 1, "response_time_ms": 200, "requests_per_second": 50},
                "digital_twin": {"status": 1, "response_time_ms": 100, "requests_per_second": 200},
                "autonomous_trading": {"status": 1, "response_time_ms": 180, "requests_per_second": 75},
                "decentralized_trading": {"status": 1, "response_time_ms": 300, "requests_per_second": 25},
                "carbon_trading": {"status": 1, "response_time_ms": 120, "requests_per_second": 150},
                "market_intelligence": {"status": 1, "response_time_ms": 90, "requests_per_second": 300}
            }
            
            return services
        except Exception as e:
            logger.error(f"Service metrics collection failed: {e}")
            return {}
    
    def get_business_metrics(self) -> Dict[str, Any]:
        """Collect business metrics"""
        try:
            # Mock business metrics - in production these would be real
            # TODO: Replace with real business metrics collection
            return {
                "total_trades": 1250,
                "total_volume_usd": 15000000.0,
                "active_portfolios": 45,
                "compliance_score": 98.5,
                "user_satisfaction_score": 4.7,
                "system_uptime_percentage": 99.9
            }
        except Exception as e:
            logger.error(f"Business metrics collection failed: {e}")
            return {}

# Initialize metrics collector
metrics_collector = MetricsCollector()

@router.get("/", response_class=PlainTextResponse)
async def prometheus_metrics():
    """Prometheus metrics endpoint"""
    try:
        # Update last metrics update timestamp
        metrics_collector.last_metrics_update = datetime.now()
        
        # Collect all metrics
        system_metrics = metrics_collector.get_system_metrics()
        application_metrics = metrics_collector.get_application_metrics()
        service_metrics = metrics_collector.get_service_metrics()
        business_metrics = metrics_collector.get_business_metrics()
        
        # Format metrics in Prometheus format
        prometheus_metrics = []
        
        # System metrics
        prometheus_metrics.append("# HELP quantaenergi_cpu_usage_percent CPU usage percentage")
        prometheus_metrics.append("# TYPE quantaenergi_cpu_usage_percent gauge")
        prometheus_metrics.append(f"quantaenergi_cpu_usage_percent {system_metrics.get('cpu_usage_percent', 0)}")
        
        prometheus_metrics.append("# HELP quantaenergi_memory_usage_percent Memory usage percentage")
        prometheus_metrics.append("# TYPE quantaenergi_memory_usage_percent gauge")
        prometheus_metrics.append(f"quantaenergi_memory_usage_percent {system_metrics.get('memory_usage_percent', 0)}")
        
        prometheus_metrics.append("# HELP quantaenergi_memory_available_bytes Available memory in bytes")
        prometheus_metrics.append("# TYPE quantaenergi_memory_available_bytes gauge")
        prometheus_metrics.append(f"quantaenergi_memory_available_bytes {system_metrics.get('memory_available_bytes', 0)}")
        
        prometheus_metrics.append("# HELP quantaenergi_disk_usage_percent Disk usage percentage")
        prometheus_metrics.append("# TYPE quantaenergi_disk_usage_percent gauge")
        prometheus_metrics.append(f"quantaenergi_disk_usage_percent {system_metrics.get('disk_usage_percent', 0)}")
        
        # Application metrics
        prometheus_metrics.append("# HELP quantaenergi_uptime_seconds Application uptime in seconds")
        prometheus_metrics.append("# TYPE quantaenergi_uptime_seconds counter")
        prometheus_metrics.append(f"quantaenergi_uptime_seconds {application_metrics.get('uptime_seconds', 0)}")
        
        prometheus_metrics.append("# HELP quantaenergi_request_count_total Total request count")
        prometheus_metrics.append("# TYPE quantaenergi_request_count_total counter")
        prometheus_metrics.append(f"quantaenergi_request_count_total {application_metrics.get('request_count_total', 0)}")
        
        prometheus_metrics.append("# HELP quantaenergi_error_count_total Total error count")
        prometheus_metrics.append("# TYPE quantaenergi_error_count_total counter")
        prometheus_metrics.append(f"quantaenergi_error_count_total {application_metrics.get('error_count_total', 0)}")
        
        prometheus_metrics.append("# HELP quantaenergi_trading_volume_total Total trading volume in USD")
        prometheus_metrics.append("# TYPE quantaenergi_trading_volume_total counter")
        prometheus_metrics.append(f"quantaenergi_trading_volume_total {application_metrics.get('trading_volume_total', 0)}")
        
        prometheus_metrics.append("# HELP quantaenergi_active_users_current Current active users")
        prometheus_metrics.append("# TYPE quantaenergi_active_users_current gauge")
        prometheus_metrics.append(f"quantaenergi_active_users_current {application_metrics.get('active_users_current', 0)}")
        
        # Service metrics
        for service_name, service_data in service_metrics.items():
            prometheus_metrics.append(f"# HELP quantaenergi_service_status_{service_name} Service status (1=healthy, 0=unhealthy)")
            prometheus_metrics.append(f"# TYPE quantaenergi_service_status_{service_name} gauge")
            prometheus_metrics.append(f"quantaenergi_service_status_{service_name} {service_data.get('status', 0)}")
            
            prometheus_metrics.append(f"# HELP quantaenergi_service_response_time_ms_{service_name} Service response time in milliseconds")
            prometheus_metrics.append(f"# TYPE quantaenergi_service_response_time_ms_{service_name} gauge")
            prometheus_metrics.append(f"quantaenergi_service_response_time_ms_{service_name} {service_data.get('response_time_ms', 0)}")
            
            prometheus_metrics.append(f"# HELP quantaenergi_service_requests_per_second_{service_name} Service requests per second")
            prometheus_metrics.append(f"# TYPE quantaenergi_service_requests_per_second_{service_name} gauge")
            prometheus_metrics.append(f"quantaenergi_service_requests_per_second_{service_name} {service_data.get('requests_per_second', 0)}")
        
        # Business metrics
        prometheus_metrics.append("# HELP quantaenergi_total_trades Total number of trades")
        prometheus_metrics.append("# TYPE quantaenergi_total_trades counter")
        prometheus_metrics.append(f"quantaenergi_total_trades {business_metrics.get('total_trades', 0)}")
        
        prometheus_metrics.append("# HELP quantaenergi_total_volume_usd Total trading volume in USD")
        prometheus_metrics.append("# TYPE quantaenergi_total_volume_usd counter")
        prometheus_metrics.append(f"quantaenergi_total_volume_usd {business_metrics.get('total_volume_usd', 0)}")
        
        prometheus_metrics.append("# HELP quantaenergi_active_portfolios Current active portfolios")
        prometheus_metrics.append("# TYPE quantaenergi_active_portfolios gauge")
        prometheus_metrics.append(f"quantaenergi_active_portfolios {business_metrics.get('active_portfolios', 0)}")
        
        prometheus_metrics.append("# HELP quantaenergi_compliance_score Compliance score percentage")
        prometheus_metrics.append("# TYPE quantaenergi_compliance_score gauge")
        prometheus_metrics.append(f"quantaenergi_compliance_score {business_metrics.get('compliance_score', 0)}")
        
        prometheus_metrics.append("# HELP quantaenergi_user_satisfaction_score User satisfaction score (1-5)")
        prometheus_metrics.append("# TYPE quantaenergi_user_satisfaction_score gauge")
        prometheus_metrics.append(f"quantaenergi_user_satisfaction_score {business_metrics.get('user_satisfaction_score', 0)}")
        
        prometheus_metrics.append("# HELP quantaenergi_system_uptime_percentage System uptime percentage")
        prometheus_metrics.append("# TYPE quantaenergi_system_uptime_percentage gauge")
        prometheus_metrics.append(f"quantaenergi_system_uptime_percentage {business_metrics.get('system_uptime_percentage', 0)}")
        
        # Add timestamp
        prometheus_metrics.append(f"# HELP quantaenergi_metrics_timestamp Metrics collection timestamp")
        prometheus_metrics.append(f"# TYPE quantaenergi_metrics_timestamp gauge")
        prometheus_metrics.append(f"quantaenergi_metrics_timestamp {metrics_collector.last_metrics_update.timestamp()}")
        
        return "\n".join(prometheus_metrics)
        
    except Exception as e:
        logger.error(f"Prometheus metrics collection failed: {e}")
        return f"# ERROR: {str(e)}"

@router.get("/summary", response_model=Dict[str, Any])
async def metrics_summary():
    """Metrics summary endpoint for human-readable format"""
    try:
        # Update last metrics update timestamp
        metrics_collector.last_metrics_update = datetime.now()
        
        # Collect all metrics
        system_metrics = metrics_collector.get_system_metrics()
        application_metrics = metrics_collector.get_application_metrics()
        service_metrics = metrics_collector.get_service_metrics()
        business_metrics = metrics_collector.get_business_metrics()
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "system": system_metrics,
                "application": application_metrics,
                "services": service_metrics,
                "business": business_metrics
            },
            "summary": {
                "total_metrics": len(system_metrics) + len(application_metrics) + len(service_metrics) + len(business_metrics),
                "last_update": metrics_collector.last_metrics_update.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Metrics summary collection failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.post("/update")
async def update_metrics(request: Request):
    """Update metrics endpoint for external systems"""
    try:
        # Parse request body
        body = await request.json()
        
        # Update metrics based on request
        if "trading_volume" in body:
            metrics_collector.update_trading_volume(body["trading_volume"])
        
        if "active_users" in body:
            metrics_collector.update_active_users(body["active_users"])
        
        if "error" in body and body["error"]:
            metrics_collector.increment_error_count()
        
        # Always increment request count
        metrics_collector.increment_request_count()
        
        return {
            "status": "success",
            "message": "Metrics updated successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Metrics update failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/health")
async def metrics_health():
    """Metrics health check endpoint"""
    try:
        return {
            "status": "healthy",
            "service": "metrics",
            "timestamp": datetime.now().isoformat(),
            "message": "Metrics service is operational"
        }
    except Exception as e:
        logger.error(f"Metrics health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "metrics",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
