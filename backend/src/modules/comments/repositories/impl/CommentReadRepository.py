from typing import Optional, List

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Comment, Article
from ..core import ICommentReadRepository

__all__ = ["CommentReadRepository"]


class CommentReadRepository(ICommentReadRepository):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def find_by_id(self, comment_id: int) -> Optional[Comment]:
        query = select(Comment).where(Comment.id == comment_id)
        result = await self._db.execute(query)
        return result.scalar_one_or_none()

    async def find_by_article_slug(self, slug: str) -> List[Comment]:
        query = select(Comment).join(Article).filter(Article.slug == slug)
        result = await self._db.execute(query)
        return result.scalars().all()
