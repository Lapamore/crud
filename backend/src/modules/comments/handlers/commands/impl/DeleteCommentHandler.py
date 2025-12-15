from ....models.commands import DeleteCommentCommand
from ....exceptions import (
    CommentNotFoundException,
    NotAuthorizedToDeleteCommentException
)
from ..core import IDeleteCommentHandler
from comments.repositories.core import ICommentWriteRepository

__all__ = ["DeleteCommentHandler"]


class DeleteCommentHandler(IDeleteCommentHandler):
    def __init__(self, repository: ICommentWriteRepository):
        self._repository = repository

    async def handle(self, command: DeleteCommentCommand) -> None:
        comment = await self._repository.find_by_id(command.comment_id)
        
        if comment is None:
            raise CommentNotFoundException(command.comment_id)
        
        if comment.author_id != command.user_id:
            raise NotAuthorizedToDeleteCommentException()

        await self._repository.delete(comment)
