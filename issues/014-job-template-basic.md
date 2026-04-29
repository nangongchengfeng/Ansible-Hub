# 作业模板（基础 CRUD）

## What to build

实现作业模板的基础 CRUD 功能，包括创建模板、编辑模板、删除模板、手动触发模板、从历史作业保存为模板。

## Acceptance criteria

- [ ] JobTemplate 模型和数据库迁移完成
- [ ] GET /job-templates 实现（模板列表，含权限过滤，支持按类型/调度状态筛选，搜索，分页）
- [ ] POST /job-templates 实现（创建作业模板）
- [ ] GET /job-templates/{id} 实现（获取模板详情）
- [ ] PUT /job-templates/{id} 实现（编辑模板）
- [ ] DELETE /job-templates/{id} 实现（删除模板）
- [ ] POST /job-templates/{id}/execute 实现（手动触发模板，支持覆盖参数）
- [ ] POST /job-executions/{id}/save-template 实现（从历史作业保存为模板）
- [ ] 审计日志记录正常

## Blocked by

- #13

