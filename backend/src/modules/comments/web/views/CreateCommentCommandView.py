from fastapi import Depends, HTTPException
from dishka import FromDishka
from dishka.integrations.fastapi import inject

from core import get_current_user, AuthenticatedUser
from ..schemas import CommentCreate, CommentResponse
from modules.comments.handlers.commands.core import ICreateCommentHandler
from modules.comments.handlers.queries.core import IGetCommentByIdHandler
from modules.comments.models.commands import CreateCommentCommand
from modules.comments.models.queries import GetCommentByIdQuery
from modules.articles.exceptions import ArticleNotFoundException

__all__ = ["CreateCommentCommandView"]


class CreateCommentCommandView:
    @inject
    async def __call__(
        self,
        slug: str,
        comment_in: CommentCreate,
        command_handler: FromDishka[ICreateCommentHandler],
        comment_query_handler: FromDishka[IGetCommentByIdHandler],
        current_user: AuthenticatedUser = Depends(get_current_user)
    ) -> CommentResponse:
        
        command = CreateCommentCommand(
            body=comment_in.body,
            article_slug=slug,
            author_id=current_user.id,
        )
        try:
            comment = await command_handler(command)
        except ArticleNotFoundException:
            raise HTTPException(status_code=404, detail="Article not found")
        
        return comment
