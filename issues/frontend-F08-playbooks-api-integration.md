# F08: 剧本管理 API 对接

## What to build

将剧本管理模块的 Mock API 替换为真实后端 API，包括剧本列表、CRUD、版本管理、diff 对比、回滚。

## Acceptance criteria

- [ ] GET /playbooks 对接真实 API
- [ ] POST /playbooks 对接真实 API
- [ ] GET /playbooks/{id} 对接真实 API
- [ ] PUT /playbooks/{id} 对接真实 API
- [ ] DELETE /playbooks/{id} 对接真实 API
- [ ] GET /playbooks/{id}/versions 对接真实 API
- [ ] GET /playbooks/{id}/versions/{version} 对接真实 API
- [ ] GET /playbooks/{id}/versions/{v1}/diff/{v2} 对接真实 API
- [ ] POST /playbooks/{id}/rollback 对接真实 API
- [ ] 移除 mock.js 中的剧本相关 Mock
- [ ] 测试剧本 CRUD 操作正常
- [ ] 测试版本管理功能正常
- [ ] 测试回滚功能正常

## Blocked by

- frontend-F01, 后端 #9

