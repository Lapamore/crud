from typing import Optional, List
from pydantic import BaseModel

__all__ = ["ArticleUpdate"]


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    body: Optional[str] = None
    tagList: Optional[List[str]] = None
