from typing import List
from abc import abstractmethod, ABC

from ....dto import ArticleDTO
from ....models.queries import ListArticlesQuery

__all__ = ["IGetListArticlesHandler"]


class IGetListArticlesHandler(ABC):

    @abstractmethod
    async def handle(self, query: ListArticlesQuery) -> List[ArticleDTO]:
        raise NotImplementedError