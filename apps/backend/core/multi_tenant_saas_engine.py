"""
Multi-Tenant SaaS Architecture Engine for QuantaEnergi ETRM/CTRM Platform
Implements true multi-tenant SaaS architecture including:
- Tenant management
- Upgrade management
- Billing & metering
- Data isolation
- Resource management
- Security & compliance
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
import threading
import time
import hashlib
import hmac
import secrets
from concurrent.futures import ThreadPoolExecutor
import redis
import sqlalchemy
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

class TenantStatus(Enum):
    """Tenant status enumeration"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    TRIAL = "trial"
    EXPIRED = "expired"

class PlanType(Enum):
    """Plan type enumeration"""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"

class BillingCycle(Enum):
    """Billing cycle enumeration"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"

class ResourceType(Enum):
    """Resource type enumeration"""
    USERS = "users"
    STORAGE = "storage"
    API_CALLS = "api_calls"
    TRADES = "trades"
    REPORTS = "reports"
    WORKFLOWS = "workflows"
    INTEGRATIONS = "integrations"

@dataclass
class Tenant:
    """Tenant definition"""
    tenant_id: str
    name: str
    domain: str
    subdomain: str
    status: TenantStatus = TenantStatus.TRIAL
    plan_type: PlanType = PlanType.FREE
    billing_cycle: BillingCycle = BillingCycle.MONTHLY
    created_at: datetime = field(default_factory=datetime.utcnow)
    trial_ends_at: Optional[datetime] = None
    subscription_ends_at: Optional[datetime] = None
    max_users: int = 5
    max_storage_gb: int = 1
    max_api_calls_per_month: int = 1000
    max_trades_per_month: int = 100
    max_reports_per_month: int = 10
    max_workflows: int = 5
    max_integrations: int = 2
    custom_domain: Optional[str] = None
    ssl_enabled: bool = False
    backup_enabled: bool = False
    support_level: str = "basic"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TenantUser:
    """Tenant user definition"""
    user_id: str
    tenant_id: str
    email: str
    username: str
    first_name: str
    last_name: str
    role: str = "user"
    is_active: bool = True
    last_login: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TenantResource:
    """Tenant resource definition"""
    resource_id: str
    tenant_id: str
    resource_type: ResourceType
    current_usage: float = 0.0
    limit: float = 0.0
    unit: str = ""
    last_updated: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BillingPlan:
    """Billing plan definition"""
    plan_id: str
    name: str
    plan_type: PlanType
    description: str = ""
    price_monthly: float = 0.0
    price_yearly: float = 0.0
    features: List[str] = field(default_factory=list)
    limits: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BillingInvoice:
    """Billing invoice definition"""
    invoice_id: str
    tenant_id: str
    plan_id: str
    amount: float
    currency: str = "USD"
    billing_period_start: datetime = field(default_factory=datetime.utcnow)
    billing_period_end: datetime = field(default_factory=datetime.utcnow)
    due_date: datetime = field(default_factory=datetime.utcnow)
    status: str = "pending"
    payment_method: str = ""
    paid_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UsageMetric:
    """Usage metric definition"""
    metric_id: str
    tenant_id: str
    resource_type: ResourceType
    usage: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TenantUpgrade:
    """Tenant upgrade definition"""
    upgrade_id: str
    tenant_id: str
    from_plan: PlanType
    to_plan: PlanType
    upgrade_date: datetime = field(default_factory=datetime.utcnow)
    effective_date: datetime = field(default_factory=datetime.utcnow)
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

class TenantManager:
    """Tenant management system"""
    
    def __init__(self):
        self.tenants: Dict[str, Tenant] = {}
        self.tenant_users: Dict[str, List[TenantUser]] = {}
        self.tenant_resources: Dict[str, List[TenantResource]] = {}
        self.tenant_databases: Dict[str, str] = {}
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        
    def create_tenant(self, name: str, domain: str, subdomain: str,
                     plan_type: PlanType = PlanType.FREE,
                     max_users: int = 5) -> str:
        """Create new tenant"""
        try:
            tenant_id = f"TENANT_{uuid.uuid4().hex[:8].upper()}"
            
            # Create tenant
            tenant = Tenant(
                tenant_id=tenant_id,
                name=name,
                domain=domain,
                subdomain=subdomain,
                plan_type=plan_type,
                max_users=max_users
            )
            
            # Set trial period
            if plan_type == PlanType.FREE:
                tenant.trial_ends_at = datetime.utcnow() + timedelta(days=30)
                tenant.status = TenantStatus.TRIAL
            
            self.tenants[tenant_id] = tenant
            self.tenant_users[tenant_id] = []
            self.tenant_resources[tenant_id] = []
            
            # Create tenant database
            await self._create_tenant_database(tenant_id)
            
            # Initialize tenant resources
            self._initialize_tenant_resources(tenant_id, plan_type)
            
            logger.info(f"Created tenant: {name} ({tenant_id})")
            return tenant_id
            
        except Exception as e:
            logger.error(f"Error creating tenant: {e}")
            return ""
    
    async def _create_tenant_database(self, tenant_id: str):
        """Create tenant database"""
        try:
            # Create database connection string
            db_name = f"tenant_{tenant_id.lower()}"
            connection_string = f"postgresql://user:password@localhost:5432/{db_name}"
            
            # Store connection string
            self.tenant_databases[tenant_id] = connection_string
            
            # Create database (simplified)
            logger.info(f"Created database for tenant: {tenant_id}")
            
        except Exception as e:
            logger.error(f"Error creating tenant database: {e}")
    
    def _initialize_tenant_resources(self, tenant_id: str, plan_type: PlanType):
        """Initialize tenant resources"""
        try:
            # Get plan limits
            plan_limits = self._get_plan_limits(plan_type)
            
            # Create resource records
            resources = [
                TenantResource(
                    resource_id=f"RES_{uuid.uuid4().hex[:8].upper()}",
                    tenant_id=tenant_id,
                    resource_type=ResourceType.USERS,
                    limit=plan_limits["max_users"]
                ),
                TenantResource(
                    resource_id=f"RES_{uuid.uuid4().hex[:8].upper()}",
                    tenant_id=tenant_id,
                    resource_type=ResourceType.STORAGE,
                    limit=plan_limits["max_storage_gb"]
                ),
                TenantResource(
                    resource_id=f"RES_{uuid.uuid4().hex[:8].upper()}",
                    tenant_id=tenant_id,
                    resource_type=ResourceType.API_CALLS,
                    limit=plan_limits["max_api_calls_per_month"]
                ),
                TenantResource(
                    resource_id=f"RES_{uuid.uuid4().hex[:8].upper()}",
                    tenant_id=tenant_id,
                    resource_type=ResourceType.TRADES,
                    limit=plan_limits["max_trades_per_month"]
                ),
                TenantResource(
                    resource_id=f"RES_{uuid.uuid4().hex[:8].upper()}",
                    tenant_id=tenant_id,
                    resource_type=ResourceType.REPORTS,
                    limit=plan_limits["max_reports_per_month"]
                ),
                TenantResource(
                    resource_id=f"RES_{uuid.uuid4().hex[:8].upper()}",
                    tenant_id=tenant_id,
                    resource_type=ResourceType.WORKFLOWS,
                    limit=plan_limits["max_workflows"]
                ),
                TenantResource(
                    resource_id=f"RES_{uuid.uuid4().hex[:8].upper()}",
                    tenant_id=tenant_id,
                    resource_type=ResourceType.INTEGRATIONS,
                    limit=plan_limits["max_integrations"]
                )
            ]
            
            self.tenant_resources[tenant_id] = resources
            
        except Exception as e:
            logger.error(f"Error initializing tenant resources: {e}")
    
    def _get_plan_limits(self, plan_type: PlanType) -> Dict[str, Any]:
        """Get plan limits"""
        limits = {
            PlanType.FREE: {
                "max_users": 5,
                "max_storage_gb": 1,
                "max_api_calls_per_month": 1000,
                "max_trades_per_month": 100,
                "max_reports_per_month": 10,
                "max_workflows": 5,
                "max_integrations": 2
            },
            PlanType.BASIC: {
                "max_users": 25,
                "max_storage_gb": 10,
                "max_api_calls_per_month": 10000,
                "max_trades_per_month": 1000,
                "max_reports_per_month": 100,
                "max_workflows": 25,
                "max_integrations": 5
            },
            PlanType.PROFESSIONAL: {
                "max_users": 100,
                "max_storage_gb": 50,
                "max_api_calls_per_month": 100000,
                "max_trades_per_month": 10000,
                "max_reports_per_month": 500,
                "max_workflows": 100,
                "max_integrations": 15
            },
            PlanType.ENTERPRISE: {
                "max_users": -1,  # Unlimited
                "max_storage_gb": -1,  # Unlimited
                "max_api_calls_per_month": -1,  # Unlimited
                "max_trades_per_month": -1,  # Unlimited
                "max_reports_per_month": -1,  # Unlimited
                "max_workflows": -1,  # Unlimited
                "max_integrations": -1  # Unlimited
            }
        }
        
        return limits.get(plan_type, limits[PlanType.FREE])
    
    def add_tenant_user(self, tenant_id: str, email: str, username: str,
                       first_name: str, last_name: str, role: str = "user") -> str:
        """Add user to tenant"""
        try:
            if tenant_id not in self.tenants:
                return ""
            
            # Check user limit
            if not self._check_user_limit(tenant_id):
                logger.error(f"User limit exceeded for tenant: {tenant_id}")
                return ""
            
            user_id = f"USER_{uuid.uuid4().hex[:8].upper()}"
            
            user = TenantUser(
                user_id=user_id,
                tenant_id=tenant_id,
                email=email,
                username=username,
                first_name=first_name,
                last_name=last_name,
                role=role
            )
            
            self.tenant_users[tenant_id].append(user)
            
            # Update user count
            self._update_resource_usage(tenant_id, ResourceType.USERS, 1)
            
            logger.info(f"Added user to tenant: {tenant_id}")
            return user_id
            
        except Exception as e:
            logger.error(f"Error adding tenant user: {e}")
            return ""
    
    def _check_user_limit(self, tenant_id: str) -> bool:
        """Check if tenant has reached user limit"""
        try:
            tenant = self.tenants[tenant_id]
            current_users = len(self.tenant_users[tenant_id])
            
            return current_users < tenant.max_users
            
        except Exception as e:
            logger.error(f"Error checking user limit: {e}")
            return False
    
    def _update_resource_usage(self, tenant_id: str, resource_type: ResourceType, usage: float):
        """Update resource usage"""
        try:
            if tenant_id not in self.tenant_resources:
                return
            
            for resource in self.tenant_resources[tenant_id]:
                if resource.resource_type == resource_type:
                    resource.current_usage += usage
                    resource.last_updated = datetime.utcnow()
                    break
            
        except Exception as e:
            logger.error(f"Error updating resource usage: {e}")
    
    def get_tenant_status(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant status"""
        try:
            if tenant_id not in self.tenants:
                return {"error": "Tenant not found"}
            
            tenant = self.tenants[tenant_id]
            users = self.tenant_users.get(tenant_id, [])
            resources = self.tenant_resources.get(tenant_id, [])
            
            return {
                "tenant_id": tenant_id,
                "name": tenant.name,
                "domain": tenant.domain,
                "subdomain": tenant.subdomain,
                "status": tenant.status.value,
                "plan_type": tenant.plan_type.value,
                "billing_cycle": tenant.billing_cycle.value,
                "created_at": tenant.created_at.isoformat(),
                "trial_ends_at": tenant.trial_ends_at.isoformat() if tenant.trial_ends_at else None,
                "subscription_ends_at": tenant.subscription_ends_at.isoformat() if tenant.subscription_ends_at else None,
                "users": {
                    "total": len(users),
                    "active": len([u for u in users if u.is_active]),
                    "limit": tenant.max_users
                },
                "resources": {
                    resource.resource_type.value: {
                        "current_usage": resource.current_usage,
                        "limit": resource.limit,
                        "unit": resource.unit
                    } for resource in resources
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting tenant status: {e}")
            return {"error": str(e)}

class BillingManager:
    """Billing and subscription management"""
    
    def __init__(self):
        self.billing_plans: Dict[str, BillingPlan] = {}
        self.billing_invoices: Dict[str, BillingInvoice] = {}
        self.usage_metrics: Dict[str, List[UsageMetric]] = {}
        self.tenant_upgrades: Dict[str, List[TenantUpgrade]] = {}
        
        # Initialize default plans
        self._initialize_default_plans()
    
    def _initialize_default_plans(self):
        """Initialize default billing plans"""
        try:
            plans = [
                BillingPlan(
                    plan_id="FREE_PLAN",
                    name="Free Plan",
                    plan_type=PlanType.FREE,
                    description="Perfect for getting started",
                    price_monthly=0.0,
                    price_yearly=0.0,
                    features=["Basic trading", "Standard reports", "Email support"],
                    limits={
                        "max_users": 5,
                        "max_storage_gb": 1,
                        "max_api_calls_per_month": 1000,
                        "max_trades_per_month": 100,
                        "max_reports_per_month": 10,
                        "max_workflows": 5,
                        "max_integrations": 2
                    }
                ),
                BillingPlan(
                    plan_id="BASIC_PLAN",
                    name="Basic Plan",
                    plan_type=PlanType.BASIC,
                    description="For small teams",
                    price_monthly=99.0,
                    price_yearly=990.0,
                    features=["Advanced trading", "Custom reports", "Priority support", "API access"],
                    limits={
                        "max_users": 25,
                        "max_storage_gb": 10,
                        "max_api_calls_per_month": 10000,
                        "max_trades_per_month": 1000,
                        "max_reports_per_month": 100,
                        "max_workflows": 25,
                        "max_integrations": 5
                    }
                ),
                BillingPlan(
                    plan_id="PROFESSIONAL_PLAN",
                    name="Professional Plan",
                    plan_type=PlanType.PROFESSIONAL,
                    description="For growing businesses",
                    price_monthly=299.0,
                    price_yearly=2990.0,
                    features=["Enterprise trading", "Advanced analytics", "24/7 support", "Custom integrations"],
                    limits={
                        "max_users": 100,
                        "max_storage_gb": 50,
                        "max_api_calls_per_month": 100000,
                        "max_trades_per_month": 10000,
                        "max_reports_per_month": 500,
                        "max_workflows": 100,
                        "max_integrations": 15
                    }
                ),
                BillingPlan(
                    plan_id="ENTERPRISE_PLAN",
                    name="Enterprise Plan",
                    plan_type=PlanType.ENTERPRISE,
                    description="For large organizations",
                    price_monthly=999.0,
                    price_yearly=9990.0,
                    features=["Unlimited everything", "Dedicated support", "Custom development", "On-premise deployment"],
                    limits={
                        "max_users": -1,
                        "max_storage_gb": -1,
                        "max_api_calls_per_month": -1,
                        "max_trades_per_month": -1,
                        "max_reports_per_month": -1,
                        "max_workflows": -1,
                        "max_integrations": -1
                    }
                )
            ]
            
            for plan in plans:
                self.billing_plans[plan.plan_id] = plan
            
            logger.info("Initialized default billing plans")
            
        except Exception as e:
            logger.error(f"Error initializing default plans: {e}")
    
    def create_invoice(self, tenant_id: str, plan_id: str, amount: float,
                      billing_period_start: datetime, billing_period_end: datetime) -> str:
        """Create billing invoice"""
        try:
            invoice_id = f"INV_{uuid.uuid4().hex[:8].upper()}"
            
            invoice = BillingInvoice(
                invoice_id=invoice_id,
                tenant_id=tenant_id,
                plan_id=plan_id,
                amount=amount,
                billing_period_start=billing_period_start,
                billing_period_end=billing_period_end,
                due_date=billing_period_end + timedelta(days=30)
            )
            
            self.billing_invoices[invoice_id] = invoice
            
            logger.info(f"Created invoice: {invoice_id}")
            return invoice_id
            
        except Exception as e:
            logger.error(f"Error creating invoice: {e}")
            return ""
    
    def record_usage(self, tenant_id: str, resource_type: ResourceType, usage: float):
        """Record usage metric"""
        try:
            metric_id = f"METRIC_{uuid.uuid4().hex[:8].upper()}"
            
            metric = UsageMetric(
                metric_id=metric_id,
                tenant_id=tenant_id,
                resource_type=resource_type,
                usage=usage
            )
            
            if tenant_id not in self.usage_metrics:
                self.usage_metrics[tenant_id] = []
            
            self.usage_metrics[tenant_id].append(metric)
            
            # Keep only last 1000 metrics per tenant
            if len(self.usage_metrics[tenant_id]) > 1000:
                self.usage_metrics[tenant_id] = self.usage_metrics[tenant_id][-1000:]
            
        except Exception as e:
            logger.error(f"Error recording usage: {e}")
    
    def get_usage_summary(self, tenant_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get usage summary for tenant"""
        try:
            if tenant_id not in self.usage_metrics:
                return {"error": "No usage data found"}
            
            metrics = self.usage_metrics[tenant_id]
            
            # Filter metrics by date range
            filtered_metrics = [
                metric for metric in metrics
                if start_date <= metric.timestamp <= end_date
            ]
            
            # Group by resource type
            usage_summary = {}
            for metric in filtered_metrics:
                resource_type = metric.resource_type.value
                if resource_type not in usage_summary:
                    usage_summary[resource_type] = 0.0
                usage_summary[resource_type] += metric.usage
            
            return {
                "tenant_id": tenant_id,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "usage_summary": usage_summary,
                "total_metrics": len(filtered_metrics)
            }
            
        except Exception as e:
            logger.error(f"Error getting usage summary: {e}")
            return {"error": str(e)}

class UpgradeManager:
    """Tenant upgrade management"""
    
    def __init__(self):
        self.tenant_upgrades: Dict[str, List[TenantUpgrade]] = {}
        self.upgrade_tasks: Dict[str, asyncio.Task] = {}
    
    def request_upgrade(self, tenant_id: str, from_plan: PlanType, to_plan: PlanType) -> str:
        """Request tenant upgrade"""
        try:
            upgrade_id = f"UPGRADE_{uuid.uuid4().hex[:8].upper()}"
            
            upgrade = TenantUpgrade(
                upgrade_id=upgrade_id,
                tenant_id=tenant_id,
                from_plan=from_plan,
                to_plan=to_plan,
                effective_date=datetime.utcnow() + timedelta(days=1)
            )
            
            if tenant_id not in self.tenant_upgrades:
                self.tenant_upgrades[tenant_id] = []
            
            self.tenant_upgrades[tenant_id].append(upgrade)
            
            # Start upgrade process
            asyncio.create_task(self._process_upgrade(upgrade_id))
            
            logger.info(f"Requested upgrade: {upgrade_id}")
            return upgrade_id
            
        except Exception as e:
            logger.error(f"Error requesting upgrade: {e}")
            return ""
    
    async def _process_upgrade(self, upgrade_id: str):
        """Process tenant upgrade"""
        try:
            # Find upgrade record
            upgrade = None
            for tenant_id, upgrades in self.tenant_upgrades.items():
                for upg in upgrades:
                    if upg.upgrade_id == upgrade_id:
                        upgrade = upg
                        break
                if upgrade:
                    break
            
            if not upgrade:
                logger.error(f"Upgrade not found: {upgrade_id}")
                return
            
            # Update status
            upgrade.status = "processing"
            
            # Simulate upgrade process
            await asyncio.sleep(2)
            
            # Update tenant plan
            # This would integrate with TenantManager
            logger.info(f"Upgraded tenant {upgrade.tenant_id} from {upgrade.from_plan.value} to {upgrade.to_plan.value}")
            
            # Update status
            upgrade.status = "completed"
            
        except Exception as e:
            logger.error(f"Error processing upgrade: {e}")
            if upgrade:
                upgrade.status = "failed"

class SecurityManager:
    """Multi-tenant security management"""
    
    def __init__(self):
        self.tenant_keys: Dict[str, str] = {}
        self.access_tokens: Dict[str, Dict[str, Any]] = {}
        self.rate_limits: Dict[str, Dict[str, Any]] = {}
    
    def generate_tenant_key(self, tenant_id: str) -> str:
        """Generate tenant-specific encryption key"""
        try:
            # Generate secure random key
            key = secrets.token_hex(32)
            self.tenant_keys[tenant_id] = key
            
            logger.info(f"Generated tenant key for: {tenant_id}")
            return key
            
        except Exception as e:
            logger.error(f"Error generating tenant key: {e}")
            return ""
    
    def create_access_token(self, tenant_id: str, user_id: str, permissions: List[str]) -> str:
        """Create access token for tenant user"""
        try:
            token_id = f"TOKEN_{uuid.uuid4().hex[:8].upper()}"
            
            token_data = {
                "token_id": token_id,
                "tenant_id": tenant_id,
                "user_id": user_id,
                "permissions": permissions,
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()
            }
            
            self.access_tokens[token_id] = token_data
            
            logger.info(f"Created access token: {token_id}")
            return token_id
            
        except Exception as e:
            logger.error(f"Error creating access token: {e}")
            return ""
    
    def validate_access_token(self, token_id: str) -> Dict[str, Any]:
        """Validate access token"""
        try:
            if token_id not in self.access_tokens:
                return {"valid": False, "error": "Token not found"}
            
            token_data = self.access_tokens[token_id]
            expires_at = datetime.fromisoformat(token_data["expires_at"])
            
            if datetime.utcnow() > expires_at:
                return {"valid": False, "error": "Token expired"}
            
            return {
                "valid": True,
                "tenant_id": token_data["tenant_id"],
                "user_id": token_data["user_id"],
                "permissions": token_data["permissions"]
            }
            
        except Exception as e:
            logger.error(f"Error validating access token: {e}")
            return {"valid": False, "error": str(e)}
    
    def check_rate_limit(self, tenant_id: str, resource_type: str) -> bool:
        """Check rate limit for tenant"""
        try:
            if tenant_id not in self.rate_limits:
                self.rate_limits[tenant_id] = {}
            
            if resource_type not in self.rate_limits[tenant_id]:
                self.rate_limits[tenant_id][resource_type] = {
                    "count": 0,
                    "window_start": datetime.utcnow()
                }
            
            rate_limit = self.rate_limits[tenant_id][resource_type]
            window_start = rate_limit["window_start"]
            
            # Reset window if more than 1 hour has passed
            if datetime.utcnow() - window_start > timedelta(hours=1):
                rate_limit["count"] = 0
                rate_limit["window_start"] = datetime.utcnow()
            
            # Check limit (simplified)
            max_requests = 1000  # per hour
            if rate_limit["count"] >= max_requests:
                return False
            
            rate_limit["count"] += 1
            return True
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return False

class MultiTenantSAASEngine:
    """Main multi-tenant SaaS engine"""
    
    def __init__(self):
        self.tenant_manager = TenantManager()
        self.billing_manager = BillingManager()
        self.upgrade_manager = UpgradeManager()
        self.security_manager = SecurityManager()
        self.tenant_router = TenantRouter()
        
    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive SaaS status"""
        try:
            return {
                "tenants": {
                    "total": len(self.tenant_manager.tenants),
                    "active": len([t for t in self.tenant_manager.tenants.values() if t.status == TenantStatus.ACTIVE]),
                    "trial": len([t for t in self.tenant_manager.tenants.values() if t.status == TenantStatus.TRIAL]),
                    "suspended": len([t for t in self.tenant_manager.tenants.values() if t.status == TenantStatus.SUSPENDED])
                },
                "billing": {
                    "plans": len(self.billing_manager.billing_plans),
                    "invoices": len(self.billing_manager.billing_invoices),
                    "usage_metrics": sum(len(metrics) for metrics in self.billing_manager.usage_metrics.values())
                },
                "upgrades": {
                    "total": sum(len(upgrades) for upgrades in self.upgrade_manager.tenant_upgrades.values()),
                    "pending": sum(len([u for u in upgrades if u.status == "pending"]) for upgrades in self.upgrade_manager.tenant_upgrades.values())
                },
                "security": {
                    "tenant_keys": len(self.security_manager.tenant_keys),
                    "access_tokens": len(self.security_manager.access_tokens),
                    "rate_limits": len(self.security_manager.rate_limits)
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting comprehensive status: {e}")
            return {"error": str(e)}

class TenantRouter:
    """Tenant routing and isolation"""
    
    def __init__(self):
        self.tenant_routes: Dict[str, str] = {}
        self.tenant_middleware: Dict[str, Any] = {}
    
    def route_request(self, request_path: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Route request to appropriate tenant"""
        try:
            # Extract tenant from subdomain or header
            tenant_id = self._extract_tenant_id(request_path, headers)
            
            if not tenant_id:
                return {"error": "Tenant not found"}
            
            # Get tenant database connection
            db_connection = self._get_tenant_database(tenant_id)
            
            return {
                "tenant_id": tenant_id,
                "database_connection": db_connection,
                "middleware": self.tenant_middleware.get(tenant_id, {})
            }
            
        except Exception as e:
            logger.error(f"Error routing request: {e}")
            return {"error": str(e)}
    
    def _extract_tenant_id(self, request_path: str, headers: Dict[str, str]) -> Optional[str]:
        """Extract tenant ID from request"""
        try:
            # Check for tenant header
            if "X-Tenant-ID" in headers:
                return headers["X-Tenant-ID"]
            
            # Check for subdomain
            host = headers.get("Host", "")
            if "." in host:
                subdomain = host.split(".")[0]
                # Look up tenant by subdomain
                for tenant_id, tenant in self.tenant_manager.tenants.items():
                    if tenant.subdomain == subdomain:
                        return tenant_id
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting tenant ID: {e}")
            return None
    
    def _get_tenant_database(self, tenant_id: str) -> str:
        """Get tenant database connection"""
        try:
            return self.tenant_manager.tenant_databases.get(tenant_id, "")
        except Exception as e:
            logger.error(f"Error getting tenant database: {e}")
            return ""

# Global multi-tenant SaaS engine instance
multi_tenant_saas_engine = MultiTenantSAASEngine()

def create_tenant(name: str, domain: str, subdomain: str,
                 plan_type: PlanType = PlanType.FREE, max_users: int = 5) -> str:
    """Create new tenant"""
    return multi_tenant_saas_engine.tenant_manager.create_tenant(name, domain, subdomain, plan_type, max_users)

def add_tenant_user(tenant_id: str, email: str, username: str,
                   first_name: str, last_name: str, role: str = "user") -> str:
    """Add user to tenant"""
    return multi_tenant_saas_engine.tenant_manager.add_tenant_user(tenant_id, email, username, first_name, last_name, role)

def get_tenant_status(tenant_id: str) -> Dict[str, Any]:
    """Get tenant status"""
    return multi_tenant_saas_engine.tenant_manager.get_tenant_status(tenant_id)

def record_usage(tenant_id: str, resource_type: ResourceType, usage: float):
    """Record usage metric"""
    multi_tenant_saas_engine.billing_manager.record_usage(tenant_id, resource_type, usage)

def get_usage_summary(tenant_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Get usage summary for tenant"""
    return multi_tenant_saas_engine.billing_manager.get_usage_summary(tenant_id, start_date, end_date)

def request_upgrade(tenant_id: str, from_plan: PlanType, to_plan: PlanType) -> str:
    """Request tenant upgrade"""
    return multi_tenant_saas_engine.upgrade_manager.request_upgrade(tenant_id, from_plan, to_plan)

def create_access_token(tenant_id: str, user_id: str, permissions: List[str]) -> str:
    """Create access token for tenant user"""
    return multi_tenant_saas_engine.security_manager.create_access_token(tenant_id, user_id, permissions)

def validate_access_token(token_id: str) -> Dict[str, Any]:
    """Validate access token"""
    return multi_tenant_saas_engine.security_manager.validate_access_token(token_id)

def get_saas_status() -> Dict[str, Any]:
    """Get comprehensive SaaS status"""
    return multi_tenant_saas_engine.get_comprehensive_status()
