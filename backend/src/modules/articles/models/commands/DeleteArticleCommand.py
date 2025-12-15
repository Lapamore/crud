from pydantic import BaseModel, ConfigDict

__all__ = ["DeleteArticleCommand"]


class DeleteArticleCommand(BaseModel):
    model_config = ConfigDict(frozen=True)

    slug: str
    user_id: int