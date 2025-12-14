from typing import Any, Dict
from celery import Celery

from ..core import ITaskProducer

__all__ = ["CeleryTaskProducer"]


class CeleryTaskProducer(ITaskProducer):
    def __init__(self, celery_app: Celery):
        self.celery_app = celery_app

    def send_task(self, name: str, args: list[Any] | None = None, kwargs: Dict[str, Any] | None = None) -> None:
        self.celery_app.send_task(name, args=args, kwargs=kwargs)
