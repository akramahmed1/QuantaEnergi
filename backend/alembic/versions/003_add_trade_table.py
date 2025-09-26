"""Add Trade table with required fields

Revision ID: 003
Revises: 002
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    """Add Trade table with comprehensive trade fields"""
    
    # Create trades table
    op.create_table('trades',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('trade_id', sa.String(length=100), nullable=False),
        sa.Column('external_trade_id', sa.String(length=100), nullable=True),
        
        # Trade details
        sa.Column('trade_type', sa.String(length=50), nullable=False),
        sa.Column('commodity', sa.String(length=50), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False, default='USD'),
        
        # Counterparty information
        sa.Column('counterparty_id', sa.String(length=100), nullable=False),
        sa.Column('counterparty_name', sa.String(length=255), nullable=True),
        
        # Delivery information
        sa.Column('delivery_date', sa.DateTime(), nullable=False),
        sa.Column('delivery_location', sa.String(length=255), nullable=False),
        sa.Column('delivery_term', sa.String(length=50), nullable=True, default='FOB'),
        
        # Trade direction and settlement
        sa.Column('trade_direction', sa.String(length=10), nullable=False),
        sa.Column('settlement_type', sa.String(length=50), nullable=True),
        sa.Column('settlement_date', sa.DateTime(), nullable=True),
        
        # Islamic finance compliance
        sa.Column('is_islamic_compliant', sa.Boolean(), nullable=False, default=False),
        sa.Column('sharia_approval', sa.String(length=255), nullable=True),
        sa.Column('islamic_compliance_notes', sa.Text(), nullable=True),
        
        # Risk and compliance
        sa.Column('risk_category', sa.String(length=50), nullable=True),
        sa.Column('compliance_status', sa.String(length=50), nullable=False, default='pending'),
        sa.Column('compliance_notes', sa.Text(), nullable=True),
        
        # Trade lifecycle status
        sa.Column('status', sa.String(length=50), nullable=False, default='captured'),
        sa.Column('lifecycle_stage', sa.String(length=50), nullable=False, default='capture'),
        
        # Financial details
        sa.Column('notional_value', sa.Float(), nullable=False),
        sa.Column('margin_requirement', sa.Float(), nullable=False, default=0.0),
        sa.Column('commission', sa.Float(), nullable=False, default=0.0),
        sa.Column('fees', sa.Float(), nullable=False, default=0.0),
        
        # Additional data
        sa.Column('trade_data', sa.JSON(), nullable=True),
        sa.Column('system_metadata', sa.JSON(), nullable=True),
        
        # Audit fields
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        
        # Soft delete
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_by', sa.String(length=100), nullable=True),
        
        # Multi-tenancy
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('trade_id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
    )
    
    # Create indexes
    op.create_index('ix_trades_organization_id', 'trades', ['organization_id'])
    op.create_index('ix_trades_trade_id', 'trades', ['trade_id'])
    op.create_index('ix_trades_commodity', 'trades', ['commodity'])
    op.create_index('ix_trades_status', 'trades', ['status'])
    op.create_index('ix_trades_delivery_date', 'trades', ['delivery_date'])
    op.create_index('ix_trades_created_at', 'trades', ['created_at'])
    op.create_index('ix_trades_tenant_id', 'trades', ['tenant_id'])
    
    # Create trade_allocations table
    op.create_table('trade_allocations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('trade_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        
        # Allocation details
        sa.Column('allocation_type', sa.String(length=50), nullable=False),
        sa.Column('allocated_quantity', sa.Float(), nullable=False),
        sa.Column('allocated_price', sa.Float(), nullable=False),
        sa.Column('allocation_percentage', sa.Float(), nullable=False),
        
        # Allocation metadata
        sa.Column('allocation_notes', sa.Text(), nullable=True),
        sa.Column('allocation_data', sa.JSON(), nullable=True),
        
        # Status and timing
        sa.Column('status', sa.String(length=50), nullable=False, default='pending'),
        sa.Column('allocated_at', sa.DateTime(), nullable=False),
        sa.Column('allocated_by', sa.String(length=100), nullable=False),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['trade_id'], ['trades.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
    )
    
    # Create trade_settlements table
    op.create_table('trade_settlements',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('trade_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        
        # Settlement details
        sa.Column('settlement_amount', sa.Float(), nullable=False),
        sa.Column('settlement_currency', sa.String(length=10), nullable=False, default='USD'),
        sa.Column('settlement_type', sa.String(length=50), nullable=False),
        
        # Payment information
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('payment_reference', sa.String(length=255), nullable=True),
        sa.Column('payment_date', sa.DateTime(), nullable=True),
        
        # Settlement status
        sa.Column('status', sa.String(length=50), nullable=False, default='pending'),
        sa.Column('settlement_notes', sa.Text(), nullable=True),
        
        # Audit fields
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['trade_id'], ['trades.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
    )
    
    # Create indexes for new tables
    op.create_index('ix_trade_allocations_trade_id', 'trade_allocations', ['trade_id'])
    op.create_index('ix_trade_allocations_organization_id', 'trade_allocations', ['organization_id'])
    op.create_index('ix_trade_allocations_tenant_id', 'trade_allocations', ['tenant_id'])
    
    op.create_index('ix_trade_settlements_trade_id', 'trade_settlements', ['trade_id'])
    op.create_index('ix_trade_settlements_organization_id', 'trade_settlements', ['organization_id'])
    op.create_index('ix_trade_settlements_tenant_id', 'trade_settlements', ['tenant_id'])
    
    # Enable Row Level Security on new tables
    op.execute('ALTER TABLE trades ENABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE trade_allocations ENABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE trade_settlements ENABLE ROW LEVEL SECURITY')
    
    # Create RLS policies for tenant isolation
    op.execute("""
        CREATE POLICY tenant_isolation_trades_new ON trades
        FOR ALL TO PUBLIC
        USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid)
    """)
    
    op.execute("""
        CREATE POLICY tenant_isolation_trade_allocations ON trade_allocations
        FOR ALL TO PUBLIC
        USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid)
    """)
    
    op.execute("""
        CREATE POLICY tenant_isolation_trade_settlements ON trade_settlements
        FOR ALL TO PUBLIC
        USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid)
    """)


def downgrade():
    """Remove Trade table and related tables"""
    
    # Drop RLS policies
    op.execute('DROP POLICY IF EXISTS tenant_isolation_trades_new ON trades')
    op.execute('DROP POLICY IF EXISTS tenant_isolation_trade_allocations ON trade_allocations')
    op.execute('DROP POLICY IF EXISTS tenant_isolation_trade_settlements ON trade_settlements')
    
    # Disable Row Level Security
    op.execute('ALTER TABLE trades DISABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE trade_allocations DISABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE trade_settlements DISABLE ROW LEVEL SECURITY')
    
    # Drop indexes
    op.drop_index('ix_trade_settlements_tenant_id', table_name='trade_settlements')
    op.drop_index('ix_trade_settlements_organization_id', table_name='trade_settlements')
    op.drop_index('ix_trade_settlements_trade_id', table_name='trade_settlements')
    
    op.drop_index('ix_trade_allocations_tenant_id', table_name='trade_allocations')
    op.drop_index('ix_trade_allocations_organization_id', table_name='trade_allocations')
    op.drop_index('ix_trade_allocations_trade_id', table_name='trade_allocations')
    
    op.drop_index('ix_trades_tenant_id', table_name='trades')
    op.drop_index('ix_trades_created_at', table_name='trades')
    op.drop_index('ix_trades_delivery_date', table_name='trades')
    op.drop_index('ix_trades_status', table_name='trades')
    op.drop_index('ix_trades_commodity', table_name='trades')
    op.drop_index('ix_trades_trade_id', table_name='trades')
    op.drop_index('ix_trades_organization_id', table_name='trades')
    
    # Drop tables
    op.drop_table('trade_settlements')
    op.drop_table('trade_allocations')
    op.drop_table('trades')
