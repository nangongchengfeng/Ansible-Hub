# 业务节点权限系统

## What to build

实现业务节点的权限管理系统，包括权限配置、权限检查服务（递归继承），以及树状查询的权限过滤。

## Acceptance criteria

- [ ] BusinessNodePermission 模型和数据库迁移完成
- [ ] GET /business-nodes/{id}/permissions 实现（获取权限列表）
- [ ] PUT /business-nodes/{id}/permissions 实现（覆盖设置权限）
- [ ] PUT /business-nodes/{id}/gateway 实现（绑定网关）
- [ ] 权限检查服务实现（递归继承检查）
- [ ] GET /business-nodes/tree 增加权限过滤（用户只能看到有权限的节点）
- [ ] GET /business-nodes/{id}/hosts 实现（获取节点及其子节点的所有主机）
- [ ] 审计日志记录正常

## Blocked by

- #3

