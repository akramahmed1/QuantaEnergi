"""
Advanced Integration Service for QuantaEnergi
ERP and external system integration with real-time data synchronization
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import json
import asyncio
import aiohttp
import logging
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import hashlib
import hmac
import base64
import ssl
import websockets

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegrationType(Enum):
    """Integration types"""
    ERP = "erp"
    CRM = "crm"
    MARKET_DATA = "market_data"
    TRADING_PLATFORM = "trading_platform"
    RISK_MANAGEMENT = "risk_management"
    COMPLIANCE = "compliance"
    ACCOUNTING = "accounting"
    REPORTING = "reporting"

class IntegrationStatus(Enum):
    """Integration status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    CONFIGURING = "configuring"
    TESTING = "testing"

@dataclass
class IntegrationConfig:
    """Integration configuration"""
    name: str
    integration_type: IntegrationType
    endpoint: str
    api_key: str
    credentials: Dict[str, Any]
    sync_frequency: int  # seconds
    enabled: bool
    last_sync: Optional[datetime] = None
    status: IntegrationStatus = IntegrationStatus.INACTIVE

class AdvancedIntegrationService:
    """
    Advanced integration service for ERP and external systems
    """
    
    def __init__(self):
        self.integrations = {}
        self.sync_jobs = {}
        self.data_mappings = {}
        self.webhook_endpoints = {}
        self.connection_pools = {}
        self.sync_history = []
        self.error_logs = []
        
    def register_integration(self, config: IntegrationConfig) -> Dict[str, Any]:
        """Register new integration"""
        try:
            integration_id = self._generate_integration_id(config.name)
            
            self.integrations[integration_id] = {
                "id": integration_id,
                "config": config,
                "created_at": datetime.now().isoformat(),
                "last_sync": None,
                "sync_count": 0,
                "error_count": 0,
                "data_schema": {},
                "webhook_subscriptions": []
            }
            
            # Test connection
            test_result = self._test_integration_connection(integration_id)
            
            if test_result["status"] == "success":
                self.integrations[integration_id]["config"].status = IntegrationStatus.ACTIVE
                self.integrations[integration_id]["config"].enabled = True
                
                # Start sync job if enabled
                if config.enabled:
                    self._start_sync_job(integration_id)
            
            return {
                "status": "success",
                "integration_id": integration_id,
                "test_result": test_result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Integration registration error: {e}")
            return {"status": "error", "message": str(e)}
    
    def _generate_integration_id(self, name: str) -> str:
        """Generate unique integration ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"int_{name.lower()}_{timestamp}"
    
    def _test_integration_connection(self, integration_id: str) -> Dict[str, Any]:
        """Test integration connection"""
        try:
            integration = self.integrations[integration_id]
            config = integration["config"]
            
            if config.integration_type == IntegrationType.ERP:
                return self._test_erp_connection(config)
            elif config.integration_type == IntegrationType.MARKET_DATA:
                return self._test_market_data_connection(config)
            elif config.integration_type == IntegrationType.TRADING_PLATFORM:
                return self._test_trading_platform_connection(config)
            else:
                return self._test_generic_connection(config)
                
        except Exception as e:
            logger.error(f"Connection test error: {e}")
            return {"status": "error", "message": str(e)}
    
    def _test_erp_connection(self, config: IntegrationConfig) -> Dict[str, Any]:
        """Test ERP system connection"""
        try:
            # Test ERP API connection
            headers = {
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json"
            }
            
            # Make test API call
            test_url = f"{config.endpoint}/api/test"
            
            async def test_call():
                async with aiohttp.ClientSession() as session:
                    async with session.get(test_url, headers=headers, timeout=10) as response:
                        if response.status == 200:
                            data = await response.json()
                            return {"status": "success", "response": data}
                        else:
                            return {"status": "error", "message": f"HTTP {response.status}"}
            
            # Run async test
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(test_call())
            loop.close()
            
            return result
            
        except Exception as e:
            logger.error(f"ERP connection test error: {e}")
            return {"status": "error", "message": str(e)}
    
    def _test_market_data_connection(self, config: IntegrationConfig) -> Dict[str, Any]:
        """Test market data connection"""
        try:
            # Test market data API
            headers = {
                "X-API-Key": config.api_key,
                "Content-Type": "application/json"
            }
            
            test_url = f"{config.endpoint}/v1/market/test"
            
            async def test_call():
                async with aiohttp.ClientSession() as session:
                    async with session.get(test_url, headers=headers, timeout=10) as response:
                        if response.status == 200:
                            data = await response.json()
                            return {"status": "success", "response": data}
                        else:
                            return {"status": "error", "message": f"HTTP {response.status}"}
            
            # Run async test
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(test_call())
            loop.close()
            
            return result
            
        except Exception as e:
            logger.error(f"Market data connection test error: {e}")
            return {"status": "error", "message": str(e)}
    
    def _test_trading_platform_connection(self, config: IntegrationConfig) -> Dict[str, Any]:
        """Test trading platform connection"""
        try:
            # Test trading platform API
            headers = {
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json"
            }
            
            test_url = f"{config.endpoint}/api/v1/account/status"
            
            async def test_call():
                async with aiohttp.ClientSession() as session:
                    async with session.get(test_url, headers=headers, timeout=10) as response:
                        if response.status == 200:
                            data = await response.json()
                            return {"status": "success", "response": data}
                        else:
                            return {"status": "error", "message": f"HTTP {response.status}"}
            
            # Run async test
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(test_call())
            loop.close()
            
            return result
            
        except Exception as e:
            logger.error(f"Trading platform connection test error: {e}")
            return {"status": "error", "message": str(e)}
    
    def _test_generic_connection(self, config: IntegrationConfig) -> Dict[str, Any]:
        """Test generic connection"""
        try:
            # Generic connection test
            headers = {
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json"
            }
            
            test_url = f"{config.endpoint}/health"
            
            async def test_call():
                async with aiohttp.ClientSession() as session:
                    async with session.get(test_url, headers=headers, timeout=10) as response:
                        if response.status == 200:
                            return {"status": "success", "message": "Connection successful"}
                        else:
                            return {"status": "error", "message": f"HTTP {response.status}"}
            
            # Run async test
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(test_call())
            loop.close()
            
            return result
            
        except Exception as e:
            logger.error(f"Generic connection test error: {e}")
            return {"status": "error", "message": str(e)}
    
    def _start_sync_job(self, integration_id: str):
        """Start synchronization job for integration"""
        try:
            integration = self.integrations[integration_id]
            config = integration["config"]
            
            # Create sync job
            sync_job = {
                "integration_id": integration_id,
                "sync_frequency": config.sync_frequency,
                "last_sync": None,
                "next_sync": datetime.now() + timedelta(seconds=config.sync_frequency),
                "active": True,
                "sync_count": 0,
                "error_count": 0
            }
            
            self.sync_jobs[integration_id] = sync_job
            
            # Start background sync task
            asyncio.create_task(self._sync_integration_data(integration_id))
            
            logger.info(f"Sync job started for integration {integration_id}")
            
        except Exception as e:
            logger.error(f"Sync job start error: {e}")
    
    async def _sync_integration_data(self, integration_id: str):
        """Background task for data synchronization"""
        try:
            while integration_id in self.sync_jobs and self.sync_jobs[integration_id]["active"]:
                sync_job = self.sync_jobs[integration_id]
                
                if datetime.now() >= sync_job["next_sync"]:
                    # Perform sync
                    sync_result = await self._perform_data_sync(integration_id)
                    
                    # Update sync job
                    sync_job["last_sync"] = datetime.now().isoformat()
                    sync_job["next_sync"] = datetime.now() + timedelta(seconds=sync_job["sync_frequency"])
                    sync_job["sync_count"] += 1
                    
                    if sync_result["status"] == "error":
                        sync_job["error_count"] += 1
                    
                    # Log sync result
                    self.sync_history.append({
                        "integration_id": integration_id,
                        "sync_result": sync_result,
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Wait before next check
                await asyncio.sleep(60)  # Check every minute
                
        except Exception as e:
            logger.error(f"Sync task error: {e}")
        finally:
            if integration_id in self.sync_jobs:
                del self.sync_jobs[integration_id]
    
    async def _perform_data_sync(self, integration_id: str) -> Dict[str, Any]:
        """Perform data synchronization"""
        try:
            integration = self.integrations[integration_id]
            config = integration["config"]
            
            if config.integration_type == IntegrationType.ERP:
                return await self._sync_erp_data(integration_id)
            elif config.integration_type == IntegrationType.MARKET_DATA:
                return await self._sync_market_data(integration_id)
            elif config.integration_type == IntegrationType.TRADING_PLATFORM:
                return await self._sync_trading_data(integration_id)
            else:
                return await self._sync_generic_data(integration_id)
                
        except Exception as e:
            logger.error(f"Data sync error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _sync_erp_data(self, integration_id: str) -> Dict[str, Any]:
        """Sync ERP data"""
        try:
            integration = self.integrations[integration_id]
            config = integration["config"]
            
            headers = {
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json"
            }
            
            # Sync different data types
            sync_results = {}
            
            # Sync financial data
            financial_data = await self._fetch_erp_financial_data(config, headers)
            if financial_data["status"] == "success":
                sync_results["financial"] = financial_data
            
            # Sync inventory data
            inventory_data = await self._fetch_erp_inventory_data(config, headers)
            if inventory_data["status"] == "success":
                sync_results["inventory"] = inventory_data
            
            # Sync customer data
            customer_data = await self._fetch_erp_customer_data(config, headers)
            if customer_data["status"] == "success":
                sync_results["customer"] = customer_data
            
            return {
                "status": "success",
                "integration_id": integration_id,
                "sync_results": sync_results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"ERP sync error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _fetch_erp_financial_data(self, config: IntegrationConfig, headers: Dict[str, str]) -> Dict[str, Any]:
        """Fetch ERP financial data"""
        try:
            url = f"{config.endpoint}/api/financial/transactions"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "status": "success",
                            "data": data,
                            "record_count": len(data.get("transactions", []))
                        }
                    else:
                        return {"status": "error", "message": f"HTTP {response.status}"}
                        
        except Exception as e:
            logger.error(f"ERP financial data fetch error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _fetch_erp_inventory_data(self, config: IntegrationConfig, headers: Dict[str, str]) -> Dict[str, Any]:
        """Fetch ERP inventory data"""
        try:
            url = f"{config.endpoint}/api/inventory/products"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "status": "success",
                            "data": data,
                            "record_count": len(data.get("products", []))
                        }
                    else:
                        return {"status": "error", "message": f"HTTP {response.status}"}
                        
        except Exception as e:
            logger.error(f"ERP inventory data fetch error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _fetch_erp_customer_data(self, config: IntegrationConfig, headers: Dict[str, str]) -> Dict[str, Any]:
        """Fetch ERP customer data"""
        try:
            url = f"{config.endpoint}/api/customers"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "status": "success",
                            "data": data,
                            "record_count": len(data.get("customers", []))
                        }
                    else:
                        return {"status": "error", "message": f"HTTP {response.status}"}
                        
        except Exception as e:
            logger.error(f"ERP customer data fetch error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _sync_market_data(self, integration_id: str) -> Dict[str, Any]:
        """Sync market data"""
        try:
            integration = self.integrations[integration_id]
            config = integration["config"]
            
            headers = {
                "X-API-Key": config.api_key,
                "Content-Type": "application/json"
            }
            
            # Sync market prices
            url = f"{config.endpoint}/v1/market/prices"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "status": "success",
                            "integration_id": integration_id,
                            "data": data,
                            "record_count": len(data.get("prices", []))
                        }
                    else:
                        return {"status": "error", "message": f"HTTP {response.status}"}
                        
        except Exception as e:
            logger.error(f"Market data sync error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _sync_trading_data(self, integration_id: str) -> Dict[str, Any]:
        """Sync trading platform data"""
        try:
            integration = self.integrations[integration_id]
            config = integration["config"]
            
            headers = {
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json"
            }
            
            # Sync trading positions
            url = f"{config.endpoint}/api/v1/positions"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "status": "success",
                            "integration_id": integration_id,
                            "data": data,
                            "record_count": len(data.get("positions", []))
                        }
                    else:
                        return {"status": "error", "message": f"HTTP {response.status}"}
                        
        except Exception as e:
            logger.error(f"Trading data sync error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _sync_generic_data(self, integration_id: str) -> Dict[str, Any]:
        """Sync generic data"""
        try:
            integration = self.integrations[integration_id]
            config = integration["config"]
            
            headers = {
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json"
            }
            
            # Generic data sync
            url = f"{config.endpoint}/api/data"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "status": "success",
                            "integration_id": integration_id,
                            "data": data
                        }
                    else:
                        return {"status": "error", "message": f"HTTP {response.status}"}
                        
        except Exception as e:
            logger.error(f"Generic data sync error: {e}")
            return {"status": "error", "message": str(e)}
    
    def create_webhook_endpoint(self, 
                               integration_id: str,
                               webhook_url: str,
                               events: List[str]) -> Dict[str, Any]:
        """Create webhook endpoint for integration"""
        try:
            if integration_id not in self.integrations:
                return {"status": "error", "message": "Integration not found"}
            
            webhook_id = f"webhook_{integration_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            webhook_config = {
                "webhook_id": webhook_id,
                "integration_id": integration_id,
                "webhook_url": webhook_url,
                "events": events,
                "active": True,
                "created_at": datetime.now().isoformat(),
                "last_triggered": None,
                "trigger_count": 0
            }
            
            self.webhook_endpoints[webhook_id] = webhook_config
            
            # Add to integration
            self.integrations[integration_id]["webhook_subscriptions"].append(webhook_id)
            
            return {
                "status": "success",
                "webhook_id": webhook_id,
                "webhook_config": webhook_config,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Webhook creation error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def trigger_webhook(self, webhook_id: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger webhook with event data"""
        try:
            if webhook_id not in self.webhook_endpoints:
                return {"status": "error", "message": "Webhook not found"}
            
            webhook = self.webhook_endpoints[webhook_id]
            
            if not webhook["active"]:
                return {"status": "error", "message": "Webhook is inactive"}
            
            # Prepare webhook payload
            payload = {
                "event_type": event_data.get("event_type"),
                "integration_id": webhook["integration_id"],
                "data": event_data.get("data"),
                "timestamp": datetime.now().isoformat()
            }
            
            # Send webhook
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook["webhook_url"],
                    json=payload,
                    timeout=10
                ) as response:
                    if response.status == 200:
                        # Update webhook stats
                        webhook["last_triggered"] = datetime.now().isoformat()
                        webhook["trigger_count"] += 1
                        
                        return {
                            "status": "success",
                            "webhook_id": webhook_id,
                            "response_status": response.status
                        }
                    else:
                        return {"status": "error", "message": f"HTTP {response.status}"}
                        
        except Exception as e:
            logger.error(f"Webhook trigger error: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_integration_status(self, integration_id: str = None) -> Dict[str, Any]:
        """Get integration status"""
        try:
            if integration_id:
                if integration_id not in self.integrations:
                    return {"status": "error", "message": "Integration not found"}
                
                integration = self.integrations[integration_id]
                sync_job = self.sync_jobs.get(integration_id)
                
                return {
                    "status": "success",
                    "integration": {
                        "id": integration_id,
                        "name": integration["config"].name,
                        "type": integration["config"].integration_type.value,
                        "status": integration["config"].status.value,
                        "enabled": integration["config"].enabled,
                        "last_sync": integration["last_sync"],
                        "sync_count": integration["sync_count"],
                        "error_count": integration["error_count"],
                        "sync_job": sync_job
                    },
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # Return all integrations
                integrations_list = []
                for int_id, integration in self.integrations.items():
                    sync_job = self.sync_jobs.get(int_id)
                    integrations_list.append({
                        "id": int_id,
                        "name": integration["config"].name,
                        "type": integration["config"].integration_type.value,
                        "status": integration["config"].status.value,
                        "enabled": integration["config"].enabled,
                        "last_sync": integration["last_sync"],
                        "sync_count": integration["sync_count"],
                        "error_count": integration["error_count"],
                        "sync_job": sync_job
                    })
                
                return {
                    "status": "success",
                    "integrations": integrations_list,
                    "total_count": len(integrations_list),
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Integration status retrieval error: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_sync_history(self, integration_id: str = None, limit: int = 100) -> Dict[str, Any]:
        """Get synchronization history"""
        try:
            filtered_history = self.sync_history
            
            if integration_id:
                filtered_history = [h for h in filtered_history if h["integration_id"] == integration_id]
            
            # Limit results
            filtered_history = filtered_history[-limit:] if limit else filtered_history
            
            return {
                "status": "success",
                "sync_history": filtered_history,
                "total_count": len(filtered_history),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Sync history retrieval error: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_integration_statistics(self) -> Dict[str, Any]:
        """Get integration service statistics"""
        try:
            total_integrations = len(self.integrations)
            active_integrations = sum(1 for i in self.integrations.values() if i["config"].enabled)
            total_sync_jobs = len(self.sync_jobs)
            total_webhooks = len(self.webhook_endpoints)
            
            # Count by type
            type_counts = {}
            for integration in self.integrations.values():
                int_type = integration["config"].integration_type.value
                type_counts[int_type] = type_counts.get(int_type, 0) + 1
            
            # Calculate success rate
            total_syncs = sum(i["sync_count"] for i in self.integrations.values())
            total_errors = sum(i["error_count"] for i in self.integrations.values())
            success_rate = ((total_syncs - total_errors) / total_syncs * 100) if total_syncs > 0 else 0
            
            return {
                "status": "success",
                "statistics": {
                    "total_integrations": total_integrations,
                    "active_integrations": active_integrations,
                    "total_sync_jobs": total_sync_jobs,
                    "total_webhooks": total_webhooks,
                    "type_breakdown": type_counts,
                    "success_rate": round(success_rate, 2),
                    "total_syncs": total_syncs,
                    "total_errors": total_errors
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Statistics retrieval error: {e}")
            return {"status": "error", "message": str(e)}
