# F02: 用户管理 API 对接

## What to build

将用户管理模块的 Mock API 替换为真实后端 API，包括用户列表、创建、编辑、删除、重置密码。

## Acceptance criteria

- [ ] GET /users 对接真实 API
- [ ] POST /users 对接真实 API
- [ ] GET /users/{id} 对接真实 API
- [ ] PUT /users/{id} 对接真实 API
- [ ] POST /users/{id}/reset-password 对接真实 API
- [ ] DELETE /users/{id} 对接真实 API
- [ ] 移除 mock.js 中的用户管理相关 Mock
- [ ] 测试用户 CRUD 操作正常
- [ ] 测试权限控制正常（仅 super_admin 可见）

## Blocked by

- frontend-F01, 后端 #2

