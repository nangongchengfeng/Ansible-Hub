"""Add scripts and script_versions tables

Revision ID: 008
Revises: 007
Create Date: 2024-04-30

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create scripts table
    op.create_table(
        'scripts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False, comment='脚本名称'),
        sa.Column('description', sa.Text(), nullable=True, comment='描述'),
        sa.Column('language', sa.String(length=20), nullable=False, server_default='bash', comment='脚本语言'),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scripts_id'), 'scripts', ['id'], unique=False)

    # Create script_versions table
    op.create_table(
        'script_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('script_id', sa.Integer(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, comment='版本号'),
        sa.Column('content', sa.Text(), nullable=False, comment='脚本内容'),
        sa.Column('change_description', sa.Text(), nullable=True, comment='变更说明'),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['script_id'], ['scripts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('script_id', 'version', name='uk_script_version')
    )
    op.create_index(op.f('ix_script_versions_id'), 'script_versions', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_script_versions_id'), table_name='script_versions')
    op.drop_table('script_versions')
    op.drop_index(op.f('ix_scripts_id'), table_name='scripts')
    op.drop_table('scripts')
