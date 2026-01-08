from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime


class IApiKeyRepository(ABC):
    """Интерфейс репозитория для API-ключей."""
    
    @abstractmethod
    async def find_by_key(self, key: str) -> Optional[any]:
        """Найти API-ключ по значению ключа."""
        raise NotImplementedError

    @abstractmethod
    async def create(self, key: str, description: str, expires_at: Optional[datetime] = None) -> any:
        """Создать новый API-ключ."""
        raise NotImplementedError

    @abstractmethod
    async def deactivate(self, key_id: int) -> None:
        """Деактивировать API-ключ."""
        raise NotImplementedError
