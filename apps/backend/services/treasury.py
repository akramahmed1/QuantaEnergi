"""
Treasury Management Service for QuantaEnergi
Advanced treasury operations, cash management, and financial controls
"""

from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
import json
import uuid
import logging
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP
import asyncio
import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TreasuryOperation(Enum):
    """Treasury operations"""
    CASH_DEPOSIT = "cash_deposit"
    CASH_WITHDRAWAL = "cash_withdrawal"
    INVESTMENT_PURCHASE = "investment_purchase"
    INVESTMENT_SALE = "investment_sale"
    LOAN_DISBURSEMENT = "loan_disbursement"
    LOAN_REPAYMENT = "loan_repayment"
    INTEREST_PAYMENT = "interest_payment"
    DIVIDEND_PAYMENT = "dividend_payment"
    FEE_COLLECTION = "fee_collection"
    EXPENSE_PAYMENT = "expense_payment"

class TreasuryStatus(Enum):
    """Treasury status"""
    PENDING = "pending"
    APPROVED = "approved"
    EXECUTED = "executed"
    CANCELLED = "cancelled"
    FAILED = "failed"

class InvestmentType(Enum):
    """Investment types"""
    MONEY_MARKET = "money_market"
    BOND = "bond"
    EQUITY = "equity"
    COMMODITY = "commodity"
    CURRENCY = "currency"
    CRYPTOCURRENCY = "cryptocurrency"
    REAL_ESTATE = "real_estate"
    ALTERNATIVE = "alternative"

@dataclass
class TreasuryAccount:
    """Treasury account structure"""
    account_id: str
    account_name: str
    account_type: str  # cash, investment, loan, etc.
    currency: str
    balance: Decimal
    available_balance: Decimal
    pending_balance: Decimal
    interest_rate: Decimal = Decimal("0.0")
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class TreasuryTransaction:
    """Treasury transaction structure"""
    transaction_id: str
    operation: TreasuryOperation
    from_account: str
    to_account: str
    amount: Decimal
    currency: str
    description: str
    status: TreasuryStatus
    approval_required: bool = True
    approved_by: str = ""
    approved_at: datetime = None
    executed_at: datetime = None
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Investment:
    """Investment structure"""
    investment_id: str
    investment_type: InvestmentType
    name: str
    symbol: str
    quantity: Decimal
    purchase_price: Decimal
    current_price: Decimal
    market_value: Decimal
    unrealized_pnl: Decimal
    currency: str
    purchase_date: datetime
    maturity_date: datetime = None
    coupon_rate: Decimal = Decimal("0.0")
    dividend_yield: Decimal = Decimal("0.0")

@dataclass
class CashFlowForecast:
    """Cash flow forecast structure"""
    forecast_id: str
    forecast_date: datetime
    forecast_period: str  # daily, weekly, monthly, quarterly, yearly
    projected_inflows: Decimal
    projected_outflows: Decimal
    net_cash_flow: Decimal
    confidence_level: float
    assumptions: Dict[str, Any] = field(default_factory=dict)

class AdvancedTreasuryService:
    """
    Advanced treasury management service with cash management and investment tracking
    """
    
    def __init__(self):
        self.accounts = {}
        self.transactions = {}
        self.investments = {}
        self.cash_flow_forecasts = {}
        self.treasury_policies = {}
        self.risk_limits = {}
        self.approval_workflows = {}
        self.reconciliation_records = {}
        
    def create_treasury_account(self, 
                               account_name: str,
                               account_type: str,
                               currency: str,
                               initial_balance: Decimal = Decimal("0.0")) -> Dict[str, Any]:
        """Create new treasury account"""
        try:
            account_id = self._generate_account_id(account_name)
            
            account = TreasuryAccount(
                account_id=account_id,
                account_name=account_name,
                account_type=account_type,
                currency=currency,
                balance=initial_balance,
                available_balance=initial_balance,
                pending_balance=Decimal("0.0")
            )
            
            self.accounts[account_id] = account
            
            # Create initial transaction record
            initial_transaction = TreasuryTransaction(
                transaction_id=self._generate_transaction_id(),
                operation=TreasuryOperation.CASH_DEPOSIT,
                from_account="external",
                to_account=account_id,
                amount=initial_balance,
                currency=currency,
                description=f"Initial balance for {account_name}",
                status=TreasuryStatus.EXECUTED,
                approval_required=False,
                executed_at=datetime.now()
            )
            
            self.transactions[initial_transaction.transaction_id] = initial_transaction
            
            return {
                "status": "success",
                "account_id": account_id,
                "account_name": account_name,
                "account_type": account_type,
                "currency": currency,
                "balance": float(initial_balance),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Treasury account creation error: {e}")
            return {"status": "error", "message": str(e)}
    
    def _generate_account_id(self, account_name: str) -> str:
        """Generate unique account ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name_hash = hashlib.md5(account_name.encode()).hexdigest()[:8]
        return f"treasury_{name_hash}_{timestamp}"
    
    def _generate_transaction_id(self) -> str:
        """Generate unique transaction ID"""
        return f"txn_{uuid.uuid4().hex[:16]}"
    
    def execute_treasury_transaction(self,
                                   operation: TreasuryOperation,
                                   from_account: str,
                                   to_account: str,
                                   amount: Decimal,
                                   currency: str,
                                   description: str,
                                   approval_required: bool = True) -> Dict[str, Any]:
        """Execute treasury transaction"""
        try:
            # Validate accounts
            if from_account != "external" and from_account not in self.accounts:
                return {"status": "error", "message": f"From account {from_account} not found"}
            
            if to_account != "external" and to_account not in self.accounts:
                return {"status": "error", "message": f"To account {to_account} not found"}
            
            # Check available balance for withdrawals
            if operation in [TreasuryOperation.CASH_WITHDRAWAL, TreasuryOperation.EXPENSE_PAYMENT]:
                if from_account in self.accounts:
                    account = self.accounts[from_account]
                    if account.available_balance < amount:
                        return {"status": "error", "message": "Insufficient available balance"}
            
            # Create transaction
            transaction = TreasuryTransaction(
                transaction_id=self._generate_transaction_id(),
                operation=operation,
                from_account=from_account,
                to_account=to_account,
                amount=amount,
                currency=currency,
                description=description,
                status=TreasuryStatus.PENDING,
                approval_required=approval_required
            )
            
            self.transactions[transaction.transaction_id] = transaction
            
            # Process transaction based on approval requirement
            if approval_required:
                # Add to approval workflow
                self._add_to_approval_workflow(transaction)
                return {
                    "status": "pending_approval",
                    "transaction_id": transaction.transaction_id,
                    "message": "Transaction pending approval",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # Execute immediately
                execution_result = self._execute_transaction(transaction)
                return execution_result
                
        except Exception as e:
            logger.error(f"Treasury transaction execution error: {e}")
            return {"status": "error", "message": str(e)}
    
    def _add_to_approval_workflow(self, transaction: TreasuryTransaction):
        """Add transaction to approval workflow"""
        try:
            workflow_id = f"workflow_{transaction.transaction_id}"
            
            self.approval_workflows[workflow_id] = {
                "transaction_id": transaction.transaction_id,
                "operation": transaction.operation.value,
                "amount": float(transaction.amount),
                "currency": transaction.currency,
                "from_account": transaction.from_account,
                "to_account": transaction.to_account,
                "description": transaction.description,
                "status": "pending",
                "approval_level": self._get_approval_level(transaction),
                "created_at": datetime.now().isoformat(),
                "approvals": [],
                "rejections": []
            }
            
        except Exception as e:
            logger.error(f"Approval workflow addition error: {e}")
    
    def _get_approval_level(self, transaction: TreasuryTransaction) -> str:
        """Get required approval level for transaction"""
        try:
            amount = float(transaction.amount)
            
            if amount <= 10000:
                return "manager"
            elif amount <= 100000:
                return "director"
            elif amount <= 1000000:
                return "vp"
            else:
                return "cfo"
                
        except Exception as e:
            logger.error(f"Approval level determination error: {e}")
            return "manager"
    
    def approve_transaction(self, 
                           transaction_id: str, 
                           approver: str,
                           approval_level: str) -> Dict[str, Any]:
        """Approve treasury transaction"""
        try:
            if transaction_id not in self.transactions:
                return {"status": "error", "message": "Transaction not found"}
            
            transaction = self.transactions[transaction_id]
            
            if transaction.status != TreasuryStatus.PENDING:
                return {"status": "error", "message": "Transaction is not pending"}
            
            # Update transaction
            transaction.status = TreasuryStatus.APPROVED
            transaction.approved_by = approver
            transaction.approved_at = datetime.now()
            
            # Update approval workflow
            workflow_id = f"workflow_{transaction_id}"
            if workflow_id in self.approval_workflows:
                workflow = self.approval_workflows[workflow_id]
                workflow["approvals"].append({
                    "approver": approver,
                    "approval_level": approval_level,
                    "approved_at": datetime.now().isoformat()
                })
                workflow["status"] = "approved"
            
            # Execute transaction
            execution_result = self._execute_transaction(transaction)
            
            return {
                "status": "success",
                "transaction_id": transaction_id,
                "approved_by": approver,
                "execution_result": execution_result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Transaction approval error: {e}")
            return {"status": "error", "message": str(e)}
    
    def _execute_transaction(self, transaction: TreasuryTransaction) -> Dict[str, Any]:
        """Execute treasury transaction"""
        try:
            # Update account balances
            if transaction.from_account != "external":
                from_account = self.accounts[transaction.from_account]
                from_account.balance -= transaction.amount
                from_account.available_balance -= transaction.amount
                from_account.updated_at = datetime.now()
            
            if transaction.to_account != "external":
                to_account = self.accounts[transaction.to_account]
                to_account.balance += transaction.amount
                to_account.available_balance += transaction.amount
                to_account.updated_at = datetime.now()
            
            # Update transaction status
            transaction.status = TreasuryStatus.EXECUTED
            transaction.executed_at = datetime.now()
            
            return {
                "status": "executed",
                "transaction_id": transaction.transaction_id,
                "executed_at": transaction.executed_at.isoformat(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Transaction execution error: {e}")
            transaction.status = TreasuryStatus.FAILED
            return {"status": "error", "message": str(e)}
    
    def add_investment(self,
                      investment_type: InvestmentType,
                      name: str,
                      symbol: str,
                      quantity: Decimal,
                      purchase_price: Decimal,
                      currency: str,
                      purchase_date: datetime,
                      maturity_date: datetime = None,
                      coupon_rate: Decimal = Decimal("0.0")) -> Dict[str, Any]:
        """Add investment to treasury portfolio"""
        try:
            investment_id = self._generate_investment_id(symbol)
            
            investment = Investment(
                investment_id=investment_id,
                investment_type=investment_type,
                name=name,
                symbol=symbol,
                quantity=quantity,
                purchase_price=purchase_price,
                current_price=purchase_price,  # Initially same as purchase price
                market_value=quantity * purchase_price,
                unrealized_pnl=Decimal("0.0"),
                currency=currency,
                purchase_date=purchase_date,
                maturity_date=maturity_date,
                coupon_rate=coupon_rate
            )
            
            self.investments[investment_id] = investment
            
            return {
                "status": "success",
                "investment_id": investment_id,
                "name": name,
                "symbol": symbol,
                "quantity": float(quantity),
                "purchase_price": float(purchase_price),
                "market_value": float(investment.market_value),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Investment addition error: {e}")
            return {"status": "error", "message": str(e)}
    
    def _generate_investment_id(self, symbol: str) -> str:
        """Generate unique investment ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"inv_{symbol}_{timestamp}"
    
    def update_investment_prices(self, price_updates: Dict[str, Decimal]) -> Dict[str, Any]:
        """Update investment prices"""
        try:
            updated_investments = []
            
            for investment_id, investment in self.investments.items():
                if investment.symbol in price_updates:
                    new_price = price_updates[investment.symbol]
                    old_price = investment.current_price
                    
                    # Update investment
                    investment.current_price = new_price
                    investment.market_value = investment.quantity * new_price
                    investment.unrealized_pnl = investment.quantity * (new_price - investment.purchase_price)
                    
                    updated_investments.append({
                        "investment_id": investment_id,
                        "symbol": investment.symbol,
                        "old_price": float(old_price),
                        "new_price": float(new_price),
                        "market_value": float(investment.market_value),
                        "unrealized_pnl": float(investment.unrealized_pnl)
                    })
            
            return {
                "status": "success",
                "updated_investments": updated_investments,
                "total_updated": len(updated_investments),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Investment price update error: {e}")
            return {"status": "error", "message": str(e)}
    
    def calculate_cash_flow_forecast(self,
                                   forecast_period: str,
                                   days_ahead: int = 30) -> Dict[str, Any]:
        """Calculate cash flow forecast"""
        try:
            forecast_id = f"forecast_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Get historical transaction data
            historical_data = self._get_historical_transaction_data(days_ahead)
            
            # Calculate projected inflows and outflows
            projected_inflows = self._calculate_projected_inflows(historical_data, forecast_period)
            projected_outflows = self._calculate_projected_outflows(historical_data, forecast_period)
            
            # Calculate net cash flow
            net_cash_flow = projected_inflows - projected_outflows
            
            # Calculate confidence level
            confidence_level = self._calculate_confidence_level(historical_data)
            
            # Create forecast
            forecast = CashFlowForecast(
                forecast_id=forecast_id,
                forecast_date=datetime.now(),
                forecast_period=forecast_period,
                projected_inflows=projected_inflows,
                projected_outflows=projected_outflows,
                net_cash_flow=net_cash_flow,
                confidence_level=confidence_level,
                assumptions={
                    "historical_period": days_ahead,
                    "trend_analysis": True,
                    "seasonality_adjustment": True
                }
            )
            
            self.cash_flow_forecasts[forecast_id] = forecast
            
            return {
                "status": "success",
                "forecast_id": forecast_id,
                "forecast_period": forecast_period,
                "projected_inflows": float(projected_inflows),
                "projected_outflows": float(projected_outflows),
                "net_cash_flow": float(net_cash_flow),
                "confidence_level": confidence_level,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Cash flow forecast calculation error: {e}")
            return {"status": "error", "message": str(e)}
    
    def _get_historical_transaction_data(self, days_ahead: int) -> List[Dict[str, Any]]:
        """Get historical transaction data"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_ahead)
            
            historical_data = []
            
            for transaction in self.transactions.values():
                if start_date <= transaction.created_at <= end_date:
                    historical_data.append({
                        "operation": transaction.operation.value,
                        "amount": float(transaction.amount),
                        "currency": transaction.currency,
                        "date": transaction.created_at.date()
                    })
            
            return historical_data
            
        except Exception as e:
            logger.error(f"Historical data retrieval error: {e}")
            return []
    
    def _calculate_projected_inflows(self, historical_data: List[Dict[str, Any]], forecast_period: str) -> Decimal:
        """Calculate projected inflows"""
        try:
            inflow_operations = [
                TreasuryOperation.CASH_DEPOSIT.value,
                TreasuryOperation.INVESTMENT_SALE.value,
                TreasuryOperation.LOAN_DISBURSEMENT.value,
                TreasuryOperation.INTEREST_PAYMENT.value,
                TreasuryOperation.DIVIDEND_PAYMENT.value,
                TreasuryOperation.FEE_COLLECTION.value
            ]
            
            total_inflows = sum(
                data["amount"] for data in historical_data
                if data["operation"] in inflow_operations
            )
            
            # Apply forecast period multiplier
            period_multipliers = {
                "daily": 1,
                "weekly": 7,
                "monthly": 30,
                "quarterly": 90,
                "yearly": 365
            }
            
            multiplier = period_multipliers.get(forecast_period, 1)
            projected_inflows = Decimal(str(total_inflows)) * Decimal(str(multiplier))
            
            return projected_inflows
            
        except Exception as e:
            logger.error(f"Projected inflows calculation error: {e}")
            return Decimal("0.0")
    
    def _calculate_projected_outflows(self, historical_data: List[Dict[str, Any]], forecast_period: str) -> Decimal:
        """Calculate projected outflows"""
        try:
            outflow_operations = [
                TreasuryOperation.CASH_WITHDRAWAL.value,
                TreasuryOperation.INVESTMENT_PURCHASE.value,
                TreasuryOperation.LOAN_REPAYMENT.value,
                TreasuryOperation.EXPENSE_PAYMENT.value
            ]
            
            total_outflows = sum(
                data["amount"] for data in historical_data
                if data["operation"] in outflow_operations
            )
            
            # Apply forecast period multiplier
            period_multipliers = {
                "daily": 1,
                "weekly": 7,
                "monthly": 30,
                "quarterly": 90,
                "yearly": 365
            }
            
            multiplier = period_multipliers.get(forecast_period, 1)
            projected_outflows = Decimal(str(total_outflows)) * Decimal(str(multiplier))
            
            return projected_outflows
            
        except Exception as e:
            logger.error(f"Projected outflows calculation error: {e}")
            return Decimal("0.0")
    
    def _calculate_confidence_level(self, historical_data: List[Dict[str, Any]]) -> float:
        """Calculate confidence level for forecast"""
        try:
            if not historical_data:
                return 0.5
            
            # Calculate variance in historical data
            amounts = [data["amount"] for data in historical_data]
            if len(amounts) < 2:
                return 0.5
            
            mean_amount = np.mean(amounts)
            variance = np.var(amounts)
            
            # Convert variance to confidence level (0-1)
            confidence = max(0.1, min(0.9, 1 - (variance / (mean_amount ** 2))))
            
            return round(confidence, 2)
            
        except Exception as e:
            logger.error(f"Confidence level calculation error: {e}")
            return 0.5
    
    def get_treasury_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive treasury dashboard"""
        try:
            # Calculate total cash balance
            total_cash_balance = sum(
                account.balance for account in self.accounts.values()
                if account.account_type == "cash"
            )
            
            # Calculate total investment value
            total_investment_value = sum(
                investment.market_value for investment in self.investments.values()
            )
            
            # Calculate total unrealized P&L
            total_unrealized_pnl = sum(
                investment.unrealized_pnl for investment in self.investments.values()
            )
            
            # Get recent transactions
            recent_transactions = sorted(
                self.transactions.values(),
                key=lambda x: x.created_at,
                reverse=True
            )[:10]
            
            # Get pending approvals
            pending_approvals = [
                workflow for workflow in self.approval_workflows.values()
                if workflow["status"] == "pending"
            ]
            
            # Get cash flow forecast
            latest_forecast = None
            if self.cash_flow_forecasts:
                latest_forecast = max(
                    self.cash_flow_forecasts.values(),
                    key=lambda x: x.forecast_date
                )
            
            return {
                "status": "success",
                "dashboard": {
                    "total_cash_balance": float(total_cash_balance),
                    "total_investment_value": float(total_investment_value),
                    "total_unrealized_pnl": float(total_unrealized_pnl),
                    "total_accounts": len(self.accounts),
                    "total_investments": len(self.investments),
                    "pending_approvals": len(pending_approvals),
                    "recent_transactions": [
                        {
                            "transaction_id": txn.transaction_id,
                            "operation": txn.operation.value,
                            "amount": float(txn.amount),
                            "currency": txn.currency,
                            "status": txn.status.value,
                            "created_at": txn.created_at.isoformat()
                        }
                        for txn in recent_transactions
                    ],
                    "pending_approvals": [
                        {
                            "transaction_id": workflow["transaction_id"],
                            "operation": workflow["operation"],
                            "amount": workflow["amount"],
                            "currency": workflow["currency"],
                            "approval_level": workflow["approval_level"]
                        }
                        for workflow in pending_approvals
                    ],
                    "latest_forecast": {
                        "forecast_id": latest_forecast.forecast_id,
                        "projected_inflows": float(latest_forecast.projected_inflows),
                        "projected_outflows": float(latest_forecast.projected_outflows),
                        "net_cash_flow": float(latest_forecast.net_cash_flow),
                        "confidence_level": latest_forecast.confidence_level
                    } if latest_forecast else None
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Treasury dashboard retrieval error: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_treasury_statistics(self) -> Dict[str, Any]:
        """Get treasury service statistics"""
        try:
            # Calculate transaction statistics
            total_transactions = len(self.transactions)
            executed_transactions = sum(
                1 for txn in self.transactions.values()
                if txn.status == TreasuryStatus.EXECUTED
            )
            
            # Calculate transaction volume by operation
            operation_volumes = {}
            for txn in self.transactions.values():
                operation = txn.operation.value
                if operation not in operation_volumes:
                    operation_volumes[operation] = 0
                operation_volumes[operation] += float(txn.amount)
            
            # Calculate investment statistics
            total_investments = len(self.investments)
            investment_types = {}
            for investment in self.investments.values():
                inv_type = investment.investment_type.value
                if inv_type not in investment_types:
                    investment_types[inv_type] = 0
                investment_types[inv_type] += 1
            
            return {
                "status": "success",
                "statistics": {
                    "total_accounts": len(self.accounts),
                    "total_transactions": total_transactions,
                    "executed_transactions": executed_transactions,
                    "transaction_success_rate": round(executed_transactions / total_transactions * 100, 2) if total_transactions > 0 else 0,
                    "total_investments": total_investments,
                    "operation_volumes": operation_volumes,
                    "investment_types": investment_types,
                    "total_forecasts": len(self.cash_flow_forecasts),
                    "pending_approvals": len(self.approval_workflows)
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Statistics retrieval error: {e}")
            return {"status": "error", "message": str(e)}
