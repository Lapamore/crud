from fastapi import HTTPException
from dishka import FromDishka
from dishka.integrations.fastapi import inject

from ..schemas import ArticleResponse
from modules.articles.handlers.queries.core import IGetArticleBySlugHandler
from modules.articles.models.queries import GetArticleBySlugQuery
from modules.articles.exceptions import ArticleNotFoundException

__all__ = ["GetArticleBySlugQueryView"]


class GetArticleBySlugQueryView:
    @inject
    async def __call__(
        self,
        slug: str,
        query_handler: FromDishka[IGetArticleBySlugHandler],
    ) -> ArticleResponse:
        
        query = GetArticleBySlugQuery(slug=slug)
        
        try:
            article = await query_handler(query)
        except ArticleNotFoundException:
            raise HTTPException(status_code=404, detail="Article not found")
        
        return article
