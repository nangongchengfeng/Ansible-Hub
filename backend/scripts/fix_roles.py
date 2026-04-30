"""修复角色数据脚本：将 super_admin 改为 superadmin"""
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import AsyncSessionLocal
from sqlalchemy import update
from app.models.user import User


async def fix_roles():
    """修复角色数据"""
    print("正在修复用户角色数据...")

    async with AsyncSessionLocal() as db:
        # 将 super_admin 更新为 superadmin
        result = await db.execute(
            update(User)
            .where(User.role == "super_admin")
            .values(role="superadmin")
        )
        await db.commit()

        print(f"已修复 {result.rowcount} 条用户角色记录")


if __name__ == "__main__":
    asyncio.run(fix_roles())
