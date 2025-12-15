from slugify import slugify

from models import Article
from ..core import ICreateArticleHandler
from ....models.commands import CreateArticleCommand
from ....exceptions import SlugAlreadyExistsException
from ....repositories.core import IArticleWriteRepository

__all__ = ["CreateArticleHandler"]


class CreateArticleHandler(ICreateArticleHandler):
    def __init__(self, repository: IArticleWriteRepository):
        self._repository = repository

    async def __call__(self, command: CreateArticleCommand) -> int:
        slug = slugify(command.title)
        
        if await self._repository.find_by_slug(slug):
            raise SlugAlreadyExistsException(slug)

        article = Article(
            title=command.title,
            description=command.description,
            body=command.body,
            slug=slug,
            author_id=command.author_id,
            tags=command.tag_list,
        )
        
        saved_article = await self._repository.save(article)
        command.id = saved_article.id
