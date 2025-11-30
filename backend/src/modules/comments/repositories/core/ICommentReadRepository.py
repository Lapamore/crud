from abc import ABC, abstractmethod
from typing import Optional, List
from src.models.Comment import Comment


class ICommentReadRepository(ABC):
    @abstractmethod
    async def find_by_id(self, comment_id: int) -> Optional[Comment]:
        raise NotImplementedError

    @abstractmethod
    async def find_by_article_slug(self, slug: str) -> List[Comment]:
        raise NotImplementedError
