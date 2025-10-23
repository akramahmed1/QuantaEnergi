"""
Advanced Contract Management Service
ETRM/CTRM Master Agreements, ISDA-style Contracts, Amendment Workflows
"""

from fastapi import HTTPException
from typing import Dict, List, Optional, Any
import asyncio
import logging
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib

logger = logging.getLogger(__name__)

class ContractType(Enum):
    """Contract type enumeration"""
    ISDA = "isda"
    PPA = "ppa"  # Power Purchase Agreement
    GAS_SALE = "gas_sale"
    OIL_SALE = "oil_sale"
    CARBON_CREDIT = "carbon_credit"
    MASTER_AGREEMENT = "master_agreement"

class ContractStatus(Enum):
    """Contract status enumeration"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    AMENDED = "amended"
    TERMINATED = "terminated"
    EXPIRED = "expired"

class ContractTypeFactory:
    """Factory pattern for creating different contract types"""
    
    @staticmethod
    def create_contract(contract_type: ContractType, data: Dict) -> Dict:
        """Create contract based on type with appropriate structure"""
        try:
            if contract_type == ContractType.ISDA:
                return ContractTypeFactory._create_isda_contract(data)
            elif contract_type == ContractType.PPA:
                return ContractTypeFactory._create_ppa_contract(data)
            elif contract_type == ContractType.GAS_SALE:
                return ContractTypeFactory._create_gas_sale_contract(data)
            elif contract_type == ContractType.OIL_SALE:
                return ContractTypeFactory._create_oil_sale_contract(data)
            elif contract_type == ContractType.CARBON_CREDIT:
                return ContractTypeFactory._create_carbon_credit_contract(data)
            elif contract_type == ContractType.MASTER_AGREEMENT:
                return ContractTypeFactory._create_master_agreement_contract(data)
            else:
                raise ValueError(f"Unsupported contract type: {contract_type}")
        except Exception as e:
            logger.error(f"Contract creation failed: {str(e)}")
            raise
    
    @staticmethod
    def _create_isda_contract(data: Dict) -> Dict:
        """Create ISDA-style contract structure"""
        return {
            "contract_type": "isda",
            "isda_version": data.get("isda_version", "2002"),
            "governing_law": data.get("governing_law", "English Law"),
            "credit_support_annex": data.get("credit_support_annex", True),
            "netting_agreement": data.get("netting_agreement", True),
            "termination_events": data.get("termination_events", ["default", "bankruptcy"]),
            "calculation_agent": data.get("calculation_agent", "party_a"),
            "dispute_resolution": data.get("dispute_resolution", "arbitration"),
            "data": data
        }
    
    @staticmethod
    def _create_ppa_contract(data: Dict) -> Dict:
        """Create Power Purchase Agreement structure"""
        return {
            "contract_type": "ppa",
            "power_plant": data.get("power_plant", {}),
            "capacity_mw": data.get("capacity_mw", 0),
            "tariff_structure": data.get("tariff_structure", "fixed"),
            "delivery_point": data.get("delivery_point", ""),
            "force_majeure": data.get("force_majeure", True),
            "environmental_attributes": data.get("environmental_attributes", True),
            "data": data
        }
    
    @staticmethod
    def _create_gas_sale_contract(data: Dict) -> Dict:
        """Create gas sale contract structure"""
        return {
            "contract_type": "gas_sale",
            "commodity": "natural_gas",
            "delivery_term": data.get("delivery_term", "fob"),
            "pricing_mechanism": data.get("pricing_mechanism", "hub_indexed"),
            "volume_mmbtu": data.get("volume_mmbtu", 0),
            "data": data
        }
    
    @staticmethod
    def _create_oil_sale_contract(data: Dict) -> Dict:
        """Create oil sale contract structure"""
        return {
            "contract_type": "oil_sale",
            "commodity": data.get("oil_type", "crude_oil"),
            "delivery_term": data.get("delivery_term", "fob"),
            "pricing_mechanism": data.get("pricing_mechanism", "dated_brent"),
            "volume_bbl": data.get("volume_bbl", 0),
            "data": data
        }
    
    @staticmethod
    def _create_carbon_credit_contract(data: Dict) -> Dict:
        """Create carbon credit contract structure"""
        return {
            "contract_type": "carbon_credit",
            "credit_type": data.get("credit_type", "ver"),
            "vintage_year": data.get("vintage_year", datetime.now().year),
            "volume_tco2e": data.get("volume_tco2e", 0),
            "verification_standard": data.get("verification_standard", "VCS"),
            "data": data
        }
    
    @staticmethod
    def _create_master_agreement_contract(data: Dict) -> Dict:
        """Create master agreement contract structure"""
        return {
            "contract_type": "master_agreement",
            "agreement_type": data.get("agreement_type", "energy_trading"),
            "governing_law": data.get("governing_law", "English Law"),
            "jurisdiction": data.get("jurisdiction", "London"),
            "data": data
        }

class AdvancedContractManagement:
    """Advanced contract management with factory pattern and amendment workflows"""
    
    def __init__(self):
        self.contracts = {}
        self.amendments = {}
        self.workflows = {}
        self.factory = ContractTypeFactory()
    
    async def create_master_agreement(self, agreement_data: Dict) -> Dict:
        """Create master agreement with proper validation"""
        try:
            if not agreement_data.get("organization_id"):
                raise ValueError("Organization ID is required")
            
            if not agreement_data.get("counterparty_id"):
                raise ValueError("Counterparty ID is required")
            
            agreement_id = str(uuid4())
            
            # Create master agreement using factory
            contract = self.factory.create_contract(
                ContractType.MASTER_AGREEMENT, 
                agreement_data
            )
            
            # Add metadata
            master_agreement = {
                "agreement_id": agreement_id,
                "organization_id": agreement_data["organization_id"],
                "counterparty_id": agreement_data["counterparty_id"],
                "status": ContractStatus.DRAFT.value,
                "created_at": datetime.utcnow().isoformat(),
                "created_by": agreement_data.get("created_by", "system"),
                "version": "1.0",
                "contract": contract,
                "effective_date": agreement_data.get("effective_date"),
                "expiry_date": agreement_data.get("expiry_date"),
                "governing_law": agreement_data.get("governing_law", "English Law"),
                "jurisdiction": agreement_data.get("jurisdiction", "London")
            }
            
            self.contracts[agreement_id] = master_agreement
            
            logger.info(f"Master agreement {agreement_id} created successfully")
            return master_agreement
            
        except ValueError as e:
            logger.error(f"Master agreement validation error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Master agreement creation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Master agreement creation failed: {str(e)}")
    
    async def create_contract(self, contract_type: str, contract_data: Dict) -> Dict:
        """Create specific contract type using factory pattern"""
        try:
            if not contract_data.get("organization_id"):
                raise ValueError("Organization ID is required")
            
            if not contract_data.get("master_agreement_id"):
                raise ValueError("Master agreement ID is required")
            
            contract_id = str(uuid4())
            
            # Validate contract type
            try:
                contract_type_enum = ContractType(contract_type)
            except ValueError:
                raise ValueError(f"Invalid contract type: {contract_type}")
            
            # Create contract using factory
            contract = self.factory.create_contract(contract_type_enum, contract_data)
            
            # Add metadata
            contract_record = {
                "contract_id": contract_id,
                "contract_type": contract_type,
                "organization_id": contract_data["organization_id"],
                "master_agreement_id": contract_data["master_agreement_id"],
                "status": ContractStatus.DRAFT.value,
                "created_at": datetime.utcnow().isoformat(),
                "created_by": contract_data.get("created_by", "system"),
                "version": "1.0",
                "contract": contract,
                "effective_date": contract_data.get("effective_date"),
                "expiry_date": contract_data.get("expiry_date"),
                "notional_amount": contract_data.get("notional_amount", 0),
                "currency": contract_data.get("currency", "USD")
            }
            
            self.contracts[contract_id] = contract_record
            
            logger.info(f"Contract {contract_id} of type {contract_type} created successfully")
            return contract_record
            
        except ValueError as e:
            logger.error(f"Contract validation error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Contract creation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Contract creation failed: {str(e)}")
    
    async def amend_contract(self, contract_id: str, amendments: Dict) -> Dict:
        """Amend existing contract with version control"""
        try:
            if contract_id not in self.contracts:
                raise ValueError(f"Contract {contract_id} not found")
            
            contract = self.contracts[contract_id]
            
            if contract["status"] == ContractStatus.TERMINATED.value:
                raise ValueError("Cannot amend terminated contract")
            
            amendment_id = str(uuid4())
            
            # Create amendment record
            amendment_record = {
                "amendment_id": amendment_id,
                "contract_id": contract_id,
                "amendment_type": amendments.get("type", "general"),
                "changes": amendments.get("changes", {}),
                "reason": amendments.get("reason", ""),
                "created_at": datetime.utcnow().isoformat(),
                "created_by": amendments.get("created_by", "system"),
                "status": "pending_approval",
                "effective_date": amendments.get("effective_date"),
                "approval_required": amendments.get("approval_required", True)
            }
            
            self.amendments[amendment_id] = amendment_record
            
            # Update contract status
            contract["status"] = ContractStatus.AMENDED.value
            contract["last_amended"] = datetime.utcnow().isoformat()
            contract["version"] = f"{float(contract['version']) + 0.1:.1f}"
            
            logger.info(f"Amendment {amendment_id} created for contract {contract_id}")
            return amendment_record
            
        except ValueError as e:
            logger.error(f"Contract amendment validation error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Contract amendment failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Contract amendment failed: {str(e)}")
    
    async def execute_amendment_workflow(self, amendment_id: str) -> Dict:
        """Execute amendment workflow with approval process"""
        try:
            if amendment_id not in self.amendments:
                raise ValueError(f"Amendment {amendment_id} not found")
            
            amendment = self.amendments[amendment_id]
            contract_id = amendment["contract_id"]
            
            if contract_id not in self.contracts:
                raise ValueError(f"Contract {contract_id} not found")
            
            contract = self.contracts[contract_id]
            
            # Simulate approval workflow
            workflow_steps = [
                {"step": "validation", "status": "completed", "timestamp": datetime.utcnow().isoformat()},
                {"step": "legal_review", "status": "completed", "timestamp": datetime.utcnow().isoformat()},
                {"step": "counterparty_approval", "status": "completed", "timestamp": datetime.utcnow().isoformat()},
                {"step": "final_approval", "status": "completed", "timestamp": datetime.utcnow().isoformat()}
            ]
            
            # Update amendment status
            amendment["status"] = "approved"
            amendment["workflow_steps"] = workflow_steps
            amendment["approved_at"] = datetime.utcnow().isoformat()
            
            # Apply changes to contract
            if amendment["changes"]:
                contract["contract"].update(amendment["changes"])
                contract["last_modified"] = datetime.utcnow().isoformat()
            
            # Update contract status
            contract["status"] = ContractStatus.ACTIVE.value
            
            workflow_result = {
                "amendment_id": amendment_id,
                "contract_id": contract_id,
                "status": "executed",
                "workflow_steps": workflow_steps,
                "executed_at": datetime.utcnow().isoformat()
            }
            
            self.workflows[amendment_id] = workflow_result
            
            logger.info(f"Amendment workflow {amendment_id} executed successfully")
            return workflow_result
            
        except ValueError as e:
            logger.error(f"Amendment workflow validation error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Amendment workflow execution failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Amendment workflow execution failed: {str(e)}")
    
    async def get_contract_analytics(self, organization_id: str) -> Dict:
        """Get contract analytics and performance metrics"""
        try:
            # Filter contracts by organization
            org_contracts = [
                c for c in self.contracts.values() 
                if c.get("organization_id") == organization_id
            ]
            
            # Calculate analytics
            total_contracts = len(org_contracts)
            active_contracts = len([c for c in org_contracts if c.get("status") == ContractStatus.ACTIVE.value])
            draft_contracts = len([c for c in org_contracts if c.get("status") == ContractStatus.DRAFT.value])
            amended_contracts = len([c for c in org_contracts if c.get("status") == ContractStatus.AMENDED.value])
            
            # Contract type distribution
            type_distribution = {}
            for contract in org_contracts:
                contract_type = contract.get("contract_type", "unknown")
                type_distribution[contract_type] = type_distribution.get(contract_type, 0) + 1
            
            # Total notional amount
            total_notional = sum(c.get("notional_amount", 0) for c in org_contracts)
            
            analytics = {
                "total_contracts": total_contracts,
                "active_contracts": active_contracts,
                "draft_contracts": draft_contracts,
                "amended_contracts": amended_contracts,
                "type_distribution": type_distribution,
                "total_notional_amount": total_notional,
                "average_contract_value": total_notional / max(total_contracts, 1),
                "contract_utilization_rate": active_contracts / max(total_contracts, 1)
            }
            
            logger.info(f"Contract analytics generated for organization {organization_id}")
            return analytics
            
        except Exception as e:
            logger.error(f"Contract analytics generation failed for {organization_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Contract analytics generation failed: {str(e)}")
    
    async def search_contracts(self, organization_id: str, filters: Dict) -> List[Dict]:
        """Search contracts with filters"""
        try:
            org_contracts = [
                c for c in self.contracts.values() 
                if c.get("organization_id") == organization_id
            ]
            
            # Apply filters
            filtered_contracts = org_contracts
            
            if filters.get("contract_type"):
                filtered_contracts = [
                    c for c in filtered_contracts 
                    if c.get("contract_type") == filters["contract_type"]
                ]
            
            if filters.get("status"):
                filtered_contracts = [
                    c for c in filtered_contracts 
                    if c.get("status") == filters["status"]
                ]
            
            if filters.get("date_from"):
                date_from = datetime.fromisoformat(filters["date_from"])
                filtered_contracts = [
                    c for c in filtered_contracts 
                    if datetime.fromisoformat(c.get("created_at", "")) >= date_from
                ]
            
            if filters.get("date_to"):
                date_to = datetime.fromisoformat(filters["date_to"])
                filtered_contracts = [
                    c for c in filtered_contracts 
                    if datetime.fromisoformat(c.get("created_at", "")) <= date_to
                ]
            
            logger.info(f"Contract search completed for organization {organization_id}")
            return filtered_contracts
            
        except Exception as e:
            logger.error(f"Contract search failed for {organization_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Contract search failed: {str(e)}")
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            logger.info("Contract management cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")
