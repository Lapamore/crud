from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .....models.Article import Article
from ..core.IArticleRepository import IArticleRepository

__all__ = ["SqlAlchemyArticleRepository"]

class SqlAlchemyArticleRepository(IArticleRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, article: Article) -> Article:
        self.db.add(article)
        await self.db.commit()
        await self.db.refresh(article)
        return article

    async def find_by_slug(self, slug: str) -> Optional[Article]:
        query = select(Article).where(Article.slug == slug)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def find_all(self, skip: int, limit: int) -> List[Article]:
        query = select(Article).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def delete(self, article: Article) -> None:
        await self.db.delete(article)
        await self.db.commit()
