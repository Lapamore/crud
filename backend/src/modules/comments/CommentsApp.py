from dishka import Provider, Scope

from .handlers.commands.core import ICreateCommentHandler, IDeleteCommentHandler
from .handlers.commands.impl import CreateCommentHandler, DeleteCommentHandler

from .handlers.queries.core import IGetCommentByIdHandler, IListCommentsByArticleSlugHandler
from .handlers.queries.impl import GetCommentByIdHandler, ListCommentsByArticleSlugHandler

from .repositories.core import ICommentReadRepository, ICommentWriteRepository
from .repositories.impl import CommentReadRepository, CommentWriteRepository

__all__ = ["CommentsApp"]


class CommentsApp:
    def __call__(self) -> Provider:
        provider = Provider(scope=Scope.REQUEST)
        
        provider.provide(CreateCommentHandler, provides=ICreateCommentHandler)
        provider.provide(DeleteCommentHandler, provides=IDeleteCommentHandler)
        
        provider.provide(GetCommentByIdHandler, provides=IGetCommentByIdHandler)
        provider.provide(ListCommentsByArticleSlugHandler, provides=IListCommentsByArticleSlugHandler)

        provider.provide(CommentReadRepository, provides=ICommentReadRepository)
        provider.provide(CommentWriteRepository, provides=ICommentWriteRepository)
        
        return provider
