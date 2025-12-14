from typing import List, Optional
from .....models.Article import Article

__all__ = ["IArticleRepository"]

class IArticleRepository:
    async def save(self, article: Article) -> Article:
        raise NotImplementedError

    async def find_by_slug(self, slug: str) -> Optional[Article]:
        raise NotImplementedError

    async def find_all(self, skip: int, limit: int) -> List[Article]:
        raise NotImplementedError

    async def delete(self, article: Article) -> None:
        raise NotImplementedError
