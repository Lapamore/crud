from pydantic import BaseModel

__all__ = ["CommentBase"]


class CommentBase(BaseModel):
    body: str
