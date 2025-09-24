"""
Prometheus monitoring configuration for QuantaEnergi
Provides metrics collection and monitoring setup
"""

from prometheus_client import Counter, Histogram, Gauge, Summary, Info, start_http_server
import time
import structlog
from functools import wraps
from typing import Callable, Any

logger = structlog.get_logger(__name__)

# Request metrics
REQUEST_COUNT = Counter(
    'quantaenergi_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'quantaenergi_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

REQUEST_SIZE = Histogram(
    'quantaenergi_request_size_bytes',
    'Request size in bytes',
    ['method', 'endpoint']
)

RESPONSE_SIZE = Histogram(
    'quantaenergi_response_size_bytes',
    'Response size in bytes',
    ['method', 'endpoint']
)

# Business metrics
TRADES_CREATED = Counter(
    'quantaenergi_trades_created_total',
    'Total number of trades created',
    ['commodity', 'trade_type']
)

TRADES_VALIDATED = Counter(
    'quantaenergi_trades_validated_total',
    'Total number of trades validated',
    ['commodity', 'trade_type']
)

TRADES_SETTLED = Counter(
    'quantaenergi_trades_settled_total',
    'Total number of trades settled',
    ['commodity', 'trade_type']
)

FORECASTS_GENERATED = Counter(
    'quantaenergi_forecasts_generated_total',
    'Total number of forecasts generated',
    ['commodity', 'periods']
)

PORTFOLIO_OPTIMIZATIONS = Counter(
    'quantaenergi_portfolio_optimizations_total',
    'Total number of portfolio optimizations',
    ['method', 'num_assets']
)

CARBON_TRADES_CREATED = Counter(
    'quantaenergi_carbon_trades_created_total',
    'Total number of carbon trades created',
    ['status']
)

SHARIA_COMPLIANCE_CHECKS = Counter(
    'quantaenergi_sharia_compliance_checks_total',
    'Total number of Sharia compliance checks',
    ['status', 'commodity']
)

COMPLIANCE_REPORTS_GENERATED = Counter(
    'quantaenergi_compliance_reports_generated_total',
    'Total number of compliance reports generated',
    ['report_type', 'status']
)

BILLING_CUSTOMERS_CREATED = Counter(
    'quantaenergi_billing_customers_created_total',
    'Total number of billing customers created'
)

SUBSCRIPTIONS_CREATED = Counter(
    'quantaenergi_subscriptions_created_total',
    'Total number of subscriptions created',
    ['plan_tier', 'status']
)

# System metrics
ACTIVE_CONNECTIONS = Gauge(
    'quantaenergi_active_connections',
    'Number of active connections'
)

DATABASE_CONNECTIONS = Gauge(
    'quantaenergi_database_connections',
    'Number of database connections',
    ['state']
)

MEMORY_USAGE = Gauge(
    'quantaenergi_memory_usage_bytes',
    'Memory usage in bytes',
    ['type']
)

CPU_USAGE = Gauge(
    'quantaenergi_cpu_usage_percent',
    'CPU usage percentage'
)

# Error metrics
ERRORS_TOTAL = Counter(
    'quantaenergi_errors_total',
    'Total number of errors',
    ['error_type', 'endpoint']
)

AUTHENTICATION_FAILURES = Counter(
    'quantaenergi_authentication_failures_total',
    'Total number of authentication failures',
    ['reason']
)

RATE_LIMIT_HITS = Counter(
    'quantaenergi_rate_limit_hits_total',
    'Total number of rate limit hits',
    ['endpoint', 'ip']
)

# Performance metrics
FORECAST_DURATION = Summary(
    'quantaenergi_forecast_duration_seconds',
    'Time spent generating forecasts',
    ['commodity']
)

OPTIMIZATION_DURATION = Summary(
    'quantaenergi_optimization_duration_seconds',
    'Time spent on portfolio optimization',
    ['method']
)

COMPLIANCE_CHECK_DURATION = Summary(
    'quantaenergi_compliance_check_duration_seconds',
    'Time spent on compliance checks',
    ['check_type']
)

# Application info
APP_INFO = Info(
    'quantaenergi_app_info',
    'Application information'
)

class PrometheusMonitoring:
    """Prometheus monitoring service"""
    
    def __init__(self, port: int = 8001):
        self.port = port
        self.server_started = False
        self._setup_app_info()
    
    def _setup_app_info(self):
        """Set up application information"""
        APP_INFO.info({
            'version': '1.0.0',
            'name': 'QuantaEnergi',
            'description': 'AI-Powered Energy Trading Platform',
            'environment': 'production'
        })
    
    def start_server(self):
        """Start Prometheus metrics server"""
        if not self.server_started:
            try:
                start_http_server(self.port)
                self.server_started = True
                logger.info("Prometheus metrics server started", port=self.port)
            except Exception as e:
                logger.error("Failed to start Prometheus server", error=str(e))
                raise
    
    def record_request(self, method: str, endpoint: str, status_code: int, 
                      duration: float, request_size: int = 0, response_size: int = 0):
        """Record request metrics"""
        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).inc()
        
        REQUEST_DURATION.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
        if request_size > 0:
            REQUEST_SIZE.labels(
                method=method,
                endpoint=endpoint
            ).observe(request_size)
        
        if response_size > 0:
            RESPONSE_SIZE.labels(
                method=method,
                endpoint=endpoint
            ).observe(response_size)
    
    def record_trade_created(self, commodity: str, trade_type: str):
        """Record trade creation"""
        TRADES_CREATED.labels(
            commodity=commodity,
            trade_type=trade_type
        ).inc()
    
    def record_trade_validated(self, commodity: str, trade_type: str):
        """Record trade validation"""
        TRADES_VALIDATED.labels(
            commodity=commodity,
            trade_type=trade_type
        ).inc()
    
    def record_trade_settled(self, commodity: str, trade_type: str):
        """Record trade settlement"""
        TRADES_SETTLED.labels(
            commodity=commodity,
            trade_type=trade_type
        ).inc()
    
    def record_forecast_generated(self, commodity: str, periods: int):
        """Record forecast generation"""
        FORECASTS_GENERATED.labels(
            commodity=commodity,
            periods=str(periods)
        ).inc()
    
    def record_portfolio_optimization(self, method: str, num_assets: int):
        """Record portfolio optimization"""
        PORTFOLIO_OPTIMIZATIONS.labels(
            method=method,
            num_assets=str(num_assets)
        ).inc()
    
    def record_carbon_trade_created(self, status: str):
        """Record carbon trade creation"""
        CARBON_TRADES_CREATED.labels(status=status).inc()
    
    def record_sharia_compliance_check(self, status: str, commodity: str):
        """Record Sharia compliance check"""
        SHARIA_COMPLIANCE_CHECKS.labels(
            status=status,
            commodity=commodity
        ).inc()
    
    def record_compliance_report_generated(self, report_type: str, status: str):
        """Record compliance report generation"""
        COMPLIANCE_REPORTS_GENERATED.labels(
            report_type=report_type,
            status=status
        ).inc()
    
    def record_billing_customer_created(self):
        """Record billing customer creation"""
        BILLING_CUSTOMERS_CREATED.inc()
    
    def record_subscription_created(self, plan_tier: str, status: str):
        """Record subscription creation"""
        SUBSCRIPTIONS_CREATED.labels(
            plan_tier=plan_tier,
            status=status
        ).inc()
    
    def record_error(self, error_type: str, endpoint: str):
        """Record error occurrence"""
        ERRORS_TOTAL.labels(
            error_type=error_type,
            endpoint=endpoint
        ).inc()
    
    def record_authentication_failure(self, reason: str):
        """Record authentication failure"""
        AUTHENTICATION_FAILURES.labels(reason=reason).inc()
    
    def record_rate_limit_hit(self, endpoint: str, ip: str):
        """Record rate limit hit"""
        RATE_LIMIT_HITS.labels(endpoint=endpoint, ip=ip).inc()
    
    def record_forecast_duration(self, commodity: str, duration: float):
        """Record forecast generation duration"""
        FORECAST_DURATION.labels(commodity=commodity).observe(duration)
    
    def record_optimization_duration(self, method: str, duration: float):
        """Record optimization duration"""
        OPTIMIZATION_DURATION.labels(method=method).observe(duration)
    
    def record_compliance_check_duration(self, check_type: str, duration: float):
        """Record compliance check duration"""
        COMPLIANCE_CHECK_DURATION.labels(check_type=check_type).observe(duration)
    
    def update_active_connections(self, count: int):
        """Update active connections count"""
        ACTIVE_CONNECTIONS.set(count)
    
    def update_database_connections(self, active: int, idle: int):
        """Update database connections count"""
        DATABASE_CONNECTIONS.labels(state='active').set(active)
        DATABASE_CONNECTIONS.labels(state='idle').set(idle)
    
    def update_memory_usage(self, used: int, available: int):
        """Update memory usage"""
        MEMORY_USAGE.labels(type='used').set(used)
        MEMORY_USAGE.labels(type='available').set(available)
    
    def update_cpu_usage(self, percent: float):
        """Update CPU usage"""
        CPU_USAGE.set(percent)

def monitor_request(func: Callable) -> Callable:
    """Decorator to monitor request metrics"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        method = getattr(func, '__name__', 'unknown')
        endpoint = getattr(func, '__name__', 'unknown')
        
        try:
            result = await func(*args, **kwargs)
            status_code = 200
            return result
        except Exception as e:
            status_code = 500
            monitoring.record_error(type(e).__name__, endpoint)
            raise
        finally:
            duration = time.time() - start_time
            monitoring.record_request(method, endpoint, status_code, duration)
    
    return wrapper

def monitor_performance(metric_name: str, labels: dict = None):
    """Decorator to monitor performance metrics"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                if metric_name == 'forecast':
                    commodity = labels.get('commodity', 'unknown') if labels else 'unknown'
                    monitoring.record_forecast_duration(commodity, duration)
                elif metric_name == 'optimization':
                    method = labels.get('method', 'unknown') if labels else 'unknown'
                    monitoring.record_optimization_duration(method, duration)
                elif metric_name == 'compliance':
                    check_type = labels.get('check_type', 'unknown') if labels else 'unknown'
                    monitoring.record_compliance_check_duration(check_type, duration)
        
        return wrapper
    return decorator

# Global monitoring instance
monitoring = PrometheusMonitoring()

# Start monitoring server
monitoring.start_server()
