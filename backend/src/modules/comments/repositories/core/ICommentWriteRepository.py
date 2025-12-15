from abc import ABC, abstractmethod

from models import Comment

__all__ = ["ICommentWriteRepository"]


class ICommentWriteRepository(ABC):
    @abstractmethod
    async def save(self, comment: Comment) -> Comment:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, comment: Comment) -> None:
        raise NotImplementedError
