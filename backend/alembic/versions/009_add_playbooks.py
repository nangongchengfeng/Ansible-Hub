"""Add playbooks and playbook_versions tables

Revision ID: 009
Revises: 008
Create Date: 2024-04-30

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create playbooks table
    op.create_table(
        'playbooks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False, comment='剧本名称'),
        sa.Column('description', sa.Text(), nullable=True, comment='描述'),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_playbooks_id'), 'playbooks', ['id'], unique=False)

    # Create playbook_versions table
    op.create_table(
        'playbook_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('playbook_id', sa.Integer(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, comment='版本号'),
        sa.Column('content', sa.Text(), nullable=False, comment='剧本内容'),
        sa.Column('change_description', sa.Text(), nullable=True, comment='变更说明'),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['playbook_id'], ['playbooks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('playbook_id', 'version', name='uk_playbook_version')
    )
    op.create_index(op.f('ix_playbook_versions_id'), 'playbook_versions', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_playbook_versions_id'), table_name='playbook_versions')
    op.drop_table('playbook_versions')
    op.drop_index(op.f('ix_playbooks_id'), table_name='playbooks')
    op.drop_table('playbooks')
