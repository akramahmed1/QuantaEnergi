"""
Settlement Management Service
ETRM/CTRM Automated Settlement, Clearing House Integration, Payment Processing
"""

from fastapi import HTTPException
from typing import Dict, List, Optional, Any
import asyncio
import logging
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib

logger = logging.getLogger(__name__)

class ClearingHouse(Enum):
    """Clearing house enumeration"""
    ICE = "ice"
    CME = "cme"
    LCH = "lch"
    EEX = "eex"
    NASDAQ = "nasdaq"

class SettlementStatus(Enum):
    """Settlement status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SETTLED = "settled"
    FAILED = "failed"
    CANCELLED = "cancelled"

class PaymentStatus(Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class ClearingHouseFactory:
    """Factory pattern for clearing house integrations"""
    
    @staticmethod
    def integrate_clearing(clearing_house: ClearingHouse, trade: Dict) -> Dict:
        """Integrate with specific clearing house"""
        try:
            if clearing_house == ClearingHouse.ICE:
                return ClearingHouseFactory._integrate_ice(trade)
            elif clearing_house == ClearingHouse.CME:
                return ClearingHouseFactory._integrate_cme(trade)
            elif clearing_house == ClearingHouse.LCH:
                return ClearingHouseFactory._integrate_lch(trade)
            elif clearing_house == ClearingHouse.EEX:
                return ClearingHouseFactory._integrate_eex(trade)
            elif clearing_house == ClearingHouse.NASDAQ:
                return ClearingHouseFactory._integrate_nasdaq(trade)
            else:
                raise ValueError(f"Unsupported clearing house: {clearing_house}")
        except Exception as e:
            logger.error(f"Clearing house integration failed: {str(e)}")
            raise
    
    @staticmethod
    def _integrate_ice(trade: Dict) -> Dict:
        """Integrate with ICE clearing"""
        return {
            "clearing_house": "ice",
            "clearing_id": f"ICE{hash(trade.get('trade_id', '')) % 1000000:06d}",
            "status": "cleared",
            "margin_requirement": trade.get("notional_amount", 0) * 0.05,
            "clearing_fee": trade.get("notional_amount", 0) * 0.001,
            "settlement_date": (datetime.utcnow() + timedelta(days=2)).isoformat(),
            "clearing_timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def _integrate_cme(trade: Dict) -> Dict:
        """Integrate with CME clearing"""
        return {
            "clearing_house": "CME",
            "clearing_id": f"CME{hash(trade.get('trade_id', '')) % 1000000:06d}",
            "status": "cleared",
            "margin_requirement": trade.get("notional_amount", 0) * 0.04,
            "clearing_fee": trade.get("notional_amount", 0) * 0.0008,
            "settlement_date": (datetime.utcnow() + timedelta(days=2)).isoformat(),
            "clearing_timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def _integrate_lch(trade: Dict) -> Dict:
        """Integrate with LCH clearing"""
        return {
            "clearing_house": "LCH",
            "clearing_id": f"LCH{hash(trade.get('trade_id', '')) % 1000000:06d}",
            "status": "cleared",
            "margin_requirement": trade.get("notional_amount", 0) * 0.06,
            "clearing_fee": trade.get("notional_amount", 0) * 0.0012,
            "settlement_date": (datetime.utcnow() + timedelta(days=2)).isoformat(),
            "clearing_timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def _integrate_eex(trade: Dict) -> Dict:
        """Integrate with EEX clearing"""
        return {
            "clearing_house": "EEX",
            "clearing_id": f"EEX{hash(trade.get('trade_id', '')) % 1000000:06d}",
            "status": "cleared",
            "margin_requirement": trade.get("notional_amount", 0) * 0.05,
            "clearing_fee": trade.get("notional_amount", 0) * 0.001,
            "settlement_date": (datetime.utcnow() + timedelta(days=2)).isoformat(),
            "clearing_timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def _integrate_nasdaq(trade: Dict) -> Dict:
        """Integrate with NASDAQ clearing"""
        return {
            "clearing_house": "NASDAQ",
            "clearing_id": f"NDQ{hash(trade.get('trade_id', '')) % 1000000:06d}",
            "status": "cleared",
            "margin_requirement": trade.get("notional_amount", 0) * 0.045,
            "clearing_fee": trade.get("notional_amount", 0) * 0.0009,
            "settlement_date": (datetime.utcnow() + timedelta(days=2)).isoformat(),
            "clearing_timestamp": datetime.utcnow().isoformat()
        }

class SettlementManagement:
    """Settlement management with clearing house integration and payment processing"""
    
    def __init__(self):
        self.settlements = {}
        self.payments = {}
        self.clearing_records = {}
        self.factory = ClearingHouseFactory()
    
    async def automate_settlement(self, trade_id: str, settlement_data: Dict) -> Dict:
        """Automate settlement process for a trade"""
        try:
            if not settlement_data.get("organization_id"):
                raise ValueError("Organization ID is required")
            
            if not settlement_data.get("counterparty_id"):
                raise ValueError("Counterparty ID is required")
            
            settlement_id = str(uuid4())
            
            # Calculate settlement amounts
            notional_amount = settlement_data.get("notional_amount", 0)
            settlement_fee = notional_amount * 0.001  # 0.1% settlement fee
            net_amount = notional_amount - settlement_fee
            
            settlement_record = {
                "settlement_id": settlement_id,
                "trade_id": trade_id,
                "organization_id": settlement_data["organization_id"],
                "counterparty_id": settlement_data["counterparty_id"],
                "status": SettlementStatus.PENDING.value,
                "notional_amount": notional_amount,
                "settlement_fee": settlement_fee,
                "net_amount": net_amount,
                "currency": settlement_data.get("currency", "USD"),
                "settlement_date": settlement_data.get("settlement_date"),
                "created_at": datetime.utcnow().isoformat(),
                "created_by": settlement_data.get("created_by", "system"),
                "settlement_type": settlement_data.get("settlement_type", "t+2"),
                "payment_method": settlement_data.get("payment_method", "wire_transfer")
            }
            
            self.settlements[settlement_id] = settlement_record
            
            # Start settlement workflow
            await self._execute_settlement_workflow(settlement_id)
            
            logger.info(f"Settlement {settlement_id} created for trade {trade_id}")
            return settlement_record
            
        except ValueError as e:
            logger.error(f"Settlement validation error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Settlement automation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Settlement automation failed: {str(e)}")
    
    async def _execute_settlement_workflow(self, settlement_id: str):
        """Execute settlement workflow steps"""
        try:
            settlement = self.settlements[settlement_id]
            
            # Step 1: Validate settlement
            settlement["status"] = SettlementStatus.IN_PROGRESS.value
            settlement["workflow_steps"] = [
                {"step": "validation", "status": "completed", "timestamp": datetime.utcnow().isoformat()}
            ]
            
            # Step 2: Calculate final amounts
            await asyncio.sleep(0.1)  # Simulate processing time
            settlement["workflow_steps"].append({
                "step": "calculation", 
                "status": "completed", 
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Step 3: Generate settlement instructions
            await asyncio.sleep(0.1)
            settlement["workflow_steps"].append({
                "step": "instructions", 
                "status": "completed", 
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Step 4: Complete settlement
            settlement["status"] = SettlementStatus.SETTLED.value
            settlement["settled_at"] = datetime.utcnow().isoformat()
            settlement["workflow_steps"].append({
                "step": "settlement", 
                "status": "completed", 
                "timestamp": datetime.utcnow().isoformat()
            })
            
            logger.info(f"Settlement workflow completed for {settlement_id}")
            
        except Exception as e:
            logger.error(f"Settlement workflow failed for {settlement_id}: {str(e)}")
            if settlement_id in self.settlements:
                self.settlements[settlement_id]["status"] = SettlementStatus.FAILED.value
                self.settlements[settlement_id]["error"] = str(e)
    
    async def integrate_clearing(self, trade_id: str, clearing_house: str, trade_data: Dict) -> Dict:
        """Integrate with clearing house for trade clearing"""
        try:
            if not trade_data.get("notional_amount"):
                raise ValueError("Notional amount is required for clearing")
            
            # Validate clearing house
            try:
                clearing_house_enum = ClearingHouse(clearing_house)
            except ValueError:
                raise ValueError(f"Invalid clearing house: {clearing_house}")
            
            # Integrate with clearing house using factory
            clearing_result = self.factory.integrate_clearing(clearing_house_enum, trade_data)
            
            # Store clearing record
            clearing_id = str(uuid4())
            clearing_record = {
                "clearing_id": clearing_id,
                "trade_id": trade_id,
                "clearing_house": clearing_house,
                "clearing_result": clearing_result,
                "created_at": datetime.utcnow().isoformat(),
                "status": "active"
            }
            
            self.clearing_records[clearing_id] = clearing_record
            
            logger.info(f"Clearing integration completed for trade {trade_id} with {clearing_house}")
            return clearing_record
            
        except ValueError as e:
            logger.error(f"Clearing integration validation error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Clearing integration failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Clearing integration failed: {str(e)}")
    
    async def process_payment(self, settlement_id: str, payment_data: Dict) -> Dict:
        """Process payment for settlement"""
        try:
            if settlement_id not in self.settlements:
                raise ValueError(f"Settlement {settlement_id} not found")
            
            settlement = self.settlements[settlement_id]
            
            if settlement["status"] != SettlementStatus.SETTLED.value:
                raise ValueError("Settlement must be completed before payment processing")
            
            payment_id = str(uuid4())
            
            # Create payment record
            payment_record = {
                "payment_id": payment_id,
                "settlement_id": settlement_id,
                "amount": settlement["net_amount"],
                "currency": settlement["currency"],
                "status": PaymentStatus.PENDING.value,
                "payment_method": settlement.get("payment_method", "wire_transfer"),
                "recipient_account": payment_data.get("recipient_account"),
                "sender_account": payment_data.get("sender_account"),
                "created_at": datetime.utcnow().isoformat(),
                "created_by": payment_data.get("created_by", "system")
            }
            
            self.payments[payment_id] = payment_record
            
            # Process payment
            await self._execute_payment_workflow(payment_id)
            
            logger.info(f"Payment {payment_id} processed for settlement {settlement_id}")
            return payment_record
            
        except ValueError as e:
            logger.error(f"Payment validation error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Payment processing failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Payment processing failed: {str(e)}")
    
    async def _execute_payment_workflow(self, payment_id: str):
        """Execute payment workflow"""
        try:
            payment = self.payments[payment_id]
            
            # Step 1: Validate payment details
            payment["status"] = PaymentStatus.PROCESSING.value
            payment["workflow_steps"] = [
                {"step": "validation", "status": "completed", "timestamp": datetime.utcnow().isoformat()}
            ]
            
            # Step 2: Process payment (simulate bank processing)
            await asyncio.sleep(0.2)  # Simulate processing time
            payment["workflow_steps"].append({
                "step": "bank_processing", 
                "status": "completed", 
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Step 3: Confirm payment
            payment["status"] = PaymentStatus.COMPLETED.value
            payment["completed_at"] = datetime.utcnow().isoformat()
            payment["workflow_steps"].append({
                "step": "confirmation", 
                "status": "completed", 
                "timestamp": datetime.utcnow().isoformat()
            })
            
            logger.info(f"Payment workflow completed for {payment_id}")
            
        except Exception as e:
            logger.error(f"Payment workflow failed for {payment_id}: {str(e)}")
            if payment_id in self.payments:
                self.payments[payment_id]["status"] = PaymentStatus.FAILED.value
                self.payments[payment_id]["error"] = str(e)
    
    async def get_settlement_analytics(self, organization_id: str) -> Dict:
        """Get settlement analytics and performance metrics"""
        try:
            # Filter settlements by organization
            org_settlements = [
                s for s in self.settlements.values() 
                if s.get("organization_id") == organization_id
            ]
            
            # Calculate analytics
            total_settlements = len(org_settlements)
            settled_count = len([s for s in org_settlements if s.get("status") == SettlementStatus.SETTLED.value])
            failed_count = len([s for s in org_settlements if s.get("status") == SettlementStatus.FAILED.value])
            
            # Payment analytics
            org_payments = [
                p for p in self.payments.values() 
                if p.get("settlement_id") in [s["settlement_id"] for s in org_settlements]
            ]
            
            completed_payments = len([p for p in org_payments if p.get("status") == PaymentStatus.COMPLETED.value])
            
            # Financial metrics
            total_notional = sum(s.get("notional_amount", 0) for s in org_settlements)
            total_fees = sum(s.get("settlement_fee", 0) for s in org_settlements)
            
            analytics = {
                "total_settlements": total_settlements,
                "settled_settlements": settled_count,
                "failed_settlements": failed_count,
                "settlement_success_rate": settled_count / max(total_settlements, 1),
                "total_payments": len(org_payments),
                "completed_payments": completed_payments,
                "payment_success_rate": completed_payments / max(len(org_payments), 1),
                "total_notional_amount": total_notional,
                "total_settlement_fees": total_fees,
                "average_settlement_amount": total_notional / max(total_settlements, 1),
                "average_settlement_fee": total_fees / max(total_settlements, 1)
            }
            
            logger.info(f"Settlement analytics generated for organization {organization_id}")
            return analytics
            
        except Exception as e:
            logger.error(f"Settlement analytics generation failed for {organization_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Settlement analytics generation failed: {str(e)}")
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            logger.info("Settlement management cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")
