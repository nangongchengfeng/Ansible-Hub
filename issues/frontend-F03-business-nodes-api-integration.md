# F03: 业务节点 API 对接

## What to build

将业务节点模块的 Mock API 替换为真实后端 API，包括树状查询、CRUD、网关绑定、权限配置、节点主机列表。

## Acceptance criteria

- [ ] GET /business-nodes/tree 对接真实 API
- [ ] GET /business-nodes 对接真实 API
- [ ] POST /business-nodes 对接真实 API
- [ ] GET /business-nodes/{id} 对接真实 API
- [ ] PUT /business-nodes/{id} 对接真实 API
- [ ] DELETE /business-nodes/{id} 对接真实 API
- [ ] PUT /business-nodes/{id}/gateway 对接真实 API
- [ ] GET /business-nodes/{id}/permissions 对接真实 API
- [ ] PUT /business-nodes/{id}/permissions 对接真实 API
- [ ] GET /business-nodes/{id}/hosts 对接真实 API
- [ ] 移除 mock.js 中的业务节点相关 Mock
- [ ] 测试业务节点 CRUD 操作正常
- [ ] 测试权限配置正常
- [ ] 测试权限过滤正常（只显示有权限的节点）

## Blocked by

- frontend-F01, 后端 #3, #4

