from abc import ABC, abstractmethod
from typing import Optional
from models import Article


class IArticleWriteRepository(ABC):
    @abstractmethod
    async def save(self, article: Article) -> Article:
        raise NotImplementedError

    @abstractmethod
    async def find_by_slug(self, slug: str) -> Optional[Article]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, article: Article) -> Article:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, article: Article) -> None:
        raise NotImplementedError
