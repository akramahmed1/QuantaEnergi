"""
Advanced Clearing and Settlement Engine for ETRM/CTRM Enterprise Application
Implements clearing and settlement systems with netting, margining, and collateral management
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy.orm import Session
import json
import asyncio

logger = logging.getLogger(__name__)

class SettlementType(Enum):
    CASH = "cash"
    PHYSICAL = "physical"
    NET = "net"
    GROSS = "gross"

class MarginType(Enum):
    INITIAL = "initial"
    VARIATION = "variation"
    MAINTENANCE = "maintenance"
    ADDITIONAL = "additional"

class CollateralType(Enum):
    CASH = "cash"
    GOVERNMENT_BONDS = "government_bonds"
    CORPORATE_BONDS = "corporate_bonds"
    EQUITIES = "equities"
    COMMODITIES = "commodities"
    CRYPTOCURRENCY = "cryptocurrency"

class NettingType(Enum):
    BILATERAL = "bilateral"
    MULTILATERAL = "multilateral"
    CENTRAL_COUNTERPARTY = "central_counterparty"

@dataclass
class Trade:
    """Trade representation for clearing"""
    trade_id: str
    counterparty_id: str
    instrument: str
    quantity: Decimal
    price: Decimal
    trade_date: datetime
    settlement_date: datetime
    trade_type: str  # buy/sell
    currency: str = "USD"
    notional_amount: Decimal = Decimal('0')
    status: str = "pending"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.notional_amount == 0:
            self.notional_amount = self.quantity * self.price

@dataclass
class MarginRequirement:
    """Margin requirement calculation"""
    margin_type: MarginType
    amount: Decimal
    currency: str
    calculation_method: str
    risk_factors: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Collateral:
    """Collateral asset"""
    collateral_id: str
    collateral_type: CollateralType
    asset_id: str
    quantity: Decimal
    unit_price: Decimal
    currency: str
    haircut: float = 0.0  # Haircut percentage
    maturity_date: Optional[datetime] = None
    credit_rating: str = "AAA"
    is_eligible: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def market_value(self) -> Decimal:
        return self.quantity * self.unit_price
    
    @property
    def collateral_value(self) -> Decimal:
        """Collateral value after haircut"""
        return self.market_value * (1 - self.haircut)

@dataclass
class NettingSet:
    """Netting set for bilateral/multilateral netting"""
    netting_set_id: str
    counterparty_id: str
    trades: List[Trade]
    netting_type: NettingType
    net_amount: Decimal = Decimal('0')
    net_quantity: Decimal = Decimal('0')
    net_price: Decimal = Decimal('0')
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def calculate_net_amount(self):
        """Calculate net amount for the netting set"""
        buy_amount = sum(trade.notional_amount for trade in self.trades if trade.trade_type == "buy")
        sell_amount = sum(trade.notional_amount for trade in self.trades if trade.trade_type == "sell")
        self.net_amount = buy_amount - sell_amount
        
        # Calculate net quantity and price
        buy_quantity = sum(trade.quantity for trade in self.trades if trade.trade_type == "buy")
        sell_quantity = sum(trade.quantity for trade in self.trades if trade.trade_type == "sell")
        self.net_quantity = buy_quantity - sell_quantity
        
        if self.net_quantity != 0:
            self.net_price = self.net_amount / self.net_quantity
        else:
            self.net_price = Decimal('0')

@dataclass
class SettlementInstruction:
    """Settlement instruction"""
    instruction_id: str
    trade_id: str
    counterparty_id: str
    instrument: str
    quantity: Decimal
    price: Decimal
    amount: Decimal
    currency: str
    settlement_date: datetime
    settlement_type: SettlementType
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MarginCall:
    """Margin call"""
    margin_call_id: str
    counterparty_id: str
    margin_type: MarginType
    required_amount: Decimal
    current_amount: Decimal
    deficit: Decimal
    currency: str
    due_date: datetime
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

class ClearingSettlementEngine:
    """Advanced clearing and settlement engine"""
    
    def __init__(self, db: Session):
        self.db = db
        self.trades: Dict[str, Trade] = {}
        self.netting_sets: Dict[str, NettingSet] = {}
        self.settlement_instructions: Dict[str, SettlementInstruction] = {}
        self.margin_calls: Dict[str, MarginCall] = {}
        self.collateral_pools: Dict[str, List[Collateral]] = {}
        self.margin_requirements: Dict[str, MarginRequirement] = {}
        
        # Risk parameters
        self.margin_rates: Dict[str, float] = {
            "crude_oil": 0.05,  # 5% margin
            "natural_gas": 0.08,  # 8% margin
            "power": 0.10,  # 10% margin
            "coal": 0.06,  # 6% margin
        }
        
        self.haircut_rates: Dict[CollateralType, float] = {
            CollateralType.CASH: 0.0,
            CollateralType.GOVERNMENT_BONDS: 0.02,
            CollateralType.CORPORATE_BONDS: 0.05,
            CollateralType.EQUITIES: 0.15,
            CollateralType.COMMODITIES: 0.20,
            CollateralType.CRYPTOCURRENCY: 0.50,
        }
        
        self.netting_agreements: Dict[str, Dict[str, Any]] = {}
        
    def add_trade(self, trade: Trade) -> str:
        """Add trade to clearing system"""
        self.trades[trade.trade_id] = trade
        logger.info(f"Trade added to clearing: {trade.trade_id}")
        return trade.trade_id
    
    def create_netting_set(self, 
                          counterparty_id: str,
                          netting_type: NettingType,
                          trade_ids: List[str]) -> str:
        """Create netting set for trades"""
        
        # Get trades for counterparty
        counterparty_trades = [trade for trade in self.trades.values() 
                             if trade.counterparty_id == counterparty_id and trade.trade_id in trade_ids]
        
        if not counterparty_trades:
            raise ValueError(f"No trades found for counterparty {counterparty_id}")
        
        netting_set_id = f"NS_{counterparty_id}_{int(datetime.utcnow().timestamp())}"
        
        netting_set = NettingSet(
            netting_set_id=netting_set_id,
            counterparty_id=counterparty_id,
            trades=counterparty_trades,
            netting_type=netting_type
        )
        
        # Calculate net amounts
        netting_set.calculate_net_amount()
        
        self.netting_sets[netting_set_id] = netting_set
        logger.info(f"Netting set created: {netting_set_id}")
        
        return netting_set_id
    
    def calculate_margin_requirements(self, 
                                     counterparty_id: str,
                                     netting_set_id: str = None) -> List[MarginRequirement]:
        """Calculate margin requirements for counterparty"""
        
        if netting_set_id:
            netting_set = self.netting_sets.get(netting_set_id)
            if not netting_set:
                raise ValueError(f"Netting set {netting_set_id} not found")
            trades = netting_set.trades
        else:
            trades = [trade for trade in self.trades.values() 
                     if trade.counterparty_id == counterparty_id]
        
        if not trades:
            return []
        
        margin_requirements = []
        
        # Calculate initial margin
        initial_margin = self._calculate_initial_margin(trades)
        if initial_margin > 0:
            margin_requirements.append(MarginRequirement(
                margin_type=MarginType.INITIAL,
                amount=initial_margin,
                currency="USD",
                calculation_method="standard_portfolio_analysis_of_risk"
            ))
        
        # Calculate variation margin
        variation_margin = self._calculate_variation_margin(trades)
        if variation_margin != 0:
            margin_requirements.append(MarginRequirement(
                margin_type=MarginType.VARIATION,
                amount=abs(variation_margin),
                currency="USD",
                calculation_method="mark_to_market"
            ))
        
        # Calculate maintenance margin
        maintenance_margin = self._calculate_maintenance_margin(trades)
        if maintenance_margin > 0:
            margin_requirements.append(MarginRequirement(
                margin_type=MarginType.MAINTENANCE,
                amount=maintenance_margin,
                currency="USD",
                calculation_method="maintenance_margin_requirement"
            ))
        
        # Store margin requirements
        for req in margin_requirements:
            req_id = f"MR_{counterparty_id}_{req.margin_type.value}_{int(datetime.utcnow().timestamp())}"
            self.margin_requirements[req_id] = req
        
        return margin_requirements
    
    def _calculate_initial_margin(self, trades: List[Trade]) -> Decimal:
        """Calculate initial margin using SPAN methodology"""
        total_margin = Decimal('0')
        
        for trade in trades:
            # Get margin rate for instrument
            margin_rate = self.margin_rates.get(trade.instrument, 0.05)  # Default 5%
            
            # Calculate margin requirement
            margin_requirement = trade.notional_amount * Decimal(str(margin_rate))
            total_margin += margin_requirement
        
        return total_margin
    
    def _calculate_variation_margin(self, trades: List[Trade]) -> Decimal:
        """Calculate variation margin (mark-to-market)"""
        total_variation = Decimal('0')
        
        for trade in trades:
            # This would typically use current market prices
            # For now, we'll use a simplified calculation
            current_price = trade.price * Decimal('1.02')  # 2% price change
            price_change = current_price - trade.price
            variation = price_change * trade.quantity
            
            if trade.trade_type == "buy":
                total_variation += variation
            else:
                total_variation -= variation
        
        return total_variation
    
    def _calculate_maintenance_margin(self, trades: List[Trade]) -> Decimal:
        """Calculate maintenance margin requirement"""
        initial_margin = self._calculate_initial_margin(trades)
        # Maintenance margin is typically 75% of initial margin
        return initial_margin * Decimal('0.75')
    
    def add_collateral(self, 
                      counterparty_id: str,
                      collateral: Collateral) -> str:
        """Add collateral to counterparty's pool"""
        
        if counterparty_id not in self.collateral_pools:
            self.collateral_pools[counterparty_id] = []
        
        self.collateral_pools[counterparty_id].append(collateral)
        logger.info(f"Collateral added for {counterparty_id}: {collateral.collateral_id}")
        
        return collateral.collateral_id
    
    def calculate_collateral_requirements(self, 
                                       counterparty_id: str) -> Dict[str, Any]:
        """Calculate collateral requirements and availability"""
        
        # Get margin requirements
        margin_requirements = [req for req in self.margin_requirements.values() 
                             if req.margin_type in [MarginType.INITIAL, MarginType.MAINTENANCE]]
        
        total_margin_required = sum(req.amount for req in margin_requirements)
        
        # Get available collateral
        collateral_pool = self.collateral_pools.get(counterparty_id, [])
        total_collateral_value = sum(collateral.collateral_value for collateral in collateral_pool)
        
        # Calculate deficit/surplus
        deficit = total_margin_required - total_collateral_value
        
        return {
            "counterparty_id": counterparty_id,
            "total_margin_required": float(total_margin_required),
            "total_collateral_value": float(total_collateral_value),
            "deficit": float(deficit),
            "collateral_ratio": float(total_collateral_value / total_margin_required) if total_margin_required > 0 else 0,
            "margin_requirements": [
                {
                    "margin_type": req.margin_type.value,
                    "amount": float(req.amount),
                    "currency": req.currency
                }
                for req in margin_requirements
            ],
            "collateral_breakdown": [
                {
                    "collateral_id": coll.collateral_id,
                    "collateral_type": coll.collateral_type.value,
                    "market_value": float(coll.market_value),
                    "collateral_value": float(coll.collateral_value),
                    "haircut": coll.haircut
                }
                for coll in collateral_pool
            ]
        }
    
    def create_margin_call(self, 
                          counterparty_id: str,
                          margin_type: MarginType,
                          required_amount: Decimal,
                          current_amount: Decimal) -> str:
        """Create margin call for counterparty"""
        
        deficit = required_amount - current_amount
        
        if deficit <= 0:
            return None  # No margin call needed
        
        margin_call_id = f"MC_{counterparty_id}_{margin_type.value}_{int(datetime.utcnow().timestamp())}"
        
        margin_call = MarginCall(
            margin_call_id=margin_call_id,
            counterparty_id=counterparty_id,
            margin_type=margin_type,
            required_amount=required_amount,
            current_amount=current_amount,
            deficit=deficit,
            currency="USD",
            due_date=datetime.utcnow() + timedelta(days=1)  # 1 day to meet margin call
        )
        
        self.margin_calls[margin_call_id] = margin_call
        logger.info(f"Margin call created: {margin_call_id}")
        
        return margin_call_id
    
    def process_settlement(self, 
                          trade_id: str,
                          settlement_type: SettlementType = SettlementType.CASH) -> str:
        """Process settlement for a trade"""
        
        trade = self.trades.get(trade_id)
        if not trade:
            raise ValueError(f"Trade {trade_id} not found")
        
        # Create settlement instruction
        instruction_id = f"SI_{trade_id}_{int(datetime.utcnow().timestamp())}"
        
        settlement_instruction = SettlementInstruction(
            instruction_id=instruction_id,
            trade_id=trade_id,
            counterparty_id=trade.counterparty_id,
            instrument=trade.instrument,
            quantity=trade.quantity,
            price=trade.price,
            amount=trade.notional_amount,
            currency=trade.currency,
            settlement_date=trade.settlement_date,
            settlement_type=settlement_type
        )
        
        self.settlement_instructions[instruction_id] = settlement_instruction
        
        # Update trade status
        trade.status = "settled"
        
        logger.info(f"Settlement instruction created: {instruction_id}")
        return instruction_id
    
    def process_netting_settlement(self, 
                                  netting_set_id: str,
                                  settlement_type: SettlementType = SettlementType.NET) -> str:
        """Process settlement for netting set"""
        
        netting_set = self.netting_sets.get(netting_set_id)
        if not netting_set:
            raise ValueError(f"Netting set {netting_set_id} not found")
        
        # Create settlement instruction for net amount
        instruction_id = f"NSI_{netting_set_id}_{int(datetime.utcnow().timestamp())}"
        
        settlement_instruction = SettlementInstruction(
            instruction_id=instruction_id,
            trade_id=netting_set_id,
            counterparty_id=netting_set.counterparty_id,
            instrument="NETTED",
            quantity=netting_set.net_quantity,
            price=netting_set.net_price,
            amount=netting_set.net_amount,
            currency="USD",
            settlement_date=datetime.utcnow(),
            settlement_type=settlement_type
        )
        
        self.settlement_instructions[instruction_id] = settlement_instruction
        
        # Update all trades in netting set
        for trade in netting_set.trades:
            trade.status = "settled"
        
        logger.info(f"Netting settlement instruction created: {instruction_id}")
        return instruction_id
    
    def calculate_settlement_risk(self, 
                                 counterparty_id: str) -> Dict[str, Any]:
        """Calculate settlement risk for counterparty"""
        
        # Get all pending trades for counterparty
        pending_trades = [trade for trade in self.trades.values() 
                         if trade.counterparty_id == counterparty_id and trade.status == "pending"]
        
        if not pending_trades:
            return {"settlement_risk": 0, "message": "No pending trades"}
        
        # Calculate total exposure
        total_exposure = sum(trade.notional_amount for trade in pending_trades)
        
        # Calculate net exposure
        buy_exposure = sum(trade.notional_amount for trade in pending_trades if trade.trade_type == "buy")
        sell_exposure = sum(trade.notional_amount for trade in pending_trades if trade.trade_type == "sell")
        net_exposure = abs(buy_exposure - sell_exposure)
        
        # Calculate settlement risk metrics
        gross_exposure = total_exposure
        net_exposure_ratio = net_exposure / gross_exposure if gross_exposure > 0 else 0
        
        # Calculate potential future exposure (simplified)
        volatility = 0.02  # 2% daily volatility
        confidence_level = 0.95
        time_horizon = 1  # 1 day
        
        # VaR calculation
        var = net_exposure * volatility * np.sqrt(time_horizon) * 1.645  # 95% confidence
        
        return {
            "counterparty_id": counterparty_id,
            "total_exposure": float(total_exposure),
            "net_exposure": float(net_exposure),
            "gross_exposure": float(gross_exposure),
            "net_exposure_ratio": float(net_exposure_ratio),
            "var_95_1d": float(var),
            "pending_trades": len(pending_trades),
            "settlement_risk_score": float(net_exposure_ratio * 100)  # Risk score 0-100
        }
    
    def get_settlement_summary(self) -> Dict[str, Any]:
        """Get settlement system summary"""
        
        total_trades = len(self.trades)
        pending_trades = len([trade for trade in self.trades.values() if trade.status == "pending"])
        settled_trades = len([trade for trade in self.trades.values() if trade.status == "settled"])
        
        total_netting_sets = len(self.netting_sets)
        total_settlement_instructions = len(self.settlement_instructions)
        total_margin_calls = len(self.margin_calls)
        
        # Calculate total exposure
        total_exposure = sum(trade.notional_amount for trade in self.trades.values())
        
        return {
            "total_trades": total_trades,
            "pending_trades": pending_trades,
            "settled_trades": settled_trades,
            "settlement_rate": settled_trades / total_trades if total_trades > 0 else 0,
            "total_netting_sets": total_netting_sets,
            "total_settlement_instructions": total_settlement_instructions,
            "total_margin_calls": total_margin_calls,
            "total_exposure": float(total_exposure),
            "counterparties": len(set(trade.counterparty_id for trade in self.trades.values())),
            "instruments": len(set(trade.instrument for trade in self.trades.values()))
        }
    
    def get_counterparty_summary(self, counterparty_id: str) -> Dict[str, Any]:
        """Get summary for specific counterparty"""
        
        counterparty_trades = [trade for trade in self.trades.values() 
                             if trade.counterparty_id == counterparty_id]
        
        if not counterparty_trades:
            return {"message": f"No trades found for counterparty {counterparty_id}"}
        
        # Calculate metrics
        total_trades = len(counterparty_trades)
        pending_trades = len([trade for trade in counterparty_trades if trade.status == "pending"])
        settled_trades = len([trade for trade in counterparty_trades if trade.status == "settled"])
        
        total_exposure = sum(trade.notional_amount for trade in counterparty_trades)
        buy_exposure = sum(trade.notional_amount for trade in counterparty_trades if trade.trade_type == "buy")
        sell_exposure = sum(trade.notional_amount for trade in counterparty_trades if trade.trade_type == "sell")
        net_exposure = buy_exposure - sell_exposure
        
        # Get margin requirements
        margin_requirements = [req for req in self.margin_requirements.values() 
                             if req.margin_type in [MarginType.INITIAL, MarginType.MAINTENANCE]]
        
        total_margin_required = sum(req.amount for req in margin_requirements)
        
        # Get collateral
        collateral_pool = self.collateral_pools.get(counterparty_id, [])
        total_collateral_value = sum(collateral.collateral_value for collateral in collateral_pool)
        
        return {
            "counterparty_id": counterparty_id,
            "total_trades": total_trades,
            "pending_trades": pending_trades,
            "settled_trades": settled_trades,
            "settlement_rate": settled_trades / total_trades if total_trades > 0 else 0,
            "total_exposure": float(total_exposure),
            "buy_exposure": float(buy_exposure),
            "sell_exposure": float(sell_exposure),
            "net_exposure": float(net_exposure),
            "total_margin_required": float(total_margin_required),
            "total_collateral_value": float(total_collateral_value),
            "collateral_ratio": float(total_collateral_value / total_margin_required) if total_margin_required > 0 else 0,
            "margin_calls": len([mc for mc in self.margin_calls.values() if mc.counterparty_id == counterparty_id]),
            "instruments": list(set(trade.instrument for trade in counterparty_trades))
        }
