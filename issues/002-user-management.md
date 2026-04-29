# 用户管理 API

## What to build

实现用户管理的完整 CRUD API，包括创建用户、编辑用户、删除用户、重置密码、角色分配。所有操作仅限 super_admin 访问。

## Acceptance criteria

- [ ] GET /users 实现（用户列表，支持按角色/启用状态筛选，分页）
- [ ] POST /users 实现（创建用户，密码哈希存储）
- [ ] GET /users/{id} 实现（获取用户详情）
- [ ] PUT /users/{id} 实现（编辑用户信息）
- [ ] POST /users/{id}/reset-password 实现（重置用户密码）
- [ ] DELETE /users/{id} 实现（删除用户，不能删除自己）
- [ ] 所有接口权限控制正常（仅 super_admin）
- [ ] 审计日志记录正常

## Blocked by

- #1

