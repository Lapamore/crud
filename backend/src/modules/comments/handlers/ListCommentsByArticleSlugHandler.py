from typing import List
from ..queries.ListCommentsByArticleSlugQuery import ListCommentsByArticleSlugQuery
from ..repositories.core.ICommentReadRepository import ICommentReadRepository
from ..dto.CommentDTO import CommentDTO


class ListCommentsByArticleSlugHandler:
    def __init__(self, repository: ICommentReadRepository):
        self._repository = repository

    async def handle(self, query: ListCommentsByArticleSlugQuery) -> List[CommentDTO]:
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
