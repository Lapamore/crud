from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..core import IUserReadRepository
from ...dto import UserDTO
from src.models import User


class SqlAlchemyUserReadRepository(IUserReadRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_dto(self, user: User) -> UserDTO:
        return UserDTO(
            id=user.id,
            email=user.email,
            username=user.username,
            hashed_password=user.hashed_password,
            bio=user.bio,
            image_url=user.image_url,
        )

    async def find_by_id(self, user_id: int) -> Optional[UserDTO]:
        query = select(User).where(User.id == user_id)
        result = await self._session.execute(query)
        user = result.scalar_one_or_none()
        return self._to_dto(user) if user else None

    async def find_by_email(self, email: str) -> Optional[UserDTO]:
        query = select(User).where(User.email == email)
        result = await self._session.execute(query)
        user = result.scalar_one_or_none()
        return self._to_dto(user) if user else None

    async def find_by_username(self, username: str) -> Optional[UserDTO]:
        query = select(User).where(User.username == username)
        result = await self._session.execute(query)
        user = result.scalar_one_or_none()
        return self._to_dto(user) if user else None
