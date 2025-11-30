from pydantic import BaseModel, ConfigDict


class DeleteArticleCommand(BaseModel):
    model_config = ConfigDict(frozen=True)

    slug: str
    user_id: int
