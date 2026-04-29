# F09: 命令过滤规则 API 对接

## What to build

将命令过滤规则模块的 Mock API 替换为真实后端 API，包括规则列表、CRUD、启用/禁用、重新排序、命令检查。

## Acceptance criteria

- [ ] GET /command-filter-rules 对接真实 API
- [ ] POST /command-filter-rules 对接真实 API
- [ ] GET /command-filter-rules/{id} 对接真实 API
- [ ] PUT /command-filter-rules/{id} 对接真实 API
- [ ] PATCH /command-filter-rules/{id}/toggle 对接真实 API
- [ ] PUT /command-filter-rules/reorder 对接真实 API
- [ ] DELETE /command-filter-rules/{id} 对接真实 API
- [ ] POST /command-filter-rules/check 对接真实 API
- [ ] 移除 mock.js 中的命令过滤规则相关 Mock
- [ ] 测试规则 CRUD 操作正常
- [ ] 测试优先级调整正常
- [ ] 测试命令检查功能正常

## Blocked by

- frontend-F01, 后端 #10

