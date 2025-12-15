from ..core import IDeleteArticleHandler
from ....models.commands import DeleteArticleCommand
from ....exceptions import ArticleNotFoundException, NotAuthorizedToModifyArticleException
from ....repositories.core import IArticleWriteRepository

__all__ = ["DeleteArticleHandler"]



class DeleteArticleHandler(IDeleteArticleHandler):
    def __init__(self, repository: IArticleWriteRepository):
        self._repository = repository

    async def __call__(self, command: DeleteArticleCommand) -> None:
        article = await self._repository.find_by_slug(command.slug)
        
        if article is None:
            raise ArticleNotFoundException(command.slug)
        
        if article.author_id != command.user_id:
            raise NotAuthorizedToModifyArticleException()

        await self._repository.delete(article)
