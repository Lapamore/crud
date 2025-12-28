from fastapi import Depends, HTTPException
from fastapi.responses import Response
from dishka import FromDishka
from dishka.integrations.fastapi import inject

from core import get_current_user, AuthenticatedUser
from modules.articles.handlers.commands.core import IDeleteArticleHandler
from modules.articles.models.commands import DeleteArticleCommand
from modules.articles.exceptions import ArticleNotFoundException, NotAuthorizedToModifyArticleException

__all__ = ["DeleteArticleCommandView"]


class DeleteArticleCommandView:
    @inject
    async def __call__(
        self,
        slug: str,
        command_handler: FromDishka[IDeleteArticleHandler],
        current_user: AuthenticatedUser = Depends(get_current_user)
    ) -> None:
        
        command = DeleteArticleCommand(slug=slug, user_id=current_user.id)
        
        try:
            await command_handler(command)
        except ArticleNotFoundException:
            raise HTTPException(status_code=404, detail="Article not found")
        except NotAuthorizedToModifyArticleException:
            raise HTTPException(status_code=403, detail="Not authorized to delete this article")
        
        return Response(status_code=204)
