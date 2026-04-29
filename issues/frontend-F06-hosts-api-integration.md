# F06: 主机管理 API 对接

## What to build

将主机管理模块的 Mock API 替换为真实后端 API，包括主机列表、CRUD、启用/禁用、移动、连接配置。

## Acceptance criteria

- [ ] GET /hosts 对接真实 API
- [ ] POST /hosts 对接真实 API
- [ ] GET /hosts/{id} 对接真实 API
- [ ] PUT /hosts/{id} 对接真实 API
- [ ] PATCH /hosts/{id}/toggle 对接真实 API
- [ ] POST /hosts/{id}/move 对接真实 API
- [ ] DELETE /hosts/{id} 对接真实 API
- [ ] GET /hosts/{id}/connection-config 对接真实 API
- [ ] 移除 mock.js 中的主机相关 Mock
- [ ] 测试主机 CRUD 操作正常
- [ ] 测试按业务节点筛选正常
- [ ] 测试连接状态显示正常

## Blocked by

- frontend-F03, frontend-F04, frontend-F05, 后端 #6, #7

