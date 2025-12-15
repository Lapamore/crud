from abc import ABC, abstractmethod

from models import Article

__all__ = ["IArticleWriteRepository"]


class IArticleWriteRepository(ABC):
    @abstractmethod
    async def save(self, article: Article) -> Article:
        raise NotImplementedError
    
    @abstractmethod
    async def update(self, article: Article) -> Article:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, article: Article) -> None:
        raise NotImplementedError
