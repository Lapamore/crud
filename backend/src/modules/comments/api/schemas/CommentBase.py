from pydantic import BaseModel


class CommentBase(BaseModel):
    body: str
