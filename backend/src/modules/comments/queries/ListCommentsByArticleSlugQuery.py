from pydantic import BaseModel, ConfigDict


class ListCommentsByArticleSlugQuery(BaseModel):
    model_config = ConfigDict(frozen=True)

    slug: str
