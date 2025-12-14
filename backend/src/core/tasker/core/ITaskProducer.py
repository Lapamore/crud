from abc import ABC, abstractmethod
from typing import Any, Dict

__all__ = ["ITaskProducer"]


class ITaskProducer(ABC):
    @abstractmethod
    def send_task(self, name: str, args: list[Any] | None = None, kwargs: Dict[str, Any] | None = None) -> None:
        raise NotImplementedError
