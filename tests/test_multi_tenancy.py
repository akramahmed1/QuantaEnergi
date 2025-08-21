"""
Comprehensive tests for multi-tenancy system.

These tests verify that the tenant-aware database sessions provide
complete data isolation between different companies/tenants.
"""

import pytest
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from src.energyopti_pro.db.models import (
    Base, Company, User, Contract, Trade, Position, 
    RiskMetrics, Compliance, MarketData, Settlement
)
from src.energyopti_pro.db.tenant_session import (
    TenantAwareSession, AsyncTenantAwareSession,
    create_tenant_session_factory
)
from src.energyopti_pro.api.dependencies import get_tenant_session

# Test database configuration
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()

@pytest.fixture
async def test_session_factory(test_engine):
    """Create test session factory."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    return async_session

@pytest.fixture
async def company_1():
    """Create test company 1."""
    return Company(
        id=uuid.uuid4(),
        name="Test Company 1",
        registration_number="REG001",
        country="UAE",
        region="ME",
        industry="Energy"
    )

@pytest.fixture
async def company_2():
    """Create test company 2."""
    return Company(
        id=uuid.uuid4(),
        name="Test Company 2",
        registration_number="REG002",
        country="UK",
        region="UK",
        industry="Energy"
    )

@pytest.fixture
async def user_1(company_1):
    """Create test user for company 1."""
    return User(
        id=1,
        username="user1",
        email="user1@company1.com",
        hashed_password="hashed_password",
        role="trader",
        company_id=company_1.id,
        region="ME"
    )

@pytest.fixture
async def user_2(company_2):
    """Create test user for company 2."""
    return User(
        id=2,
        username="user2",
        email="user2@company2.com",
        hashed_password="hashed_password",
        role="trader",
        company_id=company_2.id,
        region="UK"
    )

@pytest.fixture
async def contract_1(company_1):
    """Create test contract for company 1."""
    return Contract(
        id=str(uuid.uuid4()),
        contract_number="CTR-ME-12345678",
        contract_type="PPA",
        counterparty_id=str(uuid.uuid4()),
        commodity="Power",
        delivery_location="Dubai",
        delivery_period_start=datetime.now(),
        delivery_period_end=datetime.now() + timedelta(days=30),
        quantity=100.0,
        unit="MWh",
        price=Decimal("75.50"),
        currency="USD",
        status="active",
        region="ME",
        company_id=company_1.id
    )

@pytest.fixture
async def contract_2(company_2):
    """Create test contract for company 2."""
    return Contract(
        id=str(uuid.uuid4()),
        contract_number="CTR-UK-87654321",
        contract_type="PPA",
        counterparty_id=str(uuid.uuid4()),
        commodity="Power",
        delivery_location="London",
        delivery_period_start=datetime.now(),
        delivery_period_end=datetime.now() + timedelta(days=30),
        quantity=200.0,
        unit="MWh",
        price=Decimal("85.00"),
        currency="GBP",
        status="active",
        region="UK",
        company_id=company_2.id
    )

class TestMultiTenancyDataIsolation:
    """Test complete data isolation between tenants."""
    
    async def test_company_creation(self, test_session_factory, company_1, company_2):
        """Test that companies can be created independently."""
        async with test_session_factory() as session:
            # Add companies
            session.add(company_1)
            session.add(company_2)
            await session.commit()
            
            # Verify companies exist
            companies = await session.execute(text("SELECT * FROM companies"))
            company_list = companies.fetchall()
            assert len(company_list) == 2
            
            # Verify company IDs are different
            company_ids = [str(c[0]) for c in company_list]
            assert len(set(company_ids)) == 2
    
    async def test_user_company_isolation(self, test_session_factory, company_1, company_2, user_1, user_2):
        """Test that users are properly associated with their companies."""
        async with test_session_factory() as session:
            # Add companies and users
            session.add(company_1)
            session.add(company_2)
            session.add(user_1)
            session.add(user_2)
            await session.commit()
            
            # Verify users have correct company associations
            user1_from_db = await session.get(User, user_1.id)
            user2_from_db = await session.get(User, user_2.id)
            
            assert user1_from_db.company_id == company_1.id
            assert user2_from_db.company_id == company_2.id
            assert user1_from_db.company_id != user2_from_db.company_id
    
    async def test_contract_company_isolation(self, test_session_factory, company_1, company_2, contract_1, contract_2):
        """Test that contracts are properly isolated by company."""
        async with test_session_factory() as session:
            # Add companies and contracts
            session.add(company_1)
            session.add(company_2)
            session.add(contract_1)
            session.add(contract_2)
            await session.commit()
            
            # Verify contracts have correct company associations
            contract1_from_db = await session.get(Contract, contract_1.id)
            contract2_from_db = await session.get(Contract, contract_2.id)
            
            assert contract1_from_db.company_id == company_1.id
            assert contract2_from_db.company_id == company_2.id
            assert contract1_from_db.company_id != contract2_from_db.company_id
    
    async def test_tenant_session_creation(self, test_session_factory, company_1):
        """Test that tenant-aware sessions can be created."""
        company_id = company_1.id
        
        # Create tenant session factory
        session_factory = create_tenant_session_factory(company_id)
        
        # Create session
        session = session_factory()
        assert session.company_id == company_id
        assert isinstance(session, TenantAwareSession)
        
        session.close()
    
    async def test_tenant_session_company_scoping(self, test_session_factory, company_1, company_2, contract_1, contract_2):
        """Test that tenant sessions automatically scope queries to company_id."""
        async with test_session_factory() as session:
            # Add companies and contracts
            session.add(company_1)
            session.add(company_2)
            session.add(contract_1)
            session.add(contract_2)
            await session.commit()
        
        # Test company 1 tenant session
        company1_session_factory = create_tenant_session_factory(company_1.id)
        with company1_session_factory() as tenant_session:
            # Query contracts - should only see company 1 contracts
            contracts = tenant_session.query(Contract).all()
            assert len(contracts) == 1
            assert contracts[0].company_id == company_1.id
            assert contracts[0].contract_number == "CTR-ME-12345678"
        
        # Test company 2 tenant session
        company2_session_factory = create_tenant_session_factory(company_2.id)
        with company2_session_factory() as tenant_session:
            # Query contracts - should only see company 2 contracts
            contracts = tenant_session.query(Contract).all()
            assert len(contracts) == 1
            assert contracts[0].company_id == company_2.id
            assert contracts[0].contract_number == "CTR-UK-87654321"
    
    async def test_tenant_session_automatic_company_id_setting(self, test_session_factory, company_1):
        """Test that tenant sessions automatically set company_id on new records."""
        async with test_session_factory() as session:
            session.add(company_1)
            await session.commit()
        
        # Create tenant session
        company1_session_factory = create_tenant_session_factory(company_1.id)
        with company1_session_factory() as tenant_session:
            # Create new contract without setting company_id
            new_contract = Contract(
                id=str(uuid.uuid4()),
                contract_number="CTR-ME-NEW123",
                contract_type="PPA",
                counterparty_id=str(uuid.uuid4()),
                commodity="Gas",
                delivery_location="Abu Dhabi",
                delivery_period_start=datetime.now(),
                delivery_period_end=datetime.now() + timedelta(days=30),
                quantity=50.0,
                unit="MMBtu",
                price=Decimal("3.25"),
                currency="USD",
                status="active",
                region="ME"
                # company_id not set - should be set automatically
            )
            
            # Add to tenant session
            tenant_session.add(new_contract)
            tenant_session.commit()
            
            # Verify company_id was automatically set
            assert new_contract.company_id == company_1.id
    
    async def test_cross_tenant_data_invisibility(self, test_session_factory, company_1, company_2, contract_1, contract_2):
        """Test that data from one company is completely invisible to another."""
        async with test_session_factory() as session:
            # Add companies and contracts
            session.add(company_1)
            session.add(company_2)
            session.add(contract_1)
            session.add(contract_2)
            await session.commit()
        
        # Company 1 session should not see Company 2 data
        company1_session_factory = create_tenant_session_factory(company_1.id)
        with company1_session_factory() as tenant_session:
            # Try to query by contract ID from company 2
            contract2_from_company1 = tenant_session.query(Contract).filter(
                Contract.id == contract_2.id
            ).first()
            
            # Should return None - company 2 data is invisible
            assert contract2_from_company1 is None
        
        # Company 2 session should not see Company 1 data
        company2_session_factory = create_tenant_session_factory(company_2.id)
        with company2_session_factory() as tenant_session:
            # Try to query by contract ID from company 1
            contract1_from_company2 = tenant_session.query(Contract).filter(
                Contract.id == contract_1.id
            ).first()
            
            # Should return None - company 1 data is invisible
            assert contract1_from_company2 is None
    
    async def test_tenant_session_update_operations(self, test_session_factory, company_1, contract_1):
        """Test that tenant sessions properly handle update operations."""
        async with test_session_factory() as session:
            session.add(company_1)
            session.add(contract_1)
            await session.commit()
        
        # Test update in tenant session
        company1_session_factory = create_tenant_session_factory(company_1.id)
        with company1_session_factory() as tenant_session:
            # Get contract
            contract = tenant_session.query(Contract).first()
            assert contract is not None
            
            # Update contract
            old_price = contract.price
            contract.price = Decimal("80.00")
            tenant_session.commit()
            
            # Verify update
            updated_contract = tenant_session.query(Contract).first()
            assert updated_contract.price == Decimal("80.00")
            assert updated_contract.price != old_price
    
    async def test_tenant_session_delete_operations(self, test_session_factory, company_1, contract_1):
        """Test that tenant sessions properly handle delete operations."""
        async with test_session_factory() as session:
            session.add(company_1)
            session.add(contract_1)
            await session.commit()
        
        # Test delete in tenant session
        company1_session_factory = create_tenant_session_factory(company_1.id)
        with company1_session_factory() as tenant_session:
            # Get contract
            contract = tenant_session.query(Contract).first()
            assert contract is not None
            
            # Delete contract
            tenant_session.delete(contract)
            tenant_session.commit()
            
            # Verify deletion
            deleted_contract = tenant_session.query(Contract).first()
            assert deleted_contract is None

class TestMultiTenancySecurity:
    """Test security aspects of multi-tenancy."""
    
    async def test_tenant_session_prevents_company_id_manipulation(self, test_session_factory, company_1, company_2):
        """Test that tenant sessions prevent malicious company_id manipulation."""
        async with test_session_factory() as session:
            session.add(company_1)
            session.add(company_2)
            await session.commit()
        
        # Create tenant session for company 1
        company1_session_factory = create_tenant_session_factory(company_1.id)
        with company1_session_factory() as tenant_session:
            # Try to create a contract with company 2's ID
            malicious_contract = Contract(
                id=str(uuid.uuid4()),
                contract_number="CTR-ME-MALICIOUS",
                contract_type="PPA",
                counterparty_id=str(uuid.uuid4()),
                commodity="Power",
                delivery_location="Dubai",
                delivery_period_start=datetime.now(),
                delivery_period_end=datetime.now() + timedelta(days=30),
                quantity=100.0,
                unit="MWh",
                price=Decimal("75.50"),
                currency="USD",
                status="active",
                region="ME",
                company_id=company_2.id  # Malicious attempt
            )
            
            # Add to tenant session
            tenant_session.add(malicious_contract)
            tenant_session.commit()
            
            # The tenant session should automatically override the company_id
            assert malicious_contract.company_id == company_1.id
            assert malicious_contract.company_id != company_2.id
    
    async def test_tenant_session_query_injection_protection(self, test_session_factory, company_1, company_2, contract_1, contract_2):
        """Test that tenant sessions protect against query injection attacks."""
        async with test_session_factory() as session:
            session.add(company_1)
            session.add(company_2)
            session.add(contract_1)
            session.add(contract_2)
            await session.commit()
        
        # Company 1 session
        company1_session_factory = create_tenant_session_factory(company_1.id)
        with company1_session_factory() as tenant_session:
            # Try to query with raw SQL that might bypass company filtering
            # This should still be scoped to company 1
            contracts = tenant_session.query(Contract).from_statement(
                text("SELECT * FROM contracts")
            ).all()
            
            # All contracts should belong to company 1
            for contract in contracts:
                assert contract.company_id == company_1.id

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 