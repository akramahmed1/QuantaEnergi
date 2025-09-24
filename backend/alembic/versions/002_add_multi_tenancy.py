"""Add multi-tenancy support

Revision ID: 002
Revises: 001
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    """Add multi-tenancy tables and columns"""
    
    # Create tenants table
    op.create_table('tenants',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('admin_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('settings', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Add tenant_id column to existing tables
    op.add_column('users', sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('trades', sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('portfolios', sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('positions', sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('risk_calculations', sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True))
    
    # Create indexes for tenant_id columns
    op.create_index('ix_users_tenant_id', 'users', ['tenant_id'])
    op.create_index('ix_trades_tenant_id', 'trades', ['tenant_id'])
    op.create_index('ix_portfolios_tenant_id', 'portfolios', ['tenant_id'])
    op.create_index('ix_positions_tenant_id', 'positions', ['tenant_id'])
    op.create_index('ix_risk_calculations_tenant_id', 'risk_calculations', ['tenant_id'])
    
    # Create foreign key constraints
    op.create_foreign_key('fk_users_tenant_id', 'users', 'tenants', ['tenant_id'], ['id'])
    op.create_foreign_key('fk_trades_tenant_id', 'trades', 'tenants', ['tenant_id'], ['id'])
    op.create_foreign_key('fk_portfolios_tenant_id', 'portfolios', 'tenants', ['tenant_id'], ['id'])
    op.create_foreign_key('fk_positions_tenant_id', 'positions', 'tenants', ['tenant_id'], ['id'])
    op.create_foreign_key('fk_risk_calculations_tenant_id', 'risk_calculations', 'tenants', ['tenant_id'], ['id'])
    
    # Enable Row Level Security on tables
    op.execute('ALTER TABLE users ENABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE trades ENABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE portfolios ENABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE positions ENABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE risk_calculations ENABLE ROW LEVEL SECURITY')
    
    # Create RLS policies for tenant isolation
    op.execute("""
        CREATE POLICY tenant_isolation_users ON users
        FOR ALL TO PUBLIC
        USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid)
    """)
    
    op.execute("""
        CREATE POLICY tenant_isolation_trades ON trades
        FOR ALL TO PUBLIC
        USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid)
    """)
    
    op.execute("""
        CREATE POLICY tenant_isolation_portfolios ON portfolios
        FOR ALL TO PUBLIC
        USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid)
    """)
    
    op.execute("""
        CREATE POLICY tenant_isolation_positions ON positions
        FOR ALL TO PUBLIC
        USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid)
    """)
    
    op.execute("""
        CREATE POLICY tenant_isolation_risk_calculations ON risk_calculations
        FOR ALL TO PUBLIC
        USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid)
    """)
    
    # Create function to set current tenant ID
    op.execute("""
        CREATE OR REPLACE FUNCTION set_current_tenant_id(tenant_uuid uuid)
        RETURNS void AS $$
        BEGIN
            PERFORM set_config('app.current_tenant_id', tenant_uuid::text, true);
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Create default tenant for system operations
    op.execute("""
        INSERT INTO tenants (id, name, admin_user_id, created_at, is_active)
        VALUES (
            '00000000-0000-0000-0000-000000000000',
            'System Tenant',
            '00000000-0000-0000-0000-000000000000',
            NOW(),
            true
        )
        ON CONFLICT (id) DO NOTHING;
    """)


def downgrade():
    """Remove multi-tenancy support"""
    
    # Drop RLS policies
    op.execute('DROP POLICY IF EXISTS tenant_isolation_users ON users')
    op.execute('DROP POLICY IF EXISTS tenant_isolation_trades ON trades')
    op.execute('DROP POLICY IF EXISTS tenant_isolation_portfolios ON portfolios')
    op.execute('DROP POLICY IF EXISTS tenant_isolation_positions ON positions')
    op.execute('DROP POLICY IF EXISTS tenant_isolation_risk_calculations ON risk_calculations')
    
    # Disable Row Level Security
    op.execute('ALTER TABLE users DISABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE trades DISABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE portfolios DISABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE positions DISABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE risk_calculations DISABLE ROW LEVEL SECURITY')
    
    # Drop function
    op.execute('DROP FUNCTION IF EXISTS set_current_tenant_id(uuid)')
    
    # Drop foreign key constraints
    op.drop_constraint('fk_users_tenant_id', 'users', type_='foreignkey')
    op.drop_constraint('fk_trades_tenant_id', 'trades', type_='foreignkey')
    op.drop_constraint('fk_portfolios_tenant_id', 'portfolios', type_='foreignkey')
    op.drop_constraint('fk_positions_tenant_id', 'positions', type_='foreignkey')
    op.drop_constraint('fk_risk_calculations_tenant_id', 'risk_calculations', type_='foreignkey')
    
    # Drop indexes
    op.drop_index('ix_users_tenant_id', table_name='users')
    op.drop_index('ix_trades_tenant_id', table_name='trades')
    op.drop_index('ix_portfolios_tenant_id', table_name='portfolios')
    op.drop_index('ix_positions_tenant_id', table_name='positions')
    op.drop_index('ix_risk_calculations_tenant_id', table_name='risk_calculations')
    
    # Drop tenant_id columns
    op.drop_column('users', 'tenant_id')
    op.drop_column('trades', 'tenant_id')
    op.drop_column('portfolios', 'tenant_id')
    op.drop_column('positions', 'tenant_id')
    op.drop_column('risk_calculations', 'tenant_id')
    
    # Drop tenants table
    op.drop_table('tenants')
