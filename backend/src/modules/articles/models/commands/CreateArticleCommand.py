from typing import Optional, List
from pydantic import BaseModel, ConfigDict

__all__ = ["CreateArticleCommand"]


class CreateArticleCommand(BaseModel):
    model_config = ConfigDict(frozen=True)

    title: str
    description: str
    body: str
    tag_list: Optional[List[str]] = None