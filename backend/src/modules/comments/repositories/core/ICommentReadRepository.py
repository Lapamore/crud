from abc import ABC, abstractmethod
from typing import Optional, List

from models import Comment

__all__ = ["ICommentReadRepository"]


class ICommentReadRepository(ABC):
    @abstractmethod
    async def find_by_id(self, comment_id: int) -> Optional[Comment]:
        raise NotImplementedError

    @abstractmethod
    async def find_by_article_slug(self, slug: str) -> List[Comment]:
        raise NotImplementedError
