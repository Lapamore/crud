from pydantic import BaseModel, ConfigDict

__all__ = ["GetArticleBySlugQuery"]


class GetArticleBySlugQuery(BaseModel):
    model_config = ConfigDict(frozen=True)

    slug: str
