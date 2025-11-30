from abc import ABC, abstractmethod
from typing import Optional, List
from src.models.Comment import Comment


class ICommentWriteRepository(ABC):
    @abstractmethod
    async def save(self, comment: Comment) -> Comment:
        raise NotImplementedError

    @abstractmethod
    async def find_by_id(self, comment_id: int) -> Optional[Comment]:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, comment: Comment) -> None:
        raise NotImplementedError
