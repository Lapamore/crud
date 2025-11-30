from abc import ABC, abstractmethod
from typing import Optional

from ...dto import UserDTO


class IUserReadRepository(ABC):
    @abstractmethod
    async def find_by_id(self, user_id: int) -> Optional[UserDTO]:
        pass

    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[UserDTO]:
        pass

    @abstractmethod
    async def find_by_username(self, username: str) -> Optional[UserDTO]:
        pass
