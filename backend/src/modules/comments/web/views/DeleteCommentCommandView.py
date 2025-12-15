from fastapi import Depends, HTTPException
from dishka import FromDishka
from dishka.integrations.fastapi import inject

from core import get_current_user, AuthenticatedUser
from modules.comments.handlers.commands.core import IDeleteCommentHandler
from modules.comments.models.commands import DeleteCommentCommand
from modules.comments.exceptions import CommentNotFoundException, NotAuthorizedToDeleteCommentException
from modules.articles.exceptions import ArticleNotFoundException

__all__ = ["DeleteCommentCommandView"]


class DeleteCommentCommandView:
    @inject
    async def __call__(
        self,
        slug: str,
        comment_id: int,
        command_handler: FromDishka[IDeleteCommentHandler],
        current_user: AuthenticatedUser = Depends(get_current_user)
    ) -> None:
        
        command = DeleteCommentCommand(
            slug=slug,
            comment_id=comment_id,
            user_id=current_user.id
        )
        
        try:
            await command_handler(command)
        except ArticleNotFoundException:
            raise HTTPException(status_code=404, detail="Article not found")
        except CommentNotFoundException:
            raise HTTPException(status_code=404, detail="Comment not found")
        except NotAuthorizedToDeleteCommentException:
            raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
        
        return
