# 脚本管理（含版本）

## What to build

实现脚本的完整管理功能，包括 CRUD、版本管理、版本 diff 对比、回滚功能。每次更新创建新版本，回滚也创建新版本。

## Acceptance criteria

- [ ] Script 和 ScriptVersion 模型和数据库迁移完成
- [ ] GET /scripts 实现（脚本列表，显示最新版本号）
- [ ] POST /scripts 实现（创建脚本，同时创建 v1 版本）
- [ ] GET /scripts/{id} 实现（获取脚本详情，包含当前版本内容）
- [ ] PUT /scripts/{id} 实现（更新脚本，创建新版本）
- [ ] DELETE /scripts/{id} 实现（删除脚本，级联删除所有版本）
- [ ] GET /scripts/{id}/versions 实现（历史版本列表，分页）
- [ ] GET /scripts/{id}/versions/{version} 实现（获取指定版本详情）
- [ ] GET /scripts/{id}/versions/{v1}/diff/{v2} 实现（版本 diff 对比）
- [ ] POST /scripts/{id}/rollback 实现（回滚到指定版本，创建新版本）
- [ ] 审计日志记录正常

## Blocked by

- #2

