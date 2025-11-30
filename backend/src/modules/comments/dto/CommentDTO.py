from typing import Optional
from pydantic import BaseModel, ConfigDict


class CommentDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int
    body: str
    article_id: int
    author_id: int
