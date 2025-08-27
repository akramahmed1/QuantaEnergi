import stripe
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import structlog
from ..core.config import settings

logger = structlog.get_logger()

# Initialize Stripe
if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY

class BillingService:
    """Billing service with Stripe integration for subscription management"""
    
    def __init__(self):
        self.plans = {
            "basic": {
                "name": "Basic Plan",
                "price": 99,
                "currency": "usd",
                "interval": "month",
                "features": [
                    "Real-time market data",
                    "Basic forecasting",
                    "Email support",
                    "5 API calls/minute"
                ],
                "stripe_price_id": "price_basic_monthly"
            },
            "pro": {
                "name": "Professional Plan",
                "price": 299,
                "currency": "usd",
                "interval": "month",
                "features": [
                    "All Basic features",
                    "Advanced AI forecasting",
                    "Optimization engine",
                    "Priority support",
                    "25 API calls/minute",
                    "Custom dashboards"
                ],
                "stripe_price_id": "price_pro_monthly"
            },
            "enterprise": {
                "name": "Enterprise Plan",
                "price": 999,
                "currency": "usd",
                "interval": "month",
                "features": [
                    "All Pro features",
                    "Custom integrations",
                    "Dedicated support",
                    "Unlimited API calls",
                    "White-label solution",
                    "SLA guarantee"
                ],
                "stripe_price_id": "price_enterprise_monthly"
            }
        }
    
    async def create_customer(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Stripe customer"""
        try:
            if not settings.STRIPE_SECRET_KEY:
                return {"error": "Stripe not configured"}
            
            customer = stripe.Customer.create(
                email=user_data["email"],
                name=user_data["company_name"],
                metadata={
                    "user_id": user_data["id"],
                    "role": user_data["role"]
                }
            )
            
            logger.info(f"Created Stripe customer {customer.id} for user {user_data['email']}")
            
            return {
                "customer_id": customer.id,
                "email": customer.email,
                "created_at": datetime.fromtimestamp(customer.created).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating Stripe customer: {e}")
            return {"error": str(e)}
    
    async def create_subscription(self, customer_id: str, plan_name: str) -> Dict[str, Any]:
        """Create a subscription for a customer"""
        try:
            if not settings.STRIPE_SECRET_KEY:
                return {"error": "Stripe not configured"}
            
            if plan_name not in self.plans:
                return {"error": f"Invalid plan: {plan_name}"}
            
            plan = self.plans[plan_name]
            
            # Create subscription
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": plan["stripe_price_id"]}],
                payment_behavior="default_incomplete",
                payment_settings={"save_default_payment_method": "on_subscription"},
                expand=["latest_invoice.payment_intent"]
            )
            
            logger.info(f"Created subscription {subscription.id} for customer {customer_id}")
            
            return {
                "subscription_id": subscription.id,
                "plan_name": plan_name,
                "status": subscription.status,
                "current_period_start": datetime.fromtimestamp(subscription.current_period_start).isoformat(),
                "current_period_end": datetime.fromtimestamp(subscription.current_period_end).isoformat(),
                "amount": plan["price"],
                "currency": plan["currency"]
            }
            
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            return {"error": str(e)}
    
    async def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Cancel a subscription"""
        try:
            if not settings.STRIPE_SECRET_KEY:
                return {"error": "Stripe not configured"}
            
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
            
            logger.info(f"Cancelled subscription {subscription_id}")
            
            return {
                "subscription_id": subscription_id,
                "status": "cancelled",
                "cancel_at": datetime.fromtimestamp(subscription.cancel_at).isoformat() if subscription.cancel_at else None,
                "cancelled_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error cancelling subscription: {e}")
            return {"error": str(e)}
    
    async def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Get subscription details"""
        try:
            if not settings.STRIPE_SECRET_KEY:
                return {"error": "Stripe not configured"}
            
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "plan_name": self._get_plan_name_by_price_id(subscription.items.data[0].price.id),
                "current_period_start": datetime.fromtimestamp(subscription.current_period_start).isoformat(),
                "current_period_end": datetime.fromtimestamp(subscription.current_period_end).isoformat(),
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "cancel_at": datetime.fromtimestamp(subscription.cancel_at).isoformat() if subscription.cancel_at else None
            }
            
        except Exception as e:
            logger.error(f"Error retrieving subscription: {e}")
            return {"error": str(e)}
    
    async def update_subscription(self, subscription_id: str, new_plan: str) -> Dict[str, Any]:
        """Update subscription to a different plan"""
        try:
            if not settings.STRIPE_SECRET_KEY:
                return {"error": "Stripe not configured"}
            
            if new_plan not in self.plans:
                return {"error": f"Invalid plan: {new_plan}"}
            
            new_plan_data = self.plans[new_plan]
            
            # Get current subscription
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            # Update subscription
            updated_subscription = stripe.Subscription.modify(
                subscription_id,
                items=[{
                    "id": subscription.items.data[0].id,
                    "price": new_plan_data["stripe_price_id"]
                }],
                proration_behavior="create_prorations"
            )
            
            logger.info(f"Updated subscription {subscription_id} to {new_plan}")
            
            return {
                "subscription_id": subscription_id,
                "new_plan": new_plan,
                "status": updated_subscription.status,
                "proration_date": datetime.fromtimestamp(updated_subscription.created).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error updating subscription: {e}")
            return {"error": str(e)}
    
    async def get_invoice_history(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get invoice history for a customer"""
        try:
            if not settings.STRIPE_SECRET_KEY:
                return [{"error": "Stripe not configured"}]
            
            invoices = stripe.Invoice.list(customer=customer_id, limit=12)
            
            invoice_history = []
            for invoice in invoices.data:
                invoice_history.append({
                    "invoice_id": invoice.id,
                    "amount": invoice.amount_paid / 100,  # Convert from cents
                    "currency": invoice.currency,
                    "status": invoice.status,
                    "created": datetime.fromtimestamp(invoice.created).isoformat(),
                    "period_start": datetime.fromtimestamp(invoice.period_start).isoformat() if invoice.period_start else None,
                    "period_end": datetime.fromtimestamp(invoice.period_end).isoformat() if invoice.period_end else None
                })
            
            return invoice_history
            
        except Exception as e:
            logger.error(f"Error retrieving invoice history: {e}")
            return [{"error": str(e)}]
    
    async def create_payment_method(self, customer_id: str, payment_method_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a payment method for a customer"""
        try:
            if not settings.STRIPE_SECRET_KEY:
                return {"error": "Stripe not configured"}
            
            # Create payment method
            payment_method = stripe.PaymentMethod.create(
                type="card",
                card=payment_method_data["card"],
                billing_details=payment_method_data["billing_details"]
            )
            
            # Attach to customer
            payment_method.attach(customer=customer_id)
            
            logger.info(f"Created payment method {payment_method.id} for customer {customer_id}")
            
            return {
                "payment_method_id": payment_method.id,
                "type": payment_method.type,
                "card_last4": payment_method.card.last4,
                "card_brand": payment_method.card.brand,
                "exp_month": payment_method.card.exp_month,
                "exp_year": payment_method.card.exp_year
            }
            
        except Exception as e:
            logger.error(f"Error creating payment method: {e}")
            return {"error": str(e)}
    
    async def get_usage_metrics(self, customer_id: str, period: str = "month") -> Dict[str, Any]:
        """Get usage metrics for billing purposes"""
        try:
            # This would typically integrate with your usage tracking system
            # For now, return simulated data
            
            current_month = datetime.now().month
            base_usage = 1000 + (hash(customer_id) % 500)
            
            usage_data = {
                "customer_id": customer_id,
                "period": period,
                "api_calls": base_usage + (current_month * 50),
                "data_processed_gb": (base_usage / 100) + (current_month * 0.5),
                "forecast_queries": base_usage // 10 + (current_month * 5),
                "optimization_runs": base_usage // 20 + (current_month * 2),
                "timestamp": datetime.now().isoformat()
            }
            
            return usage_data
            
        except Exception as e:
            logger.error(f"Error getting usage metrics: {e}")
            return {"error": str(e)}
    
    async def calculate_bill(self, customer_id: str, plan_name: str, usage_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate bill based on plan and usage"""
        try:
            if plan_name not in self.plans:
                return {"error": f"Invalid plan: {plan_name}"}
            
            plan = self.plans[plan_name]
            base_price = plan["price"]
            
            # Calculate overage charges
            overage_charges = 0
            
            # API call overages (if applicable)
            if plan_name == "basic" and usage_metrics["api_calls"] > 7200:  # 5 calls/min * 24 * 60
                overage_calls = usage_metrics["api_calls"] - 7200
                overage_charges += overage_calls * 0.001  # $0.001 per call
            
            elif plan_name == "pro" and usage_metrics["api_calls"] > 36000:  # 25 calls/min * 24 * 60
                overage_calls = usage_metrics["api_calls"] - 36000
                overage_charges += overage_calls * 0.0005  # $0.0005 per call
            
            # Data processing overages
            if usage_metrics["data_processed_gb"] > 100:  # 100GB included
                overage_gb = usage_metrics["data_processed_gb"] - 100
                overage_charges += overage_gb * 0.10  # $0.10 per GB
            
            total_bill = base_price + overage_charges
            
            return {
                "plan_name": plan_name,
                "base_price": base_price,
                "overage_charges": round(overage_charges, 2),
                "total_bill": round(total_bill, 2),
                "currency": plan["currency"],
                "usage_summary": usage_metrics,
                "billing_period": datetime.now().strftime("%B %Y")
            }
            
        except Exception as e:
            logger.error(f"Error calculating bill: {e}")
            return {"error": str(e)}
    
    def get_available_plans(self) -> Dict[str, Any]:
        """Get available subscription plans"""
        return {
            "plans": self.plans,
            "currency": "usd",
            "billing_interval": "monthly",
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_plan_name_by_price_id(self, price_id: str) -> str:
        """Get plan name by Stripe price ID"""
        for plan_name, plan_data in self.plans.items():
            if plan_data["stripe_price_id"] == price_id:
                return plan_name
        return "unknown"
    
    async def handle_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Stripe webhook events"""
        try:
            if not settings.STRIPE_WEBHOOK_SECRET:
                return {"error": "Webhook secret not configured"}
            
            event_type = webhook_data.get("type")
            
            if event_type == "invoice.payment_succeeded":
                return await self._handle_payment_succeeded(webhook_data)
            elif event_type == "invoice.payment_failed":
                return await self._handle_payment_failed(webhook_data)
            elif event_type == "customer.subscription.deleted":
                return await self._handle_subscription_deleted(webhook_data)
            else:
                return {"status": "ignored", "event_type": event_type}
                
        except Exception as e:
            logger.error(f"Error handling webhook: {e}")
            return {"error": str(e)}
    
    async def _handle_payment_succeeded(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle successful payment webhook"""
        try:
            invoice = webhook_data.get("data", {}).get("object", {})
            customer_id = invoice.get("customer")
            subscription_id = invoice.get("subscription")
            
            logger.info(f"Payment succeeded for customer {customer_id}, subscription {subscription_id}")
            
            return {
                "status": "processed",
                "event": "payment_succeeded",
                "customer_id": customer_id,
                "subscription_id": subscription_id,
                "amount": invoice.get("amount_paid", 0) / 100
            }
            
        except Exception as e:
            logger.error(f"Error handling payment succeeded: {e}")
            return {"error": str(e)}
    
    async def _handle_payment_failed(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle failed payment webhook"""
        try:
            invoice = webhook_data.get("data", {}).get("object", {})
            customer_id = invoice.get("customer")
            subscription_id = invoice.get("subscription")
            
            logger.warning(f"Payment failed for customer {customer_id}, subscription {subscription_id}")
            
            return {
                "status": "processed",
                "event": "payment_failed",
                "customer_id": customer_id,
                "subscription_id": subscription_id,
                "next_payment_attempt": invoice.get("next_payment_attempt")
            }
            
        except Exception as e:
            logger.error(f"Error handling payment failed: {e}")
            return {"error": str(e)}
    
    async def _handle_subscription_deleted(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription deletion webhook"""
        try:
            subscription = webhook_data.get("data", {}).get("object", {})
            customer_id = subscription.get("customer")
            subscription_id = subscription.get("id")
            
            logger.info(f"Subscription {subscription_id} deleted for customer {customer_id}")
            
            return {
                "status": "processed",
                "event": "subscription_deleted",
                "customer_id": customer_id,
                "subscription_id": subscription_id
            }
            
        except Exception as e:
            logger.error(f"Error handling subscription deleted: {e}")
            return {"error": str(e)}

# Global instance
billing_service = BillingService()
