from slugify import slugify

from models import Article
from ..core import ICreateArticleHandler
from ....models.commands import CreateArticleCommand
from ....exceptions import SlugAlreadyExistsException
from ....repositories.core import IArticleReadRepository, IArticleWriteRepository
from .....articles.web.schemas import ArticleResponse

__all__ = ["CreateArticleHandler"]


class CreateArticleHandler(ICreateArticleHandler):
    def __init__(
            self, 
            read_repository: IArticleReadRepository,
            write_repository: IArticleWriteRepository
        ) -> None:
        self._read_repository = read_repository
        self._write_repository = write_repository

    async def __call__(self, command: CreateArticleCommand, user_id: int) -> ArticleResponse:
        slug = slugify(command.title)
        
        if await self._read_repository.find_by_slug(slug):
            raise SlugAlreadyExistsException(slug)

        article = Article(
            title=command.title,
            description=command.description,
            body=command.body,
            slug=slug,
            author_id=user_id,
            tags=command.tag_list,
        )
        
        saved_article = await self._write_repository.save(article)
        return ArticleResponse(
            id=saved_article.id,
            title=saved_article.title,
            slug=saved_article.slug,
            description=saved_article.description,
            body=saved_article.body,
            author_id=saved_article.author_id,
            tags=saved_article.tags
        )