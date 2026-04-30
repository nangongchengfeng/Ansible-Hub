import asyncio
import json
from typing import Dict, Any
from redis.asyncio import Redis as AsyncRedis
from app.core.config import settings
from app.core.websocket_manager import manager


class JobEventChannels:
    JOB_STATUS = "job_status"
    TASK_OUTPUT = "task_output"
    TASK_COMPLETE = "task_complete"
    JOB_COMPLETE = "job_complete"


async def publish_job_event(channel: str, data: Dict[str, Any]):
    """发布作业事件到 Redis"""
    redis = AsyncRedis.from_url(settings.REDIS_URL, decode_responses=True)
    await redis.publish(channel, json.dumps(data))
    await redis.close()


async def listen_to_job_events():
    """监听作业事件并转发给 WebSocket 管理器"""
    redis = AsyncRedis.from_url(settings.REDIS_URL, decode_responses=True)
    pubsub = redis.pubsub()

    await pubsub.subscribe(
        JobEventChannels.JOB_STATUS,
        JobEventChannels.TASK_OUTPUT,
        JobEventChannels.TASK_COMPLETE,
        JobEventChannels.JOB_COMPLETE
    )

    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                channel = message["channel"]

                if channel == JobEventChannels.JOB_STATUS:
                    await manager.broadcast_status_update(data["job_id"], data["status"], **data.get("extra", {}))
                elif channel == JobEventChannels.TASK_OUTPUT:
                    await manager.broadcast_task_output(
                        data["job_id"], data["task_id"],
                        data.get("stdout", ""), data.get("stderr", "")
                    )
                elif channel == JobEventChannels.TASK_COMPLETE:
                    await manager.broadcast_task_complete(
                        data["job_id"], data["task_id"],
                        data["status"], data.get("exit_code")
                    )
                elif channel == JobEventChannels.JOB_COMPLETE:
                    await manager.broadcast_job_complete(
                        data["job_id"], data["status"], data["success"]
                    )
    finally:
        await pubsub.close()
        await redis.close()


def sync_publish_job_event(channel: str, data: Dict[str, Any]):
    """同步发布作业事件（用于 Celery 任务）"""
    import asyncio
    asyncio.run(publish_job_event(channel, data))
