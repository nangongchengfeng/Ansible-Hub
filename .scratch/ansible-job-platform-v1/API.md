# Ansible Job Platform API Documentation v1

## 目录
- [数据库设计](#数据库设计)
- [API 契约规范](#api-契约规范)
- [认证 API](#认证-api)
- [用户管理 API](#用户管理-api)
- [业务节点 API](#业务节点-api)
- [主机管理 API](#主机管理-api)
- [系统用户 API](#系统用户-api)
- [网关 API](#网关-api)
- [脚本管理 API](#脚本管理-api)
- [剧本管理 API](#剧本管理-api)
- [命令过滤 API](#命令过滤-api)
- [作业执行 API](#作业执行-api)
- [作业模板 API](#作业模板-api)
- [审计日志 API](#审计日志-api)
- [运营分析 API](#运营分析-api)

---

## 数据库设计

### ER 模型概览

```
User ─┬─< BusinessNodePermission ─>─ BusinessNode
      │
      ├─< JobTemplatePermission ─>─ JobTemplate
      │
      └─< JobExecution
      
Role ──< User

BusinessNode ─┬─< BusinessNode (自引用)
              ├─< Host
              └─< Gateway

Host ─┬─< Task
      └─< SystemUser

SystemUser ──< Gateway (可选)

Script ──< ScriptVersion
Playbook ──< PlaybookVersion

JobTemplate ──< JobExecution
JobExecution ──< Task

CommandFilterRule (独立)
AuditLog (独立)
```

### 表结构详解

#### users (用户表)
```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    email VARCHAR(100) UNIQUE COMMENT '邮箱',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    real_name VARCHAR(50) COMMENT '真实姓名',
    role ENUM('super_admin', 'operator', 'developer', 'auditor') NOT NULL COMMENT '角色',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    last_login_at DATETIME COMMENT '最后登录时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT COMMENT '创建者ID',
    INDEX idx_username (username),
    INDEX idx_role (role)
) COMMENT='用户表';
```

#### business_nodes (业务节点表)
```sql
CREATE TABLE business_nodes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL COMMENT '节点名称',
    description TEXT COMMENT '描述',
    parent_id INT COMMENT '父节点ID',
    sort_order INT DEFAULT 0 COMMENT '排序',
    gateway_id INT COMMENT '绑定的网关ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT NOT NULL COMMENT '创建者ID',
    FOREIGN KEY (parent_id) REFERENCES business_nodes(id) ON DELETE CASCADE,
    FOREIGN KEY (gateway_id) REFERENCES gateways(id) ON DELETE SET NULL,
    INDEX idx_parent_id (parent_id),
    INDEX idx_sort_order (sort_order)
) COMMENT='业务节点表';
```

#### business_node_permissions (业务节点权限表)
```sql
CREATE TABLE business_node_permissions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    business_node_id INT NOT NULL COMMENT '业务节点ID',
    user_id INT NOT NULL COMMENT '用户ID',
    permission_type ENUM('view', 'execute', 'manage') NOT NULL COMMENT '权限类型',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT NOT NULL COMMENT '创建者ID',
    UNIQUE KEY uk_node_user (business_node_id, user_id),
    FOREIGN KEY (business_node_id) REFERENCES business_nodes(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) COMMENT='业务节点权限表';
```

#### hosts (主机表)
```sql
CREATE TABLE hosts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL COMMENT '主机名称',
    business_node_id INT NOT NULL COMMENT '业务节点ID',
    ip_internal VARCHAR(45) COMMENT '内网IP',
    ip_external VARCHAR(45) COMMENT '外网IP',
    ip_preference ENUM('internal', 'external') DEFAULT 'internal' COMMENT 'IP偏好',
    ssh_port INT DEFAULT 22 COMMENT 'SSH端口',
    cloud_provider VARCHAR(50) COMMENT '云厂商',
    system_user_id INT COMMENT '系统用户ID',
    gateway_id INT COMMENT '网关ID（覆盖业务节点设置）',
    is_enabled BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    last_connection_status ENUM('success', 'failed', 'unknown') DEFAULT 'unknown',
    last_connected_at DATETIME COMMENT '最后连接时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT NOT NULL COMMENT '创建者ID',
    FOREIGN KEY (business_node_id) REFERENCES business_nodes(id) ON DELETE CASCADE,
    FOREIGN KEY (system_user_id) REFERENCES system_users(id) ON DELETE SET NULL,
    FOREIGN KEY (gateway_id) REFERENCES gateways(id) ON DELETE SET NULL,
    INDEX idx_business_node_id (business_node_id),
    INDEX idx_is_enabled (is_enabled)
) COMMENT='主机表';
```

#### system_users (系统用户表)
```sql
CREATE TABLE system_users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL COMMENT '名称',
    username VARCHAR(100) NOT NULL COMMENT 'SSH用户名',
    auth_type ENUM('private_key', 'password') NOT NULL COMMENT '认证类型',
    private_key_cipher TEXT COMMENT '加密的私钥',
    password_cipher TEXT COMMENT '加密的密码',
    become_method ENUM('sudo', 'su') DEFAULT 'sudo' COMMENT '提权方式',
    become_username VARCHAR(100) COMMENT '提权用户',
    become_password_cipher TEXT COMMENT '提权密码（加密）',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT NOT NULL COMMENT '创建者ID',
    INDEX idx_name (name)
) COMMENT='系统用户表';
```

#### gateways (网关表)
```sql
CREATE TABLE gateways (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL COMMENT '网关名称',
    ip VARCHAR(45) NOT NULL COMMENT '网关IP',
    port INT DEFAULT 22 COMMENT 'SSH端口',
    system_user_id INT NOT NULL COMMENT '系统用户ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT NOT NULL COMMENT '创建者ID',
    FOREIGN KEY (system_user_id) REFERENCES system_users(id) ON DELETE RESTRICT
) COMMENT='网关表';
```

#### scripts (脚本表)
```sql
CREATE TABLE scripts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL COMMENT '脚本名称',
    description TEXT COMMENT '描述',
    language VARCHAR(20) DEFAULT 'bash' COMMENT '脚本语言',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT NOT NULL COMMENT '创建者ID',
    INDEX idx_name (name)
) COMMENT='脚本表';
```

#### script_versions (脚本版本表)
```sql
CREATE TABLE script_versions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    script_id INT NOT NULL COMMENT '脚本ID',
    version INT NOT NULL COMMENT '版本号',
    content TEXT NOT NULL COMMENT '脚本内容',
    change_description TEXT COMMENT '变更说明',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT NOT NULL COMMENT '创建者ID',
    FOREIGN KEY (script_id) REFERENCES scripts(id) ON DELETE CASCADE,
    UNIQUE KEY uk_script_version (script_id, version),
    INDEX idx_script_id (script_id)
) COMMENT='脚本版本表';
```

#### playbooks (剧本表)
```sql
CREATE TABLE playbooks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL COMMENT '剧本名称',
    description TEXT COMMENT '描述',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT NOT NULL COMMENT '创建者ID',
    INDEX idx_name (name)
) COMMENT='剧本表';
```

#### playbook_versions (剧本版本表)
```sql
CREATE TABLE playbook_versions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    playbook_id INT NOT NULL COMMENT '剧本ID',
    version INT NOT NULL COMMENT '版本号',
    content TEXT NOT NULL COMMENT '剧本内容',
    change_description TEXT COMMENT '变更说明',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT NOT NULL COMMENT '创建者ID',
    FOREIGN KEY (playbook_id) REFERENCES playbooks(id) ON DELETE CASCADE,
    UNIQUE KEY uk_playbook_version (playbook_id, version),
    INDEX idx_playbook_id (playbook_id)
) COMMENT='剧本版本表';
```

#### command_filter_rules (命令过滤规则表)
```sql
CREATE TABLE command_filter_rules (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL COMMENT '规则名称',
    description TEXT COMMENT '描述',
    match_type ENUM('contains', 'regex') NOT NULL COMMENT '匹配类型',
    pattern TEXT NOT NULL COMMENT '匹配模式',
    action ENUM('block', 'warn') DEFAULT 'block' COMMENT '动作',
    priority INT DEFAULT 0 COMMENT '优先级（数字越小优先级越高）',
    is_enabled BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT NOT NULL COMMENT '创建者ID',
    INDEX idx_is_enabled (is_enabled),
    INDEX idx_priority (priority)
) COMMENT='命令过滤规则表';
```

#### job_templates (作业模板表)
```sql
CREATE TABLE job_templates (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL COMMENT '模板名称',
    description TEXT COMMENT '描述',
    job_type ENUM('shell', 'module', 'playbook', 'script') NOT NULL COMMENT '作业类型',
    content TEXT COMMENT '执行内容',
    module_name VARCHAR(100) COMMENT 'Ansible模块名（module类型）',
    module_args TEXT COMMENT 'Ansible模块参数（module类型）',
    playbook_id INT COMMENT '剧本ID（playbook类型）',
    playbook_version INT COMMENT '剧本版本（playbook类型）',
    script_id INT COMMENT '脚本ID（script类型）',
    script_version INT COMMENT '脚本版本（script类型）',
    target_host_ids JSON COMMENT '目标主机ID列表',
    target_business_node_ids JSON COMMENT '目标业务节点ID列表',
    system_user_id INT COMMENT '系统用户ID',
    extra_vars JSON COMMENT '额外变量',
    cron_expression VARCHAR(100) COMMENT 'Cron表达式',
    is_schedule_enabled BOOLEAN DEFAULT FALSE COMMENT '是否启用调度',
    last_scheduled_at DATETIME COMMENT '最后调度时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT NOT NULL COMMENT '创建者ID',
    FOREIGN KEY (playbook_id) REFERENCES playbooks(id) ON DELETE SET NULL,
    FOREIGN KEY (script_id) REFERENCES scripts(id) ON DELETE SET NULL,
    FOREIGN KEY (system_user_id) REFERENCES system_users(id) ON DELETE SET NULL,
    INDEX idx_name (name),
    INDEX idx_is_schedule_enabled (is_schedule_enabled)
) COMMENT='作业模板表';
```

#### job_template_permissions (作业模板权限表)
```sql
CREATE TABLE job_template_permissions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    job_template_id INT NOT NULL COMMENT '作业模板ID',
    user_id INT NOT NULL COMMENT '用户ID',
    permission_type ENUM('view', 'execute', 'manage') NOT NULL COMMENT '权限类型',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT NOT NULL COMMENT '创建者ID',
    UNIQUE KEY uk_template_user (job_template_id, user_id),
    FOREIGN KEY (job_template_id) REFERENCES job_templates(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) COMMENT='作业模板权限表';
```

#### job_executions (作业执行表)
```sql
CREATE TABLE job_executions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) COMMENT '作业名称',
    job_type ENUM('shell', 'module', 'playbook', 'script') NOT NULL COMMENT '作业类型',
    content TEXT COMMENT '执行内容',
    module_name VARCHAR(100) COMMENT 'Ansible模块名',
    module_args TEXT COMMENT 'Ansible模块参数',
    playbook_id INT COMMENT '剧本ID',
    playbook_version INT COMMENT '剧本版本',
    script_id INT COMMENT '脚本ID',
    script_version INT COMMENT '脚本版本',
    target_host_ids JSON NOT NULL COMMENT '目标主机ID列表',
    system_user_id INT COMMENT '系统用户ID',
    extra_vars JSON COMMENT '额外变量',
    job_template_id INT COMMENT '来源模板ID',
    status ENUM('pending', 'running', 'success', 'failed', 'cancelled') DEFAULT 'pending' COMMENT '状态',
    started_at DATETIME COMMENT '开始时间',
    finished_at DATETIME COMMENT '结束时间',
    cancelled_at DATETIME COMMENT '取消时间',
    cancelled_by INT COMMENT '取消者ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT NOT NULL COMMENT '创建者ID',
    FOREIGN KEY (playbook_id) REFERENCES playbooks(id) ON DELETE SET NULL,
    FOREIGN KEY (script_id) REFERENCES scripts(id) ON DELETE SET NULL,
    FOREIGN KEY (job_template_id) REFERENCES job_templates(id) ON DELETE SET NULL,
    FOREIGN KEY (system_user_id) REFERENCES system_users(id) ON DELETE SET NULL,
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    INDEX idx_created_by (created_by)
) COMMENT='作业执行表';
```

#### tasks (任务表)
```sql
CREATE TABLE tasks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    job_execution_id INT NOT NULL COMMENT '作业执行ID',
    host_id INT NOT NULL COMMENT '主机ID',
    host_name VARCHAR(100) NOT NULL COMMENT '主机名快照',
    status ENUM('pending', 'running', 'success', 'failed', 'unreachable') DEFAULT 'pending' COMMENT '状态',
    output TEXT COMMENT '执行输出',
    started_at DATETIME COMMENT '开始时间',
    finished_at DATETIME COMMENT '结束时间',
    FOREIGN KEY (job_execution_id) REFERENCES job_executions(id) ON DELETE CASCADE,
    FOREIGN KEY (host_id) REFERENCES hosts(id) ON DELETE CASCADE,
    INDEX idx_job_execution_id (job_execution_id),
    INDEX idx_host_id (host_id)
) COMMENT='任务表';
```

#### audit_logs (审计日志表)
```sql
CREATE TABLE audit_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT COMMENT '用户ID',
    username VARCHAR(50) COMMENT '用户名快照',
    action VARCHAR(50) NOT NULL COMMENT '操作类型',
    resource_type VARCHAR(50) COMMENT '资源类型',
    resource_id INT COMMENT '资源ID',
    resource_name VARCHAR(255) COMMENT '资源名称',
    old_values JSON COMMENT '旧值',
    new_values JSON COMMENT '新值',
    ip_address VARCHAR(45) COMMENT 'IP地址',
    user_agent TEXT COMMENT 'User Agent',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_action (action),
    INDEX idx_resource_type (resource_type),
    INDEX idx_created_at (created_at)
) COMMENT='审计日志表';
```

---

## API 契约规范

### 基础信息

- **Base URL**: `https://api.example.com/v1`
- **协议**: HTTPS
- **数据格式**: JSON
- **字符编码**: UTF-8

### 认证方式

使用 **JWT (JSON Web Token)** 认证：

1. 登录获取 access token 和 refresh token
2. 请求时在 Header 中携带：
   ```
   Authorization: Bearer {access_token}
   ```
3. Access token 有效期：2小时
4. Refresh token 有效期：7天
5. 使用 refresh token 刷新 access token

### 错误码规范

| HTTP 状态码 | 错误码 | 说明 |
|------------|-------|------|
| 200 | - | 成功 |
| 400 | BAD_REQUEST | 请求参数错误 |
| 401 | UNAUTHORIZED | 未登录或 token 无效 |
| 403 | FORBIDDEN | 无权限访问 |
| 404 | NOT_FOUND | 资源不存在 |
| 409 | CONFLICT | 资源冲突（如已存在） |
| 422 | VALIDATION_ERROR | 数据验证失败 |
| 429 | TOO_MANY_REQUESTS | 请求过于频繁 |
| 500 | INTERNAL_ERROR | 服务器内部错误 |

### 统一响应格式

#### 成功响应
```json
{
    "success": true,
    "data": {},
    "message": "操作成功"
}
```

#### 错误响应
```json
{
    "success": false,
    "error": {
        "code": "BAD_REQUEST",
        "message": "参数错误",
        "details": [
            {
                "field": "name",
                "message": "名称不能为空"
            }
        ]
    }
}
```

#### 分页响应
```json
{
    "success": true,
    "data": {
        "items": [],
        "total": 100,
        "page": 1,
        "page_size": 20,
        "total_pages": 5
    },
    "message": "查询成功"
}
```

### 作业状态流转

```
pending
   │
   ├─→ running
   │     │
   │     ├─→ success
   │     ├─→ failed
   │     └─→ cancelled (用户取消)
   │
   └─→ cancelled (提交后立即取消)
```

### 任务状态流转

```
pending
   │
   ├─→ running
   │     │
   │     ├─→ success
   │     ├─→ failed
   │     └─→ unreachable
   │
   └─→ (如果作业被取消，任务不执行)
```

### 分页参数

所有列表 API 支持以下分页参数：

| 参数 | 类型 | 必填 | 默认 | 说明 |
|-----|------|------|------|------|
| page | int | 否 | 1 | 页码 |
| page_size | int | 否 | 20 | 每页数量，最大 100 |
| ordering | string | 否 | -created_at | 排序字段，前缀 `-` 表示降序 |

---

## 认证 API

### POST /auth/login
用户登录

**请求体：**
```json
{
    "username": "string",
    "password": "string"
}
```

**响应 (200)：**
```json
{
    "success": true,
    "data": {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "Bearer",
        "expires_in": 7200,
        "user": {
            "id": 1,
            "username": "admin",
            "real_name": "超级管理员",
            "email": "admin@example.com",
            "role": "super_admin",
            "is_active": true
        }
    }
}
```

### POST /auth/refresh
刷新 Access Token

**请求体：**
```json
{
    "refresh_token": "string"
}
```

**响应 (200)：**
```json
{
    "success": true,
    "data": {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "Bearer",
        "expires_in": 7200
    }
}
```

### POST /auth/logout
登出（将 token 加入黑名单）

**请求头：**
```
Authorization: Bearer {access_token}
```

**响应 (200)：**
```json
{
    "success": true,
    "message": "登出成功"
}
```

### GET /auth/me
获取当前用户信息

**请求头：**
```
Authorization: Bearer {access_token}
```

**响应 (200)：**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "username": "admin",
        "real_name": "超级管理员",
        "email": "admin@example.com",
        "role": "super_admin",
        "is_active": true,
        "last_login_at": "2024-01-01T12:00:00Z",
        "created_at": "2024-01-01T12:00:00Z"
    }
}
```

---

## 用户管理 API

> **权限要求**：super_admin

### GET /users
获取用户列表

**查询参数：**
- `role` (可选): 按角色筛选
- `is_active` (可选): 按启用状态筛选
- `search` (可选): 搜索用户名/真实姓名
- 分页参数

**响应 (200)：**
```json
{
    "success": true,
    "data": {
        "items": [
            {
                "id": 1,
                "username": "admin",
                "real_name": "超级管理员",
                "email": "admin@example.com",
                "role": "super_admin",
                "is_active": true,
                "last_login_at": "2024-01-01T12:00:00Z",
                "created_at": "2024-01-01T12:00:00Z",
                "created_by": null
            }
        ],
        "total": 10,
        "page": 1,
        "page_size": 20,
        "total_pages": 1
    }
}
```

### POST /users
创建用户

**请求体：**
```json
{
    "username": "string (必填, 3-50字符)",
    "password": "string (必填, 最少6字符)",
    "email": "string (可选, 邮箱格式)",
    "real_name": "string (可选)",
    "role": "super_admin|operator|developer|auditor (必填)"
}
```

**响应 (201)：**
```json
{
    "success": true,
    "data": {
        "id": 2,
        "username": "operator1",
        "real_name": "运维人员",
        "email": "operator1@example.com",
        "role": "operator",
        "is_active": true,
        "created_at": "2024-01-01T12:00:00Z"
    },
    "message": "用户创建成功"
}
```

### GET /users/{id}
获取用户详情

**路径参数：**
- `id`: 用户ID

**响应 (200)：**
```json
{
    "success": true,
    "data": {
        "id": 2,
        "username": "operator1",
        "real_name": "运维人员",
        "email": "operator1@example.com",
        "role": "operator",
        "is_active": true,
        "last_login_at": null,
        "created_at": "2024-01-01T12:00:00Z",
        "created_by": 1
    }
}
```

### PUT /users/{id}
更新用户信息

**路径参数：**
- `id`: 用户ID

**请求体：**
```json
{
    "email": "string (可选)",
    "real_name": "string (可选)",
    "role": "super_admin|operator|developer|auditor (可选)",
    "is_active": "boolean (可选)"
}
```

**响应 (200)：**
```json
{
    "success": true,
    "data": {
        "id": 2,
        "username": "operator1",
        "real_name": "运维人员",
        "email": "new@example.com",
        "role": "operator",
        "is_active": true,
        "updated_at": "2024-01-01T12:00:00Z"
    },
    "message": "用户更新成功"
}
```

### POST /users/{id}/reset-password
重置用户密码

**路径参数：**
- `id`: 用户ID

**请求体：**
```json
{
    "new_password": "string (必填, 最少6字符)"
}
```

**响应 (200)：**
```json
{
    "success": true,
    "message": "密码重置成功"
}
```

### DELETE /users/{id}
删除用户

**路径参数：**
- `id`: 用户ID（不能删除自己）

**响应 (200)：**
```json
{
    "success": true,
    "message": "用户删除成功"
}
```

---

## 业务节点 API

### GET /business-nodes/tree
获取业务节点树（含权限过滤）

**响应 (200)：**
```json
{
    "success": true,
    "data": [
        {
            "id": 1,
            "name": "生产环境",
            "description": "生产环境主机",
            "parent_id": null,
            "sort_order": 1,
            "gateway_id": 1,
            "gateway": {
                "id": 1,
                "name": "生产网关"
            },
            "children": [
                {
                    "id": 2,
                    "name": "Web服务",
                    "description": "Web服务器群",
                    "parent_id": 1,
                    "sort_order": 1,
                    "gateway_id": null,
                    "children": []
                }
            ],
            "permissions": [
                {
                    "user_id": 2,
                    "permission_type": "execute"
                }
            ]
        }
    ]
}
```

### GET /business-nodes
获取业务节点列表（平铺）

**查询参数：**
- `parent_id` (可选): 父节点ID
- 分页参数

**响应 (200)：** 分页格式

### POST /business-nodes
创建业务节点

**请求体：**
```json
{
    "name": "string (必填, 最多100字符)",
    "description": "string (可选)",
    "parent_id": "int (可选, null表示根节点)",
    "sort_order": "int (可选, 默认0)",
    "gateway_id": "int (可选)"
}
```

**响应 (201)：**
```json
{
    "success": true,
    "data": {
        "id": 3,
        "name": "数据库服务",
        "description": "MySQL集群",
        "parent_id": 1,
        "sort_order": 2,
        "gateway_id": null,
        "created_at": "2024-01-01T12:00:00Z"
    },
    "message": "业务节点创建成功"
}
```

### GET /business-nodes/{id}
获取业务节点详情

**路径参数：**
- `id`: 业务节点ID

**响应 (200)：**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "name": "生产环境",
        "description": "生产环境主机",
        "parent_id": null,
        "sort_order": 1,
        "gateway_id": 1,
        "gateway": {
            "id": 1,
            "name": "生产网关",
            "ip": "192.168.1.100"
        },
        "created_at": "2024-01-01T12:00:00Z",
        "updated_at": "2024-01-01T12:00:00Z",
        "created_by": {
            "id": 1,
            "username": "admin"
        },
        "permissions": [
            {
                "id": 1,
                "user_id": 2,
                "user": {
                    "id": 2,
                    "username": "operator1",
                    "real_name": "运维人员"
                },
                "permission_type": "execute"
            }
        ]
    }
}
```

### PUT /business-nodes/{id}
更新业务节点

**路径参数：**
- `id`: 业务节点ID

**请求体：**
```json
{
    "name": "string (可选)",
    "description": "string (可选)",
    "parent_id": "int (可选)",
    "sort_order": "int (可选)",
    "gateway_id": "int (可选, null解绑)"
}
```

**响应 (200)：**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "name": "生产环境（更新）",
        "updated_at": "2024-01-01T12:00:00Z"
    },
    "message": "业务节点更新成功"
}
```

### DELETE /business-nodes/{id}
删除业务节点（级联删除子节点和主机）

**路径参数：**
- `id`: 业务节点ID

**响应 (200)：**
```json
{
    "success": true,
    "message": "业务节点删除成功"
}
```

### PUT /business-nodes/{id}/gateway
绑定网关

**路径参数：**
- `id`: 业务节点ID

**请求体：**
```json
{
    "gateway_id": "int (必填, null解绑)"
}
```

**响应 (200)：**
```json
{
    "success": true,
    "message": "网关绑定成功"
}
```

### GET /business-nodes/{id}/permissions
获取业务节点权限列表

**路径参数：**
- `id`: 业务节点ID

**响应 (200)：**
```json
{
    "success": true,
    "data": [
        {
            "id": 1,
            "user_id": 2,
            "user": {
                "id": 2,
                "username": "operator1",
                "real_name": "运维人员"
            },
            "permission_type": "execute",
            "created_at": "2024-01-01T12:00:00Z"
        }
    ]
}
```

### PUT /business-nodes/{id}/permissions
设置业务节点权限（覆盖）

**路径参数：**
- `id`: 业务节点ID

**请求体：**
```json
{
    "permissions": [
        {
            "user_id": 2,
            "permission_type": "execute"
        },
        {
            "user_id": 3,
            "permission_type": "view"
        }
    ]
}
```

**响应 (200)：**
```json
{
    "success": true,
    "message": "权限设置成功"
}
```

### GET /business-nodes/{id}/hosts
获取业务节点及其子节点的所有主机

**路径参数：**
- `id`: 业务节点ID

**查询参数：**
- `include_children`: boolean (默认 true, 是否包含子节点)
- `only_enabled`: boolean (默认 true, 仅显示启用的主机)
- 分页参数

**响应 (200)：** 分页格式

---

## 主机管理 API

### GET /hosts
获取主机列表

**查询参数：**
- `business_node_id` (可选): 按业务节点筛选
- `is_enabled` (可选): 按启用状态筛选
- `search` (可选): 搜索主机名/IP
- 分页参数

**响应 (200)：** 分页格式，items 数据结构如下：
```json
{
    "id": 1,
    "name": "web-server-01",
    "business_node_id": 2,
    "business_node": {
        "id": 2,
        "name": "Web服务"
    },
    "ip_internal": "192.168.1.10",
    "ip_external": "203.0.113.10",
    "ip_preference": "internal",
    "ssh_port": 22,
    "cloud_provider": "aliyun",
    "system_user_id": 1,
    "system_user": {
        "id": 1,
        "name": "root"
    },
    "gateway_id": null,
    "is_enabled": true,
    "last_connection_status": "success",
    "last_connected_at": "2024-01-01T12:00:00Z",
    "created_at": "2024-01-01T12:00:00Z"
}
```

### POST /hosts
创建主机

**请求体：**
```json
{
    "name": "string (必填, 最多100字符)",
    "business_node_id": "int (必填)",
    "ip_internal": "string (可选, IPv4/IPv6)",
    "ip_external": "string (可选, IPv4/IPv6)",
    "ip_preference": "internal|external (可选, 默认internal)",
    "ssh_port": "int (可选, 默认22)",
    "cloud_provider": "string (可选)",
    "system_user_id": "int (可选)",
    "gateway_id": "int (可选, 覆盖业务节点设置)"
}
```

**响应 (201)：**
```json
{
    "success": true,
    "data": {
        "id": 5,
        "name": "web-server-05",
        "business_node_id": 2,
        "is_enabled": true,
        "created_at": "2024-01-01T12:00:00Z"
    },
    "message": "主机创建成功"
}
```

### GET /hosts/{id}
获取主机详情

**路径参数：**
- `id`: 主机ID

**响应 (200)：**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "name": "web-server-01",
        "business_node_id": 2,
        "business_node": {
            "id": 2,
            "name": "Web服务",
            "path": "/生产环境/Web服务"
        },
        "ip_internal": "192.168.1.10",
        "ip_external": "203.0.113.10",
        "ip_preference": "internal",
        "ssh_port": 22,
        "cloud_provider": "aliyun",
        "system_user_id": 1,
        "system_user": {
            "id": 1,
            "name": "root",
            "username": "root"
        },
        "gateway_id": null,
        "gateway": null,
        "is_enabled": true,
        "last_connection_status": "success",
        "last_connected_at": "2024-01-01T12:00:00Z",
        "created_at": "2024-01-01T12:00:00Z",
        "updated_at": "2024-01-01T12:00:00Z",
        "created_by": {
            "id": 1,
            "username": "admin"
        },
        "resolved_connection": {
            "ip": "192.168.1.10",
            "ssh_port": 22,
            "system_user_id": 1,
            "gateway_id": 1,
            "gateway_source": "business_node"
        }
    }
}
```

### PUT /hosts/{id}
更新主机信息

**路径参数：**
- `id`: 主机ID

**请求体：**
```json
{
    "name": "string (可选)",
    "business_node_id": "int (可选)",
    "ip_internal": "string (可选)",
    "ip_external": "string (可选)",
    "ip_preference": "internal|external (可选)",
    "ssh_port": "int (可选)",
    "cloud_provider": "string (可选)",
    "system_user_id": "int (可选, null解绑)",
    "gateway_id": "int (可选, null解绑)"
}
```

**响应 (200)：**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "name": "web-server-01",
        "updated_at": "2024-01-01T12:00:00Z"
    },
    "message": "主机更新成功"
}
```

### PATCH /hosts/{id}/toggle
启用/禁用主机

**路径参数：**
- `id`: 主机ID

**响应 (200)：**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "is_enabled": false
    },
    "message": "主机状态更新成功"
}
```

### POST /hosts/{id}/move
移动主机到其他业务节点

**路径参数：**
- `id`: 主机ID

**请求体：**
```json
{
    "target_business_node_id": "int (必填)"
}
```

**响应 (200)：**
```json
{
    "success": true,
    "message": "主机移动成功"
}
```

### DELETE /hosts/{id}
删除主机

**路径参数：**
- `id`: 主机ID

**响应 (200)：**
```json
{
    "success": true,
    "message": "主机删除成功"
}
```

### GET /hosts/{id}/connection-config
获取主机的完整连接配置（含继承）

**路径参数：**
- `id`: 主机ID

**响应 (200)：**
```json
{
    "success": true,
    "data": {
        "host_id": 1,
        "host_name": "web-server-01",
        "ip": "192.168.1.10",
        "ssh_port": 22,
        "system_user_id": 1,
        "system_user": {
            "id": 1,
            "name": "root",
            "username": "root",
            "auth_type": "private_key"
        },
        "gateway": {
            "id": 1,
            "name": "生产网关",
            "ip": "192.168.1.100",
            "port": 22,
            "system_user_id": 1,
            "source": "business_node"
        },
        "resolution_path": [
            {
                "level": "host",
                "field": "ip",
                "value": "192.168.1.10"
            },
            {
                "level": "business_node",
                "field": "gateway_id",
                "value": 1
            }
        ]
    }
}
```

---

## 系统用户 API

### GET /system-users
获取系统用户列表

**查询参数：**
- `auth_type` (可选): 按认证类型筛选
- `search` (可选): 搜索名称
- 分页参数

**响应 (200)：** 分页格式，items 数据结构如下：
```json
{
    "id": 1,
    "name": "root",
    "username": "root",
    "auth_type": "private_key",
    "become_method": "sudo",
    "become_username": null,
    "can_view_secret": true,
    "created_at": "2024-01-01T12:00:00Z",
    "created_by": 1
}
```

### POST /system-users
创建系统用户

**请求体（私钥认证）：**
```json
{
    "name": "string (必填, 最多100字符)",
    "username": "string (必填, SSH用户名)",
    "auth_type": "private_key",
    "private_key": "string (必填, 私钥内容)",
    "become_method": "sudo|su (可选, 默认sudo)",
    "become_username": "string (可选)",
    "become_password": "string (可选)"
}
```

**请求体（密码认证）：**
```json
{
    "name": "string (必填)",
    "username": "string (必填)",
    "auth_type": "password",
    "password": "string (必填)",
    "become_method": "sudo|su (可选)",
    "become_username": "string (可选)",
    "become_password": "string (可选)"
}
```

**响应 (201)：**
```json
{
    "success": true,
    "data": {
        "id": 2,
        "name": "deploy",
        "username": "deploy",
        "auth_type": "private_key",
        "can_view_secret": true,
        "created_at": "2024-01-01T12:00:00Z"
    },
    "message": "系统用户创建成功"
}
```

### GET /system-users/{id}
获取系统用户详情

**路径参数：**
- `id`: 系统用户ID

**响应 (200)：**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "name": "root",
        "username": "root",
        "auth_type": "private_key",
        "private_key": "-----BEGIN RSA PRIVATE KEY-----\n...",
        "password": null,
        "become_method": "sudo",
        "become_username": null,
        "become_password": null,
        "can_view_secret": true,
        "created_at": "2024-01-01T12:00:00Z",
        "created_by": {
            "id": 1,
            "username": "admin"
        }
    }
}
```
> **注意**：`private_key`、`password`、`become_password` 仅对创建者和 super_admin 可见

### PUT /system-users/{id}
更新系统用户

**路径参数：**
- `id`: 系统用户ID

**请求体：**
```json
{
    "name": "string (可选)",
    "username": "string (可选)",
    "private_key": "string (可选, 更新私钥)",
    "password": "string (可选, 更新密码)",
    "become_method": "sudo|su (可选)",
    "become_username": "string (可选)",
    "become_password": "string (可选)"
}
```

**响应 (200)：**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "name": "root",
        "updated_at": "2024-01-01T12:00:00Z"
    },
    "message": "系统用户更新成功"
}
```

### DELETE /system-users/{id}
删除系统用户

**路径参数：**
- `id`: 系统用户ID（被主机/网关使用时禁止删除）

**响应 (200)：**
```json
{
    "success": true,
    "message": "系统用户删除成功"
}
```

---

## 网关 API

### GET /gateways
获取网关列表

**查询参数：**
- `search` (可选): 搜索名称/IP
- 分页参数

**响应 (200)：** 分页格式，items 数据结构如下：
```json
{
    "id": 1,
    "name": "生产网关",
    "ip": "192.168.1.100",
    "port": 22,
    "system_user_id": 1,
    "system_user": {
        "id": 1,
        "name": "root"
    },
    "created_at": "2024-01-01T12:00:00Z"
}
```

### POST /gateways
创建网关

**请求体：**
```json
{
    "name": "string (必填, 最多100字符)",
    "ip": "string (必填, IPv4/IPv6)",
    "port": "int (可选, 默认22)",
    "system_user_id": "int (必填)"
}
```

**响应 (201)：**
```json
{
    "success": true,
    "data": {
        "id": 2,
        "name": "测试网关",
        "ip": "192.168.2.100",
        "port": 22,
        "system_user_id": 1,
        "created_at": "2024-01-01T12:00:00Z"
    },
    "message": "网关创建成功"
}
```

### GET /gateways/{id}
获取网关详情

**路径参数：**
- `id`: 网关ID

**响应 (200)：**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "name": "生产网关",
        "ip": "192.168.1.100",
        "port": 22,
        "system_user_id": 1,
        "system_user": {
            "id": 1,
            "name": "root",
            "username": "root"
        },
        "created_at": "2024-01-01T12:00:00Z",
        "created_by": {
            "id": 1,
            "username": "admin"
        }
    }
}
```

### PUT /gateways/{id}
更新网关

**路径参数：**
- `id`: 网关ID

**请求体：**
```json
{
    "name": "string (可选)",
    "ip": "string (可选)",
    "port": "int (可选)",
    "system_user_id": "int (可选)"
}
```

**响应 (200)：**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "name": "生产网关",
        "updated_at": "2024-01-01T12:00:00Z"
    },
    "message": "网关更新成功"
}
```

### DELETE /gateways/{id}
删除网关

**路径参数：**
- `id`: 网关ID（被业务节点/主机使用时会自动解绑）

**响应 (200)：**
```json
{
    "success": true,
    "message": "网关删除成功"
}
```

---

## 脚本管理 API

### GET /scripts
获取脚本列表

**查询参数：**
- `language` (可选): 按语言筛选
- `search` (可选): 搜索名称/描述
- 分页参数

**响应 (200)：** 分页格式，items 数据结构如下：
```json
{
    "id": 1,
    "name": "健康检查脚本",
    "description": "检查系统健康状态",
    "language": "bash",
    "latest_version": 3,
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-02T12:00:00Z",
    "created_by": {
        "id": 1,
        "username": "admin"
    }
}
```

### POST /scripts
创建脚本

**请求体：**
```json
{
    "name": "string (必填, 最多100字符)",
    "description": "string (可选)",
    "language": "bash|python|ruby (可选, 默认bash)",
    "content": "string (必填, 脚本内容)",
    "change_description": "string (可选, 变更说明)"
}
```

**响应 (201)：**
```json
{
    "success": true,
    "data": {
        "id": 2,
        "name": "备份脚本",
        "description": "数据库备份脚本",
        "language": "bash",
        "latest_version": 1,
        "created_at": "2024-01-01T12:00:00Z"
    },
    "message": "脚本创建成功"
}
```

### GET /scripts/{id}
获取脚本详情（最新版本）

**路径参数：**
- `id`: 脚本ID

**响应 (200)：**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "name": "健康检查脚本",
        "description": "检查系统健康状态",
        "language": "bash",
        "latest_version": 3,
        "current_content": "#!/bin/bash\necho \"Health check...\"",
        "current_version": {
            "id": 5,
            "version": 3,
            "content": "#!/bin/bash\necho \"Health check...\"",
            "change_description": "优化检查逻辑",
            "created_at": "2024-01-02T12:00:00Z",
            "created_by": {
                "id": 1,
                "username": "admin"
            }
        },
        "created_at": "2024-01-01T12:00:00Z",
        "updated_at": "2024-01-02T12:00:00Z"
    }
}
```

### PUT /scripts/{id}
更新脚本（创建新版本）

**路径参数：**
- `id`: 脚本ID

**请求体：**
```json
{
    "name": "string (可选)",
    "description": "string (可选)",
    "content": "string (必填, 更新内容)",
    "change_description": "string (必填, 变更说明)"
}
```

**响应 (200)：**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "name": "健康检查脚本",
        "latest_version": 4,
        "updated_at": "2024-01-03T12:00:00Z"
    },
    "message": "脚本更新成功"
}
```

### DELETE /scripts/{id}
删除脚本（级联删除所有版本）

**路径参数：**
- `id`: 脚本ID

**响应 (200)：**
```json
{
    "success": true,
    "message": "脚本删除成功"
}
```

### GET /scripts/{id}/versions
获取脚本版本列表

**路径参数：**
- `id`: 脚本ID

**查询参数：**
- 分页参数

**响应 (200)：**
```json
{
    "success": true,
    "data": {
        "items": [
            {
                "id": 5,
                "version": 3,
                "change_description": "优化检查逻辑",
                "created_at": "2024-01-02T12:00:00Z",
                "created_by": {
                    "id": 1,
                    "username": "admin"
                }
            },
            {
                "id": 4,
                "version": 2,
                "change_description": "添加磁盘检查",
                "created_at": "2024-01-01T14:00:00Z",
                "created_by": {
                    "id": 1,
                    "username": "admin"
                }
            }
        ],
        "total": 3,
        "page": 1,
        "page_size": 20,
        "total_pages": 1
    }
}
```

### GET /scripts/{id}/versions/{version}
获取脚本指定版本详情

**路径参数：**
- `id`: 脚本ID
- `version`: 版本号

**响应 (200)：**
```json
{
    "success": true,
    "data": {
        "id": 4,
        "script_id": 1,
        "version": 2,
        "content": "#!/bin/bash\necho \"Check...\"",
        "change_description": "添加磁盘检查",
        "created_at": "2024-01-01T14:00:00Z",
        "created_by": {
            "id": 1,
            "username": "admin"
        }
    }
}
```

### GET /scripts/{id}/versions/{v1}/diff/{v2}
对比两个版本的差异

**路径参数：**
- `id`: 脚本ID
- `v1`: 版本1
- `v2`: 版本2

**响应 (200)：**
```json
{
    "success": true,
    "data": {
        "version1": 2,
        "version2": 3,
        "diff": "--- version 2\n+++ version 3\n@@ -1,2 +1,3 @@\n #!/bin/bash\n-echo \"Check...\"\n+echo \"Health check...\"\n+df -h"
    }
}
```

### POST /scripts/{id}/rollback
回滚到指定版本（创建新版本）

**路径参数：**
- `id`: 脚本ID

**请求体：**
```json
{
    "target_version": "int (必填, 要回滚到的版本号)"
}
```

**响应 (200)：**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "latest_version": 4,
        "rolled_back_from": 3,
        "rolled_back_to": 2
    },
    "message": "脚本回滚成功"
}
```

---

## 剧本管理 API

> **剧本 API 与脚本 API 结构完全相同，仅路径不同**

### GET /playbooks
获取剧本列表

### POST /playbooks
创建剧本

### GET /playbooks/{id}
获取剧本详情

### PUT /playbooks/{id}
更新剧本

### DELETE /playbooks/{id}
删除剧本

### GET /playbooks/{id}/versions
获取剧本版本列表

### GET /playbooks/{id}/versions/{version}
获取剧本指定版本

### GET /playbooks/{id}/versions/{v1}/diff/{v2}
版本对比

### POST /playbooks/{id}/rollback
回滚版本

---

## 命令过滤 API

### GET /command-filter-rules
获取命令过滤规则列表

**查询参数：**
- `is_enabled` (可选): 按启用状态筛选
- `match_type` (可选): 按匹配类型筛选
- 分页参数

**响应 (200)：** 分页格式，items 数据结构如下：
```json
{
    "id": 1,
    "name": "禁止 rm -rf",
    "description": "禁止递归删除根目录",
    "match_type": "contains",
    "pattern": "rm -rf /",
    "action": "block",
    "priority": 1,
    "is_enabled": true,
    "created_at": "2024-01-01T12:00:00Z"
}
```

### POST /command-filter-rules
创建命令过滤规则

**请求体：**
```json
{
    "name": "string (必填, 最多100字符)",
    "description": "string (可选)",
    "match_type": "contains|regex (必填)",
    "pattern": "string (必填, 匹配模式)",
    "action": "block|warn (可选, 默认block)",
    "priority": "int (可选, 默认0, 数字越小优先级越高)"
}
```

**响应 (201)：**
```json
{
    "success": true,
    "data": {
        "id": 2,
        "name": "禁止格式化",
        "match_type": "regex",
        "pattern": "mkfs\\.[a-z0-9]+",
        "priority": 2,
        "created_at": "2024-01-01T12:00:00Z"
    },
    "message": "规则创建成功"
}
```

### GET /command-filter-rules/{id}
获取规则详情

**路径参数：**
- `id`: 规则ID

**响应 (200)：**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "name": "禁止 rm -rf",
        "description": "禁止递归删除根目录",
        "match_type": "contains",
        "pattern": "rm -rf /",
        "action": "block",
        "priority": 1,
        "is_enabled": true,
        "created_at": "2024-01-01T12:00:00Z",
        "created_by": {
            "id": 1,
            "username": "admin"
        }
    }
}
```

### PUT /command-filter-rules/{id}
更新规则

**路径参数：**
- `id`: 规则ID

**请求体：**
```json
{
    "name": "string (可选)",
    "description": "string (可选)",
    "match_type": "contains|regex (可选)",
    "pattern": "string (可选)",
    "action": "block|warn (可选)",
    "priority": "int (可选)"
}
```

**响应 (200)：**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "name": "禁止 rm -rf",
        "updated_at": "2024-01-01T12:00:00Z"
    },
    "message": "规则更新成功"
}
```

### PATCH /command-filter-rules/{id}/toggle
启用/禁用规则

**路径参数：**
- `id`: 规则ID

**响应 (200)：**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "is_enabled": false
    },
    "message": "规则状态更新成功"
}
```

### PUT /command-filter-rules/reorder
重新排序规则

**请求体：**
```json
{
    "order": [1, 3, 2, 4]
}
```

**响应 (200)：**
```json
{
    "success": true,
    "message": "规则排序更新成功"
}
```

### DELETE /command-filter-rules/{id}
删除规则

**路径参数：**
- `id`: 规则ID

**响应 (200)：**
```json
{
    "success": true,
    "message": "规则删除成功"
}
```

### POST /command-filter-rules/check
检查命令是否被过滤

**请求体：**
```json
{
    "command": "string (必填, 要检查的命令)"
}
```

**响应 (200)：**
```json
{
    "success": true,
    "data": {
        "allowed": false,
        "matched_rules": [
            {
                "id": 1,
                "name": "禁止 rm -rf",
                "action": "block",
                "match_type": "contains",
                "pattern": "rm -rf /"
            }
        ],
        "severity": "block",
        "message": "命令被禁止：禁止 rm -rf"
    }
}
```

---

## 作业执行 API

### POST /job-executions
提交作业执行

**请求体（Shell 类型）：**
```json
{
    "job_type": "shell",
    "name": "string (可选, 作业名称)",
    "content": "string (必填, Shell命令)",
    "target_host_ids": "[int] (必填, 目标主机ID列表)",
    "target_business_node_ids": "[int] (可选, 业务节点ID列表，展开包含子节点)",
    "system_user_id": "int (可选)",
    "extra_vars": "object (可选, 额外变量)"
}
```

**请求体（Module 类型）：**
```json
{
    "job_type": "module",
    "name": "string (可选)",
    "module_name": "string (必填, Ansible模块名)",
    "module_args": "string (可选, 模块参数)",
    "target_host_ids": "[int] (必填)",
    "target_business_node_ids": "[int] (可选)",
    "system_user_id": "int (可选)",
    "extra_vars": "object (可选)"
}
```

**请求体（Playbook 类型）：**
```json
{
    "job_type": "playbook",
    "name": "string (可选)",
    "playbook_id": "int (必填, 剧本ID)",
    "playbook_version": "int (可选, 版本号，默认最新)",
    "target_host_ids": "[int] (必填)",
    "target_business_node_ids": "[int] (可选)",
    "system_user_id": "int (可选)",
    "extra_vars": "object (可选)"
}
```

**请求体（Script 类型）：**
```json
{
    "job_type": "script",
    "name": "string (可选)",
    "script_id": "int (必填, 脚本ID)",
    "script_version": "int (可选, 版本号，默认最新)",
    "target_host_ids": "[int] (必填)",
    "target_business_node_ids": "[int] (可选)",
    "system_user_id": "int (可选)",
    "extra_vars": "object (可选)"
}
```

**响应 (202)：**
```json
{
    "success": true,
    "data": {
        "id": 1001,
        "job_type": "shell",
        "name": "检查磁盘空间",
        "status": "pending",
        "created_at": "2024-01-01T12:00:00Z",
        "command_check": {
            "allowed": true,
            "matched_rules": [],
            "severity": "allow",
            "message": "命令检查通过"
        }
    },
    "message": "作业已提交"
}
```
> **注意**：如果命令被 block，返回 400 错误

### GET /job-executions
获取作业执行列表

**查询参数：**
- `status` (可选): 按状态筛选
- `job_type` (可选): 按类型筛选
- `created_by` (可选): 按创建者筛选
- `start_time` (可选): 开始时间（ISO 8601）
- `end_time` (可选): 结束时间（ISO 8601）
- `search` (可选): 搜索作业名称
- 分页参数

**响应 (200)：** 分页格式，items 数据结构如下：
```json
{
    "id": 1001,
    "name": "检查磁盘空间",
    "job_type": "shell",
    "status": "success",
    "started_at": "2024-01-01T12:00:00Z",
    "finished_at": "2024-01-01T12:00:05Z",
    "created_at": "2024-01-01T12:00:00Z",
    "created_by": {
        "id": 1,
        "username": "admin"
    },
    "summary": {
        "total_hosts": 5,
        "success_hosts": 4,
        "failed_hosts": 1
    }
}
```

### GET /job-executions/{id}
获取作业执行详情

**路径参数：**
- `id`: 作业执行ID

**响应 (200)：**
```json
{
    "success": true,
    "data": {
        "id": 1001,
        "name": "检查磁盘空间",
        "job_type": "shell",
        "content": "df -h",
        "target_host_ids": [1, 2, 3],
        "system_user_id": 1,
        "extra_vars": {},
        "job_template_id": null,
        "status": "running",
        "started_at": "2024-01-01T12:00:00Z",
        "finished_at": null,
        "cancelled_at": null,
        "cancelled_by": null,
        "created_at": "2024-01-01T12:00:00Z",
        "created_by": {
            "id": 1,
            "username": "admin"
        },
        "tasks": [
            {
                "id": 5001,
                "host_id": 1,
                "host_name": "web-server-01",
                "status": "success",
                "started_at": "2024-01-01T12:00:01Z",
                "finished_at": "2024-01-01T12:00:02Z"
            },
            {
                "id": 5002,
                "host_id": 2,
                "host_name": "web-server-02",
                "status": "running",
                "started_at": "2024-01-01T12:00:02Z",
                "finished_at": null
            }
        ]
    }
}
```

### GET /job-executions/{id}/output
获取作业输出（WebSocket 端点）

**连接方式：**
```
wss://api.example.com/v1/job-executions/{id}/output?token={access_token}
```

**消息格式（服务端推送）：**
```json
{
    "type": "status_update",
    "data": {
        "status": "running",
        "started_at": "2024-01-01T12:00:00Z"
    }
}
```

```json
{
    "type": "task_output",
    "data": {
        "task_id": 5001,
        "host_id": 1,
        "host_name": "web-server-01",
        "output": "Filesystem      Size  Used Avail Use% Mounted on\n/dev/sda1        40G   20G   18G  53% /",
        "timestamp": "2024-01-01T12:00:01Z"
    }
}
```

```json
{
    "type": "task_complete",
    "data": {
        "task_id": 5001,
        "host_id": 1,
        "status": "success",
        "finished_at": "2024-01-01T12:00:02Z"
    }
}
```

```json
{
    "type": "job_complete",
    "data": {
        "status": "success",
        "finished_at": "2024-01-01T12:00:05Z"
    }
}
```

### GET /job-executions/{id}/logs
获取作业完整日志（用于历史查看）

**路径参数：**
- `id`: 作业执行ID

**响应 (200)：**
```json
{
    "success": true,
    "data": {
        "job_id": 1001,
        "tasks": [
            {
                "host_id": 1,
                "host_name": "web-server-01",
                "status": "success",
                "output": "Filesystem      Size  Used Avail Use% Mounted on\n/dev/sda1        40G   20G   18G  53% /",
                "started_at": "2024-01-01T12:00:01Z",
                "finished_at": "2024-01-01T12:00:02Z"
            }
        ]
    }
}
```

### POST /job-executions/{id}/cancel
取消作业执行

**路径参数：**
- `id`: 作业执行ID

**权限说明：**
- 创建者可以取消自己的作业
- super_admin 可以取消所有作业

**响应 (200)：**
```json
{
    "success": true,
    "data": {
        "id": 1001,
        "status": "cancelled",
        "cancelled_at": "2024-01-01T12:00:03Z",
        "cancelled_by": 1
    },
    "message": "作业已取消"
}
```

### POST /job-executions/{id}/retry
重做作业（创建新的作业执行）

**路径参数：**
- `id`: 作业执行ID

**响应 (202)：**
```json
{
    "success": true,
    "data": {
        "id": 1002,
        "original_job_id": 1001,
        "status": "pending",
        "created_at": "2024-01-01T12:00:00Z"
    },
    "message": "作业已重新提交"
}
```

### POST /job-executions/{id}/save-template
保存为作业模板

**路径参数：**
- `id`: 作业执行ID

**请求体：**
```json
{
    "name": "string (必填, 模板名称)",
    "description": "string (可选)"
}
```

**响应 (201)：**
```json
{
    "success": true,
    "data": {
        "id": 50,
        "name": "检查磁盘空间模板",
        "created_at": "2024-01-01T12:00:00Z"
    },
    "message": "模板创建成功"
}
```

---

## 作业模板 API

### GET /job-templates
获取作业模板列表（含权限过滤）

**查询参数：**
- `job_type` (可选): 按类型筛选
- `is_schedule_enabled` (可选): 按调度状态筛选
- `search` (可选): 搜索名称
- 分页参数

**响应 (200)：** 分页格式，items 数据结构如下：
```json
{
    "id": 50,
    "name": "检查磁盘空间",
    "description": "定期检查磁盘空间",
    "job_type": "shell",
    "content": "df -h",
    "cron_expression": "0 0 * * *",
    "is_schedule_enabled": true,
    "last_scheduled_at": "2024-01-01T00:00:00Z",
    "created_at": "2024-01-01T12:00:00Z",
    "created_by": {
        "id": 1,
        "username": "admin"
    }
}
```

### POST /job-templates
创建作业模板

**请求体：**
```json
{
    "name": "string (必填, 最多100字符)",
    "description": "string (可选)",
    "job_type": "shell|module|playbook|script (必填)",
    "content": "string (shell类型必填)",
    "module_name": "string (module类型必填)",
    "module_args": "string (module类型可选)",
    "playbook_id": "int (playbook类型必填)",
    "playbook_version": "int (playbook类型可选)",
    "script_id": "int (script类型必填)",
    "script_version": "int (script类型可选)",
    "target_host_ids": "[int] (可选)",
    "target_business_node_ids": "[int] (可选)",
    "system_user_id": "int (可选)",
    "extra_vars": "object (可选)",
    "cron_expression": "string (可选, Cron表达式)",
    "is_schedule_enabled": "boolean (可选, 默认false)"
}
```

**响应 (201)：**
```json
{
    "success": true,
    "data": {
        "id": 51,
        "name": "每日备份",
        "job_type": "playbook",
        "is_schedule_enabled": false,
        "created_at": "2024-01-01T12:00:00Z"
    },
    "message": "模板创建成功"
}
```

### GET /job-templates/{id}
获取作业模板详情

**路径参数：**
- `id`: 模板ID

**响应 (200)：**
```json
{
    "success": true,
    "data": {
        "id": 50,
        "name": "检查磁盘空间",
        "description": "定期检查磁盘空间",
        "job_type": "shell",
        "content": "df -h",
        "target_host_ids": [1, 2, 3],
        "system_user_id": 1,
        "extra_vars": {},
        "cron_expression": "0 0 * * *",
        "is_schedule_enabled": true,
        "last_scheduled_at": "2024-01-01T00:00:00Z",
        "created_at": "2024-01-01T12:00:00Z",
        "updated_at": "2024-01-01T12:00:00Z",
        "created_by": {
            "id": 1,
            "username": "admin"
        },
        "permissions": [
            {
                "user_id": 2,
                "permission_type": "execute"
            }
        ]
    }
}
```

### PUT /job-templates/{id}
更新作业模板

**路径参数：**
- `id`: 模板ID

**请求体：** 同创建接口，所有字段可选

**响应 (200)：**
```json
{
    "success": true,
    "data": {
        "id": 50,
        "name": "检查磁盘空间",
        "updated_at": "2024-01-01T12:00:00Z"
    },
    "message": "模板更新成功"
}
```

### DELETE /job-templates/{id}
删除作业模板

**路径参数：**
- `id`: 模板ID

**响应 (200)：**
```json
{
    "success": true,
    "message": "模板删除成功"
}
```

### POST /job-templates/{id}/execute
手动触发作业模板

**路径参数：**
- `id`: 模板ID

**请求体（可选，覆盖模板参数）：**
```json
{
    "name": "string (可选, 作业名称)",
    "target_host_ids": "[int] (可选, 覆盖模板)",
    "target_business_node_ids": "[int] (可选)",
    "system_user_id": "int (可选)",
    "extra_vars": "object (可选, 与模板合并)"
}
```

**响应 (202)：**
```json
{
    "success": true,
    "data": {
        "job_execution_id": 1002,
        "status": "pending",
        "created_at": "2024-01-01T12:00:00Z"
    },
    "message": "作业已提交"
}
```

### PATCH /job-templates/{id}/schedule
设置调度

**路径参数：**
- `id`: 模板ID

**请求体：**
```json
{
    "cron_expression": "string (可选)",
    "is_schedule_enabled": "boolean (可选)"
}
```

**响应 (200)：**
```json
{
    "success": true,
    "data": {
        "id": 50,
        "cron_expression": "0 */6 * * *",
        "is_schedule_enabled": true,
        "next_run_at": "2024-01-01T18:00:00Z"
    },
    "message": "调度设置成功"
}
```

### GET /job-templates/{id}/permissions
获取模板权限列表

### PUT /job-templates/{id}/permissions
设置模板权限

> **权限 API 结构同业务节点权限 API**

---

## 审计日志 API

> **权限要求**：super_admin 或 auditor

### GET /audit-logs
获取审计日志列表

**查询参数：**
- `user_id` (可选): 按用户筛选
- `action` (可选): 按操作类型筛选
- `resource_type` (可选): 按资源类型筛选
- `start_time` (可选): 开始时间
- `end_time` (可选): 结束时间
- `search` (可选): 搜索资源名称
- 分页参数

**响应 (200)：** 分页格式，items 数据结构如下：
```json
{
    "id": 10001,
    "user_id": 1,
    "username": "admin",
    "action": "create",
    "resource_type": "host",
    "resource_id": 5,
    "resource_name": "web-server-05",
    "old_values": null,
    "new_values": {
        "name": "web-server-05",
        "business_node_id": 2
    },
    "ip_address": "192.168.1.50",
    "user_agent": "Mozilla/5.0...",
    "created_at": "2024-01-01T12:00:00Z"
}
```

### GET /audit-logs/{id}
获取审计日志详情

**路径参数：**
- `id`: 日志ID

**响应 (200)：**
```json
{
    "success": true,
    "data": {
        "id": 10001,
        "user_id": 1,
        "username": "admin",
        "action": "update",
        "resource_type": "host",
        "resource_id": 1,
        "resource_name": "web-server-01",
        "old_values": {
            "name": "web-server-01",
            "ip_internal": "192.168.1.10"
        },
        "new_values": {
            "name": "web-server-01",
            "ip_internal": "192.168.1.11"
        },
        "changes": {
            "ip_internal": {
                "old": "192.168.1.10",
                "new": "192.168.1.11"
            }
        },
        "ip_address": "192.168.1.50",
        "user_agent": "Mozilla/5.0...",
        "created_at": "2024-01-01T12:00:00Z"
    }
}
```

---

## 运营分析 API

> **权限要求**：super_admin

### GET /analytics/job-success-rate
作业成功率趋势

**查询参数：**
- `period`: "day"|"week"|"month" (默认 "day")
- `start_time`: string (ISO 8601, 默认30天前)
- `end_time`: string (ISO 8601, 默认今天)

**响应 (200)：**
```json
{
    "success": true,
    "data": {
        "period": "day",
        "items": [
            {
                "date": "2024-01-01",
                "total": 100,
                "success": 90,
                "failed": 8,
                "cancelled": 2,
                "success_rate": 0.9
            }
        ],
        "summary": {
            "total": 3000,
            "success": 2700,
            "success_rate": 0.9,
            "trend": "+0.05"
        }
    }
}
```

### GET /analytics/failed-jobs-top
失败率最高的作业

**查询参数：**
- `limit`: int (默认 10)
- `start_time`: string (ISO 8601)
- `end_time`: string (ISO 8601)

**响应 (200)：**
```json
{
    "success": true,
    "data": [
        {
            "name": "复杂部署剧本",
            "job_type": "playbook",
            "playbook_id": 10,
            "total_executions": 100,
            "failed_executions": 30,
            "failure_rate": 0.3
        }
    ]
}
```

### GET /analytics/slowest-jobs
执行最慢的作业

**查询参数：**
- `limit`: int (默认 10)
- `status`: "success"|"failed" (可选, 按状态筛选)
- `start_time`: string (ISO 8601)
- `end_time`: string (ISO 8601)

**响应 (200)：**
```json
{
    "success": true,
    "data": [
        {
            "job_execution_id": 1001,
            "name": "全量部署",
            "job_type": "playbook",
            "duration_seconds": 1800,
            "status": "success",
            "created_at": "2024-01-01T12:00:00Z"
        }
    ]
}
```

### GET /analytics/most-used-playbooks
最常使用的剧本

**查询参数：**
- `limit`: int (默认 10)
- `start_time`: string (ISO 8601)
- `end_time`: string (ISO 8601)

**响应 (200)：**
```json
{
    "success": true,
    "data": [
        {
            "playbook_id": 5,
            "playbook_name": "部署 Web 服务",
            "usage_count": 500,
            "success_rate": 0.95
        }
    ]
}
```

### GET /analytics/host-coverage
自动化覆盖主机比例

**响应 (200)：**
```json
{
    "success": true,
    "data": {
        "total_hosts": 100,
        "covered_hosts": 85,
        "coverage_rate": 0.85,
        "hosts": [
            {
                "id": 1,
                "name": "web-server-01",
                "last_executed_at": "2024-01-01T12:00:00Z",
                "execution_count": 50,
                "is_covered": true
            }
        ]
    }
}
```

### GET /analytics/dashboard
仪表盘汇总数据

**查询参数：**
- `start_time`: string (ISO 8601)
- `end_time`: string (ISO 8601)

**响应 (200)：**
```json
{
    "success": true,
    "data": {
        "summary": {
            "total_jobs": 1000,
            "success_jobs": 900,
            "success_rate": 0.9,
            "avg_duration": 60
        },
        "today": {
            "total_jobs": 50,
            "success_jobs": 45,
            "running_jobs": 3
        },
        "top_playbooks": [...],
        "recent_failures": [...]
    }
}
```

---

## 附录

### 角色权限矩阵

| 功能 | super_admin | operator | developer | auditor |
|-----|-------------|----------|-----------|---------|
| 用户管理 | ✅ | ❌ | ❌ | ❌ |
| 业务节点 CRUD | ✅ | ✅ | ❌ | ❌ |
| 业务节点权限设置 | ✅ | ✅ | ❌ | ❌ |
| 主机 CRUD | ✅ | ✅ | ❌ | ❌ |
| 系统用户 CRUD | ✅ | ✅ | ❌ | ❌ |
| 网关 CRUD | ✅ | ✅ | ❌ | ❌ |
| 脚本/剧本 CRUD | ✅ | ✅ | ❌ | ❌ |
| 命令过滤规则 | ✅ | ✅ | ❌ | ❌ |
| 执行作业 | ✅ | ✅ | ✅（有权限的） | ❌ |
| 取消作业 | ✅ | ✅（自己的） | ✅（自己的） | ❌ |
| 作业模板 CRUD | ✅ | ✅ | ❌ | ❌ |
| 作业历史 | ✅ | ✅（自己的） | ✅（自己的） | ✅（所有） |
| 审计日志 | ✅ | ❌ | ❌ | ✅ |
| 运营分析 | ✅ | ❌ | ❌ | ❌ |

### 业务节点权限类型

| 权限 | 说明 |
|-----|------|
| view | 可以查看业务节点和主机 |
| execute | 可以在主机上执行作业 |
| manage | 可以管理业务节点（编辑、删除、设置权限等） |

### 命令过滤动作

| 动作 | 说明 |
|-----|------|
| block | 阻止命令执行 |
| warn | 警告但允许执行（记录审计日志） |

### Cron 表达式说明

```
┌───────────── 分钟 (0-59)
│ ┌───────────── 小时 (0-23)
│ │ ┌───────────── 日期 (1-31)
│ │ │ ┌───────────── 月份 (1-12)
│ │ │ │ ┌───────────── 星期 (0-7, 0=7=星期日)
│ │ │ │ │
* * * * *
```

示例：
- `0 0 * * *` - 每天凌晨
- `0 */6 * * *` - 每6小时
- `0 0 * * 0` - 每周日凌晨

### WebSocket 连接说明

连接时必须通过 query parameter 传递 access token：
```
wss://api.example.com/v1/job-executions/{id}/output?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

如果 token 无效，会立即关闭连接并发送错误消息。

---

**文档版本**：v1.0  
**最后更新**：2024-01-01

---

## API设计改进建议

### 1. PATCH端点支持（部分更新）

**当前问题**：所有更新操作仅使用PUT，要求客户端提供完整资源。

**改进方案**：为所有主要资源添加PATCH端点，支持部分更新：

```
PATCH /users/{id}
PATCH /business-nodes/{id}
PATCH /hosts/{id}
PATCH /system-users/{id}
PATCH /gateways/{id}
PATCH /scripts/{id}
PATCH /playbooks/{id}
PATCH /command-filter-rules/{id}
PATCH /job-templates/{id}
```

**示例（更新主机）**：
```json
{
  "name": "新主机名",
  "ip_internal": "192.168.1.20"
}
```

---

### 2. WebSocket安全增强

**当前问题**：token通过query parameter传递，可能被访问日志记录。

**改进方案**：

**连接方式（推荐）**：
```http
GET /v1/job-executions/{id}/output
Authorization: Bearer {access_token}
Upgrade: websocket
Connection: Upgrade
```

**向后兼容方案**（继续支持query param，但推荐使用header）：
```
wss://api.example.com/v1/job-executions/{id}/output?token={access_token}
```

**新增功能**：
- 心跳机制（每30秒ping/pong）
- 连接状态通知
- 消息确认机制

---

### 3. 错误响应格式统一和增强

**改进方案**：明确定义验证错误详情格式：

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "参数验证失败",
    "details": [
      {
        "field": "name",
        "code": "required",
        "message": "名称不能为空"
      },
      {
        "field": "email",
        "code": "invalid_format",
        "message": "邮箱格式不正确"
      }
    ]
  }
}
```

**常见错误码**：
- `required` - 必填字段缺失
- `invalid_format` - 格式不正确
- `too_short` / `too_long` - 长度不符合要求
- `invalid_enum` - 枚举值不正确
- `already_exists` - 资源已存在
- `not_found` - 资源不存在
- `permission_denied` - 权限不足

---

### 4. 速率限制规范

**新增内容**：添加明确的速率限制说明：

**响应头**：
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1699999999
```

**429错误响应**：
```json
{
  "success": false,
  "error": {
    "code": "TOO_MANY_REQUESTS",
    "message": "请求过于频繁，请稍后再试",
    "retry_after": 60
  }
}
```

**速率限制策略**：
- 认证接口：10次/分钟
- 读取操作：1000次/分钟
- 写入操作：100次/分钟
- 作业执行：10次/分钟

---

### 5. 新增批量操作端点

**主机批量创建**：
```
POST /hosts/batch
```

**请求体**：
```json
{
  "hosts": [
    {
      "name": "web-server-01",
      "business_node_id": 2,
      "ip_internal": "192.168.1.10"
    },
    {
      "name": "web-server-02",
      "business_node_id": 2,
      "ip_internal": "192.168.1.11"
    }
  ]
}
```

**响应**：
```json
{
  "success": true,
  "data": {
    "total": 2,
    "success": 2,
    "failed": 0,
    "hosts": [
      {
        "id": 10,
        "name": "web-server-01",
        "status": "created"
      }
    ]
  }
}
```

**其他批量端点**：
```
POST /business-nodes/{id}/hosts/batch  # 批量添加到业务节点
DELETE /hosts/batch  # 批量删除
POST /scripts/batch  # 批量导入脚本
```

---

### 6. 分页参数标准化

**改进方案**：统一分页参数名称：

| 参数 | 类型 | 必填 | 默认 | 说明 |
|-----|------|------|------|------|
| `page` | int | 否 | 1 | 页码 |
| `limit` | int | 否 | 20 | 每页数量（最大100） |
| `sort_by` | string | 否 | `created_at` | 排序字段 |
| `sort_order` | string | 否 | `desc` | 排序方向（asc/desc） |

**改进的分页响应**：
```json
{
  "success": true,
  "data": {
    "items": [],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 100,
      "total_pages": 5,
      "has_next": true,
      "has_prev": false
    }
  },
  "message": "查询成功"
}
```

---

### 7. 新增SSE端点（WebSocket备选）

**Server-Sent Events端点**：
```
GET /job-executions/{id}/events
Authorization: Bearer {access_token}
Accept: text/event-stream
```

**事件流格式**：
```
event: status_update
data: {"status": "running", "started_at": "2024-01-01T12:00:00Z"}

event: task_output
data: {"task_id": 5001, "host_id": 1, "output": "...", "timestamp": "..."}

event: task_complete
data: {"task_id": 5001, "host_id": 1, "status": "success"}

event: job_complete
data: {"status": "success", "finished_at": "..."}
```

---

### 8. 新增系统健康检查端点

**服务健康检查**：
```
GET /health
```

**响应**：
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "services": {
      "database": "healthy",
      "redis": "healthy",
      "celery_worker": "healthy"
    },
    "uptime": 86400
  }
}
```

**系统状态**：
```
GET /status
```

**响应**：
```json
{
  "success": true,
  "data": {
    "queued_jobs": 5,
    "running_jobs": 3,
    "active_users": 10,
    "database_pool": {
      "used": 15,
      "idle": 5,
      "max": 20
    }
  }
}
```

---

### 9. 新增全局搜索端点

**跨资源搜索**：
```
GET /search?q=web-server&type=host,script
```

**查询参数**：
- `q` - 搜索关键词
- `type` - 资源类型（可选，逗号分隔）
- `limit` - 结果数量限制（默认20）

**响应**：
```json
{
  "success": true,
  "data": {
    "hits": [
      {
        "type": "host",
        "id": 1,
        "name": "web-server-01",
        "summary": "192.168.1.10"
      },
      {
        "type": "script",
        "id": 5,
        "name": "web-deploy.sh",
        "summary": "部署Web服务脚本"
      }
    ],
    "total": 2
  }
}
```

---

### 10. 文件上传端点（为未来版本预留）

**剧本文件上传**：
```
POST /playbooks/upload
Content-Type: multipart/form-data

file: [剧本文件]
name: "web-deploy.yml"
description: "Web服务部署剧本"
```

**脚本文件上传**：
```
POST /scripts/upload
Content-Type: multipart/form-data

file: [脚本文件]
name: "backup.sh"
language: "bash"
```

---

### 11. 版本管理策略

**API版本控制**：
- URL路径版本：`/v1/...`（当前）
- 向后兼容保证
- 弃用通知提前3个月

**响应头添加**：
```
X-API-Version: 1.0.0
X-API-Deprecated: false
X-API-Sunset: <可选，过期日期>
```

---

### 12. 优化的主机连接配置响应

**增强当前端点**：
```
GET /hosts/{id}/connection-config
```

**新增字段**：
```json
{
  "success": true,
  "data": {
    "host_id": 1,
    "host_name": "web-server-01",
    "ip": "192.168.1.10",
    "ssh_port": 22,
    "system_user_id": 1,
    "system_user": {
      "id": 1,
      "name": "root",
      "username": "root",
      "auth_type": "private_key"
    },
    "gateway": {
      "id": 1,
      "name": "生产网关",
      "ip": "192.168.1.100",
      "port": 22,
      "system_user_id": 1,
      "source": "business_node"
    },
    "resolved_config": {
      "ansible_host": "192.168.1.10",
      "ansible_port": 22,
      "ansible_user": "root",
      "ansible_ssh_private_key": "<vaulted>",
      "ansible_ssh_common_args": "-o ProxyCommand='ssh -W %h:%p -q 192.168.1.100'"
    },
    "resolution_path": [
      {
        "level": "host",
        "field": "ip",
        "value": "192.168.1.10",
        "status": "explicit"
      },
      {
        "level": "business_node",
        "field": "gateway_id",
        "value": 1,
        "status": "inherited"
      }
    ]
  }
}
```

---

### 13. Webhook/事件订阅（为未来版本预留）

**创建订阅**：
```
POST /webhooks
```

**请求体**：
```json
{
  "url": "https://example.com/webhook",
  "events": ["job.completed", "job.failed"],
  "secret": "webhook-secret-key",
  "enabled": true
}
```

---

### 14. 改进建议优先级

| 优先级 | 功能 | 说明 |
|-------|------|------|
| P0 | PATCH端点 | 核心功能改进，提升开发体验 |
| P0 | 统一错误格式 | 提升调试体验和一致性 |
| P1 | 速率限制 | 系统稳定性保障 |
| P1 | 分页标准化 | API一致性改进 |
| P1 | 批量操作 | 提升效率的重要功能 |
| P2 | 健康检查 | 运维友好功能 |
| P2 | 全局搜索 | 用户体验优化 |
| P2 | WebSocket安全增强 | 安全性改进 |
| P3 | SSE端点 | WebSocket备选方案 |
| P3 | Webhook | 未来扩展 |

---

### 15. 与前后端任务对齐情况

✅ **完整对齐**：所有改进均不违背现有PRD和任务设计
✅ **向后兼容**：所有新增功能均为追加，不影响现有API
✅ **任务覆盖**：
- 后端任务：改进建议可直接集成到任务1-19中
- 前端任务：现有前端页面可无缝迁移到新API
✅ **安全优先**：所有改进均考虑了安全性设计

---

## 总结

本API文档提供了完整的Ansible作业平台API设计，包括：

✅ **完整的资源CRUD**
✅ **认证授权系统**
✅ **作业执行与实时输出**
✅ **版本管理**
✅ **审计日志**
✅ **运营分析**
✅ **详细的改进建议**（新增）

API设计与PRD、前端任务、后端任务完全对齐，可直接用于指导开发工作。
