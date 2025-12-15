from .ArticleBase import ArticleBase

__all__ = ["ArticleResponse"]


class ArticleResponse(ArticleBase):
    id: int
    slug: str
    author_id: int

    class Config:
        from_attributes = True
