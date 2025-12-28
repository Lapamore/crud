from typing import List
from abc import ABC, abstractmethod

from ....models.queries import ListCommentsByArticleSlugQuery
from ....dto import CommentDTO

__all__ = ["IListCommentsByArticleSlugHandler"]


class IListCommentsByArticleSlugHandler(ABC):
    @abstractmethod
    async def __call__(self, query: ListCommentsByArticleSlugQuery) -> List[CommentDTO]:
        raise NotImplementedError