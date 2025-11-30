from pydantic import BaseModel, ConfigDict


class GetArticleBySlugQuery(BaseModel):
    model_config = ConfigDict(frozen=True)

    slug: str
