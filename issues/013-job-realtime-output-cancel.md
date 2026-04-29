# 作业实时输出与取消

## What to build

实现作业的实时输出（WebSocket）、状态查询、日志查询、取消功能。

## Acceptance criteria

- [ ] WebSocket 端点实现（GET /job-executions/{id}/output）
- [ ] WebSocket 消息格式实现（status_update、task_output、task_complete、job_complete）
- [ ] GET /job-executions 实现（作业列表，支持按状态/类型/创建者/时间范围筛选，搜索，分页）
- [ ] GET /job-executions/{id} 实现（作业详情，包含任务列表）
- [ ] GET /job-executions/{id}/logs 实现（作业完整日志）
- [ ] POST /job-executions/{id}/cancel 实现（取消作业，创建者可取消自己的，super_admin 可取消所有）
- [ ] 审计日志记录正常

## Blocked by

- #12

