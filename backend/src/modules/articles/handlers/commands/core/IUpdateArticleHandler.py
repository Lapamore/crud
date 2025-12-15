from abc import ABC, abstractmethod

from ....models.commands import UpdateArticleCommand

__all__ = ["IDeleteArticleHandler"]


class IUpdateArticleHandler(ABC):

    @abstractmethod
    async def __call__(self, command: UpdateArticleCommand):
        raise NotImplementedError