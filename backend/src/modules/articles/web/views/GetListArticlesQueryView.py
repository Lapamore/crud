from typing import List

from fastapi import Depends
from dishka import FromDishka
from dishka.integrations.fastapi import inject

from core import get_current_user, AuthenticatedUser
from ..schemas import ArticleResponse
from modules.articles.handlers.queries.core import IGetListArticlesHandler
from modules.articles.models.queries import ListArticlesQuery

__all__ = ["GetListArticlesQueryView"]


class GetListArticlesQueryView:
    @inject
    async def __call__(
        self,
        skip: int,
        limit: int,
        query_handler: FromDishka[IGetListArticlesHandler],
        current_user: AuthenticatedUser = Depends(get_current_user)
    ) -> List[ArticleResponse]:
        
        query = ListArticlesQuery(skip=skip, limit=limit)
        articles = await query_handler(query)
        
        return articles
