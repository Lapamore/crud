from typing import List
from fastapi import HTTPException
from dishka import FromDishka
from dishka.integrations.fastapi import inject

from ..schemas import CommentResponse
from modules.comments.handlers.queries.core import IListCommentsByArticleSlugHandler
from modules.comments.models.queries import ListCommentsByArticleSlugQuery
from modules.articles.exceptions import ArticleNotFoundException

__all__ = ["GetCommentsByArticleSlugQueryView"]


class GetCommentsByArticleSlugQueryView:
    @inject
    async def __call__(
        self,
        slug: str,
        query_handler: FromDishka[IListCommentsByArticleSlugHandler],
    ) -> List[CommentResponse]:
        
        query = ListCommentsByArticleSlugQuery(slug=slug)
        
        try:
            comments = await query_handler(query)
        except ArticleNotFoundException:
            raise HTTPException(status_code=404, detail="Article not found")
        
        return comments
