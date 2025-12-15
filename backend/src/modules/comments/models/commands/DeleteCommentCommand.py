from pydantic import BaseModel, ConfigDict

__all__ = ["DeleteCommentCommand"]


class DeleteCommentCommand(BaseModel):
    model_config = ConfigDict(frozen=True)

    slug: str
    comment_id: int
    user_id: int
