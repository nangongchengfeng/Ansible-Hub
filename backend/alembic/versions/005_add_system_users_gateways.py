"""add-system-users-gateways

Revision ID: 005
Revises: 004
Create Date: 2026-04-30

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create system_users table
    op.create_table(
        'system_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('auth_type', sa.String(length=20), nullable=False),
        sa.Column('private_key_cipher', sa.Text(), nullable=True),
        sa.Column('password_cipher', sa.Text(), nullable=True),
        sa.Column('become_method', sa.String(length=20), nullable=True),
        sa.Column('become_username', sa.String(length=100), nullable=True),
        sa.Column('become_password_cipher', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_system_users_id'), 'system_users', ['id'], unique=False)

    # Create gateways table
    op.create_table(
        'gateways',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('ip', sa.String(length=45), nullable=False),
        sa.Column('port', sa.Integer(), nullable=False),
        sa.Column('system_user_id', sa.Integer(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['system_user_id'], ['system_users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_gateways_id'), 'gateways', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_gateways_id'), table_name='gateways')
    op.drop_table('gateways')
    op.drop_index(op.f('ix_system_users_id'), table_name='system_users')
    op.drop_table('system_users')
