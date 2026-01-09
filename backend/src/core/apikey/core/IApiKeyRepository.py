from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime


class IApiKeyRepository(ABC):

    @abstractmethod
    async def find_by_key(self, key: str) -> Optional[any]:
        raise NotImplementedError

    @abstractmethod
    async def create(self, key: str, description: str, expires_at: Optional[datetime] = None) -> any:
        raise NotImplementedError

    @abstractmethod
    async def deactivate(self, key_id: int) -> None:
        raise NotImplementedError
