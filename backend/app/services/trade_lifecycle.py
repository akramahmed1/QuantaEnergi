"""
Trade Lifecycle Service for ETRM/CTRM Trading
Handles complete trade lifecycle from capture to settlement
"""

from fastapi import HTTPException
from typing import Dict, List, Optional, Any
import asyncio
import logging
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class TradeStage(Enum):
    """Trade lifecycle stages"""
    CAPTURE = "capture"
    VALIDATION = "validation"
    CONFIRMATION = "confirmation"
    ALLOCATION = "allocation"
    SETTLEMENT = "settlement"
    INVOICING = "invoicing"
    PAYMENT = "payment"
    COMPLETED = "completed"

class TradeLifecycle:
    """Service for managing complete trade lifecycle"""
    
    def __init__(self):
        self.trades = {}  # In-memory storage for stubs
        self.trade_counter = 1000
        
    async def capture_trade(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Capture a new trade in the system
        
        Args:
            trade_data: Trade information including parties, commodity, terms
            
        Returns:
            Dict with captured trade details and ID
        """
        try:
            # Generate unique trade ID
            trade_id = str(uuid4())
            self.trade_counter += 1
            
            # Validate required fields
            required_fields = ["parties", "commodity", "quantity", "price", "delivery_date"]
            for field in required_fields:
                if field not in trade_data or not trade_data[field]:
                    raise HTTPException(status_code=400, detail=f"Required field '{field}' is missing")
            
            # Create trade record
            trade_record = {
                "trade_id": trade_id,
                "status": TradeStage.CAPTURE.value,
                "stages": [TradeStage.CAPTURE.value],
                "captured_at": datetime.now().isoformat(),
                "parties": trade_data["parties"],
                "commodity": trade_data["commodity"],
                "quantity": trade_data["quantity"],
                "price": trade_data["price"],
                "currency": trade_data.get("currency", "USD"),
                "delivery_date": trade_data["delivery_date"],
                "trade_type": trade_data.get("trade_type", "spot"),
                "delivery_location": trade_data.get("delivery_location"),
                "transport_mode": trade_data.get("transport_mode"),
                "storage_facility": trade_data.get("storage_facility"),
                "sharia_compliant": trade_data.get("sharia_compliant", False),
                "contract_terms": trade_data.get("contract_terms", {}),
                "risk_metrics": self._calculate_trade_risk(trade_data)
            }
            
            self.trades[trade_id] = trade_record
            
            logger.info(f"Trade captured successfully: {trade_id}")
            
            return trade_id
            
        except Exception as e:
            logger.error(f"Trade capture failed: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def validate_trade(self, trade_id: str) -> Dict[str, Any]:
        """
        Validate trade data and business rules
        
        Args:
            trade_id: Unique trade identifier
            
        Returns:
            Dict with validation results
        """
        try:
            if trade_id not in self.trades:
                raise HTTPException(status_code=404, detail="Trade not found")
            
            trade = self.trades[trade_id]
            
            # Business rule validation
            validation_results = {
                "quantity_valid": trade["quantity"] > 0,
                "price_valid": trade["price"] > 0,
                "delivery_date_valid": self._validate_delivery_date(trade["delivery_date"]),
                "parties_valid": len(trade["parties"]) >= 2,
                "commodity_valid": trade["commodity"] in ["crude_oil", "natural_gas", "electricity", "coal", "renewables"]
            }
            
            is_valid = all(validation_results.values())
            
            if is_valid:
                trade["status"] = TradeStage.VALIDATION.value
                trade["stages"].append(TradeStage.VALIDATION.value)
                trade["validated_at"] = datetime.now().isoformat()
            
            return {
                "success": True,
                "valid": is_valid,
                "validation_results": validation_results,
                "trade": trade
            }
            
        except Exception as e:
            logger.error(f"Trade validation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def generate_confirmation(self, trade_id: str) -> Dict[str, Any]:
        """
        Generate trade confirmation document
        
        Args:
            trade_id: Unique trade identifier
            
        Returns:
            Dict with confirmation details
        """
        try:
            if trade_id not in self.trades:
                raise HTTPException(status_code=404, detail="Trade not found")
            
            trade = self.trades[trade_id]
            
            # Generate confirmation document
            confirmation = {
                "confirmation_id": f"CONF-{self.trade_counter:06d}",
                "trade_id": trade_id,
                "generated_at": datetime.now().isoformat(),
                "parties": trade["parties"],
                "commodity": trade["commodity"],
                "quantity": trade["quantity"],
                "price": trade["price"],
                "delivery_date": trade["delivery_date"],
                "total_value": trade["quantity"] * trade["price"],
                "status": "confirmed"
            }
            
            trade["status"] = TradeStage.CONFIRMATION.value
            trade["stages"].append(TradeStage.CONFIRMATION.value)
            trade["confirmation"] = confirmation
            trade["confirmed_at"] = datetime.now().isoformat()
            
            logger.info(f"Trade confirmation generated: {confirmation['confirmation_id']}")
            
            return {
                "success": True,
                "confirmation": confirmation,
                "trade": trade
            }
            
        except Exception as e:
            logger.error(f"Confirmation generation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def allocate_trade(self, trade_id: str, allocation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Allocate trade to specific delivery schedules and locations
        
        Args:
            trade_id: Unique trade identifier
            allocation_data: Allocation information including delivery schedules
            
        Returns:
            Dict with allocation details
        """
        try:
            if trade_id not in self.trades:
                raise HTTPException(status_code=404, detail="Trade not found")
            
            trade = self.trades[trade_id]
            
            # Create allocation record
            allocation = {
                "allocation_id": f"ALLOC-{self.trade_counter:06d}",
                "trade_id": trade_id,
                "allocated_at": datetime.now().isoformat(),
                "delivery_schedules": allocation_data.get("delivery_schedules", []),
                "storage_locations": allocation_data.get("storage_locations", []),
                "transport_routes": allocation_data.get("transport_routes", []),
                "status": "allocated"
            }
            
            trade["status"] = TradeStage.ALLOCATION.value
            trade["stages"].append(TradeStage.ALLOCATION.value)
            trade["allocation"] = allocation
            trade["allocated_at"] = datetime.now().isoformat()
            
            return {
                "success": True,
                "allocation": allocation,
                "trade": trade
            }
            
        except Exception as e:
            logger.error(f"Trade allocation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def process_settlement(self, trade_id: str, settlement_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process trade settlement including delivery confirmation and payment
        
        Args:
            trade_id: Unique trade identifier
            settlement_data: Settlement information including delivery confirmation
            
        Returns:
            Dict with settlement details
        """
        try:
            if trade_id not in self.trades:
                raise HTTPException(status_code=404, detail="Trade not found")
            
            trade = self.trades[trade_id]
            
            # Create settlement record
            settlement = {
                "settlement_id": f"SETTLE-{self.trade_counter:06d}",
                "trade_id": trade_id,
                "settled_at": datetime.now().isoformat(),
                "delivery_confirmed": settlement_data.get("delivery_confirmed", False),
                "delivery_date": settlement_data.get("actual_delivery_date"),
                "quantity_delivered": settlement_data.get("quantity_delivered", trade["quantity"]),
                "quality_specifications": settlement_data.get("quality_specifications", {}),
                "payment_terms": settlement_data.get("payment_terms", "net_30"),
                "status": "settled"
            }
            
            trade["status"] = TradeStage.SETTLEMENT.value
            trade["stages"].append(TradeStage.SETTLEMENT.value)
            trade["settlement"] = settlement
            trade["settled_at"] = datetime.now().isoformat()
            
            return {
                "success": True,
                "settlement": settlement,
                "trade": trade
            }
            
        except Exception as e:
            logger.error(f"Settlement processing failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def generate_invoice(self, trade_id: str) -> Dict[str, Any]:
        """
        Generate invoice for completed trade
        
        Args:
            trade_id: Unique trade identifier
            
        Returns:
            Dict with invoice details
        """
        try:
            if trade_id not in self.trades:
                raise HTTPException(status_code=404, detail="Trade not found")
            
            trade = self.trades[trade_id]
            
            # Generate invoice
            invoice = {
                "invoice_id": f"INV-{self.trade_counter:06d}",
                "trade_id": trade_id,
                "generated_at": datetime.now().isoformat(),
                "due_date": (datetime.now() + timedelta(days=30)).isoformat(),
                "line_items": [
                    {
                        "description": f"{trade['commodity']} - {trade['quantity']} units",
                        "quantity": trade["quantity"],
                        "unit_price": trade["price"],
                        "total": trade["quantity"] * trade["price"]
                    }
                ],
                "subtotal": trade["quantity"] * trade["price"],
                "taxes": 0.0,  # TODO: Calculate applicable taxes
                "total_amount": trade["quantity"] * trade["price"],
                "currency": trade["currency"],
                "status": "generated"
            }
            
            trade["status"] = TradeStage.INVOICING.value
            trade["stages"].append(TradeStage.INVOICING.value)
            trade["invoice"] = invoice
            trade["invoiced_at"] = datetime.now().isoformat()
            
            return {
                "success": True,
                "invoice": invoice,
                "trade": trade
            }
            
        except Exception as e:
            logger.error(f"Invoice generation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def process_payment(self, trade_id: str, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process payment for trade invoice
        
        Args:
            trade_id: Unique trade identifier
            payment_data: Payment information including amount and method
            
        Returns:
            Dict with payment details
        """
        try:
            if trade_id not in self.trades:
                raise HTTPException(status_code=404, detail="Trade not found")
            
            trade = self.trades[trade_id]
            
            # Create payment record
            payment = {
                "payment_id": f"PAY-{self.trade_counter:06d}",
                "trade_id": trade_id,
                "processed_at": datetime.now().isoformat(),
                "amount": payment_data.get("amount", trade["quantity"] * trade["price"]),
                "payment_method": payment_data.get("payment_method", "wire_transfer"),
                "reference_number": payment_data.get("reference_number"),
                "status": "processed"
            }
            
            trade["status"] = TradeStage.PAYMENT.value
            trade["stages"].append(TradeStage.PAYMENT.value)
            trade["payment"] = payment
            trade["paid_at"] = datetime.now().isoformat()
            
            # Mark trade as completed
            trade["status"] = TradeStage.COMPLETED.value
            trade["stages"].append(TradeStage.COMPLETED.value)
            trade["completed_at"] = datetime.now().isoformat()
            
            return {
                "success": True,
                "payment": payment,
                "trade": trade
            }
            
        except Exception as e:
            logger.error(f"Payment processing failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_trade_status(self, trade_id: str) -> Dict[str, Any]:
        """
        Get current status of trade
        
        Args:
            trade_id: Unique trade identifier
            
        Returns:
            Dict with trade status and current stage
        """
        try:
            if trade_id not in self.trades:
                raise HTTPException(status_code=404, detail="Trade not found")
            
            trade = self.trades[trade_id]
            
            return {
                "success": True,
                "trade_id": trade_id,
                "current_stage": trade["status"],
                "stages_completed": trade["stages"],
                "trade": trade
            }
            
        except Exception as e:
            logger.error(f"Trade status retrieval failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def _calculate_trade_risk(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate basic risk metrics for trade"""
        quantity = trade_data.get("quantity", 0)
        price = trade_data.get("price", 0.0)
        notional_value = quantity * price
        
        return {
            "notional_value": notional_value,
            "max_loss": notional_value * 0.1,  # 10% max loss stub
            "risk_level": "high" if notional_value > 5000000 else "medium" if notional_value > 1000000 else "low"
        }
    
    def _validate_delivery_date(self, delivery_date) -> bool:
        """Validate delivery date is in the future"""
        try:
            if isinstance(delivery_date, str):
                delivery_dt = datetime.fromisoformat(delivery_date)
            elif isinstance(delivery_date, datetime):
                delivery_dt = delivery_date
            else:
                return False
            return delivery_dt > datetime.now()
        except (ValueError, TypeError):
            return False
