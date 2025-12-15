from fastapi import APIRouter, status, FastAPI
from dishka.integrations.fastapi import DishkaRoute

from .views.CreateArticleCommandView import CreateArticleCommandView
from .views.GetListArticlesQueryView import GetListArticlesQueryView
from .views.GetArticleBySlugQueryView import GetArticleBySlugQueryView
from .views.UpdateArticleCommandView import UpdateArticleCommandView
from .views.DeleteArticleCommandView import DeleteArticleCommandView

__all__ = ["ArticleRouter"]


class ArticleRouter:
    def __call__(self, app: FastAPI):
        create_article_view = CreateArticleCommandView()
        list_articles_view = GetListArticlesQueryView()
        get_article_view = GetArticleBySlugQueryView()
        update_article_view = UpdateArticleCommandView()
        delete_article_view = DeleteArticleCommandView()

        router = APIRouter(route_class=DishkaRoute, tags=["Articles"])

        router.add_api_route(
            path="/articles",
            methods=["GET"],
            endpoint=list_articles_view.__call__,
        )

        router.add_api_route(
            path="/articles",
            methods=["POST"],
            endpoint=create_article_view.__call__,
            status_code=status.HTTP_201_CREATED
        )

        router.add_api_route(
            path="/articles/{slug}",
            methods=["GET"],
            endpoint=get_article_view.__call__
        )

        router.add_api_route(
            path="/articles/{slug}",
            methods=["PUT"],
            endpoint=update_article_view.__call__
        )

        router.add_api_route(
            path="/articles/{slug}",
            methods=["DELETE"],
            endpoint=delete_article_view.__call__,
            status_code=status.HTTP_204_NO_CONTENT
        )

        app.include_router(router, prefix="/api")
