# F05: 系统用户 API 对接

## What to build

将系统用户模块的 Mock API 替换为真实后端 API，包括系统用户列表、CRUD，处理敏感字段权限控制。

## Acceptance criteria

- [ ] GET /system-users 对接真实 API
- [ ] POST /system-users 对接真实 API
- [ ] GET /system-users/{id} 对接真实 API
- [ ] PUT /system-users/{id} 对接真实 API
- [ ] DELETE /system-users/{id} 对接真实 API
- [ ] 处理敏感字段（私钥/密码）的权限控制逻辑
- [ ] 移除 mock.js 中的系统用户相关 Mock
- [ ] 测试系统用户 CRUD 操作正常
- [ ] 测试敏感信息权限控制正确（仅创建者和超管可见）

## Blocked by

- frontend-F01, 后端 #5

