from abc import ABC, abstractmethod

from ....models.commands import DeleteArticleCommand

__all__ = ["IDeleteArticleHandler"]


class IDeleteArticleHandler(ABC):

    @abstractmethod
    async def __call__(self, command: DeleteArticleCommand) -> None:
        raise NotImplementedError