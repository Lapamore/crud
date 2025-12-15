from abc import ABC, abstractmethod

from ....dto import ArticleDTO
from ....models.queries import GetArticleBySlugQuery

__all__ = ["IGetArticleBySlugHandler"]


class IGetArticleBySlugHandler(ABC):

    @abstractmethod
    async def handle(self, query: GetArticleBySlugQuery) -> ArticleDTO:
        raise NotImplementedError