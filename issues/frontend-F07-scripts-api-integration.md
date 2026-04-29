# F07: 脚本管理 API 对接

## What to build

将脚本管理模块的 Mock API 替换为真实后端 API，包括脚本列表、CRUD、版本管理、diff 对比、回滚。

## Acceptance criteria

- [ ] GET /scripts 对接真实 API
- [ ] POST /scripts 对接真实 API
- [ ] GET /scripts/{id} 对接真实 API
- [ ] PUT /scripts/{id} 对接真实 API
- [ ] DELETE /scripts/{id} 对接真实 API
- [ ] GET /scripts/{id}/versions 对接真实 API
- [ ] GET /scripts/{id}/versions/{version} 对接真实 API
- [ ] GET /scripts/{id}/versions/{v1}/diff/{v2} 对接真实 API
- [ ] POST /scripts/{id}/rollback 对接真实 API
- [ ] 移除 mock.js 中的脚本相关 Mock
- [ ] 测试脚本 CRUD 操作正常
- [ ] 测试版本管理功能正常
- [ ] 测试回滚功能正常

## Blocked by

- frontend-F01, 后端 #8

