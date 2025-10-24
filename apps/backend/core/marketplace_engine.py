"""
Marketplace Engine for QuantaEnergi ETRM/CTRM Platform
Implements marketplace of add-ons and partner ecosystem including:
- Plugin marketplace
- Pre-built connectors
- Partner integrations
- Add-on management
- Revenue sharing
- API marketplace
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
import requests
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import zipfile
import tempfile
import os
import shutil

logger = logging.getLogger(__name__)

class AddonType(Enum):
    """Add-on type enumeration"""
    CONNECTOR = "connector"
    INTEGRATION = "integration"
    WORKFLOW = "workflow"
    DASHBOARD = "dashboard"
    REPORT = "report"
    ANALYTICS = "analytics"
    API = "api"
    THEME = "theme"
    LANGUAGE = "language"
    CUSTOM = "custom"

class AddonStatus(Enum):
    """Add-on status enumeration"""
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"
    DEPRECATED = "deprecated"

class PartnerType(Enum):
    """Partner type enumeration"""
    TECHNOLOGY = "technology"
    CONSULTING = "consulting"
    INTEGRATION = "integration"
    DATA_PROVIDER = "data_provider"
    SERVICE_PROVIDER = "service_provider"
    RESELLER = "reseller"

class RevenueModel(Enum):
    """Revenue model enumeration"""
    FREE = "free"
    ONE_TIME = "one_time"
    SUBSCRIPTION = "subscription"
    USAGE_BASED = "usage_based"
    REVENUE_SHARE = "revenue_share"
    COMMISSION = "commission"

@dataclass
class MarketplaceAddon:
    """Marketplace add-on definition"""
    addon_id: str
    name: str
    description: str = ""
    addon_type: AddonType = AddonType.CUSTOM
    version: str = "1.0.0"
    status: AddonStatus = AddonStatus.DRAFT
    author: str = ""
    author_email: str = ""
    company: str = ""
    category: str = ""
    tags: List[str] = field(default_factory=list)
    price: float = 0.0
    revenue_model: RevenueModel = RevenueModel.FREE
    download_count: int = 0
    rating: float = 0.0
    review_count: int = 0
    file_size: int = 0
    file_path: str = ""
    dependencies: List[str] = field(default_factory=list)
    compatibility: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MarketplacePartner:
    """Marketplace partner definition"""
    partner_id: str
    name: str
    partner_type: PartnerType
    description: str = ""
    website: str = ""
    contact_email: str = ""
    contact_phone: str = ""
    address: Dict[str, str] = field(default_factory=dict)
    services: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    is_verified: bool = False
    is_active: bool = True
    partnership_level: str = "bronze"  # bronze, silver, gold, platinum
    revenue_share_rate: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AddonReview:
    """Add-on review definition"""
    review_id: str
    addon_id: str
    user_id: str
    rating: int  # 1-5
    title: str = ""
    comment: str = ""
    is_verified_purchase: bool = False
    helpful_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AddonInstallation:
    """Add-on installation definition"""
    installation_id: str
    addon_id: str
    tenant_id: str
    user_id: str
    version: str
    installation_date: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    configuration: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class APIMarketplace:
    """API marketplace definition"""
    api_id: str
    name: str
    description: str = ""
    endpoint: str = ""
    version: str = "1.0.0"
    authentication: str = "api_key"  # api_key, oauth, basic, none
    rate_limit: int = 1000  # requests per hour
    pricing_tier: str = "free"  # free, basic, premium, enterprise
    documentation_url: str = ""
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

class AddonManager:
    """Add-on management system"""
    
    def __init__(self):
        self.addons: Dict[str, MarketplaceAddon] = {}
        self.installations: Dict[str, List[AddonInstallation]] = {}
        self.reviews: Dict[str, List[AddonReview]] = {}
        self.addon_validator = AddonValidator()
        self.addon_installer = AddonInstaller()
        
    def create_addon(self, name: str, description: str, addon_type: AddonType,
                    author: str, author_email: str, company: str = "",
                    category: str = "", tags: List[str] = None) -> str:
        """Create marketplace add-on"""
        try:
            addon_id = f"ADDON_{uuid.uuid4().hex[:8].upper()}"
            
            addon = MarketplaceAddon(
                addon_id=addon_id,
                name=name,
                description=description,
                addon_type=addon_type,
                author=author,
                author_email=author_email,
                company=company,
                category=category,
                tags=tags or []
            )
            
            self.addons[addon_id] = addon
            logger.info(f"Created add-on: {name}")
            return addon_id
            
        except Exception as e:
            logger.error(f"Error creating add-on: {e}")
            return ""
    
    def upload_addon_file(self, addon_id: str, file_path: str) -> bool:
        """Upload add-on file"""
        try:
            if addon_id not in self.addons:
                return False
            
            addon = self.addons[addon_id]
            
            # Validate add-on file
            validation_result = self.addon_validator.validate_addon_file(file_path)
            if not validation_result["valid"]:
                logger.error(f"Add-on validation failed: {validation_result['error']}")
                return False
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Update add-on
            addon.file_path = file_path
            addon.file_size = file_size
            addon.updated_at = datetime.utcnow()
            
            logger.info(f"Uploaded add-on file: {addon_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading add-on file: {e}")
            return False
    
    def submit_for_review(self, addon_id: str) -> bool:
        """Submit add-on for review"""
        try:
            if addon_id not in self.addons:
                return False
            
            addon = self.addons[addon_id]
            
            # Validate add-on before submission
            validation_result = self.addon_validator.validate_addon(addon)
            if not validation_result["valid"]:
                logger.error(f"Add-on validation failed: {validation_result['error']}")
                return False
            
            # Update status
            addon.status = AddonStatus.PENDING
            addon.updated_at = datetime.utcnow()
            
            logger.info(f"Submitted add-on for review: {addon_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error submitting add-on for review: {e}")
            return False
    
    def approve_addon(self, addon_id: str) -> bool:
        """Approve add-on"""
        try:
            if addon_id not in self.addons:
                return False
            
            addon = self.addons[addon_id]
            addon.status = AddonStatus.APPROVED
            addon.published_at = datetime.utcnow()
            addon.updated_at = datetime.utcnow()
            
            logger.info(f"Approved add-on: {addon_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error approving add-on: {e}")
            return False
    
    def install_addon(self, addon_id: str, tenant_id: str, user_id: str) -> str:
        """Install add-on for tenant"""
        try:
            if addon_id not in self.addons:
                return ""
            
            addon = self.addons[addon_id]
            
            if addon.status != AddonStatus.APPROVED:
                logger.error(f"Add-on not approved: {addon_id}")
                return ""
            
            # Create installation record
            installation_id = f"INSTALL_{uuid.uuid4().hex[:8].upper()}"
            
            installation = AddonInstallation(
                installation_id=installation_id,
                addon_id=addon_id,
                tenant_id=tenant_id,
                user_id=user_id,
                version=addon.version
            )
            
            if tenant_id not in self.installations:
                self.installations[tenant_id] = []
            
            self.installations[tenant_id].append(installation)
            
            # Install add-on
            install_result = self.addon_installer.install_addon(addon, tenant_id)
            if not install_result["success"]:
                logger.error(f"Add-on installation failed: {install_result['error']}")
                return ""
            
            # Update download count
            addon.download_count += 1
            
            logger.info(f"Installed add-on: {addon_id} for tenant: {tenant_id}")
            return installation_id
            
        except Exception as e:
            logger.error(f"Error installing add-on: {e}")
            return ""
    
    def add_review(self, addon_id: str, user_id: str, rating: int,
                  title: str = "", comment: str = "") -> str:
        """Add review for add-on"""
        try:
            if addon_id not in self.addons:
                return ""
            
            review_id = f"REVIEW_{uuid.uuid4().hex[:8].upper()}"
            
            review = AddonReview(
                review_id=review_id,
                addon_id=addon_id,
                user_id=user_id,
                rating=rating,
                title=title,
                comment=comment
            )
            
            if addon_id not in self.reviews:
                self.reviews[addon_id] = []
            
            self.reviews[addon_id].append(review)
            
            # Update add-on rating
            self._update_addon_rating(addon_id)
            
            logger.info(f"Added review: {review_id}")
            return review_id
            
        except Exception as e:
            logger.error(f"Error adding review: {e}")
            return ""
    
    def _update_addon_rating(self, addon_id: str):
        """Update add-on rating"""
        try:
            if addon_id not in self.reviews:
                return
            
            reviews = self.reviews[addon_id]
            if not reviews:
                return
            
            # Calculate average rating
            total_rating = sum(review.rating for review in reviews)
            average_rating = total_rating / len(reviews)
            
            # Update add-on
            addon = self.addons[addon_id]
            addon.rating = round(average_rating, 2)
            addon.review_count = len(reviews)
            
        except Exception as e:
            logger.error(f"Error updating add-on rating: {e}")
    
    def get_addon_details(self, addon_id: str) -> Dict[str, Any]:
        """Get add-on details"""
        try:
            if addon_id not in self.addons:
                return {"error": "Add-on not found"}
            
            addon = self.addons[addon_id]
            reviews = self.reviews.get(addon_id, [])
            
            return {
                "addon_id": addon_id,
                "name": addon.name,
                "description": addon.description,
                "addon_type": addon.addon_type.value,
                "version": addon.version,
                "status": addon.status.value,
                "author": addon.author,
                "company": addon.company,
                "category": addon.category,
                "tags": addon.tags,
                "price": addon.price,
                "revenue_model": addon.revenue_model.value,
                "download_count": addon.download_count,
                "rating": addon.rating,
                "review_count": addon.review_count,
                "file_size": addon.file_size,
                "dependencies": addon.dependencies,
                "compatibility": addon.compatibility,
                "created_at": addon.created_at.isoformat(),
                "updated_at": addon.updated_at.isoformat(),
                "published_at": addon.published_at.isoformat() if addon.published_at else None,
                "reviews": [
                    {
                        "review_id": review.review_id,
                        "user_id": review.user_id,
                        "rating": review.rating,
                        "title": review.title,
                        "comment": review.comment,
                        "created_at": review.created_at.isoformat()
                    } for review in reviews
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting add-on details: {e}")
            return {"error": str(e)}

class AddonValidator:
    """Add-on validation engine"""
    
    def validate_addon(self, addon: MarketplaceAddon) -> Dict[str, Any]:
        """Validate add-on"""
        try:
            errors = []
            
            # Check required fields
            if not addon.name:
                errors.append("Name is required")
            
            if not addon.description:
                errors.append("Description is required")
            
            if not addon.author:
                errors.append("Author is required")
            
            if not addon.author_email:
                errors.append("Author email is required")
            
            if not addon.file_path:
                errors.append("File path is required")
            
            # Check file size
            if addon.file_size > 100 * 1024 * 1024:  # 100MB limit
                errors.append("File size exceeds 100MB limit")
            
            # Check version format
            if not self._is_valid_version(addon.version):
                errors.append("Invalid version format")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"Error validating add-on: {e}")
            return {"valid": False, "errors": [str(e)]}
    
    def validate_addon_file(self, file_path: str) -> Dict[str, Any]:
        """Validate add-on file"""
        try:
            errors = []
            
            # Check if file exists
            if not os.path.exists(file_path):
                errors.append("File does not exist")
                return {"valid": False, "errors": errors}
            
            # Check file extension
            if not file_path.endswith('.zip'):
                errors.append("File must be a ZIP archive")
            
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > 100 * 1024 * 1024:  # 100MB limit
                errors.append("File size exceeds 100MB limit")
            
            # Validate ZIP contents
            try:
                with zipfile.ZipFile(file_path, 'r') as zip_file:
                    # Check for required files
                    required_files = ['manifest.json', 'install.py']
                    for required_file in required_files:
                        if required_file not in zip_file.namelist():
                            errors.append(f"Required file missing: {required_file}")
                    
                    # Check for malicious files
                    for file_name in zip_file.namelist():
                        if file_name.startswith('../') or '..' in file_name:
                            errors.append(f"Potentially malicious file: {file_name}")
                            
            except zipfile.BadZipFile:
                errors.append("Invalid ZIP file")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"Error validating add-on file: {e}")
            return {"valid": False, "errors": [str(e)]}
    
    def _is_valid_version(self, version: str) -> bool:
        """Check if version format is valid"""
        try:
            # Simple version format check (semantic versioning)
            parts = version.split('.')
            if len(parts) != 3:
                return False
            
            for part in parts:
                if not part.isdigit():
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating version: {e}")
            return False

class AddonInstaller:
    """Add-on installation engine"""
    
    def install_addon(self, addon: MarketplaceAddon, tenant_id: str) -> Dict[str, Any]:
        """Install add-on for tenant"""
        try:
            # Extract add-on files
            extract_path = self._extract_addon_files(addon.file_path)
            if not extract_path:
                return {"success": False, "error": "Failed to extract add-on files"}
            
            # Read manifest
            manifest = self._read_manifest(extract_path)
            if not manifest:
                return {"success": False, "error": "Failed to read manifest"}
            
            # Install add-on components
            install_result = self._install_addon_components(addon, tenant_id, extract_path, manifest)
            
            # Clean up
            shutil.rmtree(extract_path)
            
            return install_result
            
        except Exception as e:
            logger.error(f"Error installing add-on: {e}")
            return {"success": False, "error": str(e)}
    
    def _extract_addon_files(self, file_path: str) -> Optional[str]:
        """Extract add-on files"""
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            
            # Extract ZIP file
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                zip_file.extractall(temp_dir)
            
            return temp_dir
            
        except Exception as e:
            logger.error(f"Error extracting add-on files: {e}")
            return None
    
    def _read_manifest(self, extract_path: str) -> Optional[Dict[str, Any]]:
        """Read add-on manifest"""
        try:
            manifest_path = os.path.join(extract_path, 'manifest.json')
            
            if not os.path.exists(manifest_path):
                return None
            
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            return manifest
            
        except Exception as e:
            logger.error(f"Error reading manifest: {e}")
            return None
    
    def _install_addon_components(self, addon: MarketplaceAddon, tenant_id: str,
                                extract_path: str, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Install add-on components"""
        try:
            # Install based on add-on type
            if addon.addon_type == AddonType.CONNECTOR:
                return self._install_connector(addon, tenant_id, extract_path, manifest)
            elif addon.addon_type == AddonType.INTEGRATION:
                return self._install_integration(addon, tenant_id, extract_path, manifest)
            elif addon.addon_type == AddonType.WORKFLOW:
                return self._install_workflow(addon, tenant_id, extract_path, manifest)
            elif addon.addon_type == AddonType.DASHBOARD:
                return self._install_dashboard(addon, tenant_id, extract_path, manifest)
            else:
                return self._install_generic(addon, tenant_id, extract_path, manifest)
                
        except Exception as e:
            logger.error(f"Error installing add-on components: {e}")
            return {"success": False, "error": str(e)}
    
    def _install_connector(self, addon: MarketplaceAddon, tenant_id: str,
                          extract_path: str, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Install connector add-on"""
        try:
            # Copy connector files to tenant directory
            connector_path = f"/tenants/{tenant_id}/connectors/{addon.addon_id}"
            os.makedirs(connector_path, exist_ok=True)
            
            # Copy files
            for file_name in os.listdir(extract_path):
                src_path = os.path.join(extract_path, file_name)
                dst_path = os.path.join(connector_path, file_name)
                
                if os.path.isfile(src_path):
                    shutil.copy2(src_path, dst_path)
            
            return {"success": True, "message": "Connector installed successfully"}
            
        except Exception as e:
            logger.error(f"Error installing connector: {e}")
            return {"success": False, "error": str(e)}
    
    def _install_integration(self, addon: MarketplaceAddon, tenant_id: str,
                            extract_path: str, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Install integration add-on"""
        try:
            # Copy integration files to tenant directory
            integration_path = f"/tenants/{tenant_id}/integrations/{addon.addon_id}"
            os.makedirs(integration_path, exist_ok=True)
            
            # Copy files
            for file_name in os.listdir(extract_path):
                src_path = os.path.join(extract_path, file_name)
                dst_path = os.path.join(integration_path, file_name)
                
                if os.path.isfile(src_path):
                    shutil.copy2(src_path, dst_path)
            
            return {"success": True, "message": "Integration installed successfully"}
            
        except Exception as e:
            logger.error(f"Error installing integration: {e}")
            return {"success": False, "error": str(e)}
    
    def _install_workflow(self, addon: MarketplaceAddon, tenant_id: str,
                         extract_path: str, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Install workflow add-on"""
        try:
            # Copy workflow files to tenant directory
            workflow_path = f"/tenants/{tenant_id}/workflows/{addon.addon_id}"
            os.makedirs(workflow_path, exist_ok=True)
            
            # Copy files
            for file_name in os.listdir(extract_path):
                src_path = os.path.join(extract_path, file_name)
                dst_path = os.path.join(workflow_path, file_name)
                
                if os.path.isfile(src_path):
                    shutil.copy2(src_path, dst_path)
            
            return {"success": True, "message": "Workflow installed successfully"}
            
        except Exception as e:
            logger.error(f"Error installing workflow: {e}")
            return {"success": False, "error": str(e)}
    
    def _install_dashboard(self, addon: MarketplaceAddon, tenant_id: str,
                          extract_path: str, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Install dashboard add-on"""
        try:
            # Copy dashboard files to tenant directory
            dashboard_path = f"/tenants/{tenant_id}/dashboards/{addon.addon_id}"
            os.makedirs(dashboard_path, exist_ok=True)
            
            # Copy files
            for file_name in os.listdir(extract_path):
                src_path = os.path.join(extract_path, file_name)
                dst_path = os.path.join(dashboard_path, file_name)
                
                if os.path.isfile(src_path):
                    shutil.copy2(src_path, dst_path)
            
            return {"success": True, "message": "Dashboard installed successfully"}
            
        except Exception as e:
            logger.error(f"Error installing dashboard: {e}")
            return {"success": False, "error": str(e)}
    
    def _install_generic(self, addon: MarketplaceAddon, tenant_id: str,
                        extract_path: str, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Install generic add-on"""
        try:
            # Copy files to tenant directory
            addon_path = f"/tenants/{tenant_id}/addons/{addon.addon_id}"
            os.makedirs(addon_path, exist_ok=True)
            
            # Copy files
            for file_name in os.listdir(extract_path):
                src_path = os.path.join(extract_path, file_name)
                dst_path = os.path.join(addon_path, file_name)
                
                if os.path.isfile(src_path):
                    shutil.copy2(src_path, dst_path)
            
            return {"success": True, "message": "Add-on installed successfully"}
            
        except Exception as e:
            logger.error(f"Error installing generic add-on: {e}")
            return {"success": False, "error": str(e)}

class PartnerManager:
    """Partner management system"""
    
    def __init__(self):
        self.partners: Dict[str, MarketplacePartner] = {}
        self.partner_integrations: Dict[str, List[Dict[str, Any]]] = {}
        self.revenue_tracker = RevenueTracker()
        
    def create_partner(self, name: str, partner_type: PartnerType,
                      description: str = "", website: str = "",
                      contact_email: str = "", contact_phone: str = "",
                      address: Dict[str, str] = None) -> str:
        """Create marketplace partner"""
        try:
            partner_id = f"PARTNER_{uuid.uuid4().hex[:8].upper()}"
            
            partner = MarketplacePartner(
                partner_id=partner_id,
                name=name,
                partner_type=partner_type,
                description=description,
                website=website,
                contact_email=contact_email,
                contact_phone=contact_phone,
                address=address or {}
            )
            
            self.partners[partner_id] = partner
            logger.info(f"Created partner: {name}")
            return partner_id
            
        except Exception as e:
            logger.error(f"Error creating partner: {e}")
            return ""
    
    def verify_partner(self, partner_id: str) -> bool:
        """Verify partner"""
        try:
            if partner_id not in self.partners:
                return False
            
            partner = self.partners[partner_id]
            partner.is_verified = True
            
            logger.info(f"Verified partner: {partner_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error verifying partner: {e}")
            return False
    
    def add_partner_integration(self, partner_id: str, integration_name: str,
                               integration_type: str, api_endpoint: str,
                               authentication: str = "api_key") -> str:
        """Add partner integration"""
        try:
            if partner_id not in self.partners:
                return ""
            
            integration_id = f"INT_{uuid.uuid4().hex[:8].upper()}"
            
            integration = {
                "integration_id": integration_id,
                "partner_id": partner_id,
                "integration_name": integration_name,
                "integration_type": integration_type,
                "api_endpoint": api_endpoint,
                "authentication": authentication,
                "created_at": datetime.utcnow().isoformat()
            }
            
            if partner_id not in self.partner_integrations:
                self.partner_integrations[partner_id] = []
            
            self.partner_integrations[partner_id].append(integration)
            
            logger.info(f"Added partner integration: {integration_id}")
            return integration_id
            
        except Exception as e:
            logger.error(f"Error adding partner integration: {e}")
            return ""
    
    def get_partner_details(self, partner_id: str) -> Dict[str, Any]:
        """Get partner details"""
        try:
            if partner_id not in self.partners:
                return {"error": "Partner not found"}
            
            partner = self.partners[partner_id]
            integrations = self.partner_integrations.get(partner_id, [])
            
            return {
                "partner_id": partner_id,
                "name": partner.name,
                "partner_type": partner.partner_type.value,
                "description": partner.description,
                "website": partner.website,
                "contact_email": partner.contact_email,
                "contact_phone": partner.contact_phone,
                "address": partner.address,
                "services": partner.services,
                "certifications": partner.certifications,
                "is_verified": partner.is_verified,
                "is_active": partner.is_active,
                "partnership_level": partner.partnership_level,
                "revenue_share_rate": partner.revenue_share_rate,
                "created_at": partner.created_at.isoformat(),
                "integrations": integrations
            }
            
        except Exception as e:
            logger.error(f"Error getting partner details: {e}")
            return {"error": str(e)}

class RevenueTracker:
    """Revenue tracking system"""
    
    def __init__(self):
        self.revenue_records: List[Dict[str, Any]] = []
        self.partner_revenues: Dict[str, float] = {}
        
    def record_revenue(self, addon_id: str, partner_id: str, amount: float,
                      revenue_type: str = "sale") -> str:
        """Record revenue"""
        try:
            record_id = f"REV_{uuid.uuid4().hex[:8].upper()}"
            
            record = {
                "record_id": record_id,
                "addon_id": addon_id,
                "partner_id": partner_id,
                "amount": amount,
                "revenue_type": revenue_type,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.revenue_records.append(record)
            
            # Update partner revenue
            if partner_id not in self.partner_revenues:
                self.partner_revenues[partner_id] = 0.0
            
            self.partner_revenues[partner_id] += amount
            
            logger.info(f"Recorded revenue: {record_id}")
            return record_id
            
        except Exception as e:
            logger.error(f"Error recording revenue: {e}")
            return ""
    
    def get_partner_revenue(self, partner_id: str) -> Dict[str, Any]:
        """Get partner revenue"""
        try:
            total_revenue = self.partner_revenues.get(partner_id, 0.0)
            
            # Get revenue records for partner
            partner_records = [
                record for record in self.revenue_records
                if record["partner_id"] == partner_id
            ]
            
            return {
                "partner_id": partner_id,
                "total_revenue": total_revenue,
                "record_count": len(partner_records),
                "revenue_by_type": self._get_revenue_by_type(partner_records)
            }
            
        except Exception as e:
            logger.error(f"Error getting partner revenue: {e}")
            return {"error": str(e)}
    
    def _get_revenue_by_type(self, records: List[Dict[str, Any]]) -> Dict[str, float]:
        """Get revenue by type"""
        try:
            revenue_by_type = {}
            
            for record in records:
                revenue_type = record["revenue_type"]
                if revenue_type not in revenue_by_type:
                    revenue_by_type[revenue_type] = 0.0
                revenue_by_type[revenue_type] += record["amount"]
            
            return revenue_by_type
            
        except Exception as e:
            logger.error(f"Error getting revenue by type: {e}")
            return {}

class APIMarketplaceManager:
    """API marketplace management"""
    
    def __init__(self):
        self.apis: Dict[str, APIMarketplace] = {}
        self.api_usage: Dict[str, List[Dict[str, Any]]] = {}
        
    def create_api(self, name: str, description: str, endpoint: str,
                  version: str = "1.0.0", authentication: str = "api_key",
                  rate_limit: int = 1000, pricing_tier: str = "free") -> str:
        """Create API marketplace entry"""
        try:
            api_id = f"API_{uuid.uuid4().hex[:8].upper()}"
            
            api = APIMarketplace(
                api_id=api_id,
                name=name,
                description=description,
                endpoint=endpoint,
                version=version,
                authentication=authentication,
                rate_limit=rate_limit,
                pricing_tier=pricing_tier
            )
            
            self.apis[api_id] = api
            logger.info(f"Created API: {name}")
            return api_id
            
        except Exception as e:
            logger.error(f"Error creating API: {e}")
            return ""
    
    def track_api_usage(self, api_id: str, tenant_id: str, endpoint: str,
                        response_time: float, status_code: int) -> str:
        """Track API usage"""
        try:
            usage_id = f"USAGE_{uuid.uuid4().hex[:8].upper()}"
            
            usage = {
                "usage_id": usage_id,
                "api_id": api_id,
                "tenant_id": tenant_id,
                "endpoint": endpoint,
                "response_time": response_time,
                "status_code": status_code,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if api_id not in self.api_usage:
                self.api_usage[api_id] = []
            
            self.api_usage[api_id].append(usage)
            
            logger.info(f"Tracked API usage: {usage_id}")
            return usage_id
            
        except Exception as e:
            logger.error(f"Error tracking API usage: {e}")
            return ""
    
    def get_api_usage_stats(self, api_id: str) -> Dict[str, Any]:
        """Get API usage statistics"""
        try:
            if api_id not in self.api_usage:
                return {"error": "API not found"}
            
            usage_records = self.api_usage[api_id]
            
            if not usage_records:
                return {
                    "api_id": api_id,
                    "total_requests": 0,
                    "average_response_time": 0.0,
                    "success_rate": 0.0
                }
            
            # Calculate statistics
            total_requests = len(usage_records)
            average_response_time = np.mean([record["response_time"] for record in usage_records])
            successful_requests = len([record for record in usage_records if record["status_code"] < 400])
            success_rate = successful_requests / total_requests if total_requests > 0 else 0.0
            
            return {
                "api_id": api_id,
                "total_requests": total_requests,
                "average_response_time": round(average_response_time, 3),
                "success_rate": round(success_rate, 3),
                "successful_requests": successful_requests,
                "failed_requests": total_requests - successful_requests
            }
            
        except Exception as e:
            logger.error(f"Error getting API usage stats: {e}")
            return {"error": str(e)}

class MarketplaceEngine:
    """Main marketplace engine"""
    
    def __init__(self):
        self.addon_manager = AddonManager()
        self.partner_manager = PartnerManager()
        self.api_marketplace_manager = APIMarketplaceManager()
        self.revenue_tracker = RevenueTracker()
        
    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive marketplace status"""
        try:
            return {
                "addons": {
                    "total": len(self.addon_manager.addons),
                    "approved": len([a for a in self.addon_manager.addons.values() if a.status == AddonStatus.APPROVED]),
                    "pending": len([a for a in self.addon_manager.addons.values() if a.status == AddonStatus.PENDING]),
                    "by_type": self._get_addons_by_type(),
                    "total_downloads": sum(a.download_count for a in self.addon_manager.addons.values())
                },
                "partners": {
                    "total": len(self.partner_manager.partners),
                    "verified": len([p for p in self.partner_manager.partners.values() if p.is_verified]),
                    "active": len([p for p in self.partner_manager.partners.values() if p.is_active]),
                    "by_type": self._get_partners_by_type()
                },
                "apis": {
                    "total": len(self.api_marketplace_manager.apis),
                    "active": len([a for a in self.api_marketplace_manager.apis.values() if a.is_active])
                },
                "revenue": {
                    "total_records": len(self.revenue_tracker.revenue_records),
                    "total_revenue": sum(self.revenue_tracker.partner_revenues.values())
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting comprehensive status: {e}")
            return {"error": str(e)}
    
    def _get_addons_by_type(self) -> Dict[str, int]:
        """Get add-ons by type"""
        try:
            addons_by_type = {}
            
            for addon in self.addon_manager.addons.values():
                addon_type = addon.addon_type.value
                if addon_type not in addons_by_type:
                    addons_by_type[addon_type] = 0
                addons_by_type[addon_type] += 1
            
            return addons_by_type
            
        except Exception as e:
            logger.error(f"Error getting add-ons by type: {e}")
            return {}
    
    def _get_partners_by_type(self) -> Dict[str, int]:
        """Get partners by type"""
        try:
            partners_by_type = {}
            
            for partner in self.partner_manager.partners.values():
                partner_type = partner.partner_type.value
                if partner_type not in partners_by_type:
                    partners_by_type[partner_type] = 0
                partners_by_type[partner_type] += 1
            
            return partners_by_type
            
        except Exception as e:
            logger.error(f"Error getting partners by type: {e}")
            return {}

# Global marketplace engine instance
marketplace_engine = MarketplaceEngine()

def create_addon(name: str, description: str, addon_type: AddonType,
                author: str, author_email: str, company: str = "",
                category: str = "", tags: List[str] = None) -> str:
    """Create marketplace add-on"""
    return marketplace_engine.addon_manager.create_addon(
        name, description, addon_type, author, author_email, company, category, tags
    )

def upload_addon_file(addon_id: str, file_path: str) -> bool:
    """Upload add-on file"""
    return marketplace_engine.addon_manager.upload_addon_file(addon_id, file_path)

def submit_addon_for_review(addon_id: str) -> bool:
    """Submit add-on for review"""
    return marketplace_engine.addon_manager.submit_for_review(addon_id)

def approve_addon(addon_id: str) -> bool:
    """Approve add-on"""
    return marketplace_engine.addon_manager.approve_addon(addon_id)

def install_addon(addon_id: str, tenant_id: str, user_id: str) -> str:
    """Install add-on for tenant"""
    return marketplace_engine.addon_manager.install_addon(addon_id, tenant_id, user_id)

def add_addon_review(addon_id: str, user_id: str, rating: int,
                    title: str = "", comment: str = "") -> str:
    """Add review for add-on"""
    return marketplace_engine.addon_manager.add_review(addon_id, user_id, rating, title, comment)

def get_addon_details(addon_id: str) -> Dict[str, Any]:
    """Get add-on details"""
    return marketplace_engine.addon_manager.get_addon_details(addon_id)

def create_partner(name: str, partner_type: PartnerType,
                  description: str = "", website: str = "",
                  contact_email: str = "", contact_phone: str = "",
                  address: Dict[str, str] = None) -> str:
    """Create marketplace partner"""
    return marketplace_engine.partner_manager.create_partner(
        name, partner_type, description, website, contact_email, contact_phone, address
    )

def verify_partner(partner_id: str) -> bool:
    """Verify partner"""
    return marketplace_engine.partner_manager.verify_partner(partner_id)

def get_partner_details(partner_id: str) -> Dict[str, Any]:
    """Get partner details"""
    return marketplace_engine.partner_manager.get_partner_details(partner_id)

def create_api(name: str, description: str, endpoint: str,
              version: str = "1.0.0", authentication: str = "api_key",
              rate_limit: int = 1000, pricing_tier: str = "free") -> str:
    """Create API marketplace entry"""
    return marketplace_engine.api_marketplace_manager.create_api(
        name, description, endpoint, version, authentication, rate_limit, pricing_tier
    )

def get_marketplace_status() -> Dict[str, Any]:
    """Get comprehensive marketplace status"""
    return marketplace_engine.get_comprehensive_status()
