from abc import ABC, abstractmethod
from typing import Optional

__all__ = ["IBroker"]


class IBroker(ABC):
    @abstractmethod
    def get_dedup_key(self, key: str) -> Optional[str]:
        pass

    @abstractmethod
    def set_dedup_key(self, key: str, value: str, expire: int) -> None:
        pass
