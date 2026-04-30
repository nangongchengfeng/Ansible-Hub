"""add_job_executions_and_tasks

Revision ID: c2201888b61b
Revises: 011
Create Date: 2026-04-30 18:23:04.810110

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c2201888b61b'
down_revision: Union[str, Sequence[str], None] = '011'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('job_executions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('job_type', sa.String(length=20), nullable=False, comment='作业类型: shell/module/playbook/script'),
    sa.Column('shell_command', sa.Text(), nullable=True, comment='Shell命令'),
    sa.Column('module_name', sa.String(length=100), nullable=True, comment='模块名称'),
    sa.Column('module_args', sa.Text(), nullable=True, comment='模块参数'),
    sa.Column('playbook_id', sa.Integer(), nullable=True, comment='剧本ID'),
    sa.Column('playbook_version', sa.Integer(), nullable=True, comment='剧本版本号'),
    sa.Column('script_id', sa.Integer(), nullable=True, comment='脚本ID'),
    sa.Column('script_version', sa.Integer(), nullable=True, comment='脚本版本号'),
    sa.Column('target_type', sa.String(length=20), nullable=False, comment='目标类型: host/hosts/business_node'),
    sa.Column('target_host_ids', sa.JSON(), nullable=True, comment='目标主机ID列表'),
    sa.Column('target_business_node_id', sa.Integer(), nullable=True, comment='目标业务节点ID'),
    sa.Column('status', sa.String(length=20), nullable=False, server_default='pending', comment='状态: pending/running/completed/failed/cancelled'),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=True, comment='开始时间'),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True, comment='完成时间'),
    sa.Column('command_check_passed', sa.Boolean(), nullable=True, comment='命令检查是否通过'),
    sa.Column('command_check_result', sa.JSON(), nullable=True, comment='命令检查详细结果'),
    sa.Column('error_message', sa.Text(), nullable=True, comment='错误信息'),
    sa.Column('created_by', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['playbook_id'], ['playbooks.id'], ),
    sa.ForeignKeyConstraint(['script_id'], ['scripts.id'], ),
    sa.ForeignKeyConstraint(['target_business_node_id'], ['business_nodes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_job_executions_id'), 'job_executions', ['id'], unique=False)
    op.create_table('tasks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('job_execution_id', sa.Integer(), nullable=False),
    sa.Column('host_id', sa.Integer(), nullable=False),
    sa.Column('connection_config', sa.JSON(), nullable=True, comment='连接配置快照'),
    sa.Column('status', sa.String(length=20), nullable=False, server_default='pending', comment='状态: pending/running/completed/failed/skipped'),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=True, comment='开始时间'),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True, comment='完成时间'),
    sa.Column('stdout', sa.Text(), nullable=True, comment='标准输出'),
    sa.Column('stderr', sa.Text(), nullable=True, comment='错误输出'),
    sa.Column('result_json', sa.JSON(), nullable=True, comment='完整结果JSON'),
    sa.Column('exit_code', sa.Integer(), nullable=True, comment='退出码'),
    sa.Column('error_message', sa.Text(), nullable=True, comment='错误信息'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['host_id'], ['hosts.id'], ),
    sa.ForeignKeyConstraint(['job_execution_id'], ['job_executions.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tasks_id'), 'tasks', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_tasks_id'), table_name='tasks')
    op.drop_table('tasks')
    op.drop_index(op.f('ix_job_executions_id'), table_name='job_executions')
    op.drop_table('job_executions')
