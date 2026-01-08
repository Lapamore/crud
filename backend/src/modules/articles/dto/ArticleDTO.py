from typing import Optional, List
from pydantic import BaseModel, ConfigDict

__all__ = ["ArticleDTO"]


class ArticleDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int
    slug: str
    title: str
    description: str
    body: str
    author_id: int
    tag_list: Optional[List[str]] = None
    status: str = "DRAFT"
    preview_url: Optional[str] = None
