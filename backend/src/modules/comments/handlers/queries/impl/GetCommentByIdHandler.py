from ..core import IGetCommentByIdHandler
from ....dto import CommentDTO
from ....models.queries import GetCommentByIdQuery
from ....exceptions import CommentNotFoundException
from modules.comments.repositories.core import ICommentReadRepository

__all__ = ["GetCommentByIdHandler"]


class GetCommentByIdHandler(IGetCommentByIdHandler):
    def __init__(self, repository: ICommentReadRepository):
        self._repository = repository

    async def handle(self, query: GetCommentByIdQuery) -> CommentDTO:
        comment = await self._repository.find_by_id(query.comment_id)
        
        if comment is None:
            raise CommentNotFoundException(query.comment_id)

        return CommentDTO(
            id=comment.id,
            body=comment.body,
            article_id=comment.article_id,
            author_id=comment.author_id,
        )
