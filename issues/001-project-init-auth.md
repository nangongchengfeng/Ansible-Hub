# 项目初始化与认证系统

## What to build

创建 FastAPI 项目基础结构，实现用户认证系统，包括 JWT 登录、刷新 token、登出和获取当前用户信息。

## Acceptance criteria

- [ ] FastAPI 项目结构创建完成
- [ ] SQLAlchemy（异步引擎）+ Alembic 配置完成
- [ ] Redis + Celery（Worker + Beat）配置完成
- [ ] Fernet 加密配置完成
- [ ] 环境变量管理（pydantic-settings）配置完成
- [ ] 日志系统配置完成
- [ ] CORS 配置完成
- [ ] User 模型和数据库迁移完成
- [ ] POST /auth/login 实现（返回 access_token + refresh_token）
- [ ] POST /auth/refresh 实现（刷新 access_token）
- [ ] POST /auth/logout 实现（将 token 加入黑名单）
- [ ] GET /auth/me 实现（获取当前用户信息）
- [ ] 项目能正常启动
- [ ] 数据库连接正常
- [ ] Redis 连接正常
- [ ] Celery 能正常启动

## Blocked by

None - can start immediately

