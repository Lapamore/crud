from fastapi import Depends
from dishka import FromDishka
from dishka.integrations.fastapi import inject

from core import get_current_user
from ..schemas import AuthenticatedUser, ArticleResponse
from modules.articles.handlers.commands.core import ICreateArticleHandler
from modules.articles.models.commands import CreateArticleCommand

__all__ = ["CreateArticleCommandView"]


class CreateArticleCommandView:
    @inject
    async def __call__(
        self,
        request: CreateArticleCommand,
        command_handler: FromDishka[ICreateArticleHandler],
        current_user: AuthenticatedUser = Depends(get_current_user)
    ) -> ArticleResponse:
        command = CreateArticleCommand(
            title=request.title,
            description=request.description,
            body=request.body,
            author_id=current_user.id,
            tag_list=request.tagList,
        )

        article = await command_handler(command=command)

        return article
