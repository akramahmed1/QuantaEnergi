"""initial trades

Revision ID: 004
Revises: 003
Create Date: 2025-09-26 15:10:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None

def upgrade():
    """Create trades table for ETRM trade capture"""
    op.create_table('trades',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('asset', sa.String(), nullable=True),
        sa.Column('quantity', sa.Float(), nullable=True),
        sa.Column('price', sa.Float(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    """Remove trades table"""
    op.drop_table('trades')
