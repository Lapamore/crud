from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..core import IUserWriteRepository
from ...dto import UserDTO
from src.models import User


class SqlAlchemyUserWriteRepository(IUserWriteRepository):
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

    async def create(
        self,
        email: str,
        username: str,
        hashed_password: str,
        bio: Optional[str] = None,
        image_url: Optional[str] = None,
    ) -> int:
        user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            bio=bio,
            image_url=image_url,
        )
        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        return user.id

    async def update(
        self,
        user_id: int,
        email: Optional[str] = None,
        username: Optional[str] = None,
        hashed_password: Optional[str] = None,
        bio: Optional[str] = None,
        image_url: Optional[str] = None,
    ) -> None:
        query = select(User).where(User.id == user_id)
        result = await self._session.execute(query)
        user = result.scalar_one_or_none()

        if user is None:
            return

        if email is not None:
            user.email = email
        if username is not None:
            user.username = username
        if hashed_password is not None:
            user.hashed_password = hashed_password
        if bio is not None:
            user.bio = bio
        if image_url is not None:
            user.image_url = image_url

        self._session.add(user)
        await self._session.commit()

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
