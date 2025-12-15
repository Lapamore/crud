from pydantic import BaseModel, ConfigDict

__all__ = ["CommentDTO"]


class CommentDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int
    body: str
    article_id: int
    author_id: int