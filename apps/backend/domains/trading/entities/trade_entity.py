"""
Trade Entity - Domain-Driven Design
Core business entity for energy trading with SOLID principles
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
import uuid

class TradeStatus(str, Enum):
    PENDING = "pending"
    EXECUTED = "executed"
    SETTLED = "settled"
    CANCELLED = "cancelled"

class TradeDirection(str, Enum):
    BUY = "buy"
    SELL = "sell"

class CommodityType(str, Enum):
    CRUDE_OIL = "crude_oil"
    NATURAL_GAS = "natural_gas"
    ELECTRICITY = "electricity"
    COAL = "coal"
    RENEWABLE_ENERGY = "renewable_energy"

@dataclass
class TradeEntity:
    """
    Core Trade Entity following Domain-Driven Design principles
    Encapsulates business logic and invariants
    """
    
    # Identity
    trade_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Core trade attributes
    symbol: str
    direction: TradeDirection
    quantity: float
    price: float
    currency: str = "USD"
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    executed_at: Optional[datetime] = None
    settled_at: Optional[datetime] = None
    
    # Status and metadata
    status: TradeStatus = TradeStatus.PENDING
    commodity_type: CommodityType = CommodityType.CRUDE_OIL
    
    # Risk and compliance
    counterparty_id: Optional[str] = None
    region: str = "US"
    compliance_checked: bool = False
    
    # P&L tracking
    entry_price: Optional[float] = None
    exit_price: Optional[float] = None
    realized_pnl: Optional[float] = None
    
    def __post_init__(self):
        """Validate entity invariants after initialization"""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Validate business invariants"""
        if self.quantity <= 0:
            raise ValueError("Trade quantity must be positive")
        
        if self.price <= 0:
            raise ValueError("Trade price must be positive")
        
        if self.status == TradeStatus.EXECUTED and not self.executed_at:
            raise ValueError("Executed trades must have execution timestamp")
        
        if self.status == TradeStatus.SETTLED and not self.settled_at:
            raise ValueError("Settled trades must have settlement timestamp")
    
    def execute(self, execution_price: float, execution_time: Optional[datetime] = None) -> None:
        """Execute the trade with given price"""
        if self.status != TradeStatus.PENDING:
            raise ValueError("Only pending trades can be executed")
        
        if execution_price <= 0:
            raise ValueError("Execution price must be positive")
        
        self.price = execution_price
        self.entry_price = execution_price
        self.status = TradeStatus.EXECUTED
        self.executed_at = execution_time or datetime.now()
        self._validate_invariants()
    
    def settle(self, settlement_price: float, settlement_time: Optional[datetime] = None) -> None:
        """Settle the trade with final price"""
        if self.status != TradeStatus.EXECUTED:
            raise ValueError("Only executed trades can be settled")
        
        if settlement_price <= 0:
            raise ValueError("Settlement price must be positive")
        
        self.exit_price = settlement_price
        self.status = TradeStatus.SETTLED
        self.settled_at = settlement_time or datetime.now()
        
        # Calculate realized P&L
        self._calculate_realized_pnl()
        self._validate_invariants()
    
    def cancel(self, reason: str = "User cancelled") -> None:
        """Cancel the trade"""
        if self.status not in [TradeStatus.PENDING, TradeStatus.EXECUTED]:
            raise ValueError("Only pending or executed trades can be cancelled")
        
        self.status = TradeStatus.CANCELLED
        self._validate_invariants()
    
    def _calculate_realized_pnl(self) -> None:
        """Calculate realized P&L for settled trades"""
        if self.status == TradeStatus.SETTLED and self.entry_price and self.exit_price:
            price_diff = self.exit_price - self.entry_price
            if self.direction == TradeDirection.SELL:
                price_diff = -price_diff  # Short positions profit when price goes down
            
            self.realized_pnl = self.quantity * price_diff
    
    def get_unrealized_pnl(self, current_price: float) -> float:
        """Calculate unrealized P&L for open positions"""
        if self.status not in [TradeStatus.EXECUTED]:
            return 0.0
        
        if not self.entry_price:
            return 0.0
        
        price_diff = current_price - self.entry_price
        if self.direction == TradeDirection.SELL:
            price_diff = -price_diff
        
        return self.quantity * price_diff
    
    def get_notional_value(self) -> float:
        """Get notional value of the trade"""
        return self.quantity * self.price
    
    def is_profitable(self, current_price: Optional[float] = None) -> bool:
        """Check if trade is profitable"""
        if self.status == TradeStatus.SETTLED:
            return self.realized_pnl is not None and self.realized_pnl > 0
        
        if current_price and self.status == TradeStatus.EXECUTED:
            return self.get_unrealized_pnl(current_price) > 0
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary for serialization"""
        return {
            "trade_id": self.trade_id,
            "symbol": self.symbol,
            "direction": self.direction.value,
            "quantity": self.quantity,
            "price": self.price,
            "currency": self.currency,
            "status": self.status.value,
            "commodity_type": self.commodity_type.value,
            "created_at": self.created_at.isoformat(),
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "settled_at": self.settled_at.isoformat() if self.settled_at else None,
            "counterparty_id": self.counterparty_id,
            "region": self.region,
            "compliance_checked": self.compliance_checked,
            "entry_price": self.entry_price,
            "exit_price": self.exit_price,
            "realized_pnl": self.realized_pnl,
            "notional_value": self.get_notional_value()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TradeEntity':
        """Create entity from dictionary"""
        # Convert string enums back to enum values
        if 'direction' in data and isinstance(data['direction'], str):
            data['direction'] = TradeDirection(data['direction'])
        
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = TradeStatus(data['status'])
        
        if 'commodity_type' in data and isinstance(data['commodity_type'], str):
            data['commodity_type'] = CommodityType(data['commodity_type'])
        
        # Convert ISO datetime strings back to datetime objects
        for field in ['created_at', 'executed_at', 'settled_at']:
            if field in data and data[field] and isinstance(data[field], str):
                data[field] = datetime.fromisoformat(data[field])
        
        return cls(**data)
