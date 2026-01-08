from typing import Optional
from .ArticleBase import ArticleBase


class ArticleResponse(ArticleBase):
    id: int
    slug: str
    author_id: int
    status: str = "DRAFT"
    preview_url: Optional[str] = None

    class Config:
        from_attributes = True
