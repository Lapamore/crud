from pydantic import BaseModel, ConfigDict

__all__ = ["CreateCommentCommand"]


class CreateCommentCommand(BaseModel):
    model_config = ConfigDict(frozen=True)

    body: str
    article_slug: str
    author_id: int
