from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class CreateArticleCommand(BaseModel):
    model_config = ConfigDict(frozen=True)

    title: str
    description: str
    body: str
    author_id: int
    tag_list: Optional[List[str]] = None
