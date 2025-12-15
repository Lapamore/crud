from pydantic import BaseModel, ConfigDict

__all__ = ["ListCommentsByArticleSlugQuery"]


class ListCommentsByArticleSlugQuery(BaseModel):
    model_config = ConfigDict(frozen=True)

    slug: str
