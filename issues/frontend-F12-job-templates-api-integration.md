# F12: 作业模板 API 对接

## What to build

将作业模板模块的 Mock API 替换为真实后端 API，包括模板列表、CRUD、手动触发、调度配置、权限配置。

## Acceptance criteria

- [ ] GET /job-templates 对接真实 API（含权限过滤）
- [ ] POST /job-templates 对接真实 API
- [ ] GET /job-templates/{id} 对接真实 API
- [ ] PUT /job-templates/{id} 对接真实 API
- [ ] DELETE /job-templates/{id} 对接真实 API
- [ ] POST /job-templates/{id}/execute 对接真实 API
- [ ] PATCH /job-templates/{id}/schedule 对接真实 API
- [ ] GET /job-templates/{id}/permissions 对接真实 API
- [ ] PUT /job-templates/{id}/permissions 对接真实 API
- [ ] 移除 mock.js 中的作业模板相关 Mock
- [ ] 测试模板 CRUD 操作正常
- [ ] 测试手动触发正常
- [ ] 测试 Cron 调度配置正常
- [ ] 测试权限配置正常

## Blocked by

- frontend-F11, 后端 #14, #15

