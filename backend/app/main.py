from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.middleware import AuditLogMiddleware
from app.api import (
    auth_router,
    users_router,
    business_nodes_router,
    system_users_router,
    gateways_router,
    hosts_router,
    scripts_router,
    playbooks_router,
    command_filter_rules_router,
    audit_logs_router,
    job_executions_router,
    job_templates_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时启动事件监听器
    import asyncio
    from app.core.job_events import listen_to_job_events
    task = asyncio.create_task(listen_to_job_events())

    yield

    # 停止时清理
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, lifespan=lifespan)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 审计日志中间件
app.add_middleware(AuditLogMiddleware)

# 全局异常处理器 - 确保错误响应也有CORS头
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    if settings.DEBUG:
        import traceback
        error_detail = {
            "detail": str(exc),
            "traceback": traceback.format_exc()
        }
    else:
        error_detail = {"detail": "服务器内部错误"}

    return JSONResponse(
        status_code=500,
        content=error_detail
    )

# 注册路由
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(business_nodes_router, prefix="/api")
app.include_router(system_users_router, prefix="/api")
app.include_router(gateways_router, prefix="/api")
app.include_router(hosts_router, prefix="/api")
app.include_router(scripts_router, prefix="/api")
app.include_router(playbooks_router, prefix="/api")
app.include_router(command_filter_rules_router, prefix="/api")
app.include_router(audit_logs_router, prefix="/api")
app.include_router(job_executions_router, prefix="/api")
app.include_router(job_templates_router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
