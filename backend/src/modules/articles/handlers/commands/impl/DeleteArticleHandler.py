from ..core import IDeleteArticleHandler
from ....models.commands import DeleteArticleCommand
from ....exceptions import ArticleNotFoundException, NotAuthorizedToModifyArticleException
from ....repositories.core import IArticleWriteRepository, IArticleReadRepository

__all__ = ["DeleteArticleHandler"]



class DeleteArticleHandler(IDeleteArticleHandler):
    def __init__(
            self, 
            read_repository: IArticleReadRepository,
            write_repository: IArticleWriteRepository
        ) -> None:
        self._read_repository = read_repository
        self._write_repository = write_repository

    async def __call__(self, command: DeleteArticleCommand) -> None:
        article = await self._read_repository.find_by_slug(command.slug)
        
        if article is None:
            raise ArticleNotFoundException(command.slug)
        
        if article.author_id != command.user_id:
            raise NotAuthorizedToModifyArticleException()

        await self._write_repository.delete(article)
