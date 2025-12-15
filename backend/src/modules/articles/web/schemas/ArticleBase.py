from typing import Optional, List
from pydantic import BaseModel

__all__ = ["ArticleBase"]


class ArticleBase(BaseModel):
    title: str
    description: str
    body: str
    tagList: Optional[List[str]] = []
