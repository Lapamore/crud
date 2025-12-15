from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.Article import Article
from ..core.IArticleWriteRepository import IArticleWriteRepository


class ArticleWriteRepository(IArticleWriteRepository):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def save(self, article: Article) -> Article:
        self._db.add(article)
        await self._db.commit()
        await self._db.refresh(article)
        return article

    async def find_by_slug(self, slug: str) -> Optional[Article]:
        query = select(Article).where(Article.slug == slug)
        result = await self._db.execute(query)
        return result.scalar_one_or_none()

    async def update(self, article: Article) -> Article:
        self._db.add(article)
        await self._db.commit()
        await self._db.refresh(article)
        return article

    async def delete(self, article: Article) -> None:
        await self._db.delete(article)
        await self._db.commit()
