from slugify import slugify
from src.models.Article import Article
from ..commands.CreateArticleCommand import CreateArticleCommand
from ..repositories.core.IArticleWriteRepository import IArticleWriteRepository
from ..exceptions.SlugAlreadyExistsException import SlugAlreadyExistsException


class CreateArticleHandler:
    def __init__(self, repository: IArticleWriteRepository):
        self._repository = repository

    async def handle(self, command: CreateArticleCommand) -> int:
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
        return saved_article.id
