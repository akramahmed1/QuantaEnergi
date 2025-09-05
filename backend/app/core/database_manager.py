"""
Multi-Tenant Database Manager for ETRM/CTRM Operations
Handles organization isolation, async operations, and comprehensive error handling
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Type, TypeVar
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, status

from app.models.organization import Organization
from app.models.trade import Trade, TradeAllocation, TradeSettlement

logger = logging.getLogger(__name__)

T = TypeVar('T')

class MultiTenantDBManager:
    """Async database manager with multi-tenant support and organization isolation"""
    
    def __init__(self):
        self.connection_pool = {}
        self.query_cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def get_trades_for_org(self, session: AsyncSession, org_id: UUID, 
                                limit: int = 100, offset: int = 0) -> List[Trade]:
        """
        Get trades for specific organization with pagination
        
        Args:
            session: Async database session
            org_id: Organization UUID
            limit: Maximum number of trades to return
            offset: Number of trades to skip
            
        Returns:
            List of Trade objects for the organization
            
        Raises:
            HTTPException: If database query fails
        """
        try:
            stmt = (
                select(Trade)
                .where(Trade.organization_id == org_id)
                .where(Trade.is_deleted == False)
                .order_by(Trade.created_at.desc())
                .limit(limit)
                .offset(offset)
                .options(selectinload(Trade.organization))
            )
            
            result = await session.execute(stmt)
            trades = result.scalars().all()
            
            logger.info(f"Retrieved {len(trades)} trades for organization {org_id}")
            return trades
            
        except SQLAlchemyError as e:
            logger.error(f"Database query failed for organization {org_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve trades"
            )
        except Exception as e:
            logger.error(f"Unexpected error retrieving trades: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    async def add_trade(self, session: AsyncSession, trade_data: Dict[str, Any], 
                       org_id: UUID, user_id: str) -> Trade:
        """
        Add new trade to database with organization isolation
        
        Args:
            session: Async database session
            trade_data: Trade data dictionary
            org_id: Organization UUID
            user_id: User ID creating the trade
            
        Returns:
            Created Trade object
            
        Raises:
            HTTPException: If trade creation fails
        """
        try:
            # Generate unique trade ID
            trade_id = f"TRD-{datetime.now().strftime('%Y%m%d')}-{org_id.hex[:8]}-{int(datetime.now().timestamp())}"
            
            # Create trade object
            trade = Trade(
                organization_id=org_id,
                trade_id=trade_id,
                trade_type=trade_data.get("trade_type", "spot"),
                commodity=trade_data.get("commodity"),
                quantity=trade_data.get("quantity"),
                price=trade_data.get("price"),
                currency=trade_data.get("currency", "USD"),
                counterparty_id=trade_data.get("counterparty_id"),
                counterparty_name=trade_data.get("counterparty_name"),
                delivery_date=trade_data.get("delivery_date"),
                delivery_location=trade_data.get("delivery_location"),
                trade_direction=trade_data.get("trade_direction", "buy"),
                settlement_type=trade_data.get("settlement_type", "T+2"),
                is_islamic_compliant=trade_data.get("is_islamic_compliant", False),
                risk_category=trade_data.get("risk_category"),
                notional_value=trade_data.get("quantity", 0) * trade_data.get("price", 0),
                trade_data=trade_data.get("additional_data"),
                created_by=user_id
            )
            
            session.add(trade)
            await session.commit()
            await session.refresh(trade)
            
            logger.info(f"Created trade {trade_id} for organization {org_id}")
            return trade
            
        except IntegrityError as e:
            await session.rollback()
            logger.error(f"Integrity error creating trade: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Trade data validation failed"
            )
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Database error creating trade: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create trade"
            )
        except Exception as e:
            await session.rollback()
            logger.error(f"Unexpected error creating trade: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    async def update_trade_status(self, session: AsyncSession, trade_id: str, 
                                 org_id: UUID, new_status: str, user_id: str) -> Trade:
        """
        Update trade status with organization isolation
        
        Args:
            session: Async database session
            trade_id: Trade ID to update
            org_id: Organization UUID
            new_status: New status value
            user_id: User ID making the update
            
        Returns:
            Updated Trade object
            
        Raises:
            HTTPException: If trade update fails
        """
        try:
            stmt = (
                select(Trade)
                .where(Trade.trade_id == trade_id)
                .where(Trade.organization_id == org_id)
                .where(Trade.is_deleted == False)
            )
            
            result = await session.execute(stmt)
            trade = result.scalar_one_or_none()
            
            if not trade:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Trade not found"
                )
            
            trade.status = new_status
            trade.updated_at = datetime.utcnow()
            trade.updated_by = user_id
            
            await session.commit()
            await session.refresh(trade)
            
            logger.info(f"Updated trade {trade_id} status to {new_status}")
            return trade
            
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Database error updating trade: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update trade"
            )
        except Exception as e:
            await session.rollback()
            logger.error(f"Unexpected error updating trade: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    async def get_organization_by_id(self, session: AsyncSession, org_id: UUID) -> Optional[Organization]:
        """
        Get organization by ID
        
        Args:
            session: Async database session
            org_id: Organization UUID
            
        Returns:
            Organization object or None if not found
        """
        try:
            stmt = select(Organization).where(Organization.id == org_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
            
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving organization {org_id}: {str(e)}")
            return None
    
    async def get_trade_analytics(self, session: AsyncSession, org_id: UUID, 
                                 start_date: Optional[datetime] = None,
                                 end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get trade analytics for organization
        
        Args:
            session: Async database session
            org_id: Organization UUID
            start_date: Start date for analytics (optional)
            end_date: End date for analytics (optional)
            
        Returns:
            Dictionary with trade analytics
        """
        try:
            # Base query for organization trades
            stmt = (
                select(Trade)
                .where(Trade.organization_id == org_id)
                .where(Trade.is_deleted == False)
            )
            
            # Add date filters if provided
            if start_date:
                stmt = stmt.where(Trade.created_at >= start_date)
            if end_date:
                stmt = stmt.where(Trade.created_at <= end_date)
            
            result = await session.execute(stmt)
            trades = result.scalars().all()
            
            # Calculate analytics
            total_trades = len(trades)
            total_notional = sum(trade.notional_value for trade in trades)
            total_quantity = sum(trade.quantity for trade in trades)
            
            # Status distribution
            status_counts = {}
            for trade in trades:
                status_counts[trade.status] = status_counts.get(trade.status, 0) + 1
            
            # Commodity distribution
            commodity_counts = {}
            for trade in trades:
                commodity_counts[trade.commodity] = commodity_counts.get(trade.commodity, 0) + 1
            
            # Islamic compliance stats
            islamic_trades = len([t for t in trades if t.is_islamic_compliant])
            
            analytics = {
                "total_trades": total_trades,
                "total_notional_value": total_notional,
                "total_quantity": total_quantity,
                "average_trade_value": total_notional / max(total_trades, 1),
                "status_distribution": status_counts,
                "commodity_distribution": commodity_counts,
                "islamic_compliant_trades": islamic_trades,
                "islamic_compliance_rate": islamic_trades / max(total_trades, 1),
                "period_start": start_date.isoformat() if start_date else None,
                "period_end": end_date.isoformat() if end_date else None,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Generated analytics for organization {org_id}: {total_trades} trades")
            return analytics
            
        except SQLAlchemyError as e:
            logger.error(f"Database error generating analytics: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate analytics"
            )
        except Exception as e:
            logger.error(f"Unexpected error generating analytics: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    async def soft_delete_trade(self, session: AsyncSession, trade_id: str, 
                               org_id: UUID, user_id: str) -> bool:
        """
        Soft delete trade with organization isolation
        
        Args:
            session: Async database session
            trade_id: Trade ID to delete
            org_id: Organization UUID
            user_id: User ID performing deletion
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            stmt = (
                select(Trade)
                .where(Trade.trade_id == trade_id)
                .where(Trade.organization_id == org_id)
                .where(Trade.is_deleted == False)
            )
            
            result = await session.execute(stmt)
            trade = result.scalar_one_or_none()
            
            if not trade:
                return False
            
            trade.is_deleted = True
            trade.deleted_at = datetime.utcnow()
            trade.deleted_by = user_id
            trade.updated_at = datetime.utcnow()
            trade.updated_by = user_id
            
            await session.commit()
            
            logger.info(f"Soft deleted trade {trade_id} for organization {org_id}")
            return True
            
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Database error deleting trade: {str(e)}")
            return False
        except Exception as e:
            await session.rollback()
            logger.error(f"Unexpected error deleting trade: {str(e)}")
            return False
