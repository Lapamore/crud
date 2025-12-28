from models import Comment
from ..commands.CreateCommentCommand import CreateCommentCommand
from ..repositories.core.ICommentWriteRepository import ICommentWriteRepository


class CreateCommentHandler:
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
