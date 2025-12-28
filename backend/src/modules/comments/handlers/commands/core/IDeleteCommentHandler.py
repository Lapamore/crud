from abc import ABC, abstractmethod
from ....models.commands import DeleteCommentCommand

__all__ = ["IDeleteCommentHandler"]


class IDeleteCommentHandler(ABC):

    @abstractmethod
    async def __call__(self, command: DeleteCommentCommand) -> None:
        raise NotImplementedError
