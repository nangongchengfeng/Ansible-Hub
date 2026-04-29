# F11: 临时作业执行 API 对接

## What to build

将临时作业执行模块的 Mock API 替换为真实后端 API，包括提交作业、WebSocket 实时日志、状态查询、日志查询、取消作业、保存为模板。

## Acceptance criteria

- [ ] POST /job-executions 对接真实 API
- [ ] GET /job-executions 对接真实 API
- [ ] GET /job-executions/{id} 对接真实 API
- [ ] GET /job-executions/{id}/logs 对接真实 API
- [ ] POST /job-executions/{id}/cancel 对接真实 API
- [ ] POST /job-executions/{id}/save-template 对接真实 API
- [ ] WebSocket 实时输出对接（GET /job-executions/{id}/output
- [ ] 处理 WebSocket 认证（token 通过 header 或 query parameter）
- [ ] 处理 WebSocket 消息（status_update、task_output、task_complete、job_complete）
- [ ] 移除 mock.js 中的作业执行相关 Mock
- [ ] 测试作业提交正常
- [ ] 测试实时日志显示正常
- [ ] 测试取消作业正常

## Blocked by

- frontend-F06, frontend-F07, frontend-F08, frontend-F09, frontend-F10, 后端 #12, #13

