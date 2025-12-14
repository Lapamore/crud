from abc import ABC, abstractmethod
from typing import Optional

from ...dto import UserDTO


class IUserWriteRepository(ABC):
    @abstractmethod
    async def update_subscription_key(self, user_id: int, subscription_key: str) -> None:
        """Updates the subscription key for a user."""
        pass

    @abstractmethod
    async def create(
        self,
        email: str,
        username: str,
        hashed_password: str,
        bio: Optional[str] = None,
        image_url: Optional[str] = None,
    ) -> int:
        """Creates a new user and returns the user ID."""
        pass

    @abstractmethod
    async def update(
        self,
        user_id: int,
        email: Optional[str] = None,
        username: Optional[str] = None,
        hashed_password: Optional[str] = None,
        bio: Optional[str] = None,
        image_url: Optional[str] = None,
    ) -> None:
        """Updates an existing user."""
        pass

    @abstractmethod
    async def find_by_id(self, user_id: int) -> Optional[UserDTO]:
        """Find user by ID for update operations."""
        pass

    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[UserDTO]:
        """Find user by email for uniqueness check."""
        pass

    @abstractmethod
    async def find_by_username(self, username: str) -> Optional[UserDTO]:
        """Find user by username for uniqueness check."""
        pass
