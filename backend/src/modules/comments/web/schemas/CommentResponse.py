from pydantic import BaseModel, ConfigDict

__all__ = ["CommentResponse"]


class CommentResponse(BaseModel):
    id: int
    body: str
    article_id: int
    author_id: int

    model_config = ConfigDict(from_atributes=True)