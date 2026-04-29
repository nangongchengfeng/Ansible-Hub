# 作业历史与重做

## What to build

实现作业历史查询功能，包括列表、详情、完整日志，以及基于历史作业的重做功能。审计员可以查看所有作业历史。

## Acceptance criteria

- [ ] GET /job-executions 权限控制正常（普通用户只能看到自己的，审计员可以看到所有）
- [ ] GET /job-executions/{id} 权限控制正常
- [ ] GET /job-executions/{id}/logs 返回完整日志
- [ ] POST /job-executions/{id}/redo 实现（基于历史作业创建新作业）
- [ ] 作业历史列表支持筛选、排序、分页
- [ ] 审计日志记录正常

## Blocked by

- #13

