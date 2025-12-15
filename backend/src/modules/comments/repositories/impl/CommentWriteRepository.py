from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Comment
from ..core import ICommentWriteRepository

__all__ = ["CommentWriteRepository"]


class CommentWriteRepository(ICommentWriteRepository):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def save(self, comment: Comment) -> Comment:
        self._db.add(comment)
        await self._db.commit()
        await self._db.refresh(comment)
        return comment

    async def delete(self, comment: Comment) -> None:
        await self._db.delete(comment)
        await self._db.commit()