"""
ETRM/CTRM Integration Engine for QuantaEnergi Enterprise Application
Comprehensive integration layer connecting all trading, risk, and analytics engines
"""
import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from decimal import Decimal
from sqlalchemy.orm import Session
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import all the core engines
from .advanced_trade_engine import AdvancedTradeEngine, Order, OrderType, OrderSide, Execution
from .advanced_risk_engine import AdvancedRiskEngine, RiskLimit, StressScenario, Greeks
from .pricing_models import PricingEngine, MarketData, PricingResult, BlackScholesModel, BinomialModel, MonteCarloModel
from .portfolio_optimizer import PortfolioOptimizer, Asset, OptimizationResult, OptimizationObjective
from .market_data_engine import MarketDataEngine, MarketTick, OHLCV, OrderBook
from .clearing_settlement_engine import ClearingSettlementEngine, Trade, MarginRequirement, Collateral
from .compliance_engine import ComplianceEngine, ComplianceRule, ComplianceViolation, RegulatoryReport
from .credit_risk_engine import CreditRiskEngine, Counterparty, CreditExposure, CreditValuationAdjustment
from .operational_risk_engine import OperationalRiskEngine, OperationalRiskEvent, RiskControl, RiskScenario
from .analytics_engine import AnalyticsEngine, PerformanceMetrics, AttributionResult, PnLExplain

logger = logging.getLogger(__name__)

class SystemStatus(Enum):
    INITIALIZING = "initializing"
    RUNNING = "running"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    SHUTDOWN = "shutdown"

class IntegrationEvent(Enum):
    TRADE_CAPTURED = "trade_captured"
    TRADE_EXECUTED = "trade_executed"
    RISK_LIMIT_BREACHED = "risk_limit_breached"
    COMPLIANCE_VIOLATION = "compliance_violation"
    MARGIN_CALL = "margin_call"
    SETTLEMENT_COMPLETED = "settlement_completed"
    MARKET_DATA_UPDATED = "market_data_updated"
    PRICING_UPDATED = "pricing_updated"

@dataclass
class SystemHealth:
    """System health monitoring"""
    component: str
    status: str
    last_heartbeat: datetime
    error_count: int = 0
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class IntegrationEventData:
    """Integration event data"""
    event_id: str
    event_type: IntegrationEvent
    timestamp: datetime
    source_component: str
    data: Dict[str, Any]
    priority: str = "normal"  # low, normal, high, critical
    processed: bool = False

class ETRMIntegrationEngine:
    """Comprehensive ETRM/CTRM integration engine"""
    
    def __init__(self, db: Session, redis_client=None):
        self.db = db
        self.redis_client = redis_client
        self.status = SystemStatus.INITIALIZING
        
        # Initialize all engines
        self.trade_engine = AdvancedTradeEngine(db)
        self.risk_engine = AdvancedRiskEngine(db)
        self.pricing_engine = PricingEngine()
        self.portfolio_optimizer = PortfolioOptimizer()
        self.market_data_engine = MarketDataEngine(db, redis_client)
        self.clearing_engine = ClearingSettlementEngine(db)
        self.compliance_engine = ComplianceEngine(db)
        self.credit_risk_engine = CreditRiskEngine(db)
        self.operational_risk_engine = OperationalRiskEngine(db)
        self.analytics_engine = AnalyticsEngine(db)
        
        # System monitoring
        self.system_health: Dict[str, SystemHealth] = {}
        self.integration_events: List[IntegrationEventData] = []
        self.event_handlers: Dict[IntegrationEvent, List[Callable]] = {}
        
        # Threading and async
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.running = False
        
        # Initialize system
        self._initialize_system()
    
    def _initialize_system(self):
        """Initialize the integrated system"""
        logger.info("Initializing ETRM Integration Engine...")
        
        # Initialize system health monitoring
        components = [
            "trade_engine", "risk_engine", "pricing_engine", "portfolio_optimizer",
            "market_data_engine", "clearing_engine", "compliance_engine",
            "credit_risk_engine", "operational_risk_engine", "analytics_engine"
        ]
        
        for component in components:
            self.system_health[component] = SystemHealth(
                component=component,
                status="initializing",
                last_heartbeat=datetime.utcnow()
            )
        
        # Initialize event handlers
        self._initialize_event_handlers()
        
        # Set up cross-engine dependencies
        self._setup_engine_dependencies()
        
        self.status = SystemStatus.RUNNING
        logger.info("ETRM Integration Engine initialized successfully")
    
    def _initialize_event_handlers(self):
        """Initialize event handlers for cross-engine communication"""
        
        # Trade captured event
        self.event_handlers[IntegrationEvent.TRADE_CAPTURED] = [
            self._handle_trade_captured,
            self._trigger_risk_checks,
            self._trigger_compliance_checks,
            self._update_credit_exposure
        ]
        
        # Trade executed event
        self.event_handlers[IntegrationEvent.TRADE_EXECUTED] = [
            self._handle_trade_executed,
            self._update_portfolio_metrics,
            self._trigger_settlement_process,
            self._update_analytics
        ]
        
        # Risk limit breached event
        self.event_handlers[IntegrationEvent.RISK_LIMIT_BREACHED] = [
            self._handle_risk_limit_breach,
            self._trigger_risk_controls,
            self._notify_risk_management
        ]
        
        # Compliance violation event
        self.event_handlers[IntegrationEvent.COMPLIANCE_VIOLATION] = [
            self._handle_compliance_violation,
            self._trigger_compliance_controls,
            self._notify_compliance_team
        ]
        
        # Margin call event
        self.event_handlers[IntegrationEvent.MARGIN_CALL] = [
            self._handle_margin_call,
            self._trigger_collateral_management,
            self._notify_treasury_team
        ]
        
        # Market data updated event
        self.event_handlers[IntegrationEvent.MARKET_DATA_UPDATED] = [
            self._handle_market_data_update,
            self._update_pricing_models,
            self._trigger_risk_recalculation,
            self._update_portfolio_valuations
        ]
    
    def _setup_engine_dependencies(self):
        """Set up dependencies between engines"""
        
        # Trade engine dependencies
        self.trade_engine.risk_engine = self.risk_engine
        self.trade_engine.market_data_engine = self.market_data_engine
        
        # Risk engine dependencies
        self.risk_engine.market_data_engine = self.market_data_engine
        
        # Portfolio optimizer dependencies
        self.portfolio_optimizer.risk_engine = self.risk_engine
        
        # Analytics engine dependencies
        self.analytics_engine.trade_engine = self.trade_engine
        self.analytics_engine.risk_engine = self.risk_engine
    
    async def start_system(self):
        """Start the integrated system"""
        logger.info("Starting ETRM Integration Engine...")
        
        self.running = True
        
        # Start all engines
        await self.trade_engine.start()
        await self.market_data_engine.start()
        
        # Start system monitoring
        asyncio.create_task(self._system_monitoring_loop())
        asyncio.create_task(self._event_processing_loop())
        asyncio.create_task(self._health_check_loop())
        
        self.status = SystemStatus.RUNNING
        logger.info("ETRM Integration Engine started successfully")
    
    async def stop_system(self):
        """Stop the integrated system"""
        logger.info("Stopping ETRM Integration Engine...")
        
        self.running = False
        
        # Stop all engines
        await self.trade_engine.stop()
        await self.market_data_engine.stop()
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        self.status = SystemStatus.SHUTDOWN
        logger.info("ETRM Integration Engine stopped")
    
    async def _system_monitoring_loop(self):
        """System monitoring loop"""
        while self.running:
            try:
                await self._monitor_system_health()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Error in system monitoring loop: {e}")
                await asyncio.sleep(10)
    
    async def _event_processing_loop(self):
        """Event processing loop"""
        while self.running:
            try:
                await self._process_integration_events()
                await asyncio.sleep(1)  # Process events every second
            except Exception as e:
                logger.error(f"Error in event processing loop: {e}")
                await asyncio.sleep(5)
    
    async def _health_check_loop(self):
        """Health check loop"""
        while self.running:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(60)  # Health check every minute
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(30)
    
    async def _monitor_system_health(self):
        """Monitor system health"""
        for component, health in self.system_health.items():
            try:
                # Update heartbeat
                health.last_heartbeat = datetime.utcnow()
                health.status = "healthy"
                
                # Check component-specific health
                if component == "trade_engine":
                    health.performance_metrics["active_orders"] = len(self.trade_engine.get_orders())
                    health.performance_metrics["total_positions"] = len(self.trade_engine.get_positions())
                
                elif component == "risk_engine":
                    risk_limits_status = self.risk_engine.get_risk_limits_status()
                    health.performance_metrics["total_limits"] = risk_limits_status["total_limits"]
                    health.performance_metrics["breached_limits"] = risk_limits_status["summary"]["breached_count"]
                
                elif component == "market_data_engine":
                    subscription_status = self.market_data_engine.get_subscription_status()
                    health.performance_metrics["active_subscriptions"] = subscription_status["active_subscriptions"]
                    health.performance_metrics["data_cache_size"] = sum(subscription_status["data_cache_size"].values())
                
            except Exception as e:
                health.status = "error"
                health.error_count += 1
                logger.error(f"Health check failed for {component}: {e}")
    
    async def _process_integration_events(self):
        """Process integration events"""
        # Process events in order of priority
        critical_events = [event for event in self.integration_events 
                          if event.priority == "critical" and not event.processed]
        high_events = [event for event in self.integration_events 
                      if event.priority == "high" and not event.processed]
        normal_events = [event for event in self.integration_events 
                       if event.priority == "normal" and not event.processed]
        
        # Process critical events first
        for event in critical_events + high_events + normal_events:
            try:
                await self._process_event(event)
                event.processed = True
            except Exception as e:
                logger.error(f"Error processing event {event.event_id}: {e}")
                event.error_count = event.error_count + 1 if hasattr(event, 'error_count') else 1
    
    async def _process_event(self, event: IntegrationEventData):
        """Process a single integration event"""
        handlers = self.event_handlers.get(event.event_type, [])
        
        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error(f"Error in event handler {handler.__name__} for event {event.event_id}: {e}")
    
    async def _perform_health_checks(self):
        """Perform comprehensive health checks"""
        health_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": "healthy",
            "components": {}
        }
        
        for component, health in self.system_health.items():
            component_status = {
                "status": health.status,
                "last_heartbeat": health.last_heartbeat.isoformat(),
                "error_count": health.error_count,
                "performance_metrics": health.performance_metrics
            }
            
            health_report["components"][component] = component_status
            
            # Check if component is healthy
            if health.status != "healthy":
                health_report["overall_status"] = "degraded"
        
        # Store health report
        if self.redis_client:
            await self.redis_client.setex(
                "system_health_report", 
                300,  # 5 minute expiry
                json.dumps(health_report)
            )
    
    # Event Handlers
    async def _handle_trade_captured(self, event: IntegrationEventData):
        """Handle trade captured event"""
        trade_data = event.data
        
        # Log trade capture
        logger.info(f"Trade captured: {trade_data.get('trade_id')}")
        
        # Update system health
        self.system_health["trade_engine"].performance_metrics["trades_captured"] = \
            self.system_health["trade_engine"].performance_metrics.get("trades_captured", 0) + 1
    
    async def _handle_trade_executed(self, event: IntegrationEventData):
        """Handle trade executed event"""
        execution_data = event.data
        
        # Log trade execution
        logger.info(f"Trade executed: {execution_data.get('execution_id')}")
        
        # Update analytics
        await self._update_analytics(event)
    
    async def _trigger_risk_checks(self, event: IntegrationEventData):
        """Trigger risk checks for new trade"""
        trade_data = event.data
        
        # Perform risk checks
        risk_result = self.risk_engine.validate_order(trade_data)
        
        if not risk_result.get('approved', False):
            # Create risk limit breach event
            breach_event = IntegrationEventData(
                event_id=f"RLB_{int(datetime.utcnow().timestamp())}",
                event_type=IntegrationEvent.RISK_LIMIT_BREACHED,
                timestamp=datetime.utcnow(),
                source_component="risk_engine",
                data={"trade_id": trade_data.get('trade_id'), "reason": risk_result.get('reason')},
                priority="high"
            )
            self.integration_events.append(breach_event)
    
    async def _trigger_compliance_checks(self, event: IntegrationEventData):
        """Trigger compliance checks for new trade"""
        trade_data = event.data
        
        # Perform compliance checks
        violations = self.compliance_engine.check_compliance(
            trade_data, 
            trade_data.get('counterparty_id'), 
            trade_data.get('regulatory_framework', 'REMIT')
        )
        
        if violations:
            # Create compliance violation event
            violation_event = IntegrationEventData(
                event_id=f"CV_{int(datetime.utcnow().timestamp())}",
                event_type=IntegrationEvent.COMPLIANCE_VIOLATION,
                timestamp=datetime.utcnow(),
                source_component="compliance_engine",
                data={"trade_id": trade_data.get('trade_id'), "violations": violations},
                priority="high"
            )
            self.integration_events.append(violation_event)
    
    async def _update_credit_exposure(self, event: IntegrationEventData):
        """Update credit exposure for new trade"""
        trade_data = event.data
        
        # Calculate credit exposure
        counterparty_id = trade_data.get('counterparty_id')
        if counterparty_id:
            # This would typically involve more complex exposure calculation
            exposure_amount = trade_data.get('notional_amount', 0)
            
            # Update credit risk engine
            # (Implementation would depend on specific credit risk requirements)
            pass
    
    async def _handle_risk_limit_breach(self, event: IntegrationEventData):
        """Handle risk limit breach"""
        breach_data = event.data
        
        logger.warning(f"Risk limit breached: {breach_data.get('reason')}")
        
        # Update risk engine status
        self.system_health["risk_engine"].performance_metrics["limit_breaches"] = \
            self.system_health["risk_engine"].performance_metrics.get("limit_breaches", 0) + 1
    
    async def _handle_compliance_violation(self, event: IntegrationEventData):
        """Handle compliance violation"""
        violation_data = event.data
        
        logger.warning(f"Compliance violation: {violation_data.get('violations')}")
        
        # Update compliance engine status
        self.system_health["compliance_engine"].performance_metrics["violations"] = \
            self.system_health["compliance_engine"].performance_metrics.get("violations", 0) + 1
    
    async def _handle_margin_call(self, event: IntegrationEventData):
        """Handle margin call"""
        margin_data = event.data
        
        logger.warning(f"Margin call: {margin_data.get('margin_call_id')}")
        
        # Update clearing engine status
        self.system_health["clearing_engine"].performance_metrics["margin_calls"] = \
            self.system_health["clearing_engine"].performance_metrics.get("margin_calls", 0) + 1
    
    async def _handle_market_data_update(self, event: IntegrationEventData):
        """Handle market data update"""
        market_data = event.data
        
        # Update pricing models
        await self._update_pricing_models(event)
        
        # Trigger risk recalculation
        await self._trigger_risk_recalculation(event)
    
    async def _update_pricing_models(self, event: IntegrationEventData):
        """Update pricing models with new market data"""
        # This would typically involve updating pricing models with new market data
        pass
    
    async def _trigger_risk_recalculation(self, event: IntegrationEventData):
        """Trigger risk recalculation with new market data"""
        # This would typically involve recalculating risk metrics with new market data
        pass
    
    async def _update_portfolio_valuations(self, event: IntegrationEventData):
        """Update portfolio valuations with new market data"""
        # This would typically involve updating portfolio valuations
        pass
    
    async def _update_analytics(self, event: IntegrationEventData):
        """Update analytics with new trade data"""
        # This would typically involve updating analytics with new trade data
        pass
    
    async def _update_portfolio_metrics(self, event: IntegrationEventData):
        """Update portfolio metrics"""
        # This would typically involve updating portfolio metrics
        pass
    
    async def _trigger_settlement_process(self, event: IntegrationEventData):
        """Trigger settlement process"""
        # This would typically involve triggering settlement processes
        pass
    
    async def _trigger_risk_controls(self, event: IntegrationEventData):
        """Trigger risk controls"""
        # This would typically involve triggering risk controls
        pass
    
    async def _notify_risk_management(self, event: IntegrationEventData):
        """Notify risk management team"""
        # This would typically involve sending notifications
        pass
    
    async def _trigger_compliance_controls(self, event: IntegrationEventData):
        """Trigger compliance controls"""
        # This would typically involve triggering compliance controls
        pass
    
    async def _notify_compliance_team(self, event: IntegrationEventData):
        """Notify compliance team"""
        # This would typically involve sending notifications
        pass
    
    async def _trigger_collateral_management(self, event: IntegrationEventData):
        """Trigger collateral management"""
        # This would typically involve triggering collateral management
        pass
    
    async def _notify_treasury_team(self, event: IntegrationEventData):
        """Notify treasury team"""
        # This would typically involve sending notifications
        pass
    
    # Public API Methods
    def create_trade(self, trade_data: Dict[str, Any]) -> str:
        """Create a new trade through the integrated system"""
        try:
            # Create trade in trade engine
            order = self.trade_engine.create_order(
                client_order_id=trade_data.get('client_order_id'),
                instrument=trade_data.get('instrument'),
                side=trade_data.get('side'),
                order_type=trade_data.get('order_type'),
                quantity=trade_data.get('quantity'),
                price=trade_data.get('price')
            )
            
            # Create integration event
            event = IntegrationEventData(
                event_id=f"TC_{order.order_id}",
                event_type=IntegrationEvent.TRADE_CAPTURED,
                timestamp=datetime.utcnow(),
                source_component="trade_engine",
                data=trade_data,
                priority="normal"
            )
            self.integration_events.append(event)
            
            return order.order_id
            
        except Exception as e:
            logger.error(f"Error creating trade: {e}")
            raise
    
    def execute_trade(self, order_id: str, market_price: float) -> List[Execution]:
        """Execute a trade through the integrated system"""
        try:
            # Execute trade in trade engine
            executions = await self.trade_engine.execute_order(order_id, market_price)
            
            # Create integration event for each execution
            for execution in executions:
                event = IntegrationEventData(
                    event_id=f"TE_{execution.execution_id}",
                    event_type=IntegrationEvent.TRADE_EXECUTED,
                    timestamp=datetime.utcnow(),
                    source_component="trade_engine",
                    data={"execution_id": execution.execution_id, "order_id": order_id},
                    priority="normal"
                )
                self.integration_events.append(event)
            
            return executions
            
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            raise
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "system_status": self.status.value,
            "running": self.running,
            "components": {
                component: {
                    "status": health.status,
                    "last_heartbeat": health.last_heartbeat.isoformat(),
                    "error_count": health.error_count,
                    "performance_metrics": health.performance_metrics
                }
                for component, health in self.system_health.items()
            },
            "integration_events": {
                "total_events": len(self.integration_events),
                "unprocessed_events": len([e for e in self.integration_events if not e.processed]),
                "critical_events": len([e for e in self.integration_events if e.priority == "critical" and not e.processed])
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_comprehensive_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        try:
            # Get data from all engines
            trade_summary = self.trade_engine.get_portfolio_summary()
            risk_summary = self.risk_engine.get_risk_limits_status()
            compliance_summary = self.compliance_engine.get_compliance_summary()
            credit_summary = self.credit_risk_engine.get_credit_risk_summary()
            operational_summary = self.operational_risk_engine.get_operational_risk_summary()
            analytics_summary = self.analytics_engine.get_analytics_summary()
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "system_status": self.get_system_status(),
                "trading": trade_summary,
                "risk_management": risk_summary,
                "compliance": compliance_summary,
                "credit_risk": credit_summary,
                "operational_risk": operational_summary,
                "analytics": analytics_summary
            }
            
        except Exception as e:
            logger.error(f"Error getting comprehensive dashboard: {e}")
            return {"error": str(e)}
    
    def get_engine_health(self, engine_name: str) -> Dict[str, Any]:
        """Get health status of specific engine"""
        if engine_name not in self.system_health:
            return {"error": f"Engine {engine_name} not found"}
        
        health = self.system_health[engine_name]
        return {
            "component": health.component,
            "status": health.status,
            "last_heartbeat": health.last_heartbeat.isoformat(),
            "error_count": health.error_count,
            "performance_metrics": health.performance_metrics,
            "metadata": health.metadata
        }
