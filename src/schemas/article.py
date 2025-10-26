from typing import Optional, List
from pydantic import BaseModel


class ArticleBase(BaseModel):
    title: str
    description: str
    body: str
    tagList: Optional[List[str]] = []


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    body: Optional[str] = None
    tagList: Optional[List[str]] = None


class Article(ArticleBase):
    id: int
    slug: str
    author_id: int

    class Config:
        from_attributes = True
