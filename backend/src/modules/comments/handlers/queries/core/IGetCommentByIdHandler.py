from abc import ABC, abstractmethod

from ....dto import CommentDTO
from ....models.queries import GetCommentByIdQuery

__all__ = ["IGetCommentByIdHandler"]


class IGetCommentByIdHandler(ABC):
    @abstractmethod
    async def handle(self, query: GetCommentByIdQuery) -> CommentDTO:
        raise NotImplementedError
