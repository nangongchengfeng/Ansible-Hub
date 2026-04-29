# 作业模板权限与调度

## What to build

实现作业模板的权限配置和定时调度功能，包括 Cron 表达式配置、调度启用/禁用、Celery Beat 集成。

## Acceptance criteria

- [ ] JobTemplatePermission 模型和数据库迁移完成
- [ ] GET /job-templates/{id}/permissions 实现（获取权限列表）
- [ ] PUT /job-templates/{id}/permissions 实现（覆盖设置权限）
- [ ] GET /job-templates 权限过滤正常（用户只能看到有权限的模板）
- [ ] Celery Beat 配置完成
- [ ] PATCH /job-templates/{id}/schedule 实现（设置 Cron 表达式和启用/禁用调度）
- [ ] 调度逻辑实现（检查上一次执行是否完成，未完成则跳过）
- [ ] 定时任务动态添加/移除实现
- [ ] 审计日志记录正常

## Blocked by

- #14

