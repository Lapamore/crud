from slugify import slugify
from ..commands.UpdateArticleCommand import UpdateArticleCommand
from ..repositories.core.IArticleWriteRepository import IArticleWriteRepository
from ..exceptions.ArticleNotFoundException import ArticleNotFoundException
from ..exceptions.NotAuthorizedToModifyArticleException import NotAuthorizedToModifyArticleException

__all__ = ["UpdateArticleHandler"]


class UpdateArticleHandler:
    def __init__(self, repository: IArticleWriteRepository):
        self._repository = repository

    async def handle(self, command: UpdateArticleCommand) -> int:
        article = await self._repository.find_by_slug(command.slug)
        
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

        updated_article = await self._repository.update(article)
        return updated_article.id
