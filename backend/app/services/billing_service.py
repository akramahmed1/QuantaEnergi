"""
Billing and Subscription Management Service
Comprehensive billing system with Stripe integration
"""

import stripe
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import structlog
from dataclasses import dataclass
from enum import Enum
import json

logger = structlog.get_logger()

class PlanType(str, Enum):
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"

class BillingCycle(str, Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"
    QUARTERLY = "quarterly"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"

@dataclass
class Subscription:
    """User subscription information"""
    user_id: str
    plan_type: PlanType
    billing_cycle: BillingCycle
    status: str
    start_date: datetime
    end_date: datetime
    amount: float
    currency: str
    stripe_subscription_id: Optional[str] = None
    features: List[str] = None

@dataclass
class Invoice:
    """Invoice information"""
    invoice_id: str
    user_id: str
    amount: float
    currency: str
    status: PaymentStatus
    due_date: datetime
    paid_date: Optional[datetime] = None
    stripe_invoice_id: Optional[str] = None
    items: List[Dict[str, Any]] = None

class BillingService:
    """Comprehensive billing and subscription management"""
    
    def __init__(self):
        self.stripe_api_key = "sk_test_mock_key"  # Mock Stripe key
        self.plans = self._initialize_plans()
        self.usage_tracking = {}
        self.billing_history = {}
        
    def _initialize_plans(self) -> Dict[str, Dict[str, Any]]:
        """Initialize subscription plans"""
        return {
            "basic": {
                "name": "Basic Plan",
                "price_monthly": 99.00,
                "price_yearly": 999.00,
                "features": [
                    "Basic trading",
                    "Market data",
                    "Email support",
                    "5 API calls/minute"
                ],
                "limits": {
                    "max_trades": 100,
                    "max_portfolios": 3,
                    "api_calls_per_minute": 5,
                    "storage_gb": 1
                }
            },
            "pro": {
                "name": "Pro Plan",
                "price_monthly": 299.00,
                "price_yearly": 2999.00,
                "features": [
                    "Advanced trading",
                    "AI forecasting",
                    "Portfolio optimization",
                    "Priority support",
                    "50 API calls/minute"
                ],
                "limits": {
                    "max_trades": 1000,
                    "max_portfolios": 10,
                    "api_calls_per_minute": 50,
                    "storage_gb": 10
                }
            },
            "enterprise": {
                "name": "Enterprise Plan",
                "price_monthly": 999.00,
                "price_yearly": 9999.00,
                "features": [
                    "Full platform access",
                    "Quantum optimization",
                    "Custom integrations",
                    "Dedicated support",
                    "Unlimited API calls",
                    "White-label options"
                ],
                "limits": {
                    "max_trades": -1,  # Unlimited
                    "max_portfolios": -1,
                    "api_calls_per_minute": -1,
                    "storage_gb": 100
                }
            }
        }
    
    def create_subscription(self, user_id: str, plan_type: PlanType, 
                           billing_cycle: BillingCycle, 
                           payment_method: str) -> Subscription:
        """Create new subscription"""
        try:
            plan = self.plans[plan_type.value]
            
            # Calculate pricing
            if billing_cycle == BillingCycle.MONTHLY:
                amount = plan["price_monthly"]
            elif billing_cycle == BillingCycle.YEARLY:
                amount = plan["price_yearly"]
            else:  # QUARTERLY
                amount = plan["price_monthly"] * 3
            
            # Mock Stripe subscription creation
            stripe_subscription_id = f"sub_{user_id}_{datetime.now().timestamp()}"
            
            # Create subscription
            subscription = Subscription(
                user_id=user_id,
                plan_type=plan_type,
                billing_cycle=billing_cycle,
                status="active",
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=30 if billing_cycle == BillingCycle.MONTHLY else 365),
                amount=amount,
                currency="USD",
                stripe_subscription_id=stripe_subscription_id,
                features=plan["features"]
            )
            
            logger.info("Subscription created",
                       user_id=user_id,
                       plan=plan_type.value,
                       amount=amount)
            
            return subscription
            
        except Exception as e:
            logger.error("Subscription creation failed", error=str(e))
            raise
    
    def update_subscription(self, user_id: str, new_plan: PlanType) -> Subscription:
        """Update existing subscription"""
        try:
            # Mock subscription update
            current_subscription = self._get_user_subscription(user_id)
            
            if not current_subscription:
                raise ValueError("No active subscription found")
            
            # Create new subscription with updated plan
            updated_subscription = Subscription(
                user_id=user_id,
                plan_type=new_plan,
                billing_cycle=current_subscription.billing_cycle,
                status="active",
                start_date=datetime.now(),
                end_date=current_subscription.end_date,
                amount=self.plans[new_plan.value]["price_monthly"],
                currency="USD",
                stripe_subscription_id=current_subscription.stripe_subscription_id,
                features=self.plans[new_plan.value]["features"]
            )
            
            logger.info("Subscription updated",
                       user_id=user_id,
                       old_plan=current_subscription.plan_type.value,
                       new_plan=new_plan.value)
            
            return updated_subscription
            
        except Exception as e:
            logger.error("Subscription update failed", error=str(e))
            raise
    
    def cancel_subscription(self, user_id: str, reason: str = None) -> bool:
        """Cancel subscription"""
        try:
            subscription = self._get_user_subscription(user_id)
            
            if not subscription:
                return False
            
            # Mock cancellation
            subscription.status = "cancelled"
            
            logger.info("Subscription cancelled",
                       user_id=user_id,
                       reason=reason)
            
            return True
            
        except Exception as e:
            logger.error("Subscription cancellation failed", error=str(e))
            raise
    
    def get_subscription(self, user_id: str) -> Optional[Subscription]:
        """Get user subscription"""
        return self._get_user_subscription(user_id)
    
    def get_usage(self, user_id: str, period: str = "current_month") -> Dict[str, Any]:
        """Get usage statistics"""
        try:
            subscription = self._get_user_subscription(user_id)
            
            if not subscription:
                return {"error": "No active subscription"}
            
            plan_limits = self.plans[subscription.plan_type.value]["limits"]
            
            # Mock usage data
            usage = {
                "trades_used": np.random.randint(0, plan_limits["max_trades"] // 2),
                "portfolios_used": np.random.randint(0, plan_limits["max_portfolios"] // 2),
                "api_calls_used": np.random.randint(0, plan_limits["api_calls_per_minute"] * 100),
                "storage_used_gb": np.random.uniform(0, plan_limits["storage_gb"] / 2),
                "period": period,
                "limits": plan_limits,
                "usage_percentage": {
                    "trades": 0,
                    "portfolios": 0,
                    "api_calls": 0,
                    "storage": 0
                }
            }
            
            # Calculate usage percentages
            for key in ["trades", "portfolios", "api_calls", "storage"]:
                limit_key = f"max_{key}"
                if limit_key in plan_limits and plan_limits[limit_key] > 0:
                    usage["usage_percentage"][key] = (
                        usage[f"{key}_used"] / plan_limits[limit_key] * 100
                    )
                else:
                    usage["usage_percentage"][key] = 0
            
            return usage
            
        except Exception as e:
            logger.error("Usage retrieval failed", error=str(e))
            raise
    
    def create_invoice(self, user_id: str, items: List[Dict[str, Any]], 
                      due_date: Optional[datetime] = None) -> Invoice:
        """Create invoice"""
        try:
            # Calculate total amount
            total_amount = sum(item.get("amount", 0) for item in items)
            
            # Create invoice
            invoice = Invoice(
                invoice_id=f"inv_{user_id}_{datetime.now().timestamp()}",
                user_id=user_id,
                amount=total_amount,
                currency="USD",
                status=PaymentStatus.PENDING,
                due_date=due_date or datetime.now() + timedelta(days=30),
                items=items
            )
            
            logger.info("Invoice created",
                       user_id=user_id,
                       amount=total_amount,
                       invoice_id=invoice.invoice_id)
            
            return invoice
            
        except Exception as e:
            logger.error("Invoice creation failed", error=str(e))
            raise
    
    def process_payment(self, invoice_id: str, payment_method: str) -> bool:
        """Process payment for invoice"""
        try:
            # Mock payment processing
            invoice = self._get_invoice(invoice_id)
            
            if not invoice:
                return False
            
            # Simulate payment success/failure
            payment_success = np.random.random() > 0.1  # 90% success rate
            
            if payment_success:
                invoice.status = PaymentStatus.PAID
                invoice.paid_date = datetime.now()
                invoice.stripe_invoice_id = f"pi_{invoice_id}"
                
                logger.info("Payment processed successfully",
                           invoice_id=invoice_id,
                           amount=invoice.amount)
            else:
                invoice.status = PaymentStatus.FAILED
                
                logger.warning("Payment processing failed",
                              invoice_id=invoice_id)
            
            return payment_success
            
        except Exception as e:
            logger.error("Payment processing failed", error=str(e))
            raise
    
    def get_billing_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get billing history"""
        try:
            # Mock billing history
            history = []
            
            for i in range(limit):
                history.append({
                    "invoice_id": f"inv_{user_id}_{i}",
                    "amount": np.random.uniform(99, 999),
                    "currency": "USD",
                    "status": np.random.choice(["paid", "pending", "failed"]),
                    "date": datetime.now() - timedelta(days=i*30),
                    "description": f"Subscription payment - {np.random.choice(['Basic', 'Pro', 'Enterprise'])}"
                })
            
            return history
            
        except Exception as e:
            logger.error("Billing history retrieval failed", error=str(e))
            raise
    
    def get_available_plans(self) -> List[Dict[str, Any]]:
        """Get available subscription plans"""
        return [
            {
                "plan_type": plan_type,
                "name": plan_data["name"],
                "price_monthly": plan_data["price_monthly"],
                "price_yearly": plan_data["price_yearly"],
                "features": plan_data["features"],
                "limits": plan_data["limits"]
            }
            for plan_type, plan_data in self.plans.items()
        ]
    
    def calculate_pricing(self, plan_type: PlanType, billing_cycle: BillingCycle) -> Dict[str, Any]:
        """Calculate pricing for plan and billing cycle"""
        plan = self.plans[plan_type.value]
        
        if billing_cycle == BillingCycle.MONTHLY:
            amount = plan["price_monthly"]
        elif billing_cycle == BillingCycle.YEARLY:
            amount = plan["price_yearly"]
        else:  # QUARTERLY
            amount = plan["price_monthly"] * 3
        
        return {
            "plan_type": plan_type.value,
            "billing_cycle": billing_cycle.value,
            "amount": amount,
            "currency": "USD",
            "savings": plan["price_monthly"] * 12 - plan["price_yearly"] if billing_cycle == BillingCycle.YEARLY else 0
        }
    
    def _get_user_subscription(self, user_id: str) -> Optional[Subscription]:
        """Get user subscription (mock implementation)"""
        # Mock subscription data
        if user_id in self.billing_history:
            return self.billing_history[user_id]
        
        # Create mock subscription for new user
        subscription = Subscription(
            user_id=user_id,
            plan_type=PlanType.BASIC,
            billing_cycle=BillingCycle.MONTHLY,
            status="active",
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now() + timedelta(days=30),
            amount=99.00,
            currency="USD",
            features=self.plans["basic"]["features"]
        )
        
        self.billing_history[user_id] = subscription
        return subscription
    
    def _get_invoice(self, invoice_id: str) -> Optional[Invoice]:
        """Get invoice by ID (mock implementation)"""
        # Mock invoice retrieval
        return Invoice(
            invoice_id=invoice_id,
            user_id="mock_user",
            amount=99.00,
            currency="USD",
            status=PaymentStatus.PENDING,
            due_date=datetime.now() + timedelta(days=30),
            items=[{"description": "Subscription", "amount": 99.00}]
        )

# Global billing service instance
billing_service = BillingService()
