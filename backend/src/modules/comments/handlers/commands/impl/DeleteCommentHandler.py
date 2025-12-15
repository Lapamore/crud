from ....models.commands import DeleteCommentCommand
from ....exceptions import (
    CommentNotFoundException,
    NotAuthorizedToDeleteCommentException
)
from ..core import IDeleteCommentHandler
from modules.comments.repositories.core import ICommentWriteRepository
from modules.articles.repositories.core import IArticleReadRepository
from modules.articles.exceptions import ArticleNotFoundException

__all__ = ["DeleteCommentHandler"]


class DeleteCommentHandler(IDeleteCommentHandler):
    def __init__(
        self, 
        repository: ICommentWriteRepository,
        article_repository: IArticleReadRepository
    ):
        self._repository = repository
        self._article_repository = article_repository

    async def __call__(self, command: DeleteCommentCommand) -> None:
        article = await self._article_repository.find_by_slug(command.slug)
        if article is None:
            raise ArticleNotFoundException(command.slug)

        comment = await self._repository.find_by_id(command.comment_id)
        
        if comment is None:
            raise CommentNotFoundException(command.comment_id)
        
        if comment.author_id != command.user_id:
            raise NotAuthorizedToDeleteCommentException()

        await self._repository.delete(comment)
