"""审计日志中间件"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.concurrency import iterate_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session_factory
from app.services.audit_log import AuditLogService
from app.api.deps import get_current_user_from_request
import re
import json
from typing import Optional, Dict, Any


class AuditLogMiddleware(BaseHTTPMiddleware):
    """审计日志中间件"""

    # 需要审计的路径模式和资源类型映射
    AUDIT_PATHS = {
        r'^/api/users(/\d+)?$': {'resource_type': 'user', 'methods': ['POST', 'PUT', 'DELETE']},
        r'^/api/users/\d+/reset-password$': {'resource_type': 'user', 'methods': ['POST']},
        r'^/api/hosts(/\d+)?$': {'resource_type': 'host', 'methods': ['POST', 'PUT', 'DELETE']},
        r'^/api/hosts/\d+/toggle$': {'resource_type': 'host', 'methods': ['PATCH']},
        r'^/api/hosts/\d+/move$': {'resource_type': 'host', 'methods': ['POST']},
        r'^/api/scripts(/\d+)?$': {'resource_type': 'script', 'methods': ['POST', 'PUT', 'DELETE']},
        r'^/api/scripts/\d+/rollback$': {'resource_type': 'script', 'methods': ['POST']},
        r'^/api/playbooks(/\d+)?$': {'resource_type': 'playbook', 'methods': ['POST', 'PUT', 'DELETE']},
        r'^/api/playbooks/\d+/rollback$': {'resource_type': 'playbook', 'methods': ['POST']},
        r'^/api/command-filter-rules(/\d+)?$': {'resource_type': 'command_filter_rule', 'methods': ['POST', 'PUT', 'DELETE']},
        r'^/api/command-filter-rules/\d+/toggle$': {'resource_type': 'command_filter_rule', 'methods': ['PATCH']},
        r'^/api/command-filter-rules/reorder$': {'resource_type': 'command_filter_rule', 'methods': ['PUT']},
        r'^/api/gateways(/\d+)?$': {'resource_type': 'gateway', 'methods': ['POST', 'PUT', 'DELETE']},
        r'^/api/business-nodes(/\d+)?$': {'resource_type': 'business_node', 'methods': ['POST', 'PUT', 'DELETE']},
        r'^/api/system-users(/\d+)?$': {'resource_type': 'system_user', 'methods': ['POST', 'PUT', 'DELETE']},
    }

    # 登录/登出特殊处理
    AUTH_PATHS = {
        r'^/api/auth/login$': {'action': 'login'},
        r'^/api/auth/logout$': {'action': 'logout'},
    }

    async def dispatch(self, request: Request, call_next):
        # 先处理请求，获取响应
        response = await call_next(request)

        # 检查是否需要记录审计日志
        path = request.url.path
        method = request.method

        # 检查是否是认证相关操作
        for pattern, config in self.AUTH_PATHS.items():
            if re.match(pattern, path):
                await self._log_auth_action(request, response, config['action'])
                return response

        # 检查是否是CRUD操作
        for pattern, config in self.AUDIT_PATHS.items():
            if re.match(pattern, path) and method in config['methods']:
                # 缓存响应体
                response_body = [chunk async for chunk in response.body_iterator]
                response.body_iterator = iterate_in_threadpool(iter(response_body))

                await self._log_crud_action(
                    request, response, config['resource_type'], method,
                    b''.join(response_body) if response_body else None
                )
                return response

        return response

    async def _log_auth_action(self, request: Request, response: Response, action: str):
        """记录认证操作"""
        try:
            async with async_session_factory() as db:
                # 尝试获取当前用户
                user = None
                try:
                    user = await get_current_user_from_request(request, db)
                except Exception:
                    pass

                # 对于登录，尝试从请求中获取用户名
                username = None
                if action == 'login':
                    try:
                        # 获取请求体
                        body = await request.body()
                        if body:
                            body_json = json.loads(body)
                            username = body_json.get('username')
                    except Exception:
                        pass

                # 只有登录成功或登出时才记录
                if action == 'logout' or (action == 'login' and response.status_code == 200):
                    await AuditLogService.log_action(
                        db=db,
                        user=user,
                        action=action,
                        resource_type='auth',
                        resource_name=username or (user.username if user else None),
                        ip_address=request.client.host if request.client else None,
                        user_agent=request.headers.get('user-agent')
                    )
        except Exception:
            # 审计日志失败不影响正常流程
            pass

    async def _log_crud_action(
        self, request: Request, response: Response,
        resource_type: str, method: str, response_body: Optional[bytes]
    ):
        """记录CRUD操作"""
        try:
            # 只记录成功的操作
            if response.status_code not in [200, 201, 204]:
                return

            async with async_session_factory() as db:
                # 尝试获取当前用户
                user = None
                try:
                    user = await get_current_user_from_request(request, db)
                except Exception:
                    pass

                if not user:
                    return

                # 确定操作类型
                action_map = {'POST': 'create', 'PUT': 'update', 'PATCH': 'update', 'DELETE': 'delete'}
                action = action_map.get(method, method.lower())

                # 从路径中提取资源ID
                resource_id = self._extract_resource_id(request.url.path)

                # 尝试获取资源名称
                resource_name = self._extract_resource_name(response_body, resource_type)

                await AuditLogService.log_action(
                    db=db,
                    user=user,
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    resource_name=resource_name,
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get('user-agent')
                )
        except Exception:
            # 审计日志失败不影响正常流程
            pass

    def _extract_resource_id(self, path: str) -> Optional[int]:
        """从路径中提取资源ID"""
        match = re.search(r'/(\d+)$', path)
        if match:
            return int(match.group(1))
        return None

    def _extract_resource_name(self, response_body: Optional[bytes], resource_type: str) -> Optional[str]:
        """尝试从响应中提取资源名称"""
        if not response_body:
            return None

        try:
            body = json.loads(response_body)
            # 尝试常见的名称字段
            name_fields = ['name', 'username', 'hostname', 'title']
            for field in name_fields:
                if field in body:
                    return str(body[field])
            # 如果items字段存在（列表响应），尝试从第一个item获取
            if 'items' in body and isinstance(body['items'], list) and len(body['items']) > 0:
                item = body['items'][0]
                for field in name_fields:
                    if field in item:
                        return str(item[field])
        except Exception:
            pass
        return None
