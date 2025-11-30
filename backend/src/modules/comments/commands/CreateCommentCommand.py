from pydantic import BaseModel, ConfigDict


class CreateCommentCommand(BaseModel):
    model_config = ConfigDict(frozen=True)

    body: str
    article_id: int
    author_id: int
