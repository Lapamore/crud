from typing import Optional, List
from pydantic import BaseModel


class ArticleBase(BaseModel):
    title: str
    description: str
    body: str
    tagList: Optional[List[str]] = []
