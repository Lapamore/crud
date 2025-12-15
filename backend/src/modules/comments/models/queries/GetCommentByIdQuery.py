from pydantic import BaseModel, ConfigDict

__all__ = ["GetCommentByIdQuery"]


class GetCommentByIdQuery(BaseModel):
    model_config = ConfigDict(frozen=True)

    comment_id: int
