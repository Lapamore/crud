from ..commands.DeleteArticleCommand import DeleteArticleCommand
from ..repositories.core.IArticleWriteRepository import IArticleWriteRepository
from ..exceptions.ArticleNotFoundException import ArticleNotFoundException
from ..exceptions.NotAuthorizedToModifyArticleException import NotAuthorizedToModifyArticleException

__all__ = ["DeleteArticleHandler"]


class DeleteArticleHandler:
    def __init__(self, repository: IArticleWriteRepository):
        self._repository = repository

    async def handle(self, command: DeleteArticleCommand) -> None:
        article = await self._repository.find_by_slug(command.slug)
        
        if article is None:
            raise ArticleNotFoundException(command.slug)
        
        if article.author_id != command.user_id:
            raise NotAuthorizedToModifyArticleException()

        await self._repository.delete(article)
