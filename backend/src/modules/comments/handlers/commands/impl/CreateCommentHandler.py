from models import Comment
from ..core import ICreateCommentHandler
from ....models.commands import CreateCommentCommand
from comments.repositories.core import ICommentWriteRepository

__all__ = ["CreateCommentHandler"]


class CreateCommentHandler(ICreateCommentHandler):
    def __init__(self, repository: ICommentWriteRepository):
        self._repository = repository

    async def handle(self, command: CreateCommentCommand) -> int:
        comment = Comment(
            body=command.body,
            article_id=command.article_id,
            author_id=command.author_id,
        )
        saved_comment = await self._repository.save(comment)
        return saved_comment.id
