"""
Enhanced Trade Lifecycle Service
Integrates with event bus and supports multi-tenant architecture
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from uuid import uuid4
import json

from ..core.event_bus import event_bus, EventType, create_event, publish_event
from ..schemas.trade import (
    TradeCreate, TradeUpdate, TradeResponse, TradeStatusResponse,
    TradeDetails, TradeConfirmation, TradeAllocation, TradeSettlement,
    TradeInvoice, TradePayment, TradeFilter, TradeSearchResponse,
    TradeAnalytics, ShariaComplianceCheck, ComplianceStatus
)
from ..models.organization import Organization
from .sharia_compliance import ShariaComplianceService
from .credit_manager import CreditManager
from .risk_manager import RiskManager

logger = logging.getLogger(__name__)

class EnhancedTradeLifecycleService:
    """
    Enhanced trade lifecycle service with event-driven architecture
    and multi-tenant support
    """
    
    def __init__(self):
        self.sharia_service = ShariaComplianceService()
        self.credit_manager = CreditManager()
        self.risk_manager = RiskManager()
        
        # In-memory storage for demo (replace with database in production)
        self.trades: Dict[str, Dict[str, Any]] = {}
        self.trade_history: List[Dict[str, Any]] = []
        self.confirmations: Dict[str, Dict[str, Any]] = {}
        self.allocations: Dict[str, Dict[str, Any]] = {}
        self.settlements: Dict[str, Dict[str, Any]] = {}
        self.invoices: Dict[str, Dict[str, Any]] = {}
        self.payments: Dict[str, Dict[str, Any]] = {}
        
        # Organization cache
        self.organizations: Dict[str, Organization] = {}
        
        # Initialize with sample organizations
        self._initialize_sample_organizations()
    
    def _initialize_sample_organizations(self):
        """Initialize sample organizations for demo purposes"""
        sample_orgs = [
            {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Saudi Aramco Trading",
                "code": "SAT",
                "organization_type": "oil_company",
                "classification": "tier1",
                "primary_region": "ME",
                "is_islamic_compliant": True,
                "status": "active"
            },
            {
                "id": "456e7890-e89b-12d3-a456-426614174001",
                "name": "ExxonMobil Trading",
                "code": "EMT",
                "organization_type": "oil_company",
                "classification": "tier1",
                "primary_region": "US",
                "is_islamic_compliant": False,
                "status": "active"
            },
            {
                "id": "789e0123-e89b-12d3-a456-426614174002",
                "name": "ADNOC Trading",
                "code": "ADT",
                "organization_type": "trading_firm",
                "classification": "tier2",
                "primary_region": "ME",
                "is_islamic_compliant": True,
                "status": "active"
            }
        ]
        
        for org_data in sample_orgs:
            org = Organization(**org_data)
            self.organizations[org_data["id"]] = org
    
    async def capture_trade(self, trade_data: TradeCreate, user_id: str, organization_id: str) -> TradeResponse:
        """
        Capture a new trade with event publishing
        """
        try:
            # Validate organization
            if organization_id not in self.organizations:
                raise ValueError(f"Organization {organization_id} not found")
            
            org = self.organizations[organization_id]
            if not org.is_active:
                raise ValueError(f"Organization {org.name} is not active")
            
            # Generate trade ID
            trade_id = f"trade_{uuid4().hex[:8]}"
            correlation_id = trade_data.correlation_id or str(uuid4())
            
            # Create trade record
            # Get trade data without user_id to avoid overwriting
            trade_data_dict = trade_data.model_dump()
            trade_data_dict.pop('user_id', None)  # Remove user_id if present
            
            trade_record = {
                "trade_id": trade_id,
                "correlation_id": correlation_id,
                "organization_id": organization_id,
                "user_id": user_id,
                "status": "captured",
                "captured_at": datetime.utcnow(),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                **trade_data_dict
            }
            
            # Store trade
            self.trades[trade_id] = trade_record
            self.trade_history.append(trade_record)
            
            # Publish trade captured event
            try:
                await publish_event(
                    event_type=EventType.TRADE_CAPTURED,
                    payload={
                        "trade_id": trade_id,
                        "trade_data": trade_record,
                        "organization_id": organization_id,
                        "user_id": user_id
                    },
                    correlation_id=correlation_id,
                    user_id=user_id,
                    organization_id=organization_id,
                    source_service="trade_lifecycle"
                )
            except Exception as e:
                # If event bus is not running, start it and try again
                if "Event bus is not running" in str(e):
                    logger.warning("Event bus not running, starting it...")
                    await event_bus.start()
                    await publish_event(
                        event_type=EventType.TRADE_CAPTURED,
                        payload={
                            "trade_id": trade_id,
                            "trade_data": trade_record,
                            "organization_id": organization_id,
                            "user_id": user_id
                        },
                        correlation_id=correlation_id,
                        user_id=user_id,
                        organization_id=organization_id,
                        source_service="trade_lifecycle"
                    )
                else:
                    raise
            
            logger.info(f"Trade {trade_id} captured successfully for organization {organization_id}")
            
            return TradeResponse(
                trade_id=trade_id,
                status="captured",
                message="Trade captured successfully",
                timestamp=datetime.utcnow(),
                organization_id=organization_id,
                correlation_id=correlation_id
            )
            
        except Exception as e:
            logger.error(f"Error capturing trade: {e}")
            raise
    
    async def validate_trade(self, trade_id: str, user_id: str) -> TradeStatusResponse:
        """
        Validate a captured trade
        """
        try:
            if trade_id not in self.trades:
                raise ValueError(f"Trade {trade_id} not found")
            
            trade = self.trades[trade_id]
            organization_id = trade.get("organization_id")
            
            # Check organization status
            if organization_id and organization_id in self.organizations:
                org = self.organizations[organization_id]
                if not org.is_active:
                    return TradeStatusResponse(
                        trade_id=trade_id,
                        status="failed",
                        valid=False,
                        compliant=False,
                        sharia_result={"compliant": False, "restrictions": ["Organization inactive"]},
                        organization_id=organization_id,
                        compliance_status=ComplianceStatus.REJECTED,
                        validation_errors=["Organization is not active"]
                    )
            
            # Perform validation checks
            validation_errors = []
            
            # Basic validation
            if trade.get("quantity", 0) <= 0:
                validation_errors.append("Invalid quantity")
            
            if trade.get("price", 0) <= 0:
                validation_errors.append("Invalid price")
            
            # Islamic compliance check
            if trade.get("is_islamic_compliant", False):
                sharia_check = await self.sharia_service.validate_trade(trade)
                if not sharia_check["compliant"]:
                    validation_errors.extend(sharia_check.get("restrictions", []))
                sharia_result = sharia_check
            else:
                sharia_result = {"compliant": True, "restrictions": []}
            
            # Credit check
            credit_check = await self.credit_manager.check_credit_availability(
                trade.get("counterparty"),
                trade.get("quantity", 0) * trade.get("price", 0)
            )
            
            if not credit_check.get("can_execute", False):
                validation_errors.append("Insufficient credit")
            
            # Risk check
            risk_check = await self.risk_manager.assess_trade_risk(trade)
            if risk_check.get("risk_level") == "high":
                validation_errors.append("Trade exceeds risk limits")
            
            # Update trade status
            is_valid = len(validation_errors) == 0
            is_compliant = sharia_result.get("compliant", False)
            
            if is_valid:
                trade["status"] = "validated"
                trade["validated_at"] = datetime.utcnow()
                trade["updated_at"] = datetime.utcnow()
                
                # Publish trade validated event
                await publish_event(
                    event_type=EventType.TRADE_VALIDATED,
                    payload={
                        "trade_id": trade_id,
                        "validation_result": {
                            "valid": is_valid,
                            "compliant": is_compliant,
                            "sharia_result": sharia_result,
                            "credit_check": credit_check,
                            "risk_check": risk_check
                        }
                    },
                    correlation_id=trade.get("correlation_id"),
                    user_id=user_id,
                    organization_id=organization_id,
                    source_service="trade_lifecycle"
                )
            
            return TradeStatusResponse(
                trade_id=trade_id,
                status=trade["status"],
                valid=is_valid,
                compliant=is_compliant,
                sharia_result=sharia_result,
                organization_id=organization_id,
                compliance_status=ComplianceStatus.APPROVED if is_valid else ComplianceStatus.REJECTED,
                risk_assessment=risk_check,
                validation_errors=validation_errors
            )
            
        except Exception as e:
            logger.error(f"Error validating trade {trade_id}: {e}")
            raise
    
    async def confirm_trade(self, trade_id: str, user_id: str, confirmation_notes: Optional[str] = None) -> TradeConfirmation:
        """
        Confirm a validated trade
        """
        try:
            if trade_id not in self.trades:
                raise ValueError(f"Trade {trade_id} not found")
            
            trade = self.trades[trade_id]
            if trade["status"] != "validated":
                raise ValueError(f"Trade {trade_id} must be validated before confirmation")
            
            # Create confirmation
            confirmation = TradeConfirmation(
                trade_id=trade_id,
                confirmation_number=f"CONF_{uuid4().hex[:8]}",
                confirmation_date=datetime.utcnow(),
                confirmed_by=user_id,
                confirmation_notes=confirmation_notes
            )
            
            # Store confirmation
            self.confirmations[trade_id] = confirmation.model_dump()
            
            # Update trade status
            trade["status"] = "confirmed"
            trade["confirmed_at"] = datetime.utcnow()
            trade["updated_at"] = datetime.utcnow()
            
            # Publish trade confirmed event
            await publish_event(
                event_type=EventType.TRADE_CONFIRMED,
                payload={
                    "trade_id": trade_id,
                    "confirmation": confirmation.model_dump()
                },
                correlation_id=trade.get("correlation_id"),
                user_id=user_id,
                organization_id=trade.get("organization_id"),
                source_service="trade_lifecycle"
            )
            
            logger.info(f"Trade {trade_id} confirmed successfully")
            return confirmation
            
        except Exception as e:
            logger.error(f"Error confirming trade {trade_id}: {e}")
            raise
    
    async def allocate_trade(self, trade_id: str, user_id: str, allocation_data: Dict[str, Any]) -> TradeAllocation:
        """
        Allocate a confirmed trade
        """
        try:
            if trade_id not in self.trades:
                raise ValueError(f"Trade {trade_id} not found")
            
            trade = self.trades[trade_id]
            if trade["status"] != "confirmed":
                raise ValueError(f"Trade {trade_id} must be confirmed before allocation")
            
            # Create allocation
            allocation = TradeAllocation(
                trade_id=trade_id,
                allocation_date=datetime.utcnow(),
                allocated_quantity=allocation_data.get("allocated_quantity", trade["quantity"]),
                allocated_price=allocation_data.get("allocated_price", trade["price"]),
                allocation_notes=allocation_data.get("allocation_notes")
            )
            
            # Store allocation
            self.allocations[trade_id] = allocation.model_dump()
            
            # Update trade status
            trade["status"] = "allocated"
            trade["allocated_at"] = datetime.utcnow()
            trade["updated_at"] = datetime.utcnow()
            
            # Publish trade allocated event
            await publish_event(
                event_type=EventType.TRADE_ALLOCATED,
                payload={
                    "trade_id": trade_id,
                    "allocation": allocation.model_dump()
                },
                correlation_id=trade.get("correlation_id"),
                user_id=user_id,
                organization_id=trade.get("organization_id"),
                source_service="trade_lifecycle"
            )
            
            logger.info(f"Trade {trade_id} allocated successfully")
            return allocation
            
        except Exception as e:
            logger.error(f"Error allocating trade {trade_id}: {e}")
            raise
    
    async def settle_trade(self, trade_id: str, user_id: str, settlement_data: Dict[str, Any]) -> TradeSettlement:
        """
        Settle an allocated trade
        """
        try:
            if trade_id not in self.trades:
                raise ValueError(f"Trade {trade_id} not found")
            
            trade = self.trades[trade_id]
            if trade["status"] != "allocated":
                raise ValueError(f"Trade {trade_id} must be allocated before settlement")
            
            # Create settlement
            settlement = TradeSettlement(
                trade_id=trade_id,
                settlement_date=datetime.utcnow(),
                settlement_amount=settlement_data.get("settlement_amount", trade["quantity"] * trade["price"]),
                settlement_currency=settlement_data.get("settlement_currency", trade["currency"]),
                settlement_method=settlement_data.get("settlement_method", "bank_transfer"),
                settlement_notes=settlement_data.get("settlement_notes")
            )
            
            # Store settlement
            self.settlements[trade_id] = settlement.model_dump()
            
            # Update trade status
            trade["status"] = "settled"
            trade["settled_at"] = datetime.utcnow()
            trade["updated_at"] = datetime.utcnow()
            
            # Publish trade settled event
            await publish_event(
                event_type=EventType.TRADE_SETTLED,
                payload={
                    "trade_id": trade_id,
                    "settlement": settlement.model_dump()
                },
                correlation_id=trade.get("correlation_id"),
                user_id=user_id,
                organization_id=trade.get("organization_id"),
                source_service="trade_lifecycle"
            )
            
            logger.info(f"Trade {trade_id} settled successfully")
            return settlement
            
        except Exception as e:
            logger.error(f"Error settling trade {trade_id}: {e}")
            raise
    
    async def get_trade_status(self, trade_id: str) -> TradeStatusResponse:
        """
        Get current status of a trade
        """
        try:
            if trade_id not in self.trades:
                raise ValueError(f"Trade {trade_id} not found")
            
            trade = self.trades[trade_id]
            
            # Determine compliance status
            compliance_status = ComplianceStatus.APPROVED
            if trade["status"] == "failed":
                compliance_status = ComplianceStatus.REJECTED
            elif trade["status"] in ["captured", "validated"]:
                compliance_status = ComplianceStatus.PENDING
            
            return TradeStatusResponse(
                trade_id=trade_id,
                status=trade["status"],
                valid=trade["status"] not in ["failed", "cancelled"],
                compliant=trade.get("is_islamic_compliant", False),
                sharia_result={"compliant": trade.get("is_islamic_compliant", False), "restrictions": []},
                organization_id=trade.get("organization_id"),
                compliance_status=compliance_status
            )
            
        except Exception as e:
            logger.error(f"Error getting trade status for {trade_id}: {e}")
            raise
    
    async def get_user_trades(self, user_id: str, organization_id: str, page: int = 1, page_size: int = 50) -> TradeSearchResponse:
        """
        Get trades for a specific user and organization with pagination
        """
        try:
            # Filter trades by user and organization
            user_trades = [
                trade for trade in self.trade_history
                if trade.get("user_id") == user_id and str(trade.get("organization_id")) == str(organization_id)
            ]
            
            # Apply pagination
            total_count = len(user_trades)
            total_pages = (total_count + page_size - 1) // page_size
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            
            paginated_trades = user_trades[start_idx:end_idx]
            
            # Convert to TradeDetails
            trade_details = []
            for trade in paginated_trades:
                trade_detail = TradeDetails(
                    trade_id=trade["trade_id"],
                    trade_type=trade["trade_type"],
                    commodity=trade["commodity"],
                    quantity=trade["quantity"],
                    price=trade["price"],
                    currency=trade["currency"],
                    counterparty=trade["counterparty"],
                    delivery_date=trade["delivery_date"],
                    delivery_location=trade["delivery_location"],
                    status=trade["status"],
                    trade_direction=trade.get("trade_direction", "buy"),
                    settlement_type=trade.get("settlement_type", "T+2"),
                    organization_id=trade.get("organization_id"),
                    user_id=trade.get("user_id"),
                    is_islamic_compliant=trade.get("is_islamic_compliant", False),
                    compliance_status=ComplianceStatus.APPROVED if trade["status"] not in ["failed", "cancelled"] else ComplianceStatus.REJECTED,
                    risk_category=trade.get("risk_category"),
                    risk_score=trade.get("risk_score"),
                    created_at=trade["created_at"],
                    updated_at=trade["updated_at"],
                    captured_at=trade.get("captured_at"),
                    validated_at=trade.get("validated_at"),
                    confirmed_at=trade.get("confirmed_at"),
                    settled_at=trade.get("settled_at"),
                    additional_terms=trade.get("additional_terms", {}),
                    correlation_id=trade.get("correlation_id")
                )
                trade_details.append(trade_detail)
            
            # Create filter object
            filters = TradeFilter(
                organization_id=organization_id,
                user_id=user_id
            )
            
            return TradeSearchResponse(
                trades=trade_details,
                total_count=total_count,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
                filters_applied=filters
            )
            
        except Exception as e:
            logger.error(f"Error getting user trades for {user_id}: {e}")
            raise
    
    async def get_trade_analytics(self, organization_id: str, date_from: Optional[datetime] = None, date_to: Optional[datetime] = None) -> TradeAnalytics:
        """
        Get trade analytics for an organization
        """
        try:
            # Filter trades by organization and date range
            org_trades = [
                trade for trade in self.trade_history
                if str(trade.get("organization_id")) == str(organization_id)
            ]
            
            if date_from:
                org_trades = [t for t in org_trades if t["created_at"] >= date_from]
            if date_to:
                org_trades = [t for t in org_trades if t["created_at"] <= date_to]
            
            if not org_trades:
                return TradeAnalytics(
                    total_trades=0,
                    total_volume=0,
                    total_value=0,
                    average_price=0,
                    trade_count_by_type={},
                    trade_count_by_commodity={},
                    trade_count_by_status={},
                    compliance_rate=0,
                    islamic_compliance_rate=0,
                    risk_distribution={}
                )
            
            # Calculate analytics
            total_trades = len(org_trades)
            total_volume = sum(t.get("quantity", 0) for t in org_trades)
            total_value = sum(t.get("quantity", 0) * t.get("price", 0) for t in org_trades)
            average_price = total_value / total_volume if total_volume > 0 else 0
            
            # Count by type
            trade_count_by_type = {}
            for trade in org_trades:
                trade_type = trade.get("trade_type", "unknown")
                trade_count_by_type[trade_type] = trade_count_by_type.get(trade_type, 0) + 1
            
            # Count by commodity
            trade_count_by_commodity = {}
            for trade in org_trades:
                commodity = trade.get("commodity", "unknown")
                trade_count_by_commodity[commodity] = trade_count_by_commodity.get(commodity, 0) + 1
            
            # Count by status
            trade_count_by_status = {}
            for trade in org_trades:
                status = trade.get("status", "unknown")
                trade_count_by_status[status] = trade_count_by_status.get(status, 0) + 1
            
            # Compliance rates
            compliant_trades = [t for t in org_trades if t.get("status") not in ["failed", "cancelled"]]
            compliance_rate = len(compliant_trades) / total_trades if total_trades > 0 else 0
            
            islamic_trades = [t for t in org_trades if t.get("is_islamic_compliant", False)]
            islamic_compliance_rate = len(islamic_trades) / total_trades if total_trades > 0 else 0
            
            # Risk distribution
            risk_distribution = {}
            for trade in org_trades:
                risk_category = trade.get("risk_category") or "unknown"
                risk_distribution[risk_category] = risk_distribution.get(risk_category, 0) + 1
            
            return TradeAnalytics(
                total_trades=total_trades,
                total_volume=total_volume,
                total_value=total_value,
                average_price=average_price,
                trade_count_by_type=trade_count_by_type,
                trade_count_by_commodity=trade_count_by_commodity,
                trade_count_by_status=trade_count_by_status,
                compliance_rate=compliance_rate,
                islamic_compliance_rate=islamic_compliance_rate,
                risk_distribution=risk_distribution
            )
            
        except Exception as e:
            logger.error(f"Error getting trade analytics for organization {organization_id}: {e}")
            raise
    
    async def cancel_trade(self, trade_id: str, user_id: str, reason: str) -> TradeResponse:
        """
        Cancel a trade
        """
        try:
            if trade_id not in self.trades:
                raise ValueError(f"Trade {trade_id} not found")
            
            trade = self.trades[trade_id]
            if trade["status"] in ["settled", "paid"]:
                raise ValueError(f"Cannot cancel trade {trade_id} - already settled")
            
            # Update trade status
            trade["status"] = "cancelled"
            trade["cancelled_at"] = datetime.utcnow()
            trade["updated_at"] = datetime.utcnow()
            trade["cancellation_reason"] = reason
            trade["cancelled_by"] = user_id
            
            # Publish trade cancelled event
            await publish_event(
                event_type=EventType.TRADE_CANCELLED,
                payload={
                    "trade_id": trade_id,
                    "reason": reason,
                    "cancelled_by": user_id
                },
                correlation_id=trade.get("correlation_id"),
                user_id=user_id,
                organization_id=trade.get("organization_id"),
                source_service="trade_lifecycle"
            )
            
            logger.info(f"Trade {trade_id} cancelled successfully")
            
            return TradeResponse(
                trade_id=trade_id,
                status="cancelled",
                message=f"Trade cancelled: {reason}",
                timestamp=datetime.utcnow(),
                organization_id=trade.get("organization_id"),
                correlation_id=trade.get("correlation_id")
            )
            
        except Exception as e:
            logger.error(f"Error cancelling trade {trade_id}: {e}")
            raise

# Global service instance
enhanced_trade_service = EnhancedTradeLifecycleService()
