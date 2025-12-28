from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class ArticleDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    id: int
    slug: str
    title: str
    description: str
    body: str
    author_id: int
    tag_list: Optional[List[str]] = None
