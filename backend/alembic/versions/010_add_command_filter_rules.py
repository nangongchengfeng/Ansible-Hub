"""Add command_filter_rules table

Revision ID: 010
Revises: 009
Create Date: 2024-04-30

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '010'
down_revision = '009'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create command_filter_rules table
    op.create_table(
        'command_filter_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False, comment='规则名称'),
        sa.Column('description', sa.Text(), nullable=True, comment='描述'),
        sa.Column('match_type', sa.Enum('contains', 'regex', name='matchtype'), nullable=False, comment='匹配类型'),
        sa.Column('pattern', sa.Text(), nullable=False, comment='匹配模式'),
        sa.Column('action', sa.Enum('block', 'warn', name='actiontype'), nullable=False, comment='动作'),
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
    op.execute('DROP TYPE IF EXISTS matchtype')
    op.execute('DROP TYPE IF EXISTS actiontype')
