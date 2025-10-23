"""
Blockchain Carbon NFT API Routers
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from ..base import get_db
from .services import CarbonNFTService, CarbonTokenType

router = APIRouter(prefix="/blockchain", tags=["Blockchain Carbon NFT"])

@router.post("/carbon-nft/create")
async def create_carbon_nft(
    token_type: CarbonTokenType = Body(..., description="Type of carbon token"),
    carbon_amount: float = Body(..., gt=0, description="Amount of carbon in tons CO2"),
    issuer: str = Body(..., description="Issuer of the token"),
    verifier: str = Body(..., description="Verifier of the carbon data"),
    metadata: Dict[str, Any] = Body(default_factory=dict, description="Additional metadata"),
    expiry_days: int = Body(365, ge=1, le=3650, description="Token expiry in days"),
    db: Session = Depends(get_db)
):
    """Create a new carbon NFT with blockchain verification"""
    carbon_service = CarbonNFTService()
    
    try:
        carbon_nft = carbon_service.create_carbon_nft(
            token_type, carbon_amount, issuer, verifier, metadata, expiry_days
        )
        
        return {
            "success": True,
            "carbon_nft": {
                "token_id": carbon_nft.token_id,
                "token_type": carbon_nft.token_type.value,
                "carbon_amount": carbon_nft.carbon_amount,
                "issuer": carbon_nft.issuer,
                "verifier": carbon_nft.verifier,
                "issue_date": carbon_nft.issue_date.isoformat(),
                "expiry_date": carbon_nft.expiry_date.isoformat(),
                "status": carbon_nft.status.value,
                "blockchain_hash": carbon_nft.blockchain_hash,
                "transaction_hash": carbon_nft.transaction_hash,
                "metadata": carbon_nft.metadata
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/carbon-nft/{token_id}/verify")
async def verify_carbon_nft(
    token_id: str,
    db: Session = Depends(get_db)
):
    """Verify carbon NFT authenticity using blockchain hash"""
    carbon_service = CarbonNFTService()
    
    verification = carbon_service.verify_carbon_nft(token_id)
    
    return {
        "success": True,
        "verification": verification
    }

@router.post("/carbon-nft/{token_id}/trade")
async def trade_carbon_nft(
    token_id: str,
    from_address: str = Body(..., description="Seller address"),
    to_address: str = Body(..., description="Buyer address"),
    price_usd: float = Body(..., gt=0, description="Price in USD"),
    db: Session = Depends(get_db)
):
    """Trade carbon NFT between addresses"""
    carbon_service = CarbonNFTService()
    
    try:
        transaction = carbon_service.trade_carbon_nft(token_id, from_address, to_address, price_usd)
        
        return {
            "success": True,
            "transaction": {
                "transaction_hash": transaction.transaction_hash,
                "from_address": transaction.from_address,
                "to_address": transaction.to_address,
                "amount": transaction.amount,
                "token_id": transaction.token_id,
                "gas_used": transaction.gas_used,
                "gas_price": transaction.gas_price,
                "block_number": transaction.block_number,
                "timestamp": transaction.timestamp.isoformat(),
                "status": transaction.status
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/portfolio/{address}")
async def get_carbon_nft_portfolio(
    address: str,
    db: Session = Depends(get_db)
):
    """Get carbon NFT portfolio for an address"""
    carbon_service = CarbonNFTService()
    
    portfolio = carbon_service.get_carbon_nft_portfolio(address)
    
    return {
        "success": True,
        "address": address,
        "portfolio": portfolio,
        "total_tokens": len(portfolio),
        "total_carbon": sum(nft["carbon_amount"] for nft in portfolio),
        "total_value": sum(nft["total_value"] for nft in portfolio)
    }

@router.get("/carbon-footprint/{address}")
async def calculate_carbon_footprint(
    address: str,
    db: Session = Depends(get_db)
):
    """Calculate carbon footprint for an address"""
    carbon_service = CarbonNFTService()
    
    footprint = carbon_service.calculate_carbon_footprint(address)
    
    return {
        "success": True,
        "carbon_footprint": footprint
    }

@router.get("/token-types")
async def get_carbon_token_types():
    """Get available carbon token types"""
    return {
        "token_types": [
            {
                "type": "carbon_credit",
                "name": "Carbon Credit",
                "description": "Verified carbon reduction credits",
                "use_case": "Carbon offset trading and compliance"
            },
            {
                "type": "renewable_energy",
                "name": "Renewable Energy Certificate",
                "description": "Certificates for renewable energy generation",
                "use_case": "Renewable energy trading and ESG compliance"
            },
            {
                "type": "carbon_offset",
                "name": "Carbon Offset",
                "description": "Direct carbon offset projects",
                "use_case": "Corporate carbon neutrality programs"
            },
            {
                "type": "esg_certificate",
                "name": "ESG Certificate",
                "description": "Environmental, Social, Governance certificates",
                "use_case": "ESG compliance and sustainability reporting"
            }
        ]
    }

@router.get("/blockchain-status")
async def get_blockchain_status():
    """Get blockchain connection status and capabilities"""
    return {
        "web3_available": True,  # Will be determined at runtime
        "capabilities": {
            "nft_minting": True,
            "hash_verification": True,
            "transaction_tracking": True,
            "portfolio_management": True
        },
        "supported_networks": [
            "Ethereum Mainnet",
            "Ethereum Testnet",
            "Polygon",
            "Binance Smart Chain"
        ],
        "features": [
            "Carbon NFT creation and verification",
            "Blockchain hash verification",
            "NFT trading and transfer",
            "Portfolio management",
            "Carbon footprint calculation"
        ]
    }
