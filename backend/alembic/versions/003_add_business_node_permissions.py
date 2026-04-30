"""add_business_node_permissions

Revision ID: 003
Revises: 002
Create Date: 2026-04-30

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create business_node_permissions table
    op.create_table(
        'business_node_permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('business_node_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('permission_type', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['business_node_id'], ['business_nodes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('business_node_id', 'user_id', name='_node_user_uc')
    )
    op.create_index(op.f('ix_business_node_permissions_id'), 'business_node_permissions', ['id'], unique=False)
    op.create_index(op.f('ix_business_node_permissions_business_node_id'), 'business_node_permissions', ['business_node_id'], unique=False)
    op.create_index(op.f('ix_business_node_permissions_user_id'), 'business_node_permissions', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_business_node_permissions_user_id'), table_name='business_node_permissions')
    op.drop_index(op.f('ix_business_node_permissions_business_node_id'), table_name='business_node_permissions')
    op.drop_index(op.f('ix_business_node_permissions_id'), table_name='business_node_permissions')
    op.drop_table('business_node_permissions')
