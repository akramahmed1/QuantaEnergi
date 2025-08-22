"""
Blockchain Service for EnergyOpti-Pro.

Implements P2P energy trading, smart contracts, and decentralized settlement using Ethereum-compatible blockchains.
"""

import asyncio
import json
import hashlib
import time
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timezone, timedelta
import structlog
from dataclasses import dataclass, asdict
from enum import Enum
import secrets

# Blockchain integration
try:
    from web3 import Web3
    from eth_account import Account
    from eth_account.messages import encode_defunct
    BLOCKCHAIN_AVAILABLE = True
except ImportError:
    BLOCKCHAIN_AVAILABLE = False
    print("Web3 not available, using mock blockchain service")

logger = structlog.get_logger()

class TradeStatus(Enum):
    """P2P trade status."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    ESCROW_FUNDED = "escrow_funded"
    DELIVERED = "delivered"
    SETTLED = "settled"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"

class EnergyType(Enum):
    """Energy types for P2P trading."""
    SOLAR = "solar"
    WIND = "wind"
    HYDRO = "hydro"
    NUCLEAR = "nuclear"
    FOSSIL = "fossil"
    BATTERY = "battery"
    HYDROGEN = "hydrogen"

class SmartContractType(Enum):
    """Smart contract types."""
    P2P_TRADE = "p2p_trade"
    ESCROW = "escrow"
    SETTLEMENT = "settlement"
    REWARD = "reward"
    GOVERNANCE = "governance"

@dataclass
class P2PTrade:
    """P2P energy trade."""
    id: str
    seller_id: str
    buyer_id: str
    energy_type: EnergyType
    quantity: float
    unit: str
    price: float
    currency: str
    location: str
    delivery_date: datetime
    status: TradeStatus
    blockchain_tx_id: Optional[str] = None
    escrow_address: Optional[str] = None
    smart_contract_address: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = datetime.now(timezone.utc)

@dataclass
class SmartContract:
    """Smart contract information."""
    address: str
    type: SmartContractType
    abi: str
    bytecode: str
    deployed_at: datetime
    gas_used: int
    gas_price: int
    network: str
    status: str

@dataclass
class BlockchainTransaction:
    """Blockchain transaction."""
    hash: str
    from_address: str
    to_address: str
    value: float
    gas: int
    gas_price: int
    nonce: int
    status: str
    block_number: Optional[int] = None
    timestamp: datetime
    type: str
    metadata: Dict[str, Any]

class MockBlockchainService:
    """Mock blockchain service when Web3 is not available."""
    
    def __init__(self):
        self.trades: Dict[str, P2PTrade] = {}
        self.contracts: Dict[str, SmartContract] = {}
        self.transactions: Dict[str, BlockchainTransaction] = {}
        self.accounts: Dict[str, Dict[str, Any]] = {}
        self._initialize_mock_data()
    
    def _initialize_mock_data(self):
        """Initialize mock blockchain data."""
        # Mock accounts
        self.accounts = {
            "seller_001": {
                "address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
                "balance": 1000.0,
                "private_key": "mock_private_key_1"
            },
            "buyer_001": {
                "address": "0x8ba1f109551bD432803012645Hac136c22C177e9",
                "balance": 500.0,
                "private_key": "mock_private_key_2"
            }
        }
        
        # Mock smart contracts
        self.contracts = {
            "escrow_001": SmartContract(
                address="0x1234567890123456789012345678901234567890",
                type=SmartContractType.ESCROW,
                abi="mock_abi",
                bytecode="mock_bytecode",
                deployed_at=datetime.now(timezone.utc),
                gas_used=21000,
                gas_price=20,
                network="mock_ethereum",
                status="deployed"
            )
        }
    
    async def create_p2p_trade(self, trade_data: Dict[str, Any]) -> P2PTrade:
        """Create a new P2P trade."""
        trade_id = f"trade_{len(self.trades) + 1:06d}"
        
        trade = P2PTrade(
            id=trade_id,
            seller_id=trade_data["seller_id"],
            buyer_id=trade_data["buyer_id"],
            energy_type=EnergyType(trade_data["energy_type"]),
            quantity=trade_data["quantity"],
            unit=trade_data["unit"],
            price=trade_data["price"],
            currency=trade_data["currency"],
            location=trade_data["location"],
            delivery_date=datetime.fromisoformat(trade_data["delivery_date"]),
            status=TradeStatus.PENDING
        )
        
        self.trades[trade_id] = trade
        logger.info(f"Created P2P trade: {trade_id}")
        return trade
    
    async def confirm_trade(self, trade_id: str, buyer_signature: str) -> bool:
        """Confirm a P2P trade."""
        if trade_id not in self.trades:
            return False
        
        trade = self.trades[trade_id]
        trade.status = TradeStatus.CONFIRMED
        trade.updated_at = datetime.now(timezone.utc)
        
        # Generate mock blockchain transaction
        tx_hash = f"0x{secrets.token_hex(32)}"
        transaction = BlockchainTransaction(
            hash=tx_hash,
            from_address=self.accounts["buyer_001"]["address"],
            to_address=self.accounts["seller_001"]["address"],
            value=trade.price * trade.quantity,
            gas=21000,
            gas_price=20,
            nonce=1,
            status="confirmed",
            timestamp=datetime.now(timezone.utc),
            type="trade_confirmation",
            metadata={"trade_id": trade_id}
        )
        
        self.transactions[tx_hash] = transaction
        trade.blockchain_tx_id = tx_hash
        
        logger.info(f"Confirmed P2P trade: {trade_id}")
        return True
    
    async def fund_escrow(self, trade_id: str, amount: float) -> bool:
        """Fund escrow for a trade."""
        if trade_id not in self.trades:
            return False
        
        trade = self.trades[trade_id]
        trade.status = TradeStatus.ESCROW_FUNDED
        trade.updated_at = datetime.now(timezone.utc)
        
        # Generate mock escrow transaction
        tx_hash = f"0x{secrets.token_hex(32)}"
        transaction = BlockchainTransaction(
            hash=tx_hash,
            from_address=self.accounts["buyer_001"]["address"],
            to_address=self.contracts["escrow_001"].address,
            value=amount,
            gas=50000,
            gas_price=20,
            nonce=2,
            status="confirmed",
            timestamp=datetime.now(timezone.utc),
            type="escrow_funding",
            metadata={"trade_id": trade_id, "amount": amount}
        )
        
        self.transactions[tx_hash] = transaction
        
        logger.info(f"Funded escrow for trade: {trade_id}")
        return True
    
    async def deliver_energy(self, trade_id: str, delivery_proof: str) -> bool:
        """Mark energy as delivered."""
        if trade_id not in self.trades:
            return False
        
        trade = self.trades[trade_id]
        trade.status = TradeStatus.DELIVERED
        trade.updated_at = datetime.now(timezone.utc)
        
        logger.info(f"Energy delivered for trade: {trade_id}")
        return True
    
    async def settle_trade(self, trade_id: str) -> bool:
        """Settle a completed trade."""
        if trade_id not in self.trades:
            return False
        
        trade = self.trades[trade_id]
        trade.status = TradeStatus.SETTLED
        trade.updated_at = datetime.now(timezone.utc)
        
        # Generate mock settlement transaction
        tx_hash = f"0x{secrets.token_hex(32)}"
        transaction = BlockchainTransaction(
            hash=tx_hash,
            from_address=self.contracts["escrow_001"].address,
            to_address=self.accounts["seller_001"]["address"],
            value=trade.price * trade.quantity,
            gas=30000,
            gas_price=20,
            nonce=3,
            status="confirmed",
            timestamp=datetime.now(timezone.utc),
            type="trade_settlement",
            metadata={"trade_id": trade_id}
        )
        
        self.transactions[tx_hash] = transaction
        
        logger.info(f"Settled trade: {trade_id}")
        return True
    
    async def get_trade_status(self, trade_id: str) -> Optional[TradeStatus]:
        """Get trade status."""
        if trade_id in self.trades:
            return self.trades[trade_id].status
        return None
    
    async def get_trade_history(self, user_id: str) -> List[P2PTrade]:
        """Get trade history for a user."""
        return [
            trade for trade in self.trades.values()
            if trade.seller_id == user_id or trade.buyer_id == user_id
        ]
    
    async def get_blockchain_transactions(self, address: str) -> List[BlockchainTransaction]:
        """Get blockchain transactions for an address."""
        return [
            tx for tx in self.transactions.values()
            if tx.from_address == address or tx.to_address == address
        ]

class BlockchainService:
    """Real blockchain service using Web3."""
    
    def __init__(self, rpc_url: str, private_key: str):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = Account.from_key(private_key)
        self.contracts: Dict[str, Any] = {}
        self.trades: Dict[str, P2PTrade] = {}
        
        # Load smart contract ABIs
        self._load_contract_abis()
    
    def _load_contract_abis(self):
        """Load smart contract ABIs."""
        # In real implementation, load from JSON files
        self.escrow_abi = []  # Load from escrow.json
        self.trade_abi = []   # Load from trade.json
    
    async def create_p2p_trade(self, trade_data: Dict[str, Any]) -> P2PTrade:
        """Create a new P2P trade on blockchain."""
        try:
            # Deploy smart contract for the trade
            contract = self.w3.eth.contract(
                abi=self.trade_abi,
                bytecode=self.trade_bytecode
            )
            
            # Build transaction
            construct_txn = contract.constructor(
                trade_data["seller_id"],
                trade_data["buyer_id"],
                trade_data["energy_type"],
                int(trade_data["quantity"] * 1e18),  # Convert to wei
                int(trade_data["price"] * 1e18)
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 2000000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(
                construct_txn, self.account.key
            )
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for transaction receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # Create trade record
            trade = P2PTrade(
                id=f"trade_{len(self.trades) + 1:06d}",
                seller_id=trade_data["seller_id"],
                buyer_id=trade_data["buyer_id"],
                energy_type=EnergyType(trade_data["energy_type"]),
                quantity=trade_data["quantity"],
                unit=trade_data["unit"],
                price=trade_data["price"],
                currency=trade_data["currency"],
                location=trade_data["location"],
                delivery_date=datetime.fromisoformat(trade_data["delivery_date"]),
                status=TradeStatus.PENDING,
                smart_contract_address=tx_receipt.contractAddress,
                blockchain_tx_id=tx_hash.hex()
            )
            
            self.trades[trade.id] = trade
            logger.info(f"Created P2P trade on blockchain: {trade.id}")
            return trade
            
        except Exception as e:
            logger.error(f"Failed to create P2P trade: {e}")
            raise
    
    async def confirm_trade(self, trade_id: str, buyer_signature: str) -> bool:
        """Confirm a P2P trade on blockchain."""
        try:
            trade = self.trades.get(trade_id)
            if not trade or not trade.smart_contract_address:
                return False
            
            # Call smart contract to confirm trade
            contract = self.w3.eth.contract(
                address=trade.smart_contract_address,
                abi=self.trade_abi
            )
            
            # Build transaction
            txn = contract.functions.confirmTrade().build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(txn, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for confirmation
            self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # Update trade status
            trade.status = TradeStatus.CONFIRMED
            trade.updated_at = datetime.now(timezone.utc)
            
            logger.info(f"Confirmed P2P trade on blockchain: {trade_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to confirm P2P trade: {e}")
            return False
    
    async def fund_escrow(self, trade_id: str, amount: float) -> bool:
        """Fund escrow for a trade."""
        try:
            trade = self.trades.get(trade_id)
            if not trade:
                return False
            
            # Deploy escrow contract
            escrow_contract = self.w3.eth.contract(
                abi=self.escrow_abi,
                bytecode=self.escrow_bytecode
            )
            
            # Build deployment transaction
            construct_txn = escrow_contract.constructor(
                trade.smart_contract_address,
                int(amount * 1e18)
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 1500000,
                'gasPrice': self.w3.eth.gas_price,
                'value': int(amount * 1e18)
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(
                construct_txn, self.account.key
            )
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for deployment
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # Update trade
            trade.escrow_address = tx_receipt.contractAddress
            trade.status = TradeStatus.ESCROW_FUNDED
            trade.updated_at = datetime.now(timezone.utc)
            
            logger.info(f"Funded escrow for trade: {trade_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to fund escrow: {e}")
            return False
    
    async def get_trade_status(self, trade_id: str) -> Optional[TradeStatus]:
        """Get trade status from blockchain."""
        try:
            trade = self.trades.get(trade_id)
            if not trade or not trade.smart_contract_address:
                return None
            
            # Query smart contract
            contract = self.w3.eth.contract(
                address=trade.smart_contract_address,
                abi=self.trade_abi
            )
            
            status = contract.functions.getStatus().call()
            return TradeStatus(status)
            
        except Exception as e:
            logger.error(f"Failed to get trade status: {e}")
            return None
    
    async def get_blockchain_transactions(self, address: str) -> List[BlockchainTransaction]:
        """Get blockchain transactions for an address."""
        try:
            # Get transaction count
            nonce = self.w3.eth.get_transaction_count(address)
            transactions = []
            
            # Get recent transactions (simplified)
            for i in range(max(0, nonce - 10), nonce):
                try:
                    tx = self.w3.eth.get_transaction_by_index(i)
                    if tx and (tx['from'] == address or tx['to'] == address):
                        transaction = BlockchainTransaction(
                            hash=tx['hash'].hex(),
                            from_address=tx['from'],
                            to_address=tx['to'] or '',
                            value=self.w3.from_wei(tx['value'], 'ether'),
                            gas=tx['gas'],
                            gas_price=self.w3.from_wei(tx['gasPrice'], 'gwei'),
                            nonce=tx['nonce'],
                            status='confirmed',
                            timestamp=datetime.fromtimestamp(
                                self.w3.eth.get_block(tx['blockNumber'])['timestamp']
                            ),
                            type='transfer',
                            metadata={}
                        )
                        transactions.append(transaction)
                except Exception as e:
                    logger.warning(f"Failed to get transaction {i}: {e}")
                    continue
            
            return transactions
            
        except Exception as e:
            logger.error(f"Failed to get blockchain transactions: {e}")
            return []

# Factory function to get appropriate service
def get_blockchain_service(rpc_url: str = None, private_key: str = None) -> Union[BlockchainService, MockBlockchainService]:
    """Get blockchain service instance."""
    if BLOCKCHAIN_AVAILABLE and rpc_url and private_key:
        return BlockchainService(rpc_url, private_key)
    else:
        return MockBlockchainService()
