# F01: 认证模块 API 对接

## What to build

将认证模块的 Mock API 替换为真实后端 API，包括登录、刷新 token、登出、获取当前用户信息。处理 401 未授权自动跳转登录。

## Acceptance criteria

- [ ] POST /auth/login 对接真实 API（移除 Mock）
- [ ] POST /auth/refresh 对接真实 API
- [ ] POST /auth/logout 对接真实 API
- [ ] GET /auth/me 对接真实 API
- [ ] 更新 token 存储和刷新逻辑
- [ ] Axios 拦截器处理 401 自动跳转登录页
- [ ] 移除 mock.js 中的认证相关 Mock
- [ ] 测试登录/登出流程正常
- [ ] 测试 token 过期自动刷新正常

## Blocked by

- 后端 #1

