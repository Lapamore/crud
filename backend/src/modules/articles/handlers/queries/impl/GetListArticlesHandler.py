from typing import List

from ....dto import ArticleDTO
from ....models.queries import ListArticlesQuery
from ....repositories.core import IArticleReadRepository

__all__ = ["GetListArticlesHandler"]


class GetListArticlesHandler:
    def __init__(self, repository: IArticleReadRepository):
        self._repository = repository

    async def __call__(self, query: ListArticlesQuery) -> List[ArticleDTO]:
        articles = await self._repository.find_all(query.skip, query.limit)
        return [ArticleDTO.model_validate(article) for article in articles]
