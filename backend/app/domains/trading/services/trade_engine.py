"""
Trade Engine Service - SOLID Principles Implementation
Single Responsibility: Trade execution and lifecycle management
Open/Closed: Extensible for different trade types
Liskov Substitution: Consistent interface for all trade operations
Interface Segregation: Focused interfaces for specific operations
Dependency Inversion: Depends on abstractions, not concretions
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Protocol
from datetime import datetime
import asyncio
import logging

from ..entities.trade_entity import TradeEntity, TradeStatus, TradeDirection
from ...risk.services.risk_calculator import RiskCalculator
from ...compliance.services.compliance_checker import ComplianceChecker

logger = logging.getLogger(__name__)

class TradeRepository(Protocol):
    """Repository interface for trade persistence"""
    
    async def save(self, trade: TradeEntity) -> TradeEntity:
        """Save trade to repository"""
        ...
    
    async def find_by_id(self, trade_id: str) -> Optional[TradeEntity]:
        """Find trade by ID"""
        ...
    
    async def find_by_status(self, status: TradeStatus) -> List[TradeEntity]:
        """Find trades by status"""
        ...
    
    async def find_by_symbol(self, symbol: str) -> List[TradeEntity]:
        """Find trades by symbol"""
        ...

class MarketDataProvider(Protocol):
    """Market data provider interface"""
    
    async def get_current_price(self, symbol: str) -> float:
        """Get current market price for symbol"""
        ...
    
    async def get_price_history(self, symbol: str, days: int) -> List[Dict[str, Any]]:
        """Get historical price data"""
        ...

class TradeExecutionService(ABC):
    """Abstract trade execution service"""
    
    @abstractmethod
    async def execute_trade(self, trade: TradeEntity) -> TradeEntity:
        """Execute a trade"""
        pass
    
    @abstractmethod
    async def validate_trade(self, trade: TradeEntity) -> bool:
        """Validate trade before execution"""
        pass

class EnergyTradeExecutionService(TradeExecutionService):
    """Concrete implementation for energy commodity trades"""
    
    def __init__(self, 
                 market_data: MarketDataProvider,
                 risk_calculator: RiskCalculator,
                 compliance_checker: ComplianceChecker):
        self.market_data = market_data
        self.risk_calculator = risk_calculator
        self.compliance_checker = compliance_checker
    
    async def execute_trade(self, trade: TradeEntity) -> TradeEntity:
        """Execute energy commodity trade"""
        try:
            # Validate trade
            if not await self.validate_trade(trade):
                raise ValueError("Trade validation failed")
            
            # Get current market price
            current_price = await self.market_data.get_current_price(trade.symbol)
            
            # Execute with current price
            trade.execute(current_price)
            
            logger.info(f"Trade {trade.trade_id} executed at price {current_price}")
            return trade
            
        except Exception as e:
            logger.error(f"Trade execution failed for {trade.trade_id}: {e}")
            raise
    
    async def validate_trade(self, trade: TradeEntity) -> bool:
        """Validate energy trade"""
        try:
            # Check if trade is in valid state
            if trade.status != TradeStatus.PENDING:
                return False
            
            # Check compliance
            compliance_result = await self.compliance_checker.check_trade_compliance(trade)
            if not compliance_result.get('approved', False):
                logger.warning(f"Trade {trade.trade_id} failed compliance check")
                return False
            
            # Check risk limits
            risk_result = await self.risk_calculator.calculate_trade_risk(trade)
            if risk_result.get('risk_score', 0) > 0.8:  # High risk threshold
                logger.warning(f"Trade {trade.trade_id} exceeds risk limits")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Trade validation failed for {trade.trade_id}: {e}")
            return False

class TradeEngine:
    """
    Main Trade Engine following SOLID principles
    Single Responsibility: Manages trade lifecycle
    Open/Closed: Extensible for new trade types
    Liskov Substitution: Works with any TradeExecutionService
    Interface Segregation: Focused on trade operations
    Dependency Inversion: Depends on abstractions
    """
    
    def __init__(self,
                 repository: TradeRepository,
                 execution_service: TradeExecutionService,
                 market_data: MarketDataProvider):
        self.repository = repository
        self.execution_service = execution_service
        self.market_data = market_data
    
    async def create_trade(self, 
                          symbol: str,
                          direction: TradeDirection,
                          quantity: float,
                          price: float,
                          currency: str = "USD",
                          counterparty_id: Optional[str] = None,
                          region: str = "US") -> TradeEntity:
        """Create a new trade"""
        try:
            trade = TradeEntity(
                symbol=symbol,
                direction=direction,
                quantity=quantity,
                price=price,
                currency=currency,
                counterparty_id=counterparty_id,
                region=region
            )
            
            # Save to repository
            saved_trade = await self.repository.save(trade)
            
            logger.info(f"Created trade {saved_trade.trade_id} for {symbol}")
            return saved_trade
            
        except Exception as e:
            logger.error(f"Failed to create trade: {e}")
            raise
    
    async def execute_trade(self, trade_id: str) -> TradeEntity:
        """Execute a pending trade"""
        try:
            # Get trade from repository
            trade = await self.repository.find_by_id(trade_id)
            if not trade:
                raise ValueError(f"Trade {trade_id} not found")
            
            # Execute using execution service
            executed_trade = await self.execution_service.execute_trade(trade)
            
            # Save updated trade
            saved_trade = await self.repository.save(executed_trade)
            
            logger.info(f"Executed trade {trade_id}")
            return saved_trade
            
        except Exception as e:
            logger.error(f"Failed to execute trade {trade_id}: {e}")
            raise
    
    async def settle_trade(self, trade_id: str, settlement_price: float) -> TradeEntity:
        """Settle an executed trade"""
        try:
            # Get trade from repository
            trade = await self.repository.find_by_id(trade_id)
            if not trade:
                raise ValueError(f"Trade {trade_id} not found")
            
            # Settle the trade
            trade.settle(settlement_price)
            
            # Save updated trade
            saved_trade = await self.repository.save(trade)
            
            logger.info(f"Settled trade {trade_id} at price {settlement_price}")
            return saved_trade
            
        except Exception as e:
            logger.error(f"Failed to settle trade {trade_id}: {e}")
            raise
    
    async def cancel_trade(self, trade_id: str, reason: str = "User cancelled") -> TradeEntity:
        """Cancel a trade"""
        try:
            # Get trade from repository
            trade = await self.repository.find_by_id(trade_id)
            if not trade:
                raise ValueError(f"Trade {trade_id} not found")
            
            # Cancel the trade
            trade.cancel(reason)
            
            # Save updated trade
            saved_trade = await self.repository.save(trade)
            
            logger.info(f"Cancelled trade {trade_id}: {reason}")
            return saved_trade
            
        except Exception as e:
            logger.error(f"Failed to cancel trade {trade_id}: {e}")
            raise
    
    async def get_trade_pnl(self, trade_id: str, current_price: Optional[float] = None) -> Dict[str, Any]:
        """Get P&L for a trade"""
        try:
            trade = await self.repository.find_by_id(trade_id)
            if not trade:
                raise ValueError(f"Trade {trade_id} not found")
            
            if trade.status == TradeStatus.SETTLED:
                # Realized P&L
                return {
                    "trade_id": trade_id,
                    "pnl_type": "realized",
                    "pnl": trade.realized_pnl,
                    "status": "settled"
                }
            elif trade.status == TradeStatus.EXECUTED:
                # Unrealized P&L
                if current_price is None:
                    current_price = await self.market_data.get_current_price(trade.symbol)
                
                unrealized_pnl = trade.get_unrealized_pnl(current_price)
                return {
                    "trade_id": trade_id,
                    "pnl_type": "unrealized",
                    "pnl": unrealized_pnl,
                    "current_price": current_price,
                    "status": "executed"
                }
            else:
                return {
                    "trade_id": trade_id,
                    "pnl_type": "none",
                    "pnl": 0,
                    "status": trade.status.value
                }
                
        except Exception as e:
            logger.error(f"Failed to get P&L for trade {trade_id}: {e}")
            raise
    
    async def get_portfolio_pnl(self, trades: List[TradeEntity]) -> Dict[str, Any]:
        """Calculate portfolio P&L"""
        try:
            total_realized = 0
            total_unrealized = 0
            position_pnls = []
            
            for trade in trades:
                if trade.status == TradeStatus.SETTLED and trade.realized_pnl:
                    total_realized += trade.realized_pnl
                elif trade.status == TradeStatus.EXECUTED:
                    current_price = await self.market_data.get_current_price(trade.symbol)
                    unrealized_pnl = trade.get_unrealized_pnl(current_price)
                    total_unrealized += unrealized_pnl
                
                position_pnls.append({
                    "trade_id": trade.trade_id,
                    "symbol": trade.symbol,
                    "quantity": trade.quantity,
                    "direction": trade.direction.value,
                    "status": trade.status.value,
                    "realized_pnl": trade.realized_pnl,
                    "unrealized_pnl": trade.get_unrealized_pnl(
                        await self.market_data.get_current_price(trade.symbol)
                    ) if trade.status == TradeStatus.EXECUTED else None
                })
            
            return {
                "total_realized_pnl": total_realized,
                "total_unrealized_pnl": total_unrealized,
                "total_pnl": total_realized + total_unrealized,
                "position_count": len(trades),
                "positions": position_pnls
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate portfolio P&L: {e}")
            raise
    
    async def get_trades_by_status(self, status: TradeStatus) -> List[TradeEntity]:
        """Get trades by status"""
        return await self.repository.find_by_status(status)
    
    async def get_trades_by_symbol(self, symbol: str) -> List[TradeEntity]:
        """Get trades by symbol"""
        return await self.repository.find_by_symbol(symbol)
