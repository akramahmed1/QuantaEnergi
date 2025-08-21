import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import json

class SettlementService:
    """Comprehensive settlement and clearing service for ETRM/CTRM"""
    
    def __init__(self):
        # Regional clearing houses and payment methods
        self.clearing_houses = {
            "ME": {
                "ADX_Clearing": "Abu Dhabi Securities Exchange Clearing",
                "DFM_Clearing": "Dubai Financial Market Clearing",
                "Saudi_Clearing": "Saudi Clearing Company",
                "Qatar_Clearing": "Qatar Central Securities Depository"
            },
            "US": {
                "DTCC": "Depository Trust & Clearing Corporation",
                "CME_Clearing": "CME Clearing",
                "ICE_Clearing": "ICE Clear",
                "LCH": "LCH Clearnet"
            },
            "UK": {
                "LCH": "LCH Clearnet",
                "CCP_Global": "CCP Global",
                "ICE_Clear_UK": "ICE Clear UK"
            },
            "EU": {
                "Eurex_Clearing": "Eurex Clearing",
                "LCH_Clearnet": "LCH Clearnet",
                "CCP_Global": "CCP Global",
                "OMI_Clear": "OMI Clear"
            },
            "GUYANA": {
                "Local_Clearing": "Guyana Central Securities Depository",
                "Regional_Clearing": "Caribbean Central Securities Depository"
            }
        }
        
        # Payment methods by region
        self.payment_methods = {
            "ME": ["bank_transfer", "local_currency", "USD", "AED", "SAR"],
            "US": ["ACH", "wire_transfer", "check", "USD"],
            "UK": ["CHAPS", "BACS", "wire_transfer", "GBP", "EUR"],
            "EU": ["SEPA", "wire_transfer", "EUR", "local_currencies"],
            "GUYANA": ["bank_transfer", "local_currency", "USD", "GYD"]
        }
        
        # Settlement cycles by region
        self.settlement_cycles = {
            "ME": "T+2",  # Trade date + 2 business days
            "US": "T+2",
            "UK": "T+2",
            "EU": "T+2",
            "GUYANA": "T+3"  # Longer cycle for developing markets
        }
    
    async def create_settlement(
        self,
        trade_id: str,
        settlement_amount: Decimal,
        settlement_currency: str,
        counterparty_id: int,
        region: str,
        payment_method: str,
        clearing_house: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new settlement record"""
        
        # Validate settlement parameters
        validation = await self._validate_settlement(
            settlement_amount, settlement_currency, region, payment_method
        )
        
        if not validation["valid"]:
            return {
                "status": "rejected",
                "settlement_id": None,
                "errors": validation["errors"]
            }
        
        # Generate settlement ID
        settlement_id = f"SET-{region}-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
        
        # Calculate settlement date based on regional cycle
        settlement_date = self._calculate_settlement_date(region)
        
        # Create settlement object
        settlement = {
            "settlement_id": settlement_id,
            "trade_id": trade_id,
            "settlement_amount": float(settlement_amount),
            "settlement_currency": settlement_currency,
            "counterparty_id": counterparty_id,
            "region": region,
            "payment_method": payment_method,
            "clearing_house": clearing_house or self._get_default_clearing_house(region),
            "settlement_date": settlement_date,
            "status": "pending",
            "created_at": datetime.now(),
            "processed_at": None,
            "confirmation_number": None,
            "settlement_instructions": self._generate_settlement_instructions(
                region, payment_method, clearing_house
            )
        }
        
        return {
            "status": "created",
            "settlement_id": settlement_id,
            "settlement_details": settlement
        }
    
    async def process_settlement(
        self,
        settlement_id: str,
        force_settlement: bool = False
    ) -> Dict[str, Any]:
        """Process a pending settlement"""
        
        # Mock settlement processing - in production, integrate with clearing houses
        await asyncio.sleep(0.5)  # Simulate processing time
        
        # Simulate settlement success/failure
        success_rate = 0.95  # 95% success rate
        is_successful = force_settlement or (hash(settlement_id) % 100 < int(success_rate * 100))
        
        if is_successful:
            confirmation_number = f"CONF-{uuid.uuid4().hex[:12]}"
            
            return {
                "status": "completed",
                "settlement_id": settlement_id,
                "confirmation_number": confirmation_number,
                "processed_at": datetime.now(),
                "message": "Settlement processed successfully"
            }
        else:
            return {
                "status": "failed",
                "settlement_id": settlement_id,
                "error_code": "INSUFFICIENT_FUNDS",
                "error_message": "Insufficient funds for settlement",
                "processed_at": datetime.now()
            }
    
    async def get_settlement_status(
        self,
        settlement_id: str
    ) -> Dict[str, Any]:
        """Get current status of a settlement"""
        
        # Mock settlement status - in production, query clearing house or database
        await asyncio.sleep(0.05)
        
        # Simulate different settlement statuses
        statuses = ["pending", "processing", "completed", "failed", "cancelled"]
        current_status = statuses[hash(settlement_id) % len(statuses)]
        
        settlement_status = {
            "settlement_id": settlement_id,
            "status": current_status,
            "created_at": datetime.now() - timedelta(hours=4),
            "last_updated": datetime.now(),
            "settlement_date": datetime.now() + timedelta(days=2),
            "confirmation_number": f"CONF-{uuid.uuid4().hex[:12]}" if current_status == "completed" else None
        }
        
        return settlement_status
    
    async def batch_settle_trades(
        self,
        trade_ids: List[str],
        region: str,
        settlement_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Batch settle multiple trades"""
        
        if not trade_ids:
            return {
                "status": "error",
                "message": "No trade IDs provided"
            }
        
        # Mock batch settlement - in production, integrate with clearing houses
        await asyncio.sleep(1.0)  # Simulate batch processing time
        
        settlements = []
        successful_count = 0
        failed_count = 0
        
        for trade_id in trade_ids:
            # Create settlement for each trade
            settlement = await self.create_settlement(
                trade_id=trade_id,
                settlement_amount=Decimal("10000.00"),  # Mock amount
                settlement_currency="USD",
                counterparty_id=1,  # Mock counterparty
                region=region,
                payment_method="wire_transfer"
            )
            
            if settlement["status"] == "created":
                # Process settlement
                result = await self.process_settlement(settlement["settlement_id"])
                if result["status"] == "completed":
                    successful_count += 1
                else:
                    failed_count += 1
                
                settlements.append({
                    "trade_id": trade_id,
                    "settlement_id": settlement["settlement_id"],
                    "result": result
                })
        
        return {
            "status": "completed",
            "total_trades": len(trade_ids),
            "successful_settlements": successful_count,
            "failed_settlements": failed_count,
            "settlements": settlements,
            "batch_id": f"BATCH-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "processed_at": datetime.now()
        }
    
    async def get_settlement_summary(
        self,
        region: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get settlement summary for a region and time period"""
        
        # Mock settlement summary - in production, query database
        await asyncio.sleep(0.1)
        
        start_date = start_date or (datetime.now() - timedelta(days=30))
        end_date = end_date or datetime.now()
        
        # Generate mock settlement data
        mock_settlements = []
        base_date = start_date
        
        while base_date <= end_date:
            mock_settlements.append({
                "date": base_date,
                "pending_settlements": 15 + (hash(str(base_date)) % 20),
                "completed_settlements": 25 + (hash(str(base_date)) % 30),
                "failed_settlements": 2 + (hash(str(base_date)) % 5),
                "total_amount": 1000000 + (hash(str(base_date)) % 5000000),
                "currency": "USD"
            })
            base_date += timedelta(days=1)
        
        # Calculate summary statistics
        total_pending = sum(s["pending_settlements"] for s in mock_settlements)
        total_completed = sum(s["completed_settlements"] for s in mock_settlements)
        total_failed = sum(s["failed_settlements"] for s in mock_settlements)
        total_amount = sum(s["total_amount"] for s in mock_settlements)
        
        return {
            "region": region,
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "summary": {
                "total_pending": total_pending,
                "total_completed": total_completed,
                "total_failed": total_failed,
                "total_amount": total_amount,
                "success_rate": total_completed / (total_completed + total_failed) if (total_completed + total_failed) > 0 else 0
            },
            "daily_breakdown": mock_settlements,
            "clearing_house_breakdown": self._get_clearing_house_breakdown(region),
            "currency_breakdown": self._get_currency_breakdown(region)
        }
    
    async def _validate_settlement(
        self,
        settlement_amount: Decimal,
        settlement_currency: str,
        region: str,
        payment_method: str
    ) -> Dict[str, Any]:
        """Validate settlement parameters"""
        
        errors = []
        
        # Validate amount
        if settlement_amount <= 0:
            errors.append("Settlement amount must be positive")
        
        # Validate currency
        if region in self.payment_methods:
            if settlement_currency not in self.payment_methods[region]:
                errors.append(f"Currency {settlement_currency} not supported in region {region}")
        
        # Validate payment method
        if region in self.payment_methods:
            if payment_method not in self.payment_methods[region]:
                errors.append(f"Payment method {payment_method} not supported in region {region}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _calculate_settlement_date(self, region: str) -> datetime:
        """Calculate settlement date based on regional cycle"""
        
        today = datetime.now()
        cycle_days = int(self.settlement_cycles[region].split("+")[1])
        
        # Add business days (simplified - in production, consider holidays)
        settlement_date = today + timedelta(days=cycle_days)
        
        return settlement_date
    
    def _get_default_clearing_house(self, region: str) -> str:
        """Get default clearing house for a region"""
        
        if region in self.clearing_houses:
            # Return first available clearing house
            return list(self.clearing_houses[region].keys())[0]
        
        return "OTC"  # Default to OTC
    
    def _generate_settlement_instructions(
        self,
        region: str,
        payment_method: str,
        clearing_house: Optional[str]
    ) -> Dict[str, Any]:
        """Generate settlement instructions based on region and method"""
        
        instructions = {
            "region": region,
            "payment_method": payment_method,
            "clearing_house": clearing_house,
            "settlement_cycle": self.settlement_cycles.get(region, "T+2"),
            "cut_off_time": "16:00 UTC",
            "special_instructions": []
        }
        
        # Add region-specific instructions
        if region == "ME":
            instructions["special_instructions"].append("Local banking hours apply")
            instructions["special_instructions"].append("Holiday calendar follows local market")
        elif region == "US":
            instructions["special_instructions"].append("Fedwire operating hours apply")
            instructions["special_instructions"].append("Holiday calendar follows US market")
        elif region == "UK":
            instructions["special_instructions"].append("CHAPS operating hours apply")
            instructions["special_instructions"].append("Holiday calendar follows UK market")
        elif region == "EU":
            instructions["special_instructions"].append("SEPA operating hours apply")
            instructions["special_instructions"].append("Holiday calendar follows EU market")
        elif region == "GUYANA":
            instructions["special_instructions"].append("Local banking hours apply")
            instructions["special_instructions"].append("Extended settlement cycle due to market development")
        
        return instructions
    
    def _get_clearing_house_breakdown(self, region: str) -> Dict[str, Any]:
        """Get clearing house breakdown for a region"""
        
        if region not in self.clearing_houses:
            return {}
        
        breakdown = {}
        for clearing_house, description in self.clearing_houses[region].items():
            # Mock volume distribution
            breakdown[clearing_house] = {
                "description": description,
                "settlement_volume": 1000 + (hash(clearing_house) % 5000),
                "market_share": 0.25 + (hash(clearing_house) % 50) / 100
            }
        
        return breakdown
    
    def _get_currency_breakdown(self, region: str) -> Dict[str, Any]:
        """Get currency breakdown for a region"""
        
        currencies = self.payment_methods.get(region, [])
        breakdown = {}
        
        for currency in currencies:
            if currency not in ["bank_transfer", "local_currency"]:
                # Mock currency distribution
                breakdown[currency] = {
                    "settlement_volume": 1000000 + (hash(currency) % 10000000),
                    "percentage": 20 + (hash(currency) % 60)
                }
        
        return breakdown 