from abc import ABC, abstractmethod

from ....models.commands import CreateArticleCommand

__all__ = ["ICreateArticleHandler"]


class ICreateArticleHandler(ABC):
    
    @abstractmethod
    async def __call__(self, command: CreateArticleCommand):
        raise NotImplementedError