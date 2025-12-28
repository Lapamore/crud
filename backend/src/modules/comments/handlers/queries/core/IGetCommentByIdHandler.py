from abc import ABC, abstractmethod

from ....dto import CommentDTO
from ....models.queries import GetCommentByIdQuery

__all__ = ["IGetCommentByIdHandler"]


class IGetCommentByIdHandler(ABC):
    @abstractmethod
    async def __call__(self, query: GetCommentByIdQuery) -> CommentDTO:
        raise NotImplementedError
