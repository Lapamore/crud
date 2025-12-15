from typing import List

from ....dto import CommentDTO
from ..core import IListCommentsByArticleSlugHandler
from ....models.queries import ListCommentsByArticleSlugQuery
from modules.comments.repositories.core import ICommentReadRepository
from modules.articles.repositories.core import IArticleReadRepository
from modules.articles.exceptions import ArticleNotFoundException

__all__ = ["ListCommentsByArticleSlugHandler"]


class ListCommentsByArticleSlugHandler(IListCommentsByArticleSlugHandler):
    def __init__(
        self, 
        repository: ICommentReadRepository,
        article_repository: IArticleReadRepository
    ):
        self._repository = repository
        self._article_repository = article_repository

    async def __call__(self, query: ListCommentsByArticleSlugQuery) -> List[CommentDTO]:
        article = await self._article_repository.find_by_slug(query.slug)
        if article is None:
            raise ArticleNotFoundException(query.slug)

        comments = await self._repository.find_by_article_slug(query.slug)
        
        return [
            CommentDTO(
                id=comment.id,
                body=comment.body,
                article_id=comment.article_id,
                author_id=comment.author_id,
            )
            for comment in comments
        ]
