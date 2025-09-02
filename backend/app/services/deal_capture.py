"""
Deal Capture Service for ETRM/CTRM Trading Operations
Handles trade capture, validation, and lifecycle management
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import uuid
import logging

logger = logging.getLogger(__name__)


class DealCaptureService:
    """Service for capturing and managing trading deals"""
    
    def __init__(self):
        self.deals = {}  # In-memory storage for stubs
        self.deal_counter = 1000
        
    def capture_deal(self, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Capture a new trading deal
        
        Args:
            deal_data: Deal information including parties, commodity, terms
            
        Returns:
            Dict with captured deal details and ID
        """
        # TODO: Implement real deal validation and database storage
        deal_id = f"DEAL-{self.deal_counter:06d}"
        self.deal_counter += 1
        
        # Basic validation stub
        if not deal_data.get("commodity"):
            return {
                "success": False,
                "error": "Commodity is required",
                "deal_id": None
            }
        
        # Create deal record
        deal_record = {
            "deal_id": deal_id,
            "status": "captured",
            "captured_at": datetime.now().isoformat(),
            "parties": deal_data.get("parties", []),
            "commodity": deal_data.get("commodity"),
            "quantity": deal_data.get("quantity", 0),
            "price": deal_data.get("price", 0.0),
            "currency": deal_data.get("currency", "USD"),
            "delivery_date": deal_data.get("delivery_date"),
            "trade_type": deal_data.get("trade_type", "spot"),
            "sharia_compliant": deal_data.get("sharia_compliant", False),
            "risk_metrics": self._calculate_risk_metrics(deal_data)
        }
        
        self.deals[deal_id] = deal_record
        
        return {
            "success": True,
            "deal_id": deal_id,
            "deal": deal_record
        }
    
    def get_deal(self, deal_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve deal by ID
        
        Args:
            deal_id: Unique deal identifier
            
        Returns:
            Deal record or None if not found
        """
        return self.deals.get(deal_id)
    
    def update_deal(self, deal_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update existing deal
        
        Args:
            deal_id: Unique deal identifier
            updates: Fields to update
            
        Returns:
            Dict with update status
        """
        if deal_id not in self.deals:
            return {
                "success": False,
                "error": "Deal not found"
            }
        
        # TODO: Implement proper update validation
        for key, value in updates.items():
            if key in ["deal_id", "captured_at"]:
                continue  # Protected fields
            self.deals[deal_id][key] = value
        
        self.deals[deal_id]["updated_at"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "deal": self.deals[deal_id]
        }
    
    def list_deals(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List deals with optional filtering
        
        Args:
            filters: Optional filter criteria
            
        Returns:
            List of matching deals
        """
        # TODO: Implement proper filtering and pagination
        deals = list(self.deals.values())
        
        if filters:
            # Basic stub filtering
            if "commodity" in filters:
                deals = [d for d in deals if d.get("commodity") == filters["commodity"]]
            if "status" in filters:
                deals = [d for d in deals if d.get("status") == filters["status"]]
        
        return deals
    
    def _calculate_risk_metrics(self, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate basic risk metrics for deal
        
        Args:
            deal_data: Deal information
            
        Returns:
            Dict with risk metrics
        """
        # TODO: Implement proper risk calculations
        quantity = deal_data.get("quantity", 0)
        price = deal_data.get("price", 0.0)
        
        notional_value = quantity * price
        max_loss = notional_value * 0.1  # 10% max loss stub
        
        return {
            "notional_value": notional_value,
            "max_loss": max_loss,
            "risk_level": "medium" if notional_value > 1000000 else "low"
        }


class DealValidationService:
    """Service for validating deal data and business rules"""
    
    def __init__(self):
        self.required_fields = ["parties", "commodity", "quantity", "price", "delivery_date"]
        self.max_quantity = 1000000  # 1M units max
        self.max_price = 10000.0     # $10K max price
        
    def validate_deal_data(self, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate deal data against business rules
        
        Args:
            deal_data: Deal information to validate
            
        Returns:
            Dict with validation results
        """
        errors = []
        warnings = []
        
        # Check required fields
        for field in self.required_fields:
            if field not in deal_data or not deal_data[field]:
                errors.append(f"Required field '{field}' is missing or empty")
        
        # Check business rules
        quantity = deal_data.get("quantity", 0)
        if quantity > self.max_quantity:
            errors.append(f"Quantity {quantity} exceeds maximum {self.max_quantity}")
        
        price = deal_data.get("price", 0.0)
        if price > self.max_price:
            errors.append(f"Price {price} exceeds maximum {self.max_price}")
        
        # Check delivery date
        delivery_date = deal_data.get("delivery_date")
        if delivery_date:
            try:
                delivery_dt = datetime.fromisoformat(delivery_date)
                if delivery_dt < datetime.now():
                    errors.append("Delivery date cannot be in the past")
                elif delivery_dt > datetime.now() + timedelta(days=365):
                    warnings.append("Delivery date is more than 1 year in the future")
            except ValueError:
                errors.append("Invalid delivery date format")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def validate_counterparty_limits(self, counterparty_id: str, deal_value: float) -> Dict[str, Any]:
        """
        Validate counterparty credit limits
        
        Args:
            counterparty_id: Counterparty identifier
            deal_value: Value of the proposed deal
            
        Returns:
            Dict with validation results
        """
        # TODO: Implement real counterparty limit checking
        max_limit = 10000000  # $10M stub limit
        
        if deal_value > max_limit:
            return {
                "valid": False,
                "error": f"Deal value {deal_value} exceeds counterparty limit {max_limit}",
                "available_limit": max_limit - deal_value
            }
        
        return {
            "valid": True,
            "available_limit": max_limit - deal_value
        }
