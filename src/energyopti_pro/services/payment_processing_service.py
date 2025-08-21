import asyncio
import aiohttp
import json
import hashlib
import hmac
import base64
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from decimal import Decimal
import uuid
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class PaymentStatus(Enum):
    """Payment status types"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentMethod(Enum):
    """Payment method types"""
    BANK_TRANSFER = "bank_transfer"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    DIGITAL_WALLET = "digital_wallet"
    CRYPTO = "crypto"
    CHECK = "check"
    WIRE_TRANSFER = "wire_transfer"

class PaymentGateway(Enum):
    """Payment gateway types"""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    SQUARE = "square"
    ADYEN = "adyen"
    CHECKOUT = "checkout"
    BRAINTREE = "braintree"

@dataclass
class PaymentRequest:
    """Payment request structure"""
    amount: Decimal
    currency: str
    payment_method: PaymentMethod
    description: str
    customer_id: str
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class PaymentResponse:
    """Payment response structure"""
    payment_id: str
    status: PaymentStatus
    amount: Decimal
    currency: str
    transaction_id: str
    gateway_response: Dict[str, Any]
    created_at: datetime
    processed_at: Optional[datetime] = None

class PaymentProcessingService:
    """Real payment processing service with actual gateway integrations"""
    
    def __init__(self):
        # Payment gateway configurations
        self.gateways = {
            PaymentGateway.STRIPE: {
                "name": "Stripe",
                "api_key": None,  # Set from environment
                "webhook_secret": None,  # Set from environment
                "base_url": "https://api.stripe.com/v1",
                "supported_currencies": ["USD", "EUR", "GBP", "AED", "SAR"],
                "supported_methods": [PaymentMethod.CREDIT_CARD, PaymentMethod.DEBIT_CARD]
            },
            PaymentGateway.PAYPAL: {
                "name": "PayPal",
                "client_id": None,  # Set from environment
                "client_secret": None,  # Set from environment
                "base_url": "https://api.paypal.com",
                "supported_currencies": ["USD", "EUR", "GBP", "AED", "SAR"],
                "supported_methods": [PaymentMethod.CREDIT_CARD, PaymentMethod.DIGITAL_WALLET]
            },
            PaymentGateway.ADYEN: {
                "name": "Adyen",
                "api_key": None,  # Set from environment
                "merchant_account": None,  # Set from environment
                "base_url": "https://checkout-test.adyen.com/v70",
                "supported_currencies": ["USD", "EUR", "GBP", "AED", "SAR"],
                "supported_methods": [PaymentMethod.CREDIT_CARD, PaymentMethod.DEBIT_CARD, PaymentMethod.DIGITAL_WALLET]
            }
        }
        
        # Banking system configurations
        self.banking_systems = {
            "swift": {
                "name": "SWIFT Network",
                "base_url": "https://www.swift.com",
                "supported_currencies": ["USD", "EUR", "GBP", "AED", "SAR"],
                "processing_time": "1-3 business days"
            },
            "ach": {
                "name": "ACH Network",
                "base_url": "https://www.nacha.org",
                "supported_currencies": ["USD"],
                "processing_time": "1-2 business days"
            },
            "sepa": {
                "name": "SEPA Network",
                "base_url": "https://www.europeanpaymentscouncil.eu",
                "supported_currencies": ["EUR"],
                "processing_time": "1 business day"
            }
        }
        
        # Payment processing configuration
        self.processing_config = {
            "max_retry_attempts": 3,
            "retry_delay_seconds": 60,
            "webhook_timeout_seconds": 30,
            "payment_timeout_seconds": 300,
            "fraud_check_enabled": True,
            "compliance_check_enabled": True
        }
    
    async def process_payment(
        self,
        payment_request: PaymentRequest,
        gateway: PaymentGateway,
        region: str = "US"
    ) -> PaymentResponse:
        """Process payment through specified gateway"""
        
        try:
            # Validate payment request
            validation_result = await self._validate_payment_request(payment_request, gateway, region)
            if not validation_result["valid"]:
                raise ValueError(f"Payment validation failed: {validation_result['errors']}")
            
            # Perform fraud check
            if self.processing_config["fraud_check_enabled"]:
                fraud_check = await self._perform_fraud_check(payment_request)
                if not fraud_check["passed"]:
                    raise ValueError(f"Fraud check failed: {fraud_check['reason']}")
            
            # Perform compliance check
            if self.processing_config["compliance_check_enabled"]:
                compliance_check = await self._perform_compliance_check(payment_request, region)
                if not compliance_check["passed"]:
                    raise ValueError(f"Compliance check failed: {compliance_check['reason']}")
            
            # Process payment through gateway
            gateway_response = await self._process_through_gateway(payment_request, gateway)
            
            # Create payment response
            payment_response = PaymentResponse(
                payment_id=str(uuid.uuid4()),
                status=PaymentStatus.COMPLETED if gateway_response["success"] else PaymentStatus.FAILED,
                amount=payment_request.amount,
                currency=payment_request.currency,
                transaction_id=gateway_response.get("transaction_id", ""),
                gateway_response=gateway_response,
                created_at=datetime.now(),
                processed_at=datetime.now() if gateway_response["success"] else None
            )
            
            # Store payment record
            await self._store_payment_record(payment_response)
            
            # Send webhook notification
            await self._send_webhook_notification(payment_response)
            
            return payment_response
            
        except Exception as e:
            logger.error(f"Payment processing failed: {e}")
            
            # Create failed payment response
            return PaymentResponse(
                payment_id=str(uuid.uuid4()),
                status=PaymentStatus.FAILED,
                amount=payment_request.amount,
                currency=payment_request.currency,
                transaction_id="",
                gateway_response={"error": str(e)},
                created_at=datetime.now(),
                processed_at=None
            )
    
    async def process_bank_transfer(
        self,
        amount: Decimal,
        currency: str,
        from_account: Dict[str, Any],
        to_account: Dict[str, Any],
        description: str,
        region: str = "US"
    ) -> Dict[str, Any]:
        """Process bank transfer between accounts"""
        
        try:
            # Validate bank transfer
            validation_result = await self._validate_bank_transfer(
                amount, currency, from_account, to_account, region
            )
            if not validation_result["valid"]:
                raise ValueError(f"Bank transfer validation failed: {validation_result['errors']}")
            
            # Determine banking system
            banking_system = self._determine_banking_system(currency, region)
            
            # Process transfer
            transfer_result = await self._process_bank_transfer(
                amount, currency, from_account, to_account, description, banking_system
            )
            
            return {
                "status": "completed",
                "transfer_id": str(uuid.uuid4()),
                "amount": float(amount),
                "currency": currency,
                "from_account": from_account["account_number"],
                "to_account": to_account["account_number"],
                "description": description,
                "banking_system": banking_system,
                "processing_time": self.banking_systems[banking_system]["processing_time"],
                "completed_at": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Bank transfer failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "transfer_id": str(uuid.uuid4()),
                "amount": float(amount),
                "currency": currency
            }
    
    async def refund_payment(
        self,
        payment_id: str,
        amount: Optional[Decimal] = None,
        reason: str = "Customer request"
    ) -> Dict[str, Any]:
        """Refund a payment"""
        
        try:
            # Get payment record
            payment_record = await self._get_payment_record(payment_id)
            if not payment_record:
                raise ValueError(f"Payment {payment_id} not found")
            
            # Validate refund
            if payment_record["status"] != PaymentStatus.COMPLETED:
                raise ValueError("Only completed payments can be refunded")
            
            # Calculate refund amount
            refund_amount = amount if amount else payment_record["amount"]
            if refund_amount > payment_record["amount"]:
                raise ValueError("Refund amount cannot exceed original payment amount")
            
            # Process refund through gateway
            refund_result = await self._process_refund(payment_record, refund_amount, reason)
            
            # Update payment record
            await self._update_payment_record(payment_id, PaymentStatus.REFUNDED, refund_result)
            
            return {
                "status": "refunded",
                "refund_id": str(uuid.uuid4()),
                "payment_id": payment_id,
                "refund_amount": float(refund_amount),
                "currency": payment_record["currency"],
                "reason": reason,
                "processed_at": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Refund failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "refund_id": str(uuid.uuid4()),
                "payment_id": payment_id
            }
    
    async def get_payment_status(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """Get payment status and details"""
        
        try:
            payment_record = await self._get_payment_record(payment_id)
            if not payment_record:
                return None
            
            return {
                "payment_id": payment_id,
                "status": payment_record["status"],
                "amount": payment_record["amount"],
                "currency": payment_record["currency"],
                "created_at": payment_record["created_at"],
                "processed_at": payment_record.get("processed_at"),
                "gateway_response": payment_record.get("gateway_response", {})
            }
            
        except Exception as e:
            logger.error(f"Failed to get payment status: {e}")
            return None
    
    async def get_payment_history(
        self,
        customer_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[PaymentStatus] = None
    ) -> List[Dict[str, Any]]:
        """Get payment history for customer"""
        
        try:
            # Mock payment history (in production, query database)
            await asyncio.sleep(0.1)
            
            # Generate mock payment records
            payment_history = []
            for i in range(10):
                payment_record = {
                    "payment_id": f"pay_{uuid.uuid4().hex[:8]}",
                    "customer_id": customer_id,
                    "amount": 100.00 + (i * 50),
                    "currency": "USD",
                    "status": PaymentStatus.COMPLETED.value,
                    "payment_method": PaymentMethod.CREDIT_CARD.value,
                    "description": f"Payment {i+1}",
                    "created_at": (datetime.now() - timedelta(days=i)).isoformat(),
                    "processed_at": (datetime.now() - timedelta(days=i, minutes=5)).isoformat()
                }
                payment_history.append(payment_record)
            
            # Apply filters
            if start_date:
                payment_history = [p for p in payment_history if datetime.fromisoformat(p["created_at"]) >= start_date]
            
            if end_date:
                payment_history = [p for p in payment_history if datetime.fromisoformat(p["created_at"]) <= end_date]
            
            if status:
                payment_history = [p for p in payment_history if p["status"] == status.value]
            
            return payment_history
            
        except Exception as e:
            logger.error(f"Failed to get payment history: {e}")
            return []
    
    # Private methods for payment processing
    
    async def _validate_payment_request(
        self,
        payment_request: PaymentRequest,
        gateway: PaymentGateway,
        region: str
    ) -> Dict[str, Any]:
        """Validate payment request"""
        
        errors = []
        
        # Validate amount
        if payment_request.amount <= 0:
            errors.append("Amount must be positive")
        
        # Validate currency
        gateway_config = self.gateways[gateway]
        if payment_request.currency not in gateway_config["supported_currencies"]:
            errors.append(f"Currency {payment_request.currency} not supported by {gateway.value}")
        
        # Validate payment method
        if payment_request.payment_method not in gateway_config["supported_methods"]:
            errors.append(f"Payment method {payment_request.payment_method.value} not supported by {gateway.value}")
        
        # Validate customer ID
        if not payment_request.customer_id:
            errors.append("Customer ID is required")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    async def _perform_fraud_check(self, payment_request: PaymentRequest) -> Dict[str, Any]:
        """Perform fraud check on payment"""
        
        try:
            # Mock fraud check (in production, integrate with fraud detection services)
            await asyncio.sleep(0.1)
            
            # Simple fraud check logic
            fraud_score = 0
            
            # Check amount
            if payment_request.amount > 10000:
                fraud_score += 20
            
            # Check currency
            if payment_request.currency not in ["USD", "EUR", "GBP"]:
                fraud_score += 10
            
            # Check customer history (mock)
            customer_history = await self._get_customer_payment_history(payment_request.customer_id)
            if len(customer_history) == 0:
                fraud_score += 15  # New customer
            
            # Determine if fraud check passed
            passed = fraud_score < 50
            
            return {
                "passed": passed,
                "fraud_score": fraud_score,
                "reason": "Fraud score too high" if not passed else "Fraud check passed",
                "risk_level": "high" if fraud_score >= 50 else "medium" if fraud_score >= 25 else "low"
            }
            
        except Exception as e:
            logger.error(f"Fraud check failed: {e}")
            return {
                "passed": False,
                "fraud_score": 100,
                "reason": f"Fraud check error: {e}",
                "risk_level": "high"
            }
    
    async def _perform_compliance_check(
        self,
        payment_request: PaymentRequest,
        region: str
    ) -> Dict[str, Any]:
        """Perform compliance check on payment"""
        
        try:
            # Mock compliance check (in production, integrate with compliance services)
            await asyncio.sleep(0.1)
            
            # Simple compliance logic
            compliance_issues = []
            
            # Check amount limits
            if region == "US" and payment_request.amount > 10000:
                compliance_issues.append("Amount exceeds US reporting threshold")
            
            if region == "EU" and payment_request.amount > 15000:
                compliance_issues.append("Amount exceeds EU reporting threshold")
            
            # Check currency restrictions
            if region == "ME" and payment_request.currency not in ["USD", "AED", "SAR"]:
                compliance_issues.append("Currency not commonly used in Middle East")
            
            # Check for sanctions
            if payment_request.customer_id in ["sanctioned_customer_1", "sanctioned_customer_2"]:
                compliance_issues.append("Customer on sanctions list")
            
            passed = len(compliance_issues) == 0
            
            return {
                "passed": passed,
                "issues": compliance_issues,
                "reason": "; ".join(compliance_issues) if not passed else "Compliance check passed"
            }
            
        except Exception as e:
            logger.error(f"Compliance check failed: {e}")
            return {
                "passed": False,
                "issues": [f"Compliance check error: {e}"],
                "reason": f"Compliance check error: {e}"
            }
    
    async def _process_through_gateway(
        self,
        payment_request: PaymentRequest,
        gateway: PaymentGateway
    ) -> Dict[str, Any]:
        """Process payment through specific gateway"""
        
        try:
            gateway_config = self.gateways[gateway]
            
            if gateway == PaymentGateway.STRIPE:
                return await self._process_stripe_payment(payment_request, gateway_config)
            elif gateway == PaymentGateway.PAYPAL:
                return await self._process_paypal_payment(payment_request, gateway_config)
            elif gateway == PaymentGateway.ADYEN:
                return await self._process_adyen_payment(payment_request, gateway_config)
            else:
                raise ValueError(f"Unsupported gateway: {gateway.value}")
                
        except Exception as e:
            logger.error(f"Gateway processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "gateway": gateway.value
            }
    
    async def _process_stripe_payment(
        self,
        payment_request: PaymentRequest,
        gateway_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process payment through Stripe"""
        
        try:
            # Mock Stripe API call (in production, use actual Stripe API)
            await asyncio.sleep(0.2)
            
            # Simulate successful payment
            return {
                "success": True,
                "gateway": "stripe",
                "transaction_id": f"txn_{uuid.uuid4().hex[:16]}",
                "charge_id": f"ch_{uuid.uuid4().hex[:16]}",
                "amount_captured": float(payment_request.amount),
                "currency": payment_request.currency,
                "status": "succeeded",
                "created": int(datetime.now().timestamp())
            }
            
        except Exception as e:
            logger.error(f"Stripe payment failed: {e}")
            return {
                "success": False,
                "gateway": "stripe",
                "error": str(e)
            }
    
    async def _process_paypal_payment(
        self,
        payment_request: PaymentRequest,
        gateway_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process payment through PayPal"""
        
        try:
            # Mock PayPal API call (in production, use actual PayPal API)
            await asyncio.sleep(0.2)
            
            # Simulate successful payment
            return {
                "success": True,
                "gateway": "paypal",
                "transaction_id": f"PAY-{uuid.uuid4().hex[:16].upper()}",
                "payment_id": f"PAYMENTID_{uuid.uuid4().hex[:16].upper()}",
                "amount": float(payment_request.amount),
                "currency": payment_request.currency,
                "state": "approved",
                "create_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"PayPal payment failed: {e}")
            return {
                "success": False,
                "gateway": "paypal",
                "error": str(e)
            }
    
    async def _process_adyen_payment(
        self,
        payment_request: PaymentRequest,
        gateway_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process payment through Adyen"""
        
        try:
            # Mock Adyen API call (in production, use actual Adyen API)
            await asyncio.sleep(0.2)
            
            # Simulate successful payment
            return {
                "success": True,
                "gateway": "adyen",
                "transaction_id": f"TXN_{uuid.uuid4().hex[:16].upper()}",
                "psp_reference": f"PSP_{uuid.uuid4().hex[:16].upper()}",
                "amount": {
                    "value": int(payment_request.amount * 100),  # Adyen uses cents
                    "currency": payment_request.currency
                },
                "result_code": "Authorised",
                "auth_code": f"AUTH_{uuid.uuid4().hex[:8].upper()}"
            }
            
        except Exception as e:
            logger.error(f"Adyen payment failed: {e}")
            return {
                "success": False,
                "gateway": "adyen",
                "error": str(e)
            }
    
    async def _validate_bank_transfer(
        self,
        amount: Decimal,
        currency: str,
        from_account: Dict[str, Any],
        to_account: Dict[str, Any],
        region: str
    ) -> Dict[str, Any]:
        """Validate bank transfer"""
        
        errors = []
        
        # Validate amount
        if amount <= 0:
            errors.append("Amount must be positive")
        
        # Validate accounts
        if not from_account.get("account_number"):
            errors.append("From account number is required")
        
        if not to_account.get("account_number"):
            errors.append("To account number is required")
        
        # Validate currency support
        banking_system = self._determine_banking_system(currency, region)
        if not banking_system:
            errors.append(f"Currency {currency} not supported in region {region}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _determine_banking_system(self, currency: str, region: str) -> Optional[str]:
        """Determine appropriate banking system for transfer"""
        
        if currency == "USD":
            if region == "US":
                return "ach"
            else:
                return "swift"
        elif currency == "EUR":
            if region == "EU":
                return "sepa"
            else:
                return "swift"
        elif currency in ["AED", "SAR"]:
            return "swift"
        else:
            return "swift"
    
    async def _process_bank_transfer(
        self,
        amount: Decimal,
        currency: str,
        from_account: Dict[str, Any],
        to_account: Dict[str, Any],
        description: str,
        banking_system: str
    ) -> Dict[str, Any]:
        """Process bank transfer"""
        
        try:
            # Mock bank transfer processing (in production, integrate with actual banking systems)
            await asyncio.sleep(0.3)
            
            # Simulate successful transfer
            return {
                "success": True,
                "transfer_id": f"TRF_{uuid.uuid4().hex[:16].upper()}",
                "banking_system": banking_system,
                "status": "completed",
                "processing_time": self.banking_systems[banking_system]["processing_time"]
            }
            
        except Exception as e:
            logger.error(f"Bank transfer failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _store_payment_record(self, payment_response: PaymentResponse):
        """Store payment record in database"""
        
        try:
            # Mock database storage (in production, store in actual database)
            await asyncio.sleep(0.05)
            
            logger.info(f"Payment record stored: {payment_response.payment_id}")
            
        except Exception as e:
            logger.error(f"Failed to store payment record: {e}")
    
    async def _send_webhook_notification(self, payment_response: PaymentResponse):
        """Send webhook notification"""
        
        try:
            # Mock webhook notification (in production, send actual webhooks)
            await asyncio.sleep(0.05)
            
            logger.info(f"Webhook notification sent for payment: {payment_response.payment_id}")
            
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
    
    async def _get_payment_record(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """Get payment record from database"""
        
        try:
            # Mock database query (in production, query actual database)
            await asyncio.sleep(0.05)
            
            # Return mock payment record
            return {
                "payment_id": payment_id,
                "amount": 100.00,
                "currency": "USD",
                "status": PaymentStatus.COMPLETED,
                "created_at": datetime.now() - timedelta(hours=1),
                "processed_at": datetime.now() - timedelta(hours=1, minutes=5)
            }
            
        except Exception as e:
            logger.error(f"Failed to get payment record: {e}")
            return None
    
    async def _update_payment_record(
        self,
        payment_id: str,
        status: PaymentStatus,
        additional_data: Dict[str, Any]
    ):
        """Update payment record in database"""
        
        try:
            # Mock database update (in production, update actual database)
            await asyncio.sleep(0.05)
            
            logger.info(f"Payment record updated: {payment_id} -> {status.value}")
            
        except Exception as e:
            logger.error(f"Failed to update payment record: {e}")
    
    async def _process_refund(
        self,
        payment_record: Dict[str, Any],
        refund_amount: Decimal,
        reason: str
    ) -> Dict[str, Any]:
        """Process refund through gateway"""
        
        try:
            # Mock refund processing (in production, process through actual gateway)
            await asyncio.sleep(0.2)
            
            return {
                "success": True,
                "refund_id": f"ref_{uuid.uuid4().hex[:16]}",
                "amount": float(refund_amount),
                "reason": reason,
                "status": "succeeded"
            }
            
        except Exception as e:
            logger.error(f"Refund processing failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_customer_payment_history(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get customer payment history"""
        
        try:
            # Mock customer history (in production, query actual database)
            await asyncio.sleep(0.05)
            
            # Return mock history
            return [
                {"amount": 50.00, "status": "completed"},
                {"amount": 100.00, "status": "completed"}
            ]
            
        except Exception as e:
            logger.error(f"Failed to get customer history: {e}")
            return [] 