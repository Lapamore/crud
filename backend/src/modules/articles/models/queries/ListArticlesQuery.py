from pydantic import BaseModel, ConfigDict

__all__ = ["ListArticlesQuery"]


class ListArticlesQuery(BaseModel):
    model_config = ConfigDict(frozen=True)

    skip: int = 0
    limit: int = 100