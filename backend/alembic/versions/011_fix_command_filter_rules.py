"""Fix command_filter_rules table - use strings instead of enums

Revision ID: 011
Revises: 010
Create Date: 2024-04-30

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '011'
down_revision = '010'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop old table first to avoid enum issues
    op.drop_index(op.f('ix_command_filter_rules_id'), table_name='command_filter_rules')
    op.drop_table('command_filter_rules')

    # Create new table with string columns instead of enums
    op.create_table(
        'command_filter_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False, comment='规则名称'),
        sa.Column('description', sa.Text(), nullable=True, comment='描述'),
        sa.Column('match_type', sa.String(length=20), nullable=False, comment='匹配类型: contains/regex'),
        sa.Column('pattern', sa.Text(), nullable=False, comment='匹配模式'),
        sa.Column('action', sa.String(length=20), nullable=False, comment='动作: block/warn'),
        sa.Column('priority', sa.Integer(), nullable=False, comment='优先级（数字越小优先级越高）'),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, comment='是否启用'),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_command_filter_rules_id'), 'command_filter_rules', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_command_filter_rules_id'), table_name='command_filter_rules')
    op.drop_table('command_filter_rules')
    # Recreate original table with enums if needed
    op.create_table(
        'command_filter_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('match_type', sa.Enum('contains', 'regex', name='matchtype'), nullable=False),
        sa.Column('pattern', sa.Text(), nullable=False),
        sa.Column('action', sa.Enum('block', 'warn', name='actiontype'), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_command_filter_rules_id'), 'command_filter_rules', ['id'], unique=False)
