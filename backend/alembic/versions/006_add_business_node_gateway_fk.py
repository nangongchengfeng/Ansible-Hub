"""add business node gateway foreign key

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
    # 先检查约束是否存在，不同数据库可能有不同的约束名
    # 这里我们使用 batch_alter_table 来处理
    with op.batch_alter_table('business_nodes', schema=None) as batch_op:
        # 添加 gateway_id 的外键约束
        batch_op.create_foreign_key(
            'fk_business_nodes_gateway_id_gateways',
            'gateways',
            ['gateway_id'],
            ['id'],
            ondelete='SET NULL'
        )


def downgrade() -> None:
    with op.batch_alter_table('business_nodes', schema=None) as batch_op:
        batch_op.drop_constraint('fk_business_nodes_gateway_id_gateways', type_='foreignkey')
