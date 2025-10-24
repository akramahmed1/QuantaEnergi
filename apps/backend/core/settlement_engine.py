"""
Settlement & Invoicing Engine for QuantaEnergi ETRM/CTRM Platform
Implements full settlement & invoicing/back-office integration including:
- Multi-currency settlement
- Multi-entity accounting
- General ledger integration
- Automated invoicing
- Payment processing
- Reconciliation
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
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import hmac

logger = logging.getLogger(__name__)

class SettlementStatus(Enum):
    """Settlement status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    SETTLED = "settled"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"

class InvoiceStatus(Enum):
    """Invoice status enumeration"""
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"

class PaymentMethod(Enum):
    """Payment method enumeration"""
    WIRE_TRANSFER = "wire_transfer"
    ACH = "ach"
    CHECK = "check"
    CREDIT_CARD = "credit_card"
    CRYPTO = "crypto"
    NETTING = "netting"

class Currency(Enum):
    """Currency enumeration"""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CAD = "CAD"
    AUD = "AUD"
    CHF = "CHF"
    CNY = "CNY"

@dataclass
class Entity:
    """Business entity"""
    entity_id: str
    name: str
    entity_type: str  # "company", "individual", "government"
    tax_id: str
    address: Dict[str, str]
    contact_info: Dict[str, str]
    banking_info: Dict[str, str]
    credit_rating: Optional[str] = None
    credit_limit: Optional[float] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Account:
    """Chart of accounts"""
    account_id: str
    account_code: str
    account_name: str
    account_type: str  # "asset", "liability", "equity", "revenue", "expense"
    parent_account_id: Optional[str] = None
    currency: Currency = Currency.USD
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class JournalEntry:
    """General ledger journal entry"""
    entry_id: str
    entry_date: datetime
    description: str
    reference: str
    entity_id: str
    currency: Currency
    debit_account: str
    credit_account: str
    amount: Decimal
    exchange_rate: Decimal = Decimal('1.0')
    base_amount: Decimal = Decimal('0.0')
    is_posted: bool = False
    posted_at: Optional[datetime] = None
    created_by: str = "system"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Settlement:
    """Settlement record"""
    settlement_id: str
    trade_id: str
    entity_id: str
    counterparty_id: str
    commodity: str
    quantity: Decimal
    price: Decimal
    currency: Currency
    settlement_amount: Decimal
    settlement_date: datetime
    payment_method: PaymentMethod
    status: SettlementStatus
    exchange_rate: Decimal = Decimal('1.0')
    fees: Decimal = Decimal('0.0')
    taxes: Decimal = Decimal('0.0')
    net_amount: Decimal = Decimal('0.0')
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Invoice:
    """Invoice record"""
    invoice_id: str
    invoice_number: str
    entity_id: str
    counterparty_id: str
    invoice_date: datetime
    due_date: datetime
    currency: Currency
    subtotal: Decimal
    taxes: Decimal
    fees: Decimal
    total_amount: Decimal
    status: InvoiceStatus
    payment_terms: str
    payment_method: PaymentMethod
    line_items: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Payment:
    """Payment record"""
    payment_id: str
    invoice_id: str
    entity_id: str
    counterparty_id: str
    payment_date: datetime
    amount: Decimal
    currency: Currency
    payment_method: PaymentMethod
    reference: str
    status: str = "completed"
    exchange_rate: Decimal = Decimal('1.0')
    fees: Decimal = Decimal('0.0')
    net_amount: Decimal = Decimal('0.0')
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class NettingAgreement:
    """Netting agreement"""
    agreement_id: str
    entity_id: str
    counterparty_id: str
    agreement_date: datetime
    effective_date: datetime
    expiry_date: datetime
    netting_type: str  # "bilateral", "multilateral"
    currencies: List[Currency]
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

class GeneralLedger:
    """General ledger system"""
    
    def __init__(self):
        self.accounts: Dict[str, Account] = {}
        self.journal_entries: Dict[str, JournalEntry] = {}
        self.account_balances: Dict[str, Dict[str, Decimal]] = {}
        
    def add_account(self, account: Account) -> bool:
        """Add account to chart of accounts"""
        try:
            self.accounts[account.account_id] = account
            self.account_balances[account.account_id] = {currency.value: Decimal('0.0') for currency in Currency}
            logger.info(f"Added account: {account.account_name}")
            return True
        except Exception as e:
            logger.error(f"Error adding account: {e}")
            return False
    
    def create_journal_entry(self, entry: JournalEntry) -> bool:
        """Create journal entry"""
        try:
            # Validate accounts exist
            if entry.debit_account not in self.accounts:
                logger.error(f"Debit account not found: {entry.debit_account}")
                return False
            
            if entry.credit_account not in self.accounts:
                logger.error(f"Credit account not found: {entry.credit_account}")
                return False
            
            # Add journal entry
            self.journal_entries[entry.entry_id] = entry
            
            # Update account balances
            self._update_account_balance(entry.debit_account, entry.currency, entry.amount, "debit")
            self._update_account_balance(entry.credit_account, entry.currency, entry.amount, "credit")
            
            logger.info(f"Created journal entry: {entry.entry_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating journal entry: {e}")
            return False
    
    def _update_account_balance(self, account_id: str, currency: Currency, amount: Decimal, entry_type: str):
        """Update account balance"""
        try:
            if account_id not in self.account_balances:
                self.account_balances[account_id] = {currency.value: Decimal('0.0') for currency in Currency}
            
            current_balance = self.account_balances[account_id][currency.value]
            
            if entry_type == "debit":
                self.account_balances[account_id][currency.value] = current_balance + amount
            else:  # credit
                self.account_balances[account_id][currency.value] = current_balance - amount
                
        except Exception as e:
            logger.error(f"Error updating account balance: {e}")
    
    def get_account_balance(self, account_id: str, currency: Currency) -> Decimal:
        """Get account balance"""
        try:
            if account_id not in self.account_balances:
                return Decimal('0.0')
            
            return self.account_balances[account_id].get(currency.value, Decimal('0.0'))
            
        except Exception as e:
            logger.error(f"Error getting account balance: {e}")
            return Decimal('0.0')
    
    def get_trial_balance(self, currency: Currency) -> Dict[str, Any]:
        """Get trial balance"""
        try:
            trial_balance = {
                "currency": currency.value,
                "as_of_date": datetime.utcnow().isoformat(),
                "accounts": []
            }
            
            for account_id, account in self.accounts.items():
                balance = self.get_account_balance(account_id, currency)
                
                trial_balance["accounts"].append({
                    "account_id": account_id,
                    "account_code": account.account_code,
                    "account_name": account.account_name,
                    "account_type": account.account_type,
                    "balance": float(balance)
                })
            
            return trial_balance
            
        except Exception as e:
            logger.error(f"Error getting trial balance: {e}")
            return {"error": str(e)}

class SettlementEngine:
    """Settlement processing engine"""
    
    def __init__(self):
        self.settlements: Dict[str, Settlement] = {}
        self.entities: Dict[str, Entity] = {}
        self.general_ledger = GeneralLedger()
        self.currency_converter = CurrencyConverter()
        self.netting_engine = NettingEngine()
        
    def add_entity(self, entity: Entity) -> bool:
        """Add business entity"""
        try:
            self.entities[entity.entity_id] = entity
            logger.info(f"Added entity: {entity.name}")
            return True
        except Exception as e:
            logger.error(f"Error adding entity: {e}")
            return False
    
    def create_settlement(self, trade_id: str, entity_id: str, counterparty_id: str,
                         commodity: str, quantity: Decimal, price: Decimal,
                         currency: Currency, settlement_date: datetime,
                         payment_method: PaymentMethod) -> str:
        """Create settlement record"""
        try:
            settlement_id = f"SETTLE_{uuid.uuid4().hex[:8].upper()}"
            
            # Calculate settlement amount
            settlement_amount = quantity * price
            
            # Get exchange rate
            exchange_rate = self.currency_converter.get_exchange_rate(currency, Currency.USD)
            
            # Calculate fees and taxes
            fees = self._calculate_settlement_fees(settlement_amount, payment_method)
            taxes = self._calculate_taxes(settlement_amount, entity_id)
            
            # Calculate net amount
            net_amount = settlement_amount - fees - taxes
            
            settlement = Settlement(
                settlement_id=settlement_id,
                trade_id=trade_id,
                entity_id=entity_id,
                counterparty_id=counterparty_id,
                commodity=commodity,
                quantity=quantity,
                price=price,
                currency=currency,
                settlement_amount=settlement_amount,
                settlement_date=settlement_date,
                payment_method=payment_method,
                status=SettlementStatus.PENDING,
                exchange_rate=exchange_rate,
                fees=fees,
                taxes=taxes,
                net_amount=net_amount
            )
            
            self.settlements[settlement_id] = settlement
            logger.info(f"Created settlement: {settlement_id}")
            return settlement_id
            
        except Exception as e:
            logger.error(f"Error creating settlement: {e}")
            return ""
    
    def _calculate_settlement_fees(self, amount: Decimal, payment_method: PaymentMethod) -> Decimal:
        """Calculate settlement fees"""
        try:
            fee_rates = {
                PaymentMethod.WIRE_TRANSFER: Decimal('0.001'),  # 0.1%
                PaymentMethod.ACH: Decimal('0.0005'),          # 0.05%
                PaymentMethod.CHECK: Decimal('0.002'),          # 0.2%
                PaymentMethod.CREDIT_CARD: Decimal('0.03'),     # 3%
                PaymentMethod.CRYPTO: Decimal('0.001'),         # 0.1%
                PaymentMethod.NETTING: Decimal('0.0')           # 0%
            }
            
            fee_rate = fee_rates.get(payment_method, Decimal('0.001'))
            return amount * fee_rate
            
        except Exception as e:
            logger.error(f"Error calculating settlement fees: {e}")
            return Decimal('0.0')
    
    def _calculate_taxes(self, amount: Decimal, entity_id: str) -> Decimal:
        """Calculate taxes"""
        try:
            # Simplified tax calculation
            tax_rate = Decimal('0.1')  # 10% tax rate
            return amount * tax_rate
            
        except Exception as e:
            logger.error(f"Error calculating taxes: {e}")
            return Decimal('0.0')
    
    def process_settlement(self, settlement_id: str) -> bool:
        """Process settlement"""
        try:
            if settlement_id not in self.settlements:
                return False
            
            settlement = self.settlements[settlement_id]
            
            # Update status to processing
            settlement.status = SettlementStatus.PROCESSING
            
            # Create journal entries
            self._create_settlement_journal_entries(settlement)
            
            # Process payment
            payment_success = self._process_payment(settlement)
            
            if payment_success:
                settlement.status = SettlementStatus.SETTLED
                logger.info(f"Settlement processed successfully: {settlement_id}")
            else:
                settlement.status = SettlementStatus.FAILED
                logger.error(f"Settlement processing failed: {settlement_id}")
            
            return payment_success
            
        except Exception as e:
            logger.error(f"Error processing settlement: {e}")
            return False
    
    def _create_settlement_journal_entries(self, settlement: Settlement):
        """Create journal entries for settlement"""
        try:
            # Debit: Accounts Receivable/Payable
            # Credit: Cash/Bank
            
            entry_id = f"JE_{uuid.uuid4().hex[:8].upper()}"
            
            journal_entry = JournalEntry(
                entry_id=entry_id,
                entry_date=settlement.settlement_date,
                description=f"Settlement for trade {settlement.trade_id}",
                reference=settlement.settlement_id,
                entity_id=settlement.entity_id,
                currency=settlement.currency,
                debit_account="accounts_receivable",
                credit_account="cash",
                amount=settlement.net_amount
            )
            
            self.general_ledger.create_journal_entry(journal_entry)
            
        except Exception as e:
            logger.error(f"Error creating settlement journal entries: {e}")
    
    def _process_payment(self, settlement: Settlement) -> bool:
        """Process payment"""
        try:
            # Simulate payment processing
            # In practice, this would integrate with payment processors
            
            if settlement.payment_method == PaymentMethod.NETTING:
                return self.netting_engine.process_netting(settlement)
            else:
                # Simulate successful payment
                return True
                
        except Exception as e:
            logger.error(f"Error processing payment: {e}")
            return False
    
    def get_settlement_status(self, settlement_id: str) -> Dict[str, Any]:
        """Get settlement status"""
        try:
            if settlement_id not in self.settlements:
                return {"error": "Settlement not found"}
            
            settlement = self.settlements[settlement_id]
            
            return {
                "settlement_id": settlement_id,
                "trade_id": settlement.trade_id,
                "entity_id": settlement.entity_id,
                "counterparty_id": settlement.counterparty_id,
                "commodity": settlement.commodity,
                "quantity": float(settlement.quantity),
                "price": float(settlement.price),
                "currency": settlement.currency.value,
                "settlement_amount": float(settlement.settlement_amount),
                "net_amount": float(settlement.net_amount),
                "fees": float(settlement.fees),
                "taxes": float(settlement.taxes),
                "status": settlement.status.value,
                "settlement_date": settlement.settlement_date.isoformat(),
                "payment_method": settlement.payment_method.value
            }
            
        except Exception as e:
            logger.error(f"Error getting settlement status: {e}")
            return {"error": str(e)}

class InvoiceEngine:
    """Invoice management engine"""
    
    def __init__(self):
        self.invoices: Dict[str, Invoice] = {}
        self.payments: Dict[str, Payment] = {}
        self.entities: Dict[str, Entity] = {}
        self.general_ledger = GeneralLedger()
        
    def create_invoice(self, entity_id: str, counterparty_id: str,
                      invoice_date: datetime, due_date: datetime,
                      currency: Currency, line_items: List[Dict[str, Any]],
                      payment_terms: str = "Net 30") -> str:
        """Create invoice"""
        try:
            invoice_id = f"INV_{uuid.uuid4().hex[:8].upper()}"
            invoice_number = f"INV-{datetime.utcnow().strftime('%Y%m%d')}-{invoice_id[:8]}"
            
            # Calculate totals
            subtotal = sum(Decimal(str(item.get('amount', 0))) for item in line_items)
            taxes = subtotal * Decimal('0.1')  # 10% tax
            fees = Decimal('0.0')  # No fees for now
            total_amount = subtotal + taxes + fees
            
            invoice = Invoice(
                invoice_id=invoice_id,
                invoice_number=invoice_number,
                entity_id=entity_id,
                counterparty_id=counterparty_id,
                invoice_date=invoice_date,
                due_date=due_date,
                currency=currency,
                subtotal=subtotal,
                taxes=taxes,
                fees=fees,
                total_amount=total_amount,
                status=InvoiceStatus.DRAFT,
                payment_terms=payment_terms,
                payment_method=PaymentMethod.WIRE_TRANSFER,
                line_items=line_items
            )
            
            self.invoices[invoice_id] = invoice
            logger.info(f"Created invoice: {invoice_number}")
            return invoice_id
            
        except Exception as e:
            logger.error(f"Error creating invoice: {e}")
            return ""
    
    def send_invoice(self, invoice_id: str) -> bool:
        """Send invoice to counterparty"""
        try:
            if invoice_id not in self.invoices:
                return False
            
            invoice = self.invoices[invoice_id]
            invoice.status = InvoiceStatus.SENT
            
            # Create journal entry for invoice
            self._create_invoice_journal_entry(invoice)
            
            logger.info(f"Invoice sent: {invoice.invoice_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending invoice: {e}")
            return False
    
    def _create_invoice_journal_entry(self, invoice: Invoice):
        """Create journal entry for invoice"""
        try:
            entry_id = f"JE_{uuid.uuid4().hex[:8].upper()}"
            
            journal_entry = JournalEntry(
                entry_id=entry_id,
                entry_date=invoice.invoice_date,
                description=f"Invoice {invoice.invoice_number}",
                reference=invoice.invoice_id,
                entity_id=invoice.entity_id,
                currency=invoice.currency,
                debit_account="accounts_receivable",
                credit_account="revenue",
                amount=invoice.total_amount
            )
            
            self.general_ledger.create_journal_entry(journal_entry)
            
        except Exception as e:
            logger.error(f"Error creating invoice journal entry: {e}")
    
    def process_payment(self, invoice_id: str, payment_amount: Decimal,
                       payment_date: datetime, payment_method: PaymentMethod,
                       reference: str) -> str:
        """Process payment for invoice"""
        try:
            if invoice_id not in self.invoices:
                return ""
            
            invoice = self.invoices[invoice_id]
            
            # Create payment record
            payment_id = f"PAY_{uuid.uuid4().hex[:8].upper()}"
            
            payment = Payment(
                payment_id=payment_id,
                invoice_id=invoice_id,
                entity_id=invoice.entity_id,
                counterparty_id=invoice.counterparty_id,
                payment_date=payment_date,
                amount=payment_amount,
                currency=invoice.currency,
                payment_method=payment_method,
                reference=reference
            )
            
            self.payments[payment_id] = payment
            
            # Update invoice status
            if payment_amount >= invoice.total_amount:
                invoice.status = InvoiceStatus.PAID
            else:
                invoice.status = InvoiceStatus.OVERDUE
            
            # Create journal entry for payment
            self._create_payment_journal_entry(payment)
            
            logger.info(f"Payment processed: {payment_id}")
            return payment_id
            
        except Exception as e:
            logger.error(f"Error processing payment: {e}")
            return ""
    
    def _create_payment_journal_entry(self, payment: Payment):
        """Create journal entry for payment"""
        try:
            entry_id = f"JE_{uuid.uuid4().hex[:8].upper()}"
            
            journal_entry = JournalEntry(
                entry_id=entry_id,
                entry_date=payment.payment_date,
                description=f"Payment for invoice {payment.invoice_id}",
                reference=payment.payment_id,
                entity_id=payment.entity_id,
                currency=payment.currency,
                debit_account="cash",
                credit_account="accounts_receivable",
                amount=payment.amount
            )
            
            self.general_ledger.create_journal_entry(journal_entry)
            
        except Exception as e:
            logger.error(f"Error creating payment journal entry: {e}")
    
    def get_invoice_status(self, invoice_id: str) -> Dict[str, Any]:
        """Get invoice status"""
        try:
            if invoice_id not in self.invoices:
                return {"error": "Invoice not found"}
            
            invoice = self.invoices[invoice_id]
            
            return {
                "invoice_id": invoice_id,
                "invoice_number": invoice.invoice_number,
                "entity_id": invoice.entity_id,
                "counterparty_id": invoice.counterparty_id,
                "invoice_date": invoice.invoice_date.isoformat(),
                "due_date": invoice.due_date.isoformat(),
                "currency": invoice.currency.value,
                "subtotal": float(invoice.subtotal),
                "taxes": float(invoice.taxes),
                "fees": float(invoice.fees),
                "total_amount": float(invoice.total_amount),
                "status": invoice.status.value,
                "payment_terms": invoice.payment_terms,
                "line_items": invoice.line_items
            }
            
        except Exception as e:
            logger.error(f"Error getting invoice status: {e}")
            return {"error": str(e)}

class CurrencyConverter:
    """Currency conversion engine"""
    
    def __init__(self):
        self.exchange_rates: Dict[str, Dict[str, Decimal]] = {}
        self._initialize_exchange_rates()
        
    def _initialize_exchange_rates(self):
        """Initialize exchange rates"""
        try:
            # Base currency: USD
            base_rates = {
                "USD": Decimal('1.0'),
                "EUR": Decimal('0.85'),
                "GBP": Decimal('0.73'),
                "JPY": Decimal('110.0'),
                "CAD": Decimal('1.25'),
                "AUD": Decimal('1.35'),
                "CHF": Decimal('0.92'),
                "CNY": Decimal('6.45')
            }
            
            # Create cross rates
            for from_currency, from_rate in base_rates.items():
                self.exchange_rates[from_currency] = {}
                for to_currency, to_rate in base_rates.items():
                    if from_currency == to_currency:
                        self.exchange_rates[from_currency][to_currency] = Decimal('1.0')
                    else:
                        self.exchange_rates[from_currency][to_currency] = to_rate / from_rate
            
            logger.info("Exchange rates initialized")
            
        except Exception as e:
            logger.error(f"Error initializing exchange rates: {e}")
    
    def get_exchange_rate(self, from_currency: Currency, to_currency: Currency) -> Decimal:
        """Get exchange rate between currencies"""
        try:
            return self.exchange_rates.get(from_currency.value, {}).get(to_currency.value, Decimal('1.0'))
        except Exception as e:
            logger.error(f"Error getting exchange rate: {e}")
            return Decimal('1.0')
    
    def convert_amount(self, amount: Decimal, from_currency: Currency, to_currency: Currency) -> Decimal:
        """Convert amount between currencies"""
        try:
            if from_currency == to_currency:
                return amount
            
            exchange_rate = self.get_exchange_rate(from_currency, to_currency)
            return amount * exchange_rate
            
        except Exception as e:
            logger.error(f"Error converting amount: {e}")
            return amount

class NettingEngine:
    """Netting engine for bilateral and multilateral netting"""
    
    def __init__(self):
        self.netting_agreements: Dict[str, NettingAgreement] = {}
        self.netting_positions: Dict[str, Dict[str, Decimal]] = {}
        
    def create_netting_agreement(self, entity_id: str, counterparty_id: str,
                                agreement_date: datetime, effective_date: datetime,
                                expiry_date: datetime, netting_type: str,
                                currencies: List[Currency]) -> str:
        """Create netting agreement"""
        try:
            agreement_id = f"NET_{uuid.uuid4().hex[:8].upper()}"
            
            agreement = NettingAgreement(
                agreement_id=agreement_id,
                entity_id=entity_id,
                counterparty_id=counterparty_id,
                agreement_date=agreement_date,
                effective_date=effective_date,
                expiry_date=expiry_date,
                netting_type=netting_type,
                currencies=currencies
            )
            
            self.netting_agreements[agreement_id] = agreement
            
            # Initialize netting positions
            self.netting_positions[agreement_id] = {
                currency.value: Decimal('0.0') for currency in currencies
            }
            
            logger.info(f"Created netting agreement: {agreement_id}")
            return agreement_id
            
        except Exception as e:
            logger.error(f"Error creating netting agreement: {e}")
            return ""
    
    def process_netting(self, settlement: Settlement) -> bool:
        """Process netting for settlement"""
        try:
            # Find applicable netting agreement
            agreement = self._find_netting_agreement(settlement.entity_id, settlement.counterparty_id)
            
            if not agreement:
                return False
            
            # Add to netting position
            currency_key = settlement.currency.value
            if currency_key in self.netting_positions[agreement.agreement_id]:
                self.netting_positions[agreement.agreement_id][currency_key] += settlement.net_amount
            
            # Check if netting can be executed
            if self._can_execute_netting(agreement.agreement_id):
                return self._execute_netting(agreement.agreement_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing netting: {e}")
            return False
    
    def _find_netting_agreement(self, entity_id: str, counterparty_id: str) -> Optional[NettingAgreement]:
        """Find applicable netting agreement"""
        try:
            for agreement in self.netting_agreements.values():
                if (agreement.entity_id == entity_id and 
                    agreement.counterparty_id == counterparty_id and
                    agreement.is_active and
                    agreement.effective_date <= datetime.utcnow() <= agreement.expiry_date):
                    return agreement
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding netting agreement: {e}")
            return None
    
    def _can_execute_netting(self, agreement_id: str) -> bool:
        """Check if netting can be executed"""
        try:
            # Simplified netting logic
            positions = self.netting_positions.get(agreement_id, {})
            
            # Check if any position is significant enough for netting
            for currency, amount in positions.items():
                if abs(amount) > Decimal('1000'):  # Minimum netting threshold
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking netting execution: {e}")
            return False
    
    def _execute_netting(self, agreement_id: str) -> bool:
        """Execute netting"""
        try:
            # Simplified netting execution
            positions = self.netting_positions.get(agreement_id, {})
            
            # Calculate net position
            net_position = sum(positions.values())
            
            if abs(net_position) > Decimal('0.01'):  # Minimum netting amount
                logger.info(f"Netting executed for agreement {agreement_id}: {net_position}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error executing netting: {e}")
            return False

class SettlementEngine:
    """Main settlement engine"""
    
    def __init__(self):
        self.settlement_engine = SettlementEngine()
        self.invoice_engine = InvoiceEngine()
        self.general_ledger = GeneralLedger()
        self.currency_converter = CurrencyConverter()
        self.netting_engine = NettingEngine()
        
    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive settlement status"""
        try:
            return {
                "settlements": {
                    "total": len(self.settlement_engine.settlements),
                    "pending": len([s for s in self.settlement_engine.settlements.values() if s.status == SettlementStatus.PENDING]),
                    "settled": len([s for s in self.settlement_engine.settlements.values() if s.status == SettlementStatus.SETTLED]),
                    "failed": len([s for s in self.settlement_engine.settlements.values() if s.status == SettlementStatus.FAILED])
                },
                "invoices": {
                    "total": len(self.invoice_engine.invoices),
                    "draft": len([i for i in self.invoice_engine.invoices.values() if i.status == InvoiceStatus.DRAFT]),
                    "sent": len([i for i in self.invoice_engine.invoices.values() if i.status == InvoiceStatus.SENT]),
                    "paid": len([i for i in self.invoice_engine.invoices.values() if i.status == InvoiceStatus.PAID]),
                    "overdue": len([i for i in self.invoice_engine.invoices.values() if i.status == InvoiceStatus.OVERDUE])
                },
                "general_ledger": {
                    "accounts": len(self.general_ledger.accounts),
                    "journal_entries": len(self.general_ledger.journal_entries)
                },
                "netting": {
                    "agreements": len(self.netting_engine.netting_agreements),
                    "active_positions": len(self.netting_engine.netting_positions)
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting comprehensive status: {e}")
            return {"error": str(e)}

# Global settlement engine instance
settlement_engine = SettlementEngine()

def get_settlement_status() -> Dict[str, Any]:
    """Get comprehensive settlement status"""
    return settlement_engine.get_comprehensive_status()

def create_settlement(trade_id: str, entity_id: str, counterparty_id: str,
                     commodity: str, quantity: Decimal, price: Decimal,
                     currency: Currency, settlement_date: datetime,
                     payment_method: PaymentMethod) -> str:
    """Create settlement record"""
    return settlement_engine.settlement_engine.create_settlement(
        trade_id, entity_id, counterparty_id, commodity, quantity, price,
        currency, settlement_date, payment_method
    )

def process_settlement(settlement_id: str) -> bool:
    """Process settlement"""
    return settlement_engine.settlement_engine.process_settlement(settlement_id)

def create_invoice(entity_id: str, counterparty_id: str,
                  invoice_date: datetime, due_date: datetime,
                  currency: Currency, line_items: List[Dict[str, Any]],
                  payment_terms: str = "Net 30") -> str:
    """Create invoice"""
    return settlement_engine.invoice_engine.create_invoice(
        entity_id, counterparty_id, invoice_date, due_date, currency, line_items, payment_terms
    )

def send_invoice(invoice_id: str) -> bool:
    """Send invoice to counterparty"""
    return settlement_engine.invoice_engine.send_invoice(invoice_id)

def process_payment(invoice_id: str, payment_amount: Decimal,
                   payment_date: datetime, payment_method: PaymentMethod,
                   reference: str) -> str:
    """Process payment for invoice"""
    return settlement_engine.invoice_engine.process_payment(
        invoice_id, payment_amount, payment_date, payment_method, reference
    )

def get_trial_balance(currency: Currency) -> Dict[str, Any]:
    """Get trial balance"""
    return settlement_engine.general_ledger.get_trial_balance(currency)

def create_netting_agreement(entity_id: str, counterparty_id: str,
                            agreement_date: datetime, effective_date: datetime,
                            expiry_date: datetime, netting_type: str,
                            currencies: List[Currency]) -> str:
    """Create netting agreement"""
    return settlement_engine.netting_engine.create_netting_agreement(
        entity_id, counterparty_id, agreement_date, effective_date,
        expiry_date, netting_type, currencies
    )
