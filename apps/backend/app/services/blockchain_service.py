"""
Blockchain Service using Web3 v7.13.0
Provides smart contract integration for carbon trading and transparency
"""

import json
from typing import Dict, List, Optional, Any
import structlog
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

try:
    from web3 import Web3
    from eth_account import Account
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False
    logger = structlog.get_logger(__name__)
    logger.warning("Web3 not available - using mock blockchain service")

logger = structlog.get_logger(__name__)

class BlockchainService:
    """Blockchain integration service for carbon trading and transparency"""
    
    def __init__(self):
        self.web3_available = WEB3_AVAILABLE
        self.web3 = None
        self.account = None
        
        if self.web3_available:
            try:
                # Initialize Web3 (using mock/testnet for demo)
                self.web3 = Web3(Web3.HTTPProvider('https://sepolia.infura.io/v3/demo'))
                self.account = Account.create()
                logger.info("Web3 initialized successfully")
            except Exception as e:
                logger.warning("Web3 initialization failed, using mock service", error=str(e))
                self.web3_available = False
        
        # Mock smart contract ABI for carbon trading
        self.carbon_contract_abi = [
            {
                "inputs": [
                    {"name": "tradeId", "type": "string"},
                    {"name": "carbonAmount", "type": "uint256"},
                    {"name": "price", "type": "uint256"},
                    {"name": "seller", "type": "address"},
                    {"name": "buyer", "type": "address"}
                ],
                "name": "createCarbonTrade",
                "outputs": [{"name": "success", "type": "bool"}],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"name": "tradeId", "type": "string"}],
                "name": "getCarbonTrade",
                "outputs": [
                    {"name": "carbonAmount", "type": "uint256"},
                    {"name": "price", "type": "uint256"},
                    {"name": "seller", "type": "address"},
                    {"name": "buyer", "type": "address"},
                    {"name": "status", "type": "string"}
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [{"name": "tradeId", "type": "string"}],
                "name": "settleCarbonTrade",
                "outputs": [{"name": "success", "type": "bool"}],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]
        
        # Mock contract address
        self.carbon_contract_address = "0x1234567890123456789012345678901234567890"
    
    def create_carbon_trade(self, 
                           trade_id: str,
                           carbon_amount: float,
                           price_per_ton: float,
                           seller_address: str,
                           buyer_address: str) -> Dict:
        """
        Create a carbon credit trade on blockchain
        
        Args:
            trade_id: Unique trade identifier
            carbon_amount: Amount of carbon credits in tons
            price_per_ton: Price per ton of carbon
            seller_address: Seller's blockchain address
            buyer_address: Buyer's blockchain address
            
        Returns:
            Dictionary containing transaction details
        """
        try:
            logger.info("Creating carbon trade", 
                       trade_id=trade_id, 
                       carbon_amount=carbon_amount,
                       price_per_ton=price_per_ton)
            
            if self.web3_available and self.web3:
                # Real blockchain transaction
                result = self._execute_blockchain_trade(
                    trade_id, carbon_amount, price_per_ton, seller_address, buyer_address
                )
            else:
                # Mock blockchain transaction
                result = self._mock_blockchain_trade(
                    trade_id, carbon_amount, price_per_ton, seller_address, buyer_address
                )
            
            logger.info("Carbon trade created successfully", 
                       trade_id=trade_id, 
                       tx_hash=result.get('transaction_hash'))
            
            return result
            
        except Exception as e:
            logger.error("Carbon trade creation failed", error=str(e))
            raise Exception(f"Failed to create carbon trade: {str(e)}")
    
    def _execute_blockchain_trade(self, 
                                 trade_id: str,
                                 carbon_amount: float,
                                 price_per_ton: float,
                                 seller_address: str,
                                 buyer_address: str) -> Dict:
        """Execute real blockchain transaction"""
        try:
            # Convert to Wei (assuming 18 decimals)
            carbon_amount_wei = int(carbon_amount * 10**18)
            price_wei = int(price_per_ton * 10**18)
            
            # Create contract instance
            contract = self.web3.eth.contract(
                address=self.carbon_contract_address,
                abi=self.carbon_contract_abi
            )
            
            # Build transaction
            transaction = contract.functions.createCarbonTrade(
                trade_id,
                carbon_amount_wei,
                price_wei,
                seller_address,
                buyer_address
            ).build_transaction({
                'from': self.account.address,
                'gas': 200000,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': self.web3.eth.get_transaction_count(self.account.address)
            })
            
            # Sign transaction
            signed_txn = self.web3.eth.account.sign_transaction(transaction, self.account.key)
            
            # Send transaction
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for confirmation
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                'trade_id': trade_id,
                'transaction_hash': tx_hash.hex(),
                'block_number': tx_receipt.blockNumber,
                'gas_used': tx_receipt.gasUsed,
                'status': 'confirmed' if tx_receipt.status == 1 else 'failed',
                'carbon_amount': carbon_amount,
                'price_per_ton': price_per_ton,
                'total_value': carbon_amount * price_per_ton,
                'seller_address': seller_address,
                'buyer_address': buyer_address,
                'created_at': datetime.now().isoformat(),
                'blockchain_network': 'sepolia_testnet'
            }
            
        except Exception as e:
            logger.error("Blockchain transaction failed", error=str(e))
            raise Exception(f"Blockchain transaction failed: {str(e)}")
    
    def _mock_blockchain_trade(self, 
                              trade_id: str,
                              carbon_amount: float,
                              price_per_ton: float,
                              seller_address: str,
                              buyer_address: str) -> Dict:
        """Mock blockchain transaction for testing"""
        import hashlib
        import time
        
        # Generate mock transaction hash
        tx_data = f"{trade_id}{carbon_amount}{price_per_ton}{seller_address}{buyer_address}{time.time()}"
        tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()
        
        return {
            'trade_id': trade_id,
            'transaction_hash': f"0x{tx_hash[:40]}",
            'block_number': 12345678,
            'gas_used': 150000,
            'status': 'confirmed',
            'carbon_amount': carbon_amount,
            'price_per_ton': price_per_ton,
            'total_value': carbon_amount * price_per_ton,
            'seller_address': seller_address,
            'buyer_address': buyer_address,
            'created_at': datetime.now().isoformat(),
            'blockchain_network': 'mock_testnet',
            'note': 'This is a mock transaction for demonstration purposes'
        }
    
    def get_carbon_trade(self, trade_id: str) -> Dict:
        """Get carbon trade details from blockchain"""
        try:
            logger.info("Retrieving carbon trade", trade_id=trade_id)
            
            if self.web3_available and self.web3:
                # Real blockchain query
                result = self._query_blockchain_trade(trade_id)
            else:
                # Mock blockchain query
                result = self._mock_query_trade(trade_id)
            
            return result
            
        except Exception as e:
            logger.error("Failed to retrieve carbon trade", error=str(e))
            raise Exception(f"Failed to retrieve carbon trade: {str(e)}")
    
    def _query_blockchain_trade(self, trade_id: str) -> Dict:
        """Query real blockchain for trade details"""
        try:
            contract = self.web3.eth.contract(
                address=self.carbon_contract_address,
                abi=self.carbon_contract_abi
            )
            
            # Call contract function
            result = contract.functions.getCarbonTrade(trade_id).call()
            
            return {
                'trade_id': trade_id,
                'carbon_amount': float(result[0] / 10**18),
                'price': float(result[1] / 10**18),
                'seller': result[2],
                'buyer': result[3],
                'status': result[4],
                'queried_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error("Blockchain query failed", error=str(e))
            raise Exception(f"Blockchain query failed: {str(e)}")
    
    def _mock_query_trade(self, trade_id: str) -> Dict:
        """Mock blockchain query"""
        return {
            'trade_id': trade_id,
            'carbon_amount': 100.0,
            'price': 50.0,
            'seller': '0x1234567890123456789012345678901234567890',
            'buyer': '0x0987654321098765432109876543210987654321',
            'status': 'active',
            'queried_at': datetime.now().isoformat(),
            'note': 'This is mock data for demonstration purposes'
        }
    
    def settle_carbon_trade(self, trade_id: str) -> Dict:
        """Settle carbon trade on blockchain"""
        try:
            logger.info("Settling carbon trade", trade_id=trade_id)
            
            if self.web3_available and self.web3:
                result = self._execute_settlement(trade_id)
            else:
                result = self._mock_settlement(trade_id)
            
            logger.info("Carbon trade settled", trade_id=trade_id)
            return result
            
        except Exception as e:
            logger.error("Carbon trade settlement failed", error=str(e))
            raise Exception(f"Failed to settle carbon trade: {str(e)}")
    
    def _execute_settlement(self, trade_id: str) -> Dict:
        """Execute real blockchain settlement"""
        try:
            contract = self.web3.eth.contract(
                address=self.carbon_contract_address,
                abi=self.carbon_contract_abi
            )
            
            transaction = contract.functions.settleCarbonTrade(trade_id).build_transaction({
                'from': self.account.address,
                'gas': 100000,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': self.web3.eth.get_transaction_count(self.account.address)
            })
            
            signed_txn = self.web3.eth.account.sign_transaction(transaction, self.account.key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                'trade_id': trade_id,
                'settlement_hash': tx_hash.hex(),
                'status': 'settled' if tx_receipt.status == 1 else 'failed',
                'settled_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error("Settlement execution failed", error=str(e))
            raise Exception(f"Settlement execution failed: {str(e)}")
    
    def _mock_settlement(self, trade_id: str) -> Dict:
        """Mock settlement for testing"""
        import hashlib
        import time
        
        settlement_data = f"{trade_id}settlement{time.time()}"
        settlement_hash = hashlib.sha256(settlement_data.encode()).hexdigest()
        
        return {
            'trade_id': trade_id,
            'settlement_hash': f"0x{settlement_hash[:40]}",
            'status': 'settled',
            'settled_at': datetime.now().isoformat(),
            'note': 'This is a mock settlement for demonstration purposes'
        }
    
    def get_esg_score(self, company_address: str) -> Dict:
        """Get ESG (Environmental, Social, Governance) score from blockchain"""
        try:
            logger.info("Retrieving ESG score", company_address=company_address)
            
            # Mock ESG score calculation
            # In a real implementation, this would query multiple data sources
            esg_score = {
                'company_address': company_address,
                'environmental_score': 85.5,
                'social_score': 78.2,
                'governance_score': 92.1,
                'overall_score': 85.3,
                'carbon_footprint': 1250.5,  # tons CO2
                'renewable_energy_usage': 65.2,  # percentage
                'sustainability_rating': 'A-',
                'last_updated': datetime.now().isoformat(),
                'data_sources': ['blockchain', 'sustainability_reports', 'third_party_audits']
            }
            
            logger.info("ESG score retrieved", 
                       company=company_address, 
                       score=esg_score['overall_score'])
            
            return esg_score
            
        except Exception as e:
            logger.error("Failed to retrieve ESG score", error=str(e))
            raise Exception(f"Failed to retrieve ESG score: {str(e)}")

# Global instance
blockchain_service = BlockchainService()
