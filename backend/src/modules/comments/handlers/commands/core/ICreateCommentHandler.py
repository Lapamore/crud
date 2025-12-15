from abc import ABC, abstractmethod
from ....models.commands import CreateCommentCommand

__all__ = ["ICreateCommentHandler"]


class ICreateCommentHandler(ABC):
    @abstractmethod
    async def handle(self, command: CreateCommentCommand) -> int:
        raise NotImplementedError
