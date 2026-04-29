# 临时作业执行（基础）

## What to build

实现临时作业的提交功能，支持 shell 命令、Ansible 模块、剧本、脚本四种类型。包含命令过滤检查、ansible-runner 封装、连接服务集成、审计日志记录。

## Acceptance criteria

- [ ] JobExecution 和 Task 模型和数据库迁移完成
- [ ] POST /job-executions 实现（提交作业，支持四种类型，含命令过滤检查）
- [ ] ansible-runner 封装实现（动态 inventory 生成）
- [ ] Celery 任务定义实现（执行作业）
- [ ] 连接服务集成（通过网关连接）
- [ ] 审计日志记录正常
- [ ] 作业提交时返回 command_check 结果
- [ ] 目标主机支持单个/多个/业务节点选择

## Blocked by

- #7, #8, #9, #10, #11

