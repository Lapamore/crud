from fastapi import Depends, HTTPException
from dishka import FromDishka
from dishka.integrations.fastapi import inject
from slugify import slugify

from core import get_current_user, AuthenticatedUser
from ..schemas import ArticleResponse, ArticleUpdate
from modules.articles.handlers.commands.core import IUpdateArticleHandler
from modules.articles.handlers.queries.core import IGetArticleBySlugHandler
from modules.articles.models.commands import UpdateArticleCommand
from modules.articles.models.queries import GetArticleBySlugQuery
from modules.articles.exceptions import ArticleNotFoundException, NotAuthorizedToModifyArticleException

__all__ = ["UpdateArticleCommandView"]


class UpdateArticleCommandView:
    @inject
    async def __call__(
        self,
        slug: str,
        article_in: ArticleUpdate,
        command_handler: FromDishka[IUpdateArticleHandler],
        query_handler: FromDishka[IGetArticleBySlugHandler],
        current_user: AuthenticatedUser = Depends(get_current_user)
    ) -> ArticleResponse:
        
        command = UpdateArticleCommand(
            slug=slug,
            user_id=current_user.id,
            title=article_in.title,
            description=article_in.description,
            body=article_in.body,
            tag_list=article_in.tagList,
        )
        
        try:
            await command_handler(command)
        except ArticleNotFoundException:
            raise HTTPException(status_code=404, detail="Article not found")
        except NotAuthorizedToModifyArticleException:
            raise HTTPException(status_code=403, detail="Not authorized to update this article")
        
        new_slug = slugify(command.title) if command.title else slug
        
        query = GetArticleBySlugQuery(slug=new_slug)
        updated_article = await query_handler(query)
        
        return updated_article
