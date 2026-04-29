# 连接配置服务

## What to build

实现连接配置解析服务，包含继承逻辑，并提供 API 接口获取主机的完整连接配置。同时实现 Paramiko SSH 连接封装，支持 ProxyJump。

## Acceptance criteria

- [ ] 连接配置解析服务实现（递归继承网关、SSH 端口等）
- [ ] GET /hosts/{id}/connection-config 实现（返回完整连接配置，含继承来源说明）
- [ ] Paramiko SSH 连接封装实现（支持 ProxyJump）
- [ ] 测试连接功能内部实现（暂不暴露 API）

## Blocked by

- #6

