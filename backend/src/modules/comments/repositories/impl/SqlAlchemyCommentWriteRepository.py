from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import Comment
from ..core.ICommentWriteRepository import ICommentWriteRepository


class SqlAlchemyCommentWriteRepository(ICommentWriteRepository):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def save(self, comment: Comment) -> Comment:
        self._db.add(comment)
        await self._db.commit()
        await self._db.refresh(comment)
        return comment

    async def find_by_id(self, comment_id: int) -> Optional[Comment]:
        query = select(Comment).where(Comment.id == comment_id)
        result = await self._db.execute(query)
        return result.scalar_one_or_none()

    async def delete(self, comment: Comment) -> None:
        await self._db.delete(comment)
        await self._db.commit()
