from abc import ABC, abstractmethod
from ....models.commands import DeleteCommentCommand

__all__ = ["IDeleteCommentHandler"]


class IDeleteCommentHandler(ABC):

    @abstractmethod
    async def handle(self, command: DeleteCommentCommand) -> None:
        raise NotImplementedError
