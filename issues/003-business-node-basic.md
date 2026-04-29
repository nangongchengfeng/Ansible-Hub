# 业务节点树（基础 CRUD）

## What to build

实现业务节点的基础 CRUD 和树状查询功能，支持创建、编辑、删除业务节点，以及查看树状结构。

## Acceptance criteria

- [ ] BusinessNode 模型和数据库迁移完成
- [ ] GET /business-nodes/tree 实现（获取完整树状结构）
- [ ] GET /business-nodes 实现（平铺列表，支持按 parent_id 筛选，分页）
- [ ] POST /business-nodes 实现（创建业务节点）
- [ ] GET /business-nodes/{id} 实现（获取业务节点详情）
- [ ] PUT /business-nodes/{id} 实现（编辑业务节点）
- [ ] DELETE /business-nodes/{id} 实现（删除业务节点，级联删除子节点和主机）
- [ ] 审计日志记录正常

## Blocked by

- #2

