from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models import Article
from ..core import IArticleWriteRepository

__all__ = ["ArticleWriteRepository"]


class ArticleWriteRepository(IArticleWriteRepository):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def save(self, article: Article) -> Article:
        self._db.add(article)
        await self._db.commit()
        await self._db.refresh(article)
        return article

    async def update(self, article: Article) -> Article:
        self._db.add(article)
        await self._db.commit()
        await self._db.refresh(article)
        return article

    async def delete(self, article: Article) -> None:
        await self._db.delete(article)
        await self._db.commit()
