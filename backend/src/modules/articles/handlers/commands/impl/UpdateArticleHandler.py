from slugify import slugify

from ..core import IUpdateArticleHandler
from ....web.schemas import ArticleResponse
from ....models.commands import UpdateArticleCommand
from ....exceptions import ArticleNotFoundException, NotAuthorizedToModifyArticleException
from ....repositories.core import IArticleWriteRepository, IArticleReadRepository

__all__ = ["UpdateArticleHandler"]


class UpdateArticleHandler(IUpdateArticleHandler):
    def __init__(
            self, 
            write_repository: IArticleWriteRepository,
            read_repository: IArticleReadRepository
            ):
        self._read_repository = read_repository
        self._write_repository = write_repository

    async def __call__(self, command: UpdateArticleCommand) -> ArticleResponse:
        article = await self._read_repository.find_by_slug(command.slug)
        
        if article is None:
            raise ArticleNotFoundException(command.slug)
        
        if article.author_id != command.user_id:
            raise NotAuthorizedToModifyArticleException()

        if command.title is not None:
            article.title = command.title
            article.slug = slugify(command.title)
        
        if command.description is not None:
            article.description = command.description
        
        if command.body is not None:
            article.body = command.body
        
        if command.tag_list is not None:
            article.tags = command.tag_list

        updated_article = await self._write_repository.update(article)
        return updated_article
