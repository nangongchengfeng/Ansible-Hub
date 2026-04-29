# F13: 作业历史 API 对接

## What to build

将作业历史模块的 Mock API 替换为真实后端 API，包括历史列表、详情、日志、重做。

## Acceptance criteria

- [ ] GET /job-executions 对接真实 API（历史查询，含权限控制）
- [ ] GET /job-executions/{id} 对接真实 API
- [ ] GET /job-executions/{id}/logs 对接真实 API
- [ ] POST /job-executions/{id}/redo 对接真实 API
- [ ] 移除 mock.js 中的作业历史相关 Mock
- [ ] 测试作业历史列表正常显示
- [ ] 测试权限控制正常（审计员可见所有）
- [ ] 测试重做功能正常

## Blocked by

- frontend-F11, 后端 #16

