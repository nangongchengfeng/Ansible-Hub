"""add-hosts

Revision ID: 006
Revises: 005
Create Date: 2026-04-30

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create hosts table
    op.create_table(
        'hosts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('business_node_id', sa.Integer(), nullable=False),
        sa.Column('ip_internal', sa.String(length=45), nullable=True),
        sa.Column('ip_external', sa.String(length=45), nullable=True),
        sa.Column('ip_preference', sa.String(length=20), nullable=False),
        sa.Column('ssh_port', sa.Integer(), nullable=False),
        sa.Column('cloud_provider', sa.String(length=50), nullable=True),
        sa.Column('system_user_id', sa.Integer(), nullable=True),
        sa.Column('gateway_id', sa.Integer(), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), nullable=False),
        sa.Column('last_connection_status', sa.String(length=20), nullable=True),
        sa.Column('last_connected_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['business_node_id'], ['business_nodes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['gateway_id'], ['gateways.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['system_user_id'], ['system_users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hosts_id'), 'hosts', ['id'], unique=False)
    op.create_index(op.f('ix_hosts_business_node_id'), 'hosts', ['business_node_id'], unique=False)
    op.create_index(op.f('ix_hosts_system_user_id'), 'hosts', ['system_user_id'], unique=False)
    op.create_index(op.f('ix_hosts_gateway_id'), 'hosts', ['gateway_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_hosts_gateway_id'), table_name='hosts')
    op.drop_index(op.f('ix_hosts_system_user_id'), table_name='hosts')
    op.drop_index(op.f('ix_hosts_business_node_id'), table_name='hosts')
    op.drop_index(op.f('ix_hosts_id'), table_name='hosts')
    op.drop_table('hosts')
