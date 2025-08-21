"""
ETRM/CTRM API endpoints for EnergyOpti-Pro.

This module provides comprehensive endpoints for Energy Trading and Risk Management
including contract management, trading operations, position management, risk management,
compliance, market data, settlement, and regional compliance rules.

All endpoints now use tenant-aware database sessions for complete data isolation.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from ...db.database import get_db
from ...db.models import (
    Contract, Trade, Position, RiskMetrics, Compliance,
    MarketData, Settlement, Counterparty, Company, RegionalCompliance
)
from ...api.dependencies import (
    get_tenant_session, require_trader, require_analyst, 
    require_risk_manager, require_compliance_admin
)
from ...db.schemas import User
import uuid

router = APIRouter()

# Pydantic Models
class ContractCreate(BaseModel):
    contract_type: str
    counterparty_id: str
    commodity: str
    delivery_location: str
    delivery_period_start: datetime
    delivery_period_end: datetime
    quantity: float
    unit: str
    price: Decimal
    currency: str
    region: str
    compliance_flags: Optional[Dict[str, Any]] = None

class TradeCreate(BaseModel):
    contract_id: str
    trader_id: int
    side: str  # buy or sell
    quantity: float
    price: Decimal
    trade_date: datetime
    region: str

class RiskLimitUpdate(BaseModel):
    var_limit: Optional[float] = None
    position_limit: Optional[float] = None
    correlation_limit: Optional[float] = None
    region: str

class ComplianceReport(BaseModel):
    regulation_name: str
    report_period: str
    data: Dict[str, Any]
    region: str

# Contract Management
@router.post("/contracts/", response_model=Dict[str, Any])
async def create_contract(
    contract: ContractCreate,
    current_user: User = Depends(require_trader),
    db: AsyncSession = Depends(get_tenant_session)
):
    """Create new energy contract with automatic company scoping"""
    
    # Validate contract data
    if contract.delivery_period_end <= contract.delivery_period_start:
        raise HTTPException(status_code=400, detail="Delivery end must be after start")
    
    if contract.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")
    
    if contract.price <= 0:
        raise HTTPException(status_code=400, detail="Price must be positive")
    
    # Create contract - company_id automatically set by tenant session
    db_contract = Contract(
        contract_number=f"CTR-{contract.region}-{uuid.uuid4().hex[:8].upper()}",
        contract_type=contract.contract_type,
        counterparty_id=contract.counterparty_id,
        commodity=contract.commodity,
        delivery_location=contract.delivery_location,
        delivery_period_start=contract.delivery_period_start,
        delivery_period_end=contract.delivery_period_end,
        quantity=contract.quantity,
        unit=contract.unit,
        price=contract.price,
        currency=contract.currency,
        status="active",
        region=contract.region,
        compliance_flags=contract.compliance_flags or {}
    )
    
    # Add to database - company_id automatically set
    db.add(db_contract)
    await db.commit()
    await db.refresh(db_contract)
    
    return {
        "status": "created",
        "contract_id": db_contract.id,
        "contract_number": db_contract.contract_number,
        "message": "Contract created successfully"
    }

@router.get("/contracts/", response_model=List[Dict[str, Any]])
async def get_contracts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    contract_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    current_user: User = Depends(require_trader),
    db: AsyncSession = Depends(get_tenant_session)
):
    """Get contracts with automatic company scoping"""
    
    # Build query - company_id automatically filtered by tenant session
    query = select(Contract)
    
    if contract_type:
        query = query.where(Contract.contract_type == contract_type)
    if status:
        query = query.where(Contract.status == status)
    if region:
        query = query.where(Contract.region == region)
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    # Execute query - company_id automatically filtered
    result = await db.execute(query)
    contracts = result.scalars().all()
    
    return [
        {
            "id": contract.id,
            "contract_number": contract.contract_number,
            "contract_type": contract.contract_type,
            "commodity": contract.commodity,
            "quantity": contract.quantity,
            "price": float(contract.price),
            "status": contract.status,
            "region": contract.region
        }
        for contract in contracts
    ]

# Trading Operations
@router.post("/trades/", response_model=Dict[str, Any])
async def execute_trade(
    trade: TradeCreate,
    current_user: User = Depends(require_trader),
    db: AsyncSession = Depends(get_tenant_session)
):
    """Execute trade with automatic company scoping"""
    
    # Validate trade data
    if trade.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")
    
    if trade.price <= 0:
        raise HTTPException(status_code=400, detail="Price must be positive")
    
    if trade.side not in ["buy", "sell"]:
        raise HTTPException(status_code=400, detail="Side must be 'buy' or 'sell'")
    
    # Create trade - company_id automatically set by tenant session
    db_trade = Trade(
        trade_id=f"TRD-{trade.region}-{uuid.uuid4().hex[:8].upper()}",
        contract_id=trade.contract_id,
        trader_id=trade.trader_id,
        side=trade.side,
        quantity=trade.quantity,
        price=trade.price,
        trade_date=trade.trade_date,
        status="executed",
        region=trade.region
    )
    
    # Add to database - company_id automatically set
    db.add(db_trade)
    await db.commit()
    await db.refresh(db_trade)
    
    return {
        "status": "executed",
        "trade_id": db_trade.id,
        "message": "Trade executed successfully"
    }

@router.get("/trades/", response_model=List[Dict[str, Any]])
async def get_trades(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    side: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    current_user: User = Depends(require_trader),
    db: AsyncSession = Depends(get_tenant_session)
):
    """Get trades with automatic company scoping"""
    
    # Build query - company_id automatically filtered by tenant session
    query = select(Trade)
    
    if side:
        query = query.where(Trade.side == side)
    if status:
        query = query.where(Trade.status == status)
    if region:
        query = query.where(Trade.region == region)
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    # Execute query - company_id automatically filtered
    result = await db.execute(query)
    trades = result.scalars().all()
    
    return [
        {
            "id": trade.id,
            "trade_id": trade.trade_id,
            "side": trade.side,
            "quantity": trade.quantity,
            "price": float(trade.price),
            "status": trade.status,
            "region": trade.region,
            "trade_date": trade.trade_date.isoformat()
        }
        for trade in trades
    ]

# Position Management
@router.get("/positions/", response_model=List[Dict[str, Any]])
async def get_positions(
    current_user: User = Depends(require_trader),
    db: AsyncSession = Depends(get_tenant_session)
):
    """Get current positions with automatic company scoping"""
    
    # Query positions - company_id automatically filtered by tenant session
    query = select(Position)
    result = await db.execute(query)
    positions = result.scalars().all()
    
    return [
        {
            "id": position.id,
            "quantity": position.quantity,
            "average_price": float(position.average_price),
            "mark_to_market": float(position.mark_to_market),
            "unrealized_pnl": float(position.unrealized_pnl),
            "region": position.region
        }
        for position in positions
    ]

# Risk Management
@router.get("/risk/var", response_model=Dict[str, Any])
async def calculate_var(
    region: str = Query(...),
    confidence_level: float = Query(0.95),
    current_user: User = Depends(require_risk_manager),
    db: AsyncSession = Depends(get_tenant_session)
):
    """Calculate Value at Risk with automatic company scoping"""
    
    # Mock VaR calculation - in production, use real risk models
    # company_id automatically filtered by tenant session
    var_amount = 150000.0  # Mock value
    
    return {
        "var": var_amount,
        "confidence_level": confidence_level,
        "region": region,
        "currency": "USD",
        "calculation_date": datetime.now().isoformat()
    }

@router.get("/risk/limits", response_model=Dict[str, Any])
async def get_risk_limits(
    current_user: User = Depends(require_risk_manager),
    db: AsyncSession = Depends(get_tenant_session)
):
    """Get risk limits with automatic company scoping"""
    
    # Mock risk limits - company_id automatically filtered by tenant session
    return {
        "var_limit": 1000000.0,
        "position_limit": 5000000.0,
        "correlation_limit": 0.7,
        "currency": "USD"
    }

# Compliance Management
@router.get("/compliance/status", response_model=Dict[str, Any])
async def get_compliance_status(
    current_user: User = Depends(require_compliance_admin),
    db: AsyncSession = Depends(get_tenant_session)
):
    """Get compliance status with automatic company scoping"""
    
    # Query compliance records - company_id automatically filtered by tenant session
    query = select(Compliance)
    result = await db.execute(query)
    compliance_records = result.scalars().all()
    
    return {
        "total_regulations": len(compliance_records),
        "compliant": len([r for r in compliance_records if r.compliance_status == "compliant"]),
        "non_compliant": len([r for r in compliance_records if r.compliance_status != "compliant"]),
        "last_check": max([r.last_check_date for r in compliance_records if r.last_check_date]).isoformat() if compliance_records else None
    }

@router.post("/compliance/reports", response_model=Dict[str, Any])
async def submit_compliance_report(
    report: ComplianceReport,
    current_user: User = Depends(require_compliance_admin),
    db: AsyncSession = Depends(get_tenant_session)
):
    """Submit compliance report with automatic company scoping"""
    
    # Create compliance record - company_id automatically set by tenant session
    compliance_record = Compliance(
        regulation_name=report.regulation_name,
        compliance_status="pending_review",
        last_check_date=datetime.now(),
        region=report.region
    )
    
    # Add to database - company_id automatically set
    db.add(compliance_record)
    await db.commit()
    await db.refresh(compliance_record)
    
    return {
        "status": "submitted",
        "compliance_id": compliance_record.id,
        "message": "Compliance report submitted successfully"
    }

# Market Data
@router.get("/market/prices", response_model=List[Dict[str, Any]])
async def get_market_prices(
    current_user: User = Depends(require_trader),
    db: AsyncSession = Depends(get_tenant_session)
):
    """Get market prices with automatic company scoping"""
    
    # Query market data - company_id automatically filtered by tenant session
    query = select(MarketData).order_by(MarketData.timestamp.desc()).limit(10)
    result = await db.execute(query)
    market_data = result.scalars().all()
    
    return [
        {
            "symbol": data.symbol,
            "price": data.price,
            "volume": data.volume,
            "timestamp": data.timestamp.isoformat(),
            "source": data.source
        }
        for data in market_data
    ]

# Settlement Management
@router.get("/settlements/", response_model=List[Dict[str, Any]])
async def get_settlements(
    current_user: User = Depends(require_trader),
    db: AsyncSession = Depends(get_tenant_session)
):
    """Get settlements with automatic company scoping"""
    
    # Query settlements - company_id automatically filtered by tenant session
    query = select(Settlement).order_by(Settlement.settlement_date.desc()).limit(10)
    result = await db.execute(query)
    settlements = result.scalars().all()
    
    return [
        {
            "id": settlement.id,
            "settlement_date": settlement.settlement_date.isoformat(),
            "settlement_amount": float(settlement.settlement_amount),
            "currency": settlement.currency,
            "status": settlement.status
        }
        for settlement in settlements
    ]

# Regional Compliance Rules
@router.get("/compliance/rules", response_model=List[Dict[str, Any]])
async def get_regional_compliance_rules(
    region: Optional[str] = Query(None),
    current_user: User = Depends(require_compliance_admin),
    db: AsyncSession = Depends(get_tenant_session)
):
    """Get regional compliance rules"""
    
    # Query regional compliance rules (not tenant-scoped)
    query = select(RegionalCompliance)
    if region:
        query = query.where(RegionalCompliance.region == region)
    
    result = await db.execute(query)
    rules = result.scalars().all()
    
    return [
        {
            "id": rule.id,
            "region": rule.region,
            "regulation_name": rule.regulation_name,
            "regulation_version": rule.regulation_version,
            "effective_date": rule.effective_date.isoformat() if rule.effective_date else None,
            "requirements": rule.requirements
        }
        for rule in rules
    ] 