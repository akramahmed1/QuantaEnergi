"""
Multi-Tenancy Service for QuantaEnergi
Advanced tenant isolation, resource management, and billing
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import json
import uuid
import hashlib
import logging
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import aiohttp
from decimal import Decimal
import numpy as np
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TenantStatus(Enum):
    """Tenant status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
    TRIAL = "trial"

class TenantTier(Enum):
    """Tenant tiers"""
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"

class ResourceType(Enum):
    """Resource types"""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    API_CALLS = "api_calls"
    TRADES = "trades"
    USERS = "users"

@dataclass
class TenantConfig:
    """Tenant configuration"""
    tenant_id: str
    name: str
    tier: TenantTier
    status: TenantStatus
    max_users: int
    max_trades_per_day: int
    max_api_calls_per_hour: int
    cpu_limit: str  # e.g., "2000m"
    memory_limit: str  # e.g., "4Gi"
    storage_limit: str  # e.g., "100Gi"
    network_limit: str  # e.g., "1Gbps"
    features: List[str] = field(default_factory=list)
    custom_domains: List[str] = field(default_factory=list)
    ssl_enabled: bool = True
    backup_enabled: bool = True
    monitoring_enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class ResourceUsage:
    """Resource usage tracking"""
    tenant_id: str
    resource_type: ResourceType
    current_usage: float
    limit: float
    usage_percentage: float
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class BillingInfo:
    """Billing information"""
    tenant_id: str
    billing_cycle: str  # monthly, quarterly, yearly
    base_price: Decimal
    usage_based_pricing: Dict[str, Decimal]
    overage_rates: Dict[str, Decimal]
    discount_percentage: float = 0.0
    payment_method: str = "credit_card"
    billing_email: str = ""
    next_billing_date: datetime = field(default_factory=datetime.now)

class AdvancedMultiTenancyService:
    """
    Advanced multi-tenancy service with tenant isolation and resource management
    """
    
    def __init__(self):
        self.tenants = {}
        self.tenant_configs = {}
        self.resource_usage = {}
        self.billing_info = {}
        self.tenant_isolation = {}
        self.usage_analytics = {}
        self.performance_metrics = {}
        
    def create_tenant(self, 
                     name: str,
                     tier: TenantTier,
                     admin_email: str,
                     custom_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create new tenant"""
        try:
            # Generate unique tenant ID
            tenant_id = self._generate_tenant_id(name)
            
            # Create tenant configuration
            config = TenantConfig(
                tenant_id=tenant_id,
                name=name,
                tier=tier,
                status=TenantStatus.PENDING,
                max_users=self._get_tier_limits(tier)["max_users"],
                max_trades_per_day=self._get_tier_limits(tier)["max_trades"],
                max_api_calls_per_hour=self._get_tier_limits(tier)["max_api_calls"],
                cpu_limit=self._get_tier_limits(tier)["cpu_limit"],
                memory_limit=self._get_tier_limits(tier)["memory_limit"],
                storage_limit=self._get_tier_limits(tier)["storage_limit"],
                network_limit=self._get_tier_limits(tier)["network_limit"],
                features=self._get_tier_features(tier)
            )
            
            # Apply custom configuration if provided
            if custom_config:
                config = self._apply_custom_config(config, custom_config)
            
            # Store tenant configuration
            self.tenant_configs[tenant_id] = config
            
            # Initialize resource usage tracking
            self.resource_usage[tenant_id] = {}
            for resource_type in ResourceType:
                self.resource_usage[tenant_id][resource_type.value] = ResourceUsage(
                    tenant_id=tenant_id,
                    resource_type=resource_type,
                    current_usage=0.0,
                    limit=self._get_resource_limit(resource_type, config),
                    usage_percentage=0.0
                )
            
            # Initialize billing information
            self.billing_info[tenant_id] = BillingInfo(
                tenant_id=tenant_id,
                billing_cycle="monthly",
                base_price=self._get_tier_pricing(tier)["base_price"],
                usage_based_pricing=self._get_tier_pricing(tier)["usage_pricing"],
                overage_rates=self._get_tier_pricing(tier)["overage_rates"]
            )
            
            # Initialize tenant isolation
            self.tenant_isolation[tenant_id] = {
                "network_isolation": True,
                "data_isolation": True,
                "compute_isolation": True,
                "storage_isolation": True,
                "created_at": datetime.now().isoformat()
            }
            
            # Initialize usage analytics
            self.usage_analytics[tenant_id] = {
                "daily_usage": {},
                "weekly_usage": {},
                "monthly_usage": {},
                "peak_usage": {},
                "trends": {}
            }
            
            # Initialize performance metrics
            self.performance_metrics[tenant_id] = {
                "response_times": [],
                "error_rates": [],
                "throughput": [],
                "availability": 99.9
            }
            
            # Create tenant infrastructure
            infrastructure_result = self._create_tenant_infrastructure(tenant_id, config)
            
            if infrastructure_result["status"] == "success":
                config.status = TenantStatus.ACTIVE
                config.updated_at = datetime.now()
                
                return {
                    "status": "success",
                    "tenant_id": tenant_id,
                    "tenant_name": name,
                    "tier": tier.value,
                    "status": config.status.value,
                    "infrastructure": infrastructure_result,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                config.status = TenantStatus.INACTIVE
                return {
                    "status": "error",
                    "message": "Failed to create tenant infrastructure",
                    "details": infrastructure_result
                }
                
        except Exception as e:
            logger.error(f"Tenant creation error: {e}")
            return {"status": "error", "message": str(e)}
    
    def _generate_tenant_id(self, name: str) -> str:
        """Generate unique tenant ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name_hash = hashlib.md5(name.encode()).hexdigest()[:8]
        return f"tenant_{name_hash}_{timestamp}"
    
    def _get_tier_limits(self, tier: TenantTier) -> Dict[str, Any]:
        """Get tier-specific limits"""
        limits = {
            TenantTier.BASIC: {
                "max_users": 10,
                "max_trades": 1000,
                "max_api_calls": 10000,
                "cpu_limit": "500m",
                "memory_limit": "1Gi",
                "storage_limit": "10Gi",
                "network_limit": "100Mbps"
            },
            TenantTier.PROFESSIONAL: {
                "max_users": 50,
                "max_trades": 10000,
                "max_api_calls": 100000,
                "cpu_limit": "2000m",
                "memory_limit": "4Gi",
                "storage_limit": "100Gi",
                "network_limit": "1Gbps"
            },
            TenantTier.ENTERPRISE: {
                "max_users": 200,
                "max_trades": 100000,
                "max_api_calls": 1000000,
                "cpu_limit": "8000m",
                "memory_limit": "16Gi",
                "storage_limit": "1Ti",
                "network_limit": "10Gbps"
            },
            TenantTier.CUSTOM: {
                "max_users": 1000,
                "max_trades": 1000000,
                "max_api_calls": 10000000,
                "cpu_limit": "16000m",
                "memory_limit": "32Gi",
                "storage_limit": "10Ti",
                "network_limit": "100Gbps"
            }
        }
        
        return limits.get(tier, limits[TenantTier.BASIC])
    
    def _get_tier_features(self, tier: TenantTier) -> List[str]:
        """Get tier-specific features"""
        features = {
            TenantTier.BASIC: [
                "basic_trading",
                "standard_reports",
                "email_support"
            ],
            TenantTier.PROFESSIONAL: [
                "advanced_trading",
                "custom_reports",
                "priority_support",
                "api_access",
                "webhooks"
            ],
            TenantTier.ENTERPRISE: [
                "enterprise_trading",
                "custom_dashboards",
                "dedicated_support",
                "full_api_access",
                "advanced_webhooks",
                "custom_integrations",
                "sla_guarantee"
            ],
            TenantTier.CUSTOM: [
                "custom_trading",
                "custom_dashboards",
                "dedicated_support",
                "full_api_access",
                "advanced_webhooks",
                "custom_integrations",
                "sla_guarantee",
                "custom_features",
                "white_label"
            ]
        }
        
        return features.get(tier, features[TenantTier.BASIC])
    
    def _get_tier_pricing(self, tier: TenantTier) -> Dict[str, Any]:
        """Get tier-specific pricing"""
        pricing = {
            TenantTier.BASIC: {
                "base_price": Decimal("99.00"),
                "usage_pricing": {
                    "api_calls": Decimal("0.001"),
                    "trades": Decimal("0.01"),
                    "storage": Decimal("0.10")
                },
                "overage_rates": {
                    "api_calls": Decimal("0.002"),
                    "trades": Decimal("0.02"),
                    "storage": Decimal("0.20")
                }
            },
            TenantTier.PROFESSIONAL: {
                "base_price": Decimal("499.00"),
                "usage_pricing": {
                    "api_calls": Decimal("0.0005"),
                    "trades": Decimal("0.005"),
                    "storage": Decimal("0.05")
                },
                "overage_rates": {
                    "api_calls": Decimal("0.001"),
                    "trades": Decimal("0.01"),
                    "storage": Decimal("0.10")
                }
            },
            TenantTier.ENTERPRISE: {
                "base_price": Decimal("1999.00"),
                "usage_pricing": {
                    "api_calls": Decimal("0.0001"),
                    "trades": Decimal("0.001"),
                    "storage": Decimal("0.01")
                },
                "overage_rates": {
                    "api_calls": Decimal("0.0002"),
                    "trades": Decimal("0.002"),
                    "storage": Decimal("0.02")
                }
            },
            TenantTier.CUSTOM: {
                "base_price": Decimal("5000.00"),
                "usage_pricing": {
                    "api_calls": Decimal("0.00005"),
                    "trades": Decimal("0.0005"),
                    "storage": Decimal("0.005")
                },
                "overage_rates": {
                    "api_calls": Decimal("0.0001"),
                    "trades": Decimal("0.001"),
                    "storage": Decimal("0.01")
                }
            }
        }
        
        return pricing.get(tier, pricing[TenantTier.BASIC])
    
    def _apply_custom_config(self, config: TenantConfig, custom_config: Dict[str, Any]) -> TenantConfig:
        """Apply custom configuration to tenant"""
        try:
            if "max_users" in custom_config:
                config.max_users = custom_config["max_users"]
            
            if "max_trades_per_day" in custom_config:
                config.max_trades_per_day = custom_config["max_trades_per_day"]
            
            if "max_api_calls_per_hour" in custom_config:
                config.max_api_calls_per_hour = custom_config["max_api_calls_per_hour"]
            
            if "cpu_limit" in custom_config:
                config.cpu_limit = custom_config["cpu_limit"]
            
            if "memory_limit" in custom_config:
                config.memory_limit = custom_config["memory_limit"]
            
            if "storage_limit" in custom_config:
                config.storage_limit = custom_config["storage_limit"]
            
            if "network_limit" in custom_config:
                config.network_limit = custom_config["network_limit"]
            
            if "features" in custom_config:
                config.features.extend(custom_config["features"])
            
            if "custom_domains" in custom_config:
                config.custom_domains.extend(custom_config["custom_domains"])
            
            if "ssl_enabled" in custom_config:
                config.ssl_enabled = custom_config["ssl_enabled"]
            
            if "backup_enabled" in custom_config:
                config.backup_enabled = custom_config["backup_enabled"]
            
            if "monitoring_enabled" in custom_config:
                config.monitoring_enabled = custom_config["monitoring_enabled"]
            
            return config
            
        except Exception as e:
            logger.error(f"Custom config application error: {e}")
            return config
    
    def _get_resource_limit(self, resource_type: ResourceType, config: TenantConfig) -> float:
        """Get resource limit for tenant"""
        limits = {
            ResourceType.CPU: self._parse_cpu_limit(config.cpu_limit),
            ResourceType.MEMORY: self._parse_memory_limit(config.memory_limit),
            ResourceType.STORAGE: self._parse_storage_limit(config.storage_limit),
            ResourceType.NETWORK: self._parse_network_limit(config.network_limit),
            ResourceType.API_CALLS: config.max_api_calls_per_hour,
            ResourceType.TRADES: config.max_trades_per_day,
            ResourceType.USERS: config.max_users
        }
        
        return limits.get(resource_type, 0.0)
    
    def _parse_cpu_limit(self, cpu_limit: str) -> float:
        """Parse CPU limit string to float"""
        try:
            if cpu_limit.endswith('m'):
                return float(cpu_limit[:-1]) / 1000
            else:
                return float(cpu_limit)
        except:
            return 1.0
    
    def _parse_memory_limit(self, memory_limit: str) -> float:
        """Parse memory limit string to float (in GB)"""
        try:
            if memory_limit.endswith('Gi'):
                return float(memory_limit[:-2])
            elif memory_limit.endswith('Mi'):
                return float(memory_limit[:-2]) / 1024
            else:
                return float(memory_limit)
        except:
            return 1.0
    
    def _parse_storage_limit(self, storage_limit: str) -> float:
        """Parse storage limit string to float (in GB)"""
        try:
            if storage_limit.endswith('Ti'):
                return float(storage_limit[:-2]) * 1024
            elif storage_limit.endswith('Gi'):
                return float(storage_limit[:-2])
            elif storage_limit.endswith('Mi'):
                return float(storage_limit[:-2]) / 1024
            else:
                return float(storage_limit)
        except:
            return 10.0
    
    def _parse_network_limit(self, network_limit: str) -> float:
        """Parse network limit string to float (in Mbps)"""
        try:
            if network_limit.endswith('Gbps'):
                return float(network_limit[:-4]) * 1000
            elif network_limit.endswith('Mbps'):
                return float(network_limit[:-4])
            else:
                return float(network_limit)
        except:
            return 100.0
    
    def _create_tenant_infrastructure(self, tenant_id: str, config: TenantConfig) -> Dict[str, Any]:
        """Create tenant-specific infrastructure"""
        try:
            # This would integrate with Kubernetes, Docker, or cloud providers
            # For now, return a mock success response
            
            infrastructure = {
                "namespace": f"tenant-{tenant_id}",
                "services": [
                    f"{tenant_id}-backend-service",
                    f"{tenant_id}-frontend-service",
                    f"{tenant_id}-worker-service"
                ],
                "databases": [
                    f"{tenant_id}-postgresql",
                    f"{tenant_id}-redis"
                ],
                "storage": [
                    f"{tenant_id}-persistent-volume"
                ],
                "networking": [
                    f"{tenant_id}-ingress",
                    f"{tenant_id}-service-mesh"
                ]
            }
            
            return {
                "status": "success",
                "infrastructure": infrastructure,
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Infrastructure creation error: {e}")
            return {"status": "error", "message": str(e)}
    
    def update_tenant_config(self, 
                            tenant_id: str, 
                            updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update tenant configuration"""
        try:
            if tenant_id not in self.tenant_configs:
                return {"status": "error", "message": "Tenant not found"}
            
            config = self.tenant_configs[tenant_id]
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            
            config.updated_at = datetime.now()
            
            # Update infrastructure if needed
            infrastructure_result = self._update_tenant_infrastructure(tenant_id, config)
            
            return {
                "status": "success",
                "tenant_id": tenant_id,
                "updates": updates,
                "infrastructure": infrastructure_result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Tenant config update error: {e}")
            return {"status": "error", "message": str(e)}
    
    def _update_tenant_infrastructure(self, tenant_id: str, config: TenantConfig) -> Dict[str, Any]:
        """Update tenant infrastructure"""
        try:
            # This would integrate with infrastructure management
            return {
                "status": "success",
                "message": "Infrastructure updated successfully",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Infrastructure update error: {e}")
            return {"status": "error", "message": str(e)}
    
    def track_resource_usage(self, 
                           tenant_id: str,
                           resource_type: ResourceType,
                           usage: float) -> Dict[str, Any]:
        """Track resource usage for tenant"""
        try:
            if tenant_id not in self.resource_usage:
                return {"status": "error", "message": "Tenant not found"}
            
            if resource_type.value not in self.resource_usage[tenant_id]:
                return {"status": "error", "message": "Resource type not found"}
            
            # Update resource usage
            resource_usage = self.resource_usage[tenant_id][resource_type.value]
            resource_usage.current_usage = usage
            resource_usage.usage_percentage = (usage / resource_usage.limit) * 100
            resource_usage.timestamp = datetime.now()
            
            # Check for overage
            if resource_usage.usage_percentage > 100:
                self._handle_resource_overage(tenant_id, resource_type, resource_usage)
            
            # Update usage analytics
            self._update_usage_analytics(tenant_id, resource_type, usage)
            
            return {
                "status": "success",
                "tenant_id": tenant_id,
                "resource_type": resource_type.value,
                "current_usage": usage,
                "limit": resource_usage.limit,
                "usage_percentage": resource_usage.usage_percentage,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Resource usage tracking error: {e}")
            return {"status": "error", "message": str(e)}
    
    def _handle_resource_overage(self, 
                                tenant_id: str, 
                                resource_type: ResourceType, 
                                resource_usage: ResourceUsage):
        """Handle resource overage"""
        try:
            # Send alert
            self._send_overage_alert(tenant_id, resource_type, resource_usage)
            
            # Apply overage charges
            self._apply_overage_charges(tenant_id, resource_type, resource_usage)
            
            # Consider throttling or suspension
            if resource_usage.usage_percentage > 150:
                self._consider_tenant_suspension(tenant_id, resource_type)
                
        except Exception as e:
            logger.error(f"Resource overage handling error: {e}")
    
    def _send_overage_alert(self, 
                           tenant_id: str, 
                           resource_type: ResourceType, 
                           resource_usage: ResourceUsage):
        """Send overage alert"""
        try:
            # This would integrate with notification service
            alert_data = {
                "tenant_id": tenant_id,
                "resource_type": resource_type.value,
                "usage_percentage": resource_usage.usage_percentage,
                "current_usage": resource_usage.current_usage,
                "limit": resource_usage.limit,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.warning(f"Resource overage alert: {alert_data}")
            
        except Exception as e:
            logger.error(f"Overage alert error: {e}")
    
    def _apply_overage_charges(self, 
                              tenant_id: str, 
                              resource_type: ResourceType, 
                              resource_usage: ResourceUsage):
        """Apply overage charges"""
        try:
            if tenant_id not in self.billing_info:
                return
            
            billing_info = self.billing_info[tenant_id]
            overage_amount = resource_usage.current_usage - resource_usage.limit
            
            if overage_amount > 0 and resource_type.value in billing_info.overage_rates:
                overage_rate = billing_info.overage_rates[resource_type.value]
                overage_cost = overage_amount * overage_rate
                
                # This would integrate with billing system
                logger.info(f"Overage charge applied: {overage_cost} for {resource_type.value}")
                
        except Exception as e:
            logger.error(f"Overage charges error: {e}")
    
    def _consider_tenant_suspension(self, tenant_id: str, resource_type: ResourceType):
        """Consider tenant suspension for severe overage"""
        try:
            # This would implement suspension logic
            logger.warning(f"Considering suspension for tenant {tenant_id} due to {resource_type.value} overage")
            
        except Exception as e:
            logger.error(f"Tenant suspension consideration error: {e}")
    
    def _update_usage_analytics(self, 
                               tenant_id: str, 
                               resource_type: ResourceType, 
                               usage: float):
        """Update usage analytics"""
        try:
            if tenant_id not in self.usage_analytics:
                return
            
            analytics = self.usage_analytics[tenant_id]
            current_date = datetime.now().date()
            
            # Update daily usage
            if current_date not in analytics["daily_usage"]:
                analytics["daily_usage"][current_date] = {}
            
            if resource_type.value not in analytics["daily_usage"][current_date]:
                analytics["daily_usage"][current_date][resource_type.value] = []
            
            analytics["daily_usage"][current_date][resource_type.value].append({
                "usage": usage,
                "timestamp": datetime.now().isoformat()
            })
            
            # Update peak usage
            if resource_type.value not in analytics["peak_usage"]:
                analytics["peak_usage"][resource_type.value] = usage
            else:
                analytics["peak_usage"][resource_type.value] = max(
                    analytics["peak_usage"][resource_type.value], usage
                )
            
        except Exception as e:
            logger.error(f"Usage analytics update error: {e}")
    
    def get_tenant_analytics(self, tenant_id: str) -> Dict[str, Any]:
        """Get comprehensive tenant analytics"""
        try:
            if tenant_id not in self.tenant_configs:
                return {"status": "error", "message": "Tenant not found"}
            
            config = self.tenant_configs[tenant_id]
            usage = self.resource_usage.get(tenant_id, {})
            analytics = self.usage_analytics.get(tenant_id, {})
            performance = self.performance_metrics.get(tenant_id, {})
            
            return {
                "status": "success",
                "tenant_id": tenant_id,
                "config": {
                    "name": config.name,
                    "tier": config.tier.value,
                    "status": config.status.value,
                    "max_users": config.max_users,
                    "max_trades_per_day": config.max_trades_per_day,
                    "max_api_calls_per_hour": config.max_api_calls_per_hour,
                    "features": config.features,
                    "created_at": config.created_at.isoformat(),
                    "updated_at": config.updated_at.isoformat()
                },
                "resource_usage": {
                    resource_type: {
                        "current_usage": usage_data.current_usage,
                        "limit": usage_data.limit,
                        "usage_percentage": usage_data.usage_percentage,
                        "timestamp": usage_data.timestamp.isoformat()
                    }
                    for resource_type, usage_data in usage.items()
                },
                "analytics": analytics,
                "performance": performance,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Tenant analytics retrieval error: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_multi_tenancy_statistics(self) -> Dict[str, Any]:
        """Get multi-tenancy service statistics"""
        try:
            total_tenants = len(self.tenant_configs)
            active_tenants = sum(1 for config in self.tenant_configs.values() if config.status == TenantStatus.ACTIVE)
            
            # Count by tier
            tier_counts = {}
            for config in self.tenant_configs.values():
                tier = config.tier.value
                tier_counts[tier] = tier_counts.get(tier, 0) + 1
            
            # Count by status
            status_counts = {}
            for config in self.tenant_configs.values():
                status = config.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Calculate average resource usage
            avg_resource_usage = {}
            for resource_type in ResourceType:
                total_usage = 0
                count = 0
                for tenant_usage in self.resource_usage.values():
                    if resource_type.value in tenant_usage:
                        total_usage += tenant_usage[resource_type.value].usage_percentage
                        count += 1
                
                if count > 0:
                    avg_resource_usage[resource_type.value] = round(total_usage / count, 2)
                else:
                    avg_resource_usage[resource_type.value] = 0.0
            
            return {
                "status": "success",
                "statistics": {
                    "total_tenants": total_tenants,
                    "active_tenants": active_tenants,
                    "tier_breakdown": tier_counts,
                    "status_breakdown": status_counts,
                    "average_resource_usage": avg_resource_usage,
                    "total_billing_info": len(self.billing_info),
                    "total_usage_analytics": len(self.usage_analytics)
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Statistics retrieval error: {e}")
            return {"status": "error", "message": str(e)}
