from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth_router, users_router, business_nodes_router, system_users_router, gateways_router, hosts_router

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(business_nodes_router, prefix="/api")
app.include_router(system_users_router, prefix="/api")
app.include_router(gateways_router, prefix="/api")
app.include_router(hosts_router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
