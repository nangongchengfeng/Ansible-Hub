# 审计日志系统

## What to build

实现审计日志系统，包括自动记录关键操作、审计日志查询 API。审计日志不可删除，仅 super_admin 和 auditor 可查看。

## Acceptance criteria

- [ ] AuditLog 模型和数据库迁移完成
- [ ] 审计日志记录中间件/装饰器实现（自动记录创建/更新/删除操作）
- [ ] GET /audit-logs 实现（审计日志列表，支持按用户/操作/资源类型/时间范围筛选，搜索，分页）
- [ ] GET /audit-logs/{id} 实现（获取审计日志详情）
- [ ] 审计日志不可删除保证
- [ ] 权限控制正常（仅 super_admin 和 auditor 可访问）
- [ ] 审计日志包含旧值和新值的对比

## Blocked by

- #2

