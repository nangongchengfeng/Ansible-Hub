# 运营分析统计

## What to build

实现运营分析的各类统计 API，包括作业成功率趋势、失败率 Top 10、最耗时作业、最常执行剧本、自动化覆盖主机比例。

## Acceptance criteria

- [ ] GET /analytics/job-success-rate 实现（作业成功率趋势，支持 period/start_time/end_time）
- [ ] GET /analytics/failed-jobs-top 实现（失败率 Top 10 作业，支持 limit/时间范围）
- [ ] GET /analytics/slowest-jobs 实现（执行最耗时的作业，支持 limit/status/时间范围）
- [ ] GET /analytics/most-used-playbooks 实现（最常被执行的剧本，支持 limit/时间范围）
- [ ] GET /analytics/host-coverage 实现（自动化覆盖主机比例）
- [ ] GET /analytics/dashboard 实现（仪表盘汇总数据）
- [ ] 所有统计接口权限控制正常（仅 super_admin）

## Blocked by

- #16

