# 主机管理（基础）

## What to build

实现主机的完整管理功能，包括 CRUD、启用/禁用、移动到其他业务节点、按业务节点查询（含子节点）。

## Acceptance criteria

- [ ] Host 模型和数据库迁移完成
- [ ] GET /hosts 实现（主机列表，支持按业务节点/启用状态筛选，搜索，分页）
- [ ] POST /hosts 实现（创建主机）
- [ ] GET /hosts/{id} 实现（获取主机详情）
- [ ] PUT /hosts/{id} 实现（编辑主机信息）
- [ ] PATCH /hosts/{id}/toggle 实现（启用/禁用主机）
- [ ] POST /hosts/{id}/move 实现（移动主机到其他业务节点）
- [ ] DELETE /hosts/{id} 实现（删除主机）
- [ ] GET /business-nodes/{id}/hosts 支持 include_children 和 only_enabled 参数
- [ ] 主机列表显示最后连接状态
- [ ] 审计日志记录正常

## Blocked by

- #4, #5

