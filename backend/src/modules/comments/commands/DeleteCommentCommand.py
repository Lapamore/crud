from pydantic import BaseModel, ConfigDict


class DeleteCommentCommand(BaseModel):
    model_config = ConfigDict(frozen=True)

    comment_id: int
    user_id: int
