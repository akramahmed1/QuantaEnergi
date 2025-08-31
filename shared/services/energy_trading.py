from abc import ABC, abstractmethod
from typing import Dict, Any, List, Callable
from datetime import datetime
import structlog
from collections import defaultdict

logger = structlog.get_logger()

class TradingStrategy(ABC):
    """Abstract base class for trading strategies"""
    
    @abstractmethod
    def execute(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the trading strategy"""
        pass
    
    @abstractmethod
    def get_risk_score(self) -> float:
        """Get the risk score for this strategy"""
        pass

class BaseTradingStrategy(TradingStrategy):
    """Base implementation of trading strategy"""
    
    def __init__(self, name: str, risk_level: float):
        self.name = name
        self.risk_level = risk_level
    
    def execute(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute base trading strategy"""
        return {
            "strategy": self.name,
            "execution_time": datetime.now().isoformat(),
            "risk_level": self.risk_level,
            "status": "executed"
        }
    
    def get_risk_score(self) -> float:
        """Get base risk score"""
        return self.risk_level

class TradingStrategyDecorator(TradingStrategy):
    """Decorator base class for trading strategies"""
    
    def __init__(self, strategy: TradingStrategy):
        self._strategy = strategy
    
    def execute(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute decorated strategy"""
        return self._strategy.execute(market_data)
    
    def get_risk_score(self) -> float:
        """Get decorated risk score"""
        return self._strategy.get_risk_score()

class RiskManagementDecorator(TradingStrategyDecorator):
    """Decorator that adds risk management to trading strategies"""
    
    def execute(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute with risk management"""
        base_result = self._strategy.execute(market_data)
        
        # Add risk management logic
        risk_assessment = self._assess_risk(market_data)
        
        base_result["risk_management"] = {
            "risk_assessment": risk_assessment,
            "stop_loss": self._calculate_stop_loss(market_data),
            "position_size": self._calculate_position_size(market_data)
        }
        
        return base_result
    
    def get_risk_score(self) -> float:
        """Get adjusted risk score with risk management"""
        base_score = self._strategy.get_risk_score()
        return max(0.1, base_score * 0.8)  # Reduce risk by 20%
    
    def _assess_risk(self, market_data: Dict[str, Any]) -> str:
        """Assess market risk"""
        volatility = market_data.get("volatility", 0)
        if volatility > 0.3:
            return "high"
        elif volatility > 0.15:
            return "medium"
        else:
            return "low"
    
    def _calculate_stop_loss(self, market_data: Dict[str, Any]) -> float:
        """Calculate stop loss level"""
        current_price = market_data.get("current_price", 100)
        volatility = market_data.get("volatility", 0.1)
        return current_price * (1 - volatility)
    
    def _calculate_position_size(self, market_data: Dict[str, Any]) -> float:
        """Calculate recommended position size"""
        risk_score = self.get_risk_score()
        return max(0.1, 1.0 - risk_score)

class ComplianceDecorator(TradingStrategyDecorator):
    """Decorator that adds compliance checks to trading strategies"""
    
    def execute(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute with compliance checks"""
        base_result = self._strategy.execute(market_data)
        
        # Add compliance checks
        compliance_status = self._check_compliance(market_data)
        
        base_result["compliance"] = {
            "status": compliance_status,
            "checks": self._run_compliance_checks(market_data),
            "timestamp": datetime.now().isoformat()
        }
        
        return base_result
    
    def get_risk_score(self) -> float:
        """Get compliance-adjusted risk score"""
        base_score = self._strategy.get_risk_score()
        return base_score  # Compliance doesn't change risk score
    
    def _check_compliance(self, market_data: Dict[str, Any]) -> str:
        """Check trading compliance"""
        # Basic compliance checks
        if market_data.get("market_hours", True):
            return "compliant"
        else:
            return "non_compliant"
    
    def _run_compliance_checks(self, market_data: Dict[str, Any]) -> List[str]:
        """Run all compliance checks"""
        checks = []
        
        # Market hours check
        if market_data.get("market_hours", True):
            checks.append("Market hours: PASS")
        else:
            checks.append("Market hours: FAIL")
        
        # Position limits check
        if market_data.get("position_size", 0) <= 1000:
            checks.append("Position limits: PASS")
        else:
            checks.append("Position limits: FAIL")
        
        return checks

class MonitoringDecorator(TradingStrategyDecorator):
    """Decorator that adds monitoring and logging to trading strategies"""
    
    def execute(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute with monitoring and logging"""
        start_time = datetime.now()
        
        try:
            # Execute base strategy
            base_result = self._strategy.execute(market_data)
            
            # Add monitoring data
            execution_time = (datetime.now() - start_time).total_seconds()
            base_result["monitoring"] = {
                "execution_time_ms": round(execution_time * 1000, 2),
                "timestamp": datetime.now().isoformat(),
                "performance_metrics": self._calculate_performance_metrics(base_result),
                "resource_usage": self._get_resource_usage()
            }
            
            # Log successful execution
            logger.info("Strategy executed successfully", 
                       strategy=self._strategy.name,
                       execution_time=execution_time,
                       market_data_keys=list(market_data.keys()))
            
            return base_result
            
        except Exception as e:
            # Log error and add error monitoring
            execution_time = (datetime.now() - start_time).total_seconds()
            error_result = {
                "error": str(e),
                "execution_time_ms": round(execution_time * 1000, 2),
                "timestamp": datetime.now().isoformat(),
                "status": "failed"
            }
            
            logger.error("Strategy execution failed",
                        strategy=self._strategy.name,
                        error=str(e),
                        execution_time=execution_time)
            
            return error_result
    
    def get_risk_score(self) -> float:
        """Get monitoring-adjusted risk score"""
        return self._strategy.get_risk_score()
    
    def _calculate_performance_metrics(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance metrics for the strategy execution"""
        return {
            "success_rate": 1.0 if "error" not in result else 0.0,
            "data_quality": len(result.get("risk_management", {})) > 0,
            "compliance_status": result.get("compliance", {}).get("status", "unknown")
        }
    
    def _get_resource_usage(self) -> Dict[str, Any]:
        """Get current resource usage metrics"""
        import psutil
        try:
            return {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent
            }
        except ImportError:
            return {"cpu_percent": "N/A", "memory_percent": "N/A", "disk_usage": "N/A"}

class PerformanceOptimizationDecorator(TradingStrategyDecorator):
    """Decorator that adds performance optimization to trading strategies"""
    
    def execute(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute with performance optimization"""
        # Cache market data if it's the same
        cache_key = self._generate_cache_key(market_data)
        
        if hasattr(self, '_cache') and cache_key in self._cache:
            cached_result = self._cache[cache_key]
            cached_result["cached"] = True
            cached_result["cache_hit"] = True
            return cached_result
        
        # Execute base strategy
        base_result = self._strategy.execute(market_data)
        
        # Add performance optimization data
        base_result["performance_optimization"] = {
            "cached": False,
            "cache_hit": False,
            "optimization_applied": True,
            "cache_key": cache_key
        }
        
        # Cache the result
        if not hasattr(self, '_cache'):
            self._cache = {}
        self._cache[cache_key] = base_result.copy()
        
        # Limit cache size
        if len(self._cache) > 100:
            # Remove oldest entries
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        
        return base_result
    
    def get_risk_score(self) -> float:
        """Get performance-optimized risk score"""
        return self._strategy.get_risk_score()
    
    def _generate_cache_key(self, market_data: Dict[str, Any]) -> str:
        """Generate cache key from market data"""
        import hashlib
        data_str = str(sorted(market_data.items()))
        return hashlib.md5(data_str.encode()).hexdigest()

class MarketEvent:
    """Represents a market event"""
    
    def __init__(self, event_type: str, data: Dict[str, Any], timestamp: datetime = None):
        self.event_type = event_type
        self.data = data
        self.timestamp = timestamp or datetime.now()
        self.event_id = f"{event_type}_{int(self.timestamp.timestamp())}"

class MarketObserver(ABC):
    """Abstract base class for market observers"""
    
    @abstractmethod
    def update(self, event: MarketEvent) -> None:
        """Update observer with market event"""
        pass

class MarketSubject(ABC):
    """Abstract base class for market subject (observable)"""
    
    def __init__(self):
        self._observers: List[MarketObserver] = []
    
    def attach(self, observer: MarketObserver) -> None:
        """Attach an observer"""
        if observer not in self._observers:
            self._observers.append(observer)
            logger.info(f"Observer attached: {type(observer).__name__}")
    
    def detach(self, observer: MarketObserver) -> None:
        """Detach an observer"""
        if observer in self._observers:
            self._observers.remove(observer)
            logger.info(f"Observer detached: {type(observer).__name__}")
    
    def notify(self, event: MarketEvent) -> None:
        """Notify all observers"""
        for observer in self._observers:
            try:
                observer.update(event)
            except Exception as e:
                logger.error(f"Error notifying observer {type(observer).__name__}: {e}")

class MarketDataObserver(MarketObserver):
    """Observer for market data updates"""
    
    def __init__(self, name: str):
        self.name = name
        self.last_update = None
        self.update_count = 0
    
    def update(self, event: MarketEvent) -> None:
        """Handle market data update"""
        self.last_update = event.timestamp
        self.update_count += 1
        
        logger.info(f"Market data updated for {self.name}",
                   event_type=event.event_type,
                   update_count=self.update_count,
                   timestamp=event.timestamp.isoformat())
        
        # Process market data based on event type
        if event.event_type == "price_change":
            self._handle_price_change(event.data)
        elif event.event_type == "volume_spike":
            self._handle_volume_spike(event.data)
        elif event.event_type == "market_open":
            self._handle_market_open(event.data)
    
    def _handle_price_change(self, data: Dict[str, Any]) -> None:
        """Handle price change events"""
        logger.info(f"Price change detected for {self.name}",
                   symbol=data.get("symbol"),
                   price_change=data.get("price_change"),
                   percentage_change=data.get("percentage_change"))
    
    def _handle_volume_spike(self, data: Dict[str, Any]) -> None:
        """Handle volume spike events"""
        logger.info(f"Volume spike detected for {self.name}",
                   symbol=data.get("symbol"),
                   volume=data.get("volume"),
                   average_volume=data.get("average_volume"))
    
    def _handle_market_open(self, data: Dict[str, Any]) -> None:
        """Handle market open events"""
        logger.info(f"Market opened for {self.name}",
                   market=data.get("market"),
                   opening_time=data.get("opening_time"))

class TradingSignalObserver(MarketObserver):
    """Observer for trading signal generation"""
    
    def __init__(self, strategy_name: str):
        self.strategy_name = strategy_name
        self.signals_generated = 0
        self.last_signal = None
    
    def update(self, event: MarketEvent) -> None:
        """Handle trading signal events"""
        if event.event_type == "trading_signal":
            self.signals_generated += 1
            self.last_signal = event.timestamp
            
            signal_data = event.data
            logger.info(f"Trading signal generated for {self.strategy_name}",
                       signal_type=signal_data.get("signal_type"),
                       symbol=signal_data.get("symbol"),
                       confidence=signal_data.get("confidence"),
                       timestamp=event.timestamp.isoformat())
            
            # Generate trading recommendation
            self._generate_trading_recommendation(signal_data)
    
    def _generate_trading_recommendation(self, signal_data: Dict[str, Any]) -> None:
        """Generate trading recommendation based on signal"""
        signal_type = signal_data.get("signal_type", "unknown")
        confidence = signal_data.get("confidence", 0.0)
        
        if confidence > 0.7:
            action = "STRONG_BUY" if signal_type == "buy" else "STRONG_SELL"
        elif confidence > 0.5:
            action = "BUY" if signal_type == "buy" else "SELL"
        else:
            action = "HOLD"
        
        logger.info(f"Trading recommendation for {self.strategy_name}",
                   action=action,
                   confidence=confidence,
                   signal_type=signal_type)

class EnergyTradingService(MarketSubject):
    """Main energy trading service using decorator pattern and observer pattern"""
    
    def __init__(self):
        super().__init__()
        self.strategies = {}
        self._initialize_strategies()
        self._initialize_observers()
    
    def _initialize_strategies(self):
        """Initialize available trading strategies"""
        # Base strategies
        base_strategy = BaseTradingStrategy("Basic Energy Trading", 0.5)
        
        # Decorated strategies
        self.strategies["basic"] = base_strategy
        self.strategies["risk_managed"] = RiskManagementDecorator(base_strategy)
        self.strategies["compliant"] = ComplianceDecorator(base_strategy)
        self.strategies["monitored"] = MonitoringDecorator(base_strategy)
        self.strategies["optimized"] = PerformanceOptimizationDecorator(base_strategy)
        self.strategies["full_featured"] = ComplianceDecorator(
            RiskManagementDecorator(
                MonitoringDecorator(
                    PerformanceOptimizationDecorator(base_strategy)
                )
            )
        )
    
    def _initialize_observers(self):
        """Initialize market observers"""
        # Create market data observer
        market_observer = MarketDataObserver("Energy Market")
        self.attach(market_observer)
        
        # Create trading signal observer
        signal_observer = TradingSignalObserver("Energy Trading Strategy")
        self.attach(signal_observer)
        
        logger.info("Market observers initialized")
    
    def publish_market_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Publish a market event to all observers"""
        event = MarketEvent(event_type, data)
        self.notify(event)
        logger.info(f"Market event published: {event_type}")
    
    def execute_strategy(self, strategy_name: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific trading strategy"""
        if strategy_name not in self.strategies:
            raise ValueError(f"Unknown strategy: {strategy_name}")
        
        strategy = self.strategies[strategy_name]
        return strategy.execute(market_data)
    
    def get_strategy_risk_score(self, strategy_name: str) -> float:
        """Get risk score for a specific strategy"""
        if strategy_name not in self.strategies:
            raise ValueError(f"Unknown strategy: {strategy_name}")
        
        strategy = self.strategies[strategy_name]
        return strategy.get_risk_score()
    
    def list_strategies(self) -> List[str]:
        """List all available strategies"""
        return list(self.strategies.keys())
