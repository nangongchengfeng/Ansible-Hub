# F10: 审计日志 API 对接

## What to build

将审计日志模块的 Mock API 替换为真实后端 API，包括日志列表、详情。

## Acceptance criteria

- [ ] GET /audit-logs 对接真实 API
- [ ] GET /audit-logs/{id} 对接真实 API
- [ ] 移除 mock.js 中的审计日志相关 Mock
- [ ] 测试审计日志列表正常显示
- [ ] 测试权限控制正常（仅 super_admin 和 auditor 可见）

## Blocked by

- frontend-F01, 后端 #11

