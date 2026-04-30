"""初始化脚本：创建默认管理员用户"""
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import AsyncSessionLocal
from app.services.user import UserService


async def create_default_admin():
    """创建默认管理员"""
    print("正在创建默认管理员用户...")

    async with AsyncSessionLocal() as db:
        # 检查是否已存在管理员
        existing = await UserService.get_user_by_username(db, "admin")
        if existing:
            print("管理员用户已存在，跳过创建")
            return

        # 创建默认管理员
        user = await UserService.create_user(
            db=db,
            username="admin",
            email="admin@example.com",
            password="admin123",
            is_superuser=True,
            is_active=True,
        )
        print(f"管理员创建成功！")
        print(f"用户名: {user.username}")
        print(f"邮箱: {user.email}")
        print(f"密码: admin123")
        print("请登录后立即修改密码！")


if __name__ == "__main__":
    asyncio.run(create_default_admin())
