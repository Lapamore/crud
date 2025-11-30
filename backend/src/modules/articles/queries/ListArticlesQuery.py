from pydantic import BaseModel, ConfigDict


class ListArticlesQuery(BaseModel):
    model_config = ConfigDict(frozen=True)

    skip: int = 0
    limit: int = 100
