# 命令过滤规则

## What to build

实现命令过滤规则的完整管理功能，包括 CRUD、启用/禁用、优先级调整、命令匹配检查服务。

## Acceptance criteria

- [ ] CommandFilterRule 模型和数据库迁移完成
- [ ] GET /command-filter-rules 实现（规则列表，支持按启用状态/匹配类型筛选，分页）
- [ ] POST /command-filter-rules 实现（创建规则，支持字符串包含/正则匹配）
- [ ] GET /command-filter-rules/{id} 实现（获取规则详情）
- [ ] PUT /command-filter-rules/{id} 实现（编辑规则）
- [ ] PATCH /command-filter-rules/{id}/toggle 实现（启用/禁用规则）
- [ ] PUT /command-filter-rules/reorder 实现（重新排序规则）
- [ ] DELETE /command-filter-rules/{id} 实现（删除规则）
- [ ] POST /command-filter-rules/check 实现（检查命令是否被过滤，返回匹配规则）
- [ ] 命令匹配检查服务实现（按优先级匹配）
- [ ] 审计日志记录正常

## Blocked by

- #2

