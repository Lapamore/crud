from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.Article import Article
from ..core.IArticleReadRepository import IArticleReadRepository


class SqlAlchemyArticleReadRepository(IArticleReadRepository):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def find_by_slug(self, slug: str) -> Optional[Article]:
        query = select(Article).where(Article.slug == slug)
        result = await self._db.execute(query)
        return result.scalar_one_or_none()

    async def find_all(self, skip: int, limit: int) -> List[Article]:
        query = select(Article).offset(skip).limit(limit)
        result = await self._db.execute(query)
        return result.scalars().all()
