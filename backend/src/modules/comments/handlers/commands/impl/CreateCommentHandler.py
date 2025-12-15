from models import Comment
from ..core import ICreateCommentHandler
from ....models.commands import CreateCommentCommand
from modules.comments.repositories.core import ICommentWriteRepository
from modules.articles.repositories.core import IArticleReadRepository
from modules.articles.exceptions import ArticleNotFoundException

__all__ = ["CreateCommentHandler"]


class CreateCommentHandler(ICreateCommentHandler):
    def __init__(
        self, 
        repository: ICommentWriteRepository,
        article_repository: IArticleReadRepository
    ):
        self._repository = repository
        self._article_repository = article_repository

    async def __call__(self, command: CreateCommentCommand) -> int:
        article = await self._article_repository.find_by_slug(command.article_slug)
        if article is None:
            raise ArticleNotFoundException(command.article_slug)

        comment = Comment(
            body=command.body,
            article_id=article.id,
            author_id=command.author_id,
        )
        saved_comment = await self._repository.save(comment)
        return saved_comment.id
