from pydantic import BaseModel, ConfigDict


class GetCommentByIdQuery(BaseModel):
    model_config = ConfigDict(frozen=True)

    comment_id: int
