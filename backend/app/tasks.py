"""Celery任务模块"""
from app.core.celery_app import celery_app


@celery_app.task
def example_async_task(name: str) -> str:
    """示例异步任务"""
    return f"Hello, {name}! This is an async task."
