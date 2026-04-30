# Ansible Job Platform - Backend

## 开发环境设置

### 1. 安装依赖
```bash
uv sync
uv pip install -e ".[dev]"
```

### 2. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，配置数据库等信息
```

### 3. 运行数据库迁移
```bash
# 确保PostgreSQL正在运行
uv run alembic upgrade head
```

### 4. 启动开发服务器
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 启动Celery Worker（可选）
```bash
uv run celery -A app.core.celery_app worker --loglevel=info --pool=solo
```

### 6. 启动Celery Beat（可选，用于定时任务）
```bash
uv run celery -A app.core.celery_app beat --loglevel=info
```

## 运行测试
```bash
uv run pytest tests/ -v
```

## API文档
启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
