from dishka import Provider, Scope

from handlers.commands.core import ICreateArticleHandler, IDeleteArticleHandler, IUpdateArticleHandler
from handlers.commands.impl import CreateArticleHandler, DeleteArticleHandler, UpdateArticleHandler

from handlers.queries.core import IGetArticleBySlugHandler, IGetListArticlesHandler
from handlers.queries.impl import GetArticleBySlugHandler, GetListArticlesHandler

from repositories.core import IArticleReadRepository, IArticleWriteRepository
from repositories.impl import ArticleReadRepository, ArticleWriteRepository

__all__ = ["ArcticlesApp"]


class ArcticlesApp:
    def __call__(self) -> Provider:
        provider = Provider(scope=Scope.REQUEST)
        
        provider.provide(CreateArticleHandler, provides=ICreateArticleHandler)
        provider.provide(DeleteArticleHandler, provides=IDeleteArticleHandler)
        provider.provide(UpdateArticleHandler, provides=IUpdateArticleHandler)
        provider.provide(GetArticleBySlugHandler, provides=IGetArticleBySlugHandler)
        provider.provide(GetListArticlesHandler, provides=IGetListArticlesHandler)

        provider.provide(ArticleReadRepository, provides=IArticleReadRepository)
        provider.provide(ArticleWriteRepository, provides=IArticleWriteRepository)
        
        return provider
