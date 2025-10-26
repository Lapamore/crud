from typing import Optional
from pydantic import BaseModel


class CommentBase(BaseModel):
    body: str


class CommentCreate(CommentBase):
    pass


class Comment(CommentBase):
    id: int
    article_id: int
    author_id: int

    class Config:
        from_attributes = True
