from abc import ABC, abstractmethod
from typing import Optional, List
from models import Article


class IArticleReadRepository(ABC):
    @abstractmethod
    async def find_by_slug(self, slug: str) -> Optional[Article]:
        raise NotImplementedError

    @abstractmethod
    async def find_all(self, skip: int, limit: int) -> List[Article]:
        raise NotImplementedError
