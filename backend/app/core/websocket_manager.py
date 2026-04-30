from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect
import json
from datetime import datetime


class WebSocketMessageType:
    STATUS_UPDATE = "status_update"
    TASK_OUTPUT = "task_output"
    TASK_COMPLETE = "task_complete"
    JOB_COMPLETE = "job_complete"


class ConnectionManager:
    def __init__(self):
        # 每个 job_id 对应一组 WebSocket 连接
        self.active_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, job_id: int, websocket: WebSocket):
        await websocket.accept()
        if job_id not in self.active_connections:
            self.active_connections[job_id] = set()
        self.active_connections[job_id].add(websocket)

    def disconnect(self, job_id: int, websocket: WebSocket):
        if job_id in self.active_connections:
            self.active_connections[job_id].discard(websocket)
            if not self.active_connections[job_id]:
                del self.active_connections[job_id]

    async def send_to_job(self, job_id: int, message: Dict):
        """发送消息给某个 job 的所有连接"""
        if job_id not in self.active_connections:
            return
        disconnected = set()
        for connection in self.active_connections[job_id]:
            try:
                await connection.send_json(message)
            except WebSocketDisconnect:
                disconnected.add(connection)
        # 清理断开的连接
        for connection in disconnected:
            self.disconnect(job_id, connection)

    async def broadcast_status_update(self, job_id: int, status: str, **kwargs):
        """广播作业状态更新"""
        message = {
            "type": WebSocketMessageType.STATUS_UPDATE,
            "job_id": job_id,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }
        await self.send_to_job(job_id, message)

    async def broadcast_task_output(self, job_id: int, task_id: int, stdout: str = "", stderr: str = ""):
        """广播任务输出"""
        message = {
            "type": WebSocketMessageType.TASK_OUTPUT,
            "job_id": job_id,
            "task_id": task_id,
            "stdout": stdout,
            "stderr": stderr,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_to_job(job_id, message)

    async def broadcast_task_complete(self, job_id: int, task_id: int, status: str, exit_code: int = None):
        """广播任务完成"""
        message = {
            "type": WebSocketMessageType.TASK_COMPLETE,
            "job_id": job_id,
            "task_id": task_id,
            "status": status,
            "exit_code": exit_code,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_to_job(job_id, message)

    async def broadcast_job_complete(self, job_id: int, status: str, success: bool):
        """广播作业完成"""
        message = {
            "type": WebSocketMessageType.JOB_COMPLETE,
            "job_id": job_id,
            "status": status,
            "success": success,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_to_job(job_id, message)


manager = ConnectionManager()
