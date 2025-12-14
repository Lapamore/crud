from slugify import slugify

from ....models import Article
from ....core.tasker.core import ITaskProducer
from ..commands.CreateArticleCommand import CreateArticleCommand
from ..repositories.core.IArticleWriteRepository import IArticleWriteRepository
from ..exceptions.SlugAlreadyExistsException import SlugAlreadyExistsException


class CreateArticleHandler:
    def __init__(self, repository: IArticleWriteRepository, task_producer: ITaskProducer):
        self._repository = repository
        self._task_producer = task_producer

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
        
        self._task_producer.send_task(
            "notify_followers",
            kwargs={
                "author_id": command.author_id,
                "post_id": saved_article.id,
                "post_title": saved_article.title
            }
        )

        return saved_article.id
