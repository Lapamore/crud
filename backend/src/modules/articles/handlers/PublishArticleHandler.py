from core.enums import ArticleStatus
from core.tasker.core.ITaskProducer import ITaskProducer
from ..repositories.core import IArticleWriteRepository
from ..commands.PublishArticleCommand import PublishArticleCommand
from ..exceptions import ArticleNotFoundException, NotAuthorizedToModifyArticleException, ArticleNotInDraftException


class PublishArticleHandler:
    """
    Handler для публикации статьи.
    Начинает SAGA: переводит статус в PENDING_PUBLISH и ставит задачу post.moderate в очередь.
    """

    def __init__(self, repository: IArticleWriteRepository, task_producer: ITaskProducer):
        self._repository = repository
        self._task_producer = task_producer

    async def handle(self, command: PublishArticleCommand) -> dict:
        article = await self._repository.find_by_id(command.article_id)
        
        if not article:
            raise ArticleNotFoundException()
        
        if article.author_id != command.user_id:
            raise NotAuthorizedToModifyArticleException()
        
        if article.status != ArticleStatus.DRAFT.value:
            raise ArticleNotInDraftException()
        
        article.status = ArticleStatus.PENDING_PUBLISH.value
        await self._repository.update(article)
        
        self._task_producer.send_task(
            "post.moderate",
            {
                "post_id": article.id,
                "author_id": article.author_id,
                "title": article.title,
                "body": article.body,
                "requested_by": command.user_id
            }
        )
        
        return {
            "id": article.id,
            "status": article.status,
            "message": "Article submitted for moderation"
        }
