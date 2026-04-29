# 网关管理

## What to build

实现系统用户和网关的管理功能，包括系统用户（私钥/密码认证，敏感字段加密存储）和网关的 CRUD API。

## Acceptance criteria

- [ ] SystemUser 模型和数据库迁移完成（含 Fernet 加密字段）
- [ ] Gateway 模型和数据库迁移完成
- [ ] GET /system-users 实现（系统用户列表，敏感字段隐藏）
- [ ] POST /system-users 实现（创建系统用户，支持私钥/密码认证）
- [ ] GET /system-users/{id} 实现（获取详情，仅创建者和 super_admin 可查看敏感字段）
- [ ] PUT /system-users/{id} 实现（编辑系统用户）
- [ ] DELETE /system-users/{id} 实现（删除系统用户，被使用时禁止删除）
- [ ] GET /gateways 实现（网关列表）
- [ ] POST /gateways 实现（创建网关）
- [ ] GET /gateways/{id} 实现（获取网关详情）
- [ ] PUT /gateways/{id} 实现（编辑网关）
- [ ] DELETE /gateways/{id} 实现（删除网关，被使用时自动解绑）
- [ ] 审计日志记录正常

## Blocked by

- #2

