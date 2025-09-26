"""Add trade table

Revision ID: 001
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Add trades table for PRD 4.1 trade capture"""
    op.create_table('trades',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('asset', sa.String(length=50), nullable=False),
        sa.Column('volume', sa.Float(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('region', sa.String(length=50), nullable=False),
        sa.Column('amendments', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_trades_id'), 'trades', ['id'], unique=False)

def downgrade():
    """Remove trades table"""
    op.drop_index(op.f('ix_trades_id'), table_name='trades')
    op.drop_table('trades')
