from typing import Optional, List
from pydantic import BaseModel, ConfigDict

__all__ = ["UpdateArticleCommand"]


class UpdateArticleCommand(BaseModel):
    model_config = ConfigDict(frozen=True)

    slug: str
    user_id: int
    title: Optional[str] = None
    description: Optional[str] = None
    body: Optional[str] = None
    tag_list: Optional[List[str]] = None