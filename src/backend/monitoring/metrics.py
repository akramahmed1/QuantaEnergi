"""
Custom Metrics for QuantaEnergi Application
Provides application-specific metrics for monitoring and auto-scaling
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone
import asyncio
import time
from collections import defaultdict, deque
from dataclasses import dataclass

import structlog
from prometheus_client import Counter, Histogram, Gauge, Summary, Info, start_http_server
from prometheus_client.core import CollectorRegistry

logger = structlog.get_logger(__name__)


@dataclass
class MetricSnapshot:
    """Snapshot of metrics at a point in time"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    active_connections: int
    requests_per_second: float
    response_time_p95: float
    error_rate: float
    trade_volume: float
    risk_calculations: int


class QuantaEnergiMetrics:
    """Custom metrics collector for QuantaEnergi application"""
    
    def __init__(self, registry: Optional[CollectorRegistry] = None):
        """
        Initialize metrics collector
        
        Args:
            registry: Prometheus registry (optional)
        """
        self.registry = registry or CollectorRegistry()
        self._initialize_metrics()
        self._initialize_custom_metrics()
        
        # Metrics history for calculations
        self.request_times = deque(maxlen=1000)
        self.error_counts = defaultdict(int)
        self.trade_volumes = deque(maxlen=100)
        
        logger.info("QuantaEnergi metrics initialized")
    
    def _initialize_metrics(self):
        """Initialize standard Prometheus metrics"""
        
        # HTTP Request Metrics
        self.http_requests_total = Counter(
            'quantaenergi_http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status_code', 'tenant_id'],
            registry=self.registry
        )
        
        self.http_request_duration = Histogram(
            'quantaenergi_http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint', 'tenant_id'],
            registry=self.registry,
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        )
        
        self.http_requests_in_flight = Gauge(
            'quantaenergi_http_requests_in_flight',
            'Current number of HTTP requests being processed',
            registry=self.registry
        )
        
        # Trading Metrics
        self.trades_total = Counter(
            'quantaenergi_trades_total',
            'Total number of trades',
            ['trade_type', 'commodity', 'region', 'tenant_id'],
            registry=self.registry
        )
        
        self.trade_volume = Counter(
            'quantaenergi_trade_volume_total',
            'Total trade volume',
            ['commodity', 'currency', 'tenant_id'],
            registry=self.registry
        )
        
        self.trade_value = Summary(
            'quantaenergi_trade_value',
            'Trade value distribution',
            ['commodity', 'tenant_id'],
            registry=self.registry
        )
        
        # Risk Analytics Metrics
        self.risk_calculations_total = Counter(
            'quantaenergi_risk_calculations_total',
            'Total risk calculations performed',
            ['calculation_type', 'tenant_id'],
            registry=self.registry
        )
        
        self.risk_calculation_duration = Histogram(
            'quantaenergi_risk_calculation_duration_seconds',
            'Risk calculation duration in seconds',
            ['calculation_type', 'tenant_id'],
            registry=self.registry,
            buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 25.0, 50.0, 100.0]
        )
        
        # Portfolio Metrics
        self.portfolio_value = Gauge(
            'quantaenergi_portfolio_value',
            'Current portfolio value',
            ['portfolio_id', 'tenant_id'],
            registry=self.registry
        )
        
        self.position_count = Gauge(
            'quantaenergi_position_count',
            'Number of positions in portfolio',
            ['portfolio_id', 'tenant_id'],
            registry=self.registry
        )
        
        # System Metrics
        self.active_users = Gauge(
            'quantaenergi_active_users',
            'Number of active users',
            ['tenant_id'],
            registry=self.registry
        )
        
        self.database_connections = Gauge(
            'quantaenergi_database_connections',
            'Number of active database connections',
            ['database', 'tenant_id'],
            registry=self.registry
        )
        
        self.cache_hit_ratio = Gauge(
            'quantaenergi_cache_hit_ratio',
            'Cache hit ratio',
            ['cache_type', 'tenant_id'],
            registry=self.registry
        )
        
        # Compliance Metrics
        self.compliance_violations = Counter(
            'quantaenergi_compliance_violations_total',
            'Total compliance violations',
            ['rule_id', 'region', 'severity', 'tenant_id'],
            registry=self.registry
        )
        
        self.compliance_reports_generated = Counter(
            'quantaenergi_compliance_reports_generated_total',
            'Total compliance reports generated',
            ['report_type', 'region', 'tenant_id'],
            registry=self.registry
        )
        
        # WebSocket Metrics
        self.websocket_connections = Gauge(
            'quantaenergi_websocket_connections',
            'Number of active WebSocket connections',
            ['tenant_id'],
            registry=self.registry
        )
        
        self.websocket_messages_sent = Counter(
            'quantaenergi_websocket_messages_sent_total',
            'Total WebSocket messages sent',
            ['message_type', 'tenant_id'],
            registry=self.registry
        )
    
    def _initialize_custom_metrics(self):
        """Initialize custom application metrics"""
        
        # Custom Trading Signals
        self.trading_signals_generated = Counter(
            'quantaenergi_trading_signals_generated_total',
            'Total trading signals generated',
            ['signal_type', 'confidence_level', 'tenant_id'],
            registry=self.registry
        )
        
        # ESG Metrics
        self.esg_score = Gauge(
            'quantaenergi_esg_score',
            'Current ESG score',
            ['metric_type', 'tenant_id'],
            registry=self.registry
        )
        
        # Market Data Metrics
        self.market_data_updates = Counter(
            'quantaenergi_market_data_updates_total',
            'Total market data updates received',
            ['data_source', 'commodity', 'tenant_id'],
            registry=self.registry
        )
        
        # Authentication Metrics
        self.authentication_attempts = Counter(
            'quantaenergi_authentication_attempts_total',
            'Total authentication attempts',
            ['provider', 'result', 'tenant_id'],
            registry=self.registry
        )
        
        # Multi-tenancy Metrics
        self.tenant_operations = Counter(
            'quantaenergi_tenant_operations_total',
            'Total tenant operations',
            ['operation_type', 'tenant_id'],
            registry=self.registry
        )
    
    def record_http_request(self, method: str, endpoint: str, status_code: int, 
                          duration: float, tenant_id: str = "system"):
        """
        Record HTTP request metrics
        
        Args:
            method: HTTP method
            endpoint: Request endpoint
            status_code: Response status code
            duration: Request duration in seconds
            tenant_id: Tenant identifier
        """
        self.http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code),
            tenant_id=tenant_id
        ).inc()
        
        self.http_request_duration.labels(
            method=method,
            endpoint=endpoint,
            tenant_id=tenant_id
        ).observe(duration)
        
        # Track request times for P95 calculation
        self.request_times.append(duration)
        
        # Track errors
        if status_code >= 400:
            self.error_counts[tenant_id] += 1
    
    def record_trade(self, trade_type: str, commodity: str, volume: float, 
                    value: float, region: str, tenant_id: str = "system"):
        """
        Record trade metrics
        
        Args:
            trade_type: Type of trade
            commodity: Commodity type
            volume: Trade volume
            value: Trade value
            region: Trading region
            tenant_id: Tenant identifier
        """
        self.trades_total.labels(
            trade_type=trade_type,
            commodity=commodity,
            region=region,
            tenant_id=tenant_id
        ).inc()
        
        self.trade_volume.labels(
            commodity=commodity,
            currency="USD",  # Default currency
            tenant_id=tenant_id
        ).inc(volume)
        
        self.trade_value.labels(
            commodity=commodity,
            tenant_id=tenant_id
        ).observe(value)
        
        # Track trade volumes for metrics
        self.trade_volumes.append(volume)
    
    def record_risk_calculation(self, calculation_type: str, duration: float, 
                              tenant_id: str = "system"):
        """
        Record risk calculation metrics
        
        Args:
            calculation_type: Type of risk calculation
            duration: Calculation duration in seconds
            tenant_id: Tenant identifier
        """
        self.risk_calculations_total.labels(
            calculation_type=calculation_type,
            tenant_id=tenant_id
        ).inc()
        
        self.risk_calculation_duration.labels(
            calculation_type=calculation_type,
            tenant_id=tenant_id
        ).observe(duration)
    
    def update_portfolio_metrics(self, portfolio_id: str, value: float, 
                               position_count: int, tenant_id: str = "system"):
        """
        Update portfolio metrics
        
        Args:
            portfolio_id: Portfolio identifier
            value: Portfolio value
            position_count: Number of positions
            tenant_id: Tenant identifier
        """
        self.portfolio_value.labels(
            portfolio_id=portfolio_id,
            tenant_id=tenant_id
        ).set(value)
        
        self.position_count.labels(
            portfolio_id=portfolio_id,
            tenant_id=tenant_id
        ).set(position_count)
    
    def update_system_metrics(self, active_users: int, db_connections: int, 
                            cache_hit_ratio: float, tenant_id: str = "system"):
        """
        Update system metrics
        
        Args:
            active_users: Number of active users
            db_connections: Number of database connections
            cache_hit_ratio: Cache hit ratio
            tenant_id: Tenant identifier
        """
        self.active_users.labels(tenant_id=tenant_id).set(active_users)
        self.database_connections.labels(
            database="postgresql",
            tenant_id=tenant_id
        ).set(db_connections)
        self.cache_hit_ratio.labels(
            cache_type="redis",
            tenant_id=tenant_id
        ).set(cache_hit_ratio)
    
    def record_compliance_violation(self, rule_id: str, region: str, 
                                  severity: str, tenant_id: str = "system"):
        """
        Record compliance violation
        
        Args:
            rule_id: Compliance rule identifier
            region: Regulatory region
            severity: Violation severity
            tenant_id: Tenant identifier
        """
        self.compliance_violations.labels(
            rule_id=rule_id,
            region=region,
            severity=severity,
            tenant_id=tenant_id
        ).inc()
    
    def record_websocket_connection(self, tenant_id: str = "system"):
        """Record WebSocket connection"""
        self.websocket_connections.labels(tenant_id=tenant_id).inc()
    
    def record_websocket_disconnection(self, tenant_id: str = "system"):
        """Record WebSocket disconnection"""
        self.websocket_connections.labels(tenant_id=tenant_id).dec()
    
    def record_websocket_message(self, message_type: str, tenant_id: str = "system"):
        """Record WebSocket message sent"""
        self.websocket_messages_sent.labels(
            message_type=message_type,
            tenant_id=tenant_id
        ).inc()
    
    def get_metrics_snapshot(self, tenant_id: str = "system") -> MetricSnapshot:
        """
        Get current metrics snapshot
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            Metrics snapshot
        """
        # Calculate derived metrics
        requests_per_second = self._calculate_requests_per_second()
        response_time_p95 = self._calculate_p95_response_time()
        error_rate = self._calculate_error_rate(tenant_id)
        trade_volume = self._calculate_total_trade_volume()
        risk_calculations = self._get_risk_calculation_count(tenant_id)
        
        # Get system metrics (these would be populated by system monitoring)
        cpu_usage = self._get_cpu_usage()
        memory_usage = self._get_memory_usage()
        active_connections = self._get_active_connections(tenant_id)
        
        return MetricSnapshot(
            timestamp=datetime.now(timezone.utc),
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            active_connections=active_connections,
            requests_per_second=requests_per_second,
            response_time_p95=response_time_p95,
            error_rate=error_rate,
            trade_volume=trade_volume,
            risk_calculations=risk_calculations
        )
    
    def _calculate_requests_per_second(self) -> float:
        """Calculate requests per second from recent data"""
        if not self.request_times:
            return 0.0
        
        # Simple calculation based on recent requests
        recent_requests = list(self.request_times)[-60:]  # Last 60 requests
        return len(recent_requests) / 60.0  # Assuming 1-minute window
    
    def _calculate_p95_response_time(self) -> float:
        """Calculate 95th percentile response time"""
        if not self.request_times:
            return 0.0
        
        sorted_times = sorted(self.request_times)
        p95_index = int(len(sorted_times) * 0.95)
        return sorted_times[p95_index] if p95_index < len(sorted_times) else 0.0
    
    def _calculate_error_rate(self, tenant_id: str) -> float:
        """Calculate error rate for tenant"""
        total_requests = sum(
            counter._value.get((tenant_id,), {}).get('total', 0)
            for counter in [self.http_requests_total]
        )
        
        if total_requests == 0:
            return 0.0
        
        error_count = self.error_counts.get(tenant_id, 0)
        return (error_count / total_requests) * 100.0
    
    def _calculate_total_trade_volume(self) -> float:
        """Calculate total trade volume"""
        return sum(self.trade_volumes) if self.trade_volumes else 0.0
    
    def _get_risk_calculation_count(self, tenant_id: str) -> int:
        """Get risk calculation count for tenant"""
        # This would be implemented with actual metric retrieval
        return 0
    
    def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        # This would integrate with system monitoring
        return 0.0
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage percentage"""
        # This would integrate with system monitoring
        return 0.0
    
    def _get_active_connections(self, tenant_id: str) -> int:
        """Get active connections for tenant"""
        # This would be implemented with actual connection tracking
        return 0


# Global metrics instance
_metrics: Optional[QuantaEnergiMetrics] = None


def get_metrics() -> QuantaEnergiMetrics:
    """Get the global metrics instance"""
    global _metrics
    
    if _metrics is None:
        _metrics = QuantaEnergiMetrics()
    
    return _metrics


def start_metrics_server(port: int = 8001):
    """
    Start Prometheus metrics server
    
    Args:
        port: Port to serve metrics on
    """
    start_http_server(port, registry=get_metrics().registry)
    logger.info("Metrics server started", port=port)


# Metrics middleware for FastAPI
class MetricsMiddleware:
    """Middleware to automatically collect HTTP metrics"""
    
    def __init__(self, metrics: QuantaEnergiMetrics):
        self.metrics = metrics
    
    async def __call__(self, request, call_next):
        """Process request and collect metrics"""
        start_time = time.time()
        
        # Extract tenant ID from request
        tenant_id = request.headers.get("X-Tenant-ID", "system")
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Record metrics
        self.metrics.record_http_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            duration=duration,
            tenant_id=tenant_id
        )
        
        return response
