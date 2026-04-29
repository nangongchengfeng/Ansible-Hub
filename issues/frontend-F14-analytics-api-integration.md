# F14: 运营分析 API 对接

## What to build

将运营分析模块的 Mock API 替换为真实后端 API，包括各类统计数据和仪表盘。

## Acceptance criteria

- [ ] GET /analytics/job-success-rate 对接真实 API
- [ ] GET /analytics/failed-jobs-top 对接真实 API
- [ ] GET /analytics/slowest-jobs 对接真实 API
- [ ] GET /analytics/most-used-playbooks 对接真实 API
- [ ] GET /analytics/host-coverage 对接真实 API
- [ ] GET /analytics/dashboard 对接真实 API
- [ ] 移除 mock.js 中的运营分析相关 Mock
- [ ] 测试所有统计数据正常显示
- [ ] 测试时间范围筛选正常
- [ ] 测试权限控制正常（仅 super_admin 可见）

## Blocked by

- frontend-F13, 后端 #17

