"""
Billing Service using Stripe v16.9.0
Provides subscription management and payment processing
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import structlog
from enum import Enum

logger = structlog.get_logger(__name__)

try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    logger.warning("Stripe not available - using mock billing service")

class SubscriptionTier(Enum):
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"

class BillingService:
    """Billing service for subscription management and payments"""
    
    def __init__(self):
        self.stripe_available = STRIPE_AVAILABLE
        
        if self.stripe_available:
            # Initialize Stripe (use test keys in development)
            stripe.api_key = "sk_test_demo_key_replace_with_real_key"
            self.webhook_secret = "whsec_demo_webhook_secret"
        else:
            logger.warning("Stripe not available - using mock billing service")
        
        # Subscription plans
        self.subscription_plans = {
            'basic': {
                'name': 'Basic Plan',
                'price': 99.00,
                'currency': 'usd',
                'interval': 'month',
                'features': [
                    'Up to 100 trades per month',
                    'Basic analytics',
                    'Email support',
                    'Standard compliance reporting'
                ],
                'limits': {
                    'trades_per_month': 100,
                    'api_calls_per_day': 1000,
                    'storage_gb': 1
                }
            },
            'professional': {
                'name': 'Professional Plan',
                'price': 299.00,
                'currency': 'usd',
                'interval': 'month',
                'features': [
                    'Up to 1000 trades per month',
                    'Advanced analytics with AI forecasting',
                    'Priority support',
                    'Advanced compliance reporting',
                    'Quantum optimization (limited)'
                ],
                'limits': {
                    'trades_per_month': 1000,
                    'api_calls_per_day': 10000,
                    'storage_gb': 10
                }
            },
            'enterprise': {
                'name': 'Enterprise Plan',
                'price': 999.00,
                'currency': 'usd',
                'interval': 'month',
                'features': [
                    'Unlimited trades',
                    'Full AI and quantum features',
                    '24/7 dedicated support',
                    'Custom compliance reporting',
                    'Blockchain integration',
                    'White-label options'
                ],
                'limits': {
                    'trades_per_month': -1,  # Unlimited
                    'api_calls_per_day': -1,  # Unlimited
                    'storage_gb': 100
                }
            }
        }
    
    def create_customer(self, user_data: Dict) -> Dict:
        """
        Create a new Stripe customer
        
        Args:
            user_data: User information including email, name, etc.
            
        Returns:
            Dictionary containing customer information
        """
        try:
            logger.info("Creating Stripe customer", email=user_data.get('email'))
            
            if self.stripe_available:
                customer = stripe.Customer.create(
                    email=user_data.get('email'),
                    name=user_data.get('name'),
                    metadata={
                        'user_id': user_data.get('user_id'),
                        'created_at': datetime.now().isoformat()
                    }
                )
                
                result = {
                    'customer_id': customer.id,
                    'email': customer.email,
                    'name': customer.name,
                    'created_at': datetime.now().isoformat(),
                    'subscription_status': 'none'
                }
            else:
                # Mock customer creation
                result = self._mock_create_customer(user_data)
            
            logger.info("Customer created successfully", customer_id=result['customer_id'])
            return result
            
        except Exception as e:
            logger.error("Customer creation failed", error=str(e))
            raise Exception(f"Customer creation failed: {str(e)}")
    
    def _mock_create_customer(self, user_data: Dict) -> Dict:
        """Mock customer creation for testing"""
        import hashlib
        import time
        
        customer_id = f"cus_mock_{hashlib.sha256(f"{user_data.get('email')}{time.time()}".encode()).hexdigest()[:16]}"
        
        return {
            'customer_id': customer_id,
            'email': user_data.get('email'),
            'name': user_data.get('name'),
            'created_at': datetime.now().isoformat(),
            'subscription_status': 'none',
            'note': 'This is a mock customer for demonstration purposes'
        }
    
    def create_subscription(self, 
                           customer_id: str, 
                           plan_tier: str,
                           payment_method_id: Optional[str] = None) -> Dict:
        """
        Create a subscription for a customer
        
        Args:
            customer_id: Stripe customer ID
            plan_tier: Subscription plan tier
            payment_method_id: Payment method ID (optional)
            
        Returns:
            Dictionary containing subscription information
        """
        try:
            logger.info("Creating subscription", 
                       customer_id=customer_id, 
                       plan_tier=plan_tier)
            
            if plan_tier not in self.subscription_plans:
                raise ValueError(f"Invalid plan tier: {plan_tier}")
            
            plan = self.subscription_plans[plan_tier]
            
            if self.stripe_available:
                # Create Stripe subscription
                subscription = stripe.Subscription.create(
                    customer=customer_id,
                    items=[{
                        'price_data': {
                            'currency': plan['currency'],
                            'product_data': {
                                'name': plan['name'],
                            },
                            'unit_amount': int(plan['price'] * 100),  # Convert to cents
                            'recurring': {
                                'interval': plan['interval'],
                            },
                        },
                    }],
                    payment_behavior='default_incomplete',
                    payment_settings={'save_default_payment_method': 'on_subscription'},
                    expand=['latest_invoice.payment_intent'],
                )
                
                result = {
                    'subscription_id': subscription.id,
                    'customer_id': customer_id,
                    'plan_tier': plan_tier,
                    'status': subscription.status,
                    'current_period_start': datetime.fromtimestamp(subscription.current_period_start).isoformat(),
                    'current_period_end': datetime.fromtimestamp(subscription.current_period_end).isoformat(),
                    'price': plan['price'],
                    'currency': plan['currency'],
                    'created_at': datetime.now().isoformat()
                }
            else:
                # Mock subscription creation
                result = self._mock_create_subscription(customer_id, plan_tier, plan)
            
            logger.info("Subscription created successfully", 
                       subscription_id=result['subscription_id'])
            return result
            
        except Exception as e:
            logger.error("Subscription creation failed", error=str(e))
            raise Exception(f"Subscription creation failed: {str(e)}")
    
    def _mock_create_subscription(self, customer_id: str, plan_tier: str, plan: Dict) -> Dict:
        """Mock subscription creation for testing"""
        import hashlib
        import time
        
        subscription_id = f"sub_mock_{hashlib.sha256(f"{customer_id}{plan_tier}{time.time()}".encode()).hexdigest()[:16]}"
        
        return {
            'subscription_id': subscription_id,
            'customer_id': customer_id,
            'plan_tier': plan_tier,
            'status': 'active',
            'current_period_start': datetime.now().isoformat(),
            'current_period_end': (datetime.now() + timedelta(days=30)).isoformat(),
            'price': plan['price'],
            'currency': plan['currency'],
            'created_at': datetime.now().isoformat(),
            'note': 'This is a mock subscription for demonstration purposes'
        }
    
    def get_subscription(self, subscription_id: str) -> Dict:
        """Get subscription details"""
        try:
            logger.info("Retrieving subscription", subscription_id=subscription_id)
            
            if self.stripe_available:
                subscription = stripe.Subscription.retrieve(subscription_id)
                
                result = {
                    'subscription_id': subscription.id,
                    'customer_id': subscription.customer,
                    'status': subscription.status,
                    'current_period_start': datetime.fromtimestamp(subscription.current_period_start).isoformat(),
                    'current_period_end': datetime.fromtimestamp(subscription.current_period_end).isoformat(),
                    'cancel_at_period_end': subscription.cancel_at_period_end,
                    'created_at': datetime.fromtimestamp(subscription.created).isoformat()
                }
            else:
                # Mock subscription retrieval
                result = self._mock_get_subscription(subscription_id)
            
            return result
            
        except Exception as e:
            logger.error("Failed to retrieve subscription", error=str(e))
            raise Exception(f"Failed to retrieve subscription: {str(e)}")
    
    def _mock_get_subscription(self, subscription_id: str) -> Dict:
        """Mock subscription retrieval for testing"""
        return {
            'subscription_id': subscription_id,
            'customer_id': 'cus_mock_customer',
            'status': 'active',
            'current_period_start': datetime.now().isoformat(),
            'current_period_end': (datetime.now() + timedelta(days=30)).isoformat(),
            'cancel_at_period_end': False,
            'created_at': datetime.now().isoformat(),
            'note': 'This is mock subscription data for demonstration purposes'
        }
    
    def cancel_subscription(self, subscription_id: str, immediately: bool = False) -> Dict:
        """Cancel a subscription"""
        try:
            logger.info("Cancelling subscription", 
                       subscription_id=subscription_id, 
                       immediately=immediately)
            
            if self.stripe_available:
                if immediately:
                    subscription = stripe.Subscription.delete(subscription_id)
                    status = 'cancelled'
                else:
                    subscription = stripe.Subscription.modify(
                        subscription_id,
                        cancel_at_period_end=True
                    )
                    status = 'cancelling'
                
                result = {
                    'subscription_id': subscription_id,
                    'status': status,
                    'cancelled_at': datetime.now().isoformat(),
                    'cancel_at_period_end': subscription.cancel_at_period_end
                }
            else:
                # Mock subscription cancellation
                result = self._mock_cancel_subscription(subscription_id, immediately)
            
            logger.info("Subscription cancelled", subscription_id=subscription_id)
            return result
            
        except Exception as e:
            logger.error("Subscription cancellation failed", error=str(e))
            raise Exception(f"Subscription cancellation failed: {str(e)}")
    
    def _mock_cancel_subscription(self, subscription_id: str, immediately: bool) -> Dict:
        """Mock subscription cancellation for testing"""
        return {
            'subscription_id': subscription_id,
            'status': 'cancelled' if immediately else 'cancelling',
            'cancelled_at': datetime.now().isoformat(),
            'cancel_at_period_end': not immediately,
            'note': 'This is mock cancellation data for demonstration purposes'
        }
    
    def create_payment_intent(self, 
                             amount: float, 
                             currency: str = 'usd',
                             customer_id: Optional[str] = None) -> Dict:
        """Create a payment intent for one-time payments"""
        try:
            logger.info("Creating payment intent", 
                       amount=amount, 
                       currency=currency,
                       customer_id=customer_id)
            
            if self.stripe_available:
                payment_intent = stripe.PaymentIntent.create(
                    amount=int(amount * 100),  # Convert to cents
                    currency=currency,
                    customer=customer_id,
                    metadata={
                        'created_at': datetime.now().isoformat()
                    }
                )
                
                result = {
                    'payment_intent_id': payment_intent.id,
                    'amount': amount,
                    'currency': currency,
                    'status': payment_intent.status,
                    'client_secret': payment_intent.client_secret,
                    'created_at': datetime.now().isoformat()
                }
            else:
                # Mock payment intent creation
                result = self._mock_create_payment_intent(amount, currency, customer_id)
            
            logger.info("Payment intent created", 
                       payment_intent_id=result['payment_intent_id'])
            return result
            
        except Exception as e:
            logger.error("Payment intent creation failed", error=str(e))
            raise Exception(f"Payment intent creation failed: {str(e)}")
    
    def _mock_create_payment_intent(self, amount: float, currency: str, customer_id: Optional[str]) -> Dict:
        """Mock payment intent creation for testing"""
        import hashlib
        import time
        
        payment_intent_id = f"pi_mock_{hashlib.sha256(f"{amount}{currency}{time.time()}".encode()).hexdigest()[:16]}"
        
        return {
            'payment_intent_id': payment_intent_id,
            'amount': amount,
            'currency': currency,
            'status': 'requires_payment_method',
            'client_secret': f"{payment_intent_id}_secret_mock",
            'created_at': datetime.now().isoformat(),
            'note': 'This is a mock payment intent for demonstration purposes'
        }
    
    def get_usage_stats(self, customer_id: str, period_start: datetime, period_end: datetime) -> Dict:
        """Get usage statistics for billing"""
        try:
            logger.info("Retrieving usage stats", 
                       customer_id=customer_id,
                       period_start=period_start.isoformat(),
                       period_end=period_end.isoformat())
            
            # Mock usage statistics
            usage_stats = {
                'customer_id': customer_id,
                'period': {
                    'start': period_start.isoformat(),
                    'end': period_end.isoformat()
                },
                'trades_count': 150,  # Mock data
                'api_calls_count': 5000,  # Mock data
                'storage_used_gb': 2.5,  # Mock data
                'forecasting_requests': 25,  # Mock data
                'quantum_optimizations': 10,  # Mock data
                'blockchain_transactions': 5,  # Mock data
                'generated_at': datetime.now().isoformat()
            }
            
            logger.info("Usage stats retrieved", customer_id=customer_id)
            return usage_stats
            
        except Exception as e:
            logger.error("Failed to retrieve usage stats", error=str(e))
            raise Exception(f"Failed to retrieve usage stats: {str(e)}")
    
    def get_available_plans(self) -> Dict:
        """Get available subscription plans"""
        return {
            'plans': self.subscription_plans,
            'generated_at': datetime.now().isoformat()
        }

# Global instance
billing_service = BillingService()
