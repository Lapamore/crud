from fastapi import APIRouter, status, FastAPI
from dishka.integrations.fastapi import DishkaRoute

from .views.CreateCommentCommandView import CreateCommentCommandView
from .views.GetCommentsByArticleSlugQueryView import GetCommentsByArticleSlugQueryView
from .views.DeleteCommentCommandView import DeleteCommentCommandView

__all__ = ["CommentRouter"]


class CommentRouter:
    def __call__(self, app: FastAPI):
        create_comment_view = CreateCommentCommandView()
        list_comments_view = GetCommentsByArticleSlugQueryView()
        delete_comment_view = DeleteCommentCommandView()

        router = APIRouter(route_class=DishkaRoute, tags=["Comments"])

        router.add_api_route(
            path="/articles/{slug}/comments",
            methods=["POST"],
            endpoint=create_comment_view.__call__,
            status_code=status.HTTP_201_CREATED
        )

        router.add_api_route(
            path="/articles/{slug}/comments",
            methods=["GET"],
            endpoint=list_comments_view.__call__
        )

        router.add_api_route(
            path="/articles/{slug}/comments/{comment_id}",
            methods=["DELETE"],
            endpoint=delete_comment_view.__call__,
            status_code=status.HTTP_204_NO_CONTENT
        )

        app.include_router(router, prefix="/api")
