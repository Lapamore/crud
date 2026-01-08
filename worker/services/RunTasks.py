"""
Точка входа для Celery воркеров.
"""
from infrastructure.core.ioc.container import container

celery = container.resolve("celery")

# Импортируем SAGA задачи для регистрации
from services.saga import (
    moderate_post,
    generate_preview,
    publish_post,
    notify_subscribers,
    notify_followers,
    process_dlq,
)

__all__ = [
    "moderate_post",
    "generate_preview",
    "publish_post",
    "notify_subscribers",
    "notify_followers",
    "process_dlq",
]