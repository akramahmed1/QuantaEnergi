"""
Blockchain Services
Carbon NFT Web3 implementation with hash verification
"""
import hashlib
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
from enum import Enum
from dataclasses import dataclass, asdict
import uuid

# Web3 imports with fallbacks
try:
    from web3 import Web3
    from eth_account import Account
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False
    print("Warning: Web3 not available, using mock blockchain implementation")

logger = logging.getLogger(__name__)

class CarbonTokenType(str, Enum):
    CARBON_CREDIT = "carbon_credit"
    RENEWABLE_ENERGY = "renewable_energy"
    CARBON_OFFSET = "carbon_offset"
    ESG_CERTIFICATE = "esg_certificate"

class TokenStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    TRADED = "traded"
    RETIRED = "retired"
    EXPIRED = "expired"

@dataclass
class CarbonNFT:
    token_id: str
    token_type: CarbonTokenType
    carbon_amount: float  # in tons CO2
    issuer: str
    verifier: str
    issue_date: datetime
    expiry_date: datetime
    status: TokenStatus
    blockchain_hash: str
    metadata: Dict[str, Any]
    transaction_hash: Optional[str] = None
    owner: Optional[str] = None
    price_usd: Optional[float] = None

@dataclass
class BlockchainTransaction:
    transaction_hash: str
    from_address: str
    to_address: str
    amount: float
    token_id: str
    gas_used: int
    gas_price: int
    block_number: int
    timestamp: datetime
    status: str

class CarbonNFTService:
    """Carbon NFT Web3 service with hash verification"""
    
    def __init__(self):
        self.web3 = None
        self.contract_address = None
        self.private_key = None
        self.account = None
        self._initialize_web3()
    
    def _initialize_web3(self):
        """Initialize Web3 connection"""
        try:
            if WEB3_AVAILABLE:
                # Connect to Ethereum mainnet or testnet
                # For demo purposes, using mock connection
                self.web3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/demo"))
                
                # Generate demo account
                self.account = Account.create()
                self.private_key = self.account.privateKey.hex()
                
                # Mock contract address
                self.contract_address = "0x1234567890123456789012345678901234567890"
                
                logger.info("Web3 connection initialized successfully")
            else:
                logger.info("Using mock blockchain implementation")
                
        except Exception as e:
            logger.error(f"Error initializing Web3: {e}")
            logger.info("Falling back to mock blockchain implementation")
    
    def create_carbon_nft(self,
                         token_type: CarbonTokenType,
                         carbon_amount: float,
                         issuer: str,
                         verifier: str,
                         metadata: Dict[str, Any],
                         expiry_days: int = 365) -> CarbonNFT:
        """
        Create a new carbon NFT with blockchain verification
        
        Args:
            token_type: Type of carbon token
            carbon_amount: Amount of carbon in tons CO2
            issuer: Issuer of the token
            verifier: Verifier of the carbon data
            metadata: Additional metadata
            expiry_days: Token expiry in days
            
        Returns:
            Created carbon NFT
        """
        try:
            # Generate unique token ID
            token_id = f"CNFT-{uuid.uuid4().hex[:16].upper()}"
            
            # Create token metadata
            issue_date = datetime.now()
            expiry_date = issue_date + timedelta(days=expiry_days)
            
            # Create blockchain hash
            blockchain_hash = self._create_blockchain_hash(
                token_id, token_type, carbon_amount, issuer, verifier, issue_date
            )
            
            # Create carbon NFT
            carbon_nft = CarbonNFT(
                token_id=token_id,
                token_type=token_type,
                carbon_amount=carbon_amount,
                issuer=issuer,
                verifier=verifier,
                issue_date=issue_date,
                expiry_date=expiry_date,
                status=TokenStatus.PENDING,
                blockchain_hash=blockchain_hash,
                metadata=metadata
            )
            
            # Mint NFT on blockchain (mock implementation)
            transaction_hash = self._mint_nft_on_blockchain(carbon_nft)
            carbon_nft.transaction_hash = transaction_hash
            carbon_nft.status = TokenStatus.VERIFIED
            
            logger.info(f"Carbon NFT created: {token_id}")
            return carbon_nft
            
        except Exception as e:
            logger.error(f"Error creating carbon NFT: {e}")
            raise
    
    def verify_carbon_nft(self, token_id: str) -> Dict[str, Any]:
        """
        Verify carbon NFT authenticity using blockchain hash
        
        Args:
            token_id: Token ID to verify
            
        Returns:
            Verification result
        """
        try:
            # In real implementation, this would query the blockchain
            # For demo, we'll simulate verification
            
            # Mock blockchain query
            blockchain_data = self._query_blockchain(token_id)
            
            if blockchain_data:
                # Verify hash integrity
                hash_valid = self._verify_hash_integrity(token_id, blockchain_data)
                
                # Check token status
                status_valid = blockchain_data.get("status") == "verified"
                
                # Check expiry
                expiry_valid = self._check_token_expiry(blockchain_data.get("expiry_date"))
                
                verification_result = {
                    "token_id": token_id,
                    "verified": hash_valid and status_valid and expiry_valid,
                    "hash_valid": hash_valid,
                    "status_valid": status_valid,
                    "expiry_valid": expiry_valid,
                    "blockchain_data": blockchain_data,
                    "verification_timestamp": datetime.now().isoformat()
                }
                
                return verification_result
            else:
                return {
                    "token_id": token_id,
                    "verified": False,
                    "error": "Token not found on blockchain",
                    "verification_timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error verifying carbon NFT: {e}")
            return {
                "token_id": token_id,
                "verified": False,
                "error": str(e),
                "verification_timestamp": datetime.now().isoformat()
            }
    
    def trade_carbon_nft(self,
                        token_id: str,
                        from_address: str,
                        to_address: str,
                        price_usd: float) -> BlockchainTransaction:
        """
        Trade carbon NFT between addresses
        
        Args:
            token_id: Token ID to trade
            from_address: Seller address
            to_address: Buyer address
            price_usd: Price in USD
            
        Returns:
            Blockchain transaction
        """
        try:
            # Verify token exists and is tradeable
            verification = self.verify_carbon_nft(token_id)
            if not verification["verified"]:
                raise ValueError(f"Token {token_id} is not verified or tradeable")
            
            # Create transaction
            transaction_hash = self._create_transaction_hash(
                token_id, from_address, to_address, price_usd
            )
            
            # Execute trade on blockchain
            gas_used, gas_price, block_number = self._execute_trade_transaction(
                token_id, from_address, to_address, price_usd
            )
            
            # Create transaction record
            transaction = BlockchainTransaction(
                transaction_hash=transaction_hash,
                from_address=from_address,
                to_address=to_address,
                amount=price_usd,
                token_id=token_id,
                gas_used=gas_used,
                gas_price=gas_price,
                block_number=block_number,
                timestamp=datetime.now(),
                status="confirmed"
            )
            
            logger.info(f"Carbon NFT traded: {token_id} from {from_address} to {to_address}")
            return transaction
            
        except Exception as e:
            logger.error(f"Error trading carbon NFT: {e}")
            raise
    
    def get_carbon_nft_portfolio(self, address: str) -> List[Dict[str, Any]]:
        """
        Get carbon NFT portfolio for an address
        
        Args:
            address: Wallet address
            
        Returns:
            List of carbon NFTs owned by address
        """
        try:
            # Query blockchain for NFTs owned by address
            portfolio = self._query_address_nfts(address)
            
            # Format portfolio data
            formatted_portfolio = []
            for nft in portfolio:
                formatted_portfolio.append({
                    "token_id": nft["token_id"],
                    "token_type": nft["token_type"],
                    "carbon_amount": nft["carbon_amount"],
                    "status": nft["status"],
                    "issue_date": nft["issue_date"],
                    "expiry_date": nft["expiry_date"],
                    "current_price": nft.get("current_price", 0),
                    "total_value": nft["carbon_amount"] * nft.get("current_price", 0)
                })
            
            return formatted_portfolio
            
        except Exception as e:
            logger.error(f"Error getting carbon NFT portfolio: {e}")
            return []
    
    def calculate_carbon_footprint(self, address: str) -> Dict[str, Any]:
        """
        Calculate carbon footprint for an address
        
        Args:
            address: Wallet address
            
        Returns:
            Carbon footprint calculation
        """
        try:
            portfolio = self.get_carbon_nft_portfolio(address)
            
            total_carbon = sum(nft["carbon_amount"] for nft in portfolio)
            total_value = sum(nft["total_value"] for nft in portfolio)
            
            # Calculate ESG score based on carbon tokens
            esg_score = self._calculate_esg_score_from_tokens(portfolio)
            
            return {
                "address": address,
                "total_carbon_tons": total_carbon,
                "total_value_usd": total_value,
                "token_count": len(portfolio),
                "esg_score": esg_score,
                "carbon_intensity": total_carbon / max(total_value, 1),  # tons per USD
                "calculation_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating carbon footprint: {e}")
            return {
                "address": address,
                "error": str(e),
                "calculation_timestamp": datetime.now().isoformat()
            }
    
    def _create_blockchain_hash(self,
                              token_id: str,
                              token_type: CarbonTokenType,
                              carbon_amount: float,
                              issuer: str,
                              verifier: str,
                              issue_date: datetime) -> str:
        """Create blockchain hash for token"""
        # Create hash input
        hash_input = {
            "token_id": token_id,
            "token_type": token_type.value,
            "carbon_amount": carbon_amount,
            "issuer": issuer,
            "verifier": verifier,
            "issue_date": issue_date.isoformat()
        }
        
        # Create hash
        hash_string = json.dumps(hash_input, sort_keys=True)
        blockchain_hash = hashlib.sha256(hash_string.encode()).hexdigest()
        
        return blockchain_hash
    
    def _mint_nft_on_blockchain(self, carbon_nft: CarbonNFT) -> str:
        """Mint NFT on blockchain (mock implementation)"""
        # In real implementation, this would interact with smart contract
        transaction_hash = f"0x{hashlib.sha256(carbon_nft.token_id.encode()).hexdigest()[:40]}"
        return transaction_hash
    
    def _query_blockchain(self, token_id: str) -> Optional[Dict[str, Any]]:
        """Query blockchain for token data (mock implementation)"""
        # Mock blockchain data
        return {
            "token_id": token_id,
            "status": "verified",
            "expiry_date": (datetime.now() + timedelta(days=365)).isoformat(),
            "blockchain_hash": f"mock_hash_{token_id}",
            "transaction_hash": f"mock_tx_{token_id}"
        }
    
    def _verify_hash_integrity(self, token_id: str, blockchain_data: Dict[str, Any]) -> bool:
        """Verify hash integrity"""
        # Mock verification - in real implementation, this would verify
        # the hash against the blockchain data
        return True
    
    def _check_token_expiry(self, expiry_date_str: str) -> bool:
        """Check if token is not expired"""
        try:
            expiry_date = datetime.fromisoformat(expiry_date_str)
            return datetime.now() < expiry_date
        except:
            return False
    
    def _create_transaction_hash(self, token_id: str, from_addr: str, to_addr: str, price: float) -> str:
        """Create transaction hash"""
        hash_input = f"{token_id}{from_addr}{to_addr}{price}{datetime.now().isoformat()}"
        return f"0x{hashlib.sha256(hash_input.encode()).hexdigest()[:40]}"
    
    def _execute_trade_transaction(self, token_id: str, from_addr: str, to_addr: str, price: float) -> Tuple[int, int, int]:
        """Execute trade transaction on blockchain (mock implementation)"""
        # Mock transaction execution
        gas_used = 21000  # Standard gas limit
        gas_price = 20  # Gwei
        block_number = 18000000  # Mock block number
        
        return gas_used, gas_price, block_number
    
    def _query_address_nfts(self, address: str) -> List[Dict[str, Any]]:
        """Query NFTs owned by address (mock implementation)"""
        # Mock portfolio data
        return [
            {
                "token_id": "CNFT-1234567890ABCDEF",
                "token_type": "carbon_credit",
                "carbon_amount": 100.0,
                "status": "verified",
                "issue_date": (datetime.now() - timedelta(days=30)).isoformat(),
                "expiry_date": (datetime.now() + timedelta(days=335)).isoformat(),
                "current_price": 50.0
            },
            {
                "token_id": "CNFT-FEDCBA0987654321",
                "token_type": "renewable_energy",
                "carbon_amount": 50.0,
                "status": "verified",
                "issue_date": (datetime.now() - timedelta(days=15)).isoformat(),
                "expiry_date": (datetime.now() + timedelta(days=350)).isoformat(),
                "current_price": 75.0
            }
        ]
    
    def _calculate_esg_score_from_tokens(self, portfolio: List[Dict[str, Any]]) -> float:
        """Calculate ESG score from carbon tokens"""
        if not portfolio:
            return 0.0
        
        # Calculate score based on carbon amount and token types
        total_carbon = sum(nft["carbon_amount"] for nft in portfolio)
        renewable_tokens = sum(1 for nft in portfolio if nft["token_type"] == "renewable_energy")
        
        # Base score from carbon amount (more carbon = higher score)
        base_score = min(total_carbon / 1000, 100)  # Max 100 for 1000+ tons
        
        # Bonus for renewable energy tokens
        renewable_bonus = renewable_tokens * 10
        
        esg_score = min(base_score + renewable_bonus, 100)
        return round(esg_score, 2)
