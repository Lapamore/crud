"""
Общие утилиты и конфигурация для SAGA воркеров.
"""
import logging
from config import config
from infrastructure.core.ioc.container import container

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

celery = container.resolve("celery")
broker = container.resolve("broker")

USERS_DATABASE_URL = config.users_database_url
MAIN_DATABASE_URL = config.main_database_url
BACKEND_URL = config.backend_url
INTERNAL_API_KEY = config.internal_api_key

DLQ_QUEUE = "dlq"


def get_internal_headers():
    """Получить заголовки для внутренних запросов."""
    return {
        "X-API-Key": INTERNAL_API_KEY,
        "Content-Type": "application/json"
    }


def send_to_dlq(task_name: str, task_data: dict, error: str):
    """Отправить задачу в DLQ."""
    celery.send_task(
        "dlq.process",
        args=[{
            "original_task": task_name,
            "data": task_data,
            "error": str(error)
        }],
        queue=DLQ_QUEUE
    )
    logger.info(f"Task {task_name} sent to DLQ: {error}")
